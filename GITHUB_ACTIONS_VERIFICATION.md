# GitHub-hosted stable reproduction receipt

## Result

A GitHub-hosted runner independently executed the stabilized public reproduction workflow from a clean checkout.

- Workflow: `Verify ARC-AGI-2 Public Result`
- Run ID: `37769412232`
- Job ID: `113284966228`
- Source commit: `55a3b920b41a37942ac37667a238bac9e9dccabe`
- Runner: GitHub-hosted Azure runner, Ubuntu 24.04.5 LTS
- SWI-Prolog: 9.0.4 for x86_64-linux
- Upstream Mentova commit: `d117c699416692cac7ceb951b09f2cdb484a89a6`
- Patch application: success, 65 insertions, no transformation-rule or benchmark-data changes
- Exact result: **120/120 tasks**
- Solver elapsed time: **40,412 ms**
- Wall-clock solver time: **41.18 seconds**
- Failed tasks: `[]`

## Evidence

- Workflow run: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37769412232
- Evidence artifact: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37769412232/artifacts/11547158323
- Artifact ID: `11547158323`
- Artifact service digest: `sha256:da6a5d98a745c6f5fcad6d5a7a01b54f2b4e97f3c27279e8c873281ba7ead37b`
- Inner evidence ZIP SHA-256: `b79224b93df193dc9454be4b74eb5d3f1e752624c93291fbd8855cb1ee6f0bd1`
- GitHub artifact attestation: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/attestations/53909570
- Sigstore Rekor transparency-log entry: https://search.sigstore.dev?logIndex=3147098838

## Files inside the evidence artifact

- `github_actions_public_run.log` — SHA-256 `cd4f2feb3b4a13584d2d8e482c4fb2b12d476e0920266e890d38369b7874e516`
- `merenvay_dispatch_fix.patch` — SHA-256 `11a330022288ce124851d70488c0f7a1efe1351d109ea39d21c2e81d9aaa065c`
- `run_native_benchmark.pl` — SHA-256 `46516f5efd776bb19eaec1f9004a412d85104ede657a3fe5b25a4d5fec35373e`
- `swipl_version.txt` — SHA-256 `3ea77e6bd4bc68319e3c43e0dd9895970f2604e191ad7e689d8188b4d8b0997e`
- `upstream_commit.txt` — SHA-256 `22b359de64c7efc8c97d73dc6d39a736271081e529403d50acad90192e44a87d`

## Attestation

GitHub generated a SLSA build-provenance attestation for the evidence ZIP. The attestation was signed using the Public Good Sigstore instance and uploaded to the Rekor transparency log. The attestation binds the evidence artifact to the public workflow and commit above.

## Cross-platform corroboration

The same stabilized dispatcher produced **120/120** on Windows x64 with SWI-Prolog 10.0.2 in **78,185 ms**, failures `[]`. A second Windows repetition is recorded separately to test run-to-run stability.

## Scope limitation

This proves reproducible execution of the stated code on the ARC-AGI-2 **public evaluation** data in the upstream repository. It is not an ARC Prize Verified semi-private score, does not establish hidden-set generalisation, and is not a certificate of general intelligence.
