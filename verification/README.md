# ARC-AGI-2 Verification Readiness

This directory prepares MERENVAY's ARC-AGI-2 work for a genuinely
answer-isolated submission path.

## Why this exists

The current public reproduction is useful evidence of reproducibility, but it
is **not** an ARC Prize Verified score. ARC Prize states that Community
Leaderboard public scores are self-reported by default. Exceptional open-source
submissions may be selected for verification on the **Semi-Private** set.

For ARC-AGI-2, ARC Prize's current testing policy says that a verified
Semi-Private score and the Public score should agree within **±3 percentage
points**. Selection for verification is discretionary.

Official policy:
- https://arcprize.org/policy
- https://arcprize.org/arc-agi/2

## Current evidence

Public-set engineering record:
- public tasks: 120
- reproduced public scorer: 120/120
- GitHub-hosted public reproduction: 40.412 s
- separate answer-isolated first-candidate diagnostic: 120/120, 0 failures,
  20.026 s

Important limitation: the upstream Mentova rule library was developed against
the known public corpus. These public results therefore do **not** establish
unseen-task generalisation.

## What this branch adds

### 1. Test-output-free task conversion

`challenges_to_prolog.py` serializes:
- training inputs,
- training outputs,
- test inputs,

and deliberately omits expected test outputs.

### 2. Answer-isolated prediction

`predict_unseen.pl` selects predictions without receiving expected test
outputs. It emits two attempts per test input, matching the ARC Prize 2026
submission contract.

### 3. Submission validation

`build_submission.py` writes and validates:

```json
{
  "task_id": [
    {
      "attempt_1": [[0]],
      "attempt_2": [[0]]
    }
  ]
}
```

No scoring code or evaluation solutions are read by this path.

## Usage

The current path assumes:
1. SWI-Prolog is installed as `swipl`.
2. A pinned Mentova checkout exists.
3. `merenvay_dispatch_fix.patch` has been applied to
   `src/mentova/games/arc_benchmark_2.pl`.

Example:

```bash
python verification/build_submission.py \
  --challenges /path/to/arc-agi_evaluation_challenges.json \
  --benchmark-file /path/to/Mentova/src/mentova/games/arc_benchmark_2.pl \
  --output submission.json
```

## Verification blockers still open

This branch does **not** claim ARC Verified readiness is complete.

1. **Unseen generalisation is unknown.**
   The rule library has public-corpus development exposure. The only meaningful
   test is a genuinely unseen Semi-Private/Private evaluation.

2. **Kaggle runtime packaging is unresolved.**
   The current solver depends on SWI-Prolog. A verification notebook must package
   all runtime dependencies reproducibly and meet ARC/Kaggle execution limits.

3. **No ARC selection has occurred.**
   ARC Prize chooses which Community submissions to verify.

4. **Public 100% must not be presented as an official hidden-set score.**
   Until ARC runs a Semi-Private evaluation, the defensible language remains:
   reproducible/self-reported public result and open Community submission.

## Promotion gate

Do not promote any claim to "ARC Prize Verified", "official #1", "hidden-set
100%", "general intelligence", or equivalent unless ARC Prize publishes or
directly confirms the corresponding verified result.

The next technical milestone is not another public rerun. It is a fully
packaged, answer-isolated Kaggle execution path that can accept unseen challenge
JSON without code changes.
