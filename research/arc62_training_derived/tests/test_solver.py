"""Original synthetic tests; not ARC hidden-score evidence."""
import unittest
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generic_solver import solve_task, solve_challenges, fit_programs, validate_grid, transform, program_trace


def result(train, grid):
    answers = solve_task([{"input": x, "output": y} for x, y in train], [grid])
    return answers[0]

class GenericTrainingDerivedTests(unittest.TestCase):
    def assert_derived(self, train, test, expected):
        entry = result(train, test)
        self.assertIn(expected, [entry['attempt_1'],entry['attempt_2']])

    def test_identity(self):
        self.assert_derived([([[1,0],[0,2]],[[1,0],[0,2]]), ([[0,3]],[[0,3]])], [[2,3]], [[2,3]])

    def test_rotate_90(self):
        self.assert_derived([([[1,2,3]],[[1],[2],[3]]), ([[5,6]],[[5],[6]])], [[7,8]], [[7],[8]])

    def test_flip_horizontal(self):
        self.assert_derived([([[1,2]],[[2,1]]), ([[3,4,5]],[[5,4,3]])], [[6,7,8]], [[8,7,6]])

    def test_crop_nonzero(self):
        self.assert_derived([([[0,0,0],[0,2,2],[0,0,0]],[[2,2]]), ([[0,3,0],[0,3,0]],[[3],[3]])], [[0,0,4,0],[0,0,4,0]], [[4],[4]])

    def test_double_scale(self):
        self.assert_derived([([[2]],[[2,2],[2,2]]), ([[3]],[[3,3],[3,3]])],[[4]],[[4,4],[4,4]])

    def test_tiling_2x2(self):
        self.assert_derived([([[1,2]],[[1,2,1,2],[1,2,1,2]]), ([[3,4]],[[3,4,3,4],[3,4,3,4]])],[[5,6]],[[5,6,5,6],[5,6,5,6]])

    def test_color_map(self):
        self.assert_derived([([[1,0,1]],[[2,0,2]]), ([[0,1,1]],[[0,2,2]])], [[1,1,0]], [[2,2,0]])

    def test_no_task_id_dependency(self):
        tasks = {'anonymous-test-a':{'train':[{'input':[[1,0]],'output':[[0,1]]}], 'test':[{'input':[[2,0]]}]},
                 'random-unseen-id-9087':{'train':[{'input':[[1,0]],'output':[[0,1]]}], 'test':[{'input':[[2,0]]}]}}
        o = solve_challenges(tasks)
        self.assertEqual(o['anonymous-test-a'],o['random-unseen-id-9087'])

    def test_rejects_leaked_test_output(self):
        with self.assertRaises(ValueError):
            solve_challenges({'abc':{'train':[{'input':[[1]],'output':[[1]]}], 'test':[{'input':[[2]],'output':[[2]]}]}})

    def test_rejects_malformed_grid_and_out_of_range(self):
        for grid in ([],[[1,2],[3]],[[10]],[[True]],[[1.3]],[[0]*31]):
            with self.subTest(grid=repr(grid)[:80]), self.assertRaises(ValueError):
                validate_grid(grid)

    def test_conflicting_training_demonstrations_yield_explicit_unverified_fallback(self):
        train = [{'input':[[1]],'output':[[2]]},{'input':[[1]],'output':[[3]]}]
        trace = program_trace(train)
        self.assertEqual(trace['supported_count'],0)
        self.assertEqual(solve_task(train,[[[1]]])[0]['attempt_1'],[[1]])

    def test_multiple_test_inputs_and_outputs(self):
        train=[{'input':[[1,2,3]],'output':[[3,2,1]]}, {'input':[[4,5]],'output':[[5,4]]}]
        out=solve_task(train,[[[6,7]],[[8,9,0]]])
        self.assertEqual(len(out),2)
        self.assertIn([[7,6]],[out[0]['attempt_1'],out[0]['attempt_2']])

    def test_does_not_allow_any_output_template_witness_into_predictor(self):
        bad=[{'input':[[1]], 'output':[[1]], 'test_answer':[[0]]}]
        with self.assertRaises(ValueError):solve_task(bad, [[[3]]])

    def test_eligible_predictions_max_two(self):
        train=[{'input':[[0,0],[0,0]],'output':[[0,0],[0,0]]}]
        outputs=solve_task(train, [[[1,0],[0,0]]])
        self.assertEqual(set(outputs[0]), {'attempt_1','attempt_2'})
        self.assertEqual(len(outputs),1)

    def test_empty_train_invalid(self):
        with self.assertRaises(ValueError): solve_task([], [[[1]]])

if __name__=='__main__': unittest.main()
