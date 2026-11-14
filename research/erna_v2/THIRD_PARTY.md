# Sources and license treatment

| Material | Origin | Treatment |
|---|---|---|
| Forty original training tasks and their underlying content | `arcprize/ARC-AGI-2`, commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`, `data/training/` | Unmodified task bytes verified against official Git blobs; retain Apache-2.0 license and original attribution. Projections reorganize task fields. |
| Standalone `vendor/generic_solver.py` | This owner's `merenvay-arc2-public-reproduction`, commit `7a89d10f82cb5d6767a35c8db9017437cd0b3081` | Exact source identity verified (Git blob `238ae3136bacbd95ab47a616582d42a578d445d6`); no earlier implementation license inferred. This release explicitly covers the supplied project copy under `LICENSE_SCOPE.md`. |
| `vendor/evaluate_public.py` and historical baseline README | Retained project baseline material in the frozen package | Historical context is preserved. The standalone evaluator is not invoked by the v2 reproduction commands. |
| Python standard library | Runtime dependency | Not redistributed as part of this package. |

No external solver, model weights or Mentova implementation is included in the v2 solving path. The historical project repository may contain other research; this release's license scope does not extend to it. Public source identity and a license grant are different questions; neither dataset licensing nor the old root NOTICE establishes rights in independent solver code.

The official dataset tree inspected for attribution contains no separate NOTICE file. Its full original LICENSE, including its attribution statement, is retained unchanged in `LICENSES/ARC-AGI-2-Apache-2.0.txt`.
