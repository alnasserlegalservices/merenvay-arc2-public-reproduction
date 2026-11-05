# Frozen local public evaluation — 5 November 2026

The unchanged training-derived Python baseline scored **0.0% task-average** on
the full ARC-AGI-2 public evaluation split: **0/167 exact test outputs**, with
**0/120 tasks** having every test output correct. Both task-average and
output-weighted scores are 0.0%. There were no process or prediction-schema
failures. This is a negative result for this limited grammar; its synthetic
mechanics tests do not establish public ARC accuracy.

This is one locally executed, self-reported public-data trial. It is not an
official ARC verification, competition submission, independent human audit,
leaderboard rank or unseen-task generalisation measurement. The earlier
Mentova-derived public figures elsewhere in this repository do not belong to
this different method. No solver change or score-driven tuning followed this
run, and no alternative trial has been substituted for it.

## Data and frozen method

- Dataset: <https://github.com/arcprize/ARC-AGI-2>, commit
  `f3283f727488ad98fe575ea6a5ac981e4a188e49`; clean clone at execution.
- All 120 JSON task files in `data/evaluation/` were included, with their IDs
  checked for exact equality with `data/evaluation.txt`. They contain 167 test
  inputs. No sampling, first-test-only selection or training-split substitution
  was used. The source README describes 1,000 training and 120 evaluation tasks.
- Base method commit: `be73bc4917f2877abae0dfd36736b1a6e8117049`.
- Unchanged `generic_solver.py` SHA-256:
  `37084696d0040d26ce08fc3d18e0cea20f78436152abb4ba59b9a24add01e769`.
- New evaluation runner SHA-256:
  `40737334db50a93c46e5de1c7f663b76ff36a5247bc40a50151081c5a4563022`.
- Runtime: Python 3.12.14, standard library only. No API, keys or paid inference.
- Solver defaults: at most 256 candidate programs and 512 validation
  demonstration checks per task. The validation-check counter **does not
  include `_fit_map` scans**. At most two prediction grids are scored per test
  input. No CLI setting was added or overridden.
- Fallback: the existing solver selects the same one or two programs across
  every test input of a task and deduplicates whole-task output sequences. If
  none of the training-consistent programs applies to every test grid, it uses
  identity across the whole task. A single sequence is duplicated across the
  two attempts. The runner does not replace or repair failures; process and
  schema failures abort evaluation.

The dataset is distributed under its retained Apache 2.0 license in
`DATASET_LICENSE.txt`. `challenge_only.json` is a modified projection of the
official evaluation files: training pairs are retained and test outputs are
removed. No labelled solution file is copied into this result directory.

## Scoring and process boundary

An output is correct only if either of its at most two predicted grids exactly
matches every expected cell and dimension. Predictions with extra attempts,
missing/extra task IDs, missing/extra test records or malformed grids are
rejected. Task-average is
`100 * mean(correct test outputs / test outputs for each task)`; output-weighted
is `100 * total correct outputs / 167`. `score.json` retains both exact rational
fractions, every task's test count, and correctness for every test index.

The projection subprocess necessarily opens official public task files that
contain test labels, discarding their test output fields. Source inventory
hashing also reads those files' bytes. The unchanged solver CLI subprocess
receives only the path to the projected training pairs plus test inputs, and
the path for its prediction output. The runner freezes complete predictions,
their SHA-256, the challenge SHA-256 and a manifest before launching a distinct
scoring subprocess. That scorer verifies the frozen digests before consuming
expected grids for grading. This is process/data-flow separation, **not an OS
security sandbox**: the labelled source dataset remains on the same host.

The manifest was frozen at `2026-11-05T18:01:58.858911+00:00`; the scorer process
was launched at `2026-11-05T18:01:58.864088+00:00`. The scorer's own start time
was `2026-11-05T18:01:58.906680+00:00`. UTC run start was
`2026-11-05T18:01:57.718148+00:00` and completion was
`2026-11-05T18:01:59.058670+00:00`.

Prediction process elapsed time was 0.880097 seconds; projection was 0.151756
seconds and the scoring process was 0.194144 seconds. These are local wall-clock
measurements from one run and are not a speed record.

## Reproduce and inspect

From the repository root, with an official dataset clone at the recorded commit:

```bash
python -B research/arc62_training_derived/evaluate_public.py run \
  --dataset /path/to/ARC-AGI-2 \
  --output /path/to/a/new/result-directory

python -B -m unittest discover -s research/arc62_training_derived/tests -v
```

The runner refuses to overwrite an existing result directory. Exact executed
absolute commands, working directories, UTC process times, return codes and
complete stdout/stderr are retained in `projection_process.json`,
`prediction_process.json`, `scoring_process.json` and `frozen_manifest.json`.
The scorer was executed separately with the frozen manifest digest supplied as
an argument. No inference rerun is needed to audit the saved complete
predictions.

All **25 tests passed**: the existing 18 synthetic solver controls, unchanged,
and seven new scorer/projection controls. The latter cover unequal test counts,
credit for the second attempt, rejection of a third attempt, mismatched/missing
records, strict exact grids and exclusion of test answers from the projection.
The retained full test output is `tests.log`.

## Core artifact fingerprints

| Artifact | SHA-256 |
| --- | --- |
| `challenge_only.json` | `8cade36130fdf1fa8fbab00cfcdfb5be8e74acbf04140f6fe18c5f502f0639be` |
| `predictions.json` | `d3bb5745077d6c638b626ad1220e7eab31d25c89e771dc1256c6b0fbada2de83` |
| `frozen_manifest.json` | `d5f3bb03cbcbad6a2cc76376e9c4181a881e36376a6bea7e6f4589c915ccbba1` |
| `score.json` | `aff5edcc9d287b4234b128a3763e47b59c2fb44750a7440bfd226ebd8f251072` |

`result_receipt.json` separately records the result hash, frozen artifact
hashes, final source hashes and scoring process receipt. `artifact_checksums.sha256`
covers all files in this result directory other than itself; no self-hash or
external attestation is claimed.
