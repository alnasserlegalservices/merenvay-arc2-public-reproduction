"""Reproduce both experiments using only Python and the bundled public ARC data."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
ARMS = ('baseline', 'no_feedback', 'feedback')


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(folder, script, *args):
    subprocess.run([sys.executable, '-B', str(folder / script), *map(str, args)],
                   cwd=folder, check=True, stdout=subprocess.PIPE, text=True)


def replay_object(out):
    folder = ROOT / 'object_feedback'
    archived = read(folder / 'PACKAGE_SHA256.json')
    tasks = read(folder / 'prereg.json')['task_ids']
    files = ('erna2.py', 'run_experiment.py', 'prereg.json', 'vendor/generic_solver.py')
    for name in (*files, *(f'data/{task}.json' for task in tasks)):
        require(digest(folder / name) == archived[name], f'Archived source differs: {name}')
    run(folder, 'run_experiment.py', 'run', '--out', out)
    score = read(out / 'score.json')
    actual = []
    for arm in ARMS:
        name = f'{arm}_predictions.json'
        require(digest(out / name) == archived[f'results/run1/{name}'],
                f'Archived predictions differ: {arm}')
        current = score['arms'][arm]
        actual.append((current['correct_test_outputs'], current['total_test_outputs']))
    require(actual == [(1, 40), (1, 40), (2, 40)], 'Unexpected cohort scores')

    task = '0c786b71'
    trace_path = out / f'traces/feedback/{task}.json.gz'
    trace = json.loads(gzip.decompress(trace_path.read_bytes()))
    selected = trace['trace'][trace['selected_rule_ids'][0]]
    parent = trace['trace'][selected['origin']['parent_id']]
    axes = [step['axis'] for step in selected['program']]
    parent_errors = [row['n_diff_cells'] for row in parent['outcomes']]
    child_errors = [row['n_diff_cells'] for row in selected['outcomes']]
    require(selected['origin']['pair'] == 0 and selected['origin']['type'] == 'residual'
            and axes == ['h', 'v'] and parent_errors == [36, 36, 36]
            and child_errors == [0, 0, 0], 'Unexpected mirror witness')
    require([score['task_table'][task][arm]['correct'] for arm in ARMS] == [0, 0, 1],
            'Unexpected witness scores')
    return {'outputs': dict(zip(ARMS, actual)), 'archived_prediction_hashes': '3/3',
            'discordant_tasks': score['discordant_feedback_vs_no_feedback'],
            'witness': {'id': task, 'parent_id': parent['id'], 'child_id': selected['id'],
                        'parent_errors': parent_errors, 'child_errors': child_errors,
                        'archived_gzip_sha_matches': digest(trace_path)
                        == archived[f'results/run1/traces/feedback/{task}.json.gz']}}


def replay_negative(out):
    folder = ROOT / 'independent_negative'
    run(folder, 'verify_controls.py')
    for stage in ('prepare', 'infer', 'score'):
        run(folder, 'joint_experiment.py', stage, out)
    score = read(out / 'score.json')
    for arm, result in score['arms'].items():
        name = f'{arm}_predictions.json'
        require(digest(out / name) == digest(folder / 'results' / name),
                f'Negative run predictions differ: {arm}')
        require(result['correct_outputs'] == 0 and not result['solved'],
                f'Unexpected negative result: {arm}')
    return {'tasks': score['tasks'], 'outputs': score['outputs'], 'correct_per_arm': 0,
            'prediction_hashes': f"{len(score['arms'])}/{len(score['arms'])}",
            'controls': 'passed'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='merenvay-erna-replay-') as tmp:
        root = Path(tmp)
        result = {'object_feedback': replay_object(root / 'object'),
                  'joint_constraints': replay_negative(root / 'joint')}
    print(json.dumps(result, indent=2, sort_keys=True))
