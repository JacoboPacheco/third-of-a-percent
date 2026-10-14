"""Per-file summary of an S3-style results directory: CPU, A/A half-width (stored and recomputed
from details.json raw samples with an independent numpy bootstrap), verdict form, N, layout A/A,
placement-sensitive cells."""
import glob, json, os, sys
import numpy as np
rng = np.random.default_rng(11)
def hw(a, b):
    a, b = np.asarray(a), np.asarray(b)
    ra = np.median(a[rng.integers(0, len(a), (10000, len(a)))], 1)
    rb = np.median(b[rng.integers(0, len(b), (10000, len(b)))], 1)
    lo, hi = np.percentile(rb / ra, [2.5, 97.5]); return (hi - lo) / 2 * 100
for root in sys.argv[1:]:
    for p in sorted(glob.glob(os.path.join(root, '*', 'results.json'))):
        d = json.load(open(p)); v = d['verdict']; aa = d['controls']['aa']
        det = json.load(open(os.path.join(os.path.dirname(p), 'details.json')))
        mine = hw(det['aa']['a_ns'], det['aa']['b_ns'])
        n = (v.get('n') or {}).get('median')
        print(os.path.basename(os.path.dirname(p))[8:], f"AA stored {aa['half_width_pct']:.2f}% mine {mine:.2f}%", v['form'],
              'N=' + (f"{n:.2f}" if n else '-'), f"layAA {v.get('layout_aa_half_width_pct') or 0:.2f}",
              [x['cell_id'] for x in v.get('placement_sensitive', [])])
    c = os.path.join(root, 'combined.json')
    if os.path.exists(c): print('combined:', json.dumps(json.load(open(c)))[:900])
