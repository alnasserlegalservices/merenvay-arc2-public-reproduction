"""Regression tests for task-level program consistency; synthetic only."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generic_solver


class MockProgram:
    def __init__(self, label, invalid=None):
        self.label = label
        self.invalid = invalid

    def apply(self, grid):
        if grid == self.invalid:
            raise ValueError("invalid for this grid")
        return ((self.label,),)


class TaskLevelConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.train = [{"input": [[1]], "output": [[1]]}]
        self.tests = [[[2]], [[3]]]

    def test_candidate_invalid_on_second_grid_never_selected_on_first(self):
        programs = [MockProgram(5, ((3,),)), MockProgram(6), MockProgram(7)]
        with patch.object(generic_solver, "fit_programs", return_value=(programs, {})):
            result = generic_solver.solve_task(self.train, self.tests)
        self.assertEqual(result, [
            {"attempt_1": [[6]], "attempt_2": [[7]]},
            {"attempt_1": [[6]], "attempt_2": [[7]]},
        ])

    def test_no_candidate_valid_across_entire_task_falls_back_consistently(self):
        programs = [MockProgram(5, ((2,),)), MockProgram(6, ((3,),))]
        with patch.object(generic_solver, "fit_programs", return_value=(programs, {})):
            result = generic_solver.solve_task(self.train, self.tests)
        self.assertEqual(result, [
            {"attempt_1": [[2]], "attempt_2": [[2]]},
            {"attempt_1": [[3]], "attempt_2": [[3]]},
        ])

    def test_duplicate_candidate_sequences_do_not_consume_two_attempts(self):
        programs = [MockProgram(5), MockProgram(5), MockProgram(6)]
        with patch.object(generic_solver, "fit_programs", return_value=(programs, {})):
            result = generic_solver.solve_task(self.train, self.tests)
        self.assertEqual(result[0], {"attempt_1": [[5]], "attempt_2": [[6]]})


if __name__ == "__main__":
    unittest.main()
