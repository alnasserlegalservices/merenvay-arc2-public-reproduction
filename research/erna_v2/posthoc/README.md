# Post-hoc sampler diagnostic

This directory retains the script and output supplied in the author's 14 November PR kit, unchanged. It is outside the original frozen experiment and was not preregistered. The publication workflow verified the source kit's hashes and the analytic formula; it did not repeat the 600,000-draw Monte Carlo.

The exact formula concerns the two identified mirror recipes, not an exhaustively established set of all matching programs. With independent draws and a fixed draw count of 153, their combined probability is `1-(1-1/4096)^153`, approximately 0.0367. The draw count was observed after the original run and is not the candidate cap. This does not establish causal benefit, seed robustness, or a probability that luck explains the arm difference.

The script loads a complete labeled public task file, then evaluates programs on its training pairs. Test answers are not used in the calculation; they are not technically inaccessible to the process. The retained output's phrase “exact per-draw probability” should be read specifically as the probability of the two identified recipes. No exhaustive support search was performed.

To run it, extract the complete original archive. From this release directory, with an extracted package at `/tmp/merenvay-v2-original/MERENVAY_E_RNA_v2`:

```sh
python3 -I -B posthoc/posthoc_reach.py /tmp/merenvay-v2-original/MERENVAY_E_RNA_v2
```

This optional diagnostic is not required to reproduce the frozen scored run. Runtime depends on the host.
