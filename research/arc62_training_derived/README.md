# MERENVAY Training-Derived Symbolic Baseline

**Proposed replacement method for ARC Community PR #62, updated 5 November 2026. Actual self-reported ARC-AGI-2 public result: 0.0%, covering all 120 tasks and 167 test inputs with at most two attempts per input. This is not official ARC verification or maintainer acceptance.**

This self-contained Python 3 enumerative symbolic baseline is a different submitted method from the task-specific Mentova recipes the ARC Community reviewer challenged. It does NOT import or invoke Mentova. It has no branches on task IDs or known solution layouts. The solver receives only training input/output examples plus unlabeled test inputs, fits programs against *all* visible demonstrations and emits at most two grid predictions. The familiar transformation operators and enumerative search are not claimed as new algorithms; contribution and eligibility remain for maintainer review.

Its finite, task-agnostic grammar includes D4 rotations/flips, foreground crop, 2x/3x scaling, 2x2 repetition, two-operator compositions and an optional color mapping inferred solely from training examples. Invalid/test-output inputs are rejected. The grammar is deliberately limited: it does not implement general recursive program invention, the full E-RNA/Decision DNA memory process, object counting or advanced relational rules.

## Run original synthetic controls

From this directory:

    python -B -m unittest discover -s tests -v

The 18 existing synthetic controls check operators, multi-test support, task-ID independence, training consistency, absence of test labels, invalid grids, task-level strategy freezing, whole-task fallback and deduplication of candidate output sequences. Seven new projection/scoring controls check two-attempt scoring, unequal task sizes and malformed records. All **25 tests passed**; the [complete log](results/20261105_public_evaluation/tests.log) is retained. These are software checks, not solved ARC tasks.

## Run on challenge-only JSON

    python generic_solver.py --challenges challenge_only.json --submission output.json

Task IDs are used only as output keys. The input must contain train pairs and test-input grids **without test output labels**. Any scoring belongs to a separate process after submission is frozen.

## Actual complete public evaluation and reproduction

The unchanged published solver at `be73bc4917f2877abae0dfd36736b1a6e8117049` was run once on the full official ARC-AGI-2 `data/evaluation/` split at dataset commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`: **0/167 exact outputs and 0/120 fully correct tasks**. Both the mean of each task's solved-output fraction and output-weighted accuracy are **0.0%**. There were no process/schema failures. No solver change, score-driven tuning or replacement trial followed this result.

The contribution proposed for review combines all-demonstration rule induction, deterministic task-level multi-test selection, and a challenge-only prediction/freeze/separate-score workflow. This limited grammar lacks coverage of the evaluated ARC-AGI-2 tasks; the negative result is retained transparently.

Use the immutable method tree linked by the submission YAML's `code_url`. From its repository root:

```bash
git clone https://github.com/arcprize/ARC-AGI-2.git /tmp/arc62-official-data
git -C /tmp/arc62-official-data checkout f3283f727488ad98fe575ea6a5ac981e4a188e49
python -B research/arc62_training_derived/evaluate_public.py run \
  --dataset /tmp/arc62-official-data \
  --output /tmp/arc62-new-result
python -B -m unittest discover -s research/arc62_training_derived/tests -v
```

The output directory must be new. The standard-library evaluator projects training pairs plus test inputs, invokes the unchanged solver in a separate process, freezes predictions and hashes, then launches a separate scorer. The projection process necessarily reads public labelled files to discard their test output fields, and those files remain on the same host. This is a data-flow boundary, not an OS security sandbox. Solver defaults are 256 candidate evaluations and 512 validation checks; `_fit_map` scans are outside that check counter, and no total wall-time bound is claimed.

An output is correct only when either of its two grids matches every expected cell and dimension. Task-average is `100 * mean(correct outputs / outputs per task)`; output-weighted is `100 * total correct outputs / total outputs`. Invalid schema, missing/extra IDs and excess attempts abort validation.

See the [full execution record](results/20261105_public_evaluation/README.md), [scores](results/20261105_public_evaluation/score.json), [complete frozen predictions](results/20261105_public_evaluation/predictions.json), [freeze manifest](results/20261105_public_evaluation/frozen_manifest.json), and [independent arithmetic recomputation](INDEPENDENT_SCORE_AUDIT_20261105.json). Solver SHA-256: `37084696d0040d26ce08fc3d18e0cea20f78436152abb4ba59b9a24add01e769`; prediction SHA-256: `d3bb5745077d6c638b626ad1220e7eab31d25c89e771dc1256c6b0fbada2de83`.

## PR #62 status and limitations

Following the maintainer's 5 November request, this standalone baseline is proposed as the submitted method in the existing PR, replacing the historical Mentova runtime-repair descriptor. No historical Mentova score is inherited. The actual local public-data result is self-reported, not official verification, a Kaggle submission, a hidden-set generalisation measurement or a certificate of general intelligence. Method eligibility and originality remain for maintainer review.

Only the standalone source and public evaluation data are involved. The retained dataset Apache 2.0 license covers its projected challenge data; this does not automatically specify a license for the independent solver implementation. No new license grant is made here.

## Task-level strategy selection (3 November revision)

Candidate programs are fitted to visible training demonstrations only. The same selected first and second program must apply to **all** test inputs of a task; a program that fails on any test grid is excluded globally. If none can handle all grids, the baseline returns an explicitly unverified identity fallback for every test input. A single surviving prediction sequence is duplicated into both slots. Previously unseen colors retain their input values. The full public result above uses this task-level selection and the unchanged grammar.
