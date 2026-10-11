#!/usr/bin/env python3
"""Offline Kaggle entry point for the MERENVAY ARC-AGI-2 verification candidate."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

INPUT_ROOT = Path(os.environ.get("KAGGLE_INPUT_ROOT", "/kaggle/input"))
WORKING_ROOT = Path(os.environ.get("KAGGLE_WORKING_ROOT", "/kaggle/working"))


def find_challenges() -> Path:
    patterns = [
        "**/arc-agi_test_challenges.json",
        "**/arc-agi-2_test_challenges.json",
        "**/*test*challenges*.json",
        "**/*evaluation*challenges*.json",
    ]
    candidates = []
    for pattern in patterns:
        candidates.extend(INPUT_ROOT.glob(pattern))
        if candidates:
            break
    unique = sorted({p.resolve() for p in candidates if p.is_file()})
    if not unique:
        raise FileNotFoundError(f"Could not locate ARC challenge JSON under {INPUT_ROOT}")
    return unique[0]


def locate_package() -> Path:
    matches = sorted(INPUT_ROOT.glob("**/OFFLINE_BUNDLE_README.md"))
    if not matches:
        raise FileNotFoundError("Attach the MERENVAY offline bundle dataset")
    return matches[0].parent


def main() -> None:
    package = locate_package()
    challenges = find_challenges()
    work = WORKING_ROOT / "merenvay_arc2"
    WORKING_ROOT.mkdir(parents=True, exist_ok=True)
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(package, work)

    swipl = work / "runtime" / "swi-portable" / "swipl-portable"
    app = work / "app"
    benchmark = app / "Mentova" / "src" / "mentova" / "games" / "arc_benchmark_2.pl"
    output = WORKING_ROOT / "submission.json"

    cmd = [
        "python",
        str(app / "build_submission.py"),
        "--challenges", str(challenges),
        "--benchmark-file", str(benchmark),
        "--output", str(output),
        "--swipl", str(swipl),
        "--timeout", "39600",
    ]
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    subprocess.run(cmd, env=env, check=True)

    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("submission.json was not produced")
    print(f"submission.json ready: {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
