# Prepared new-PR description

Status: the v2 release and submission branch are public. The API could not open the upstream PR because the integration returned HTTP 403 (Resource not accessible by integration). This is the prepared text; it does not assert that a PR exists.

Proposed title: Add MERENVAY E-RNA v2 residual-conditioned development probe

---

This is a new submission following [the 10 November guidance on #62](https://github.com/arcprize/ARC-AGI-Community-Leaderboard/pull/62#issuecomment-6771731333). It requests review of a concrete, task-local residual-to-program proposal mechanism. It does not presume that its distinctiveness has been accepted.

**Producing code, complete frozen package, erratum, license scope and reproduction evidence:** https://github.com/alnasserlegalservices/merenvay-arc2-public-reproduction/tree/08cf1ba38f6600d17370c8f4af8ee1f2dcaf3d4a/research/erna_v2

## Scoped result

One seed-0 development run on the first 40 sorted IDs of the **public ARC-AGI-2 training split**, at dataset commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`, recorded:

| Arm | Exact outputs / fully solved tasks |
|---|---:|
| Frozen symbolic baseline | 1/40 |
| Generator without residual proposals | 1/40 |
| Generator with residual proposals | 2/40 |

Each task has one test output; at most two attempts are permitted. There is one feedback-only discordance and none in the other direction. The preregistered ten-discordance reporting threshold is not met: **this is not evidence that feedback improves ARC performance**.

The YAML uses `set: training-development-40` to avoid presenting 5.0% as a public-evaluation score. There is no v2 public-evaluation, competition, hidden-set or ARC Prize Verified result. Please assess whether this explicitly development-only result is suitable for the showcase.

## Inspectable mechanism and failures

After a candidate fails on a training demonstration, hand-written rules use that witness's residual to propose an extension. Programs have at most two steps. Children must pass every training demonstration before acceptance; if none is usable, the system emits an explicitly unverified identity fallback.

On `0c786b71`, a failed mirror candidate leads to a second mirror step; the stored trace records the parent, witness, derivation and subsequent checks. Across the probe there were 1,476 residual analyses and 138 derived children. Five derived programs matched all demonstrations, but only one recorded task answer used a selected residual-derived program.

Failures are retained: the new generator loses `0d3d703e` to the baseline because it does not aggregate color-map evidence across demonstrations; `007bbfb7` and `00576224` lack a fitting construction; `009d5c81` produces witness-specific maps that fail other demonstrations.

## Limits corrected in the separate erratum

- The no-feedback control is weak: static shape proposals or systematic mirror enumeration could also find the illustrative program.
- Residual derivation has wider parameter support than the sampler. Shared operators and caps do not isolate residual information under matched support.
- Derivation/prechecks and other operations are not fully counted; equal caps do not establish equal compute.
- This exposed, lexicographically selected training sample is not held out from designer/model familiarity. There is one seed, no persistent-memory validation and no cross-task learning claim.
- The post-hoc 3.7% calculation concerns two identified recipes under a fixed 153-independent-draw model. It is not a probability that luck caused the score gap, or proof of seed robustness. The retained Monte Carlo was not repeated by the publication review.
- Local hashes show consistency, not independently authenticated design chronology. Label separation is a one-host data-flow convention, not OS isolation.

## Human/model input and validation

Mohammed Al Nasser directed the research and requested this publication. The original package reports Claude-assisted authorship of the solver, fixtures, harness, preregistration and documentation, configured as `claude-sonnet-5-5`; actual serving-model identity was not independently established. This statement does not claim that Mohammed personally wrote or reviewed every source line.

OpenAI Codex assisted with publication documentation, scoped Apache-2.0 licensing/attribution packaging and reproduction. Two additional AI agents reviewed source and submission rules. These are AI reviews, not independent human validation. The solver makes no LLM or network calls at inference and uses no task-specific prompts or hints.

On 14 November, all 184 original manifest entries and all 40 upstream task blobs were checked. The frozen experiment was replayed into a separate directory: all three prediction files and all 120 decompressed trace payloads matched byte for byte. Scores and counters reproduced. Compressed gzip containers differed. Eighteen packaged tests passed, with one vacuous assertion expressly disclosed. No original solver code, data or prediction was changed.

Reproduction instructions, original and replayed score files, and the detailed receipt are in the linked release. The original archive SHA-256 is `273b4bd11b72907e660723b75ce066bb10537d8fa1a5dda2803f4e4899730d6c`. Dataset notices are retained; the source grant is scoped to the published experiment files. V3 remains a separate, unfrozen follow-up.

Validation: the current repository validator passed locally, including the live public code link.
