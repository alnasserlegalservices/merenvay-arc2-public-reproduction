# GitHub-hosted reproduction receipt

## Result

A GitHub-hosted runner independently executed the public reproduction workflow from a clean checkout.

- Workflow: `Verify ARC-AGI-2 Public Result`
- Run ID: `37768344525`
- Job ID: `113281400304`
- Runner: GitHub-hosted Azure runner, Ubuntu 24.04.5 LTS
- SWI-Prolog: 9.0.4 for x86_64-linux
- Upstream Mentova commit: `d117c699416692cac7ceb951b09f2cdb484a89a6`
- Patch application: success, 25 insertions, no transformation-rule changes
- Exact result: **120/120 tasks**
- Solver elapsed time: **50,871 ms**
- Wall-clock solver time: **51.63 seconds**
- Failed tasks: `[]`

## Evidence

- Workflow run: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37768344525
- Evidence artifact: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/actions/runs/37768344525/artifacts/11546801467
- Artifact ID: `11546801467`
- Artifact service digest: `sha256:a274ea80aa90c79f4924cc1fd45fb51f7b89174a89cfc43b18aa98a4a778fce4`
- Inner evidence ZIP SHA-256: `bbcd5b26a618bb752b399446654682730f9426465f1c12fc6b93113650b8343e`
- GitHub artifact attestation: https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/attestations/53907094
- Sigstore Rekor transparency-log entry: https://search.sigstore.dev?logIndex=3146941983

## Files inside the evidence artifact

- `github_actions_public_run.log` — SHA-256 `73c3837fa4d525db08bb714a2a0b98e376b5a4eb956a782f1588bbff0500eda1`
- `merenvay_dispatch_fix.patch` — SHA-256 `20b537e969fa25f829b9b9fbe32bfdb11ab98e7a7a688125e15ac4481660ac02`
- `run_native_benchmark.pl` — SHA-256 `46516f5efd776bb19eaec1f9004a412d85104ede657a3fe5b25a4d5fec35373e`
- `swipl_version.txt` — SHA-256 `3ea77e6bd4bc68319e3c43e0dd9895970f2604e191ad7e689d8188b4d8b0997e`
- `upstream_commit.txt` — SHA-256 `22b359de64c7efc8c97d73dc6d39a736271081e529403d50acad90192e44a87d`

## Attestation

GitHub generated a SLSA build-provenance attestation for the evidence ZIP. The attestation was signed using the Public Good Sigstore instance and uploaded to the Rekor transparency log.

## Scope limitation

This proves reproducible execution of the stated code on the ARC-AGI-2 **public evaluation** data in the upstream repository. It is not an ARC Prize Verified semi-private score, does not establish hidden-set generalisation, and is not a certificate of general intelligence.
