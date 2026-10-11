# MERENVAY ARC-AGI-2 Verification Readiness Receipt

**Date:** 11 October 2026  
**Candidate branch:** `verification/arc-agi2-generic-submission`  
**Scope:** execution/tooling readiness only. This receipt is **not** an ARC Prize Verified score and does not claim unseen-task generalisation.

## Frozen public reference

The generic answer-isolated submission pipeline:
- consumes training inputs/outputs and test inputs only;
- never receives expected test outputs during prediction;
- freezes `submission.json` before public scoring;
- covers all 120 public tasks / 167 public test outputs.

Frozen submission SHA-256:

`a9e169517a419a1ff9bb7613f2d44803a00825dc5820aa3058dcf4b331cf9199`

Public metrics from the frozen artifact:
- **94.027778%** community-style task-average score;
- **152/167 = 91.017964%** output-weighted / Kaggle-style;
- **105/120** tasks with every public test output correct.

These metrics are self-reported on the known public corpus.

## Gate matrix

| Gate | Status | Evidence |
| --- | --- | --- |
| Answer-isolated challenge conversion | PASS | Test outputs omitted from predictor facts |
| Full 120-task / 167-output generic prediction | PASS | GitHub Actions public regression |
| Frozen-before-score separation | PASS | Submission created before scorer runs |
| ID/order/path invariance | PASS | Verification hardening CI |
| Timeout containment | PASS | Forced timeout fixture falls back to valid grid |
| Crash containment | PASS | Forced exception fixture falls back to valid grid |
| Atomic submission write | PASS | Existing output survives malformed predictor failure |
| Container-cross-user readability | PASS | Atomic file mode fixed to 0644 |
| Offline runtime bundle | PASS | Network-namespace-isolated end-to-end CI |
| Runtime checksum manifest | PASS | SHA-256 validation after extraction |
| Public ARC corpus excluded from runtime bundle | PASS | Final bundle packages patched solver only, no `arc_tasks_2.pl` / solutions corpus |
| Clean offline full-public reproduction | PASS | Run 38122094457: challenge-only input, network disabled, frozen SHA preserved, post-freeze score reconciled |
| Official Kaggle CPU image compatibility | PASS | Clean bundle ran successfully with `--network none` in `gcr.io/kaggle-images/python@sha256:81b1e7c4b4f0f2a7e0a33943c95754b1b7af6b30d65221633a284b6b601cd84a` (run 38122078200) |
| ARC Prize Semi-Private evaluation | NOT RUN | External ARC verification required |
| ARC Prize Private evaluation | NOT RUN | External competition/evaluator action required |

## Runtime package

The clean offline package contains:
- portable Linux SWI-Prolog runtime;
- patched `arc_benchmark_2.pl` only from pinned Mentova commit `d117c699416692cac7ceb951b09f2cdb484a89a6`;
- upstream licence files;
- answer-isolated converter/predictor/submission validator;
- offline Kaggle entrypoint.

It deliberately excludes:
- `data/arc_agi_2/arc_tasks_2.pl`;
- ARC public test-output corpus files;
- upstream Git history;
- public-solution walkthrough documents;
- scoring solution files.

Latest clean-bundle CI artifact digest before final compatibility closure:

`sha256:9b3cce4773df3641dc6863de7d49db8ce13aa890269f0ad3df266e16f8b577c6`

Artifact archive size: **23,303,654 bytes**.

Official Kaggle-image compatibility evidence artifact digest:

`sha256:7c8cd26ff0094ce0e989d2def0e4145c9370a7c281bd08a9407e59c35acafcb3`

Kaggle CPU image digest used for the successful clean-bundle test:

`sha256:81b1e7c4b4f0f2a7e0a33943c95754b1b7af6b30d65221633a284b6b601cd84a`.

Full offline public-regression evidence artifact digest:

`sha256:80e9eb7e28d32dd07a8539b379f9fab405b7c41a34b95f5cdb00404b08a4ab35`

The isolated run regenerated the exact frozen submission SHA `a9e169517a419a1ff9bb7613f2d44803a00825dc5820aa3058dcf4b331cf9199` and re-confirmed 94.027778% community-style / 91.017964% output-weighted / 105 of 120 all-test task passes.

## Methodological boundary

**Answer isolation is not exposure isolation.** The Mentova rule library was developed against known ARC public tasks. The public score therefore demonstrates execution on an exposed corpus, not fluid generalisation to unseen ARC tasks.

No amount of additional public rerunning can close that gap. The only decisive next evidence is a frozen-candidate run on genuinely unseen tasks under a competent external protocol.

## Claim ceiling

Until an authorised unseen evaluation occurs, do not use:
- `ARC Prize Verified`;
- `official #1`;
- `100% ARC-AGI-2`;
- `hidden-set 100%`;
- `general intelligence`;
- `world record`.

Defensible wording remains:
**MERENVAY currently has a self-reported 94.027778% ARC-AGI-2 public community-style submitted score on its corrected full multi-test pipeline; in the 11 Oct 2026 snapshot of explicit public-score entries across the Community main branch plus open PRs, it is second behind CCARC 96.81%. The Community PR remains under review and no ARC Prize hidden-set verification has occurred.**
