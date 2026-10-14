"""For each results.json of the audit run and each in-cache cell (as-compiled and aligned columns),
does the audit ratio fall inside the 95% interval of the same cell in the earlier S3 files drawn
on the same CPU model? Earlier files with a byte-identical A/A half-width above 2% are reported
but marked (the written 'usable' rule). Usage: reproduce.py AUDIT_DIR EARLIER_DIR [EARLIER_DIR...]"""
import glob, json, os, sys
def load(root):
    out = []
    for p in sorted(glob.glob(os.path.join(root, '*', 'results.json'))):
        d = json.load(open(p)); out.append((os.path.basename(os.path.dirname(p)), d))
    return out
audit = load(sys.argv[1]); earlier = sum((load(r) for r in sys.argv[2:]), [])
for an, a in audit:
    cpu = a['run']['runner']['cpu_model']
    ref = [(n, d) for n, d in earlier if d['run']['runner']['cpu_model'] == cpu]
    usable_ref = [(n, d) for n, d in ref if d['controls']['aa']['half_width_pct'] <= 2.0]
    print(f"\n== audit {an}: {cpu}; A/A {a['controls']['aa']['half_width_pct']:.2f}%; verdict {a['verdict']['form']}; "
          f"earlier files on this CPU: {len(ref)} ({len(usable_ref)} usable)")
    if not ref: print('   no earlier file on this CPU model: nothing to compare'); continue
    tot = inside_all = inside_any = 0; misses = []
    for c in a['cells']:
        if c['size_class'] not in ('L1', 'L2'): continue
        for col in ('as_compiled', 'aligned'):
            r = c['ratio'] if col == 'as_compiled' else c['aligned']['ratio']
            hits = []
            for n, d in usable_ref:
                e = next((x for x in d['cells'] if x['cell_id'] == c['cell_id']), None)
                if e is None: continue
                lo, hi = e['ci95'] if col == 'as_compiled' else e['aligned']['ci95']
                hits.append((lo <= r <= hi, lo, hi, d['run']['id']))
            if not hits: continue
            tot += 1
            if all(h[0] for h in hits): inside_all += 1
            if any(h[0] for h in hits): inside_any += 1
            if not all(h[0] for h in hits):
                misses.append(f"   {c['cell_id']:16s} {col:11s} audit {r:.3f}  earlier " + '; '.join(f"[{lo:.3f},{hi:.3f}]{'' if ok else '*'}" for ok, lo, hi, _ in hits))
    print(f"   in-cache ratios: {tot}; inside every earlier interval: {inside_all}; inside at least one: {inside_any}")
    print('\n'.join(misses))
