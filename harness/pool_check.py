"""An independent recomputation of a sample of pooled.json's numbers (criteria-v3), called by scripts/check.py.

It does not import harness/pool.py or harness/stats.py and does not use numpy: it reads the raw
samples from the per-job results.json files named in pooled.json "inputs", and redoes

  - every per-job ratio median(B)/median(A) of the sampled statistics (must match to 1e-12),
  - the pooled ratio exp(mean ln r_j) (must match to 1e-9),
  - the two-level bootstrap interval with its own plain nested loop, Python's random.Random(7) and
    4000 resamples (pool.py: splitmix64 and 2000). The two intervals differ only by Monte Carlo
    error, so each bound must agree within 15 % of the stored interval's width plus 0.05 % of the
    ratio, and the two widths within a factor of 1.5. A pooled interval that left out the
    between-job level, or resampled the wrong thing, fails this.

Sample, per CPU model: the A/A, the layout A/A of k02_add_fwd.L1, and k01_sum_fwd.L1, k02_add_fwd.L1,
k03_stencil.L1, k04_rev.L1, k05_stride2.L2, k06_gather.L1 and k08_matmul.L1 in both columns where
present, plus the placement statistic of k03_stencil.L1 and k02_add_fwd.L1.

Usage: python harness/pool_check.py <pooled.json>     exit 0 if every sampled number agrees.
"""
import json
import math
import os
import random
import sys

SAMPLE_CELLS = ("k01_sum_fwd.L1", "k02_add_fwd.L1", "k03_stencil.L1", "k04_rev.L1", "k05_stride2.L2",
                "k06_gather.L1", "k08_matmul.L1")
PLACEMENT_CELLS = ("k02_add_fwd.L1", "k03_stencil.L1")
B = 4000  # 1000 was too few: a lumpy tail (median of 40, one job) swung its 2.5 % bound by 2 % (run 38258465995)
BOUND_TOL_WIDTH = 0.15
BOUND_TOL_RATIO = 0.0005
WIDTH_FACTOR = 1.5


def med(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def two_level(groups, f, rng):
    """groups: per job, a list of sides; f(medians) -> ratio. Returns (point, per_job, lo, hi)."""
    per_job = [f(*[med(s) for s in g]) for g in groups]
    point = math.exp(math.fsum(math.log(r) for r in per_job) / len(per_job))
    J = len(groups)
    reps = []
    for _ in range(B):
        acc = 0.0
        for _ in range(J):
            g = groups[rng.randrange(J)]
            acc += math.log(f(*[med([s[rng.randrange(len(s))] for _ in range(len(s))]) for s in g]))
        reps.append(math.exp(acc / J))
    reps.sort()
    return point, per_job, reps[int(0.025 * B)], reps[int(0.975 * B) - 1]


def ratio2(a, b):
    return b / a


def ratio4(n, f, na, fa):
    return (f / n) / (fa / na)


def check(path):
    with open(path, encoding="utf-8") as fh:
        pooled = json.load(fh)
    base = os.path.dirname(os.path.abspath(path))
    docs = {}
    for inp in pooled["inputs"]:
        with open(os.path.join(base, inp["path"]), encoding="utf-8") as fh:
            docs[inp["path"]] = json.load(fh)
    rng = random.Random(7)
    problems, n = [], 0
    for blk in pooled["cpus"]:
        cpu = blk["cpu_model"]
        jobs = [docs[i["path"]] for i in pooled["inputs"] if i["cpu_model"] == cpu]  # pooled.json's job order
        todo = [("aa", [[d["controls"]["aa"]["a_ns"], d["controls"]["aa"]["b_ns"]] for d in jobs], ratio2, blk["aa"])]
        if "k02_add_fwd.L1" in blk["layout_aa"]:
            lay = [next(p for p in d["controls"]["layout_aa"] if p["id"] == "k02_add_fwd.L1") for d in jobs]
            todo.append(("layout k02_add_fwd.L1", [[p["a_ns"], p["b_ns"]] for p in lay], ratio2,
                         blk["layout_aa"]["k02_add_fwd.L1"]))
        stored_cells = {c["cell_id"]: c for c in blk["cells"]}
        for cid in SAMPLE_CELLS:
            if cid not in stored_cells:
                continue
            cs = [next(c for c in d["cells"] if c["cell_id"] == cid) for d in jobs]
            todo.append((f"{cid} as compiled", [[c["none_ns"], c["fast_ns"]] for c in cs], ratio2,
                         stored_cells[cid]["as_compiled"]))
            todo.append((f"{cid} aligned", [[c["aligned"]["none_ns"], c["aligned"]["fast_ns"]] for c in cs], ratio2,
                         stored_cells[cid]["aligned"]))
            if cid in PLACEMENT_CELLS and "placement" in stored_cells[cid]:
                todo.append((f"{cid} placement", [[c["none_ns"], c["fast_ns"], c["aligned"]["none_ns"],
                                                   c["aligned"]["fast_ns"]] for c in cs], ratio4,
                             stored_cells[cid]["placement"]["d"]))
        for name, groups, f, st in todo:
            n += 1
            point, per_job, lo, hi = two_level(groups, f, rng)
            slo, shi = st["ci95"]
            width = shi - slo
            tol = BOUND_TOL_WIDTH * width + BOUND_TOL_RATIO * st["ratio"]
            bad = []
            if len(per_job) != len(st["per_job"]) or any(abs(x - y) > 1e-12 * abs(y) for x, y in zip(per_job, st["per_job"])):
                bad.append("per-job ratios differ")
            if abs(point - st["ratio"]) > 1e-9 * st["ratio"]:
                bad.append(f"pooled ratio {point:.6f} vs stored {st['ratio']:.6f}")
            if abs(lo - slo) > tol or abs(hi - shi) > tol:
                bad.append(f"interval [{lo:.5f}, {hi:.5f}] vs stored [{slo:.5f}, {shi:.5f}] (tolerance {tol:.5f})")
            if width > 0 and not (1 / WIDTH_FACTOR <= (hi - lo) / width <= WIDTH_FACTOR):
                bad.append(f"width {hi - lo:.5f} vs stored {width:.5f}")
            line = (f"{cpu[:34]:34s} {name:28s} J={len(groups):2d} stored {st['ratio']:.4f} [{slo:.4f}, {shi:.4f}]  "
                    f"independent {point:.4f} [{lo:.4f}, {hi:.4f}]")
            print(("   ok   " if not bad else "   FAIL ") + line + ("  " + "; ".join(bad) if bad else ""))
            if bad:
                problems.append(f"{cpu} {name}: " + "; ".join(bad))
    return n, problems


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    n, problems = check(argv[1])
    print(f"   {n} pooled statistics recomputed independently; {len(problems)} disagree")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
