# MERENVAY ARC-AGI-2 Offline Bundle

This package is an offline runtime candidate, not a performance claim.

It contains a portable SWI-Prolog runtime, a pinned Mentova checkout, the
MERENVAY dispatch/runtime patch, answer-isolated challenge conversion, generic
prediction, submission validation, and an offline Kaggle entry script.

The runtime contract is:
1. read competition challenge JSON from attached Kaggle input;
2. read this bundle from an attached Kaggle dataset;
3. copy the bundle to /kaggle/working;
4. run the answer-isolated predictor;
5. write /kaggle/working/submission.json.

This package does not prove Semi-Private or Private performance, unseen-task
generalisation, ARC Prize verification, an official #1 position, or general
intelligence. The upstream Mentova rule library was developed against the known
public corpus. Hidden evaluation remains the only meaningful generalisation
test.
