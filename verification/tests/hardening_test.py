#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
VERIFICATION = HERE.parent
BUILD = VERIFICATION / "build_submission.py"
FIXTURE_BENCH = HERE / "fixture_benchmark.pl"
HANG_BENCH = HERE / "hang_benchmark.pl"
CRASH_BENCH = HERE / "crash_benchmark.pl"


def run_builder(challenges: Path, benchmark: Path, output: Path, *, env=None, swipl="swipl"):
    cmd = [
        sys.executable,
        str(BUILD),
        "--challenges", str(challenges),
        "--benchmark-file", str(benchmark),
        "--output", str(output),
        "--swipl", str(swipl),
        "--timeout", "30",
    ]
    return subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def flip_task(a: int, b: int):
    return {
        "train": [
            {"input": [[a, 0], [0, 0]], "output": [[0, a], [0, 0]]},
            {"input": [[a, b], [0, 0]], "output": [[b, a], [0, 0]]},
        ],
        "test": [
            {"input": [[b, 0], [a, b]]},
        ],
    }


def test_id_order_and_path_invariance(tmp: Path) -> None:
    tasks_a = {
        "task_alpha": flip_task(1, 2),
        "task_beta": flip_task(3, 4),
    }
    tasks_reordered = {
        "task_beta": tasks_a["task_beta"],
        "task_alpha": tasks_a["task_alpha"],
    }
    tasks_renamed = {
        "renamed_one": tasks_a["task_alpha"],
        "renamed_two": tasks_a["task_beta"],
    }

    a = tmp / "a" / "challenges.json"
    b = tmp / "deep" / "different" / "reordered.json"
    c = tmp / "renamed.json"
    write_json(a, tasks_a)
    write_json(b, tasks_reordered)
    write_json(c, tasks_renamed)

    out_a = tmp / "out_a.json"
    out_b = tmp / "out_b.json"
    out_c = tmp / "out_c.json"

    for src, out in [(a, out_a), (b, out_b), (c, out_c)]:
        proc = run_builder(src, FIXTURE_BENCH, out)
        if proc.returncode != 0:
            raise AssertionError(proc.stderr + proc.stdout)

    sa, sb, sc = load(out_a), load(out_b), load(out_c)

    # Same IDs/content with different JSON insertion order and filesystem path.
    assert sa == sb, (sa, sb)

    # Renaming task IDs must not change predictions for the same task content.
    assert sa["task_alpha"] == sc["renamed_one"]
    assert sa["task_beta"] == sc["renamed_two"]


def failure_task():
    return {
        "failure_case": {
            "train": [
                {"input": [[1, 0], [0, 0]], "output": [[0, 1], [0, 0]]}
            ],
            "test": [
                {"input": [[4, 0], [5, 6]]}
            ],
        }
    }


def test_timeout_and_crash_fallback(tmp: Path) -> None:
    src = tmp / "failure.json"
    write_json(src, failure_task())

    env = os.environ.copy()
    env["MERENVAY_TASK_TIMEOUT"] = "0.05"

    for bench, name in [(HANG_BENCH, "hang"), (CRASH_BENCH, "crash")]:
        out = tmp / f"{name}.json"
        proc = run_builder(src, bench, out, env=env)
        if proc.returncode != 0:
            raise AssertionError(proc.stderr + proc.stdout)
        data = load(out)
        expected_identity = [[4, 0], [5, 6]]
        assert data["failure_case"][0]["attempt_1"] == expected_identity
        assert data["failure_case"][0]["attempt_2"] == expected_identity


def test_atomic_output_preservation(tmp: Path) -> None:
    src = tmp / "atomic.json"
    write_json(src, {"fixture_flip": flip_task(1, 2)})

    fake = tmp / "fake-swipl"
    fake.write_text("#!/usr/bin/env bash\necho 'NOT JSON'\nexit 0\n", encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)

    out = tmp / "submission.json"
    sentinel = '{"sentinel":true}'
    out.write_text(sentinel, encoding="utf-8")

    proc = run_builder(src, FIXTURE_BENCH, out, swipl=fake)
    assert proc.returncode != 0, proc.stdout
    assert out.read_text(encoding="utf-8") == sentinel


def main() -> None:
    if shutil.which("swipl") is None:
        raise SystemExit("swipl is required for hardening tests")

    with tempfile.TemporaryDirectory(prefix="merenvay_hardening_") as td:
        root = Path(td)
        test_id_order_and_path_invariance(root / "invariance")
        test_timeout_and_crash_fallback(root / "failure")
        test_atomic_output_preservation(root / "atomic")

    print("HARDENING_TESTS_OK")


if __name__ == "__main__":
    main()
