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

Current full public multi-test regression under the generic answer-isolated
submission path:
- **152/167 exact public test outputs = 91.017964%**
- **105/120 task IDs** with every public test output correct
- **120 task IDs / 167 test inputs** processed
- GitHub-hosted submission generation: **46.115 s**
- frozen submission SHA-256:
  `a9e169517a419a1ff9bb7613f2d44803a00825dc5820aa3058dcf4b331cf9199`
- evidence run:
  https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/38120350359

Legacy engineering records remain preserved:
- first-test-per-task GitHub reproduction: **120/120**, 40.412 s
- separate first-candidate diagnostic: **120/120 first test inputs**, 0 failures,
  20.026 s

The legacy 120/120 figures are **not** the full ARC multi-test public metric.
The upstream Mentova rule library was developed against the known public corpus,
so these public results do **not** establish unseen-task generalisation.

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

2. **External ARC/Kaggle execution is not yet completed.**
   Offline packaging is now demonstrated in network-isolated CI: portable
   SWI-Prolog, pinned Mentova, patch, answer-isolated predictor, and
   `submission.json` generation all pass without network access. The latest
   offline bundle CI artifact is 164,224,044 bytes with GitHub artifact digest
   `sha256:9c04be2ff6840d7db73675f422e2e72c22720071296ea1a5a2243c8db713286b`.
   This proves packaging/tooling, not acceptance by ARC Prize or Kaggle.

3. **No ARC selection has occurred.**
   ARC Prize chooses which Community submissions to verify.

4. **The current full public score is 91.017964%, not 100%.**
   Until ARC runs a Semi-Private evaluation, the defensible language is:
   **91.018% self-reported ARC-AGI-2 public result under a generic
   answer-isolated pipeline**. The Community Leaderboard is a showcase, not an
   official ranking of self-reported scores.

## Promotion gate

Do not promote any claim to "ARC Prize Verified", "official #1", "hidden-set
100%", "general intelligence", or equivalent unless ARC Prize publishes or
directly confirms the corresponding verified result.

The packaging milestone is now complete at CI level. The next material proof
milestone is external execution by ARC Prize on a swapped unseen/Semi-Private
challenge set, subject to ARC's discretionary selection and verification policy.
