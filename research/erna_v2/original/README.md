# MERENVAY E-RNA v2: object-level residual-feedback probe

Run date: 10 November 2026. Local, self-reported, unpublished. No PR, no license, no external message.

## Result first

Development sample: 40 public ARC-AGI-2 **training** tasks (fixed by `prereg.json` before any solver code or task content). One scored run, results in `results/run1/`.

| Arm | Exact test outputs (pass@2) | Fully solved tasks | Candidates / checks | Wall time |
|---|---:|---:|---:|---:|
| Pinned symbolic baseline | 1 / 40 | 1 / 40 (`0d3d703e`) | 3,205 / 10,260 | 1.39 s |
| New generator, **no** feedback (seeds + random restarts) | 1 / 40 | 1 / 40 (`00d62c1b`) | 5,120 / 16,384 | 1.91 s |
| Same generator, **with** residual feedback | 2 / 40 | 2 / 40 (`00d62c1b`, `0c786b71`) | 5,120 / 16,384 | 2.23 s |

Feedback vs no-feedback differ on **one** task. The preregistered rule says a comparison with fewer than 10 discordant tasks is uninformative, so **this run does not show that feedback improves ARC performance**. It shows one real, inspectable instance where a residual changed the next attempt (below), and a list of where the method fails.

Work is **not** equal: the baseline's grammar is finite and stopped early (3,205 candidates); both new arms exhausted the 128-candidate cap on every task. Caps are equal, CPU time is not. Wall times are single descriptive measurements.

## What the feedback loop does (one real trace)

Task `0c786b71`, feedback arm. Seed candidate `[mirror_concat(h, before)]` fails on training pair 0 (36 residual cells). The residual says the output doubles one more dimension than the prediction, so the generator derives the child `[mirror_concat(h, before), mirror_concat(v, before)]`, checks that it fixes the witness pair exactly, then evaluates it on all pairs. It is accepted and solves the test output. The no-feedback arm has the same seeds and the same sampler but its 128 candidates did not include this two-step program. That is a statement about this seed and this budget: the program lies inside the sampler's family, so a larger budget or another seed could reach it without feedback. The family is small, so this is a real limit on what the one-task difference means. The trace (`results/run1/traces/feedback/0c786b71.json.gz`) stores parent, witness pair, derivation text and per-pair outcomes.

Overall yield of the loop: 1,476 feedback pair analyses, **138 derived children, 1 selected for a correct answer.** Derivation types: per-object consistent recolor 83, functional color change 25, output smaller than prediction (crop) 14, displacement 9, background fill 5, output doubles one dimension 2.

## What was implemented

`erna2.py` (standard library only). A hypothesis is a JSON program of at most two steps over: identity, rotate/flip (7), color map, translate one color, gravity, crop (bounding box / largest / smallest object / by color), fill enclosed background, recolor objects by attribute (size, extreme size, border contact, height, width), upscale, tile, mirror-concatenate. Objects are connected components.

Both generator arms share identical first-demonstration seeds, an identical seeded random sampler over the **same** parameter family, and identical budgets. The only difference: after a candidate fails on a training pair, the feedback arm derives child programs from that pair's cell residuals (color-change map, fill color, per-object recolor map, translation offset, output-shape ratio) and tries them before the sampler. A child is queued only if it exactly fixes the witness pair; it is accepted only if it matches every training pair.

All operators, attributes, orderings and derivation rules are hand-designed. Nothing is discovered. Two steps maximum.

## Three diagnosed failures (nothing was changed after seeing them)

1. **`0d3d703e`, global color permutation. The baseline solved it, the new arms did not.** The baseline fits one color map across all demonstrations. The new generator induces its color-map seed from demonstration 0 only (`5→1, 6→2, 8→9`); it matches pair 0 and fails pairs 1 to 3 (6, 9 and 9 wrong cells). Its 17 derived children use one witness pair's residual and never aggregate evidence across pairs. Missing: cross-pair aggregation.
2. **`007bbfb7` and `00576224`, output grows by self-referential tiling.** Zero derived children, identity fallback. Upscale, tile and mirror-concatenate are not the right construction (conditional masking by the input itself, alternating flips), so no derivation reproduces even the witness pair. Missing: conditional and self-referential output construction.
3. **`009d5c81`, witness overfitting.** 46 derived children, none accepted. Example: `recolor_objects(size)` with map `1→0, 31→7, 5→0` memorizes object sizes from pair 0, passes it and fails the other 4 pairs. The per-object derivation fired 83 times in total, mostly memorizing. Missing: generalization constraints on derived maps.

Also: 29 of 40 tasks keep dimensions in all training pairs, yet most need object-level logic (movement, counting, pattern completion) outside this operator set. 38 of 40 tasks ended in identity fallback for the feedback arm.

## Provenance and chronology

- Dataset: `arcprize/ARC-AGI-2`, commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`, split `data/training`. The task IDs were taken from the git tree listing only (blobs not fetched); the first 40 of the 1,000 IDs sorted bytewise. `prereg.json` (SHA-256 `a808ec6df94c643dc176bf4c8119bde44039b04c21d5beca7bd7cdc499862b71`) was written before solver code and before any task content was read. The harness refuses to run if the file differs.
- Task files are the unchanged git blobs; every file matches its upstream SHA-1 (`data/source_metadata.json`).
- Solver and tests were developed on procedurally built synthetic fixtures only. One scored run. No code change after it. Re-running produced byte-identical predictions for all three arms.
- Baseline: `vendor/generic_solver.py`, unchanged, SHA-256 `37084696d0040d26ce08fc3d18e0cea20f78436152abb4ba59b9a24add01e769` (upstream commit `7a89d10f82cb5d6767a35c8db9017437cd0b3081`), run through the v1 instrumented wrapper that records all training pairs per candidate.
- The v1 probe's 24 ARC-AGI-2 public-evaluation tasks (0/37 for every arm) were not used for development or tuning here; that failed result stands.

## Disclosures (material human/model input)

- Solver, fixtures, harness and this README were written by an Anthropic Claude model in a Cowork session (configured as `claude-sonnet-5-5`; the serving model may differ), at the user's request. No task-specific prompts, solutions or hints are used at inference. No LLM, network or randomness beyond the recorded seed at inference.
- The operator set came from general ARC knowledge, which includes familiarity with public ARC-1 tasks that also appear in the ARC-AGI-2 training split. **The dev sample is not held out from the designer's or any model's prior knowledge.** Both solved tasks (`00d62c1b`, fill enclosed region; `0c786b71`, mirror tiling) are well-known task types.
- The sample is a lexicographic slice of a public split, not random, not hidden.
- Data-flow separation (challenge file vs scoring answers, separate processes, hash freeze) is inspected, not an OS sandbox. Everything runs on one host.
- Unit tests include a deliberately mechanism-aligned fixture (two-step program revealed by residuals). It is a unit test, not evidence of ARC performance.

## Reproduce

Python 3 standard library only. No network or packages at inference.

```sh
python -B -m unittest discover -s tests -v          # 18 tests
python -B run_experiment.py run --out results/reproduction   # ~6 s; directory must not exist
python -B run_experiment.py score --out results/run1         # re-verify hashes and re-score the stored run
```

`results/run1/prediction_freeze.json` holds hashes of all predictions, traces and source files; the scorer refuses to run if any changed. `PACKAGE_SHA256.json` lists every file in this package.

## Claims not made

No competition or leaderboard score. No hidden-set generalization. No equal-compute guarantee. No causal claim that feedback improves ARC performance (1 discordant task; preregistered threshold 10). No claim of novelty beyond the narrow residual-to-program derivations listed. Not general program synthesis, not the full MERENVAY theory.

## Next step (not done here)

Aggregate residuals across all training pairs before deriving a child (fixes failure 1 and constrains failure 3), add output-construction operators for failure 2, and evaluate on a **new** preregistered sample large enough to give at least 10 discordant tasks. Keep this result as is. Decide a license and review upstream licenses before any publication.
