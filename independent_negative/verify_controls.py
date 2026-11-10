"""Verify the merge rule and replay the already-inspected development case."""
import hashlib
from pathlib import Path

import erna2
import joint_experiment as experiment

root = Path(__file__).resolve().parent
for file in experiment.read(root / 'source_data.json'):
    assert experiment.sha(root / file['path']) == file['sha256'], file['path']

identity = [{'op': 'identity'}]
demos = [(((1, 0),), ((3, 0),)), (((2, 0),), ((4, 0),))]
outcomes = [{'match': False}] * 2
children, cells = experiment.joint_color_repairs(identity, [a for a, _ in demos],
                                                demos, outcomes)
assert children[0][0] == [{'op': 'colormap', 'map': [[1, 3], [2, 4]]}]
assert children[0][1]['single_pair_has_full_map'] == [False, False] and cells == 4
demos.append((((1, 0),), ((1, 0),)))
children, _ = experiment.joint_color_repairs(identity, [a for a, _ in demos],
                                            demos, outcomes + [{'match': True}])
assert not children

known = root / 'data/known_0d3d703e.json'
assert hashlib.sha1(f'blob {known.stat().st_size}\0'.encode()
                    + known.read_bytes()).hexdigest() == 'b67b72661a27fafe630137d270f9f788a315e860'
case = experiment.read(known)
test = [row['input'] for row in case['test']]
runs = {'baseline': experiment.baseline_solve(case['train'], test, 128, 1024)}
for name, feedback, repair in (
    ('no_feedback', False, None),
    ('first_witness', True, None),
    ('static_joint', True, experiment.static_color_repairs),
    ('joint_feedback', True, experiment.joint_color_repairs),
):
    runs[name] = erna2.solve(case['train'], test, feedback, extra_repairs=repair)
expected = [row['output'] for row in case['test']]
counts = {
    name: sum(y in (row['attempt_1'], row['attempt_2']) for y, row in zip(expected, run['attempts']))
    for name, run in runs.items()
}
assert counts == {'baseline': 1, 'no_feedback': 0, 'first_witness': 0,
                  'static_joint': 1, 'joint_feedback': 1}
print('Synthetic controls passed. Previously inspected ARC case:', counts)
