#!/usr/bin/env python3
"""Score a frozen ARC submission against public task JSON after prediction.

This script is deliberately separate from the predictor. It is for public
regression testing only and must never be present in a hidden verification path
with access to solutions before predictions are frozen.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_public_tasks(source: Path):
    if not source.is_dir():
        raise ValueError("Public scorer expects a directory of task JSON files")
    tasks = {}
    for path in sorted(source.glob("*.json")):
        tasks[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True, type=Path)
    parser.add_argument("--submission", required=True, type=Path)
    args = parser.parse_args()

    tasks = load_public_tasks(args.tasks)
    submission = json.loads(args.submission.read_text(encoding="utf-8"))

    if set(tasks) != set(submission):
        raise SystemExit(
            f"Task IDs differ: missing={sorted(set(tasks)-set(submission))[:5]} "
            f"extra={sorted(set(submission)-set(tasks))[:5]}"
        )

    total_outputs = 0
    passed_outputs = 0
    passed_all_tasks = 0
    failed = []

    for task_id, task in sorted(tasks.items()):
        expected_tests = task["test"]
        predictions = submission[task_id]
        if len(expected_tests) != len(predictions):
            raise SystemExit(
                f"{task_id}: {len(expected_tests)} expected test outputs, "
                f"{len(predictions)} predictions"
            )

        task_ok = True
        for idx, (test, pred) in enumerate(zip(expected_tests, predictions)):
            expected = test.get("output")
            if expected is None:
                raise SystemExit(f"{task_id}[{idx}] has no public output to score")
            total_outputs += 1
            ok = pred["attempt_1"] == expected or pred["attempt_2"] == expected
            if ok:
                passed_outputs += 1
            else:
                task_ok = False
                failed.append(f"{task_id}:{idx}")

        if task_ok:
            passed_all_tasks += 1

    pct = 100.0 * passed_outputs / total_outputs if total_outputs else 0.0
    print(f"PUBLIC_OUTPUT_SCORE {passed_outputs}/{total_outputs} = {pct:.6f}%")
    print(f"PUBLIC_TASKS_ALL_TESTS_PASSED {passed_all_tasks}/{len(tasks)}")
    print("PUBLIC_FAILED_TEST_OUTPUTS", " ".join(failed) if failed else "[]")


if __name__ == "__main__":
    main()
