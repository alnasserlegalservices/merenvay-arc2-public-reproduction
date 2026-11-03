# ARC-AGI-2 — training-derived generic baseline for PR #62 review

**Research-only prototype created 3 November 2026. Not a Kaggle score, official ARC verification, new legal-AI benchmark, or a replacement for an existing scored competition entry.**

This is an original self-contained Python 3 method that demonstrates a procedural alternative to the task-specific Mentova recipes the ARC Community reviewer challenged. It does NOT import or invoke Mentova. It has no branches on task IDs or known solution layouts. The solver receives only training input/output examples plus unlabeled test inputs, fits programs against *all* visible demonstrations and emits at most two grid predictions.

Its finite, task-agnostic grammar includes D4 rotations/flips, foreground crop, 2x/3x scaling, 2x2 repetition, two-operator compositions and an optional color mapping inferred solely from training examples. Invalid/test-output inputs are rejected. The grammar is deliberately limited: it does not implement general recursive program invention, the full E-RNA/Decision DNA memory process, object counting or advanced relational rules.

## Run original synthetic controls

From this directory:

    python -B -m unittest discover -s tests -v

15 synthetic unit tests check operators, multi-test support, task-ID independence, training consistency, absence of test labels, invalid grids and explicit fallback. Passing those tests demonstrates mechanics within this deliberately small grammar and does **not** establish hidden or public ARC-AGI-2 accuracy. No cherry-picked public ARC task score is claimed.

## Run on challenge-only JSON

    python generic_solver.py --challenges challenge_only.json --submission output.json

Task IDs are used only as output keys. The input must contain train pairs and test-input grids **without test output labels**. Any scoring belongs to a separate process after submission is frozen.

## PR #62 status and limitations

The previous public Mentova reproduction was based on solution-informed public tasks. Its 94.027778% public task-average and 152/167 output score are **not inherited by this new method**. This prototype is submitted for technical inspection as a *different* answer-isolated generic baseline; it has no independent ARC score or claim of novelty. It is not yet substituted for the PR #62 submission's upstream rule set. Maintainer input is needed on whether a method with much lower likely coverage is eligible as a separate entry.

The private MERENVAY multi-jurisdiction legal engine, 20-year archive, client information and isolated Hazem vault are not accessed or bundled. No licence to those assets is granted or implied.
