# MERENVAY ARC-AGI-2 stable public-evaluation evidence

## Cross-platform exact results

- Windows x64 / SWI-Prolog 10.0.2, run 1: 120/120, 78,185 ms, failures []
- Windows x64 / SWI-Prolog 10.0.2, run 2: 120/120, 78,442 ms, failures []
- GitHub-hosted Ubuntu 24.04.5 / SWI-Prolog 9.0.4: 120/120, 40,412 ms, failures []

## GitHub-hosted external execution

- Source commit: 55a3b920b41a37942ac37667a238bac9e9dccabe
- Workflow run: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37769412232
- Artifact: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37769412232/artifacts/11547158323
- Artifact service digest: sha256:da6a5d98a745c6f5fcad6d5a7a01b54f2b4e97f3c27279e8c873281ba7ead37b
- Inner evidence ZIP SHA-256: b79224b93df193dc9454be4b74eb5d3f1e752624c93291fbd8855cb1ee6f0bd1
- SLSA/Sigstore attestation: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/attestations/53909570
- Rekor transparency entry: https://search.sigstore.dev?logIndex=3147098838

## Upstream and patch scope

- Upstream: https://github.com/ai-university-aiu/Mentova
- Upstream commit: d117c699416692cac7ceb951b09f2cdb484a89a6
- The patch moves six already-existing verified rules earlier in the dispatcher using O(cells) gates.
- It does not add answer keys, change task data, or change transformation semantics.

## Final DigiCert timestamp

- Evidence ZIP SHA-256: 5aab73ee0d7bc5c53430ebfa0565b75c29206815c394792d9c4b31925c46b59f
- Timestamp response SHA-256: 4f5e00edf540b1d18bbdd1793ad260561f720c2b9ca7fcb36458712db50ff2ef
- Timestamp: 2026-10-08 11:24:23 GMT
- Status: Granted
- Cryptographic verification: OK

## Claim boundary

This package establishes reproducible execution on the ARC-AGI-2 public evaluation data. It is not ARC Prize Verified, does not establish semi-private/private performance, and is not proof of general intelligence.
