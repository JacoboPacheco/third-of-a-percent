# What the placement exemption depends on: a minimum size for D

This is a sensitivity analysis, not a verdict. Every result figure in this document sits in a block that
`robustness/placement_floor.py --report` writes from the stored pooled files. The prose around the block states no result
figure, only the parameters of the rules (the floors, the `64`-byte line); `tests/test_placement_floor.py` checks that, and checks
the sentences below that name rows, cells and words against `robustness/placement-floor.json`.

## What was computed

A forward in-cache cell is exempt from the forward rule of the pooled verdict (`harness/criteria-v3.json`,
`v3.placement_sensitive`, applied in `harness/pool.py`) when two things hold. The statistical part: the pooled `95%`
interval of D, the ratio of the cell's FAST/NONE ratio as compiled to its FAST/NONE ratio with loops aligned
(`-falign-loops=64`), excludes `1`. The mechanical part: the hot loops of the NONE and the FAST build differ in where they
start in a `64`-byte line, in length, in the number of `64`-byte windows they touch or in an extra window. An exempt cell
is left out of the forward rule and out of X, and is listed with both pooled ratios and the interval of D in the CPU
model's verdict line. Neither part says how far from `1` D has to be: a cell whose D is a fraction of a percent away from `1`
is exempt as soon as its interval clears `1`.

`placement_floor.py` asks how much of the stored picture depends on that. It reads only the stored pooled files, one per
pool in the table below, never a timing file, and takes no new measurement. For each stored CPU-model block it copies the
block, recomputes the exemption flag of every cell under four rules, and applies `harness/pool.py`'s own verdict function
(`pool.cpu_verdict`, read-only use) to the copy:

- the stored rule (the statistical and the mechanical part);
- the stored rule, and also `|D - 1|` of at least `2%`;
- the stored rule, and also `|D - 1|` of at least the layout A/A half-width of the same pool and CPU model, taken as the
  largest half-width among the two designated pairs `k02_add_fwd.L1` and `k02_add_fwd.L2` (the definition in
  `harness/criteria-v2.json`; `harness/criteria-v3.json` no longer uses that half-width as a cutoff);
- the stored rule, and also `|D - 1|` of at least the larger of the two.

The stored rule must reproduce every stored verdict exactly (word, reason, line and numbers); the script fails
otherwise, so a reproduction failure cannot pass as a finding. The two floors are examples of a size requirement chosen
for this note. They are not proposed as replacements, and no stored verdict, pool or rule file was changed.

Pools read: three earlier x86-64 pools of different sizes (`s4`, `s6`, `s7`; the page's x86-64 verdicts come from `s7`),
the x86-64 replication set (`s9-x86-c`) and the x86-64 pool of both (`s9-x86-ac`), the Arm pool (`s8-arm`), the Arm
replication set (`s9-arm-b`) and the Arm pool of both (`s9-arm-ab`). A CPU model with fewer than the minimum number of
jobs has no verdict; its exempt cells are listed and its row is left out of the word table.

## The numbers (generated)

<!-- placement-floor:begin -->
### Verdict words under the alternative exemption rules (generated)

One row per pool and CPU model with enough jobs for a verdict. The first word column is the stored word. A word followed by (changed) differs from it.

| pool | CPU model | jobs | stored rule | D floor 2% | D floor = layout A/A | D floor = larger | layout A/A half-width % | exempt cells: stored / 2% / layout / larger |
|---|---|---:|---|---|---|---|---:|---|
| s4 | EPYC 7763 | 19 | map | map | map | map | 0.575 | 3 / 3 / 3 / 3 |
| s4 | EPYC 9V45 | 5 | map | inconclusive (changed) | map | inconclusive (changed) | 0.725 | 2 / 1 / 2 / 1 |
| s4 | EPYC 9V74 | 5 | map | map | map | map | 0.562 | 3 / 2 / 3 / 2 |
| s6 | EPYC 7763 | 20 | map | map | map | map | 0.590 | 3 / 3 / 3 / 3 |
| s6 | EPYC 9V45 | 20 | map | inconclusive (changed) | map | inconclusive (changed) | 0.264 | 3 / 1 / 3 / 1 |
| s6 | EPYC 9V74 | 23 | map | map | map | map | 0.441 | 3 / 2 / 3 / 2 |
| s6 | Xeon 8573C | 6 | inconclusive | inconclusive | inconclusive | inconclusive | 1.510 | 1 / 1 / 1 / 1 |
| s6 | Xeon 6973P-C | 6 | inconclusive | inconclusive | inconclusive | inconclusive | 2.201 | 2 / 1 / 1 / 1 |
| s7 | EPYC 7763 | 29 | map | map | map | map | 0.413 | 3 / 3 / 3 / 3 |
| s7 | EPYC 9V45 | 23 | map | inconclusive (changed) | map | inconclusive (changed) | 0.241 | 3 / 1 / 3 / 1 |
| s7 | EPYC 9V74 | 28 | map | map | map | map | 0.369 | 3 / 2 / 3 / 2 |
| s7 | Xeon 8573C | 7 | inconclusive | inconclusive | inconclusive | inconclusive | 1.303 | 1 / 1 / 1 / 1 |
| s7 | Xeon 6973P-C | 7 | map | map | map | map | 1.824 | 2 / 1 / 1 / 1 |
| s9-x86-c | EPYC 7763 | 19 | map | map | map | map | 0.434 | 3 / 3 / 3 / 3 |
| s9-x86-c | EPYC 9V45 | 5 | inconclusive | inconclusive | inconclusive | inconclusive | 0.334 | 2 / 1 / 2 / 1 |
| s9-x86-c | EPYC 9V74 | 7 | map | map | map | map | 0.895 | 3 / 2 / 2 / 2 |
| s9-x86-c | Xeon 8573C | 7 | map | inconclusive (changed) | map | inconclusive (changed) | 0.410 | 3 / 1 / 3 / 1 |
| s9-x86-ac | EPYC 7763 | 48 | map | map | map | map | 0.326 | 3 / 3 / 3 / 3 |
| s9-x86-ac | EPYC 9V45 | 28 | map | map | map | map | 0.210 | 3 / 1 / 3 / 1 |
| s9-x86-ac | EPYC 9V74 | 35 | map | map | map | map | 0.347 | 3 / 2 / 3 / 2 |
| s9-x86-ac | Xeon 8573C | 14 | inconclusive | inconclusive | inconclusive | inconclusive | 0.682 | 2 / 1 / 2 / 1 |
| s9-x86-ac | Xeon 6973P-C | 8 | inconclusive | inconclusive | inconclusive | inconclusive | 1.615 | 1 / 1 / 1 / 1 |
| s8-arm | Neoverse-N2 | 30 | inconclusive | inconclusive | inconclusive | inconclusive | 2.402 | 4 / 2 / 2 / 2 |
| s9-arm-b | Neoverse-N2 | 29 | inconclusive | inconclusive | inconclusive | inconclusive | 2.899 | 4 / 2 / 1 / 1 |
| s9-arm-ab | Neoverse-N2 | 59 | map | map | map | map | 1.939 | 4 / 2 / 2 / 2 |

### Exempt cells that would not pass the forward rule if they were judged (generated)

A cell is listed when, in at least one pool, its aligned ratio is above 1.02 or its aligned upper interval end is above the forward limit of that CPU model. Ranges run over the pools in which the cell is exempt; the last three columns count the pools in which it stays exempt.

| CPU model | cell | pools (jobs) | aligned ratio | aligned upper end | \|D - 1\| % | pools with ratio above 1.02 / interval above limit | stays exempt: 2% floor | layout floor | larger floor |
|---|---|---|---|---|---|---|---|---|---|
| EPYC 7763 | k03_stencil.L1 | s4 (19), s6 (20), s7 (29), s9-x86-c (19), s9-x86-ac (48) | 1.0559 to 1.0563 | 1.0564 to 1.0568 | 4.71 to 4.74 | 5 / 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 |
| EPYC 9V45 | k03_stencil.L1 | s4 (5), s6 (20), s7 (23) | 1.0151 to 1.0160 | 1.0203 to 1.0239 | 1.35 to 1.50 | 0 / 3 of 3 | 0 of 3 | 3 of 3 | 0 of 3 |
| Xeon 8573C | k02_add_fwd.L1 | s9-x86-c (7) | 1.0604 | 1.0633 | 0.57 | 1 / 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 |
| Xeon 6973P-C | k02_add_fwd.L1 | s6 (6), s7 (7), s9-x86-c (1), s9-x86-ac (8) | 1.1985 to 1.2044 | 1.2043 to 1.2177 | 2.58 to 2.75 | 4 / 4 of 4 | 4 of 4 | 4 of 4 | 4 of 4 |
| Xeon 8370C | k02_add_fwd.L1 | s7 (1), s9-x86-c (1), s9-x86-ac (2) | 1.0569 to 1.0571 | 1.0575 to 1.0578 | 0.95 to 1.03 | 3 / 3 of 3 | 0 of 3 | 3 of 3 | 0 of 3 |
| Neoverse-N2 | k08_matmul.L1 | s8-arm (30), s9-arm-b (29), s9-arm-ab (59) | 1.5891 to 1.5894 | 1.5893 to 1.5895 | 2.59 to 2.62 | 3 / 3 of 3 | 3 of 3 | 2 of 3 | 2 of 3 |
| Neoverse-V3 | k08_matmul.L1 | s9-arm-b (1), s9-arm-ab (1) | 1.6417 | 1.6445 | 6.63 | 2 / 2 of 2 | 2 of 2 | 2 of 2 | 2 of 2 |

### Facts read from the stored files (generated)

- 25 pool and CPU-model rows have enough jobs for a verdict. The stored rule reproduces the stored verdict of every row, with the same word, reason, line and numbers.
- The stored rule, and also |D - 1| >= 2%: 4 row(s) change word: s4 EPYC 9V45 map to inconclusive (k03_stencil.L1 judged and missing the forward rule); s6 EPYC 9V45 map to inconclusive (k03_stencil.L1 judged and missing the forward rule); s7 EPYC 9V45 map to inconclusive (k03_stencil.L1 judged and missing the forward rule); s9-x86-c Xeon 8573C map to inconclusive (k02_add_fwd.L1 judged and missing the forward rule).
- The stored rule, and also |D - 1| >= the pool's layout A/A half-width (largest of the designated pairs): no row changes word. Rows whose word stays although a cell missing the forward rule is judged: s9-arm-b Neoverse-N2 inconclusive (k08_matmul.L1).
- The stored rule, and also |D - 1| >= the larger of the 2% floor and the layout A/A half-width: 4 row(s) change word: s4 EPYC 9V45 map to inconclusive (k03_stencil.L1 judged and missing the forward rule); s6 EPYC 9V45 map to inconclusive (k03_stencil.L1 judged and missing the forward rule); s7 EPYC 9V45 map to inconclusive (k03_stencil.L1 judged and missing the forward rule); s9-x86-c Xeon 8573C map to inconclusive (k02_add_fwd.L1 judged and missing the forward rule). Rows whose word stays although a cell missing the forward rule is judged: s9-arm-b Neoverse-N2 inconclusive (k08_matmul.L1).
- 82 exempt-cell records over all pools and CPU models (including rows with too few jobs for a verdict). |D - 1| runs from 0.133% to 93.95%; 31 records are below 2% and 14 are below the layout A/A half-width of their pool and CPU model.
- Exempt cells with an aligned ratio above 1.02, 18 records, 6 distinct cells: EPYC 7763 k03_stencil.L1; Xeon 8573C k02_add_fwd.L1; Xeon 6973P-C k02_add_fwd.L1; Xeon 8370C k02_add_fwd.L1; Neoverse-N2 k08_matmul.L1; Neoverse-V3 k08_matmul.L1.
<!-- placement-floor:end -->

## What it means, in plain words

- **The stored words depend on a few small exemptions.** Under a floor of `2%` the EPYC 9V45 rows of the three earlier
  x86-64 pools and the Xeon 8573C row of the x86-64 replication set would go from MAP to INCONCLUSIVE. Under the larger of
  the two floors the same rows change. Under the layout A/A floor alone no row changes word. Every other row keeps its
  word under all four rules.
- **The EPYC 9V45 rows hinge on one cell.** The cell is the stencil at the L1 size. Its aligned ratio is under the point
  limit, but the upper end of its aligned interval is above the forward limit in the three earlier pools, and its D is
  less than `2%` from `1`. Exempt, the cell is not judged; judged, it misses the forward rule on the interval. In the
  replication set the cell is not exempt at all and the 9V45 word is INCONCLUSIVE already; in the pool of both x86-64
  sets the upper end is under the limit, so the word holds under every rule.
- **The Xeon 8573C row of the replication set hinges on the forward add at L1.** In that set the cell is exempt: its D is
  less than `1%` from `1`, and its aligned ratio is above the point limit. In the pools `s7` and `s9-x86-ac` the same cell
  is not exempt, it is judged, it misses the forward rule, and the word is INCONCLUSIVE. The MAP of the replication set
  for this model therefore rests on the exemption of that one cell.
- **Besides those two, the cells that would miss the forward rule are exempt by a D of at least `2%`, with two
  exceptions.** The exceptions are the Xeon 8370C forward add at L1 (a D under `2%`, one or two jobs per pool, no verdict)
  and, under the layout A/A floor only, the Neoverse-N2 matmul at L1 in the Arm replication set, which would be judged;
  that row is INCONCLUSIVE with or without it. The EPYC 7763 stencil at L1, the Xeon 6973P-C forward add at L1 and the
  Neoverse-V3 matmul at L1 stay exempt under every rule.
- **What this does not show.** It does not say which rule is right, and the two floors are not the only choices. D is
  itself a pooled statistic with an interval, and the layout A/A half-width differs between pools and CPU models by an
  order of magnitude. The mechanical part of the exemption is not varied here. The analysis reads the stored pools only
  and says nothing about whether the cells would stay where they are in another build or on another machine.
- **Where this matters.** The stored rule leaves out of the forward rule every cell that meets its two parts, whatever the
  size of D. This note shows which stored words rest on that for a small D; it does not say whether leaving those cells
  out is right.

## Reproduce

```
python robustness/placement_floor.py             # writes robustness/placement-floor.json
python robustness/placement_floor.py --report    # also rewrites the generated block above
python robustness/placement_floor.py --verify    # recomputes everything; fails on any difference (the file, the README block, the input hashes)
```

Nothing here changes `harness/pool.py`, `harness/criteria-v3.json` or any file under `results/`.
