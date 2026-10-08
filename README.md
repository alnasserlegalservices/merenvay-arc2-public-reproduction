# MERENVAY ARC-AGI-2 Public Evaluation Reproduction

A reproducible, bounded runtime-stability repair of the public Mentova ARC-AGI-2 evaluator.

## Stable result

The same public evaluator and patch produced exact results across independent runs and two operating systems:

- Windows x64 / SWI-Prolog 10.0.2 — run 1: **120/120**, 78,185 ms, failures `[]`
- Windows x64 / SWI-Prolog 10.0.2 — run 2: **120/120**, 78,442 ms, failures `[]`
- GitHub-hosted Ubuntu 24.04.5 / SWI-Prolog 9.0.4: **120/120**, 40,412 ms, failures `[]`

Upstream source: `ai-university-aiu/Mentova`  
Pinned upstream commit: `d117c699416692cac7ceb951b09f2cdb484a89a6`

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

This repository proves reproducible execution on the ARC-AGI-2 **public evaluation** data contained in the upstream repository. It is not ARC Prize Verified, does not establish semi-private/private generalisation, and is not a certificate of general intelligence. ARC Prize has been asked to consider the system for its official verification process.
