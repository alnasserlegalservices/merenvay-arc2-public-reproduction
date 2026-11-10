"""Scoped, deterministic arms: baseline, no_feedback, feedback. No network or model at inference.

prepare reads public labels to make two separate files. infer reads only the
challenge file, validates training pairs and freezes predictions; score is a later
process that verifies file, code and preregistration hashes. This is data-flow
separation on one host, NOT an OS-enforced sandbox.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from vendor import generic_solver as baseline

PREREG_SHA256 = 'a808ec6df94c643dc176bf4c8119bde44039b04c21d5beca7bd7cdc499862b71'
ARMS = ('baseline', 'no_feedback', 'feedback')


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n')


def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(pred, expected):
    h = max(len(pred), len(expected))
    w = max(len(pred[0]) if pred else 0, len(expected[0]))
    get = lambda g, r, c: g[r][c] if r < len(g) and c < len(g[r]) else None
    return [[r, c, get(pred, r, c), get(expected, r, c)] for r in range(h) for c in range(w)
            if get(pred, r, c) != get(expected, r, c)]


def baseline_solve(train, tests, max_candidates, max_checks):
    demos = baseline._validated_demos(train)
    accepted, seen, trace, checks = [], set(), [], 0
    for proto in baseline._candidate_shapes():
        branches = [proto]
        mapping = baseline._fit_map(proto, demos)
        if mapping:
            branches.append(baseline.Program(proto.ops, mapping))
        for p in branches:
            if len(trace) >= max_candidates or checks + len(demos) > max_checks:
                break
            if p.name in seen:
                continue
            seen.add(p.name)
            pairs = []
            for j, (a, b) in enumerate(demos):
                checks += 1
                reason = None
                try:
                    out = baseline.as_list(p.apply(a))
                except ValueError as e:
                    out, reason = [], str(e)
                diff = errors(out, baseline.as_list(b))
                pairs.append({'pair': j, 'passed': not diff, 'n_cell_errors': len(diff), 'execution_error': reason})
            ok = all(x['passed'] for x in pairs)
            trace.append({'hypothesis': {'ops': p.ops, 'mapping': p.mapping}, 'pairs': pairs, 'accepted': ok})
            if ok:
                accepted.append(p)
        if len(trace) >= max_candidates or checks + len(demos) > max_checks:
            break
    accepted.sort(key=lambda p: (p.cost, p.name))
    selected, seqseen = [], set()
    for p in accepted:
        try:
            seq = tuple(p.apply(baseline.validate_grid(g)) for g in tests)
        except ValueError:
            continue
        if seq in seqseen:
            continue
        selected.append(seq)
        seqseen.add(seq)
        if len(selected) == 2:
            break
    fallback = not selected
    if fallback:
        selected = [tuple(baseline.validate_grid(g) for g in tests)]
    if len(selected) == 1:
        selected.append(selected[0])
    attempts = [{'attempt_1': baseline.as_list(selected[0][i]), 'attempt_2': baseline.as_list(selected[1][i])}
                for i in range(len(tests))]
    return {'attempts': attempts, 'trace': trace,
            'stats': {'candidates': len(trace), 'checks': checks, 'accepted_programs': len(accepted), 'fallback_identity': fallback}}


def prepare(out):
    if out.exists():
        raise ValueError('Refusing to overwrite existing run directory')
    if sha(ROOT / 'prereg.json') != PREREG_SHA256:
        raise ValueError('prereg.json differs from the frozen preregistration')
    prereg = read(ROOT / 'prereg.json')
    challenges, answers, sources = {}, {}, {}
    for key in prereg['task_ids']:
        path = ROOT / 'data' / f'{key}.json'
        raw = read(path)
        challenges[key] = {'train': raw['train'], 'test': [{'input': p['input']} for p in raw['test']]}
        answers[key] = [p['output'] for p in raw['test']]
        sources[key] = sha(path)
    dump(out / 'challenge_only.json', challenges)
    dump(out / 'answers_scoring_only.json', answers)
    dump(out / 'input_manifest.json', {'prereg_sha256': sha(ROOT / 'prereg.json'), 'source_sha256': sources,
                                       'challenge_sha256': sha(out / 'challenge_only.json'),
                                       'answers_sha256': sha(out / 'answers_scoring_only.json')})


def infer(out, arm):
    challenges = read(out / 'challenge_only.json')
    prereg = read(ROOT / 'prereg.json')
    budgets = prereg['budgets_per_task']
    predictions, stats, start = {}, {}, time.perf_counter()
    if arm != 'baseline':
        import erna2
    for key, task in challenges.items():
        if set(task) != {'train', 'test'} or any(set(t) != {'input'} for t in task['test']):
            raise ValueError('Labeled tests rejected')
        tests = [t['input'] for t in task['test']]
        kw = {'max_candidates': budgets['max_candidates'], 'max_checks': budgets['max_checks']}
        t0 = time.perf_counter()
        if arm == 'baseline':
            result = baseline_solve(task['train'], tests, **kw)
        else:
            result = erna2.solve(task['train'], tests, feedback=(arm == 'feedback'), seed=prereg['seed'], **kw)
        predictions[key] = result.pop('attempts')
        stats[key] = dict(result.get('stats', {}), wall_seconds=time.perf_counter() - t0)
        path = out / 'traces' / arm / f'{key}.json.gz'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(json.dumps(result, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    dump(out / f'{arm}_predictions.json', predictions)
    dump(out / f'{arm}_stats.json', {'task_stats': stats, 'wall_seconds': time.perf_counter() - start})


def freeze(out):
    files = [p for p in out.rglob('*') if p.is_file() and p.name != 'answers_scoring_only.json']
    source = [ROOT / 'run_experiment.py', ROOT / 'erna2.py', ROOT / 'prereg.json', ROOT / 'vendor/generic_solver.py']
    dump(out / 'prediction_freeze.json', {
        'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'files': {str(p.relative_to(out)): sha(p) for p in files if p.name != 'prediction_freeze.json'},
        'code_sha256': {str(p.relative_to(ROOT)): sha(p) for p in source}})


def score(out):
    frozen = read(out / 'prediction_freeze.json')
    for rel, expected in frozen['files'].items():
        if sha(out / rel) != expected:
            raise ValueError('Frozen artifact changed: ' + rel)
    for rel, expected in frozen['code_sha256'].items():
        if sha(ROOT / rel) != expected:
            raise ValueError('Code changed since prediction freeze: ' + rel)
    if sha(ROOT / 'prereg.json') != PREREG_SHA256:
        raise ValueError('prereg.json differs from the frozen preregistration')
    inputs = read(out / 'input_manifest.json')
    if sha(out / 'answers_scoring_only.json') != inputs['answers_sha256']:
        raise ValueError('Scoring answers changed since preparation')
    answers = read(out / 'answers_scoring_only.json')
    result = {'arms': {}, 'task_table': {}, 'scope': 'Self-reported development sample of 40 public ARC-AGI-2 training tasks; no competition score or hidden generalization claim.'}
    for arm in ARMS:
        pred = read(out / f'{arm}_predictions.json')
        stats = read(out / f'{arm}_stats.json')
        correct = total = 0
        complete, avgs = [], []
        if set(pred) != set(answers):
            raise ValueError('Missing task predictions')
        for key, outputs in answers.items():
            if len(pred[key]) != len(outputs):
                raise ValueError('Wrong test output count')
            for row in pred[key]:
                if type(row) is not dict or set(row) != {'attempt_1', 'attempt_2'}:
                    raise ValueError('Exactly two named attempts required')
                for grid in row.values():
                    baseline.validate_grid(grid)
            flags = [any(row[a] == expected for a in ('attempt_1', 'attempt_2')) for row, expected in zip(pred[key], outputs)]
            correct += sum(flags)
            total += len(flags)
            avgs.append(sum(flags) / len(flags))
            if all(flags):
                complete.append(key)
            result['task_table'].setdefault(key, {'test_outputs': len(flags)})[arm] = {'correct': sum(flags), 'all_correct': all(flags)}
        ts = stats['task_stats'].values()
        result['arms'][arm] = {'correct_test_outputs': correct, 'total_test_outputs': total, 'fully_correct_tasks': len(complete),
                               'total_tasks': len(answers), 'task_average_percent': 100 * sum(avgs) / len(avgs), 'solved_ids': complete,
                               'candidates': sum(s['candidates'] for s in ts), 'checks': sum(s['checks'] for s in ts),
                               'wall_seconds': stats['wall_seconds'],
                               'selected_residual_derived': sum(s.get('selected_residual_derived', 0) for s in ts),
                               'derived_children': sum(s.get('derived_children', 0) for s in ts),
                               'feedback_pair_analyses': sum(s.get('feedback_pair_analyses', 0) for s in ts)}
    sets = {a: set(result['arms'][a]['solved_ids']) for a in ARMS}
    result['overlap'] = {'all_three': sorted(set.intersection(*sets.values())), 'none': sorted(set(answers) - set.union(*sets.values())),
                         'feedback_only_vs_no_feedback': sorted(sets['feedback'] - sets['no_feedback']),
                         'no_feedback_only_vs_feedback': sorted(sets['no_feedback'] - sets['feedback']),
                         'baseline_only': sorted(sets['baseline'] - sets['feedback'] - sets['no_feedback'])}
    result['discordant_feedback_vs_no_feedback'] = len(result['overlap']['feedback_only_vs_no_feedback']) + len(result['overlap']['no_feedback_only_vs_feedback'])
    result['informative_comparison'] = result['discordant_feedback_vs_no_feedback'] >= 10
    dump(out / 'score.json', result)
    print(json.dumps({'arms': result['arms'], 'discordant': result['discordant_feedback_vs_no_feedback'],
                      'informative': result['informative_comparison']}, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['prepare', 'infer', 'freeze', 'score', 'run'])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--arm', choices=list(ARMS))
    a = p.parse_args()
    if a.command == 'run':
        prepare(a.out)
        for arm in ARMS:
            subprocess.run([sys.executable, '-B', __file__, 'infer', '--out', str(a.out), '--arm', arm], check=True)
        freeze(a.out)
        subprocess.run([sys.executable, '-B', __file__, 'score', '--out', str(a.out)], check=True)
    elif a.command == 'prepare':
        prepare(a.out)
    elif a.command == 'infer':
        infer(a.out, a.arm)
    elif a.command == 'freeze':
        freeze(a.out)
    else:
        score(a.out)


if __name__ == '__main__':
    main()
