"""Reproduce a frozen, local ARC-AGI-2 public evaluation using stdlib only.

This is process/data-flow separation, not a security sandbox. The projection
process opens labelled public task files, but writes only training pairs and
test inputs. The unchanged solver CLI is a separate process given that file.
Only after predictions and a manifest are frozen is a separate scorer launched.
Public labels remain on the host and are not made inaccessible by this script.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


DATASET_URL = "https://github.com/arcprize/ARC-AGI-2"
ROOT = Path(__file__).resolve().parent
SOLVER = ROOT / "generic_solver.py"
SETTINGS = {
    "max_candidates": 256,
    "max_validation_demonstration_checks": 512,
    "validation_check_budget_excludes_fit_map_scans": True,
    "max_attempts_per_test": 2,
    "settings_source": "unchanged generic_solver.py defaults; CLI has no overrides",
}
FALLBACK = (
    "The unchanged solver selects up to two training-consistent programs that "
    "apply to every test input of a task, deduplicating whole-task output "
    "sequences. If none applies, identity is used for every test input; a single "
    "prediction sequence is duplicated into both attempts. The evaluation runner "
    "does not repair failed predictions: process or schema failures abort."
)
BOUNDARY = (
    "The projection process opens official public task JSON containing test "
    "labels and discards the test output fields. The solver is launched through "
    "its unchanged CLI with only a challenge-only JSON path and submission path. "
    "Predictions and their SHA-256 manifest are written before a separate scorer "
    "process reads expected outputs. This is an auditable process/data-flow "
    "boundary, not an OS security sandbox: public labels remain on the host."
)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def write_json(path, data, *, compact=False):
    text = json.dumps(data, sort_keys=True, **({"separators": (",", ":")} if compact else {"indent": 2}))
    Path(path).write_text(text + "\n", encoding="utf-8")


def validate_grid(grid):
    if type(grid) is not list or not 1 <= len(grid) <= 30:
        raise ValueError("Grid must have 1..30 rows")
    width = None
    for row in grid:
        if type(row) is not list or not 1 <= len(row) <= 30:
            raise ValueError("Grid must have 1..30 columns")
        if width is None:
            width = len(row)
        if len(row) != width or any(type(c) is not int or not 0 <= c <= 9 for c in row):
            raise ValueError("Grid must be rectangular with integer colors 0..9")
    return grid


def evaluation_paths(dataset):
    dataset = Path(dataset)
    split_ids = (dataset / "data/evaluation.txt").read_text(encoding="utf-8").splitlines()
    paths = sorted((dataset / "data/evaluation").glob("*.json"))
    if not paths or len(split_ids) != len(set(split_ids)) or set(split_ids) != {p.stem for p in paths}:
        raise ValueError("evaluation.txt must exactly match all evaluation JSON task IDs")
    return paths


def project_task(task):
    """Copy the official task to the only schema accepted by the solver CLI."""
    if type(task) is not dict or set(task) != {"train", "test"}:
        raise ValueError("Invalid official task keys")
    if type(task["train"]) is not list or not task["train"] or type(task["test"]) is not list or not task["test"]:
        raise ValueError("Official tasks require nonempty train and test lists")
    train = []
    for pair in task["train"]:
        if type(pair) is not dict or set(pair) != {"input", "output"}:
            raise ValueError("Invalid official training pair")
        train.append({"input": validate_grid(pair["input"]), "output": validate_grid(pair["output"])})
    tests = []
    for pair in task["test"]:
        if type(pair) is not dict or set(pair) != {"input", "output"}:
            raise ValueError("Invalid official test pair")
        # Deliberately do not copy, validate, compare or use pair['output'].
        tests.append({"input": validate_grid(pair["input"])})
    return {"train": train, "test": tests}


def project_dataset(dataset):
    return {path.stem: project_task(read_json(path)) for path in evaluation_paths(dataset)}


def validate_challenges(challenges):
    if type(challenges) is not dict or not challenges:
        raise ValueError("Nonempty challenge mapping required")
    for task_id, task in challenges.items():
        if type(task_id) is not str or not task_id or type(task) is not dict or set(task) != {"train", "test"}:
            raise ValueError("Invalid challenge task")
        if type(task["train"]) is not list or not task["train"]:
            raise ValueError("Nonempty training list required")
        for pair in task["train"]:
            if type(pair) is not dict or set(pair) != {"input", "output"}:
                raise ValueError("Training pairs require input and output only")
            validate_grid(pair["input"])
            validate_grid(pair["output"])
        if type(task["test"]) is not list or not task["test"]:
            raise ValueError("Nonempty test list required")
        for pair in task["test"]:
            if type(pair) is not dict or set(pair) != {"input"}:
                raise ValueError("Challenge test pairs must contain input only")
            validate_grid(pair["input"])


def validate_predictions(challenges, predictions):
    validate_challenges(challenges)
    if type(predictions) is not dict or set(predictions) != set(challenges):
        raise ValueError("Prediction task IDs must exactly match challenge task IDs")
    for task_id, task in challenges.items():
        rows = predictions[task_id]
        if type(rows) is not list or len(rows) != len(task["test"]):
            raise ValueError(f"Prediction test count mismatch: {task_id}")
        for row in rows:
            if type(row) is not dict or not row or not set(row) <= {"attempt_1", "attempt_2"}:
                raise ValueError("Each test requires one or two named attempts; extra attempts are rejected")
            for grid in row.values():
                validate_grid(grid)


def score_predictions(challenges, predictions, answers):
    """Strict exact-match scorer; task-average and output-weighted are distinct."""
    validate_predictions(challenges, predictions)
    if type(answers) is not dict or set(answers) != set(challenges):
        raise ValueError("Answer task IDs must exactly match challenge task IDs")
    per_task = {}
    correct_outputs = 0
    output_count = 0
    fractions = []
    for task_id in sorted(challenges):
        expected = answers[task_id]
        if type(expected) is not list or len(expected) != len(challenges[task_id]["test"]):
            raise ValueError(f"Answer test count mismatch: {task_id}")
        correct = []
        for row, answer in zip(predictions[task_id], expected):
            validate_grid(answer)
            correct.append(any(grid == answer for grid in row.values()))
        count = sum(correct)
        total = len(correct)
        fraction = Fraction(count, total)
        per_task[task_id] = {"correct_outputs": count, "test_outputs": total,
                             "correct_by_test": correct, "fraction": str(fraction),
                             "all_tests_correct": count == total}
        fractions.append(fraction)
        correct_outputs += count
        output_count += total
    task_mean = sum(fractions, Fraction()) / len(fractions)
    weighted = Fraction(correct_outputs, output_count)
    return {
        "task_count": len(challenges), "test_output_count": output_count,
        "correct_outputs": correct_outputs,
        "all_tests_correct_tasks": sum(v["all_tests_correct"] for v in per_task.values()),
        "task_mean_fraction_exact": str(task_mean),
        "task_mean_percent": float(task_mean * 100),
        "output_weighted_fraction_exact": str(weighted),
        "output_weighted_percent": float(weighted * 100),
        "max_attempts_per_test": 2,
        "metric_definition": "task_mean_percent = 100 * mean(correct test outputs / test outputs for each task)",
        "match_rule": "Exact dimensions and all integer cells; either of at most two predictions may match",
        "per_task": per_task,
    }


def git(dataset, *args):
    return subprocess.check_output(["git", "-C", str(dataset), *args], text=True).strip()


def dataset_inventory(dataset):
    paths = evaluation_paths(dataset)
    inventory = {str(p.relative_to(dataset)): sha256(p) for p in paths}
    for name in ("data/evaluation.txt", "readme.md", "LICENSE"):
        inventory[name] = sha256(Path(dataset) / name)
    return inventory


def execute(command, cwd):
    started = utc_now()
    tick = time.perf_counter()
    process = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    receipt = {"command": command, "cwd": str(cwd), "started_utc": started,
               "finished_utc": utc_now(), "elapsed_seconds": time.perf_counter() - tick,
               "returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr}
    return receipt


def run_evaluation(dataset, output):
    dataset = Path(dataset).resolve()
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Output directory already exists; refuse to overwrite any trial")
    output.mkdir(parents=True)
    started = utc_now()
    evaluator_hash = sha256(__file__)
    solver_hash = sha256(SOLVER)
    inventory = dataset_inventory(dataset)
    provenance = {"url": DATASET_URL, "origin": git(dataset, "remote", "get-url", "origin"),
                  "commit": git(dataset, "rev-parse", "HEAD"),
                  "git_status_porcelain": git(dataset, "status", "--porcelain"),
                  "split": "full data/evaluation/*.json, matched exactly to data/evaluation.txt",
                  "file_sha256": inventory}
    challenges_path = output / "challenge_only.json"
    predictions_path = output / "predictions.json"
    project_command = [sys.executable, "-B", str(Path(__file__).resolve()), "project", "--dataset", str(dataset),
                       "--challenges", str(challenges_path)]
    projection = execute(project_command, ROOT)
    write_json(output / "projection_process.json", projection)
    if projection["returncode"]:
        raise RuntimeError("Projection failed; see projection_process.json")
    challenges = read_json(challenges_path)
    validate_challenges(challenges)
    predict_command = [sys.executable, "-B", str(SOLVER), "--challenges", str(challenges_path),
                       "--submission", str(predictions_path)]
    generation = execute(predict_command, ROOT)
    write_json(output / "prediction_process.json", generation)
    if generation["returncode"]:
        raise RuntimeError("Prediction failed; see prediction_process.json")
    validate_predictions(challenges, read_json(predictions_path))
    if sha256(SOLVER) != solver_hash or sha256(__file__) != evaluator_hash or dataset_inventory(dataset) != inventory:
        raise RuntimeError("Source or dataset changed during prediction")
    manifest_path = output / "frozen_manifest.json"
    manifest = {
        "schema_version": 1, "run_started_utc": started, "predictions_frozen_utc": utc_now(),
        "dataset": provenance, "method_commit": git(ROOT, "rev-parse", "HEAD"),
        "source_module": str(SOLVER), "source_module_sha256": solver_hash,
        "evaluator_module": str(Path(__file__).resolve()), "evaluator_module_sha256": evaluator_hash,
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "settings": SETTINGS, "fallback_policy": FALLBACK, "boundary": BOUNDARY,
        "challenge_only": {"path": str(challenges_path), "sha256": sha256(challenges_path)},
        "predictions": {"path": str(predictions_path), "sha256": sha256(predictions_path)},
        "task_count": len(challenges), "test_input_count": sum(len(t["test"]) for t in challenges.values()),
        "test_counts_by_task": {k: len(v["test"]) for k, v in challenges.items()},
        "projection_process": projection, "prediction_process": generation,
        "failures": [],
        "claims": "Local self-reported public evaluation of this frozen limited-grammar baseline; no official verification, ranking or unseen-task generalisation claim",
    }
    write_json(manifest_path, manifest)
    # A digest is fixed before launching the scorer; no scorer is called earlier.
    manifest_digest = sha256(manifest_path)
    (output / "frozen_manifest.sha256").write_text(manifest_digest + "  frozen_manifest.json\n", encoding="utf-8")
    score_command = [sys.executable, "-B", str(Path(__file__).resolve()), "score", "--dataset", str(dataset),
                     "--manifest", str(manifest_path), "--manifest-sha256", manifest_digest,
                     "--result", str(output / "score.json")]
    scoring = execute(score_command, ROOT)
    write_json(output / "scoring_process.json", scoring)
    receipt = {"run_finished_utc": utc_now(), "scoring_process": scoring,
               "manifest_sha256": manifest_digest,
               "challenge_only_sha256": sha256(challenges_path),
               "predictions_sha256": sha256(predictions_path),
               "score_sha256": sha256(output / "score.json") if (output / "score.json").exists() else None,
               "source_module_sha256_after": sha256(SOLVER),
               "evaluator_module_sha256_after": sha256(__file__),
               "failures": [] if scoring["returncode"] == 0 else ["scoring process failed"]}
    write_json(output / "result_receipt.json", receipt)
    if scoring["returncode"]:
        raise RuntimeError("Scoring failed; see scoring_process.json")
    print(json.dumps(read_json(output / "score.json") | {"per_task": "See score.json"}, sort_keys=True))


def score_frozen(dataset, manifest_path, expected_manifest_sha256, result_path):
    started = utc_now()
    if sha256(manifest_path) != expected_manifest_sha256:
        raise ValueError("Frozen manifest digest mismatch")
    manifest = read_json(manifest_path)
    challenges_path = Path(manifest["challenge_only"]["path"])
    predictions_path = Path(manifest["predictions"]["path"])
    for path, key in ((challenges_path, "challenge_only"), (predictions_path, "predictions")):
        if sha256(path) != manifest[key]["sha256"]:
            raise ValueError(f"Frozen {key} digest mismatch")
    if sha256(SOLVER) != manifest["source_module_sha256"] or sha256(__file__) != manifest["evaluator_module_sha256"]:
        raise ValueError("Frozen source digest mismatch")
    dataset = Path(dataset).resolve()
    if git(dataset, "rev-parse", "HEAD") != manifest["dataset"]["commit"] or dataset_inventory(dataset) != manifest["dataset"]["file_sha256"]:
        raise ValueError("Frozen dataset provenance mismatch")
    challenges = read_json(challenges_path)
    predictions = read_json(predictions_path)
    # Expected output contents are consumed for grading only in this process,
    # after all frozen prediction/manifest digest checks above.
    answers = {}
    for path in evaluation_paths(dataset):
        raw = read_json(path)
        if project_task(raw) != challenges[path.stem]:
            raise ValueError("Official task and frozen challenge mismatch")
        answers[path.stem] = [pair["output"] for pair in raw["test"]]
    result = score_predictions(challenges, predictions, answers)
    result.update({"scoring_started_utc": started, "scoring_finished_utc": utc_now(),
                   "manifest_sha256": expected_manifest_sha256, "predictions_sha256": sha256(predictions_path),
                   "challenge_only_sha256": sha256(challenges_path), "dataset_commit": manifest["dataset"]["commit"],
                   "source_module_sha256": manifest["source_module_sha256"], "failures": []})
    if sha256(manifest_path) != expected_manifest_sha256 or sha256(predictions_path) != manifest["predictions"]["sha256"]:
        raise ValueError("Frozen artifacts changed during scoring")
    write_json(result_path, result)
    print(f"SCORED {result['task_count']} tasks / {result['test_output_count']} test outputs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--dataset", required=True, type=Path)
    run.add_argument("--output", required=True, type=Path)
    project = commands.add_parser("project")
    project.add_argument("--dataset", required=True, type=Path)
    project.add_argument("--challenges", required=True, type=Path)
    score = commands.add_parser("score")
    score.add_argument("--dataset", required=True, type=Path)
    score.add_argument("--manifest", required=True, type=Path)
    score.add_argument("--manifest-sha256", required=True)
    score.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "project":
        challenges = project_dataset(args.dataset)
        validate_challenges(challenges)
        write_json(args.challenges, challenges, compact=True)
        print(f"PROJECTED {len(challenges)} tasks; test pairs contain input only")
    elif args.command == "score":
        score_frozen(args.dataset, args.manifest, args.manifest_sha256, args.result)
    else:
        run_evaluation(args.dataset, args.output)


if __name__ == "__main__":
    main()

