#!/usr/bin/env python3
"""Build ARC Prize submission.json without test-output access.

This wrapper:
  1. converts challenge JSON to answer-isolated Prolog facts,
  2. runs verification/predict_unseen.pl,
  3. validates exact ARC submission shape,
  4. writes submission.json.

It does not score predictions and never reads evaluation solutions.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from challenges_to_prolog import convert, load_tasks


def validate_grid(grid: Any) -> None:
    if not isinstance(grid, list) or not grid:
        raise ValueError("Prediction grid must be a non-empty list")
    if not all(isinstance(row, list) and row for row in grid):
        raise ValueError("Prediction grid rows must be non-empty lists")
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("Prediction grid must be rectangular")
    if len(grid) > 30 or width > 30:
        raise ValueError("Prediction grid exceeds ARC 30x30 limit")
    for row in grid:
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError(f"Invalid prediction cell: {cell!r}")


def run_predictor(
    swipl: str,
    runner: Path,
    task_facts: Path,
    benchmark_file: Path,
    timeout_seconds: int,
) -> list[dict[str, Any]]:
    cmd = [
        swipl,
        "-q",
        "-f",
        str(runner),
        "--",
        str(task_facts),
        str(benchmark_file),
    ]
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Predictor failed with exit code {proc.returncode}\n"
            f"STDERR:\n{proc.stderr}\nSTDOUT:\n{proc.stdout}"
        )

    records: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def validate_submission(
    challenges: dict[str, dict[str, Any]],
    submission: dict[str, list[dict[str, Any]]],
) -> None:
    if set(submission) != set(challenges):
        missing = sorted(set(challenges) - set(submission))
        extra = sorted(set(submission) - set(challenges))
        raise ValueError(f"Task mismatch; missing={missing[:5]}, extra={extra[:5]}")

    for task_id, task in challenges.items():
        expected_tests = task.get("test", [])
        entries = submission[task_id]
        if len(entries) != len(expected_tests):
            raise ValueError(
                f"{task_id}: expected {len(expected_tests)} test predictions, got {len(entries)}"
            )
        for index, entry in enumerate(entries):
            if set(entry) != {"attempt_1", "attempt_2"}:
                raise ValueError(f"{task_id}[{index}]: attempts must be attempt_1 and attempt_2")
            validate_grid(entry["attempt_1"])
            validate_grid(entry["attempt_2"])


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenges", required=True, type=Path)
    parser.add_argument("--benchmark-file", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("submission.json"))
    parser.add_argument("--swipl", default="swipl")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--runner", type=Path, default=here / "predict_unseen.pl")
    args = parser.parse_args()

    challenges = load_tasks(args.challenges)

    with tempfile.TemporaryDirectory(prefix="merenvay_arc_") as temp_dir:
        facts = Path(temp_dir) / "arc_input_tasks.pl"
        convert(args.challenges, facts)
        records = run_predictor(
            args.swipl,
            args.runner,
            facts,
            args.benchmark_file,
            args.timeout,
        )

    submission: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        task_id = record["id"]
        if task_id in submission:
            raise ValueError(f"Duplicate predictor output for task {task_id}")
        submission[task_id] = record["predictions"]

    validate_submission(challenges, submission)
    args.output.write_text(
        json.dumps(submission, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Wrote validated submission for {len(submission)} tasks to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
