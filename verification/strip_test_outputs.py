#!/usr/bin/env python3
"""Create ARC challenge JSON with test outputs removed.

Useful for answer-isolated regression: scoring material remains outside the
prediction environment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_tasks(source: Path):
    if source.is_dir():
        tasks = {}
        for path in sorted(source.glob("*.json")):
            tasks[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        return tasks
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Input must be task directory or task-id JSON map")
    return data


def strip_outputs(tasks):
    clean = {}
    for task_id, task in tasks.items():
        train = task["train"]
        tests = task["test"]
        clean[task_id] = {
            "train": [
                {"input": pair["input"], "output": pair["output"]}
                for pair in train
            ],
            "test": [
                {"input": test["input"]}
                for test in tests
            ],
        }
    return clean


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("dest", type=Path)
    args = parser.parse_args()

    clean = strip_outputs(load_tasks(args.source))
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    args.dest.write_text(
        json.dumps(clean, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Wrote {len(clean)} challenge-only tasks to {args.dest}")


if __name__ == "__main__":
    main()
