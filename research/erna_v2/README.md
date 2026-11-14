# MERENVAY E-RNA v2: residual-conditioned program proposals

Released 14 November 2026. Original experiment: 10 November 2026.

This is a small, task-local symbolic ARC development probe. After a candidate fails on a training demonstration, hand-written derivation rules use that witness's residual to propose a program extension of at most two steps. Candidate extensions are checked against all demonstrations. Only training-consistent programs are accepted; if none is usable on every test input, the solver emits an explicitly unverified identity fallback. The producing code is public in [code/](code/); the [complete original package](archive/MERENVAY_E_RNA_v2.zip) is preserved byte for byte.

**Read the [erratum](ERRATUM.md) alongside the historical README.** It corrects the original matched-parameter-support claim and explains the weak control, incomplete work accounting, prior-exposure limitations and a vacuous software test. This release is a request for method review, not a claim that distinctiveness has been accepted.

## Recorded development result

One seed-0 run used the first 40 lexicographically sorted IDs in the public ARC-AGI-2 training split at dataset commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`. Each task has one test output and at most two attempts.

| Arm | Exact outputs / fully solved tasks | Candidates | Checks |
|---|---:|---:|---:|
| Frozen symbolic baseline | 1/40 | 3,205 | 10,260 |
| Generator without residual proposals | 1/40 | 5,120 | 16,384 |
| Generator with residual proposals | 2/40 | 5,120 | 16,384 |

There is one feedback-only task and no no-feedback-only tasks. The preregistered ten-discordance threshold is not met. **This result does not establish that feedback improves ARC performance.** These are training-development results, not public-evaluation, competition, hidden-set or ARC Prize Verified scores.

The illustrative additional success, `0c786b71`, follows a failed mirror proposal with a second mirror step. This program is reachable by the sampler; a systematic mirror control or static shape heuristic could also find it. No stronger control was run in v2. Derivation can also emit parameters outside the random sampler's support. The implementation demonstrates a residual-conditioned next attempt, without isolating a causal benefit from residual information.

The [separate post-hoc sampler diagnostic](posthoc/README.md) is retained with explicit limits. Its approximately 3.7% calculation concerns two identified recipes under a fixed-draw probability model; it does not establish a feedback advantage or robustness across seeds.

## Reproduce the frozen package

Python 3 standard library only; there are no LLM or network calls during inference. Download this directory, or clone this repository and enter `research/erna_v2`.

```sh
python3 -m zipfile -e archive/MERENVAY_E_RNA_v2.zip /tmp/merenvay-v2-original
cd /tmp/merenvay-v2-original/MERENVAY_E_RNA_v2
python3 -B -m unittest discover -s tests -v
python3 -B run_experiment.py run --out /tmp/merenvay-v2-reproduction
```

Use a new extraction location and a new output directory. Do not overwrite `results/run1`. The archive contains all producing code, tests, the 40 unmodified task files, original predictions, traces and manifests. The `code/` directory is a byte-identical browsing mirror of the producing source; use the complete archive for reproduction. The original package SHA-256 is:

`273b4bd11b72907e660723b75ce066bb10537d8fa1a5dda2803f4e4899730d6c`

## Publication verification, 14 November 2026

The publication workflow checked all 184 entries of the original package manifest, verified the 40 dataset blobs against the official pinned Git tree, ran the 18 packaged unit tests, and replayed the frozen experiment into a separate output directory. All 18 tests passed; one test has a vacuous assertion and does not verify its stated property.

All three reproduced prediction files were byte-identical to the originals, and the scores, candidate/check counts, discordance and 138 derived children were reproduced. The 120 decompressed trace payloads were also byte-identical. Gzip container bytes differed; no byte-identity claim is made for those containers. Wall times vary by host and are not speed evidence. See the [verification receipt](evidence/reproduction_receipt.json), [original score](evidence/original_score.json) and [reproduced score](evidence/reproduced_score.json).

This is local software reproduction by an AI-assisted workflow, not external human validation or official ARC verification. The archive and original sources were not changed.

## Material human and model input

Mohammed Al Nasser directed this MERENVAY research. The original package reports that an Anthropic Claude model wrote the solver, synthetic fixtures, harness and original documentation in a Cowork session. Its configured label was `claude-sonnet-5-5`; the actual serving-model identity was not independently established. The operator vocabulary, derivation rules and search order are hand-designed. Prior knowledge of public ARC task types is not excluded.

OpenAI Codex assisted with the publication review, final documentation, license/attribution packaging and reproduction on 14 November. Two additional AI agents reviewed the source and submission rules. These are AI reviews, not independent human review. No original solver code or frozen prediction was altered. No task-specific prompts or hints are supplied at inference.

The method has no validated persistent memory or cross-task learning. Local hashes establish consistency, not an independent timestamp of the complete design history. Challenge/answer separation is a data-flow convention on one host, not OS-enforced isolation. The workflow used only the 40 packaged development tasks; it did not open other ARC task contents. Exposure in other sessions remains unknown.

## Licensing and provenance

The Apache-2.0 grant is scoped to this release directory and the specific project files listed in [LICENSE_SCOPE.md](LICENSE_SCOPE.md). It does not apply a license to the rest of MERENVAY or the historical repository. Apache-2.0 permits commercial reuse of the covered files under its terms. Dataset attribution and its original license are retained separately in [NOTICE](NOTICE), [THIRD_PARTY.md](THIRD_PARTY.md) and [LICENSES/](LICENSES/).

The standalone baseline is the unchanged copy from this owner's project at commit `7a89d10f82cb5d6767a35c8db9017437cd0b3081`; it does not import Mentova. Its earlier public availability was not itself a license grant. The release now states a scoped grant for the supplied project copy. The broader MERENVAY brand, logo and private product are outside this release.
