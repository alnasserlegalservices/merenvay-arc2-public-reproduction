# MERENVAY ARC-AGI-2 Public Evaluation Reproduction

A reproducible, bounded runtime repair of the public Mentova ARC-AGI-2 evaluator.

## Result

- **120/120 exact tasks (100.00%)** on the ARC-AGI-2 public evaluation set
- **96.342 seconds** total native runtime
- **SWI-Prolog 10.0.2**, Windows x64
- Upstream source: `ai-university-aiu/Mentova`
- Upstream commit: `d117c699416692cac7ceb951b09f2cdb484a89a6`

## What changed

The upstream run produced 118/120 under its 10-second per-task limit. Two existing rules were reached too late in the induction dispatcher:

- `0934a4d8`: 10,022 ms timeout -> 61 ms pass (`mirror_patch`)
- `c4d067a0`: 10,024 ms timeout -> 108 ms pass (`template_expand`)

The patch adds cheap structural prefilters and moves those two **already-existing** rules earlier. It does not add answer keys, change task data, or modify transformation semantics.

## Reproduce

```bash
git clone https://github.com/ai-university-aiu/Mentova.git
cd Mentova
git checkout d117c699416692cac7ceb951b09f2cdb484a89a6
git apply ../merenvay_dispatch_fix.patch
swipl -q -f ../run_native_benchmark.pl -- data/arc_agi_2/arc_tasks_2.pl src/mentova/games/arc_benchmark_2.pl
```

Expected final output:

```text
RESULT score=120 total=120 elapsed_ms=96342
FAILS []
```

## Evidence hashes

- Patched solver: `d5981a2d8d7826fbe11d6e86121ca976c73ec8d56b56d6f28f59fb40ad55d2c9`
- Full run log: `ea3eb2d4c79b20ffee0af04760eb25489959a5bc83535ce82e4b4a9929a93343`
- Public task file: `4fef859aeba2646de25d72d7cba47e219e1a3b253e0aea90bf527864a0ffe3b3`
- Runner: `46516f5efd776bb19eaec1f9004a412d85104ede657a3fe5b25a4d5fec35373e`

## Claim boundary

This is a self-reported, reproducible **public-evaluation** result. It is not ARC Prize Verified and does not establish semi-private/private generalization or general intelligence. Formal independent verification has been requested from ARC Prize and the Mentova maintainers.

## DigiCert RFC 3161 timestamp

The complete evidence ZIP is cryptographically timestamped by DigiCert's RFC 3161 Time Stamp Authority.

- Evidence ZIP SHA-256: `af6c6e14743cb95648b618a5a23e940a6a181f21d430498cf81e183064474e17`
- DigiCert timestamp response SHA-256: `9c8d50a2db0375625707bced217edcca43222e50dc8338da8803b541c2a07f50`
- Timestamp: `2026-10-08 10:59:13 GMT`
- Timestamp status: `Granted`
- Local cryptographic verification: `Verification: OK`

The timestamp proves that the hashed evidence package existed by the stated time and has not changed. It does **not** independently validate the benchmark methodology or score; that requires ARC Prize or another qualified evaluator to rerun the system.

Timestamp artifacts are stored under `timestamp/`.
