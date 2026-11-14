"""Post-hoc, NOT preregistered. Run from the v2 package root:  python3 -I -B ../MERENVAY_E_RNA_v2_PR_KIT/posthoc/posthoc_reach.py .
Question: how likely is it that the frozen random sampler, with the colours of task 0c786b71, draws a
program that matches all of that task's TRAINING pairs? Uses training pairs only. No test answers. No code change."""
import sys, json, glob, random, gzip, math
pkg = sys.argv[1]; sys.path.insert(0, pkg)
import erna2
task = json.load(open(glob.glob(pkg + '/data/**/0c786b71.json', recursive=True)[0]))
demos = erna2._validated_demos(task['train'])
colors = sorted({v for a, b in demos for g in (a, b) for row in g for v in row})
n_ops = len(erna2.OPERATORS) - 1
p_exact = 2 * (1 / n_ops * 1 / 4) ** 2 * 0.5   # P(2 steps)=1/2; both steps mirror_concat; either of the two accepted orders
rng = random.Random(777); N = 600_000; cache = {}; hits = {}
for _ in range(N):
    prog = erna2.sample_program(rng, colors); k = erna2.key(prog)
    if k not in cache:
        ok = True
        for a, b in demos:
            try:
                if erna2.run(prog, a) != b: ok = False; break
            except ValueError: ok = False; break
        cache[k] = ok
    if cache[k]: hits[k] = hits.get(k, 0) + 1
nf = json.load(gzip.open(pkg + '/results/run1/traces/no_feedback/0c786b71.json.gz'))
draws = nf['stats']['sampler_draws']
print('operators in sampler:', n_ops, '| exact per-draw probability: 1/%d' % round(1 / p_exact))
print('Monte Carlo: %d draws, %d matched all training pairs, distinct matching programs: %d' % (N, sum(hits.values()), len(hits)))
for k, v in sorted(hits.items(), key=lambda kv: -kv[1]): print('  ', v, k)
print('no_feedback arm sampler draws on this task:', draws)
print('P(at least one matching draw in those draws) = %.4f' % (1 - (1 - p_exact) ** draws))
