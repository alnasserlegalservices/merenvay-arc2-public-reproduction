# ARC Prize 2026 ARC-AGI-2 — Competition Readiness

Status: **PREPARED / NOT YET SUBMITTED / NOT YET VERIFIED**

## Official route
- Competition: ARC Prize 2026 — ARC-AGI-2 on Kaggle.
- Official evaluation requires a Kaggle notebook.
- Evaluation runs without internet access.
- Semi-Private evaluation is the live contest/ARC leaderboard path; Private evaluation determines the final contest leaderboard.
- Do not describe any result as ARC Prize Verified until an official Kaggle/ARC Prize evaluation receipt or published result exists.

## Candidate
- Public repository: `alnasserlegalservices/merenvay-arc2-public-reproduction`.
- Existing answer-isolated predictor consumes training demonstrations and test inputs only.
- Offline bundle contract: attach bundle as Kaggle input; notebook runs `kaggle_entry.py`; output is `/kaggle/working/submission.json`.
- Public reference score remains self-reported and is not used as a hidden-set claim.

## 2026 competition notebook
Use:
`verification/notebooks/arc_agi2_2026_offline_submission.ipynb`

This notebook intentionally:
1. does not clone any GitHub repository;
2. does not install packages from the internet;
3. locates the attached offline bundle;
4. executes the answer-isolated entrypoint;
5. verifies that every test input has `attempt_1` and `attempt_2`;
6. emits only `submission.json`;
7. performs no grading or solution-file access.

## Human/account gates
The account holder must personally:
- sign in to Kaggle;
- join/accept the competition rules and any identity/eligibility terms;
- attach or upload the prepared offline bundle dataset if not already present;
- review the notebook and competition metadata;
- deliberately click the Kaggle submission action.

No one should accept competition terms, identity statements, eligibility declarations, or other personal attestations on the account holder's behalf.

## Remaining technical gate
Before the first paid/limited competition submission, verify that the attached offline bundle is the same package already tested in the Kaggle CPU image and that its manifest/digest matches the recorded readiness receipt. If the bundle available for upload cannot be matched to the recorded digest, classify the run **HOLD — BUNDLE IDENTITY UNVERIFIED** and rebuild/retest rather than guessing.
