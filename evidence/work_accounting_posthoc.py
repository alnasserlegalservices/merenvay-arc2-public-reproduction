#!/usr/bin/env python3
"""Post hoc, label-free call accounting for frozen E-RNA v2 files.

Accepts the original ZIP or an extracted package directory (for example
object_feedback/). It reads only challenge inputs, code, frozen metadata, and
stored predictions. It never opens answers_scoring_only.json or raw task files.
The solver is instrumented in memory; source files remain unchanged.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


PREFIX = "MERENVAY_E_RNA_v2/"
ORIGINAL_FREEZE_SHA256 = "3aab7888eda77625b3d51decb60879a531145a38f4d187533293cb193b623e59"
CODE = ("erna2.py", "vendor/__init__.py", "vendor/generic_solver.py")
ARMS = ("no_feedback", "feedback")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def safe_relative(relative: str) -> str:
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(p in (".", "..") for p in path.parts):
        raise ValueError(f"Unsafe package path: {relative}")
    return relative


@contextmanager
def package_reader(source: Path):
    if source.is_dir():
        def read(relative: str) -> bytes:
            return (source / safe_relative(relative)).read_bytes()
        yield read, {"type": "directory", "directory_name": source.name}
    elif source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            def read(relative: str) -> bytes:
                return archive.read(PREFIX + safe_relative(relative))
            yield read, {"type": "zip", "source_zip_sha256": digest(source.read_bytes())}
    else:
        raise ValueError("Source must be the original ZIP or an extracted package directory")


def verify_frozen_inputs(read) -> dict:
    frozen_bytes = read("results/run1/prediction_freeze.json")
    if digest(frozen_bytes) != ORIGINAL_FREEZE_SHA256:
        raise AssertionError("Prediction freeze differs from the original v2 package")
    freeze = json.loads(frozen_bytes)
    code = freeze["code_sha256"]
    for relative, expected in code.items():
        if digest(read(relative)) != expected:
            raise AssertionError(f"Frozen code mismatch: {relative}")
    frozen_files = (
        "challenge_only.json", "input_manifest.json",
        "no_feedback_predictions.json", "feedback_predictions.json"
    )
    for relative in frozen_files:
        if digest(read("results/run1/" + relative)) != freeze["files"][relative]:
            raise AssertionError(f"Frozen result mismatch: {relative}")
    manifest = json.loads(read("results/run1/input_manifest.json"))
    if digest(read("prereg.json")) != manifest["prereg_sha256"]:
        raise AssertionError("Preregistration differs from input manifest")
    if digest(read("results/run1/challenge_only.json")) != manifest["challenge_sha256"]:
        raise AssertionError("Challenge differs from input manifest")
    return {"original_prediction_freeze_sha256": ORIGINAL_FREEZE_SHA256,
            "code_hashes": len(code), "frozen_file_hashes": len(frozen_files),
            "input_manifest_challenge_and_prereg": True}


def run_audit(source: Path) -> dict:
    with package_reader(source) as (read, source_identity), tempfile.TemporaryDirectory() as root_name:
        verification = verify_frozen_inputs(read)
        root = Path(root_name)
        for relative in CODE:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(read(relative))

        prereg = json.loads(read("prereg.json"))
        challenge = json.loads(read("results/run1/challenge_only.json"))
        sys.path.insert(0, str(root))
        try:
            solver = importlib.import_module("erna2")
            step_original = solver.apply_step
            derive_original = solver.derive_children
            arm_results = {}
            for arm in ARMS:
                calls = {"apply_step_total": 0, "child_prefilter_apply_step": 0}
                in_derivation = False

                def counted_step(step, grid):
                    calls["apply_step_total"] += 1
                    if in_derivation:
                        calls["child_prefilter_apply_step"] += 1
                    return step_original(step, grid)

                def counted_derive(*args, **kwargs):
                    nonlocal in_derivation
                    if in_derivation:
                        raise RuntimeError("Unexpected recursive derivation")
                    in_derivation = True
                    try:
                        return derive_original(*args, **kwargs)
                    finally:
                        in_derivation = False

                solver.apply_step = counted_step
                solver.derive_children = counted_derive
                predictions = {}
                for task_id, task in challenge.items():
                    if set(task) != {"train", "test"} or any(set(test) != {"input"} for test in task["test"]):
                        raise ValueError("Challenge file contains test labels")
                    result = solver.solve(
                        task["train"],
                        [test["input"] for test in task["test"]],
                        feedback=(arm == "feedback"),
                        seed=prereg["seed"],
                        max_candidates=prereg["budgets_per_task"]["max_candidates"],
                        max_checks=prereg["budgets_per_task"]["max_checks"],
                    )
                    predictions[task_id] = result["attempts"]
                actual = canonical_json(predictions)
                expected = read(f"results/run1/{arm}_predictions.json")
                arm_results[arm] = {
                    **calls,
                    "run_path_apply_step": calls["apply_step_total"] - calls["child_prefilter_apply_step"],
                    "frozen_predictions_sha256": digest(expected),
                    "byte_identical_predictions": actual == expected,
                    "tasks": len(predictions),
                }
                solver.apply_step = step_original
                solver.derive_children = derive_original
            if not all(arm_results[a]["byte_identical_predictions"] for a in ARMS):
                raise AssertionError("Instrumented predictions differ from frozen predictions")
        finally:
            sys.path.pop(0)
            for name in ("erna2", "vendor", "vendor.generic_solver"):
                sys.modules.pop(name, None)

    base = arm_results["no_feedback"]["apply_step_total"]
    feedback = arm_results["feedback"]["apply_step_total"]
    return {
        "scope": "Post hoc instrumented replay, not a preregistered run or compute-equivalence test",
        "source": source_identity,
        "frozen_hashes_verified": verification,
        "test_answer_entries_opened": False,
        "arms": arm_results,
        "extra_feedback_apply_step_calls": feedback - base,
        "extra_feedback_calls_percent_of_no_feedback": round(100 * (feedback - base) / base, 3),
        "limitations": [
            "A Python call count is not CPU time or cell-operation cost.",
            "Residual scans, component analysis and other work are not measured.",
            "The replay cannot prove the original run's chronology or number of prior runs."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Original v2 ZIP or extracted object_feedback directory")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_audit(args.source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(json.dumps(result, indent=2, sort_keys=True).encode() + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
