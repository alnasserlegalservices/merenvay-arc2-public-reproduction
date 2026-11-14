# E-RNA v2: post hoc work-accounting audit

This is an independent replay measurement of the frozen local v2 package, **not** a preregistered result. Original ZIP SHA-256: `273b4bd11b72907e660723b75ce066bb10537d8fa1a5dda2803f4e4899730d6c`. The audit accepts that ZIP or an extracted `object_feedback/` directory; both sources were read only and gave the same counts and byte-identical predictions.

The audit loaded only `challenge_only.json`, the solver, the preregistered budgets, frozen metadata and predictions. It did not extract or parse test answers or raw task files. Before replay, it pinned `prediction_freeze.json` to the original v2 SHA-256 (`3aab7888eda77625b3d51decb60879a531145a38f4d187533293cb193b623e59`), then checked its four code hashes, hashes for the challenge, input manifest and two prediction files, plus the input manifest's preregistration and challenge hashes. It wrapped `erna2.apply_step` in memory and separately counted calls from the `derive_children` witness prefilter. Both replayed arms produced byte-identical prediction files to those frozen in `results/run1/`.

| Arm | All `apply_step` calls | Calls inside child prefilter | Other calls |
|---|---:|---:|---:|
| No feedback | 25,296 | 0 | 25,296 |
| Feedback | 29,051 | 3,553 | 25,498 |

Feedback made **3,755 more calls, or 14.844% relative to no feedback**, despite both arms reporting 5,120 candidates and 16,384 training-pair checks. The 3,553 prefilter calls are absent from those counters and the reported `step_applications`. This count does not show a 14.844% CPU-time increase: different operations have different cost. It also excludes residual scans, connected-component analysis, and cell visits. Therefore the original arm comparison has equal nominal candidate/check caps, not matched real work.

Reproduce from the public repository root (Python 3 standard library only):

```sh
python -B evidence/work_accounting_posthoc.py object_feedback --out /tmp/work_accounting_posthoc.json
```

For the original ZIP, substitute its path for `object_feedback`. The archived directory-mode output is `evidence/work_accounting_posthoc.json`. This audit does not prove the original run's chronology, independently authenticate upstream task files, or establish a causal feedback advantage.
