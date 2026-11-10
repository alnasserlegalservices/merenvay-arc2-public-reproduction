# MERENVAY E-RNA joint-witness spike

Local exploratory experiment, 10 November 2026.

All five arms scored **0/26 exact test outputs and 0/24 fully solved tasks** on the declared public training slice. The joint-feedback and first-witness prediction files are identical. Joint feedback examined 200,182 cells in 403 eligible merge calls and produced zero evaluated joint children. The method currently proposes only global color maps and rejects contradictory source-to-target mappings, including conflicts with cells that should stay unchanged.

A separate replay of the already-inspected development case `0d3d703e` verified that joint evidence repairs the generator's earlier failure. Four pairs jointly constrained an eight-entry color map. The first-witness and no-feedback arms failed. The symbolic baseline, the direct all-pair map from identity (static control), and the joint-feedback arm each solved it. This explains the case without crediting iterative feedback for an advantage over direct fitting. It was excluded from the fresh slice. The prior `0c786b71` mirror witness is a separate experiment.

## Protocol

The first 40 public training task IDs in lexical order were used in a prior report. This spike declared positions 41–64 from the same pinned official training index and froze its source and protocol before fetching their data. The public sample may overlap prior knowledge and is not representative or hidden. Seed 0, 128 candidates, 1,024 validation applications, and two test predictions per input. Candidate caps and observed validation counts do not equalize total work.

The original solver and baseline came from prior MERENVAY research artifacts. OpenAI coding assistance added the joint color constraints, controls and harness. No task-specific inference hints or hosted model calls. The existing single-witness branch remains enabled for both joint controls. The static control adds all-pair fitting only to the identity parent, while the joint-feedback arm can add it to any eligible parent. Separate inference and score stages receive different files on the same machine.

## Reproduce

Python 3 standard library only.

```sh
python3 -B verify_controls.py
python3 -B joint_experiment.py prepare reproduction
python3 -B joint_experiment.py infer reproduction
python3 -B joint_experiment.py score reproduction
```

A replay generates compressed traces and per-task scores. This copy includes frozen predictions and data-source hashes. Public dataset license is included. MERENVAY code in this release is under MIT. See the root README for the dataset attribution.
