"""Procedurally constructed fixtures only; no ARC dataset access.

The feedback-vs-restart test is deliberately mechanism-aligned (the target is a
two-step program that residuals can reveal): a unit test, NOT evidence of ARC
performance.
"""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import erna2, run_experiment
from erna2 import apply_step, components, attributes, derive_children, solve, run


def G(*rows):
    return tuple(tuple(r) for r in rows)


class Operators(unittest.TestCase):
    def test_colormap(self):
        self.assertEqual(apply_step({'op': 'colormap', 'map': [[1, 2]]}, G((1, 0), (0, 1))), G((2, 0), (0, 2)))

    def test_translate_collision_and_bounds(self):
        g = G((1, 0, 0), (0, 0, 0), (0, 0, 2))
        self.assertEqual(apply_step({'op': 'translate_color', 'color': 1, 'dr': 1, 'dc': 1}, g), G((0, 0, 0), (0, 1, 0), (0, 0, 2)))
        for dr, dc in ((2, 2), (-1, 0)):
            with self.assertRaises(ValueError):
                apply_step({'op': 'translate_color', 'color': 1, 'dr': dr, 'dc': dc}, g)

    def test_gravity(self):
        g = G((1, 0), (0, 0), (2, 0))
        self.assertEqual(apply_step({'op': 'gravity', 'dir': 'down'}, g), G((0, 0), (1, 0), (2, 0)))
        self.assertEqual(apply_step({'op': 'gravity', 'dir': 'up'}, g), G((1, 0), (2, 0), (0, 0)))
        h = G((1, 0, 2), (0, 3, 0))
        self.assertEqual(apply_step({'op': 'gravity', 'dir': 'right'}, h), G((0, 1, 2), (0, 0, 3)))
        self.assertEqual(apply_step({'op': 'gravity', 'dir': 'left'}, h), G((1, 2, 0), (3, 0, 0)))

    def test_crop(self):
        g = G((0, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 0), (0, 2, 0, 0))
        self.assertEqual(apply_step({'op': 'crop', 'selector': 'bbox_nonbg'}, g), G((1, 1), (0, 0), (2, 0)))
        self.assertEqual(apply_step({'op': 'crop', 'selector': 'largest_obj'}, g), G((1, 1)))
        self.assertEqual(apply_step({'op': 'crop', 'selector': 'smallest_obj'}, g), G((2,)))
        self.assertEqual(apply_step({'op': 'crop', 'selector': 'color', 'color': 2}, g), G((2,)))
        with self.assertRaises(ValueError):
            apply_step({'op': 'crop', 'selector': 'largest_obj'}, G((1, 0, 2)))

    def test_fill_enclosed(self):
        closed = G((1, 1, 1), (1, 0, 1), (1, 1, 1))
        self.assertEqual(apply_step({'op': 'fill_enclosed', 'color': 5}, closed)[1][1], 5)
        opened = G((1, 1, 1), (1, 0, 0), (1, 1, 1))
        self.assertEqual(apply_step({'op': 'fill_enclosed', 'color': 5}, opened), opened)

    def test_recolor_and_attributes(self):
        g = G((1, 1, 0, 0), (0, 0, 0, 2), (0, 0, 0, 0))
        comps = components(g)
        ats = attributes(g, comps)
        self.assertEqual([a['size'] for a in ats], [2, 1])
        self.assertEqual([a['extreme'] for a in ats], ['max', 'min'])
        self.assertEqual(apply_step({'op': 'recolor_objects', 'attr': 'size', 'map': [[2, 7]]}, g),
                         G((7, 7, 0, 0), (0, 0, 0, 2), (0, 0, 0, 0)))

    def test_shape_operators(self):
        g = G((1, 2), (3, 4))
        self.assertEqual(apply_step({'op': 'upscale', 'k': 2}, g), G((1, 1, 2, 2), (1, 1, 2, 2), (3, 3, 4, 4), (3, 3, 4, 4)))
        self.assertEqual(apply_step({'op': 'tile', 'rows': 1, 'cols': 2}, g), G((1, 2, 1, 2), (3, 4, 3, 4)))
        self.assertEqual(apply_step({'op': 'mirror_concat', 'axis': 'h', 'order': 'after'}, g), G((1, 2, 2, 1), (3, 4, 4, 3)))
        self.assertEqual(apply_step({'op': 'mirror_concat', 'axis': 'h', 'order': 'before'}, g), G((2, 1, 1, 2), (4, 3, 3, 4)))
        self.assertEqual(apply_step({'op': 'mirror_concat', 'axis': 'v', 'order': 'after'}, g), G((1, 2), (3, 4), (3, 4), (1, 2)))
        self.assertEqual(apply_step({'op': 'mirror_concat', 'axis': 'v', 'order': 'before'}, g), G((3, 4), (1, 2), (1, 2), (3, 4)))
        with self.assertRaises(ValueError):
            apply_step({'op': 'upscale', 'k': 5}, tuple(tuple([1] * 7) for _ in range(7)))


class Derivations(unittest.TestCase):
    def test_colormap_residual_and_changed_residual(self):
        parent = [{'op': 'identity'}]
        pred = G((3, 0), (0, 3))
        for target in (5, 6):
            kids = derive_children(parent, pred, G((target, 0), (0, target)), 0)
            self.assertEqual(kids[0][0][1], {'op': 'colormap', 'map': [[3, target]]})
            self.assertEqual(kids[0][1]['type'], 'residual')

    def test_fill_shape_translate_recolor(self):
        parent = [{'op': 'identity'}]
        closed = G((1, 1, 1), (1, 0, 1), (1, 1, 1))
        exp = G((1, 1, 1), (1, 4, 1), (1, 1, 1))
        steps = [k[0][1] for k in derive_children(parent, closed, exp, 0)]
        self.assertIn({'op': 'fill_enclosed', 'color': 4}, steps)
        small = G((1, 2), (3, 4))
        steps = [k[0][1] for k in derive_children(parent, small, apply_step({'op': 'upscale', 'k': 2}, small), 0)]
        self.assertIn({'op': 'upscale', 'k': 2}, steps)
        self.assertFalse(any(s['op'] == 'tile' for s in steps))
        steps = [k[0][1] for k in derive_children(parent, G((1, 0, 0), (0, 0, 0)), G((0, 0, 0), (0, 0, 1)), 0)]
        self.assertIn({'op': 'translate_color', 'color': 1, 'dr': 1, 'dc': 2}, steps)
        pred = G((1, 1, 0, 2), (0, 0, 0, 0))
        steps = [k[0][1] for k in derive_children(parent, pred, G((7, 7, 0, 2), (0, 0, 0, 0)), 0)]
        self.assertTrue(any(s['op'] == 'recolor_objects' for s in steps))

    def test_unfixable_witness_yields_no_children(self):
        self.assertEqual(derive_children([{'op': 'identity'}], G((1, 2), (3, 4)), G((4, 3), (2, 1)), 0)[:0], [])


def base_grid(seed):
    rows = [[0] * 6 for _ in range(6)]
    pts = [(0, 0), (1, 3), (2, 1), (4, 5), (5, 2)]
    for i, (r, c) in enumerate(pts):
        rows[(r + seed) % 6][(c + 2 * seed) % 6] = 3 if i % 2 == 0 else 1
    return rows


class Arms(unittest.TestCase):
    def task(self, target):
        prog = [{'op': 'flip_h'}, {'op': 'colormap', 'map': [[3, target]]}]
        train = [{'input': base_grid(s), 'output': [list(r) for r in run(prog, erna2.validate_grid(base_grid(s)))]} for s in (0, 1, 2)]
        test = base_grid(4)
        return train, test, [list(r) for r in run(prog, erna2.validate_grid(test))]

    def test_feedback_finds_two_step_program_and_changed_residual_changes_rule(self):
        for target in (5, 6):
            train, test, gold = self.task(target)
            on, off = solve(train, [test], True), solve(train, [test], False)
            self.assertIn(gold, on['attempts'][0].values())
            self.assertNotIn(gold, off['attempts'][0].values())
            self.assertGreaterEqual(on['stats']['selected_residual_derived'], 1)
            self.assertEqual(off['stats']['derived_children'], 0)
            win = on['trace'][on['selected_rule_ids'][0]]
            self.assertEqual(win['program'][1], {'op': 'colormap', 'map': [[3, target]]})
            self.assertEqual(win['origin']['type'], 'residual')
            self.assertIn('parent_id', win['origin'])

    def test_arms_share_seeds_and_budgets(self):
        train, test, _ = self.task(5)
        on, off = solve(train, [test], True), solve(train, [test], False)
        seeds = lambda r: [t['program'] for t in r['trace'] if t['origin']['type'] == 'seed']
        self.assertEqual(seeds(on), seeds(off))
        for r in (on, off):
            self.assertLessEqual(r['stats']['candidates'], 128)
            self.assertLessEqual(r['stats']['checks'], 1024)
        small = solve(train, [test], True, max_candidates=10, max_checks=40)
        self.assertLessEqual(small['stats']['candidates'], 10)
        self.assertLessEqual(small['stats']['checks'], 40)

    def test_determinism_and_invalid_settings(self):
        train, test, _ = self.task(5)
        self.assertEqual(json.dumps(solve(train, [test], True), sort_keys=True), json.dumps(solve(train, [test], True), sort_keys=True))
        for kw in ({'max_candidates': 0}, {'max_checks': 0}, {'max_candidates': 'x'}):
            with self.assertRaises(ValueError):
                solve(train, [test], True, **kw)
        with self.assertRaises(ValueError):
            solve(train, [test], 'yes')

    def test_all_demonstrations_required_and_fallback(self):
        train = [{'input': base_grid(0), 'output': base_grid(0)}, {'input': base_grid(1), 'output': base_grid(2)}]
        out = solve(train, [base_grid(3)], True)
        self.assertEqual(out['stats']['accepted_programs'] == 0, out['fallback_identity'])


class Harness(unittest.TestCase):
    def tiny_run(self, out):
        train, test = Arms().task(5)[:2]
        gold = Arms().task(5)[2]
        out.mkdir()
        run_experiment.dump(out / 'challenge_only.json', {'t': {'train': train, 'test': [{'input': test}]}})
        run_experiment.dump(out / 'answers_scoring_only.json', {'t': [gold]})
        run_experiment.dump(out / 'input_manifest.json', {'answers_sha256': run_experiment.sha(out / 'answers_scoring_only.json')})
        for arm in run_experiment.ARMS:
            run_experiment.infer(out, arm)
        run_experiment.freeze(out)

    def test_inference_rejects_test_labels(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'run'
            out.mkdir()
            train, test = Arms().task(5)[:2]
            run_experiment.dump(out / 'challenge_only.json', {'t': {'train': train, 'test': [{'input': test, 'output': test}]}})
            with self.assertRaises(ValueError):
                run_experiment.infer(out, 'feedback')

    def test_scorer_accepts_untouched_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'run'
            self.tiny_run(out)
            run_experiment.score(out)
            self.assertEqual(json.loads((out / 'score.json').read_text())['arms']['feedback']['correct_test_outputs'], 1)
            (out / 'feedback_predictions.json').write_text('{}\n')
            with self.assertRaises(ValueError):
                run_experiment.score(out)

    def test_scorer_rejects_changed_answers(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'run'
            self.tiny_run(out)
            (out / 'answers_scoring_only.json').write_text('{"t":[[[0]]]}\n')
            with self.assertRaises(ValueError):
                run_experiment.score(out)

    def test_preparation_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                run_experiment.prepare(Path(d))


if __name__ == '__main__':
    unittest.main()
