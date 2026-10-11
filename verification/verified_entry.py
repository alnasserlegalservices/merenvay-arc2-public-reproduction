#!/usr/bin/env python3
"""One-click ARC-AGI-2 verification entry point for Kaggle.

This script is intentionally answer-isolated:
- it reads challenge JSON only;
- it never reads evaluation solution files;
- it serializes training demonstration outputs and test inputs only;
- prediction happens before any grading because there is no grading step here.

It prepares a submission artifact. It does not claim ARC Prize Verified status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

MENTOVA_REPO = "https://github.com/ai-university-aiu/Mentova.git"
MENTOVA_COMMIT = "d117c699416692cac7ceb951b09f2cdb484a89a6"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def ensure_swipl() -> str:
    existing = shutil.which("swipl")
    if existing:
        print(f"Using SWI-Prolog: {existing}")
        return existing

    if shutil.which("apt-get") is None:
        raise RuntimeError(
            "SWI-Prolog is not installed and apt-get is unavailable. "
            "For ARC Verified runs, use a Kaggle image with internet enabled "
            "or attach an offline SWI-Prolog runtime package."
        )

    run(["apt-get", "update"])
    run(["apt-get", "install", "-y", "swi-prolog-nox"])
    installed = shutil.which("swipl")
    if not installed:
        raise RuntimeError("SWI-Prolog installation completed but swipl is unavailable")
    return installed


def candidate_challenge_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    patterns = [
        "**/arc-agi_test_challenges.json",
        "**/*test*challenges*.json",
        "**/*challenges*.json",
    ]
    seen: set[Path] = set()
    found: list[Path] = []
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            resolved = path.resolve()
            if resolved not in seen and path.is_file():
                seen.add(resolved)
                found.append(path)
    return found


def locate_challenges(explicit: Path | None, input_root: Path) -> Path:
    if explicit:
        if not explicit.is_file():
            raise FileNotFoundError(f"Challenge file not found: {explicit}")
        return explicit

    env_path = os.environ.get("ARC_CHALLENGES")
    if env_path:
        path = Path(env_path)
        if not path.is_file():
            raise FileNotFoundError(f"ARC_CHALLENGES does not exist: {path}")
        return path

    found = candidate_challenge_files(input_root)
    if not found:
        raise FileNotFoundError(
            f"No ARC challenge JSON found under {input_root}. "
            "Set ARC_CHALLENGES to the swapped evaluation challenge file."
        )

    test_named = [p for p in found if "test" in p.name.lower()]
    if len(test_named) == 1:
        return test_named[0]
    if len(test_named) > 1:
        raise RuntimeError(
            "Multiple test challenge files found; set ARC_CHALLENGES explicitly:\n"
            + "\n".join(str(p) for p in test_named)
        )

    if len(found) == 1:
        return found[0]

    raise RuntimeError(
        "Multiple challenge files found and none is uniquely identifiable as test data; "
        "set ARC_CHALLENGES explicitly:\n" + "\n".join(str(p) for p in found)
    )


def validate_no_solution_dependency(repo_root: Path) -> None:
    files = [
        repo_root / "verification" / "challenges_to_prolog.py",
        repo_root / "verification" / "predict_unseen.pl",
        repo_root / "verification" / "build_submission.py",
    ]
    forbidden = ("evaluation_solutions", "test_out", "expected_output")
    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        # "test outputs" can appear in comments; these exact solution-file/code tokens may not.
        for token in forbidden:
            if token in text:
                raise RuntimeError(f"Forbidden solution dependency token {token!r} in {path}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clone_mentova(workdir: Path) -> Path:
    target = workdir / "Mentova"
    if target.exists():
        shutil.rmtree(target)
    run(["git", "clone", "--no-tags", MENTOVA_REPO, str(target)])
    run(["git", "checkout", MENTOVA_COMMIT], cwd=target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenges", type=Path)
    parser.add_argument("--input-root", type=Path, default=Path("/kaggle/input"))
    parser.add_argument("--output", type=Path, default=Path("/kaggle/working/submission.json"))
    parser.add_argument("--workdir", type=Path, default=Path("/kaggle/working/merenvay-arc-verified"))
    parser.add_argument("--skip-swipl-install", action="store_true")
    args = parser.parse_args()

    started = time.time()
    repo_root = Path(__file__).resolve().parents[1]
    validate_no_solution_dependency(repo_root)

    swipl = shutil.which("swipl") if args.skip_swipl_install else ensure_swipl()
    if not swipl:
        raise RuntimeError("swipl is required")

    challenges = locate_challenges(args.challenges, args.input_root)
    print(f"Challenge file: {challenges}")

    args.workdir.mkdir(parents=True, exist_ok=True)
    mentova = clone_mentova(args.workdir)
    benchmark = mentova / "src" / "mentova" / "games" / "arc_benchmark_2.pl"
    patch = repo_root / "merenvay_dispatch_fix.patch"

    run(["git", "apply", "--check", str(patch)], cwd=mentova)
    run(["git", "apply", str(patch)], cwd=mentova)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    builder = repo_root / "verification" / "build_submission.py"
    run(
        [
            sys.executable,
            str(builder),
            "--challenges",
            str(challenges),
            "--benchmark-file",
            str(benchmark),
            "--output",
            str(args.output),
            "--swipl",
            str(swipl),
            "--timeout",
            "39600",
        ],
        cwd=repo_root,
    )

    submission = json.loads(args.output.read_text(encoding="utf-8"))
    challenge_count = len(submission)
    prediction_count = sum(len(v) for v in submission.values())
    elapsed = time.time() - started

    print("VERIFICATION_ENTRY_OK")
    print(f"tasks={challenge_count}")
    print(f"test_inputs={prediction_count}")
    print(f"elapsed_seconds={elapsed:.3f}")
    print(f"submission_sha256={sha256_file(args.output)}")
    print(f"output={args.output}")
    print(
        "CLAIM_BOUNDARY: submission tooling only; no ARC Prize Verified status, "
        "no hidden-set score, no generalisation claim."
    )


if __name__ == "__main__":
    main()
