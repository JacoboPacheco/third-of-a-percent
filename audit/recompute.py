"""Independent recompute of ratio-of-medians and percentile-bootstrap 95% intervals from the raw
samples in S3 results.json files. numpy only; does not import harness/. Seed 7 (not the harness seed),
10000 resamples per side, vectorized. Prints stored vs recomputed for every cell and column, and
flags a cell when the stored point ratio differs at all or a stored bound differs by more than
the bootstrap's own Monte Carlo slack (0.5% of the ratio)."""
import glob, json, sys
import numpy as np

RNG = np.random.default_rng(7)
B = 10000

def boot(none, fast):
    none, fast = np.asarray(none), np.asarray(fast)
    r = np.median(fast) / np.median(none)
    bn = np.median(none[RNG.integers(0, len(none), (B, len(none)))], axis=1)
    bf = np.median(fast[RNG.integers(0, len(fast), (B, len(fast)))], axis=1)
    lo, hi = np.percentile(bf / bn, [2.5, 97.5])
    return r, lo, hi

def main(paths):
    worst = 0.0; n = 0; flagged = []
    for p in paths:
        d = json.load(open(p))
        tag = d['run']['id'] + ' ' + d['run']['runner']['cpu_model'][:14] + ' ' + p.split('-j')[-1][:1]
        rows = [(c['cell_id'], '', c) for c in d['cells']] + [(c['cell_id'], 'aligned', c['aligned']) for c in d['cells'] if c.get('aligned')]
        rows += [(g['name'], '', g) for g in d['programs']]
        aa = d['controls']['aa']
        for cid, col, c in rows:
            if not c.get('none_ns'): continue
            r, lo, hi = boot(c['none_ns'], c['fast_ns'])
            sr, (slo, shi) = c['ratio'], c['ci95']
            dpt = abs(r - sr); dlo = abs(lo - slo) / sr; dhi = abs(hi - shi) / sr
            n += 1; worst = max(worst, dlo, dhi)
            bad = dpt > 1e-12 or dlo > 0.005 or dhi > 0.005
            if bad: flagged.append((tag, cid, col, sr, r, slo, lo, shi, hi))
            print(f"{tag:34s} {cid:16s} {col:7s} stored {sr:.4f} [{slo:.4f},{shi:.4f}]  mine {r:.4f} [{lo:.4f},{hi:.4f}]{'  <-- DIFF' if bad else ''}")
    print(f"\n{n} pairs recomputed; largest bound gap {100*worst:.3f}% of the ratio; flagged {len(flagged)}")
    for f in flagged: print('FLAG', f)

if __name__ == '__main__':
    main(sorted(sum((glob.glob(a) for a in sys.argv[1:]), [])))
