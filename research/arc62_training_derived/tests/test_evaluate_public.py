"""Synthetic scorer/projection controls, independent of public-task accuracy."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluate_public import project_task, score_predictions, validate_challenges


def task(n):
    return {"train": [{"input": [[1]], "output": [[2]]}],
            "test": [{"input": [[3]]} for _ in range(n)]}


class PublicEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.challenges = {"one": task(1), "three": task(3)}
        self.answers = {"one": [[[8]]], "three": [[[8]], [[8]], [[8]]]}
        self.predictions = {
            "one": [{"attempt_1": [[0]], "attempt_2": [[8]]}],
            "three": [{"attempt_1": [[8]]}, {"attempt_1": [[0]]}, {"attempt_1": [[0]]}],
        }

    def test_unequal_test_counts_distinguish_task_mean_and_output_weighted(self):
        score = score_predictions(self.challenges, self.predictions, self.answers)
        self.assertEqual(score["task_mean_fraction_exact"], "2/3")
        self.assertAlmostEqual(score["task_mean_percent"], 200 / 3)
        self.assertEqual(score["output_weighted_fraction_exact"], "1/2")
        self.assertEqual(score["correct_outputs"], 2)
        self.assertEqual(score["test_output_count"], 4)
        self.assertEqual(score["all_tests_correct_tasks"], 1)

    def test_second_attempt_counts_but_third_attempt_is_rejected(self):
        self.assertEqual(score_predictions(self.challenges, self.predictions, self.answers)["per_task"]["one"]["correct_outputs"], 1)
        self.predictions["three"][1]["attempt_3"] = [[8]]
        with self.assertRaisesRegex(ValueError, "extra attempts"):
            score_predictions(self.challenges, self.predictions, self.answers)

    def test_missing_or_extra_prediction_task_is_rejected(self):
        for mode in ("missing", "extra"):
            predictions = copy.deepcopy(self.predictions)
            if mode == "missing":
                del predictions["three"]
            else:
                predictions["other"] = predictions["one"]
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "task IDs"):
                score_predictions(self.challenges, predictions, self.answers)

    def test_mismatched_prediction_test_counts_rejected(self):
        for rows in ([], self.predictions["three"][:2], self.predictions["three"] + self.predictions["three"][:1]):
            predictions = dict(self.predictions, three=rows)
            with self.subTest(n=len(rows)), self.assertRaisesRegex(ValueError, "count mismatch"):
                score_predictions(self.challenges, predictions, self.answers)

    def test_missing_answer_tasks_or_test_records_rejected(self):
        for answers in ({"one": [[[8]]]}, dict(self.answers, three=[[[8]]])):
            with self.subTest(answers=answers), self.assertRaises(ValueError):
                score_predictions(self.challenges, self.predictions, answers)

    def test_projection_contains_training_outputs_but_no_test_answers(self):
        raw = {"train": [{"input": [[1]], "output": [[2]]}],
               "test": [{"input": [[3]], "output": [[9, 9]]}]}
        before = copy.deepcopy(raw)
        projected = project_task(raw)
        self.assertEqual(projected, task(1))
        self.assertEqual(set(projected["test"][0]), {"input"})
        self.assertEqual(raw, before)
        raw["test"][0]["output"] = "sentinel ignored by projection"
        self.assertEqual(project_task(raw), projected)
        leaked = copy.deepcopy(projected)
        leaked["test"][0]["output"] = [[9]]
        with self.assertRaisesRegex(ValueError, "input only"):
            validate_challenges({"leak": leaked})

    def test_exact_match_requires_dimensions_and_strict_integer_colors(self):
        predictions = copy.deepcopy(self.predictions)
        predictions["one"] = [{"attempt_1": [[8, 8]]}]
        score = score_predictions(self.challenges, predictions, self.answers)
        self.assertEqual(score["per_task"]["one"]["correct_outputs"], 0)
        predictions["one"] = [{"attempt_1": [[True]]}]
        with self.assertRaises(ValueError):
            score_predictions(self.challenges, predictions, self.answers)


if __name__ == "__main__":
    unittest.main()
