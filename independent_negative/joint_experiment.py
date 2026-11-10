"""Compare single-pair and jointly constrained color repairs on ARC training tasks."""
import argparse
import gzip
import json
import time
from pathlib import Path

import erna2
from reference_runner import baseline_solve, dump, read, sha

ROOT = Path(__file__).resolve().parent
ARMS = ('baseline', 'no_feedback', 'first_witness', 'static_joint', 'joint_feedback')
SOURCE_FILES = ('protocol.json', 'training_index.txt', 'erna2.py',
                'reference_runner.py', 'joint_experiment.py', 'vendor/generic_solver.py')


def joint_color_repairs(parent, predictions, demos, outcomes):
    if any(pred is None or (len(pred), len(pred[0])) != (len(dst), len(dst[0]))
           for pred, (_, dst) in zip(predictions, demos)):
        return [], 0
    if sum(not row['match'] for row in outcomes) < 2:
        return [], 0

    pair_constraints = []
    scanned = 0
    for pred, (_, dst) in zip(predictions, demos):
        constraints = set()
        for a_row, b_row in zip(pred, dst):
            constraints.update(zip(a_row, b_row))
            scanned += len(a_row)
        pair_constraints.append(constraints)

    joined = {}
    for constraints in pair_constraints:
        for old, new in sorted(constraints):
            if joined.setdefault(old, new) != new:
                return [], scanned
    mapping = [[a, b] for a, b in sorted(joined.items()) if a != b]
    if not mapping:
        return [], scanned

    provenance = {
        'type': 'residual', 'scope': 'joint', 'derivation': 'merge color constraints',
        'pairs': [i for i, row in enumerate(outcomes) if not row['match']],
        'pair_constraints': [sorted(pair) for pair in pair_constraints],
        'single_pair_has_full_map': [
            sorted((a, b) for a, b in pair if a != b) == [tuple(m) for m in mapping]
            for pair in pair_constraints
        ],
    }
    # Recoloring an unmodified grid is one operation, so normalize the identity.
    prefix = [] if parent == [{'op': 'identity'}] else parent
    return [(prefix + [{'op': 'colormap', 'map': mapping}], provenance)], scanned


def static_color_repairs(parent, predictions, demos, outcomes):
    if parent != [{'op': 'identity'}]:
        return [], 0
    return joint_color_repairs(parent, predictions, demos, outcomes)


def source_hashes():
    return {name: sha(ROOT / name) for name in SOURCE_FILES}


def prepare(out):
    if source_hashes() != read(ROOT / 'source_freeze.json'):
        raise ValueError('Source differs from the frozen experiment')
    out.mkdir(parents=True, exist_ok=False)
    protocol = read(ROOT / 'protocol.json')
    challenges, answers = {}, {}
    for tid in protocol['task_ids']:
        task = read(ROOT / 'data' / f'{tid}.json')
        challenges[tid] = {'train': task['train'], 'test': [r['input'] for r in task['test']]}
        answers[tid] = [r['output'] for r in task['test']]
    dump(out / 'challenge.json', challenges)
    dump(out / 'answers.json', answers)
    dump(out / 'input_freeze.json', {'answers': sha(out / 'answers.json'),
                                    'challenge': sha(out / 'challenge.json')})


def infer(out):
    inputs = read(out / 'input_freeze.json')
    if source_hashes() != read(ROOT / 'source_freeze.json') or sha(out / 'challenge.json') != inputs['challenge']:
        raise ValueError('Source or challenge changed after freeze')
    challenges = read(out / 'challenge.json')
    protocol = read(ROOT / 'protocol.json')
    for arm in ARMS:
        started = time.perf_counter()
        predictions, stats = {}, {}
        for tid in protocol['task_ids']:
            case = challenges[tid]
            if arm == 'baseline':
                solved = baseline_solve(case['train'], case['test'],
                                        protocol['max_candidates'], protocol['max_checks'])
            else:
                callback = {'static_joint': static_color_repairs,
                            'joint_feedback': joint_color_repairs}.get(arm)
                solved = erna2.solve(case['train'], case['test'],
                                     feedback=arm in ('first_witness', 'static_joint', 'joint_feedback'),
                                     max_candidates=protocol['max_candidates'],
                                     max_checks=protocol['max_checks'], seed=protocol['seed'],
                                     extra_repairs=callback)
            predictions[tid] = solved['attempts']
            stats[tid] = solved['stats']
            trace = out / 'traces' / arm / f'{tid}.json.gz'
            trace.parent.mkdir(parents=True, exist_ok=True)
            trace.write_bytes(gzip.compress(json.dumps({
                'rules': solved['trace'], 'selected': solved.get('selected_rule_ids'),
            }, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
        dump(out / f'{arm}_predictions.json', predictions)
        dump(out / f'{arm}_stats.json', {'tasks': stats, 'seconds': time.perf_counter() - started})
    files = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'answers.json')
    dump(out / 'prediction_freeze.json', {str(p.relative_to(out)): sha(p) for p in files})


def score(out):
    if source_hashes() != read(ROOT / 'source_freeze.json'):
        raise ValueError('Frozen source changed')
    for name, digest in read(out / 'prediction_freeze.json').items():
        if sha(out / name) != digest:
            raise ValueError(f'Frozen artifact changed: {name}')
    if sha(out / 'answers.json') != read(out / 'input_freeze.json')['answers']:
        raise ValueError('Frozen answers changed')
    answers = read(out / 'answers.json')
    summary = {'tasks': len(answers), 'outputs': sum(map(len, answers.values())), 'arms': {}}
    for arm in ARMS:
        attempts = read(out / f'{arm}_predictions.json')
        counts, wins = {}, []
        for tid, expected in answers.items():
            if len(attempts[tid]) != len(expected):
                raise ValueError(f'Attempt count mismatch: {arm}/{tid}')
            counts[tid] = sum(y in (p['attempt_1'], p['attempt_2'])
                              for y, p in zip(expected, attempts[tid]))
            if counts[tid] == len(expected):
                wins.append(tid)
        stats = read(out / f'{arm}_stats.json')
        counters = ('candidates', 'checks', 'feedback_pair_analyses', 'joint_calls',
                    'joint_constraint_cells', 'accepted_programs')
        summary['arms'][arm] = {'correct_outputs': sum(counts.values()), 'solved': wins,
                                'per_task': counts,
                                'actual_work': {k: sum(t.get(k, 0) for t in stats['tasks'].values())
                                                for k in counters},
                                'seconds': stats['seconds']}
    dump(out / 'score.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('prepare', 'infer', 'score'))
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    {'prepare': prepare, 'infer': infer, 'score': score}[args.stage](args.out)
