# MERENVAY E-RNA v2 publication erratum

14 November 2026. This sidecar accompanies the unchanged 10 November development probe; it does not amend the frozen code, data, predictions, preregistration or manifest.

## Corrected interpretation

The recorded result is 1/40 for the symbolic baseline, 1/40 for the generator without residual proposals, and 2/40 with them, on public **training** tasks. Feedback vs no-feedback has one discordance, below the preregistered reporting threshold of ten. It does not establish improved ARC performance, generalization, novelty, a ranking, or whole-engine validation.

## Corrections to the historical description

1. **Parameter support is unequal.** The arms share operator implementations, static seeds and a random sampler. Residual derivation can produce values beyond sampler support: translation beyond ±3, scale through 5 rather than 2/3, tile ratios through 4 rather than 1–3, larger attribute keys and more mapping entries. Replace the historical “same parameter family / only difference” description with: “The arms compare complete proposal policies, including witness-conditioned parameters outside sampler support; this does not isolate residual information under matched support.”

2. **The principal control is weak.** The mirror-composition success is inside sampler support. A static shape proposal or systematic two-mirror enumeration is a plausible alternative explanation. Neither stronger control was run in v2. The trace demonstrates a residual-conditioned extension, not that residual feedback is necessary.

3. **Caps are not total work.** Residual analysis, witness prechecks and baseline color-map fitting include work outside candidate/check counters. The baseline also exhausts its grammar earlier. `step_applications` counts scheduled program length before execution, even when an early operator fails; it is not a count of completed primitive operations. Do not infer equal compute or a speed advantage.

4. **This is an exposed development sample.** The 40 tasks are a lexicographic slice of a public training split. Designer/model familiarity is not excluded. Derivation uses one failed witness, then checks children against all demonstrations; it does not aggregate residual evidence across all pairs before proposing a rule.

5. **Learning claims are task-local.** Operators and derivation rules are hand-designed and programs have at most two steps. There is no validated persistent-memory update or transfer to a distinct task. Acceptance of a child on the current task is not evidence of learned generalization.

6. **One packaged test is vacuous.** `tests/test_erna2.py` compares `derive_children(... )[:0]` with `[]`. Every list slice of that form is empty, so a pass does not verify the claimed absence of children. The fixture itself is repairable by a color permutation; simply deleting the slice would not correct its expected outcome. The frozen source remains unchanged, and the test's passing result is disclosed with this limitation.

7. **Chronology and isolation are limited.** Local hashes and freeze files establish consistency, not externally authenticated chronology. Challenge/answer separation on one host is not an OS sandbox. The original configured Claude label does not independently establish actual serving-model identity.

## Fresh reproduction of the original artifact

### Yield clarification and subsequent sampler diagnostic

Five residual-derived programs in the stored feedback traces matched all training demonstrations: three on `00d62c1b`, already solved by a seed, and two on `0c786b71` (candidates 24 and 25, with the mirror orders swapped). Candidate 24 was selected. The reported one selected correct answer concerns the recorded residual-derived selection, not a proof that the residual mechanism was necessary.

The author's subsequent [post-hoc script and retained output](posthoc/README.md) are supplied separately from the frozen experiment. Its two identified matching recipes have combined theoretical probability `1/4096` per sampler draw. Under a fixed 153-independent-draw model, the probability of seeing either is approximately 3.7%; absence is therefore unsurprising. A reported 600,000-draw Monte Carlo found 152 matches and those two recipes only, but is not exhaustive proof that no other programs in the sampler support match. This calculation does not estimate the probability that luck caused the score difference, establish robustness across seeds, or demonstrate a causal feedback benefit. The publication workflow checked the formula and the stored acceptance records but did not rerun the Monte Carlo. Calculations use training pairs; the loader reads the complete labeled public task file, so no label-inaccessibility claim is made.

### Replay evidence

The publication replay on 14 November reproduced all three prediction files byte for byte and retained the 1/40, 1/40, 2/40 result. All 120 decompressed trace payloads matched; compressed gzip containers differed. All 184 original manifest entries still match, and all 40 task blobs match the pinned official dataset tree. Eighteen packaged tests passed, subject to correction 6 above. See [the receipt](evidence/reproduction_receipt.json).

This updates the earlier draft review's statement that it had not freshly rerun inference. It is a replay of the same exposed tasks, not a fresh held-out experiment, external human validation, or an official score verification. Host-specific wall times do not replace the original measurements or establish equal compute.

## Publication status and scope

The [original archive](archive/MERENVAY_E_RNA_v2.zip), [producing code](code/), [preregistration](code/prereg.json), result evidence, material-input disclosure and this erratum are supplied together. Licensing is stated prospectively in [LICENSE_SCOPE.md](LICENSE_SCOPE.md), independently of the dataset's Apache-2.0 terms. The historical README's unpublished/no-license wording is retained as historical documentation, not the current release status.

[Matt's 10 November guidance](https://github.com/arcprize/ARC-AGI-Community-Leaderboard/pull/62#issuecomment-6771731333) invited a new PR with a concrete mechanism, scoped result, code, reproduction instructions and material-input disclosure. It did not require completing v3 first. A new PR requests review; it does not imply acceptance of distinctiveness. V3 remains a separate, unfrozen follow-up.
