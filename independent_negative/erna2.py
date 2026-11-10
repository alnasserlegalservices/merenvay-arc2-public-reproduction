"""MERENVAY E-RNA v2: object-level residual-feedback probe. Standard library only.

A hypothesis is a JSON program of at most two steps over a small, hand-designed
operator set (see OPERATORS). Both generator arms share identical first-
demonstration seeds, an identical seeded random sampler over the SAME parameter
family, and identical budgets. They differ in one thing only: the feedback arm,
after a candidate fails on a training pair, derives child programs from that
pair's cell residuals and tries them before the sampler. Children are kept only
if they exactly fix the witness pair; they are then evaluated on all pairs.

Limits (by design): operators, attributes, ordering and derivation rules are
human/model-designed, not discovered. No rotation of single objects, no object
matching across grids, no counting-based output sizes, no pattern completion, no
conditional logic. Two-step programs only. Not general program synthesis.
No task IDs, labels, network, files, LLMs or randomness beyond the recorded
seed enter inference. Equal caps do not imply equal CPU time.
"""
import json
import random
from collections import Counter, deque
from vendor.generic_solver import validate_grid, as_list, _validated_demos, _operation, MAX_SIDE

D4 = ('rot90', 'rot180', 'rot270', 'flip_h', 'flip_v', 'transpose', 'anti_diag')
ATTRS = ('size', 'extreme', 'touches_border', 'height', 'width')
OPERATORS = ('identity',) + D4 + ('colormap', 'translate_color', 'gravity', 'crop',
             'fill_enclosed', 'recolor_objects', 'upscale', 'tile', 'mirror_concat')
MIRRORS = (('h', 'after'), ('h', 'before'), ('v', 'after'), ('v', 'before'))
MAX_STEPS = 2
MAX_CHILDREN = 6


def components(g, same_color=True, conn=4):
    h, w = len(g), len(g[0])
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if conn == 8:
        nb += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen, comps = set(), []
    for r in range(h):
        for c in range(w):
            if (r, c) in seen or g[r][c] == 0:
                continue
            col = g[r][c]
            stack, cells = [(r, c)], []
            seen.add((r, c))
            while stack:
                y, x = stack.pop()
                cells.append((y, x))
                for dy, dx in nb:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and (ny, nx) not in seen:
                        v = g[ny][nx]
                        if (v == col) if same_color else (v != 0):
                            seen.add((ny, nx))
                            stack.append((ny, nx))
            comps.append({'color': col, 'cells': sorted(cells)})
    return comps


def attributes(g, comps):
    h, w = len(g), len(g[0])
    sizes = [len(c['cells']) for c in comps]
    lo, hi = min(sizes), max(sizes)
    out = []
    for c, s in zip(comps, sizes):
        rows = [p[0] for p in c['cells']]
        cols = [p[1] for p in c['cells']]
        ext = 'both' if lo == hi else 'max' if s == hi else 'min' if s == lo else 'mid'
        out.append({'size': s, 'extreme': ext, 'height': max(rows) - min(rows) + 1,
                    'width': max(cols) - min(cols) + 1,
                    'touches_border': int(min(rows) == 0 or min(cols) == 0 or max(rows) == h - 1 or max(cols) == w - 1)})
    return out


def _bbox(cells):
    rows = [p[0] for p in cells]
    cols = [p[1] for p in cells]
    return min(rows), max(rows), min(cols), max(cols)


def _crop(g, cells):
    r0, r1, c0, c1 = _bbox(cells)
    return tuple(tuple(row[c0:c1 + 1]) for row in g[r0:r1 + 1])


def apply_step(step, g):
    op = step['op']
    h, w = len(g), len(g[0])
    if op == 'identity':
        return g
    if op in D4:
        return _operation(g, op)
    if op == 'colormap':
        m = {a: b for a, b in step['map']}
        return tuple(tuple(m.get(v, v) for v in row) for row in g)
    if op == 'translate_color':
        color, dr, dc = step['color'], step['dr'], step['dc']
        pts = [(r, c) for r in range(h) for c in range(w) if g[r][c] == color]
        if not pts:
            raise ValueError('Color absent')
        out = [list(row) for row in g]
        for r, c in pts:
            out[r][c] = 0
        for r, c in pts:
            rr, cc = r + dr, c + dc
            if not (0 <= rr < h and 0 <= cc < w) or out[rr][cc] != 0:
                raise ValueError('Translation leaves grid or collides')
            out[rr][cc] = color
        return validate_grid(out)
    if op == 'gravity':
        d = step['dir']
        if d in ('down', 'up'):
            cols = []
            for c in range(w):
                vals = [g[r][c] for r in range(h) if g[r][c] != 0]
                pad = [0] * (h - len(vals))
                cols.append(pad + vals if d == 'down' else vals + pad)
            return tuple(tuple(cols[c][r] for c in range(w)) for r in range(h))
        rows = []
        for r in range(h):
            vals = [v for v in g[r] if v != 0]
            pad = [0] * (w - len(vals))
            rows.append(tuple(pad + vals if d == 'right' else vals + pad))
        return tuple(rows)
    if op == 'crop':
        sel = step['selector']
        if sel == 'bbox_nonbg':
            cells = [(r, c) for r in range(h) for c in range(w) if g[r][c] != 0]
        elif sel in ('largest_obj', 'smallest_obj'):
            comps = components(g, same_color=False, conn=8)
            if not comps:
                raise ValueError('No objects')
            sizes = [len(c['cells']) for c in comps]
            target = max(sizes) if sel == 'largest_obj' else min(sizes)
            if sizes.count(target) != 1:
                raise ValueError('Ambiguous object selection')
            cells = comps[sizes.index(target)]['cells']
        else:
            cells = [(r, c) for r in range(h) for c in range(w) if g[r][c] == step['color']]
        if not cells:
            raise ValueError('Crop target absent')
        return _crop(g, cells)
    if op == 'fill_enclosed':
        reach, stack = set(), []
        for r in range(h):
            for c in range(w):
                if (r in (0, h - 1) or c in (0, w - 1)) and g[r][c] == 0:
                    reach.add((r, c))
                    stack.append((r, c))
        while stack:
            y, x = stack.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and g[ny][nx] == 0 and (ny, nx) not in reach:
                    reach.add((ny, nx))
                    stack.append((ny, nx))
        return tuple(tuple(step['color'] if g[r][c] == 0 and (r, c) not in reach else g[r][c]
                           for c in range(w)) for r in range(h))
    if op == 'recolor_objects':
        comps = components(g)
        if not comps:
            raise ValueError('No objects')
        m = {tuple(a) if isinstance(a, list) else a: b for a, b in step['map']}
        out = [list(row) for row in g]
        for comp, at in zip(comps, attributes(g, comps)):
            new = m.get(at[step['attr']])
            if new is not None:
                for r, c in comp['cells']:
                    out[r][c] = new
        return validate_grid(out)
    if op == 'upscale':
        k = step['k']
        if h * k > MAX_SIDE or w * k > MAX_SIDE:
            raise ValueError('Too large')
        return tuple(tuple(g[r // k][c // k] for c in range(w * k)) for r in range(h * k))
    if op == 'tile':
        a, b = step['rows'], step['cols']
        if h * a > MAX_SIDE or w * b > MAX_SIDE:
            raise ValueError('Too large')
        return tuple(tuple(g[r % h][c % w] for c in range(w * b)) for r in range(h * a))
    if op == 'mirror_concat':
        axis, order = step['axis'], step['order']
        if axis == 'h':
            flipped = _operation(g, 'flip_h')
            a, b = (g, flipped) if order == 'after' else (flipped, g)
            out = tuple(ra + rb for ra, rb in zip(a, b))
        else:
            flipped = _operation(g, 'flip_v')
            a, b = (g, flipped) if order == 'after' else (flipped, g)
            out = a + b
        if len(out) > MAX_SIDE or len(out[0]) > MAX_SIDE:
            raise ValueError('Too large')
        return out
    raise ValueError('Unknown operator ' + str(op))


def run(program, g):
    for step in program:
        g = apply_step(step, g)
    return validate_grid(g)


def key(program):
    return json.dumps(program, sort_keys=True)


def _diff(pred, expected, cap=50):
    ph, pw = (0, 0) if pred is None else (len(pred), len(pred[0]))
    eh, ew = len(expected), len(expected[0])
    cells = []
    count = 0
    for r in range(max(ph, eh)):
        for c in range(max(pw, ew)):
            a = pred[r][c] if r < ph and c < pw else None
            b = expected[r][c] if r < eh and c < ew else None
            if a != b:
                count += 1
                if len(cells) < cap:
                    cells.append([r, c, a, b])
    return count, cells


def seed_programs(demos):
    a0, b0 = demos[0]
    seeds = [([{'op': 'identity'}], 'identity')]
    seeds += [([{'op': d}], 'D4') for d in D4]
    seeds += [([{'op': 'gravity', 'dir': d}], 'gravity') for d in ('down', 'up', 'left', 'right')]
    seeds += [([{'op': 'crop', 'selector': s}], 'crop') for s in ('bbox_nonbg', 'largest_obj', 'smallest_obj')]
    for col in sorted({v for row in a0 for v in row} - {0}):
        seeds.append(([{'op': 'crop', 'selector': 'color', 'color': col}], 'crop'))
    h, w = len(a0), len(a0[0])
    bh, bw = len(b0), len(b0[0])
    if (h, w) == (bh, bw):
        pairs = {}
        ok = True
        for r in range(h):
            for c in range(w):
                if pairs.setdefault(a0[r][c], b0[r][c]) != b0[r][c]:
                    ok = False
        if ok:
            m = sorted([a, b] for a, b in pairs.items() if a != b)
            if m:
                seeds.append(([{'op': 'colormap', 'map': m}], 'colormap'))
        for col in sorted({v for row in a0 for v in row} - {0}):
            src = [(r, c) for r in range(h) for c in range(w) if a0[r][c] == col]
            dst = [(r, c) for r in range(h) for c in range(w) if b0[r][c] == col]
            if src and len(src) == len(dst):
                dr, dc = dst[0][0] - src[0][0], dst[0][1] - src[0][1]
                if (dr, dc) != (0, 0) and sorted((r + dr, c + dc) for r, c in src) == dst:
                    seeds.append(([{'op': 'translate_color', 'color': col, 'dr': dr, 'dc': dc}], 'translate'))
        newc = {b0[r][c] for r in range(h) for c in range(w) if a0[r][c] == 0 and b0[r][c] != 0}
        for col in sorted(newc):
            seeds.append(([{'op': 'fill_enclosed', 'color': col}], 'fill'))
        comps = components(a0)
        if comps:
            ats = attributes(a0, comps)
            for attr in ATTRS:
                m, ok = {}, True
                for comp, at in zip(comps, ats):
                    tgt = {b0[r][c] for r, c in comp['cells']}
                    if len(tgt) != 1:
                        ok = False
                        break
                    t = tgt.pop()
                    if m.setdefault(at[attr], t) != t:
                        ok = False
                        break
                if ok and any(t != comp['color'] for comp, t in zip(comps, [m[at[attr]] for at in ats])):
                    seeds.append(([{'op': 'recolor_objects', 'attr': attr,
                                    'map': [[k, v] for k, v in sorted(m.items(), key=lambda kv: str(kv[0]))]}], 'recolor'))
    if bh % h == 0 and bw % w == 0 and (bh, bw) != (h, w):
        kr, kc = bh // h, bw // w
        if kr == kc and 2 <= kr <= 5:
            seeds.append(([{'op': 'upscale', 'k': kr}], 'upscale'))
        if kr <= 4 and kc <= 4:
            seeds.append(([{'op': 'tile', 'rows': kr, 'cols': kc}], 'tile'))
    for axis, order in MIRRORS:
        seeds.append(([{'op': 'mirror_concat', 'axis': axis, 'order': order}], 'mirror'))
    return seeds


def sample_program(rng, colors):
    n = 1 if rng.random() < 0.5 else 2
    prog = []
    for _ in range(n):
        op = rng.choice(OPERATORS[1:])
        if op in D4:
            prog.append({'op': op})
        elif op == 'colormap':
            pairs = {}
            for _ in range(rng.choice((1, 2))):
                pairs[rng.choice(colors)] = rng.choice(colors)
            prog.append({'op': op, 'map': sorted([a, b] for a, b in pairs.items() if a != b) or [[colors[0], colors[-1]]]})
        elif op == 'translate_color':
            dr, dc = rng.randint(-3, 3), rng.randint(-3, 3)
            prog.append({'op': op, 'color': rng.choice(colors), 'dr': dr, 'dc': dc if (dr, dc) != (0, 0) else 1})
        elif op == 'gravity':
            prog.append({'op': op, 'dir': rng.choice(('down', 'up', 'left', 'right'))})
        elif op == 'crop':
            sel = rng.choice(('bbox_nonbg', 'largest_obj', 'smallest_obj', 'color'))
            prog.append({'op': op, 'selector': sel, **({'color': rng.choice(colors)} if sel == 'color' else {})})
        elif op == 'fill_enclosed':
            prog.append({'op': op, 'color': rng.choice(colors)})
        elif op == 'recolor_objects':
            attr = rng.choice(ATTRS)
            vals = {'size': list(range(1, 9)), 'extreme': ['max', 'min'], 'touches_border': [0, 1],
                    'height': list(range(1, 7)), 'width': list(range(1, 7))}[attr]
            m = {rng.choice(vals): rng.choice(colors) for _ in range(rng.choice((1, 2)))}
            prog.append({'op': op, 'attr': attr, 'map': [[k, v] for k, v in sorted(m.items(), key=lambda kv: str(kv[0]))]})
        elif op == 'upscale':
            prog.append({'op': op, 'k': rng.choice((2, 3))})
        elif op == 'tile':
            a, b = rng.randint(1, 3), rng.randint(1, 3)
            prog.append({'op': op, 'rows': a, 'cols': b if (a, b) != (1, 1) else 2})
        else:
            axis, order = rng.choice(MIRRORS)
            prog.append({'op': op, 'axis': axis, 'order': order})
    return prog


def derive_children(parent, pred, expected, pair):
    """Residual -> child programs, each verified to fix the witness pair exactly."""
    count, cells = _diff(pred, expected, cap=10 ** 6)
    ph, pw, eh, ew = len(pred), len(pred[0]), len(expected), len(expected[0])
    cands = []

    def add(step, why):
        cands.append((step, why))
    if (ph, pw) != (eh, ew):
        if eh % ph == 0 and ew % pw == 0:
            kr, kc = eh // ph, ew // pw
            if kr == kc and 2 <= kr <= 5:
                add({'op': 'upscale', 'k': kr}, 'output is %dx the predicted size on both axes' % kr)
            if kr <= 4 and kc <= 4:
                add({'op': 'tile', 'rows': kr, 'cols': kc}, 'output is (%d,%d) multiple of predicted size' % (kr, kc))
        if (eh, ew) in ((2 * ph, pw), (ph, 2 * pw)):
            for axis, order in MIRRORS:
                add({'op': 'mirror_concat', 'axis': axis, 'order': order}, 'output doubles one predicted dimension')
        if eh <= ph and ew <= pw:
            for sel in ('bbox_nonbg', 'largest_obj', 'smallest_obj'):
                add({'op': 'crop', 'selector': sel}, 'output is smaller than prediction')
            for col in sorted({v for row in pred for v in row} - {0}):
                add({'op': 'crop', 'selector': 'color', 'color': col}, 'output is smaller than prediction')
    else:
        changes = Counter((a, b) for _, _, a, b in cells)
        by_src = {}
        for (a, b), n in changes.items():
            by_src.setdefault(a, set()).add(b)
        if all(len(v) == 1 for v in by_src.values()):
            add({'op': 'colormap', 'map': sorted([a, next(iter(v))] for a, v in by_src.items())},
                'functional predicted->expected color change over %d cells' % count)
        if all(a == 0 for _, _, a, _ in cells) and len({b for _, _, _, b in cells}) == 1:
            add({'op': 'fill_enclosed', 'color': cells[0][3]}, 'residual cells are background that should be color %d' % cells[0][3])
        comps = components(pred)
        if comps:
            ats = attributes(pred, comps)
            for attr in ATTRS:
                m, ok = {}, True
                for comp, at in zip(comps, ats):
                    tgt = {expected[r][c] for r, c in comp['cells']}
                    if len(tgt) != 1:
                        ok = False
                        break
                    t = tgt.pop()
                    if m.setdefault(at[attr], t) != t:
                        ok = False
                        break
                if ok:
                    add({'op': 'recolor_objects', 'attr': attr,
                         'map': [[k, v] for k, v in sorted(m.items(), key=lambda kv: str(kv[0]))]},
                        'per-object consistent target color by attribute ' + attr)
        for col in sorted({v for row in pred for v in row} - {0}):
            src = [(r, c) for r in range(ph) for c in range(pw) if pred[r][c] == col]
            dst = [(r, c) for r in range(eh) for c in range(ew) if expected[r][c] == col]
            if src and len(src) == len(dst):
                dr, dc = dst[0][0] - src[0][0], dst[0][1] - src[0][1]
                if (dr, dc) != (0, 0) and sorted((r + dr, c + dc) for r, c in src) == dst:
                    add({'op': 'translate_color', 'color': col, 'dr': dr, 'dc': dc},
                        'color %d displaced by (%d,%d) in the residual' % (col, dr, dc))
    children = []
    for step, why in cands:
        try:
            if apply_step(step, pred) == expected:
                children.append((parent + [step], {'type': 'residual', 'pair': pair, 'derivation': why,
                                                   'n_residual_cells': count}))
        except ValueError:
            continue
        if len(children) >= MAX_CHILDREN:
            break
    return children


def solve(train, test_inputs, feedback, max_candidates=128, max_checks=1024, seed=0,
          extra_repairs=None):
    demos = _validated_demos(train)
    if type(feedback) is not bool:
        raise ValueError('feedback must be a boolean')
    if type(max_candidates) is not int or not 1 <= max_candidates <= 512:
        raise ValueError('max_candidates must be in 1..512')
    if type(max_checks) is not int or not 1 <= max_checks <= 8192:
        raise ValueError('max_checks must be in 1..8192')
    if type(test_inputs) is not list or not test_inputs:
        raise ValueError('Nonempty label-free grid list required')
    tests = [validate_grid(g) for g in test_inputs]
    colors = sorted({v for a, b in demos for g in (a, b) for row in g for v in row})
    rng = random.Random(seed)
    queue = deque((p, {'type': 'seed', 'family': f}) for p, f in seed_programs(demos))
    seen, trace, accepted = set(), [], []
    checks = steps_applied = draws = derived = feedback_analyses = 0
    joint_calls = joint_cells = 0
    misses = 0
    while len(trace) < max_candidates and checks + len(demos) <= max_checks:
        if queue:
            prog, origin = queue.popleft()
        else:
            if misses > 200:
                break
            prog, origin = sample_program(rng, colors), {'type': 'sampler'}
            draws += 1
        k = key(prog)
        if k in seen:
            if origin['type'] == 'sampler':
                misses += 1
            continue
        misses = 0
        seen.add(k)
        rec = {'id': len(trace), 'program': prog, 'origin': origin, 'outcomes': [], 'accepted': False}
        trace.append(rec)
        preds = []
        for j, (a, b) in enumerate(demos):
            checks += 1
            steps_applied += len(prog)
            err = None
            try:
                pred = run(prog, a)
            except ValueError as exc:
                pred, err = None, str(exc)
            n, cells = _diff(pred, b)
            rec['outcomes'].append({'pair': j, 'match': pred == b, 'n_diff_cells': n, 'diff_cells': cells, 'error': err})
            preds.append(pred)
        rec['accepted'] = all(o['match'] for o in rec['outcomes'])
        if rec['accepted']:
            accepted.append((rec['id'], prog))
        elif len(prog) < MAX_STEPS:
            kids = []
            if extra_repairs is not None:
                new_kids, scanned = extra_repairs(prog, preds, demos, rec['outcomes'])
                if scanned:
                    joint_calls += 1
                    joint_cells += scanned
                kids.extend(new_kids)
            first = next((j for j, o in enumerate(rec['outcomes']) if not o['match'] and preds[j] is not None), None)
            if feedback and first is not None:
                feedback_analyses += 1
                kids.extend(derive_children(prog, preds[first], demos[first][1], first))
            if kids:
                rec['children'] = [{'program': p, 'origin': o} for p, o in kids]
                for p, o in kids:
                    o = dict(o, parent_id=rec['id'])
                    queue.append((p, o))
                    derived += 1
    accepted.sort(key=lambda t: (len(t[1]), t[0]))
    selected, outs = [], []
    for rid, prog in accepted:
        try:
            out = tuple(run(prog, g) for g in tests)
        except ValueError:
            continue
        if out not in outs:
            selected.append(rid)
            outs.append(out)
        if len(outs) == 2:
            break
    fallback = not outs
    if fallback:
        outs = [tuple(tests)]
    if len(outs) == 1:
        outs.append(outs[0])
    residual_accepted = sum(1 for rid, _ in accepted if trace[rid]['origin']['type'] == 'residual')
    return {'attempts': [{'attempt_1': as_list(outs[0][i]), 'attempt_2': as_list(outs[1][i])} for i in range(len(tests))],
            'trace': trace, 'selected_rule_ids': selected, 'fallback_identity': fallback,
            'stats': {'candidates': len(trace), 'checks': checks, 'step_applications': steps_applied,
                      'sampler_draws': draws, 'derived_children': derived, 'feedback_pair_analyses': feedback_analyses,
                      'joint_calls': joint_calls, 'joint_constraint_cells': joint_cells,
                      'accepted_programs': len(accepted), 'accepted_residual_derived': residual_accepted,
                      'selected_residual_derived': sum(1 for rid in selected if trace[rid]['origin']['type'] == 'residual'),
                      'max_candidates': max_candidates, 'max_checks': max_checks, 'seed': seed, 'feedback': feedback}}
