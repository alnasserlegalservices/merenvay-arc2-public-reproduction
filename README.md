# MERENVAY E-RNA reproducibility package

Release assembled on 10 November 2026. It includes two experiments on the public ARC-AGI-2 training split. Both use the pinned official data revision `f3283f727488ad98fe575ea6a5ac981e4a188e49`. The cohorts are separate.

## Reproduce

Extract the ZIP and run `python3 -B verify_bundle.py` from the extracted directory. Python standard library only. The verifier creates new temporary runs and verifies predictions against the preserved hashes. The inference processes receive training pairs and test inputs. A separate scoring step reads the expected test outputs after the predictions are frozen. The files remain on the same machine.

| Experiment | Outcome |
| --- | --- |
| 40-task object-feedback development run | Symbolic baseline 1/40, same generator without feedback 1/40, generator with feedback 2/40. |
| 24-task joint-constraints experiment | Five variants each scored 0/26 test outputs. |
| Previously inspected diagnostic `0d3d703e` | Direct all-pair color fitting, joint repair and the symbolic baseline all solved the task. |

On task `0c786b71`, parent 21 applies a horizontal mirror-and-concatenate. It leaves 36 grid differences on each of the three training pairs, counting cells outside the predicted shape. The shape discrepancy on pair 0 leads to child 24, which adds a vertical mirror-and-concatenate. The child matches all three training pairs and the test output. The no-feedback run misses this output under the same seed and search caps. The shared search family already includes this two-step program. The one-task difference is descriptive and below the original protocol's threshold for an informative comparison. Both cohorts were drawn from public training data and may contain familiar task types.

The reconstruction reproduces all three archived object-feedback prediction hashes exactly. The freshly generated compressed mirror trace has a different hash from the prior compressed record. The verifier checks the new trace's parent, child, error counts and score, and reports the compressed-file comparison separately. The source code, benchmark inputs, predictions and logs remain distinct artifacts. The example trace excerpt and compact score records are in `evidence/`. The verifier regenerates the full traces.

## Provenance and publication status

- **Dataset.** ARC-AGI-2 public training data. The upstream Apache-2.0 license is preserved in `ARC-AGI-2-LICENSE.txt`. Task source hashes are in the original and joint-run manifests.
- **Original object-feedback implementation.** Unchanged source from the archived experiment. The object-feedback solver and harness were built with Claude coding assistance. Human involvement included commissioning and reviewing the experimental work. The implementation uses hand-designed operators and no task-specific prompts or hints at inference. The symbolic comparator is pinned to MERENVAY's published `generic_solver.py` at commit `7a89d10f82cb5d6767a35c8db9017437cd0b3081`. The replay and joint constraints experiment used OpenAI coding assistance. No hosted model is invoked at inference.
- **Licenses.** MERENVAY's code and documentation in this release are licensed under MIT (see `LICENSE`). The bundled ARC-AGI-2 task data and training index are under the upstream Apache-2.0 license (see `ARC-AGI-2-LICENSE.txt`).
- **Score scope.** Self-reported ARC-AGI-2 public training slices, with fixed task lists. The 40-task slice result is 2/40 (5%) with feedback. The separate 24-task slice is 0/26 outputs across all variants.

[Matt's review guidance](https://github.com/arcprize/ARC-AGI-Community-Leaderboard/pull/62#issuecomment-6771731333) · [Community contribution requirements](https://github.com/arcprize/ARC-AGI-Community-Leaderboard/blob/main/CONTRIBUTING.md)
