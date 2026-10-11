# MERENVAY ARC-AGI-2 Public Evaluation Reproduction

## Submission status — 11 October 2026

The earlier ARC Prize Community pull request **#61** was closed without merge after the head branch was force-reset from the submitting account. GitHub's public event log records the submitting account as the actor for both the closure and the same-second force-push; no maintainer rejection comment is recorded.

The corrected submission content has been restored in the fork and preserved on the clean replacement branch `submission/merenvay-arc2-corrected`.

Current defensible public metrics:
- **94.027778%** community-style task-average
- **152/167 = 91.017964%** output-weighted
- **105/120** task IDs fully correct
- GitHub-hosted generation elapsed: **46.115 s** in run `38120350359` and **24.716 s** in independent rescore run `38124392038`; timing is environment/run dependent, not a speed record

The earlier **120/120** figure is retained only as a first-test-per-task legacy diagnostic, not as the full multi-test ARC-AGI-2 public score. Resubmission to the community repository is pending; no official ARC Prize ranking or Verified score is claimed.


**MERENVAY founder and project maintainer:** Mohammed Mazen Al Nasser ([`@alnasserlegalservices`](https://github.com/alnasserlegalservices)). This identifies the founder and MERENVAY's documented engineering work; upstream Mentova authorship and licensing remain distinct and are credited below.

A reproducible, bounded runtime-stability repair of the public Mentova ARC-AGI-2 evaluator.

> **Methodology notice — updated 11 October 2026.** The pinned upstream Mentova scorer tests `Computed = TestOut` *inside candidate search*, so the **original** 120/120 run cannot establish answer-independent prediction and covered only one selected test input per public task ID. MERENVAY therefore built a generic answer-isolated submission path that never receives expected test outputs. On the current official ARC-AGI-2 public evaluation data, the frozen pipeline produced a **94.027778% community-style task-average score**, alongside **152/167 exact test outputs = 91.017964%** on an output-weighted/Kaggle-style calculation, with **105/120 task IDs** having all test outputs correct. The same frozen submission SHA-256 was reproduced in two GitHub-hosted runs, with generation elapsed **46.115 s** and **24.716 s** respectively; timing is treated as environment/run dependent. A separate earlier first-candidate diagnostic remains preserved as **120/120 first test inputs**, 20,026 ms, zero failures. The upstream Mentova rule library was developed against these public tasks, so none of these results establishes unseen-task generalisation or ARC Prize verification. GitHub's attestation documents artifact provenance, not generalisation. See [peer-review finding](https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/issues/1). No ARC Prize Verified score, official ranking, general-intelligence certificate, global ranking or BSI approval is claimed.

## Current full public multi-test result — answer-isolated

A generic submission path was added that serializes **training inputs, training outputs and test inputs only**. Expected test outputs are not passed into prediction. The generated submission is frozen before the separate public scorer reads expected outputs.

Current official public-data regression:

- **94.027778% community-style task-average score** — mean of each task's fraction of solved test outputs; comparable to Noemon's published scoring method
- **152/167 exact test outputs = 91.017964%** — output-weighted/Kaggle-style
- **105/120 task IDs** with all of their test outputs correct
- **120 task IDs / 167 test inputs**
- GitHub-hosted generation elapsed: **46.115 s** in run `38120350359`; **24.716 s** in independent rescore run `38124392038`
- submission SHA-256 in both runs: `a9e169517a419a1ff9bb7613f2d44803a00825dc5820aa3058dcf4b331cf9199`
- original full multi-test regression: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/38120350359
- independent rescore regression: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/38124392038

These are the current defensible **self-reported public metrics** for the generic answer-isolated pipeline. The 94.027778% figure is the Community-style comparator; the 91.017964% figure is output-weighted. It is not an ARC Prize Verified Semi-Private/Private score and is not an official leaderboard rank.

## Reproducible result of the original public-set scorer

The same original **answer-conditioned, first-test-per-task** public evaluator and patch reproduced the following legacy execution results across runs and two operating systems:

- Windows x64 / SWI-Prolog 10.0.2 — run 1: **120/120 first test inputs**, 78,185 ms, failures `[]`
- Windows x64 / SWI-Prolog 10.0.2 — run 2: **120/120 first test inputs**, 78,442 ms, failures `[]`
- GitHub-hosted Ubuntu 24.04.5 / SWI-Prolog 9.0.4: **120/120 first test inputs**, 40,412 ms, failures `[]`

Upstream source: `ai-university-aiu/Mentova`  
Pinned upstream commit: `d117c699416692cac7ceb951b09f2cdb484a89a6`

## Separate answer-isolated diagnostic (9 October 2026)

The [first-candidate runner](https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/blob/audit/blind-first-candidate-20261009/run_blind_first_candidate.pl) has a different scoring procedure from the original evaluator. It calls `once(first_proposed_output(TrainingPairs, TestIn, Rule, Prediction))` before the grade function ever sees the expected output, then uses strict equality `==` to score the frozen prediction. It keeps the same pinned upstream repository, runtime patch and 10-second per-task limit.

| Procedure | Corpus | Logged result | What it establishes |
| --- | --- | --- | --- |
| Upstream evaluator, expected output consulted within rule search | ARC-AGI-2 public evaluation (120 tasks) | 120/120 | Reproducibility of the original answer-conditioned scorer |
| First candidate selected with no expected output passed to the predictor | Same publicly exposed 120 tasks | **120/120**, 20,026 ms; 120 unique task IDs; 0 failures | A separate answer-isolated public-task replay, not hidden-set generalisation |

- [Answer-isolated CI execution and 120 per-task results](https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37907563655)
- Frozen diagnostic commit: `5ffa9fd92ed4f5fa1a29509b78ffca563465fb12`
- This first-candidate policy is a diagnostic heuristic, **not** a claim of optimal or independently validated general-purpose performance. The upstream rule library includes task-specific development against the public corpus.
- Independent expert audit and ARC Prize Verified semi-private evaluation remain **not completed**.

## Externally executed evidence

- [Stable GitHub Actions run](https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37769412232)
- [Evidence artifact](https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37769412232/artifacts/11547158323)
- [GitHub SLSA/Sigstore attestation](https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/attestations/53909570)
- [Rekor transparency-log entry](https://search.sigstore.dev?logIndex=3147098838)
- [Detailed GitHub-hosted receipt](GITHUB_ACTIONS_VERIFICATION.md)
- [Cross-platform stable receipt](STABLE_VERIFICATION_RECEIPT.md)

The GitHub-hosted workflow performs a clean checkout, pins the upstream commit, applies the public patch, runs all 120 tasks, asserts `RESULT score=120 total=120`, asserts `FAILS []`, uploads an artifact, and generates signed build provenance.

## What changed

The upstream dispatcher could reach correct, already-existing rules too late under the repository's 10-second per-task limit. The patch moves six verified rules earlier using narrow O(cells) structural gates:

- `mirror_patch`
- `template_expand`
- `constellation`
- `mosaic_heal`
- `hole_color`
- `frame_compass`

The patch does **not** add answer keys, change task data, or modify transformation semantics.

## Reproduce

```bash
git clone https://github.com/ai-university-aiu/Mentova.git
cd Mentova
git checkout d117c699416692cac7ceb951b09f2cdb484a89a6
git apply ../merenvay_dispatch_fix.patch
swipl -q -f ../run_native_benchmark.pl -- \
  data/arc_agi_2/arc_tasks_2.pl \
  src/mentova/games/arc_benchmark_2.pl
```

Expected final lines:

```text
RESULT score=120 total=120 elapsed_ms=<environment-dependent>
FAILS []
```

## Evidence fingerprints

- Stable local patch SHA-256: `e45c29eee818209a2eafa0c3edd822f2a0423d2f8309b1af3920d66a368360c9`
- GitHub artifact patch SHA-256: `11a330022288ce124851d70488c0f7a1efe1351d109ea39d21c2e81d9aaa065c`
- Runner SHA-256: `46516f5efd776bb19eaec1f9004a412d85104ede657a3fe5b25a4d5fec35373e`
- GitHub run-log SHA-256: `cd4f2feb3b4a13584d2d8e482c4fb2b12d476e0920266e890d38369b7874e516`
- GitHub evidence ZIP SHA-256: `b79224b93df193dc9454be4b74eb5d3f1e752624c93291fbd8855cb1ee6f0bd1`
- Windows run 1 log SHA-256: `5a98419534e6b6ae5b5cb95b16392fff4aa2d66b918579ba2f7cceb7c0f52bf3`
- Windows run 2 log SHA-256: `55670b4fbfc507dcba9e7e55119c8bac9b01c0257cd8443b0998c34f6cef2175`

The local-patch and artifact-patch hashes differ because the local file contains a UTF-8 comment character while the public GitHub patch uses ASCII-only comments. The executable Prolog clauses are equivalent; the public repository file is the canonical publication artifact.

## DigiCert RFC 3161 timestamp

The final stable local evidence ZIP was timestamped by DigiCert's RFC 3161 Time Stamp Authority.

- Evidence ZIP SHA-256: `5aab73ee0d7bc5c53430ebfa0565b75c29206815c394792d9c4b31925c46b59f`
- Timestamp response SHA-256: `4f5e00edf540b1d18bbdd1793ad260561f720c2b9ca7fcb36458712db50ff2ef`
- Timestamp: `2026-10-08 11:24:23 GMT`
- Status: `Granted`
- Local cryptographic verification: `Verification: OK`

See the text records in [`timestamp/`](timestamp/).

## Claim boundary

This repository preserves the original **answer-conditioned** public scorer result and adds a separately completed **answer-isolated first-candidate** diagnostic on the same 120 known public tasks. Neither is a score on genuinely unseen tasks: the upstream code was developed against the public data. The result is not ARC Prize Verified, not a legal-reasoning result for MERENVAY's backend, not a global ranking, not a certificate of general intelligence, and not an independent BSI assessment. The earlier community PR #61 is closed without merge; corrected resubmission is pending.
