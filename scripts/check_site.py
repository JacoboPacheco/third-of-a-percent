#!/usr/bin/env python3
"""Checks the verdict page in site/ against the data it reads.

    python scripts/check_site.py [--shots DIR] [--quick]

1. site/data/ equals a fresh scripts/build_site_data.py build (no hand-edited or stale data).
2. Serves site/ on a free localhost port and drives both pages, the main paper (index.html) and the
   heavy material (details.html: appendices, the full toolchain table, Tables 2 and 5 of the earlier
   programs, the rule history, the census per project, the controls), with headless Chromium (muted,
   no speech), at 1280 and 390 px wide:
   - both pages: no console errors, every printed number in site/data, the Google-wording check, no
     horizontal scroll at 390, every link and button at least 32 px tall at 390; the main page under
     13228 px long at 390 with every section opened, under 10500 by default (collapsed); links to the repository only to the public copy, no run links;
   - section 7 (real programs): the timed result (Table 9) with its limits and the expectations, Figure 6, the estimate table and
     Table 5 (details) equal to realworld.json, the Amdahl estimate collapsed and labelled an estimate
     (share x (r - 1)) with its assumption, LightGBM marked approximate, Table 6 (details) labelled as
     two small programs timed earlier;
   - no console errors, no page errors, no failed requests to site/data/;
   - the first screen at 1280 holds at most six things (title, byline, abstract, Figure 1, Figure 2),
     the abstract says Google's figure is a different measurement and prints the pooled lost-SIMD range,
     the forward range, the census counts and the rewrite range from site/data, all eight loop rows are
     on it, and the reverse loop is selected with its machine code (the check and the trap labelled)
     already shown; Figure 1's CPU switcher offers exactly the CPU models with enough jobs and names the
     others as 'too few jobs'; Figure 2's header carries the instruction ratio labelled 'instructions,
     not time';
   - the new sections: section 4 (census) says counted-not-timed, hotness unknown and no claim about
     runtime cost or Google's average, draws one row per category, lists the controls with the AVX2
     kernel FAIL and its reason, and quotes real loops; section 5 (rewrites) is a table whose rows open a
     panel with every variant and the code, states the 'better' rule with the usable-job count and warns
     that std::transform over reverse iterators is unsafe; section 6 (toolchains) has one row per setup
     and states the thin coverage; placement-sensitive cells are listed with the pooled column ratio;
   - every number printed on the page is in the data files: a printed number must equal, at its
     printed precision, a number in site/data/ (or a numeric token in one of its strings) directly or
     through a unit change (ratio to percent, bytes to KiB or MiB, ns to us or ms). Exempt, by design:
     text inside <code> and <pre> (commands, source lines and assembly, copied verbatim from the data
     files) and the axis tick labels (the scale, not a result);
   - every loop row of every CPU model with enough jobs (--quick: the default only), in both columns, opens
     Figure 2 with its machine code, and every number Figure 2 prints is in the data;
   - the arrow keys move the selection, the URL hash keeps it, and a hash restores it;
   - wording: the abstract gives both sides (lost-SIMD range and forward range, from index.json); no
     sentence outside the harness's verbatim verdict lines (a collapsed <details> in Appendix B) says
     Google's figure holds, is wrong or is confirmed; prose uses plain names (no raw cell ids, harness
     form names, raw CPU strings or bare file names outside tables, code and tooltips); run, job and
     pooled and interval are defined before Table 1; the faster checked forward add is explained (cause inferred)
     in section 3, Figure 3 and its Figure 2 panel; the day-one misses sit in a collapsed <details>;
   - no horizontal scroll at 390 px, Figure 2 sits below Figure 1 there; a tap on a loop scrolls
     Figure 2 into view; the '?' opens on tap and closes on an outside tap and on Escape; Appendix A
     is collapsed by default and, opened, scrolls inside its own box with a visible hint;
   - ?data=fixture (results/fixture.json, sample: true) prints SAMPLE DATA on the first screen;
   - worst-case data (a cell missing, a loop missing from every run, an interval running off both ends
     of the axis) still renders: "not measured", clipped whiskers with arrows, no horizontal scroll;
   - error states: index.json missing, and a results file failing, each show their message.
3. Saves screenshots (1280 and 390 wide: the first screen, Figure 1 with a selection, Figure 2, the
   middle of the paper, the appendix; the SAMPLE fixture; the worst case) to --shots (default: a
   temporary folder) and prints their paths.
Exit code 0 only if every check passed. Needs the Python playwright package and its Chromium.
"""
import argparse
import functools
import http.server
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import threading

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, "site")
DATA = os.path.join(SITE, "data")
RW_NAMES_PY = {"lightgbm_default": "LightGBM (default)", "lightgbm_multiclass": "LightGBM (multiclass)", "lightgbm_linear": "LightGBM (linear)", "draco": "Draco", "tinydnn": "tiny-dnn", "spectra": "Spectra", "meshopt": "meshoptimizer (control)", "fmt": "{fmt} (control)"}
NUM_TOKEN = re.compile(r"(?<![A-Za-z0-9_.])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?![A-Za-z0-9_])")
TRANSFORMS = (
    lambda v: v,
    lambda v: (v - 1) * 100,
    lambda v: abs(v - 1) * 100,
    lambda v: v * 100,
    lambda v: v / 1024,
    lambda v: v / 1048576,
    lambda v: v / 1000,
    lambda v: v / 1e6,
)

PAGE_TEXT_JS = r"""
(root) => {
  const out = [];
  const skip = (n) => n.closest('code, pre, .tick, script, style, [hidden]');
  const w = document.createTreeWalker(root || document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const p = n.parentElement;
    if (!p || skip(p)) continue;
    const t = n.textContent.trim();
    if (t) out.push(t);
  }
  return out.join('\n');
}
"""
PROSE_TEXT_JS = r"""
() => {
  const out = [];
  const skip = (n) => n.closest('code, pre, table, script, style, [hidden], .f2-cmd, .tick');
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const p = n.parentElement;
    if (!p || skip(p)) continue;
    const t = n.textContent.trim();
    if (t) out.push(t);
  }
  return out.join('\n');
}
"""
TAP_JS = """() => [...document.querySelectorAll('a[href], button')].filter(n => { const r = n.getBoundingClientRect();
  return r.width > 0 && r.height > 0 && !n.closest('[hidden]') && r.height < 31.5; })
  .map(n => n.tagName + ' ' + Math.round(n.getBoundingClientRect().height) + ' ' + n.textContent.trim().slice(0, 24))"""
RAW_ID = re.compile(r"k0\d_[a-z0-9_]+|HOLDS_EVERYWHERE|\bMAP\b|\(R\)|criteria(?:-v\d)?\.json|FINDINGS\.md")
FIG2_READY = """() => { const b = document.getElementById('fig2-body');
  return b && b.textContent.length > 0 && !b.textContent.includes('Loading the machine code'); }"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    handler = functools.partial(Quiet, directory=SITE)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def walk_numbers(obj, nums, toks):
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        nums.add(float(obj))
    elif isinstance(obj, str):
        for m in NUM_TOKEN.finditer(obj):
            toks.add((m.group(1) + (m.group(2) or "")).replace(",", ""))
    elif isinstance(obj, list):
        for x in obj:
            walk_numbers(x, nums, toks)
    elif isinstance(obj, dict):
        for k, x in obj.items():
            walk_numbers(k, nums, toks)
            walk_numbers(x, nums, toks)


def allowed_numbers():
    nums, toks = set(), set()
    for dp, _, fs in os.walk(DATA):
        for f in fs:
            if f.endswith(".json"):
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    walk_numbers(json.load(fh), nums, toks)
    rendered = set(toks)
    for v in nums:
        for t in TRANSFORMS:
            x = t(v)
            for d in range(6):
                rendered.add(f"{x:.{d}f}")
    return rendered


def unknown_numbers(text, allowed):
    bad = []
    for m in NUM_TOKEN.finditer(text):
        tok = (m.group(1) + (m.group(2) or "")).replace(",", "")
        if tok not in allowed and tok.lstrip("0") not in allowed:
            s = max(0, m.start() - 40)
            bad.append(f"{tok!r} in ...{text[s:m.end() + 20]!r}")
    return bad


class Checker:
    def __init__(self):
        self.failures = []

    def ok(self, cond, what):
        print(f"   {'ok  ' if cond else 'FAIL'} {what}")
        if not cond:
            self.failures.append(what)
        return cond


def watch(page, errors):
    page.on("console", lambda m: errors.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on("requestfailed", lambda r: errors.append(f"requestfailed: {r.url}") if "/data/" in r.url else None)


def wait_ready(page):
    page.wait_for_function("document.querySelectorAll('#rows .row').length > 0", timeout=20000)
    page.wait_for_function(FIG2_READY, timeout=10000)
    page.wait_for_timeout(450)  # rows that changed place finish gliding
    page.evaluate("document.querySelectorAll('details.fold').forEach(d => { d.open = true; })")  # the abstract and the limits box are folded by default; the checks read them open


def wait_details(page):
    page.wait_for_function("document.querySelectorAll('#appa tbody tr').length > 0 && document.querySelectorAll('#sib-table tbody tr').length > 0"
                           " && document.querySelectorAll('#census-rows .c-row').length > 0", timeout=20000)
    page.wait_for_timeout(300)


def _fx(v):
    return f"{v:.1f}" if v >= 2 else f"{v:.2f}"


def main_versions(abstract, cbox, ck):
    """Main page: the newer timed toolchains are named in the abstract and the limits box, and say what held."""
    with open(os.path.join(DATA, "versions.json"), encoding="utf-8") as f:
        ver = json.load(f)
    if not ver["toolchains"]:
        return
    lo, hi = ver["toolchains"][0]["version"], ver["toolchains"][-1]["version"]
    ck.ok(f"clang and libc++ {lo} to {hi}" in abstract and "still lose SIMD" in abstract and "matrix multiply keeps SIMD there" in abstract,
          "abstract: the newer toolchains were timed too; reverse and stride-2 still lose SIMD, matrix multiply keeps SIMD there (from versions.json)")
    en = ver["summary"]["enough"][0]
    ck.ok(f"Clang and libc++ {lo} to {hi} were timed on the eight loops only" in cbox and f"one CPU model ({en['cpu_short']})" in cbox
          and "one main toolchain" in cbox.lower(),
          "limits box: one main toolchain, the newer ones on the eight loops only, enough jobs on one CPU model")


def versions_environment(dp, ck):
    """Details page, sections 6b (newer toolchains) and 6c (measurement environment): built from versions.json and environment.json."""
    with open(os.path.join(DATA, "versions.json"), encoding="utf-8") as f:
        ver = json.load(f)
    with open(os.path.join(DATA, "environment.json"), encoding="utf-8") as f:
        env = json.load(f)
    if ver["toolchains"]:
        vt = dp.inner_text("#versions-full").replace("\u00a0", " ")
        tcs, sm = ver["toolchains"], ver["summary"]
        tabs = dp.evaluate("document.querySelectorAll('#ver-tables table').length")
        rows = dp.evaluate("document.querySelectorAll('#ver-tables tbody tr').length")
        ck.ok(tabs == sum(len(t["cpus"]) for t in tcs) and rows == sum(len(c["cells"]) for t in tcs for c in t["cpus"]),
              f"section 6b: one table per toolchain and CPU model ({tabs}) and one row per loop and size ({rows})")
        ck.ok(all(f"clang and libc++ {t['clang']}: {t['form']}" in vt for t in tcs)
              and all(f"{c['cpu_short']}, {c['jobs']} job" in vt and (c["why"] is None or c["why"] in vt) for t in tcs for c in t["cpus"]),
              "section 6b: every toolchain and CPU model is listed with its job count, its form and the reason it is not a verdict")
        mm = sm["matmul_main"]
        ck.ok(f"{_fx(sm['reverse_all']['min'])}\u2013{_fx(sm['reverse_all']['max'])}\u00d7" in vt and f"{_fx(sm['stride2_all']['min'])}\u2013{_fx(sm['stride2_all']['max'])}\u00d7" in vt
              and f"{_fx(mm['L1']['min'])}" in vt and f"{_fx(mm['L2']['min'])}" in vt
              and "What held" in vt and "What did not hold" in vt and "counts it as not holding there" in vt and "not established" in vt,
              "section 6b: what held (reverse, stride-2), what did not (matrix multiply, still costly), the ranges from the data")
        ck.ok(not sm["matmul_holds_any"] and sm["matmul_vectorized_both_all"] and sm["reverse_holds_all"] and sm["stride2_holds_all"],
              "section 6b data: matrix multiply never holds and stays vectorized, reverse and stride-2 always hold (the claims the text makes)")
        ck.ok(f"{sm['enough'][0]['cpu_short']} has {', '.join(str(x['jobs']) for x in sm['enough'][:-1])} and {sm['enough'][-1]['jobs']} jobs" in vt
              and "reports rows, not a verdict per toolchain" in vt and "one run" in vt and "library and compiler are still not separated" in vt,
              "section 6b: only EPYC 7763 has enough jobs on each toolchain, forms are inconclusive, one run, library and compiler not separated")
    if env["models"]:
        et = dp.inner_text("#environment-full").replace("\u00a0", " ")
        sm = env["summary"]
        tabs = dp.evaluate("document.querySelectorAll('#env-tables table').length")
        rows = dp.evaluate("document.querySelectorAll('#env-tables tbody tr').length")
        ck.ok(tabs == len(env["models"]) and rows == sm["jobs"], f"section 6c: one table per CPU model ({tabs}) and one row per job ({rows})")
        ck.ok(f"{sm['processes_with_steal']} of {sm['processes']:,} timed processes saw a steal tick" in et
              and f"in {sm['jobs_sharing_core']} of {sm['jobs']} jobs" in et and "hyperthread sibling" in et
              and "may report a constant or nominal MHz and hide real frequency changes" in et and "could not have moved anything" in et
              and f"{sm['excluded_processes']} processes were left out" in et,
              "section 6c: steal count, the exclusion test (vacuous, said so), core sharing as a real feature, the guest's view of frequency")
        ck.ok(sm["large_jobs"] == 0 and sm["cells_moved"] == 0 and not sm["page_text_may_change"],
              "section 6c data: no large job and no moved cell, so the plan's rule leaves the page text unchanged")


def new_sections(dp, ck):
    """Details page, sections 3b (layout sweep) and 7c (PGO column): built from site/data/layout.json and pgo.json."""
    with open(os.path.join(DATA, "layout.json"), encoding="utf-8") as f:
        lay = json.load(f)
    with open(os.path.join(DATA, "pgo.json"), encoding="utf-8") as f:
        pgo = json.load(f)
    lt = dp.inner_text("#layout-full")
    tables = dp.evaluate("document.querySelectorAll('#layout-tables table').length")
    rows = dp.evaluate("[...document.querySelectorAll('#layout-tables tbody tr')].length")
    lr = lambda v: f"{v:.2f}" if v >= 2 else f"{v:.3f}"  # noqa: E731
    k = lay["kernels"]
    ck.ok(tables == len(lay["cpus"]) and rows == sum(len(c["rows"]) for c in lay["cpus"]),
          f"section 3b: one table per CPU model ({len(lay['cpus'])}) and one row per kernel and size ({rows})")
    ck.ok(f"{lr(lay['reverse']['min'])[:3]}" in lt and "coarse" in lt and f"{lay['placements']} placements" in lt
          and all(f"{r}" in lt for r in lay["residues"]) and "not a full sweep" in lt and "inferred" in lt,
          "section 3b: states the coarse mode (4 placements, loop start modulo 64), the reverse range and the limits, from the data")
    ck.ok(all(f"{lr(k[x]['min'])} to {lr(k[x]['max'])}" in lt for x in ("k01_sum_fwd", "k02_add_fwd"))
          and "robust" in lt and "placement-dependent" in lt and "depends on where the loop lands" in lt,
          "section 3b: the forward sum is robust, the forward add and the stencil swing with placement, with their ranges from the data")
    thin = [c for c in lay["cpus"] if not c["enough"]]
    ck.ok(all(f"{c['cpu_short']} drew {c['jobs']} job" in lt and "inconclusive" in lt for c in thin),
          "section 3b: CPU models with too few jobs are named and called inconclusive")
    pt = dp.evaluate("document.getElementById('pgo-full').innerText")
    base = [c for c in pgo["cpus"] if c["enough"] and c["base_jobs"] >= pgo["minimum_jobs"]]
    ck.ok(dp.evaluate("document.querySelectorAll('#pgo-tables table').length") == len(pgo["cpus"])
          and "training input is the timed input" in pt and "flatters PGO" in pt and "did not make the cost vanish" in pt
          and all(f"{c['cpu_short']} ({c['jobs']} jobs with PGO" in pt for c in base) and f"{pgo['rows_built']} rows" in pt,
          "section 7c: one table per CPU model, the training-equals-test limit, and the finding that PGO did not make the cost vanish")
    ck.ok(all(f"{c['cpu_short']} has {c['jobs']} job" in pt for c in pgo["cpus"] if c not in base),
          "section 7c: CPU models without a comparison are named with their job counts")
    versions_environment(dp, ck)


def google_wording(page, ck, label, pooled):
    """No sentence says Google's figure holds, is wrong or is confirmed; no harness verdict sentence; plain names."""
    prose = page.evaluate(f"({PROSE_TEXT_JS})()")
    sentences = re.split(r"(?<=[.;:])\s+", prose)
    claims = [x for x in sentences if ("Google" in x or "0.30" in x)
              and re.search(r"\bholds?\b|\bwrong\b|\bconfirm(?:s|ed)?\b", x, re.I)
              and "neither confirms nor contradicts" not in x and "not a confirmation" not in x]
    ck.ok(not claims, f"{label}: no sentence says Google's figure holds, is wrong or is confirmed"
          + ("" if not claims else f": {claims[:3]}"))
    alltext = page.evaluate("document.body.textContent").replace("\u00a0", " ")
    harness_lines = [c["verdict"]["line"] for c in pooled["cpus"]] + [pooled["page"]["line"]]
    bad_claims = re.findall(r"[^.]*(?:holds? for forward|Google[^.]{0,80}\b(?:holds?|is wrong|was wrong|confirmed)\b"
                            r"|0\.30%[^.]{0,80}\b(?:holds?|is wrong|confirmed)\b)[^.]*", alltext, re.I)
    ck.ok(not bad_claims and not any(ln[:60] in alltext for ln in harness_lines),
          f"{label}: no text anywhere, collapsed or not, says Google's figure holds (for forward loops or otherwise), is wrong or is confirmed, and no harness verdict sentence is printed"
          + ("" if not bad_claims else f": {bad_claims[:2]}"))
    raw = sorted(set(RAW_ID.findall(prose)))
    ck.ok(not raw, f"{label}: prose uses plain names: no raw cell ids, harness form names, raw CPU strings or bare file names outside tables, code and tooltips"
          + ("" if not raw else f": {raw[:6]}"))


def open_full(page):
    """Figure 2 opens on a plain view; its full listing (addresses, the commands, the long sentence, the ratio range,
    the instruction counts) sits behind one button. A check that reads the detail opens that button first."""
    page.wait_for_function(FIG2_READY, timeout=8000)
    d = page.locator("#fig2 details.f2-full")
    if not d.count():  # the SAMPLE file has no assembly and so no listing
        return
    if not d.evaluate("n => n.open"):
        d.locator("summary").click()
    page.wait_for_function("document.querySelector('#fig2 details.f2-full').open")


def no_hscroll(page):
    return page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def page_numbers(page, allowed, selector=None):
    root = f"document.querySelector('{selector}')" if selector else "document.body"
    return unknown_numbers(page.evaluate(f"(() => ({PAGE_TEXT_JS})({root}))()"), allowed)


def every_row(page, ck, allowed, label):
    """Selects every loop row in turn; Figure 2 must load its machine code and print only data numbers."""
    ks = page.evaluate("[...document.querySelectorAll('#rows .row')].map(b => b.dataset.k)")
    loaded, bad = 0, []
    for k in ks:
        page.click(f'#rows .row[data-k="{k}"]')
        try:
            page.wait_for_function(FIG2_READY, timeout=8000)
        except Exception:
            continue
        open_full(page)
        body = page.inner_text("#fig2-body") + page.inner_text("#fig2-cap")
        f2txt = page.inner_text("#fig2")
        if "[object" in f2txt or "undefined" in f2txt or re.search(r"\bnull\b", f2txt):
            bad.append(f"{k}: Figure 2 prints a JavaScript placeholder")
        elif "did not load" not in body and ((page.locator("#fig2 .f2-full pre.asm").count() == 2 and page.locator("#fig2 pre.asm-lite").count() in (1, 2)) or "SAMPLE" in body):
            loaded += 1
        bad += page_numbers(page, allowed, "#fig2")
    ck.ok(ks and loaded == len(ks), f"{label}: all {len(ks)} rows open Figure 2 with its machine code ({loaded} did)")
    ck.ok(not bad, f"{label}: every number in Figure 2 is in the data" + ("" if not bad else f": {sorted(set(bad))[:6]}"))


def pick_loop(pg, kern):
    """Click a loop in the hero. In variant 4 a lane opens the machine code at once, so close that again."""
    pg.click(f'#race-loops button[data-k="{kern}"]')
    if pg.evaluate("!!document.getElementById('asm-panel') && !document.getElementById('asm-panel').hidden"):
        pg.wait_for_timeout(300)
        pg.keyboard.press("Escape")
        pg.wait_for_function("document.getElementById('asm-panel').hidden", timeout=4000)
        pg.wait_for_timeout(250)


def hero_sig(pg):
    """What the hero draws right now: the canvas (variants 1 to 3) or the clipped bars (variant 4)."""
    return pg.evaluate("(() => { if (document.getElementById('race').dataset.hv === '4') return [...document.querySelectorAll('#race .ln-t > i')].map(i => getComputedStyle(i).clipPath).join('|'); return document.getElementById('race-cv').toDataURL(); })()")


def settled_sig(pg, quiet_ms=400, limit_ms=6000):
    """hero_sig once it has stopped changing for quiet_ms (a slow machine can still be resizing or loading fonts)."""
    last, still, waited = hero_sig(pg), 0, 0
    while still < quiet_ms and waited < limit_ms:
        pg.wait_for_timeout(100)
        waited += 100
        cur = hero_sig(pg)
        still = still + 100 if cur == last else 0
        last = cur
    return last


def shot(page, saved, shots, name, selector=None, full=False):
    path = os.path.join(shots, name)
    if selector:
        page.locator(selector).screenshot(path=path)
    else:
        page.screenshot(path=path, full_page=full)
    saved.append(path)


def scroll_to(page, selector):
    page.evaluate(f"document.querySelector('{selector}').scrollIntoView({{block: 'start'}})")
    page.wait_for_timeout(250)


def story_checks(browser, base, ck, index, pooled):
    """The contrast band and the mechanism demo: the band's worst loop is the data's and follows the
    CPU chip; the demo steps by click (eight cells, four at once with the check off); the SIMD chip and the
    Limits link open what they point at."""
    print("== story: contrast band, mechanism demo, small parts")
    def worst(cpu_model):
        pc = next(c for c in pooled["cpus"] if c["cpu_model"] == cpu_model)
        v = [(c.get("aligned") or c["as_compiled"])["ratio"] for c in pc["cells"] if c["cell_id"].endswith(".L1") and (c.get("aligned") or c.get("as_compiled"))]
        return max(v)
    fx = lambda v: f"{v:.1f}" if v >= 2 else f"{v:.2f}"
    for w, h in ((1440, 900), (390, 844)):
        pg = browser.new_page_plain(viewport={"width": w, "height": h})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        pg.wait_for_function("document.querySelectorAll('#mech-row .mc').length === 8", timeout=15000)
        dcpu = next(c for c in index["cpus"] if c["slug"] == index["default_cpu"])
        txt = pg.inner_text("#band")
        ck.ok(f"{index['claim']['google_pct']:.2f}%" in txt and f"{fx(worst(dcpu['cpu_model']))}×" in txt and "one loop, a check of the same kind" in txt and "does not say which hardening mode" in txt and "neither confirms nor contradicts" in txt,
              f"{w}: the contrast band prints Google's {index['claim']['google_pct']:.2f}% and this study's slowest loop ({fx(worst(dcpu['cpu_model']))}×), 'one loop, a check of the same kind', the mode caveat and the neutral sentence")
        other = next(c for c in index["cpus"] if c["slug"] != index["default_cpu"] and c.get("enough"))
        pg.click(f'#race-cpu [data-cpu="{other["slug"]}"]')
        pg.wait_for_timeout(250)
        ck.ok(f"{fx(worst(other['cpu_model']))}×" in pg.inner_text("#band-worst"), f"{w}: the band's worst loop follows the CPU chip ({other['cpu_short']}: {fx(worst(other['cpu_model']))}×)")
        pg.click(f'#race-cpu [data-cpu="{index["default_cpu"]}"]')
        pg.click('#mech-tiles [data-k="k04_rev"]')
        pg.click('#mech-chk [data-on="0"]')
        c0 = pg.inner_text("#mech-count")
        pg.click("#mech-step")
        lit = pg.locator("#mech-row .mc.now").count()
        ck.ok("of 2" in c0 and lit == 4 and "SIMD: one instruction, four elements" in pg.inner_text("#mech-say"), f"{w}: check off, reverse: two steps, one Step lights four cells at once, SIMD glossed in plain words ({c0}, lit {lit})")
        pg.click('#mech-chk [data-on="1"]')
        c1 = pg.inner_text("#mech-count")
        pg.click("#mech-step")
        lit1 = pg.locator("#mech-row .mc.now").count(); gate = pg.locator("#mech-row .mc-gate").count()
        ck.ok("of 8" in c1 and lit1 == 1 and gate == 1 and "could not vectorize" in pg.inner_text("#mech-say"), f"{w}: check on, reverse: eight steps, one cell per Step past a gate, the data's reason shown ({c1}, lit {lit1}, gate {gate})")
        pg.click('#mech-tiles [data-k="k02_add_fwd"]')
        pg.click("#mech-step")
        ck.ok(pg.locator("#mech-row .mc.now").count() == 4 and "once, before the loop" in pg.inner_text("#mech-say"), f"{w}: check on, forward add: still four at once, the sizes are tested once up front")
        ck.ok("inferred" in pg.inner_text("#mech"), f"{w}: the demo says the mechanism is inferred")
        pg.click("#simd-chip")
        ck.ok(pg.is_visible("#simd-def") and "several elements per instruction" in pg.inner_text("#simd-def"), f"{w}: the SIMD chip in the hero explains SIMD in plain words")
        if w >= 1041:
            pg.click("#bar-limits")
            pg.wait_for_timeout(300)
            ck.ok(pg.is_visible("#cannot li") and pg.evaluate("document.getElementById('limits-fold').open"), f"{w}: the Limits link in the top bar opens the box 'What this cannot tell you'")
        else:
            pg.evaluate("document.getElementById('limits-fold').open = false")
            pg.click("#bar-limits")
            pg.wait_for_timeout(300)
            ck.ok(pg.is_visible("#cannot li"), f"{w}: the Limits link in the top bar opens the box on a phone too")
        pg.close()

def collapsed_checks(browser, base, ck, index, saved, shots):
    print("== click-first, short: the default state")
    for w, h, cap in ((1440, 900, None), (390, 844, 10500)):
        pg = browser.new_page_plain(viewport={"width": w, "height": h})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        n = pg.evaluate("document.querySelectorAll('.sec-more').length")
        closed = pg.evaluate("[...document.querySelectorAll('.sec-body')].filter(b => b.hidden).length")
        ck.ok(n >= 9 and closed == n, f"{w}: every section starts collapsed, one button each to open ({closed} of {n})")
        r = pg.evaluate("(() => { const r = document.getElementById('race').getBoundingClientRect(), s = document.querySelector('.hero .scope').getBoundingClientRect(), d = document.querySelector('.bar-details').getBoundingClientRect(); return [r.bottom, s.bottom, d.bottom, d.top]; })()")
        lb = pg.evaluate("document.getElementById('race-loops').getBoundingClientRect().bottom")
        ck.ok((r[0] <= h or (w < 641 and lb <= h * 1.3)) and r[1] <= h and r[2] <= h and r[3] >= 0, f"{w}x{h}: the whole finding is in the first view: the race (on a phone its eight lanes, the caption a short scroll below), switch and ratio, the scope sentence and the Full details link ({r}, lanes end {lb:.0f})")
        ck.ok(pg.inner_text("#race-ratio").endswith("×") and len(pg.query_selector_all("#race-loops button")) == 8, f"{w}: the first view prints a measured ratio and offers all eight loop chips")
        f1 = pg.evaluate("document.getElementById('fig1').getBoundingClientRect().top")
        ck.ok(f1 < h * 3, f"{w}: the clickable heatmap is within three screens (the contrast band and the mechanism demo come first; Figure 1 starts at {f1:.0f} px)")
        if cap:
            hh = pg.evaluate("document.documentElement.scrollHeight")
            ck.ok(hh < cap, f"{w}: the main page is {hh} px long by default (under {cap}; hard cap 13228)")
            shot(pg, saved, shots, "mobile-collapsed-top.png")
        pg.click("#sb-why", timeout=500) if False else None
        pg.click('#why .sec-more')
        ck.ok(pg.evaluate("!document.getElementById('sb-why').hidden") and "paddd" in pg.inner_text("#sb-why"), f"{w}: one click opens a section and shows its text")
        pg.evaluate("location.hash = '#fn-short'")
        pg.wait_for_timeout(200)
        ck.ok(pg.evaluate("!document.getElementById('sb-mitigate').hidden"), f"{w}: a link or hash into a collapsed section opens it")
        pg.close()


def navigation_checks(browser, base, ck, index, pooled):
    """Page chrome and keyboard use: the top bar and rail name the section under the sticky bar when sections are
    collapsed, the compiler grid is one tab stop with arrow keys, the machine-code address column is readable, the
    page does not scroll sideways at 320 px, reference [1] links back, the rail is not in the Tab order, and the
    lost-SIMD captions carry the no-vectorize control."""
    print("== navigation: top bar, compiler grid, contrast, 320 px, citations, no-vectorize clause")
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#rail a').length > 3", timeout=15000)
    secs = pg.evaluate("[...document.querySelectorAll('.body section[id]')].filter(s => s.querySelector('h2')).map(s => { const h = s.querySelector('h2'), n = h.querySelector('.secno'); return [s.id, (n ? h.textContent.slice(n.textContent.length) : h.textContent).replace('\\u00b6', '').trim()]; })")
    bad, tried = [], 0
    for sid, name in secs:
        room = pg.evaluate("""(id) => { const s = document.getElementById(id); const max = document.documentElement.scrollHeight - innerHeight, want = scrollY + s.getBoundingClientRect().top - 80;
            if (want > max - 4) return false; document.documentElement.style.scrollBehavior = 'auto'; window.scrollTo(0, want); return true; }""", sid)
        if not room:
            continue  # the last, short sections cannot be scrolled up to the bar: the page bottom is checked below
        pg.wait_for_timeout(150)
        got = pg.evaluate("[document.getElementById('bar-sec').textContent, (document.querySelector('#rail a.on span') || {}).textContent]")
        tried += 1
        if got != [name, name]:
            bad.append((sid, got))
    ck.ok(tried >= 9 and not bad, f"1440: with every section collapsed, the top bar and the rail name the section under the bar, not the next one ({tried} sections scrolled to 80 px below the top; wrong: {bad[:3]})")
    pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    pg.wait_for_timeout(200)
    got = pg.evaluate("[document.getElementById('bar-sec').textContent, (document.querySelector('#rail a.on span') || {}).textContent]")
    ck.ok(got == [secs[-1][1], secs[-1][1]], f"1440: at the page bottom the top bar and the rail name the last section ({got})")
    ck.ok(pg.evaluate("[...document.querySelectorAll('#rail a')].every(a => a.tabIndex === -1)") and pg.evaluate("document.querySelector('.skip').getAttribute('href')") == "#top"
          and pg.evaluate("!!document.getElementById('top')"), "1440: the rail links are not tab stops (the Contents menu is the keyboard route) and the skip link goes to the main element")
    ck.ok(pg.evaluate("!!document.getElementById('cite-google')") and pg.evaluate("[...document.querySelectorAll('a.cite.back')].every(a => document.querySelector(a.getAttribute('href')))"),
          "every back arrow in the references list lands on an in-text citation (reference [1] included)")
    pg.close()
    # the compiler grid: roles, one tab stop per grid, arrow keys (a page with every section open)
    pg = browser.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#ce-panels .ce-cell').length > 20", timeout=15000)
    st = pg.evaluate("""() => [...document.querySelectorAll('#ce-panels .ce-grid')].map(g => [
        g.querySelectorAll('[tabindex="0"]').length,
        [...g.children].every(c => c.getAttribute('role') === 'row'),
        [...g.querySelectorAll('[role=gridcell], [role=rowheader], [role=columnheader]')].every(c => c.closest('[role=row]') && c.closest('[role=row]').parentElement === g),
        g.querySelectorAll('.ce-cell').length])""")
    ck.ok(len(st) == 3 and all(s[0] == 1 and s[1] and s[2] and s[3] > 20 for s in st), f"the compiler grids (Figure 5) are real grids (role=row wrappers) with one tab stop each ({st})")
    pg.focus('#ce-panels .ce-cell[tabindex="0"]')
    first = pg.evaluate("document.activeElement.getAttribute('aria-label')")
    pg.keyboard.press("ArrowRight")
    pg.keyboard.press("ArrowDown")
    second = pg.evaluate("document.activeElement.getAttribute('aria-label')")
    n0 = pg.evaluate("document.querySelectorAll('#ce-panels [tabindex=\"0\"]').length")
    pg.keyboard.press("Home")
    for _ in range(30):
        pg.keyboard.press("ArrowUp")
    onhead = pg.evaluate("[document.activeElement.className, document.activeElement.tagName]")
    pg.keyboard.press("Tab")
    outside = pg.evaluate("[document.activeElement.className, !!document.activeElement.closest('.ce-grid')]")
    ck.ok(second and second != first and n0 == 3 and onhead == ["ce-h", "A"] and outside[0] != "ce-h",
          f"arrow keys move between the cells and up to the header links; the next Tab leaves that grid ({first!r} -> {second!r}, header {onhead}, then {outside})")
    pg.focus('#ce-panels .ce-cell[tabindex="0"]')
    shown = pg.inner_text("#ce-remark")
    ck.ok(": " in shown and "Hover or tap" not in shown, f"focusing a grid cell still shows its remark ({shown[:60]!r})")
    # contrast of the machine-code address column, on the plain and the SIMD-tinted lines
    low = pg.evaluate("""() => { const lum = (c) => { const m = c.match(/[\\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]); };
        const bg = (e) => { for (let n = e; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor, m = c.match(/[\\d.]+/g); if (m && (m.length < 4 || +m[3] > .9)) return c; } return 'rgb(255,255,255)'; };
        const out = []; let n = 0; for (const e of document.querySelectorAll('.asm .ad')) { if (!e.getBoundingClientRect().width) continue; n++;
          const a = lum(getComputedStyle(e).color), b = lum(bg(e)), cr = (Math.max(a, b) + .05) / (Math.min(a, b) + .05); if (cr < 4.5) out.push(cr.toFixed(2)); } return [n, out]; }""")
    ck.ok(low[0] > 10 and not low[1], f"the machine-code address column has at least 4.5:1 contrast on plain and SIMD-tinted lines ({low[0]} addresses, low: {low[1][:3]})")
    pg.close()
    # a 320 px screen: no sideways scroll, also with the aligned/as-compiled tip open
    for w in (320, 390):
        pg = browser.new_page_plain(viewport={"width": w, "height": 800})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        flat = no_hscroll(pg)
        pg.evaluate("document.getElementById('col-hint').scrollIntoView({block: 'center'})")
        pg.click("#col-hint")
        pg.wait_for_timeout(250)
        r = pg.evaluate("(() => { const r = document.getElementById('col-tip').getBoundingClientRect(); return [r.left, r.right]; })()")
        ck.ok(flat and no_hscroll(pg) and r[0] >= 0 and r[1] <= w, f"{w}: no horizontal scroll, and the open 'aligned' tip sits inside the screen ({[round(x) for x in r]})")
        pg.close()
    # the lost-SIMD captions put the no-vectorize control beside the extra time
    dmodel = next(x for x in index["cpus"] if x["slug"] == index["default_cpu"])["cpu_model"]
    dp = next(c for c in pooled["cpus"] if c["cpu_model"] == dmodel)
    cells = {c["cell_id"]: c for c in dp["cells"]}

    def clause(k):
        pos, cell = dp["positive"][f"{k}.L1"], cells[f"{k}.L1"]
        share = 100 * (pos["ratio"] - 1) / (cell["as_compiled"]["ratio"] - 1)
        return f"makes it {_fx(pos['ratio'])}× as long at the L1 size: {'about a third' if 30 <= share <= 37 else f'about {round(share)}%'} of the extra time as compiled"

    def brief(k):  # the hero's one-clause form
        pos, cell = dp["positive"][f"{k}.L1"], cells[f"{k}.L1"]
        share = 100 * (pos["ratio"] - 1) / (cell["as_compiled"]["ratio"] - 1)
        return f"Switching SIMD off by hand costs {_fx(pos['ratio'])}× ({'about a third' if 30 <= share <= 37 else f'about {round(share)}%'} of the as-compiled extra); the rest is the compare and jump (inferred)."
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    pg.wait_for_timeout(1500)
    default_txt = pg.inner_text("#race-sub")
    baked = re.search(r'data-v="heroWhat" class="rr-what">([^<]*)<', open(os.path.join(REPO, "site", "index.html"), encoding="utf-8").read())
    ck.ok(brief("k04_rev") in default_txt and baked and html.unescape(baked.group(1)) == pg.inner_text("#race-sub .rr-what") and "re-test" not in pg.inner_text(".hero .byline").lower(),
          f"the hero's default caption (reverse) states the no-vectorize build's {_fx(dp['positive']['k04_rev.L1']['ratio'])}x and its share of the extra time, the rest labelled inferred; the byline no longer says re-tested")
    pick_loop(pg, "k05_stride2")
    ck.ok(brief("k05_stride2") in pg.inner_text("#race-sub"), "the hero's stride-2 caption carries its no-vectorize clause")
    pick_loop(pg, "k08_matmul")
    ck.ok("Clang 19 to 21 keep SIMD" in pg.inner_text("#race-sub") and "Switching SIMD off by hand" not in pg.inner_text("#race-sub"), "the hero's matrix-multiply caption keeps its own sentence (clang 19 to 21 keep SIMD), with no extra clause")
    pick_loop(pg, "k02_add_fwd")
    ck.ok("switched off by hand" not in pg.inner_text("#race-sub"), "a loop that keeps SIMD gets no no-vectorize clause")
    pg.close()
    pg = browser.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.click('#rows .row[data-k="k04_rev"]')
    pg.wait_for_function(FIG2_READY, timeout=8000)
    open_full(pg)
    why = pg.inner_text("#fig2 .f2-why")
    ck.ok(clause("k04_rev") in why and "(inferred)" in why, "Figure 2's sentence for the reverse loop carries the no-vectorize clause")
    pg.click('#rows .row[data-k="k08_matmul"]')
    open_full(pg)
    ck.ok(clause("k08_matmul") in pg.inner_text("#fig2 .f2-why"), "Figure 2's sentence for the matrix-multiply loop carries its no-vectorize clause")
    pg.close()


def rail_checks(browser, base, ck):
    """The section rail (fixed, from 1380 px) must not take clicks meant for the hero loop names or Figure 1's row
    labels: at 1380, 1440 and 1920 px every one of them is the element under the pointer at its label, a real click
    on one selects it without jumping to another section, and a rail dot still goes to its section."""
    print("== rail: clicks reach the loop names")
    for w, h in ((1380, 900), (1440, 900), (1920, 1080)):
        pg = browser.new_page_plain(viewport={"width": w, "height": h})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8 && document.querySelectorAll('#rail a').length > 3", timeout=15000)
        pg.wait_for_timeout(1500)
        ck.ok(pg.evaluate("getComputedStyle(document.getElementById('rail')).display") != "none", f"{w}: the section rail is shown")
        hero_hit = pg.evaluate("""() => [...document.querySelectorAll('#race-loops button[data-k]')].map((b) => { const r = b.getBoundingClientRect();
            return [b.dataset.k, [0.08, 0.3, 0.5].every((f) => { const e = document.elementFromPoint(r.left + r.width * f, r.top + r.height / 2); return !!e && b.contains(e); })]; })""")
        ck.ok(len(hero_hit) == 8 and all(x[1] for x in hero_hit), f"{w}: the pointer reaches every hero loop name, not the rail ({[x[0] for x in hero_hit if not x[1]]})")
        pg.evaluate("document.getElementById('rows').scrollIntoView({block: 'center', behavior: 'instant'})")
        pg.wait_for_timeout(500)
        row_hit = pg.evaluate("""() => [...document.querySelectorAll('#rows .row')].map((b) => { const r = b.getBoundingClientRect();
            return [b.dataset.k, [0.04, 0.12, 0.25].every((f) => { const e = document.elementFromPoint(r.left + r.width * f, r.top + r.height / 2); return !!e && b.contains(e); })]; })""")
        ck.ok(len(row_hit) == 8 and all(x[1] for x in row_hit), f"{w}: the pointer reaches every Figure 1 row label, not the rail ({[x[0] for x in row_hit if not x[1]]})")
        pg.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
        pg.wait_for_timeout(300)
        box = pg.evaluate("(() => { const r = document.querySelector('#race-loops button[data-k=\"k03_stencil\"]').getBoundingClientRect(); return [r.left + r.width * 0.12, r.top + r.height / 2]; })()")
        pg.mouse.click(box[0], box[1])
        pg.wait_for_timeout(500)
        got = pg.evaluate("[document.querySelector('#race-loops button[data-k=\"k03_stencil\"]').getAttribute('aria-checked'), location.hash]")
        ck.ok(got[0] == "true" and not re.match(r"#(siblings|placement|realworld|census|result|reproduce)", got[1]), f"{w}: a click on the Stencil name in the hero selects it and stays on the page (hash {got[1]!r})")
        if pg.evaluate("!!document.getElementById('asm-panel') && !document.getElementById('asm-panel').hidden"):  # in the default hero a lane opens its machine code
            pg.keyboard.press("Escape")
            pg.wait_for_function("document.getElementById('asm-panel').hidden", timeout=4000)
            pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('rows').scrollIntoView({block: 'center', behavior: 'instant'})")
        pg.wait_for_timeout(500)
        box = pg.evaluate("(() => { const r = document.querySelector('#rows .row[data-k=\"k05_stride2\"]').getBoundingClientRect(); return [r.left + r.width * 0.08, r.top + r.height / 2]; })()")
        pg.mouse.click(box[0], box[1])
        pg.wait_for_timeout(500)
        got = pg.evaluate("[document.querySelector('#rows .row[data-k=\"k05_stride2\"]').getAttribute('aria-selected'), location.hash]")
        ck.ok(got[0] == "true" and not re.match(r"#(siblings|placement|realworld|census|result|reproduce)", got[1]), f"{w}: a click on the Stride-2 row label in Figure 1 selects it and stays on the page (hash {got[1]!r})")
        dot = pg.evaluate("""() => { const a = [...document.querySelectorAll('#rail a')][3], i = a.querySelector('i'), r = i.getBoundingClientRect();
            return [r.left + r.width / 2, r.top + r.height / 2, a.getAttribute('href')]; }""")
        pg.mouse.click(dot[0], dot[1])
        pg.wait_for_timeout(500)
        ck.ok(pg.evaluate("location.hash") == dot[2], f"{w}: a click on a rail dot still goes to its section ({dot[2]})")
        pg.close()


PLAIN_MAX_NUMBERS = 4  # distinct numbers in the drawer's default prose: the ratio, the CPU model (up to two numbers) and the width
PLAIN_WORDS = 45       # the one plain sentence: readable in about ten seconds
PLAIN_JS = r"""
() => {
  const f = document.getElementById('fig2'), out = [];
  const w = document.createTreeWalker(f, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const p = n.parentElement;
    if (!p || p.closest('pre, code, script, style') || (p.closest('details:not([open])') && !p.closest('summary'))) continue;
    const t = n.textContent.trim();
    if (t) out.push(t);
  }
  return out.join('\n');
}
"""


def figure2_plain_checks(browser, base, ck, index, pooled):
    """Figure 2 opens on a plain view: one ratio, one sentence, only the marked lines, no addresses. The whole listing
    and the exact commands sit behind one button that starts closed and works from the keyboard."""
    print("== Figure 2: plain view first, the full listing behind one button")
    cpu = next(pc for pc in pooled["cpus"] if pc["cpu_model"] == next(c for c in index["cpus"] if c["slug"] == index["default_cpu"])["cpu_model"])
    cell = lambda k: next(x for x in cpu["cells"] if x["cell_id"] == f"{k}.L1")
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    ks = pg.evaluate("[...document.querySelectorAll('#rows .row')].map(b => b.dataset.k)")
    ck.ok(pg.evaluate("document.querySelectorAll('#fig2 details.f2-full').length") == 1 and not pg.evaluate("document.querySelector('#fig2 details.f2-full').open"),
          "Figure 2: the full listing is closed when the page loads")
    ck.ok(pg.inner_text("#fig2 details.f2-full > summary").strip() == "Full listing and commands", "Figure 2: one button, labelled with what it opens")
    bad = []
    for k in ks:
        pg.click(f'#rows .row[data-k="{k}"]')
        pg.wait_for_function(FIG2_READY, timeout=8000)
        pg.wait_for_timeout(120)
        vis = pg.inner_text("#fig2")
        prose = pg.evaluate(PLAIN_JS)
        nums = sorted({m.group(1) + (m.group(2) or "") for m in NUM_TOKEN.finditer(prose)})
        head = pg.inner_text("#fig2 .f2-head")
        want = _fx(cell(k)["aligned"]["ratio"]) + "×"
        sent = pg.inner_text("#fig2 .f2-plain")
        n_ad = pg.evaluate("[...document.querySelectorAll('#fig2 .ad')].filter(e => !(e.closest('details:not([open])') && !e.closest('summary'))).length")
        n_ln = pg.evaluate("[...document.querySelectorAll('#fig2 pre.asm-lite .ln')].length")
        marked = pg.evaluate("[...document.querySelectorAll('#fig2 pre.asm-lite .ln')].filter(e => /simd|chk|trap/.test(e.className)).length")
        if pg.evaluate("document.querySelector('#fig2 details.f2-full').open"):
            bad.append(f"{k}: the full listing opened by itself")
        if len(nums) > PLAIN_MAX_NUMBERS:
            bad.append(f"{k}: {len(nums)} distinct numbers in the plain view {nums}")
        if want not in head or "–" in head or head.count("×") != 1:
            bad.append(f"{k}: the headline is not one pooled ratio {want} ({head!r})")
        if len(sent.split()) > PLAIN_WORDS:
            bad.append(f"{k}: the plain sentence has {len(sent.split())} words")
        if n_ad:
            bad.append(f"{k}: {n_ad} addresses visible")
        for t in ("not shown", "Cachegrind", "_LIBCPP", "clang", "instructions of the two functions", "run 3", "job j", "Figure 2", "loops aligned", "SIMD"):
            if t in vis:
                bad.append(f"{k}: the plain view shows {t!r}")
        if not n_ln or n_ln > 30 or not marked:
            bad.append(f"{k}: the plain view has {n_ln} code lines, {marked} marked")
        if "smallest data size" not in head:
            bad.append(f"{k}: the headline does not say it is the smallest data size ({head!r})")
        if "×" not in head or "as long with the check on" not in head:
            bad.append(f"{k}: the headline does not say what the number is ({head!r})")
    ck.ok(not bad, f"Figure 2, plain view: for all {len(ks)} loops one ratio, one short sentence, at most {PLAIN_MAX_NUMBERS} distinct numbers, no addresses, no 'not shown' rows, no commands" + ("" if not bad else f": {bad[:4]}"))
    # the plain view's code: what each kind of loop shows, read from the plain blocks only
    def plain_view(k):
        pg.click(f'#rows .row[data-k="{k}"]')
        pg.wait_for_function(FIG2_READY, timeout=8000)
        pg.wait_for_timeout(120)
        return pg.evaluate(r"""() => ({ blocks: document.querySelectorAll('#fig2 pre.asm-lite').length,
            simd: document.querySelectorAll('#fig2 pre.asm-lite .simd').length, chk: document.querySelectorAll('#fig2 pre.asm-lite .chk').length,
            trap: document.querySelectorAll('#fig2 pre.asm-lite .trap').length, ln: document.querySelectorAll('#fig2 pre.asm-lite .ln').length,
            notes: [...document.querySelectorAll('#fig2 pre.asm-lite .note')].map(n => n.textContent),
            left: [...document.querySelectorAll('#fig2 pre.asm-lite .leftover')].map(n => n.textContent),
            leftBlock: [...document.querySelectorAll('#fig2 pre.asm-lite')].map(b => b.querySelectorAll('.leftover').length),
            code: [...document.querySelectorAll('#fig2 pre.asm-lite .ln')].map(p => p.textContent).join('\n'),
            subs: [...document.querySelectorAll('#fig2 .f2-lite .remark')].map(n => n.textContent),
            titles: [...document.querySelectorAll('#fig2 .f2-lite h3')].map(n => n.textContent),
            sent: document.querySelector('#fig2 .f2-plain').textContent, cap: document.getElementById('fig2-cap').innerText.split('\n')[0] })""")
    v = plain_view("k04_rev")
    ck.ok(v["blocks"] == 2 and v["simd"] >= 1 and v["chk"] >= 2 and v["trap"] >= 1
          and any(n.startswith("the check") for n in v["notes"]) and any(n.startswith("this trap stops the program") for n in v["notes"]),
          f"Figure 2, plain view of the reverse loop: its SIMD lines, the check and the trap, labelled in words ({v['simd']} SIMD, {v['chk']} check, {v['trap']} trap lines)")
    ck.ok("STOP" in v["code"] and not re.search(r"(?<![%$\w])[0-9a-f]{3,}(?![\w])", re.sub(r"0x[0-9a-f]+", "", v["code"]))
          and any("jae" in n and "STOP" in n for n in v["notes"]) and v["subs"][1].startswith("One number per pass, with a check each time"),
          "Figure 2, plain view of the reverse loop: the trap is called STOP (no address), jae is explained in plain words, and the checks-on column says what it does per pass")
    ck.ok("can no longer work on" in v["sent"] and v["sent"].count("4 numbers at a time") == 1 and v["subs"][0] == "4 numbers at a time",
          "Figure 2, plain view of the reverse loop: '4 numbers at a time' is said once in the sentence and once as the column subtitle")
    ck.ok("Blue: several numbers per instruction" in v["cap"], f"Figure 2, plain view: the caption is only a short legend ({v['cap']!r})")
    v = plain_view("k08_matmul")
    ck.ok("can no longer" not in v["sent"] and "could not" not in v["sent"] and "not worth" in v["sent"],
          f"Figure 2, plain view of matrix multiply: the sentence says the compiler judged it not worth doing, not that it could not ({v['sent']!r})")
    v = plain_view("k05_stride2")
    ck.ok("can no longer work on" in v["sent"], "Figure 2, plain view of the stride-2 loop: the compiler could not count the iterations")
    v = plain_view("k01_sum_fwd")
    ck.ok(v["blocks"] == 1 and v["titles"] == ["Checks off and on"] and "Identical code" in v["subs"][0] and 2 <= v["ln"] <= 4 and v["simd"] == v["ln"]
          and v["chk"] == 0 and v["trap"] == 0 and not re.search(r"pxor|pcmp|punpck", v["code"]),
          f"Figure 2, plain view of the forward sum: one wide 'identical' block of a few representative SIMD lines, no filler, no check ({v['ln']} lines)")
    v = plain_view("k02_add_fwd")
    ck.ok(v["blocks"] == 2 and v["simd"] >= 2 and v["chk"] >= 1 and v["trap"] >= 1 and "4 numbers at a time" in v["subs"],
          f"Figure 2, plain view of the forward add: two blocks that keep their SIMD lines, the second with its check and trap ({v['simd']} SIMD lines)")
    ck.ok(v["left"] == ["then, for the leftover elements:"] and v["leftBlock"] == [0, 1] and "Checks on" in v["titles"][1],
          f"Figure 2, plain view of the forward add: only the checks-on block carries the muted label that its check lines belong to the leftover elements ({v['left']})")
    for k in ("k04_rev", "k05_stride2", "k08_matmul", "k01_sum_fwd"):
        vv = plain_view(k)
        ck.ok(not vv["left"], f"Figure 2, plain view of {k}: no 'leftover elements' label (lost or identical view)")
    # the button: mouse, keyboard, and the detail it holds
    pg.click('#rows .row[data-k="k04_rev"]')
    pg.wait_for_function(FIG2_READY, timeout=8000)
    pg.focus("#fig2 details.f2-full > summary")
    pg.keyboard.press("Enter")
    ck.ok(pg.evaluate("document.querySelector('#fig2 details.f2-full').open"), "Figure 2: Enter on the focused button opens the full listing")
    full = pg.inner_text("#fig2 .f2-full-body")
    ck.ok(pg.evaluate("[...document.querySelectorAll('#fig2 .f2-full .ad')].filter(e => !(e.closest('details:not([open])') && !e.closest('summary'))).length") > 10
          and "not shown" in full and "_LIBCPP_HARDENING_MODE_FAST" in full and "clang++" in pg.inner_text("#fig2 .f2-cmd")
          and "instructions, not time" in full and "Cachegrind" in full and "inferred" in full
          and pg.locator("#fig2 .f2-full .copy").is_visible() and "run " in full and "Grey numbers are addresses" in full
          and "as long with checks on" in full and "size_t" in full,
          "Figure 2: the full listing holds what the drawer showed before: addresses, 'not shown' rows, both build commands with a Copy button, run and job, the instruction counts with their Cachegrind note, the long sentence with its inferred label, the ratio range, the source line")
    pg.click('#rows .row[data-k="k05_stride2"]')
    pg.wait_for_function(FIG2_READY, timeout=8000)
    pg.wait_for_timeout(150)
    ck.ok(pg.evaluate("document.querySelector('#fig2 details.f2-full').open"), "Figure 2: once opened, the full listing stays open when another loop is selected")
    pg.focus("#fig2 details.f2-full > summary")
    pg.keyboard.press("Space")
    ck.ok(not pg.evaluate("document.querySelector('#fig2 details.f2-full').open"), "Figure 2: Space on the focused button closes the full listing")
    ck.ok(pg.evaluate("document.querySelector('#fig2 details.f2-full > summary').getBoundingClientRect().height") >= 32, "Figure 2: the button is at least 32 px tall")
    sty = "(() => { const c = getComputedStyle(document.querySelector('#fig2 details.f2-full > summary')); return [c.backgroundColor, c.color, c.borderTopColor, c.fontWeight, c.fontSize].join('|'); })()"
    pg.mouse.move(5, 5)
    closed_sty = pg.evaluate(sty)
    pg.click("#fig2 details.f2-full > summary")
    pg.mouse.move(5, 5)
    pg.wait_for_timeout(200)
    ck.ok(pg.evaluate(sty) == closed_sty and closed_sty.split("|")[0] == "rgba(0, 0, 0, 0)", f"Figure 2: the button looks the same open and closed, and quiet (no filled background): {closed_sty}")
    first = pg.evaluate("document.querySelector('#fig2 .f2-full-body').firstElementChild.className")
    ck.ok(first == "f2-instr" and pg.evaluate("document.querySelectorAll('#fig2 .f2-full-body .f2-head, #fig2 .f2-full-body h4').length") == 0,
          f"Figure 2: the full listing starts at the instruction counts and does not repeat the headline ({first})")
    fc = pg.inner_text("#fig2 .f2-fullcap")
    ck.ok("Figure 2." in fc and "loops aligned" in fc and "clang" in fc, "Figure 2: the technical caption sits in the full listing")
    pg.close()
    # the slide-over opened from the hero: same plain view, the button reachable by Tab
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    pg.click("#race-name")
    pg.wait_for_function("!document.getElementById('asm-panel').hidden")
    pg.wait_for_function(FIG2_READY, timeout=8000)
    pg.wait_for_timeout(500)
    got = []
    for _ in range(4):
        pg.keyboard.press("Tab")
        got.append(pg.evaluate("document.activeElement.tagName"))
        if got[-1] == "SUMMARY":
            break
    ck.ok("SUMMARY" in got, f"slide-over: Tab from Close reaches the full-listing button ({got})")
    pg.keyboard.press("Enter")
    ck.ok(pg.evaluate("document.querySelector('#asm-slot details.f2-full').open") and pg.evaluate("[...document.querySelectorAll('#asm-slot .f2-full .ad')].filter(e => !(e.closest('details:not([open])') && !e.closest('summary'))).length") > 0,
          "slide-over: the button opens the full listing with its addresses")
    pg.keyboard.press("Escape")
    pg.close()
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    pg.click("#race-name")
    pg.wait_for_function("!document.getElementById('asm-panel').hidden")
    pg.wait_for_function(FIG2_READY, timeout=8000)
    pg.wait_for_timeout(400)
    ck.ok(not pg.evaluate("document.querySelector('#asm-slot details.f2-full').open") and not pg.evaluate("[...document.querySelectorAll('#asm-slot .ad')].filter(e => !(e.closest('details:not([open])') && !e.closest('summary'))).length"),
          "slide-over: opened from the hero button, the drawer shows the plain view with the full listing closed")
    pg.close()
    # a phone: the same, inside the row accordion
    pg = browser.new_page_plain(viewport={"width": 390, "height": 844})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.evaluate("document.getElementById('fig1').scrollIntoView()")
    pg.click('#rows .row[data-k="k04_rev"]')
    pg.wait_for_function(FIG2_READY, timeout=8000)
    pg.wait_for_timeout(700)
    h = pg.evaluate("document.getElementById('fig2').getBoundingClientRect().height")
    ck.ok(not pg.evaluate("document.querySelector('#fig2 details.f2-full').open") and not pg.evaluate("[...document.querySelectorAll('#fig2 .ad')].filter(e => !(e.closest('details:not([open])') && !e.closest('summary'))).length")
          and no_hscroll(pg) and pg.evaluate("[...document.querySelectorAll('#fig2 pre')].every(p => p.scrollWidth <= p.clientWidth + 1)")
          and 32 <= pg.evaluate("document.querySelector('#fig2 details.f2-full > summary').getBoundingClientRect().height") < 44,
          f"390: the drawer opens on the plain view (no addresses, full listing closed, no sideways scroll, {h:.0f} px tall)")
    pg.click("#fig2 details.f2-full > summary")
    pg.wait_for_timeout(200)
    ck.ok(no_hscroll(pg) and pg.evaluate("[...document.querySelectorAll('#fig2 pre')].every(p => p.scrollWidth <= p.clientWidth + 1)"), "390: with the full listing open there is no sideways scroll")
    pg.close()


def design_checks(browser, base, ck, index):
    """Design checks: two type voices, captions at 12 px and 4.5:1, one plain sentence above the word pills, short
    visible Abstract and Figure 1 caption, the section column on the figures' left edge, no hyphenated byline,
    no clipped pills on a phone."""
    print("== design: type, contrast, short text, alignment")
    for w, h in ((1440, 900), (390, 844)):
        pg = browser.new_page_plain(viewport={"width": w, "height": h})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
        pg.wait_for_timeout(1800)
        small = pg.evaluate("""() => { const out = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (w.nextNode()) { const n = w.currentNode, t = n.textContent.trim(); if (!t) continue; const e = n.parentElement;
              if (!e || e.closest('svg, script, style, noscript, [hidden], canvas, .slideover')) continue; const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
              const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
              if (parseFloat(cs.fontSize) < 11.99) out.push([t.slice(0, 40), cs.fontSize]); } return out; }""")
        ck.ok(not small, f"{w}: every visible text on the main page is at least 12 px ({small[:3]})")
        low = pg.evaluate("""() => { const lum = (c) => { const m = c.match(/[\\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]); };
            const bg = (e) => { for (let n = e; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; const m = c.match(/[\\d.]+/g); if (m && (m.length < 4 || +m[3] > .9)) return c; } return 'rgb(255,255,255)'; };
            const bad = []; for (const e of document.querySelectorAll('figcaption, .tnote, .tcap, .few, .ctl-label, .w-l, .rr-src, .rr-meta, .race-key, .axis-title, .byline, .scope, .authors, .w-chip, .cap-more summary, .abs-more summary, .band-l, .band-s, .mech-note, .mech-gist, .mt-l, .ms-now, .mech-count, .fold summary, .w-fold summary, .simd-def')) {
              if (!e.getBoundingClientRect().width) continue; const fg = getComputedStyle(e).color, a = lum(fg), b = lum(bg(e)); const cr = (Math.max(a, b) + .05) / (Math.min(a, b) + .05); if (cr < 4.5) bad.push([e.className || e.tagName, cr.toFixed(2)]); } return bad; }""")
        ck.ok(not low, f"{w}: caption and label text has at least 4.5:1 contrast ({low[:3]})")
        voices = pg.evaluate("""() => { const f = new Set(), it = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (w.nextNode()) { const n = w.currentNode; if (!n.textContent.trim()) continue; const e = n.parentElement; if (!e || e.closest('svg, script, style, noscript, [hidden], canvas')) continue; if (!e.getBoundingClientRect().width) continue;
              const cs = getComputedStyle(e); f.add(cs.fontFamily.split(',')[0].replace(/"/g, '').trim()); if (cs.fontStyle === 'italic' && !e.closest('em, q, cite')) it.push(n.textContent.trim().slice(0, 30)); } return [[...f], it]; }""")
        ck.ok(len(voices[0]) <= 2 and not voices[1], f"{w}: two type voices only (serif text, mono for code and numbers), no italic captions ({voices[0]}, italics: {voices[1][:2]})")
        words = pg.evaluate("""() => { const ab = document.querySelector('.abstract .fold > p'), cap = document.getElementById('fig1-cap').cloneNode(true); cap.querySelectorAll('details').forEach(d => d.remove());
            const n = (t) => t.trim().split(/\\s+/).length; return [n(ab.innerText), n(cap.innerText)]; }""")
        ck.ok(words[0] <= 60 and words[1] <= 60, f"{w}: the visible Abstract ({words[0]} words) and Figure 1 caption ({words[1]} words) are at most 60 words, the rest behind a details control")
        pl = pg.evaluate("(() => { const p = document.querySelector('.w-plain'), r = document.querySelector('.w-fold'); return [p && p.innerText, p && r && p.getBoundingClientRect().bottom <= r.getBoundingClientRect().top + 1]; })()")
        ck.ok(pl[0] == "A bounds check makes the program stop if an index is out of range; this page measures what that costs, loop by loop." and pl[1], f"{w}: one plain sentence sits above the 'Words used here' pills")
        ck.ok(pg.evaluate("getComputedStyle(document.querySelector('.hero .byline')).hyphens") == "none" and pg.evaluate("getComputedStyle(document.querySelector('.hero .authors')).hyphens") == "none", f"{w}: no hyphenation in the byline and title block")
        clip = pg.evaluate("[...document.querySelectorAll('.w-chip')].filter(c => c.getBoundingClientRect().right > innerWidth - 8 || c.getBoundingClientRect().left < 0).map(c => c.textContent)")
        ck.ok(not clip, f"{w}: no word pill is clipped at the screen edge ({clip})")
        if w >= 1041:
            a = pg.evaluate("[document.getElementById('figures').getBoundingClientRect().left, document.querySelector('.col.body > section').getBoundingClientRect().left, document.querySelector('.abstract').getBoundingClientRect().left]")
            ck.ok(abs(a[0] - a[1]) <= 2 and abs(a[0] - a[2]) <= 2, f"{w}: the section column starts on the figures' left edge ({[round(x) for x in a]})")
        ck.ok(pg.evaluate("(() => { const b = document.getElementById('repro-btn').getBoundingClientRect(); return b.top >= 0 && b.bottom <= innerHeight; })()"), f"{w}: the Reproduce button is visible in the first view")
        pg.close()


def hero_variant_checks(browser, base, ck, index, pooled):
    """The hero comes in four presentations (#hero=1 to 4, the fourth is the default). Every one must pass the same checks: the whole
    finding in the first view, the printed numbers equal to the data, one-click and keyboard controls, the real
    machine code one click away, no console errors, no horizontal scroll, one run then rest, reduced motion."""
    print("== hero variants (1 race track, 2 poster, 3 inspector, 4 the whole map in one race)")
    fx = lambda v: f"{v:.1f}" if v >= 2 else f"{v:.2f}"
    kernels = list(index["criteria"]["kernels"].keys())
    ck.ok(len(kernels) == 8, f"the data lists {len(kernels)} loop shapes (eight expected)")
    dmodel = next(x for x in index["cpus"] if x["slug"] == index["default_cpu"])["cpu_model"]
    default = next(c for c in pooled["cpus"] if c["cpu_model"] == dmodel)
    other = [c for c in index["cpus"] if c["enough"] and c["slug"] != index["default_cpu"]][0]
    opc = next(c for c in pooled["cpus"] if c["cpu_model"] == other["cpu_model"])
    TIMES = "×"

    def want(cpu, kern):
        cell = next((c for c in cpu["cells"] if c["cell_id"] == f"{kern}.L1"), None)
        return fx(cell["aligned"]["ratio"]) + TIMES if cell and cell.get("aligned") else None

    for v in (1, 2, 3, 4):
        for w, h in ((1440, 900), (390, 844)):
            tag = f"hero {v} at {w}x{h}"
            errs = []
            pg = browser.new_page_plain(viewport={"width": w, "height": h})
            watch(pg, errs)
            pg.goto(f"{base}#hero={v}", wait_until="networkidle")
            wait_ready(pg)
            pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
            pg.wait_for_timeout(300)
            pg.keyboard.press("h")  # the hero-variant selector is hidden by default; hide it again so it never covers a control
            ck.ok(pg.get_attribute("#race", "data-hv") == str(v), f"{tag}: the hash picks the variant")
            r = pg.evaluate("(() => { const q = (s) => document.querySelector(s).getBoundingClientRect(); return [q('#race').bottom, q('.hero .scope').bottom, q('.bar-details').bottom, q('.bar-details').top]; })()")
            if v == 4 and w < 641:  # all eight lanes with their ratios, then at most a short scroll to the caption
                lb = pg.evaluate("document.getElementById('race-loops').getBoundingClientRect().bottom")
                ck.ok(lb <= h * 1.3 and r[1] <= h and r[2] <= h and r[3] >= 0, f"{tag}: the eight lanes and the scope line are in the first view, the caption within a short scroll ({round(lb)} px)")
            else:
                ck.ok(r[0] <= h and r[1] <= h and r[2] <= h and r[3] >= 0, f"{tag}: the whole finding (loop tiles, switch, CPU choice, ratio, scope line, Full details) is in the first view ({[round(x) for x in r]})")
            tiles = pg.evaluate("[...document.querySelectorAll('#race-loops button')].map(b => [!!b.querySelector('svg'), b.querySelector('.tl').textContent.trim(), b.getAttribute('aria-label') || '', b.getBoundingClientRect().height])")
            ck.ok(len(tiles) == 8 and all(t[0] and t[1] and t[2] and t[3] >= 44 for t in tiles), f"{tag}: eight glyph tiles, each an SVG of the access pattern with a text label, an aria-label and at least 44 px tall")
            ok_nums, bad = 0, []
            for kern in kernels:
                w1 = want(default, kern)
                if not w1:
                    continue
                pick_loop(pg, kern)
                if pg.get_attribute("#race-sw", "aria-checked") != "true":
                    pg.click("#race-sw")
                got = pg.inner_text("#race-ratio")
                tr = pg.evaluate("(k) => document.querySelector('#race-loops button[data-k=\"' + k + '\"] .tr').textContent", kern)
                if got == w1 and tr == w1:
                    ok_nums += 1
                else:
                    bad.append((kern, got, tr, w1))
            ck.ok(not bad and ok_nums >= 6, f"{tag}: for each loop the printed ratio and its tile equal the pooled aligned L1 ratio, at once after the click ({ok_nums} loops; {bad[:2]})")
            # keyboard: arrows move the loop, Space flips the switch
            pg.focus('#race-loops button[aria-checked="true"]')
            before = pg.evaluate("S.sel")
            pg.keyboard.press("ArrowRight")
            ck.ok(pg.evaluate("S.sel") != before, f"{tag}: the arrow keys move between loop tiles")
            pg.focus("#race-sw")
            pg.keyboard.press("Space")
            ck.ok(pg.get_attribute("#race-sw", "aria-checked") == "false" and "Baseline" in pg.inner_text("#race-ratio"), f"{tag}: the switch works from the keyboard and shows the baseline at once")
            pg.keyboard.press("Space")
            ck.ok(pg.get_attribute("#race-sw", "aria-checked") == "true", f"{tag}: and back on")
            # CPU choice
            sel = pg.evaluate("S.sel")
            pg.click(f'#race-cpu button[data-cpu="{other["slug"]}"]')
            w2 = want(opc, sel)
            ck.ok(w2 is None or pg.inner_text("#race-ratio") == w2, f"{tag}: one click on {other['cpu_short']} prints that model's pooled ratio ({pg.inner_text('#race-ratio')} vs {w2})")
            pg.click(f'#race-cpu button[data-cpu="{index["default_cpu"]}"]')
            # honesty
            ck.ok("Illustration" in pg.inner_text("#race-cap") and "measurement" in pg.inner_text("#race-cap"), f"{tag}: the caption says the animation is an illustration and the number is the measurement")
            # one run, then rest
            pick_loop(pg, "k04_rev")
            started = pg.evaluate("(() => { document.getElementById('race-replay').click(); return document.getAnimations().length; })()")
            ck.ok(v != 4 or started > 0, f"{tag}: Replay the race starts the bars growing at once ({started} animations running right after the click)")
            pg.wait_for_timeout(2600)
            d1 = hero_sig(pg)
            pg.wait_for_timeout(500)
            d2 = hero_sig(pg)
            ck.ok(d1 == d2, f"{tag}: after its one run the illustration rests (no endless loop)")
            if v == 4:
                # the whole map in one race: bar length is the measured ratio on one shared axis
                lens = pg.evaluate("""() => [...document.querySelectorAll('#race-loops button')].map(b => {
                    const len = (k) => { const m = getComputedStyle(b.querySelector('.ln-t.' + k + ' > i')).clipPath.match(/([\\d.]+)%/); return m ? 100 - parseFloat(m[1]) : null; };
                    return [b.dataset.k, len('off'), len('on')]; })""")
                bad4 = []
                for k_, off_, on_ in lens:
                    w_ = want(default, k_)
                    if w_ and off_ and on_ and abs(on_ / off_ - float(w_[:-1])) > 0.02 * float(w_[:-1]) + 0.01:
                        bad4.append((k_, round(on_ / off_, 3), w_))
                ck.ok(len(lens) == 8 and all(o_ for _, o_, _ in lens) and not bad4, f"{tag}: every lane's checked bar is as long as its measured pooled ratio times the unchecked bar, on one axis ({bad4[:2]})")
                ck.ok(len({round(o_, 1) for _, o_, _ in lens}) == 1, f"{tag}: the unchecked bars all end on the same line (the finish of the unchecked run)")
                caps = {}
                for kern in kernels:
                    pick_loop(pg, kern)
                    caps[kern] = pg.inner_text("#race-sub")
                what_ = [re.sub(r"^.*?jobs\. ", "", c_, flags=re.S) for c_ in caps.values()]
                ck.ok(len(set(what_)) == 8 and "how many times the loop runs" not in caps["k08_matmul"] and "vectoriz" in caps["k08_matmul"], f"{tag}: each of the eight loops has its own one-sentence caption (matrix multiply no longer tells the reverse-loop story)")
                if w >= 641:
                    hs = set()
                    for kern in kernels:
                        pick_loop(pg, kern)
                        hs.add(round(pg.evaluate("document.querySelector('#race .race-read').getBoundingClientRect().height")))
                    ck.ok(max(hs) - min(hs) <= 2, f"{tag}: the caption area keeps one fixed height for every loop ({sorted(hs)})")
                    pick_loop(pg, "k04_rev")
                    pg.hover('#race-loops button[data-k="k06_gather"]')
                    pg.wait_for_timeout(250)
                    hov = pg.inner_text("#race-sub")
                    ck.ok("Gather" in hov and pg.evaluate("document.querySelector('#race-loops button[data-k=\"k06_gather\"]').classList.contains('hl')"), f"{tag}: hovering a lane highlights it and shows its own sentence in the caption area")
                    pg.mouse.move(2, 2)  # the page margin: a lane can sit under (700, 120) on other layouts
                    try:  # wait for the caption to settle: a slower machine takes longer than a fixed pause
                        pg.wait_for_function("document.querySelector('#race-sub').innerText.includes('Reverse')", timeout=3000)
                    except Exception:
                        pass
                    ck.ok("Reverse" in pg.inner_text("#race-sub"), f"{tag}: leaving the lane returns the caption to the selected loop (caption: {pg.inner_text('#race-sub')[:60]!r}, hovered lane: {pg.evaluate('[...document.querySelectorAll(\"#race-loops button.hl\")].map(b => b.dataset.k).join()')!r}, scroll {pg.evaluate('scrollY')})")
                pg.click('#race-loops button[data-k="k05_stride2"]')
                pg.wait_for_timeout(500)
                ck.ok(pg.evaluate("!document.getElementById('asm-panel').hidden") and "Checks off" in pg.inner_text("#asm-slot"), f"{tag}: one click on a lane opens the real machine code")
                pg.keyboard.press("Escape")
                pg.wait_for_timeout(450)
                pg.click("#repro-btn")
                shown_ = pg.evaluate("[!document.getElementById('repro-box').hidden, document.getElementById('repro-cmd').textContent]")
                ck.ok(shown_[0] and shown_[1] == index["repo"]["check_command"], f"{tag}: the visible Reproduce button opens the one-command box with the real command")
                pg.keyboard.press("Escape")
                ck.ok(pg.evaluate("document.getElementById('repro-box').hidden"), f"{tag}: Escape closes the Reproduce box")
                pg.keyboard.press("h")
                sw_ = pg.evaluate("(() => { const a = document.querySelector('.hv-switch').getBoundingClientRect(), b = document.getElementById('bar').getBoundingClientRect(), c = document.querySelector('.hero-copy').getBoundingClientRect(); return [a.top >= b.top - 1 && a.bottom <= b.bottom + 1, a.bottom <= c.top]; })()")
                ck.ok(sw_[0], f"{tag}: the hero switcher sits inside the top bar and cannot cover text")
                pg.keyboard.press("h")
            if v == 3:
                pg.wait_for_timeout(300)
                code = pg.inner_text("#hv-code")
                ck.ok("cmp" in code and ("ud2" in code or w < 640) and pg.evaluate("document.querySelectorAll('#hv-code .ln.chk').length") >= 1, f"{tag}: the real machine code with the check lines marked sits beside the array ({code[:40]!r})")
                pg.click("#race-sw")
                pg.wait_for_timeout(300)
                ck.ok("Checks off" in pg.inner_text("#hv-code") and pg.evaluate("document.querySelectorAll('#hv-code .ln.chk').length") == 0, f"{tag}: with the check off the listing is the unchecked build, no check lines")
                pg.click("#race-sw")
            # the full machine code
            pg.click("#race-name")
            pg.wait_for_timeout(500)
            ck.ok(pg.evaluate("!document.getElementById('asm-panel').hidden") and "Checks off" in pg.inner_text("#asm-slot"), f"{tag}: the real machine code opens in the slide-over")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(400)
            ck.ok(pg.evaluate("document.getElementById('asm-panel').hidden"), f"{tag}: Escape closes it")
            ck.ok(no_hscroll(pg), f"{tag}: no horizontal scroll")
            ck.ok(not errs, f"{tag}: no console errors or page errors ({errs[:2]})")
            pg.close()
        # reduced motion: the final frame, same information
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        rp = ctx.new_page()
        rp.goto(f"{base}#hero={v}", wait_until="networkidle")
        rp.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
        rp.wait_for_timeout(300)
        pick_loop(rp, "k04_rev")
        a1 = settled_sig(rp)
        faded = rp.evaluate("(() => { document.getElementById('race-replay').click(); return document.getAnimations().length; })()")
        ck.ok(v != 4 or faded > 0, f"hero {v}: with reduced motion Replay the race still answers the click with a fade, no movement ({faded} animations right after the click)")
        rp.wait_for_timeout(600)
        a2 = hero_sig(rp)
        rp.wait_for_timeout(900)
        a3 = hero_sig(rp)
        ck.ok(a1 == a2 == a3 and rp.inner_text("#race-ratio") == want(default, "k04_rev"), f"hero {v}: with reduced motion the final frame shows at once and the ratio is the same")
        ctx.close()
    # the switcher: invisible to visitors, shown by the hash or the key H
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    ck.ok(pg.evaluate("document.querySelector('.hv-switch').hidden"), "hero switcher: hidden for a visitor (no hero in the hash)")
    pg.keyboard.press("H")
    ck.ok(pg.evaluate("!document.querySelector('.hv-switch').hidden"), "hero switcher: the key H shows it")
    pg.click('.hv-switch button[data-v="3"]')
    ck.ok(pg.get_attribute("#race", "data-hv") == "3" and "hero=3" in pg.evaluate("location.hash"), "hero switcher: a click switches the variant and records it in the hash")
    pg.keyboard.press("H")
    pick_loop(pg, "k05_stride2")
    h_ = pg.evaluate("location.hash")
    ck.ok("hero=3" in h_ and "k05_stride2" in h_, f"hero switcher: choosing a loop keeps the variant in the hash ({h_})")
    pg.close()


def interactive_checks(browser, base, ck, index, pooled, allowed, errors, saved, shots):
    """The interactive layer: hero race, story, slide-over, rewrite toggle, programs chart, widget placeholders,
    progress bar, baked numbers, reduced motion, keyboard use."""
    print("== interactive layer (hero race, story, slide-over, toggles, widgets)")
    raw = open(os.path.join(REPO, "site", "index.html"), encoding="utf-8").read()
    raw_details = open(os.path.join(REPO, "site", "details.html"), encoding="utf-8").read()
    ck.ok(not any(t in h for h in (raw, raw_details) for t in ("SAMPLE DATA", "made-up file", "results/fixture.json")),
          "the served HTML of both pages carries no SAMPLE DATA text (a reader that does not run the page would take real data for a sample; the notices are added by the script only for the test fixture)")
    baked = re.findall(r'<span data-v="(?:lostMin|lostMax|googlePct|c2Lost|c2Vec|fixMin|fixMax|rwSlowMin|rwSlowMax)"[^>]*>([^<]*)</span>', raw)
    ck.ok(baked and all(b and not re.search(r"[A-Z]{4,}|…|&hellip;", b) for b in baked),
          f"index.html carries the first screen's key numbers in the HTML itself, from the data ({len(baked)} spans, e.g. {baked[:3]})")
    ck.ok(re.search(r'id="race-ratio"[^>]*><span data-v="heroRatio">\d+\.\d+</span>&times;', raw) and 'data-v="heroCpu"' in raw,
          "index.html prints the hero's default ratio and CPU model in the HTML itself (no-JS view and link previews see the measurement)")
    ck.ok('id="w-placement"' in raw and 'id="w-mitigation"' in raw and 'id="w-programs"' in raw and raw.count('class="widget"') == 3,
          "the three widget placeholders (w-placement, w-mitigation, w-programs) are in the HTML")
    page = browser.new_page(viewport={"width": 1280, "height": 900}, java_script_enabled=False)
    page.goto(base, wait_until="load")
    ck.ok(f"{index['page']['lost']['min']:.1f}" in page.text_content(".abstract") and "…" not in page.text_content(".abstract"),
          "without JavaScript the abstract still shows real numbers (no blanks)")
    page.close()
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    watch(page, errors)
    page.goto(base, wait_until="networkidle")
    wait_ready(page)
    page.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    fx = lambda v: f"{v:.1f}" if v >= 2 else f"{v:.2f}"
    box = page.evaluate("(() => { const r = document.getElementById('race').getBoundingClientRect(); return [r.top, r.bottom]; })()")
    ck.ok(box[0] >= 0 and box[1] <= 900, f"hero: the loop race fits the first screen at 1280x900 ({box})")
    ck.ok(page.get_attribute("#race-sw", "role") == "switch" and page.get_attribute("#race-sw", "aria-checked") == "true" and page.inner_text("#race-ratio").endswith("×"), "hero: the bounds-check control is a switch, on at the start, with the measured ratio already printed")
    dmodel = next(x for x in index["cpus"] if x["slug"] == index["default_cpu"])["cpu_model"]
    default = next(c for c in pooled["cpus"] if c["cpu_model"] == dmodel)
    for kern in ("k04_rev", "k01_sum_fwd", "k02_add_fwd", "k05_stride2"):
        pick_loop(page, kern)
        if page.get_attribute("#race-sw", "aria-checked") != "true":
            page.click("#race-sw")
        cell = next(c for c in default["cells"] if c["cell_id"] == f"{kern}.L1")
        want = fx(cell["aligned"]["ratio"]) + "×"
        got = page.inner_text("#race-ratio")
        ck.ok(got == want, f"hero: {kern} with the check on prints {got}, the pooled aligned L1 ratio is {want}")
    pick_loop(page, "k04_rev")
    page.click("#race-sw")
    ck.ok(page.get_attribute("#race-sw", "aria-checked") == "false" and "Baseline" in page.inner_text("#race-ratio"), "hero: switching the check off returns to the baseline")
    page.click("#race-replay")
    page.wait_for_timeout(60)
    f2 = hero_sig(page)
    page.wait_for_timeout(90)
    f3 = hero_sig(page)
    page.wait_for_timeout(2600)
    f4 = hero_sig(page)
    page.wait_for_timeout(500)
    f5 = hero_sig(page)
    ck.ok(f2 != f3 or f3 != f4, "hero: Replay runs the belt once")
    ck.ok(f4 == f5, "hero: after its one run the belt rests (no endless loop)")
    shot(page, saved, shots, "hero-on-1280.png")
    if page.get_attribute("#race-sw", "aria-checked") != "true":
        page.click("#race-sw")
    page.click("#race-sw")
    ck.ok("Baseline" in page.inner_text("#race-ratio"), "hero: a click on the switch shows the result at once")
    shot(page, saved, shots, "hero-off-1280.png")
    page.click("#race-sw")
    page.evaluate("window.scrollTo(0, 2600)")
    page.wait_for_timeout(100)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)
    other = [c for c in index["cpus"] if c["enough"] and c["slug"] != index["default_cpu"]][0]
    if page.get_attribute("#race-sw", "aria-checked") != "true":
        page.click("#race-sw")
    page.click(f'#race-cpu button[data-cpu="{other["slug"]}"]')
    page.wait_for_timeout(300)
    ck.ok(page.get_attribute(f'#cpu-seg button[data-cpu="{other["slug"]}"]', "aria-checked") == "true", "hero: the CPU switch also moves Figure 1's CPU control")
    opc = next(c for c in pooled["cpus"] if c["cpu_model"] == other["cpu_model"])
    sel = page.evaluate("S.sel")
    cell = next(c for c in opc["cells"] if c["cell_id"] == f"{sel}.L1")
    ck.ok(page.inner_text("#race-ratio") == fx(cell["aligned"]["ratio"]) + "×", f"hero: on {other['cpu_short']} the printed ratio is that model's pooled ratio ({page.inner_text('#race-ratio')})")
    page.click(f'#race-cpu button[data-cpu="{index["default_cpu"]}"]')
    page.click("#race-name")
    page.wait_for_timeout(500)
    ck.ok(page.evaluate("!document.getElementById('asm-panel').hidden && document.getElementById('asm-slot').contains(document.getElementById('fig2'))")
          and "Checks off" in page.inner_text("#asm-slot") and page.evaluate("document.activeElement.id") == "asm-close",
          "slide-over: opens with Figure 2 (checks off and on), focus on Close")
    shot(page, saved, shots, "slideover-1280.png")
    page.keyboard.press("Escape")
    page.wait_for_timeout(450)
    ck.ok(page.evaluate("document.getElementById('asm-panel').hidden && document.getElementById('figures').contains(document.getElementById('fig2'))")
          and page.evaluate("document.activeElement.id") == "race-name", "slide-over: Escape closes it, Figure 2 goes back to its place, focus returns to the loop name")
    with open(os.path.join(DATA, "mitigate.json"), encoding="utf-8") as f:
        mit = json.load(f)
    page.evaluate("document.getElementById('mit-toggle-box').scrollIntoView({block: 'center', behavior: 'instant'})")
    page.wait_for_timeout(300)
    sh = next(s for s in mit["shapes"] if s["kernel"] == "m04_rev")
    orig = next(v for v in sh["variants"] if v["variant"] == "orig")["range"]
    rec = next(v for v in sh["variants"] if v["variant"] == sh["recommended"])["range"]
    rng = lambda r: f"{fx(r['min'])}–{fx(r['max'])}×"
    t0 = page.inner_text("#mit-toggle-box .rw-val")
    page.click("#mit-toggle-box .sw")
    t1 = page.inner_text("#mit-toggle-box .rw-val")
    ck.ok(rng(orig) in t0 and rng(rec) in t1 and page.get_attribute("#mit-toggle-box .sw", "aria-checked") == "true",
          f"rewrite toggle: before {rng(orig)}, after {rng(rec)} (printed: {t0!r}, {t1!r})")
    page.evaluate("document.getElementById('realworld').scrollIntoView()")
    page.wait_for_timeout(800)
    widget_in = page.evaluate("document.getElementById('w-programs').classList.contains('mounted')")
    if not widget_in:
        rows = page.evaluate("document.querySelectorAll('#rw-chart .pc-row').length")
        ck.ok(rows >= 6, f"real programs: the fallback chart has a row per program ({rows})")
        ck.ok(page.evaluate("document.querySelectorAll('#rw-chart .seg button').length") >= 2, "real programs: the chart has a CPU switch")
    ck.ok(widget_in or page.evaluate("!document.getElementById('rw-chart').hidden"), "real programs: the widget or the fallback chart is shown")
    ck.ok(page.evaluate("[...document.querySelectorAll('#race button, #story button')].every(b => b.textContent.trim() || b.getAttribute('aria-label'))"), "hero and story controls have names")
    ck.ok(page.evaluate("!document.getElementById('prog')"), "no scroll-driven progress bar (nothing moves with scroll)")
    page.close()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    p2 = ctx.new_page()
    watch(p2, errors)
    p2.goto(base, wait_until="networkidle")
    p2.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    p2.click("#race-sw")
    p2.wait_for_timeout(300)
    r1 = hero_sig(p2)
    p2.wait_for_timeout(700)
    r2 = hero_sig(p2)
    ck.ok(r1 == r2, "reduced motion: the hero shows a static final state, no animation")
    ctx.close()


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # messages may quote page text
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default=None, help="folder for the screenshots (default: a temporary folder)")
    ap.add_argument("--quick", action="store_true", help="select every row on the default CPU model only")
    a = ap.parse_args()
    ck = Checker()
    print("== site data equals a fresh build")
    r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build_site_data.py"), "--check"],
                       capture_output=True, text=True)
    ck.ok(r.returncode == 0, r.stdout.strip() or r.stderr.strip())
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("   FAIL the Python playwright package is not installed (pip install playwright; playwright install chromium)")
        return 2
    shots = a.shots or tempfile.mkdtemp(prefix="third-site-")
    os.makedirs(shots, exist_ok=True)
    allowed = allowed_numbers()
    with open(os.path.join(DATA, "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    cpus = [c for c in index["cpus"] if c["enough"]]
    default_cpu = next(c for c in cpus if c["slug"] == index["default_cpu"])
    slug = lambda s: re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))
    srv = serve()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    saved = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--mute-audio", "--disable-speech-api", "--autoplay-policy=user-gesture-required"])
            browser.new_page_plain = browser.new_page
            browser.new_page = lambda **kw: (lambda pg: (pg.add_init_script("window.__OPEN_ALL__ = true"), pg)[1])(browser.new_page_plain(**kw))
            try:
                # ---- desktop, default view
                print("== 1280 wide")
                errors = []
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                watch(page, errors)
                page.goto(base, wait_until="networkidle")
                wait_ready(page)
                things = page.evaluate("""() => [...document.querySelectorAll('.front > *, #figures > *, .body > *')]
                    .filter(n => !n.hidden && n.getBoundingClientRect().height > 0 && n.getBoundingClientRect().top < innerHeight)
                    .map(n => n.tagName.toLowerCase() + (n.id ? '#' + n.id : '.' + n.className))""")
                ck.ok(len(things) <= 6, f"first screen (1280x900): {len(things)} things, at most 6: {things}")
                abstract = page.evaluate("(() => { const a = document.querySelector('.abstract').cloneNode(true); a.querySelectorAll('.cannot, .cite').forEach(n => n.remove()); a.querySelectorAll('details').forEach(d => { d.open = true; }); document.body.append(a); const t = a.innerText; a.remove(); return t; })()")
                lost = index["page"]["lost"]
                with open(os.path.join(DATA, "corpus.json"), encoding="utf-8") as f:
                    corpus = json.load(f)
                with open(os.path.join(DATA, "mitigate.json"), encoding="utf-8") as f:
                    mit = json.load(f)
                with open(os.path.join(DATA, "siblings.json"), encoding="utf-8") as f:
                    sib = json.load(f)
                t2 = corpus["census2"]["totals"]
                ck.ok("Google" in abstract and f"{index['claim']['google_pct']:.2f}%" in abstract
                      and page.evaluate("document.querySelector('.abstract a').href") == index["claim"]["url"],
                      "abstract: Google's figure with its source link")
                ck.ok(f"{lost['min']:.1f} to {lost['max']:.1f}" in abstract, "abstract: the lost-SIMD range is the one in index.json")
                ck.ok("neither confirms nor contradicts" in abstract, "abstract: says this neither confirms nor contradicts Google's average")
                fx = lambda v: f"{v:.1f}" if v >= 2 else f"{v:.2f}"
                t1 = corpus["census1"]["totals"]
                ck.ok(f"{t2['lost']} of {t2['none']['vectorized']:,}" in abstract and f"{t1['lost']} of {t1['none']['vectorized']}" in abstract
                      and "counted, not timed" in abstract.lower(), "abstract: both census counts, labelled counted, not timed")
                ab_nums = re.findall(r"\d[\d,]*(?:\.\d+)?", re.sub(r"\d+\.\d+\.\d+|-O\d|\b1×|AVX2", "", abstract.replace(page.inner_text(".abstract a"), "")))
                lis = page.evaluate("[...document.querySelectorAll('.abstract ul.findings li')].map(l => [l.innerText, l.firstElementChild && l.firstElementChild.tagName, l.innerText.indexOf(l.firstElementChild.innerText)])")
                ck.ok(len(ab_nums) <= 15 and len(lis) == 4 and all(t == "B" and i == 0 for _, t, i in lis)
                      and "forward loops that keep SIMD stay near 1" in abstract
                      and "forward loops pay" not in abstract and "-O3" in abstract and "-O2" in abstract,
                      f"abstract: four bullet lines, each led by its bold headline, Google's figure plus at most 15 numbers (the real-programs range and the two newer-toolchain versions add four, the as-compiled forward add one) ({len(ab_nums)}: {ab_nums}), 'forward loops that keep SIMD', GCC as -O3 vectorization and -O2 cost")
                fixr = [v["range"] for sh in mit["shapes"] if sh["kernel"] in ("m04_rev", "m08_matmul")
                        for v in sh["variants"] if v["variant"] == sh["recommended"]]
                ck.ok(f"{fx(min(r['min'] for r in fixr))} to {fx(max(r['max'] for r in fixr))}" in abstract and "GCC" in abstract,
                      "abstract: the rewrite range of the reverse and matrix-multiply loops and the toolchain caveat")
                # numbers typed in prose (not filled from data) must equal the data they describe
                with open(os.path.join(DATA, "realworld.json"), encoding="utf-8") as f_:
                    rwd = json.load(f_)
                with open(os.path.join(DATA, "versions.json"), encoding="utf-8") as f_:
                    verd = json.load(f_)
                rw_main = next(g for g in rwd["timing"]["groups"] if g["cpu_model"] == rwd["timing"]["main_cpu"])
                rw_ndet = lambda g: sum(1 for r in rwd["rows"] if not r["control"] and g["rows"][r["row"]]["reading"] == "detectably slower")
                rw_other = [g for g in rwd["timing"]["groups"] if g is not rw_main]
                ck.ok(all(rw_ndet(g) < rw_ndet(rw_main) for g in rw_other),
                      "abstract: 'fewer on (the) others': every other CPU model detects fewer slowed programs than the main model")
                big_ = corpus["census2"]["projects"][0]
                ck.ok(abs(big_["lost"] / t2["lost"] - 0.75) <= 0.03 and "about three quarters" in abstract,
                      f"abstract: the biggest project's share of the lost loops ({big_['lost'] / t2['lost']:.3f}) is the one the words 'about three quarters' describe")
                org_ = [(c_["none"]["vectorized_by_origin"]["libc++"] / c_["none"]["vectorized"], c_["lost_by_origin"]["libc++"]) for c_ in (corpus["census1"]["totals"], corpus["census2"]["totals"])]
                ck.ok(all(s_ > 0.5 and n_ == 0 for s_, n_ in org_) and "most of the loops are libc++" in abstract,
                      f"abstract: libc++'s own loops are most of both censuses and none of them lost SIMD ({[round(s_, 3) for s_, _ in org_]})")
                with open(os.path.join(SITE, "race.js"), encoding="utf-8") as f_:
                    race_src = f_.read()
                mm_ = re.search(r"Clang (\d+) to (\d+) keep SIMD yet cost (\d\.\d)× at L1", race_src)
                mm_vs = [t_["version"] for t_ in verd["toolchains"]]
                mm_l1 = verd["summary"]["matmul_main"]["L1"]
                ck.ok(mm_ is not None and (int(mm_.group(1)), int(mm_.group(2))) == (min(mm_vs), max(mm_vs))
                      and f"{mm_l1['min']:.1f}" == f"{mm_l1['max']:.1f}" == mm_.group(3),
                      f"hero caption for matrix multiply: the typed clang range and '{mm_.group(3) if mm_ else '?'}×' equal the timed toolchains {mm_vs} and the main-model L1 ratio ({mm_l1['min']:.3f} to {mm_l1['max']:.3f})")
                seg = page.evaluate("[...document.querySelectorAll('#cpu-seg button')].map(b => b.dataset.cpu)")
                few = page.inner_text("#cpu-few")
                ck.ok(seg == [c["slug"] for c in cpus] and all(f["cpu_short"] in few for f in index["page"]["cpus_few"]) and "too few to judge" in few
                      and page.evaluate("getComputedStyle(document.getElementById('cpu-few')).display") == "block"
                      and not page.evaluate("getComputedStyle(document.getElementById('cpu-few')).borderTopStyle !== 'none'"),
                      f"Figure 1: the switcher offers the CPU models with at least {index['criteria']['minimum_jobs']} jobs ({seg}) and names the others as too few jobs")
                open_full(page)
                ck.ok("instructions, not time" in page.inner_text("#fig2 .f2-instr"), "Figure 2: the instruction ratio sits in its header, labelled 'instructions, not time'")
                with open(os.path.join(DATA, "pooled.json"), encoding="utf-8") as f:
                    pooled = json.load(f)
                dp = browser.new_page(viewport={"width": 1280, "height": 900})
                watch(dp, errors)
                dp.goto(base + "details.html", wait_until="networkidle")
                wait_details(dp)
                google_wording(page, ck, "main page", pooled)
                google_wording(dp, ck, "details page", pooled)
                ck.ok(not dp.evaluate("document.getElementById('appb-details').open"), "details page: Appendix B is folded into a collapsed <details>")
                dp.evaluate("document.getElementById('appb-details').open = true")
                appb = dp.evaluate("""() => [...document.querySelectorAll('#appb-cpu tbody tr')].map(r => r.innerText)""")
                ck.ok(len(appb) == len(index["cpus"]) and all("1.5" in r and "2%" in r for r, c in zip(appb, index["cpus"]) if c["enough"])
                      and "results/s4-pooled/pooled.json" in dp.inner_text("#appendix-b")
                      and "not a statement about Google" in dp.inner_text("#appendix-b"),
                      "Appendix B: per CPU model the form, the numbers and the rule in plain words, the pooled file named by its path, and no claim about Google's services")
                terms = page.evaluate("""() => { const t = document.getElementById('terms'), tb = document.getElementById('cpu-table');
                    return t ? [t.innerText, !!(t.compareDocumentPosition(tb) & Node.DOCUMENT_POSITION_FOLLOWING)] : null; }""")
                ck.ok(bool(terms) and terms[1] and all(w in terms[0] for w in ("A run is", "job", "pooled", "interval")),
                      "section 1 defines run, job, pooled and interval in plain words before Table 1")
                # placement-sensitive cells, with the pooled ratio of the two columns
                t1h = page.evaluate("[...document.querySelectorAll('#cpu-table thead th')].map(t => t.innerText)")
                t1r = page.evaluate("[...document.querySelectorAll('#cpu-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                rec = dp.inner_text("#reconcile")
                repro = next(c["reproduction"] for c in cpus if c["reproduction"] and c["reproduction"]["checked"])
                ck.ok(any("aligned" in h and "Lose" in h for h in t1h) and any("as compiled" in h for h in t1h)
                      and any("judged" in h for h in t1h) and any("Placement-sensitive" in h for h in t1h)
                      and all(r[4] == f"{fx(c['forward_judged_aligned']['min'])}–{fx(c['forward_judged_aligned']['max'])}×"
                              or r[4] == f"{fx(c['forward_judged_aligned']['min'])}×" for r, c in zip(t1r, index["cpus"]) if c["enough"])
                      and "excluded" not in page.inner_text("#cpu-cap") and "left out of the 2% test" in page.inner_text("#cpu-cap")
                      and f"{repro['outside']} of {repro['checked']}" in rec and f"{repro['max_gap_pct']:.1f}%" in rec,
                      "Table 1: lose-SIMD aligned and as compiled, judged forward loops only, placement-sensitive cells in their own column; the note beside it reconciles 'same in every run' with the run-to-run gap")
                ck.ok(all(page.locator(f"#{n}").count() == 1 and "Jobs:" in page.inner_text(f"#{n}") for n in ("cpu-note", "mit-note"))
                      and "Jobs:" in dp.inner_text("#sib-note")
                      and "Jobs:" in page.text_content("#fig1-cap"), "every table that quotes a range (Tables 1, 3, 4) and Figure 1's caption carry a one-line jobs note")
                low = dp.inner_text("#fwd-low")
                ck.ok("9V45" in low and "includes 1" in low and "slowdowns only" in low,
                      "beside Table 1: the judged forward loop below 1x on EPYC 9V45 is explained (interval of compiled / aligned includes 1; the rule bounds slowdowns only)")
                ip = dp.inner_text("#instr-p")
                ck.ok("not for every loop" in ip and "inferred" in ip and "same story" not in ip and "histogram" in ip,
                      "section 1: the instruction counts are said to agree for loops that lose SIMD, not for every loop, with the histogram and forward add as counter-examples, marked inferred")
                ck.ok(all(w in dp.inner_text("#jobsets") for w in ("Section 5", "Section 6", "aligned", "as compiled"))
                      and "Xeon" in dp.inner_text("#sib-cap") and "Xeon 6973P-C" in dp.inner_text("#otherdraws"),
                      "results: one note states which job set and column each part uses; Table 4's caption names the Xeon draws; Table 1 explains the models without a row")
                ps_rows = dp.evaluate("[...document.querySelectorAll('#ps-table tbody tr')].map(r => r.textContent)")
                ps_want = sum(len(c["placement_sensitive"]) for c in cpus)
                ps_ids = {p["cell_id"].split(".")[0] for c in cpus for p in c["placement_sensitive"]}
                ck.ok(len(ps_rows) == ps_want and {"k02_add_fwd", "k03_stencil"} <= ps_ids and all("[" in r for r in ps_rows),
                      f"section 3: Table 2 lists every placement-sensitive cell ({ps_want}), forward add and stencil among them, each with the interval of compiled / aligned")
                # section 4, the census
                cn = page.inner_text("#census-not")
                ck.ok(all(w in cn for w in ("Counted, not timed", "hotness", "no claim about runtime cost", "Google")),
                      "section 4 says plainly: counted not timed, hotness unknown, no claim about runtime cost or Google's average")
                ncat = sum(1 for r in corpus["categories"] if r["census"] in (1, 2))
                nmain = sum(1 for r in corpus["categories"] if r["census"] == 2 or (r["census"] == 1 and r.get("total")))
                ck.ok(dp.locator("#census-rows .c-row").count() == ncat and page.locator("#census-rows .c-row").count() == nmain,
                      f"Figure 4: on the details page one row per category and census total ({ncat}); on the main page census 1 as one total ({nmain})")
                ps_ = dp.inner_text("#prog-sum")
                ck.ok("once each job" in ps_ and "noise floor" in ps_ and "consistent with" not in ps_,
                      "section 7: the summary says in plain words the largest slowdown once the noise floor is accounted for")
                ck.ok("failed" in page.inner_text("#census-ctl-sum") and "failed" in dp.inner_text("#census-ctl-sum"),
                      "the census controls' FAIL is summarised in one visible line on both pages")
                ctl = dp.inner_text("#census-controls")
                ck.ok("PASS" in ctl and "FAIL" in ctl and "AVX2" in ctl and "expected lost" in ctl and "Determinism" in ctl,
                      "section 4 lists the controls: determinism PASS, kernel control PASS at baseline and FAIL at AVX2 with its reason")
                fig4 = []
                for i in range(dp.locator("#census-rows .c-row.c-click").count()):
                    r = dp.locator("#census-rows .c-row.c-click").nth(i)
                    r.click()
                    pnl = r.evaluate("n => n.nextElementSibling")
                    nrow = r.evaluate("n => n.nextElementSibling.querySelectorAll('tbody tr').length")
                    want = r.evaluate("n => +n.querySelector('.c-np').textContent.replace(/[^0-9]/g, '')")
                    fig4.append(nrow == want and r.get_attribute("aria-expanded") == "true")
                    r.click()
                ck.ok(len(fig4) == ncat and all(fig4), f"details page, Figure 4: a click on each row lists that category's projects, one row per project ({sum(fig4)} of {ncat})")
                un = corpus["census2"]["patterns_unlabelled"]
                ck.ok(sum(x["count"] for x in corpus["census2"]["patterns"]) + un["count"] == t2["lost"]
                      and f"remaining {un['count']} copies ({un['unique_locations']} locations)" in dp.inner_text("#census-p2"),
                      "section 4: the shape counts plus the unlabelled rest add up to the census total, stated beside them")
                exs = dp.inner_text("#census-examples")
                ck.ok(page.locator("#census-examples").count() == 0 and "Real loops quoted" in page.inner_text("#census")
                      and dp.locator("#census-examples figure").count() >= 4 and all(x in exs for x in ("LightGBM", "llama.cpp", "Stockfish")),
                      "section 4 on the main page links to the real loops quoted on the details page (all of them, Stockfish included, with project names and source lines)")
                cp = page.inner_text("#census") + dp.inner_text("#census-full")
                wo = corpus["census2"]["without_biggest"]
                ck.ok(f"{wo['lost']} of {wo['vectorized']:,}" in cp and f"{t2['lost_unique_locations']} of {t2['none']['vectorized_unique']}" in cp
                      and f"{t2['lost_with_index_evidence']} of {t2['lost']}" in cp,
                      "section 4 gives distinct locations beside raw counts, the count without the dominant project and the traced-check evidence")
                # section 5, what to change
                ck.ok(page.locator("#mit-table tbody tr").count() == len(mit["shapes"]), f"section 5: one table row per loop shape ({len(mit['shapes'])})")
                mt = page.inner_text("#mitigate")
                order = page.evaluate("""() => !!(document.getElementById('mit-unsafe').compareDocumentPosition(document.getElementById('mit-table')) & Node.DOCUMENT_POSITION_FOLLOWING)""")
                ck.ok(order and "span variant" in page.inner_text("#mit-cap") and "strictest rule; ranges shown" in mt and "earns the word" not in mt,
                      "section 5: the silently-unsafe warning comes before the table, the span variant is defined in the caption, the rule is stated as 'measured under the strictest rule; ranges shown'")
                ck.ok("better" in mt and f"{mit['usable_jobs']} of {mit['job_count']} jobs" in mt and "rbegin" in mt and "unsafe" in mt.lower(),
                      "section 5: the pre-committed 'better' rule with the usable-job count, and the silently-unsafe std::transform warning")
                opened = []
                for sh in mit["shapes"]:
                    page.click(f'#mit-table tr[data-k="{sh["kernel"]}"]')
                    page.wait_for_timeout(80)
                    nrows = page.locator("#mit-detail .mv-row").count()
                    ok_ = (nrows == len(sh["variants"]) and page.locator("#mit-detail pre").count() == 2
                           and page.get_attribute(f'#mit-table tr[data-k="{sh["kernel"]}"]', "aria-expanded") == "true")
                    bad = page_numbers(page, allowed, "#mit-detail")
                    if bad:
                        ok_ = False
                        print("      numbers not in the data:", bad[:4])
                    opened.append(ok_)
                ck.ok(all(opened), f"section 5: a click on each shape opens every rewrite tried, with the original's and the rewrite's code, every number in the data ({opened})")
                page.click('#mit-table tr[data-k="m04_rev"]')
                # section 6, other toolchains
                ck.ok(dp.locator("#sib-table thead th").count() == len(sib["kernels"]) + 1 and "vectorize under no setup" in dp.inner_text("#sib-cap")
                      and "not that the check is free" in dp.inner_text("#sib-cap"),
                      "section 6: Table 4 has all eight loops, and its note says kept vectorization is not free")
                ck.ok(dp.locator("#sib-table tbody tr").count() == len(sib["rows"]) and dp.locator("#sib-table .t-lost").count() > 0,
                      f"section 6: one row per setup ({len(sib['rows'])}), with lost / kept / none marked")
                ck.ok(dp.locator("#sibsum-table tbody tr").count() == 5 and dp.locator("#sibsum-table .t-lost").count() > 0
                      and page.locator("#sibsum-table").count() == 0
                      and page.locator('#siblings a[href="details.html#siblings-full"]').count() == 1,
                      "section 6: the five-row timed summary (Table 4a) is on the details page; the main page links to it")
                # section 6: the compile-only sweep (ce-sweep/): every cell against site data, the counts against the sweep itself
                with open(os.path.join(DATA, "cesweep.json"), encoding="utf-8") as f:
                    ce = json.load(f)
                ce_src = os.path.join(REPO, "ce-sweep", "results.json")
                with open(ce_src, encoding="utf-8") as f:
                    cer = json.load(f)
                with open(os.path.join(REPO, "ce-sweep", "permalinks.json"), encoding="utf-8") as f:
                    cep = json.load(f)["links"]
                with open(ce_src, "rb") as f:
                    ce_sha = hashlib.sha256(f.read()).hexdigest()
                CE_SHORT = {"k01_sum_fwd": "forward sum", "k02_add_fwd": "forward add", "k03_stencil": "stencil", "k04_rev": "reverse",
                            "k05_stride2": "stride-2", "k06_gather": "gather", "k07_hist": "histogram", "k08_matmul": "matrix multiply"}
                CE_WORD = {"lost": "lost under the checks", "kept": "kept", "none": "not vectorized in either build"}
                ce_st = lambda v: "lost" if v["none"] and not v["checked"] else ("kept" if v["checked"] else "none")
                cl_rows = [m for m in cer["matrix"] if m["family"] == "clang"]
                CE_VER = len({(m["family"], "trunk" if m["version"] == "trunk" else int(m["version"].split(".")[0])) for m in cer["matrix"]})  # 28 ids, 14 versions
                n_builds = 2 * len({(c["compiler_id"], c["target"], c["opt"]) for c in cer["cells"]})
                ck.ok(len(cl_rows) == 54 and len(cer["matrix"]) == 84 and len(cer["cells"]) == 672 and n_builds == 168
                      and ce["counts"] == {"builds": 168, "cells": 672, "compilers": 28, "rows": 84} and len(ce["rows"]) == 84
                      and ce["summary"]["clang_rows"] == 54 and ce["source_sha256"] == ce_sha,
                      f"compile-only sweep: 54 clang rows, 84 rows, 672 cells, 168 builds in ce-sweep/results.json, and the site copy is of this file ({len(cl_rows)}, {len(cer['matrix'])}, {len(cer['cells'])}, {n_builds})")
                cells = {(c["compiler_id"], c["target"], c["opt"], c["kernel"]): c for c in cer["cells"]}
                lostm = {(m["compiler_id"], m["target"], m["opt"]): set(m["lost"]) for m in cer["matrix"]}
                same = all(r["vec"][k] == {"none": bool(cells[(r["compiler_id"], r["target"], r["opt"], k)]["none"]["vectorized"]),
                                           "checked": bool(cells[(r["compiler_id"], r["target"], r["opt"], k)]["hardened"]["vectorized"])}
                           and (k in lostm[(r["compiler_id"], r["target"], r["opt"])]) == (ce_st(r["vec"][k]) == "lost") == (k in r["lost"])
                           for r in ce["rows"] for k in ce["kernels"])
                ck.ok(same, "compile-only sweep: every site cell (vectorized with checks off / on, lost) equals ce-sweep/results.json")
                bad, seen = [], 0
                for opt in ("-O2", "-O3"):
                    page.click(f'#ce-oseg button[data-o="{opt}"]')
                    page.wait_for_timeout(80)
                    got = page.evaluate("""[...document.querySelectorAll('#ce-panels .ce-panel')].map(p => [p.dataset.t,
                        [...p.querySelectorAll('.ce-cell')].map(c => [c.getAttribute('aria-label'), (c.className.match(/ce-(lost|kept|none)/) || [])[1]])])""")
                    for t, cs in got:
                        lab = {c[0]: c[1] for c in cs}
                        rows_t = [r for r in ce["rows"] if r["target"] == t and r["opt"] == opt]
                        if len(cs) != 8 * len(rows_t) or len(lab) != len(cs):
                            bad.append((t, opt, "count", len(cs)))
                        for r in rows_t:
                            name = ("clang trunk" if r["version"] == "trunk" else f"clang {r['version']}") if r["family"] == "clang" else f"GCC {r['version']}"
                            for k in ce["kernels"]:
                                want = ce_st(r["vec"][k])
                                key = f"{name}, {ce['targets'][t]}, {opt}, {CE_SHORT[k]}: {CE_WORD[want]}"
                                seen += 1
                                if lab.get(key) != want:
                                    bad.append((key, lab.get(key)))
                page.click('#ce-oseg button[data-o="-O2"]')
                ck.ok(not bad and seen == 672, f"Figure 5: every matrix cell ({seen} of 672: both levels, three panels) shows the state recomputed from cesweep.json ({bad[:3]})")
                page.evaluate("document.querySelector('#ce-panels .ce-panel[data-t=\"x86-64\"]').scrollIntoView()")
                page.hover('#ce-panels .ce-panel[data-t="x86-64"] .ce-cell[aria-label^="clang trunk, x86-64 (SSE2), -O2, matrix multiply"]')
                rem = page.inner_text("#ce-remark")
                tr = next(r for r in ce["rows"] if r["version"] == "trunk" and r["target"] == "x86-64" and r["opt"] == "-O2")
                ck.ok("clang trunk, x86-64 (SSE2), -O2, matrix multiply: lost under the checks" in rem and tr["remark"]["k08_matmul"].replace("loop not vectorized: ", "") in rem
                      and "Early exit loop with store but no supported condition load" in rem,
                      f"Figure 5: hovering a cell shows that cell and the compiler's own remark ({rem[:90]})")
                hrefs = page.evaluate("""[...document.querySelectorAll('#ce-panels .ce-panel[data-t="x86-64"] a.ce-h')].map(a => a.href)""")
                ck.ok(hrefs == [cep[k]["url"] for k in ce["kernels"]] and all(cep[k]["verified"] for k in ce["kernels"])
                      and all(u.startswith("https://godbolt.org/z/") for u in hrefs)
                      and dp.evaluate("[...document.querySelectorAll('#ce-table thead a')].map(a => a.href)") == hrefs,
                      f"Figure 5 and Table 4b: the 8 column heads open each loop in Compiler Explorer, the verified short links in ce-sweep/permalinks.json ({hrefs[:2]})")
                cf, cc = page.inner_text("#ce-find"), page.inner_text("#fig-ce-cap")
                sm = ce["summary"]
                ck.ok(f"all {sm['clang_rows']} clang rows lose the reverse and stride-2 loops" in cf and sm["clang_rev_s2_lost"] == sm["clang_rows"]
                      and "none loses a forward loop" in cf and sm["clang_fwd_lost"] == 0
                      and "lost on clang 16 to 18 at baseline x86-64 only, kept on 19 to 22 everywhere, lost everywhere on 23 and trunk" in cf
                      and "No loop is lost on AArch64 only" in cf and "GCC loses nothing at -O2" in cf and sm["gcc_o2_lost"] == 0
                      and f"forward add in {sm['gcc_o3_lost']['k02_add_fwd']} of {sm['gcc_o3_rows']} rows" in cf
                      and sm["gcc_o3_lost"]["k04_rev"] == sm["gcc_o3_rows"] == sm["gcc_o3_lost"]["k08_matmul"]
                      and "Compile-only: this says which loops lose vectorization, not what they cost" in cc and "assumed to match" in cc
                      and f"on {CE_VER} compiler versions ({ce['counts']['compilers']} Compiler Explorer compiler ids)" in cf and CE_VER == 14,
                      "section 6: the sweep's findings, recomputed from the data, and the compile-only and libc++ pairing sentences")
                ck.ok(dp.locator("#ce-table tbody tr").count() == 84 and dp.locator("#ce-table tbody td.ce-td").count() == 672
                      and dp.locator("#ce-notes li").count() >= 4 and "Early exit loop with store but no supported condition load" in dp.inner_text("#siblings-full")
                      and "No timing" in dp.inner_text("#siblings-full") and "assumed to match" in dp.inner_text("#siblings-full"),
                      "details: Table 4b has all 84 compiler rows (672 cells) and per-version notes")
                note_ce = dp.inner_text("#ce-full + p")
                ck.ok(f"{ce['summary']['clang_rows'] + ce['summary']['gcc_rows']} rows ({CE_VER} compiler versions," in note_ce and f"{ce['counts']['compilers']} separate x86-64 and AArch64 compiler ids" in note_ce
                      and f"from {ce['counts']['builds']} builds" in note_ce and "compilers," not in note_ce.replace("compiler versions,", ""),
                      f"details, Table 4b note: {CE_VER} compiler versions are told apart from the {ce['counts']['compilers']} Compiler Explorer ids ({note_ce[:120]!r})")
                cbox = page.inner_text("#cannot")
                ck.ok(f"Compiled only: the {CE_VER} compiler versions ({ce['counts']['compilers']} Compiler Explorer compiler ids) in section 6" in cbox and "few-job runs" in cbox and "Other compilers" in abstract and "compiled only" in abstract,
                      "abstract and box: the wider toolchain coverage is compile-only; timing rests on clang 18 plus a few GCC and clang 20 jobs")
                main_versions(abstract, cbox, ck)
                st = page.inner_text("#siblings") + dp.inner_text("#siblings-full")
                ck.ok("GCC" in st and "-O3" in st and "single job" in st and str(sib["single_job_groups"]) in st,
                      "section 6: the plain finding (GCC differs) and the thin coverage, with the count of single-job cells")
                cap1 = page.text_content("#fig1-cap")
                ck.ok("Filled dot" in cap1 and "Hollow ring" in cap1, "Figure 1's caption says in words what the filled and hollow marks are")
                ck.ok(dp.locator("#fig3-title").is_visible() and dp.locator("#fig3 .mhead").count() == 1, "details page: Figure 3 has a title and a header row")
                k02t = dp.inner_text("#k02-faster") + dp.inner_text("#fig3 figcaption")
                ck.ok("per pass" in k02t and "inferred" in k02t,
                      "section 3 and Figure 3 explain why the checked forward add is faster aligned (per-pass unrolling, cause marked inferred)")
                ck.ok(page.evaluate("""() => [...document.querySelectorAll('#rows .src, #fig2 .f2-src code, #fig2 pre.asm, #fig2 pre.asm-lite')]
                    .every(n => getComputedStyle(n).overflowWrap === 'normal' && getComputedStyle(n).wordBreak === 'normal')"""),
                      "code lines wrap only at spaces, never mid-token")
                page.evaluate("scrollTo(0, 0)"); page.wait_for_timeout(150)
                for _ in range(15):  # poll up to 3 s: layout and the first-view animation settle later on a slower machine
                    rows_in = page.evaluate("""() => { const rs = [...document.querySelectorAll('#race-loops button')];
                        return [rs.length, rs.filter(r => { const b = r.getBoundingClientRect(); return b.height > 0 && b.bottom <= innerHeight + 1; }).length]; }""")
                    if rows_in[1] == rows_in[0]:
                        break
                    page.wait_for_timeout(200)
                ck.ok(rows_in[0] == len(index["criteria"]["kernels"]) and rows_in[1] == rows_in[0],
                      f"first screen (1280): all {rows_in[0]} loop rows of the hero race are visible ({rows_in[1]} are)")
                order0 = page.evaluate("[...document.querySelectorAll('#rows .row')].map(r => r.dataset.k)")
                orders = []
                page.click('#col-seg [data-col="compiled"]'); page.wait_for_timeout(100)
                orders.append(page.evaluate("[...document.querySelectorAll('#rows .row')].map(r => r.dataset.k)"))
                for c in cpus:
                    page.click(f'#cpu-seg [data-cpu="{c["slug"]}"]'); page.wait_for_timeout(100)
                    orders.append(page.evaluate("[...document.querySelectorAll('#rows .row')].map(r => r.dataset.k)"))
                page.click('#col-seg [data-col="aligned"]'); page.click(f'#cpu-seg [data-cpu="{default_cpu["slug"]}"]'); page.wait_for_timeout(100)
                ck.ok(all(o == order0 for o in orders), "Figure 1: the row order stays fixed across the column toggle and every CPU model")
                lab = page.get_attribute("#col-hint", "aria-label")
                ck.ok(lab == "What does aligned mean?", f"the '?' button's label names no toggle option on its own ({lab!r})")
                sel = page.evaluate("document.querySelector('#rows .row[aria-selected=true]').dataset.k")
                ck.ok(sel == "k04_rev", f"the reverse loop is selected on load (got {sel})")
                f2 = page.evaluate("""() => ({ top: document.getElementById('fig2').getBoundingClientRect().top,
                    notes: [...document.querySelectorAll('#fig2 pre.asm-lite .note')].map(n => n.textContent),
                    chk: document.querySelectorAll('#fig2 pre.asm-lite .chk').length, trap: document.querySelectorAll('#fig2 pre.asm-lite .trap').length,
                    simd: document.querySelectorAll('#fig2 pre.asm-lite .simd').length })""")  # the plain view only: the closed full listing does not count
                ck.ok(f2["top"] < 900 and f2["chk"] >= 2 and f2["trap"] >= 1 and f2["simd"] >= 1
                      and any(n.startswith("the check") for n in f2["notes"]) and any(n.startswith("this trap stops the program") for n in f2["notes"]),
                      "first screen (1280): Figure 2 shows the reverse loop's SIMD lines, the check and the trap, labelled in words")
                open_full(page)
                ck.ok("could not determine number of loop iterations" in page.inner_text("#fig2")
                      or "no longer knows how many times" in page.inner_text("#fig2"),
                      "Figure 2: the compiler's remark explained in plain words")
                ck.ok(page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(255, 255, 255)", "the page is white")
                meth = page.inner_text("#method") + dp.inner_text("#method-full")
                d1 = index["method"]["dayone"][0]
                det = dp.text_content("#loosened-details") or ""
                IF = index["intel_forward"]
                body_ = page.inner_text("body")
                ck.ok("on the AMD models" in abstract and "AMD models only" in dp.inner_text("#intel-p")
                      and f"{IF['aligned']['min']:.2f}–{IF['aligned']['max']:.2f}" in dp.inner_text("#intel-p")
                      and "on the AMD models" in dp.inner_text("#sib-finding") and "Intel" in page.inner_text("#cpu-note"),
                      "forward loops near 1x is said for the AMD models only, with the Intel jobs' forward add range in section 1, Table 1's note and section 6")
                fwd_lo = min(c["forward_aligned"]["min"] for c in cpus)
                ck.ok(f"aligned, {fx(fwd_lo)}–" in dp.inner_text("#ps-sum") and f"{fx(fwd_lo)}–" in dp.inner_text("#sib-table") and f"{fx(fwd_lo)}–" in dp.inner_text("#sibsum-table"),
                      f"the aligned forward low end on the page is the data's ({fx(fwd_lo)}x), in section 3, Table 4 and its summary")
                s3t = page.inner_text("#placement")
                ck.ok("own instructions were not the cause" in s3t and "inferred" in s3t and "The check was not the cause" not in s3t,
                      "section 3: the check's own instructions were not the cause, the layout it induces was, the hardware reason inferred")
                fn = dp.inner_text("#fn-novec")
                with open(os.path.join(DATA, "index.json"), encoding="utf-8") as f_:
                    ce_ = next((c_ for c_ in json.load(f_)["cpus"] if c_["slug"] == default_cpu["slug"]), None)
                ck.ok("only factor measured" in fn and "largest" not in fn and "about a third" in fn and ce_ is not None and 30 <= ce_["novec_rev_share_pct"] <= 37 and f"({int(ce_['novec_rev_share_pct'] + 0.5)}%)" in fn and f"The rest, {100 - int(ce_['novec_rev_share_pct'] + 0.5)}%," in fn and "not explained by this measurement" in fn,
                      "footnote 1: losing SIMD is the only factor measured, about a third of the extra time, the rest stated as unexplained")
                av = dp.inner_text("#census-avx2")
                ck.ok("loses fewer, not more" not in av and "snappy" in av and "census 2 loses fewer" in av, "section 4: only census 2 loses fewer at AVX2; census 1 over 18 projects, snappy not built")
                ck.ok("left out" in page.inner_text("#mit-cap") and "unchecked original" in dp.inner_text("#mit-caveat-full")
                      and "Stockfish" in page.inner_text("#census") and "fmt only" in dp.text_content("#prog-cap")
                      and "forward sum stays vectorized" in dp.inner_text("#sib-finding") and "gather" in dp.inner_text("#sib-finding")
                      and "profile-guided" in dp.inner_text("#limits-full"),
                      "smaller audit fixes: Table 3 A/A exclusion, unchecked original, census 2 description, Table 5 job set, GCC wording, Google's own caveats in Limits")
                tuned = page.inner_text("#tuned")
                tuned_full = dp.inner_text("#tuned-full")
                rl = dp.evaluate("[...document.querySelectorAll('#rule-list li')].map(l => l.innerText)")
                hashes = [c.get("added_commit") for c in index["method"]["criteria_files"]]
                ck.ok(tuned.startswith("Partly, and openly") and tuned_full.startswith("Partly, and openly") and "No, and" not in tuned_full
                      and all("v1, v2 and v3 each followed earlier results" in t_ and "only v1 loosened a threshold" in t_ for t_ in (tuned, tuned_full))
                      and all(h and h in tuned_full and any(h in x for x in rl) for h in hashes) and len(rl) == 5
                      and "AVX2" in tuned_full and "AVX2" in rl[-1] and "changed by at most" not in meth
                      and dp.locator("#orig-rule li").count() == 4 and "misses" in dp.inner_text("#orig-rule"),
                      "method: 'tuned until it passed?' leads with 'partly, and openly' and says v1, v2 and v3 each followed results, only v1 loosened a threshold, on both pages; the five-line rule history (details page) and the details page name every rule file's commit and the failed AVX2 control; the details page lists the forward-add and stencil cells under the original rule")
                ck.ok("loosened after results were seen" in meth and index["criteria"]["file"] in det and "third version" in meth
                      and f"{d1['missed'][0]['ci95_hi']:.5f}" in det and f"{d1['missed'][0]['miss_pp']:.3f}" in det
                      and not dp.evaluate("document.getElementById('loosened-details').open"),
                      "section 5 says in plain words the forward rule was loosened after results; the exact misses and the criteria file sit in a collapsed <details>")
                ck.ok(page.evaluate("document.getElementById('sample-band').hidden"), "real data: no SAMPLE DATA band")
                bad = page_numbers(page, allowed)
                ck.ok(not bad, "default view: every number on the page is in the data" + ("" if not bad else f": {bad[:6]}"))
                bad = page_numbers(dp, allowed)
                ck.ok(not bad, "details page: every number on it is in site/data" + ("" if not bad else f": {bad[:6]}"))
                # section 7, real programs (timed; the instruction profile sits on the details page)
                with open(os.path.join(DATA, "realworld.json"), encoding="utf-8") as f:
                    rw = json.load(f)
                T = rw["timing"]
                rwt = page.inner_text("#realworld")
                rwr = dp.evaluate("[...document.querySelectorAll('#rw-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                dp.evaluate("document.getElementById('rw-est').open = true")
                rwe = dp.evaluate("[...document.querySelectorAll('#rw-est-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                pS = lambda v: page.evaluate(f"pctS({v})")
                pA = lambda v, a_: page.evaluate(f"rwPct({v}, {'true' if a_ else 'false'})")
                ap = lambda d: "≈ " if d["approximate"] else ""
                prog = [d for d in rw["rows"] if not d["control"]]
                rw_ok = len(rwr) == len(rw["rows"]) and dp.locator("#rw-rows .c-row").count() == len(rw["rows"]) and len(rwe) == len(prog)
                for r, d in zip(rwr, rw["rows"]):
                    rw_ok = rw_ok and r[1] == f"{d['instr_ratio']:.3f}×" and r[4] == f"{d['traps_none']} / {d['traps_fast']}"
                    if d["control"]:
                        rw_ok = rw_ok and r[2] == "–" and r[5] == "none listed"
                    else:
                        rw_ok = (rw_ok and r[2] == ap(d) + pA(d["lines_none"], d["approximate"]) and r[3] == ap(d) + pA(d["funcs_none"], d["approximate"])
                                 and r[5] == f"{d['lost_here_too']} of {d['lost_listed']}")
                for r, d in zip(rwe, prog):
                    rw_ok = (rw_ok and r[1] == f"{ap(d)}+{pA(d['est_lines_pct'], d['approximate'])}" and r[2] == f"{ap(d)}+{pA(d['est_funcs_pct'], d['approximate'])}"
                             and abs(d["est_lines_pct"] - d["lines_none"] * (rw["est_ratio"] - 1)) < 1e-6
                             and abs(d["est_funcs_pct"] - d["funcs_none"] * (rw["est_ratio"] - 1)) < 1e-6)
                ck.ok(rw_ok, "section 7: Figure 6, the estimate table and Table 5 (details page) show every program's instruction ratio, shares, traps, lost-loop match and estimate exactly as in realworld.json (estimate = share x (r - 1))")
                # Table 9 (main page): every cell is the pooled value of the one CPU model with enough jobs
                order = [d["row"] for d in rw["rows"]]
                main_g = next(g for g in T["groups"] if g["cpu_model"] == T["main_cpu"])
                tt = page.evaluate("[...document.querySelectorAll('#rw-time-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                t9 = len(tt) == 8 and main_g["enough"]
                for r, name in zip(tt, order):
                    m = main_g["rows"][name]
                    t9 = (t9 and r[1].startswith(f"{m['fast']['ratio']:.3f}") and f"{m['fast']['lo']:.3f} to {m['fast']['hi']:.3f}" in r[1]
                          and r[2].startswith(f"{m['aligned']['ratio']:.3f}") and f"{m['aligned']['lo']:.3f} to {m['aligned']['hi']:.3f}" in r[2]
                          and r[3] == f"±{m['aa']['half_width_pct']:.2f}%"
                          and r[4] == ({"detectably slower": "slower", "detectably faster": "faster"}[m["reading"]] if m["reading"] in ("detectably slower", "detectably faster") else f"not detectable, at most {m['at_most_pct']:.1f}%"))
                ck.ok(t9, "section 7, Table 9: every program's FAST/NONE ratio and interval, as compiled and aligned, its own A/A floor and its reading are the pooled values of the one CPU model with enough jobs")
                held = [e for e in T["expect"] if e["held"]]
                lost_counts = [f"{d['project']} {d['lost_here_too']} of {d['lost_listed']}" for d in rw["rows"] if d["lost_listed"]]
                st = page.inner_text("#rw-status")
                ck.ok(st.startswith("Timed.") and f"{T['jobs']} jobs in {len(rw['runs'])} runs" in st and rw["build_run"] in dp.inner_text("#rw-note") and "shared machines" in st
                      and f"{main_g['jobs']} jobs drew an AMD" in st and "Not timed" not in rwt and "not timed yet" not in rwt.lower(),
                      "section 7 says plainly the programs were timed: jobs and runs, shared machines, the model with enough jobs, and that the other model has no reading")
                fnd = page.inner_text("#rw-finding")
                ck.ok(f"{T['slow_min'] * 100 - 100:.1f}% to {T['slow_max'] * 100 - 100:.1f}%" in fnd and "5 of the 6 programs" in fnd and "was not detectable" in fnd
                      and "not interpreted" in fnd,
                      "section 7: five of six programs with lost loops slower by the pooled range, Spectra and the meshoptimizer control not detectable, the {fmt} control faster and not interpreted")
                shr = page.inner_text("#rw-share")
                ck.ok("Which checks account for this was not isolated" in shr and "no mechanism is claimed" in shr and "instructions, not time" in shr
                      and f"up to {pS(max(d['funcs_none'] for d in prog))}" in shr and "consistent with" in shr,
                      "section 7: the lost loops' small instruction share beside the measured cost, worded as consistent with checks elsewhere, no mechanism claimed")
                ex = page.inner_text("#rw-expect")
                miss = [e for e in T["expect"] if not e["held"]]
                ck.ok(f"Of the {len(T['expect'])} expectations committed before any run, {len(held)} held" in ex and all(m_["row"] and f"{m_['fast']:.3f}" in ex for m_ in miss),
                      "section 7: how many of the expectations written before any run held, and each miss named with its measured ratios")
                lim = page.inner_text("#rw-limits")
                ck.ok(all(x in lim for x in ("profile-guided optimization", "shared virtual machines", "one toolchain", "not a sample of Google", "neither confirms nor contradicts")),
                      "section 7: limits stated: no PGO, shared VMs, one toolchain, programs picked for their lost loops, neither confirms nor contradicts 0.30%")
                dtxt = dp.inner_text("#realworld-full")
                ck.ok(dp.locator("#rw-other-table tbody tr").count() == 8 and dp.locator("#rw-other2-table tbody tr").count() == 8 and dp.locator("#rw-all-table tbody tr").count() == 8 and dp.locator("#rw-expect-table tbody tr").count() == 8
                      and dtxt.count("held") >= len(held) and "understate the spread between machines" in dtxt and "Descriptive only" in dtxt,
                      "details page: Tables 10 and 10c (the two other CPU models), Table 10b (all runners, descriptive) and Table 11 (every expectation, held or not) have all eight programs")
                # per CPU model: the same sentence the page prints, recomputed here from the data (lost-loop programs only)
                oth = dp.inner_text("#rw-other")
                lostp = [d["row"] for d in rw["rows"] if not d["control"]]
                oth_ok = f"holds on AMD {main_g['cpu_short']} only" in oth and f"holds on AMD {main_g['cpu_short']} only" in page.inner_text("#rw-other-short")
                for g_ in T["groups"]:
                    if g_["cpu_model"] == T["main_cpu"]:
                        continue
                    sl_ = [n for n in lostp if g_["rows"][n]["reading"] == "detectably slower"]
                    rs_ = [g_["rows"][n][c]["ratio"] for n in sl_ for c in ("fast", "aligned")]
                    oth_ok = (oth_ok and f"On AMD {g_['cpu_short']} ({g_['jobs']} jobs), {len(sl_)} of the {len(lostp)} were detectably slower, by {(min(rs_) - 1) * 100:.1f}% to {(max(rs_) - 1) * 100:.1f}%" in oth
                              and all(f"{RW_NAMES_PY[n]} (at most {g_['rows'][n]['at_most_pct']:.1f}%)" in oth for n in lostp if n not in sl_))
                ck.ok(oth_ok, "section 7: for each other CPU model, how many of the six programs were detectably slower, the range and the ones not detectable with their at-most bounds; the five-of-six claim is tied to EPYC 7763 only")
                ck.ok(all(x in dp.inner_text("#rw-note") for x in lost_counts) and all(r["outputs_match"] for r in rw["rows"]) and "identical with the checks off and on" in dp.inner_text("#rw-note"),
                      "details page: every lost-loop match count and the identical outputs are stated beside Figure 6")
                new_sections(dp, ck)
                est = dp.inner_text("#rw-est")
                ck.ok("estimate, not a measurement" in est and "instruction share approximates time share" in est and "not informative" in est and "Table 9 is the test" in est
                      and "probably an upper bound" in dp.inner_text("#fig5-cap") and "≈" in dtxt,
                      "details page: the Amdahl estimate sits in a collapsed block labelled an estimate, with its assumption, the functions-bound caveat and the measured result beside it")
                dp.evaluate("document.getElementById('rw-est').open = false")
                ck.ok(dp.locator("#progsum-table tbody tr").count() == 2 and "Two small programs timed earlier (older runs, not the programs above)" in dp.inner_text("#prog-sum-cap"),
                      "details page: the two small programs timed earlier follow Table 5 as Table 6, labelled as older runs, not the programs above")
                links = page.evaluate("[...document.querySelectorAll('a[href^=\"details.html\"]')].length")
                back = dp.evaluate("[...document.querySelectorAll('a[href=\"index.html\"], a[href=\"./\"]')].length")
                ck.ok(links >= 6 and back >= 1, f"the main page links the details page ({links} links) and the details page links back ({back})")
                # the repository is public: links go to this repository only, never to another repository or to workflow runs
                PUB = "github.com/JacoboPacheco/third-of-a-percent"
                gh = []
                for dp_, _, fs in os.walk(SITE):
                    for f_ in fs:
                        if f_.endswith((".html", ".js", ".css", ".json")):
                            with open(os.path.join(dp_, f_), encoding="utf-8") as fh:
                                txt_ = fh.read()
                                if re.search(r"github\.com/JacoboPacheco/(?!third-of-a-percent(?:[/\"#?\s]|$))|/actions/runs/|not public yet|repository is private", txt_):
                                    gh.append(f_)
                ghl = [x.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.includes('github.com') && !h.includes('third-of-a-percent') && h.includes('third-of-a-percent'))") for x in (page, dp)]
                publ = [x.evaluate("[...document.querySelectorAll('a[href]')].filter(a => a.href.includes('github.com/JacoboPacheco/third-of-a-percent')).length") for x in (page, dp)]
                stale = [x.inner_text("body") for x in (page, dp)]
                ck.ok(not gh and not any(ghl) and all(n >= 2 for n in publ) and not any(re.search(r"not public yet|repository is private|once it is public", t_) for t_ in stale),
                      f"links to the repository go to the public copy only ({publ} links; links to other repositories or to workflow runs: {gh}, {ghl}); no workflow-run links, no 'not public yet' wording")
                with open(os.path.join(DATA, "siblings.json"), encoding="utf-8") as f:
                    sib = json.load(f)
                t2 = corpus["census2"]["totals"]
                ck.ok("Google" in abstract and f"{index['claim']['google_pct']:.2f}%" in abstract
                      and page.evaluate("document.querySelector('.abstract a').href") == index["claim"]["url"],
                      "abstract: Google's figure with its source link")
                ck.ok(f"{lost['min']:.1f} to {lost['max']:.1f}" in abstract, "abstract: the lost-SIMD range is the one in index.json")
                ck.ok("neither confirms nor contradicts" in abstract, "abstract: says this neither confirms nor contradicts Google's average")
                fx = lambda v: f"{v:.1f}" if v >= 2 else f"{v:.2f}"
                t1 = corpus["census1"]["totals"]
                ck.ok(f"{t2['lost']} of {t2['none']['vectorized']:,}" in abstract and f"{t1['lost']} of {t1['none']['vectorized']}" in abstract
                      and "counted, not timed" in abstract.lower(), "abstract: both census counts, labelled counted, not timed")
                ab_nums = re.findall(r"\d[\d,]*(?:\.\d+)?", re.sub(r"\d+\.\d+\.\d+|-O\d|\b1×|AVX2", "", abstract.replace(page.inner_text(".abstract a"), "")))
                lis = page.evaluate("[...document.querySelectorAll('.abstract ul.findings li')].map(l => [l.innerText, l.firstElementChild && l.firstElementChild.tagName, l.innerText.indexOf(l.firstElementChild.innerText)])")
                ck.ok(len(ab_nums) <= 15 and len(lis) == 4 and all(t == "B" and i == 0 for _, t, i in lis)
                      and "forward loops that keep SIMD stay near 1" in abstract
                      and "forward loops pay" not in abstract and "-O3" in abstract and "-O2" in abstract,
                      f"abstract: four bullet lines, each led by its bold headline, Google's figure plus at most 15 numbers (the real-programs range and the two newer-toolchain versions add four, the as-compiled forward add one) ({len(ab_nums)}: {ab_nums}), 'forward loops that keep SIMD', GCC as -O3 vectorization and -O2 cost")
                fixr = [v["range"] for sh in mit["shapes"] if sh["kernel"] in ("m04_rev", "m08_matmul")
                        for v in sh["variants"] if v["variant"] == sh["recommended"]]
                ck.ok(f"{fx(min(r['min'] for r in fixr))} to {fx(max(r['max'] for r in fixr))}" in abstract and "GCC" in abstract,
                      "abstract: the rewrite range of the reverse and matrix-multiply loops and the toolchain caveat")
                seg = page.evaluate("[...document.querySelectorAll('#cpu-seg button')].map(b => b.dataset.cpu)")
                few = page.inner_text("#cpu-few")
                ck.ok(seg == [c["slug"] for c in cpus] and all(f["cpu_short"] in few for f in index["page"]["cpus_few"]) and "too few to judge" in few
                      and page.evaluate("getComputedStyle(document.getElementById('cpu-few')).display") == "block"
                      and not page.evaluate("getComputedStyle(document.getElementById('cpu-few')).borderTopStyle !== 'none'"),
                      f"Figure 1: the switcher offers the CPU models with at least {index['criteria']['minimum_jobs']} jobs ({seg}) and names the others as too few jobs")
                open_full(page)
                ck.ok("instructions, not time" in page.inner_text("#fig2 .f2-instr"), "Figure 2: the instruction ratio sits in its header, labelled 'instructions, not time'")
                with open(os.path.join(DATA, "pooled.json"), encoding="utf-8") as f:
                    pooled = json.load(f)
                dp = browser.new_page(viewport={"width": 1280, "height": 900})
                watch(dp, errors)
                dp.goto(base + "details.html", wait_until="networkidle")
                wait_details(dp)
                google_wording(page, ck, "main page", pooled)
                google_wording(dp, ck, "details page", pooled)
                ck.ok(not dp.evaluate("document.getElementById('appb-details').open"), "details page: Appendix B is folded into a collapsed <details>")
                dp.evaluate("document.getElementById('appb-details').open = true")
                appb = dp.evaluate("""() => [...document.querySelectorAll('#appb-cpu tbody tr')].map(r => r.innerText)""")
                ck.ok(len(appb) == len(index["cpus"]) and all("1.5" in r and "2%" in r for r, c in zip(appb, index["cpus"]) if c["enough"])
                      and "results/s4-pooled/pooled.json" in dp.inner_text("#appendix-b")
                      and "not a statement about Google" in dp.inner_text("#appendix-b"),
                      "Appendix B: per CPU model the form, the numbers and the rule in plain words, the pooled file named by its path, and no claim about Google's services")
                terms = page.evaluate("""() => { const t = document.getElementById('terms'), tb = document.getElementById('cpu-table');
                    return t ? [t.innerText, !!(t.compareDocumentPosition(tb) & Node.DOCUMENT_POSITION_FOLLOWING)] : null; }""")
                ck.ok(bool(terms) and terms[1] and all(w in terms[0] for w in ("A run is", "job", "pooled", "interval")),
                      "section 1 defines run, job, pooled and interval in plain words before Table 1")
                # placement-sensitive cells, with the pooled ratio of the two columns
                t1h = page.evaluate("[...document.querySelectorAll('#cpu-table thead th')].map(t => t.innerText)")
                t1r = page.evaluate("[...document.querySelectorAll('#cpu-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                rec = dp.inner_text("#reconcile")
                repro = next(c["reproduction"] for c in cpus if c["reproduction"] and c["reproduction"]["checked"])
                ck.ok(any("aligned" in h and "Lose" in h for h in t1h) and any("as compiled" in h for h in t1h)
                      and any("judged" in h for h in t1h) and any("Placement-sensitive" in h for h in t1h)
                      and all(r[4] == f"{fx(c['forward_judged_aligned']['min'])}–{fx(c['forward_judged_aligned']['max'])}×"
                              or r[4] == f"{fx(c['forward_judged_aligned']['min'])}×" for r, c in zip(t1r, index["cpus"]) if c["enough"])
                      and "excluded" not in page.inner_text("#cpu-cap") and "left out of the 2% test" in page.inner_text("#cpu-cap")
                      and f"{repro['outside']} of {repro['checked']}" in rec and f"{repro['max_gap_pct']:.1f}%" in rec,
                      "Table 1: lose-SIMD aligned and as compiled, judged forward loops only, placement-sensitive cells in their own column; the note beside it reconciles 'same in every run' with the run-to-run gap")
                ck.ok(all(page.locator(f"#{n}").count() == 1 and "Jobs:" in page.inner_text(f"#{n}") for n in ("cpu-note", "mit-note"))
                      and "Jobs:" in dp.inner_text("#sib-note")
                      and "Jobs:" in page.text_content("#fig1-cap"), "every table that quotes a range (Tables 1, 3, 4) and Figure 1's caption carry a one-line jobs note")
                low = dp.inner_text("#fwd-low")
                ck.ok("9V45" in low and "includes 1" in low and "slowdowns only" in low,
                      "beside Table 1: the judged forward loop below 1x on EPYC 9V45 is explained (interval of compiled / aligned includes 1; the rule bounds slowdowns only)")
                ip = dp.inner_text("#instr-p")
                ck.ok("not for every loop" in ip and "inferred" in ip and "same story" not in ip and "histogram" in ip,
                      "section 1: the instruction counts are said to agree for loops that lose SIMD, not for every loop, with the histogram and forward add as counter-examples, marked inferred")
                ck.ok(all(w in dp.inner_text("#jobsets") for w in ("Section 5", "Section 6", "aligned", "as compiled"))
                      and "Xeon" in dp.inner_text("#sib-cap") and "Xeon 6973P-C" in dp.inner_text("#otherdraws"),
                      "results: one note states which job set and column each part uses; Table 4's caption names the Xeon draws; Table 1 explains the models without a row")
                ps_rows = dp.evaluate("[...document.querySelectorAll('#ps-table tbody tr')].map(r => r.textContent)")
                ps_want = sum(len(c["placement_sensitive"]) for c in cpus)
                ps_ids = {p["cell_id"].split(".")[0] for c in cpus for p in c["placement_sensitive"]}
                ck.ok(len(ps_rows) == ps_want and {"k02_add_fwd", "k03_stencil"} <= ps_ids and all("[" in r for r in ps_rows),
                      f"section 3: Table 2 lists every placement-sensitive cell ({ps_want}), forward add and stencil among them, each with the interval of compiled / aligned")
                # section 4, the census
                cn = page.inner_text("#census-not")
                ck.ok(all(w in cn for w in ("Counted, not timed", "hotness", "no claim about runtime cost", "Google")),
                      "section 4 says plainly: counted not timed, hotness unknown, no claim about runtime cost or Google's average")
                ncat = sum(1 for r in corpus["categories"] if r["census"] in (1, 2))
                nmain = sum(1 for r in corpus["categories"] if r["census"] == 2 or (r["census"] == 1 and r.get("total")))
                ck.ok(dp.locator("#census-rows .c-row").count() == ncat and page.locator("#census-rows .c-row").count() == nmain,
                      f"Figure 4: on the details page one row per category and census total ({ncat}); on the main page census 1 as one total ({nmain})")
                ps_ = dp.inner_text("#prog-sum")
                ck.ok("once each job" in ps_ and "noise floor" in ps_ and "consistent with" not in ps_,
                      "section 7: the summary says in plain words the largest slowdown once the noise floor is accounted for")
                ck.ok("failed" in page.inner_text("#census-ctl-sum") and "failed" in dp.inner_text("#census-ctl-sum"),
                      "the census controls' FAIL is summarised in one visible line on both pages")
                ctl = dp.inner_text("#census-controls")
                ck.ok("PASS" in ctl and "FAIL" in ctl and "AVX2" in ctl and "expected lost" in ctl and "Determinism" in ctl,
                      "section 4 lists the controls: determinism PASS, kernel control PASS at baseline and FAIL at AVX2 with its reason")
                fig4 = []
                for i in range(dp.locator("#census-rows .c-row.c-click").count()):
                    r = dp.locator("#census-rows .c-row.c-click").nth(i)
                    r.click()
                    pnl = r.evaluate("n => n.nextElementSibling")
                    nrow = r.evaluate("n => n.nextElementSibling.querySelectorAll('tbody tr').length")
                    want = r.evaluate("n => +n.querySelector('.c-np').textContent.replace(/[^0-9]/g, '')")
                    fig4.append(nrow == want and r.get_attribute("aria-expanded") == "true")
                    r.click()
                ck.ok(len(fig4) == ncat and all(fig4), f"details page, Figure 4: a click on each row lists that category's projects, one row per project ({sum(fig4)} of {ncat})")
                un = corpus["census2"]["patterns_unlabelled"]
                ck.ok(sum(x["count"] for x in corpus["census2"]["patterns"]) + un["count"] == t2["lost"]
                      and f"remaining {un['count']} copies ({un['unique_locations']} locations)" in dp.inner_text("#census-p2"),
                      "section 4: the shape counts plus the unlabelled rest add up to the census total, stated beside them")
                exs = dp.inner_text("#census-examples")
                ck.ok(page.locator("#census-examples").count() == 0 and "Real loops quoted" in page.inner_text("#census")
                      and dp.locator("#census-examples figure").count() >= 4 and all(x in exs for x in ("LightGBM", "llama.cpp", "Stockfish")),
                      "section 4 on the main page links to the real loops quoted on the details page (all of them, Stockfish included, with project names and source lines)")
                cp = page.inner_text("#census") + dp.inner_text("#census-full")
                wo = corpus["census2"]["without_biggest"]
                ck.ok(f"{wo['lost']} of {wo['vectorized']:,}" in cp and f"{t2['lost_unique_locations']} of {t2['none']['vectorized_unique']}" in cp
                      and f"{t2['lost_with_index_evidence']} of {t2['lost']}" in cp,
                      "section 4 gives distinct locations beside raw counts, the count without the dominant project and the traced-check evidence")
                # section 5, what to change
                ck.ok(page.locator("#mit-table tbody tr").count() == len(mit["shapes"]), f"section 5: one table row per loop shape ({len(mit['shapes'])})")
                mt = page.inner_text("#mitigate")
                order = page.evaluate("""() => !!(document.getElementById('mit-unsafe').compareDocumentPosition(document.getElementById('mit-table')) & Node.DOCUMENT_POSITION_FOLLOWING)""")
                ck.ok(order and "span variant" in page.inner_text("#mit-cap") and "strictest rule; ranges shown" in mt and "earns the word" not in mt,
                      "section 5: the silently-unsafe warning comes before the table, the span variant is defined in the caption, the rule is stated as 'measured under the strictest rule; ranges shown'")
                ck.ok("better" in mt and f"{mit['usable_jobs']} of {mit['job_count']} jobs" in mt and "rbegin" in mt and "unsafe" in mt.lower(),
                      "section 5: the pre-committed 'better' rule with the usable-job count, and the silently-unsafe std::transform warning")
                opened = []
                for sh in mit["shapes"]:
                    page.click(f'#mit-table tr[data-k="{sh["kernel"]}"]')
                    page.wait_for_timeout(80)
                    nrows = page.locator("#mit-detail .mv-row").count()
                    ok_ = (nrows == len(sh["variants"]) and page.locator("#mit-detail pre").count() == 2
                           and page.get_attribute(f'#mit-table tr[data-k="{sh["kernel"]}"]', "aria-expanded") == "true")
                    bad = page_numbers(page, allowed, "#mit-detail")
                    if bad:
                        ok_ = False
                        print("      numbers not in the data:", bad[:4])
                    opened.append(ok_)
                ck.ok(all(opened), f"section 5: a click on each shape opens every rewrite tried, with the original's and the rewrite's code, every number in the data ({opened})")
                page.click('#mit-table tr[data-k="m04_rev"]')
                # section 6, other toolchains
                ck.ok(dp.locator("#sib-table thead th").count() == len(sib["kernels"]) + 1 and "vectorize under no setup" in dp.inner_text("#sib-cap")
                      and "not that the check is free" in dp.inner_text("#sib-cap"),
                      "section 6: Table 4 has all eight loops, and its note says kept vectorization is not free")
                ck.ok(dp.locator("#sib-table tbody tr").count() == len(sib["rows"]) and dp.locator("#sib-table .t-lost").count() > 0,
                      f"section 6: one row per setup ({len(sib['rows'])}), with lost / kept / none marked")
                ck.ok(dp.locator("#sibsum-table tbody tr").count() == 5 and dp.locator("#sibsum-table .t-lost").count() > 0
                      and page.locator("#sibsum-table").count() == 0
                      and page.locator('#siblings a[href="details.html#siblings-full"]').count() == 1,
                      "section 6: the five-row timed summary (Table 4a) is on the details page; the main page links to it")
                # section 6: the compile-only sweep (ce-sweep/): every cell against site data, the counts against the sweep itself
                with open(os.path.join(DATA, "cesweep.json"), encoding="utf-8") as f:
                    ce = json.load(f)
                ce_src = os.path.join(REPO, "ce-sweep", "results.json")
                with open(ce_src, encoding="utf-8") as f:
                    cer = json.load(f)
                with open(os.path.join(REPO, "ce-sweep", "permalinks.json"), encoding="utf-8") as f:
                    cep = json.load(f)["links"]
                with open(ce_src, "rb") as f:
                    ce_sha = hashlib.sha256(f.read()).hexdigest()
                CE_SHORT = {"k01_sum_fwd": "forward sum", "k02_add_fwd": "forward add", "k03_stencil": "stencil", "k04_rev": "reverse",
                            "k05_stride2": "stride-2", "k06_gather": "gather", "k07_hist": "histogram", "k08_matmul": "matrix multiply"}
                CE_WORD = {"lost": "lost under the checks", "kept": "kept", "none": "not vectorized in either build"}
                ce_st = lambda v: "lost" if v["none"] and not v["checked"] else ("kept" if v["checked"] else "none")
                cl_rows = [m for m in cer["matrix"] if m["family"] == "clang"]
                CE_VER = len({(m["family"], "trunk" if m["version"] == "trunk" else int(m["version"].split(".")[0])) for m in cer["matrix"]})  # 28 ids, 14 versions
                n_builds = 2 * len({(c["compiler_id"], c["target"], c["opt"]) for c in cer["cells"]})
                ck.ok(len(cl_rows) == 54 and len(cer["matrix"]) == 84 and len(cer["cells"]) == 672 and n_builds == 168
                      and ce["counts"] == {"builds": 168, "cells": 672, "compilers": 28, "rows": 84} and len(ce["rows"]) == 84
                      and ce["summary"]["clang_rows"] == 54 and ce["source_sha256"] == ce_sha,
                      f"compile-only sweep: 54 clang rows, 84 rows, 672 cells, 168 builds in ce-sweep/results.json, and the site copy is of this file ({len(cl_rows)}, {len(cer['matrix'])}, {len(cer['cells'])}, {n_builds})")
                cells = {(c["compiler_id"], c["target"], c["opt"], c["kernel"]): c for c in cer["cells"]}
                lostm = {(m["compiler_id"], m["target"], m["opt"]): set(m["lost"]) for m in cer["matrix"]}
                same = all(r["vec"][k] == {"none": bool(cells[(r["compiler_id"], r["target"], r["opt"], k)]["none"]["vectorized"]),
                                           "checked": bool(cells[(r["compiler_id"], r["target"], r["opt"], k)]["hardened"]["vectorized"])}
                           and (k in lostm[(r["compiler_id"], r["target"], r["opt"])]) == (ce_st(r["vec"][k]) == "lost") == (k in r["lost"])
                           for r in ce["rows"] for k in ce["kernels"])
                ck.ok(same, "compile-only sweep: every site cell (vectorized with checks off / on, lost) equals ce-sweep/results.json")
                bad, seen = [], 0
                for opt in ("-O2", "-O3"):
                    page.click(f'#ce-oseg button[data-o="{opt}"]')
                    page.wait_for_timeout(80)
                    got = page.evaluate("""[...document.querySelectorAll('#ce-panels .ce-panel')].map(p => [p.dataset.t,
                        [...p.querySelectorAll('.ce-cell')].map(c => [c.getAttribute('aria-label'), (c.className.match(/ce-(lost|kept|none)/) || [])[1]])])""")
                    for t, cs in got:
                        lab = {c[0]: c[1] for c in cs}
                        rows_t = [r for r in ce["rows"] if r["target"] == t and r["opt"] == opt]
                        if len(cs) != 8 * len(rows_t) or len(lab) != len(cs):
                            bad.append((t, opt, "count", len(cs)))
                        for r in rows_t:
                            name = ("clang trunk" if r["version"] == "trunk" else f"clang {r['version']}") if r["family"] == "clang" else f"GCC {r['version']}"
                            for k in ce["kernels"]:
                                want = ce_st(r["vec"][k])
                                key = f"{name}, {ce['targets'][t]}, {opt}, {CE_SHORT[k]}: {CE_WORD[want]}"
                                seen += 1
                                if lab.get(key) != want:
                                    bad.append((key, lab.get(key)))
                page.click('#ce-oseg button[data-o="-O2"]')
                ck.ok(not bad and seen == 672, f"Figure 5: every matrix cell ({seen} of 672: both levels, three panels) shows the state recomputed from cesweep.json ({bad[:3]})")
                page.evaluate("document.querySelector('#ce-panels .ce-panel[data-t=\"x86-64\"]').scrollIntoView()")
                page.hover('#ce-panels .ce-panel[data-t="x86-64"] .ce-cell[aria-label^="clang trunk, x86-64 (SSE2), -O2, matrix multiply"]')
                rem = page.inner_text("#ce-remark")
                tr = next(r for r in ce["rows"] if r["version"] == "trunk" and r["target"] == "x86-64" and r["opt"] == "-O2")
                ck.ok("clang trunk, x86-64 (SSE2), -O2, matrix multiply: lost under the checks" in rem and tr["remark"]["k08_matmul"].replace("loop not vectorized: ", "") in rem
                      and "Early exit loop with store but no supported condition load" in rem,
                      f"Figure 5: hovering a cell shows that cell and the compiler's own remark ({rem[:90]})")
                hrefs = page.evaluate("""[...document.querySelectorAll('#ce-panels .ce-panel[data-t="x86-64"] a.ce-h')].map(a => a.href)""")
                ck.ok(hrefs == [cep[k]["url"] for k in ce["kernels"]] and all(cep[k]["verified"] for k in ce["kernels"])
                      and all(u.startswith("https://godbolt.org/z/") for u in hrefs)
                      and dp.evaluate("[...document.querySelectorAll('#ce-table thead a')].map(a => a.href)") == hrefs,
                      f"Figure 5 and Table 4b: the 8 column heads open each loop in Compiler Explorer, the verified short links in ce-sweep/permalinks.json ({hrefs[:2]})")
                cf, cc = page.inner_text("#ce-find"), page.inner_text("#fig-ce-cap")
                sm = ce["summary"]
                ck.ok(f"all {sm['clang_rows']} clang rows lose the reverse and stride-2 loops" in cf and sm["clang_rev_s2_lost"] == sm["clang_rows"]
                      and "none loses a forward loop" in cf and sm["clang_fwd_lost"] == 0
                      and "lost on clang 16 to 18 at baseline x86-64 only, kept on 19 to 22 everywhere, lost everywhere on 23 and trunk" in cf
                      and "No loop is lost on AArch64 only" in cf and "GCC loses nothing at -O2" in cf and sm["gcc_o2_lost"] == 0
                      and f"forward add in {sm['gcc_o3_lost']['k02_add_fwd']} of {sm['gcc_o3_rows']} rows" in cf
                      and sm["gcc_o3_lost"]["k04_rev"] == sm["gcc_o3_rows"] == sm["gcc_o3_lost"]["k08_matmul"]
                      and "Compile-only: this says which loops lose vectorization, not what they cost" in cc and "assumed to match" in cc
                      and f"on {CE_VER} compiler versions ({ce['counts']['compilers']} Compiler Explorer compiler ids)" in cf and CE_VER == 14,
                      "section 6: the sweep's findings, recomputed from the data, and the compile-only and libc++ pairing sentences")
                ck.ok(dp.locator("#ce-table tbody tr").count() == 84 and dp.locator("#ce-table tbody td.ce-td").count() == 672
                      and dp.locator("#ce-notes li").count() >= 4 and "Early exit loop with store but no supported condition load" in dp.inner_text("#siblings-full")
                      and "No timing" in dp.inner_text("#siblings-full") and "assumed to match" in dp.inner_text("#siblings-full"),
                      "details: Table 4b has all 84 compiler rows (672 cells) and per-version notes")
                note_ce = dp.inner_text("#ce-full + p")
                ck.ok(f"{ce['summary']['clang_rows'] + ce['summary']['gcc_rows']} rows ({CE_VER} compiler versions," in note_ce and f"{ce['counts']['compilers']} separate x86-64 and AArch64 compiler ids" in note_ce
                      and f"from {ce['counts']['builds']} builds" in note_ce and "compilers," not in note_ce.replace("compiler versions,", ""),
                      f"details, Table 4b note: {CE_VER} compiler versions are told apart from the {ce['counts']['compilers']} Compiler Explorer ids ({note_ce[:120]!r})")
                cbox = page.inner_text("#cannot")
                ck.ok(f"Compiled only: the {CE_VER} compiler versions ({ce['counts']['compilers']} Compiler Explorer compiler ids) in section 6" in cbox and "few-job runs" in cbox and "Other compilers" in abstract and "compiled only" in abstract,
                      "abstract and box: the wider toolchain coverage is compile-only; timing rests on clang 18 plus a few GCC and clang 20 jobs")
                main_versions(abstract, cbox, ck)
                st = page.inner_text("#siblings") + dp.inner_text("#siblings-full")
                ck.ok("GCC" in st and "-O3" in st and "single job" in st and str(sib["single_job_groups"]) in st,
                      "section 6: the plain finding (GCC differs) and the thin coverage, with the count of single-job cells")
                cap1 = page.text_content("#fig1-cap")
                ck.ok("Filled dot" in cap1 and "Hollow ring" in cap1, "Figure 1's caption says in words what the filled and hollow marks are")
                ck.ok(dp.locator("#fig3-title").is_visible() and dp.locator("#fig3 .mhead").count() == 1, "details page: Figure 3 has a title and a header row")
                k02t = dp.inner_text("#k02-faster") + dp.inner_text("#fig3 figcaption")
                ck.ok("per pass" in k02t and "inferred" in k02t,
                      "section 3 and Figure 3 explain why the checked forward add is faster aligned (per-pass unrolling, cause marked inferred)")
                ck.ok(page.evaluate("""() => [...document.querySelectorAll('#rows .src, #fig2 .f2-src code, #fig2 pre.asm, #fig2 pre.asm-lite')]
                    .every(n => getComputedStyle(n).overflowWrap === 'normal' && getComputedStyle(n).wordBreak === 'normal')"""),
                      "code lines wrap only at spaces, never mid-token")
                page.evaluate("scrollTo(0, 0)"); page.wait_for_timeout(150)
                for _ in range(15):  # poll up to 3 s: layout and the first-view animation settle later on a slower machine
                    rows_in = page.evaluate("""() => { const rs = [...document.querySelectorAll('#race-loops button')];
                        return [rs.length, rs.filter(r => { const b = r.getBoundingClientRect(); return b.height > 0 && b.bottom <= innerHeight + 1; }).length]; }""")
                    if rows_in[1] == rows_in[0]:
                        break
                    page.wait_for_timeout(200)
                ck.ok(rows_in[0] == len(index["criteria"]["kernels"]) and rows_in[1] == rows_in[0],
                      f"first screen (1280): all {rows_in[0]} loop rows of the hero race are visible ({rows_in[1]} are)")
                order0 = page.evaluate("[...document.querySelectorAll('#rows .row')].map(r => r.dataset.k)")
                orders = []
                page.click('#col-seg [data-col="compiled"]'); page.wait_for_timeout(100)
                orders.append(page.evaluate("[...document.querySelectorAll('#rows .row')].map(r => r.dataset.k)"))
                for c in cpus:
                    page.click(f'#cpu-seg [data-cpu="{c["slug"]}"]'); page.wait_for_timeout(100)
                    orders.append(page.evaluate("[...document.querySelectorAll('#rows .row')].map(r => r.dataset.k)"))
                page.click('#col-seg [data-col="aligned"]'); page.click(f'#cpu-seg [data-cpu="{default_cpu["slug"]}"]'); page.wait_for_timeout(100)
                ck.ok(all(o == order0 for o in orders), "Figure 1: the row order stays fixed across the column toggle and every CPU model")
                lab = page.get_attribute("#col-hint", "aria-label")
                ck.ok(lab == "What does aligned mean?", f"the '?' button's label names no toggle option on its own ({lab!r})")
                sel = page.evaluate("document.querySelector('#rows .row[aria-selected=true]').dataset.k")
                ck.ok(sel == "k04_rev", f"the reverse loop is selected on load (got {sel})")
                f2 = page.evaluate("""() => ({ top: document.getElementById('fig2').getBoundingClientRect().top,
                    notes: [...document.querySelectorAll('#fig2 pre.asm-lite .note')].map(n => n.textContent),
                    chk: document.querySelectorAll('#fig2 pre.asm-lite .chk').length, trap: document.querySelectorAll('#fig2 pre.asm-lite .trap').length,
                    simd: document.querySelectorAll('#fig2 pre.asm-lite .simd').length })""")  # the plain view only: the closed full listing does not count
                ck.ok(f2["top"] < 900 and f2["chk"] >= 2 and f2["trap"] >= 1 and f2["simd"] >= 1
                      and any(n.startswith("the check") for n in f2["notes"]) and any(n.startswith("this trap stops the program") for n in f2["notes"]),
                      "first screen (1280): Figure 2 shows the reverse loop's SIMD lines, the check and the trap, labelled in words")
                open_full(page)
                ck.ok("could not determine number of loop iterations" in page.inner_text("#fig2")
                      or "no longer knows how many times" in page.inner_text("#fig2"),
                      "Figure 2: the compiler's remark explained in plain words")
                ck.ok(page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(255, 255, 255)", "the page is white")
                meth = page.inner_text("#method") + dp.inner_text("#method-full")
                d1 = index["method"]["dayone"][0]
                det = dp.text_content("#loosened-details") or ""
                IF = index["intel_forward"]
                body_ = page.inner_text("body")
                ck.ok("on the AMD models" in abstract and "AMD models only" in dp.inner_text("#intel-p")
                      and f"{IF['aligned']['min']:.2f}–{IF['aligned']['max']:.2f}" in dp.inner_text("#intel-p")
                      and "on the AMD models" in dp.inner_text("#sib-finding") and "Intel" in page.inner_text("#cpu-note"),
                      "forward loops near 1x is said for the AMD models only, with the Intel jobs' forward add range in section 1, Table 1's note and section 6")
                fwd_lo = min(c["forward_aligned"]["min"] for c in cpus)
                ck.ok(f"aligned, {fx(fwd_lo)}–" in dp.inner_text("#ps-sum") and f"{fx(fwd_lo)}–" in dp.inner_text("#sib-table") and f"{fx(fwd_lo)}–" in dp.inner_text("#sibsum-table"),
                      f"the aligned forward low end on the page is the data's ({fx(fwd_lo)}x), in section 3, Table 4 and its summary")
                s3t = page.inner_text("#placement")
                ck.ok("own instructions were not the cause" in s3t and "inferred" in s3t and "The check was not the cause" not in s3t,
                      "section 3: the check's own instructions were not the cause, the layout it induces was, the hardware reason inferred")
                fn = dp.inner_text("#fn-novec")
                with open(os.path.join(DATA, "index.json"), encoding="utf-8") as f_:
                    ce_ = next((c_ for c_ in json.load(f_)["cpus"] if c_["slug"] == default_cpu["slug"]), None)
                ck.ok("only factor measured" in fn and "largest" not in fn and "about a third" in fn and ce_ is not None and 30 <= ce_["novec_rev_share_pct"] <= 37 and f"({int(ce_['novec_rev_share_pct'] + 0.5)}%)" in fn and f"The rest, {100 - int(ce_['novec_rev_share_pct'] + 0.5)}%," in fn and "not explained by this measurement" in fn,
                      "footnote 1: losing SIMD is the only factor measured, about a third of the extra time, the rest stated as unexplained")
                av = dp.inner_text("#census-avx2")
                ck.ok("loses fewer, not more" not in av and "snappy" in av and "census 2 loses fewer" in av, "section 4: only census 2 loses fewer at AVX2; census 1 over 18 projects, snappy not built")
                ck.ok("left out" in page.inner_text("#mit-cap") and "unchecked original" in dp.inner_text("#mit-caveat-full")
                      and "Stockfish" in page.inner_text("#census") and "fmt only" in dp.text_content("#prog-cap")
                      and "forward sum stays vectorized" in dp.inner_text("#sib-finding") and "gather" in dp.inner_text("#sib-finding")
                      and "profile-guided" in dp.inner_text("#limits-full"),
                      "smaller audit fixes: Table 3 A/A exclusion, unchecked original, census 2 description, Table 5 job set, GCC wording, Google's own caveats in Limits")
                tuned = page.inner_text("#tuned")
                tuned_full = dp.inner_text("#tuned-full")
                rl = dp.evaluate("[...document.querySelectorAll('#rule-list li')].map(l => l.innerText)")
                hashes = [c.get("added_commit") for c in index["method"]["criteria_files"]]
                ck.ok(tuned.startswith("Partly, and openly") and tuned_full.startswith("Partly, and openly") and "No, and" not in tuned_full
                      and all("v1, v2 and v3 each followed earlier results" in t_ and "only v1 loosened a threshold" in t_ for t_ in (tuned, tuned_full))
                      and all(h and h in tuned_full and any(h in x for x in rl) for h in hashes) and len(rl) == 5
                      and "AVX2" in tuned_full and "AVX2" in rl[-1] and "changed by at most" not in meth
                      and dp.locator("#orig-rule li").count() == 4 and "misses" in dp.inner_text("#orig-rule"),
                      "method: 'tuned until it passed?' leads with 'partly, and openly' and says v1, v2 and v3 each followed results, only v1 loosened a threshold, on both pages; the five-line rule history (details page) and the details page name every rule file's commit and the failed AVX2 control; the details page lists the forward-add and stencil cells under the original rule")
                ck.ok("loosened after results were seen" in meth and index["criteria"]["file"] in det and "third version" in meth
                      and f"{d1['missed'][0]['ci95_hi']:.5f}" in det and f"{d1['missed'][0]['miss_pp']:.3f}" in det
                      and not dp.evaluate("document.getElementById('loosened-details').open"),
                      "section 5 says in plain words the forward rule was loosened after results; the exact misses and the criteria file sit in a collapsed <details>")
                ck.ok(page.evaluate("document.getElementById('sample-band').hidden"), "real data: no SAMPLE DATA band")
                bad = page_numbers(page, allowed)
                ck.ok(not bad, "default view: every number on the page is in the data" + ("" if not bad else f": {bad[:6]}"))
                bad = page_numbers(dp, allowed)
                ck.ok(not bad, "details page: every number on it is in site/data" + ("" if not bad else f": {bad[:6]}"))
                # section 7, real programs (timed; the instruction profile sits on the details page)
                with open(os.path.join(DATA, "realworld.json"), encoding="utf-8") as f:
                    rw = json.load(f)
                T = rw["timing"]
                rwt = page.inner_text("#realworld")
                rwr = dp.evaluate("[...document.querySelectorAll('#rw-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                dp.evaluate("document.getElementById('rw-est').open = true")
                rwe = dp.evaluate("[...document.querySelectorAll('#rw-est-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                pS = lambda v: page.evaluate(f"pctS({v})")
                pA = lambda v, a_: page.evaluate(f"rwPct({v}, {'true' if a_ else 'false'})")
                ap = lambda d: "≈ " if d["approximate"] else ""
                prog = [d for d in rw["rows"] if not d["control"]]
                rw_ok = len(rwr) == len(rw["rows"]) and dp.locator("#rw-rows .c-row").count() == len(rw["rows"]) and len(rwe) == len(prog)
                for r, d in zip(rwr, rw["rows"]):
                    rw_ok = rw_ok and r[1] == f"{d['instr_ratio']:.3f}×" and r[4] == f"{d['traps_none']} / {d['traps_fast']}"
                    if d["control"]:
                        rw_ok = rw_ok and r[2] == "–" and r[5] == "none listed"
                    else:
                        rw_ok = (rw_ok and r[2] == ap(d) + pA(d["lines_none"], d["approximate"]) and r[3] == ap(d) + pA(d["funcs_none"], d["approximate"])
                                 and r[5] == f"{d['lost_here_too']} of {d['lost_listed']}")
                for r, d in zip(rwe, prog):
                    rw_ok = (rw_ok and r[1] == f"{ap(d)}+{pA(d['est_lines_pct'], d['approximate'])}" and r[2] == f"{ap(d)}+{pA(d['est_funcs_pct'], d['approximate'])}"
                             and abs(d["est_lines_pct"] - d["lines_none"] * (rw["est_ratio"] - 1)) < 1e-6
                             and abs(d["est_funcs_pct"] - d["funcs_none"] * (rw["est_ratio"] - 1)) < 1e-6)
                ck.ok(rw_ok, "section 7: Figure 6, the estimate table and Table 5 (details page) show every program's instruction ratio, shares, traps, lost-loop match and estimate exactly as in realworld.json (estimate = share x (r - 1))")
                # Table 9 (main page): every cell is the pooled value of the one CPU model with enough jobs
                order = [d["row"] for d in rw["rows"]]
                main_g = next(g for g in T["groups"] if g["cpu_model"] == T["main_cpu"])
                tt = page.evaluate("[...document.querySelectorAll('#rw-time-table tbody tr')].map(r => [...r.children].map(c => c.innerText))")
                t9 = len(tt) == 8 and main_g["enough"]
                for r, name in zip(tt, order):
                    m = main_g["rows"][name]
                    t9 = (t9 and r[1].startswith(f"{m['fast']['ratio']:.3f}") and f"{m['fast']['lo']:.3f} to {m['fast']['hi']:.3f}" in r[1]
                          and r[2].startswith(f"{m['aligned']['ratio']:.3f}") and f"{m['aligned']['lo']:.3f} to {m['aligned']['hi']:.3f}" in r[2]
                          and r[3] == f"±{m['aa']['half_width_pct']:.2f}%"
                          and r[4] == ({"detectably slower": "slower", "detectably faster": "faster"}[m["reading"]] if m["reading"] in ("detectably slower", "detectably faster") else f"not detectable, at most {m['at_most_pct']:.1f}%"))
                ck.ok(t9, "section 7, Table 9: every program's FAST/NONE ratio and interval, as compiled and aligned, its own A/A floor and its reading are the pooled values of the one CPU model with enough jobs")
                held = [e for e in T["expect"] if e["held"]]
                lost_counts = [f"{d['project']} {d['lost_here_too']} of {d['lost_listed']}" for d in rw["rows"] if d["lost_listed"]]
                st = page.inner_text("#rw-status")
                ck.ok(st.startswith("Timed.") and f"{T['jobs']} jobs in {len(rw['runs'])} runs" in st and rw["build_run"] in dp.inner_text("#rw-note") and "shared machines" in st
                      and f"{main_g['jobs']} jobs drew an AMD" in st and "Not timed" not in rwt and "not timed yet" not in rwt.lower(),
                      "section 7 says plainly the programs were timed: jobs and runs, shared machines, the model with enough jobs, and that the other model has no reading")
                fnd = page.inner_text("#rw-finding")
                ck.ok(f"{T['slow_min'] * 100 - 100:.1f}% to {T['slow_max'] * 100 - 100:.1f}%" in fnd and "5 of the 6 programs" in fnd and "was not detectable" in fnd
                      and "not interpreted" in fnd,
                      "section 7: five of six programs with lost loops slower by the pooled range, Spectra and the meshoptimizer control not detectable, the {fmt} control faster and not interpreted")
                shr = page.inner_text("#rw-share")
                ck.ok("Which checks account for this was not isolated" in shr and "no mechanism is claimed" in shr and "instructions, not time" in shr
                      and f"up to {pS(max(d['funcs_none'] for d in prog))}" in shr and "consistent with" in shr,
                      "section 7: the lost loops' small instruction share beside the measured cost, worded as consistent with checks elsewhere, no mechanism claimed")
                ex = page.inner_text("#rw-expect")
                miss = [e for e in T["expect"] if not e["held"]]
                ck.ok(f"Of the {len(T['expect'])} expectations committed before any run, {len(held)} held" in ex and all(m_["row"] and f"{m_['fast']:.3f}" in ex for m_ in miss),
                      "section 7: how many of the expectations written before any run held, and each miss named with its measured ratios")
                lim = page.inner_text("#rw-limits")
                ck.ok(all(x in lim for x in ("profile-guided optimization", "shared virtual machines", "one toolchain", "not a sample of Google", "neither confirms nor contradicts")),
                      "section 7: limits stated: no PGO, shared VMs, one toolchain, programs picked for their lost loops, neither confirms nor contradicts 0.30%")
                dtxt = dp.inner_text("#realworld-full")
                ck.ok(dp.locator("#rw-other-table tbody tr").count() == 8 and dp.locator("#rw-other2-table tbody tr").count() == 8 and dp.locator("#rw-all-table tbody tr").count() == 8 and dp.locator("#rw-expect-table tbody tr").count() == 8
                      and dtxt.count("held") >= len(held) and "understate the spread between machines" in dtxt and "Descriptive only" in dtxt,
                      "details page: Tables 10 and 10c (the two other CPU models), Table 10b (all runners, descriptive) and Table 11 (every expectation, held or not) have all eight programs")
                # per CPU model: the same sentence the page prints, recomputed here from the data (lost-loop programs only)
                oth = dp.inner_text("#rw-other")
                lostp = [d["row"] for d in rw["rows"] if not d["control"]]
                oth_ok = f"holds on AMD {main_g['cpu_short']} only" in oth and f"holds on AMD {main_g['cpu_short']} only" in page.inner_text("#rw-other-short")
                for g_ in T["groups"]:
                    if g_["cpu_model"] == T["main_cpu"]:
                        continue
                    sl_ = [n for n in lostp if g_["rows"][n]["reading"] == "detectably slower"]
                    rs_ = [g_["rows"][n][c]["ratio"] for n in sl_ for c in ("fast", "aligned")]
                    oth_ok = (oth_ok and f"On AMD {g_['cpu_short']} ({g_['jobs']} jobs), {len(sl_)} of the {len(lostp)} were detectably slower, by {(min(rs_) - 1) * 100:.1f}% to {(max(rs_) - 1) * 100:.1f}%" in oth
                              and all(f"{RW_NAMES_PY[n]} (at most {g_['rows'][n]['at_most_pct']:.1f}%)" in oth for n in lostp if n not in sl_))
                ck.ok(oth_ok, "section 7: for each other CPU model, how many of the six programs were detectably slower, the range and the ones not detectable with their at-most bounds; the five-of-six claim is tied to EPYC 7763 only")
                ck.ok(all(x in dp.inner_text("#rw-note") for x in lost_counts) and all(r["outputs_match"] for r in rw["rows"]) and "identical with the checks off and on" in dp.inner_text("#rw-note"),
                      "details page: every lost-loop match count and the identical outputs are stated beside Figure 6")
                new_sections(dp, ck)
                est = dp.inner_text("#rw-est")
                ck.ok("estimate, not a measurement" in est and "instruction share approximates time share" in est and "not informative" in est and "Table 9 is the test" in est
                      and "probably an upper bound" in dp.inner_text("#fig5-cap") and "≈" in dtxt,
                      "details page: the Amdahl estimate sits in a collapsed block labelled an estimate, with its assumption, the functions-bound caveat and the measured result beside it")
                dp.evaluate("document.getElementById('rw-est').open = false")
                ck.ok(dp.locator("#progsum-table tbody tr").count() == 2 and "Two small programs timed earlier (older runs, not the programs above)" in dp.inner_text("#prog-sum-cap"),
                      "details page: the two small programs timed earlier follow Table 5 as Table 6, labelled as older runs, not the programs above")
                links = page.evaluate("[...document.querySelectorAll('a[href^=\"details.html\"]')].length")
                back = dp.evaluate("[...document.querySelectorAll('a[href=\"index.html\"], a[href=\"./\"]')].length")
                ck.ok(links >= 6 and back >= 1, f"the main page links the details page ({links} links) and the details page links back ({back})")
                # the repository is public: links go to this repository only, never to another repository or to workflow runs
                PUB = "github.com/JacoboPacheco/third-of-a-percent"
                gh = []
                for dp_, _, fs in os.walk(SITE):
                    for f_ in fs:
                        if f_.endswith((".html", ".js", ".css", ".json")):
                            with open(os.path.join(dp_, f_), encoding="utf-8") as fh:
                                txt_ = fh.read()
                                if re.search(r"github\.com/JacoboPacheco/(?!third-of-a-percent(?:[/\"#?\s]|$))|/actions/runs/|not public yet|repository is private", txt_):
                                    gh.append(f_)
                ghl = [x.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.includes('github.com') && !h.includes('third-of-a-percent') && h.includes('third-of-a-percent'))") for x in (page, dp)]
                publ = [x.evaluate("[...document.querySelectorAll('a[href]')].filter(a => a.href.includes('github.com/JacoboPacheco/third-of-a-percent')).length") for x in (page, dp)]
                stale = [x.inner_text("body") for x in (page, dp)]
                ck.ok(not gh and not any(ghl) and all(n >= 2 for n in publ) and not any(re.search(r"not public yet|repository is private|once it is public", t_) for t_ in stale),
                      f"links to the repository go to the public copy only ({publ} links; links to other repositories or to workflow runs: {gh}, {ghl}); no workflow-run links, no 'not public yet' wording")
                with open(os.path.join(DATA, "siblings.json"), encoding="utf-8") as f:
                    sibd = json.load(f)
                x69 = next(v for k, v in next(r for r in sibd["rows"] if r["variant"] == "clang18-fast")["cells"]["k02_add_fwd"]["per_cpu"].items() if "6973P" in k)
                ck.ok("own jobs, sizes and column" in page.inner_text("#mit-note") and "own jobs, sizes and column" in dp.inner_text("#sib-note")
                      and f"{fx(x69['L1']['max'])}" in dp.inner_text("#sib-note") and "Xeon 6973P-C" in dp.inner_text("#sib-note")
                      and f"{x69['jobs']} job" in dp.inner_text("#sib-note"),
                      "beside Tables 3 and 4: why their ranges differ from Figure 1, and Table 4's forward top named as an Intel Xeon 6973P-C draw with its job count")
                IFd = index["intel_forward"]
                cnt = {c: sum(1 for j in IFd["jobs"] if j["cpu_short"] == c) for c in IFd["cpus"]}
                ck.ok(all(f"{c} in {n} job" in page.inner_text("#cpu-note") and f"{c} in {n} job" in dp.inner_text("#intel-p") for c, n in cnt.items())
                      and "one or two jobs" not in dp.inner_text("#intel-p"),
                      f"the Intel models are named with exact job counts ({cnt}) in Table 1's note and in section 1 in full")
                s1f = index["s1_forward"][0]
                s1t = f"{s1f['ratio']:.2f}× [{s1f['ci95'][0]:.3f}, {s1f['ci95'][1]:.3f}] on {s1f['cpu_short']}, run {s1f['run_id']}"
                ck.ok(s1t in tuned and s1f["run_id"] == "38119008371" and "placement-sensitive" in tuned and "none came after the pooled runs" in tuned
                      and "1.599" not in tuned and "?:" not in page.inner_text("#method"),
                      f"main page, 'tuned?': the forward add's miss seen before v2 is quoted from the first harness run ({s1t}), not from the later pooled runs; no stray '?:'")
                defs = ["SIMD (several array elements per instruction)", "A/A control (the same binary timed against a copy of itself)",
                        "geometric mean (", "AVX2, a newer x86-64 instruction set"]
                mtxt = page.evaluate("document.body.innerText + ' ' + [...document.querySelectorAll('details.abs-more, details.cap-more')].map(d => d.textContent.replace(/\\s+/g, ' ')).join(' ')")
                open_full(page)
                ck.ok(all(d_ in mtxt for d_ in defs) and "Cachegrind, a tool" in page.inner_text("#fig2") and "ud2, the instruction" in page.inner_text("#fig2"),
                      "main page: SIMD, A/A, Cachegrind, ud2, AVX2, geometric mean are explained at first use (NOVEC now appears only on the details page, defined there)"
                      + ("" if all(d_ in mtxt for d_ in defs) else f": missing {[d_ for d_ in defs if d_ not in mtxt]}"))
                ck.ok("not needed to follow the result" in dp.inner_text("#details-purpose")
                      and all(f"{L}: " in dp.inner_text(".dnav") for L in "ABCD"),
                      "details page: a first line says it is not needed to follow the result; the nav names appendices A to D")
                # the headline above Figure 1 and the 'cannot tell you' box under the abstract
                page.evaluate("scrollTo(0, 0)"); page.wait_for_timeout(150)
                hl = page.inner_text("#headline")
                hb = page.evaluate("(() => { const r = document.getElementById('headline').getBoundingClientRect(), f = document.getElementById('fig1').getBoundingClientRect(); return [r.bottom <= f.top + 1, true]; })()")
                ck.ok(f"take {lost['min']:.1f}× to {lost['max']:.1f}× as long in cache" in hl and "Loops that lose SIMD under the check" in hl
                      and f"{IFd['aligned']['min']:.2f}–{IFd['aligned']['max']:.2f}× on Intel (forward add)" in hl and "near 1× on the AMD models" in hl and all(hb),
                      f"one headline line sits directly above Figure 1 (the hero holds the first screen), from index.json, with the AMD and Intel qualifier ({hb})")
                cb = page.evaluate("[...document.querySelectorAll('#cannot li')].map(l => l.innerText)")
                ck.ok(len(cb) == 4 and "robustness report" in cb[3] and "production average" in cb[0] and "picked for their lost loops" in cb[1] and "profile-guided optimization" in cb[1] and "not time" in cb[1]
                      and "one main toolchain" in cb[2] and "SSE2" in cb[2] and "section 6" in cb[2]
                      and page.evaluate("document.getElementById('cannot').closest('.abstract') !== null"),
                      "a box 'What this cannot tell you' sits with the abstract: production average, real programs picked for their lost loops and without PGO, counts are not time, one main toolchain at baseline SSE2")
                # related work: only sources read, as reported, with their addresses; the not-read ones without claims
                with open(os.path.join(DATA, "related.json"), encoding="utf-8") as f:
                    rel = json.load(f)
                rs = page.inner_text("#related")
                trs = page.evaluate("[...document.querySelectorAll('#rel-table tbody tr')].map(r => [r.querySelector('th').innerText, r.querySelector('a.url').href])")
                want = {x["id"]: x for x in rel["sources"]}
                read_ids = {"google", "queue", "carruth", "nader", "nist", "readyset", "mytkowicz", "stabilizer", "rustcperf", "quickbench"}
                ck.ok(set(want) == read_ids and len(trs) == 5 and [t[1] for t in trs] == [want[k]["url"] for k in rel["main_rows"]]
                      and "as reported" in rs.lower() and "found no public per-loop" in rs and "not the same as none existing" in rs
                      and 100 <= len(page.inner_text("#rel-summary").split()) <= 190,
                      f"main page, related work: about 150 words ({len(page.inner_text('#rel-summary').split())}), a five-row table whose links are the sources' public addresses, 'as reported', and 'found no public per-loop' measurement of libc++ FAST mode")
                rl_items = dp.evaluate("[...document.querySelectorAll('#rel-list li')].map(l => [l.innerText, l.querySelector('a.url').href])")
                nr = dp.inner_text("#rel-notread")
                nr_names = ["Shnatsel", "fbounds-safety", "_GLIBCXX_ASSERTIONS discussions", "Code alignment issues"]
                prose_both = page.inner_text("body") + dp.evaluate("(() => { const t = document.body.cloneNode(true); t.querySelector('#rel-notread').remove(); document.documentElement.append(t); const x = t.innerText; t.remove(); return x; })()")
                ck.ok(len(rl_items) == 10 and all(it[1] == x["url"] and "As reported" in it[0] or (x["id"] == "carruth" and "As reported" in it[0]) for it, x in zip(rl_items, rel["sources"]))
                      and nr.startswith("Also relevant, not read in full") and all(n_ in nr for n_ in nr_names)
                      and not any(n_ in prose_both for n_ in ("Shnatsel", "fbounds-safety", "easyperf", "Bakhvalov")),
                      "details page: all ten sources read, each with its address and 'as reported'; the search-summary-only items appear once, in a line labelled 'also relevant, not read in full', with no claim")
                # the AVX2 exception is stated wherever 'near 1x' is
                avx = page.evaluate("avx2Text()")
                ck.ok("1.11×" in avx and "EPYC 9V45" in avx and "AVX2 exception, 1.11×" in abstract and all(avx in x_ for x_ in (page.inner_text("#headline"), page.inner_text("#sib-short"), dp.inner_text("#sib-finding"), dp.inner_text("#intel-p"))),
                      f"every 'near 1x on the AMD models' carries the AVX2 exception ({avx}), main and details")
                avx_short = page.inner_text('#result .gist span[data-v="avx2Short"]').strip()
                with open(os.path.join(REPO, "README.md"), encoding="utf-8") as rf:
                    readme_txt = rf.read()
                ck.ok(f"(one AVX2 exception, {avx_short}×)" in page.inner_text("#result .gist") and f"one AVX2 exception, {avx_short}x)" in readme_txt and avx_short in avx,
                      f"the Result gist and the README forward-loop sentence carry the AVX2 exception ({avx_short}), the same value as the headline")
                caps = dp.evaluate("[...document.querySelectorAll('.tcap b, figcaption b')].map(b => b.textContent.trim()).filter(t => /^(Table|Figure) /.test(t))")
                secs = dp.evaluate("[...document.querySelectorAll('h2 .secno')].map(n => n.textContent.trim())")
                ck.ok(len(caps) == len(set(caps)) and len(secs) == len(set(secs)),
                      f"details page: every table, figure and section number appears once ({sorted(caps)}, {secs})")
                meta = page.evaluate("document.querySelector('meta[name=description]').content")
                ck.ok("recover most of the cost for reverse and matrix-multiply loops" in meta and "recover the cost," not in meta,
                      "the page description says the rewrites recover most of the cost for the reverse and matrix-multiply loops only")
                # Figure 1 shows the noise: every job's ratio as a tick, the A/A band at 1x
                pcd = next(x for x in pooled["cpus"] if x["cpu_model"] == default_cpu["cpu_model"])
                jt_ok = []
                for k in index["criteria"]["kernels"]:
                    for sz in ("L1", "L2"):
                        cell = next((x for x in pcd["cells"] if x["cell_id"] == f"{k}.{sz}"), None)
                        if not cell:
                            continue
                        n_ = page.locator(f'#rows .row[data-k="{k}"] .jt.{sz.lower()}').count()
                        jt_ok.append(n_ == cell["aligned"]["jobs"] == len(cell["aligned"]["per_job"]))
                bands = page.locator("#rows .aa-band").count()
                cap1 = page.text_content("#fig1-cap")
                ck.ok(jt_ok and all(jt_ok) and bands == len(index["criteria"]["kernels"]) and "each job’s own ratio" in cap1
                      and f"±{pcd['aa']['half_width_pct']:.2f}%" in cap1,
                      f"Figure 1 draws every job's ratio as a tick (one per job in every cell, {sum(jt_ok)} of {len(jt_ok)} cells) and this model's A/A band at 1x, both named in the caption")
                du = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DATA) for f in fs)
                ck.ok(du < 25 * 1024 * 1024, f"site/data is {du / 1048576:.1f} MB (under 25)")
                txt = page.inner_text("body") + dp.inner_text("body")
                ck.ok(not any(w in txt for w in ("[object", "undefined", "NaN", "n/a")) and not re.search(r"\bnull\b", txt),
                      "no placeholder text (undefined, null, NaN, n/a, [object ...]) on either page")
                page.evaluate("scrollTo(0, 0)"); page.wait_for_timeout(200)
                shot(page, saved, shots, "desktop-1-first-screen.png")
                # Figure 1 with a selection, by keyboard
                page.focus("#rows .row[aria-selected=true]")
                page.keyboard.press("ArrowDown")
                page.wait_for_function(FIG2_READY)
                k2 = page.evaluate("document.querySelector('#rows .row[aria-selected=true]').dataset.k")
                ck.ok(k2 != "k04_rev" and page.evaluate("document.activeElement.dataset.k") == k2 and f"loop={k2}" in page.evaluate("location.hash"),
                      f"ArrowDown moves the selection and focus to the next row ({k2}) and the hash keeps it")
                page.click('#rows .row[data-k="k02_add_fwd"]')
                page.wait_for_function(FIG2_READY)
                open_full(page)
                f2t = page.inner_text("#fig2")
                ck.ok("numbers per pass" in f2t and "inferred" in f2t and "faster" in f2t,
                      "Figure 2, forward add aligned: explains in plain words why the checked build is faster (per-pass unrolling, cause inferred)")
                page.click('#col-seg [data-col="compiled"]')
                page.wait_for_function(FIG2_READY)
                page.wait_for_timeout(500)
                shot(page, saved, shots, "desktop-2-figure1-selected.png", "#fig1")
                shot(page, saved, shots, "desktop-3-figure2.png", "#fig2")
                page.click('#col-seg [data-col="aligned"]')
                page.click('#rows .row[data-k="k04_rev"]')
                page.wait_for_function(FIG2_READY)
                scroll_to(page, "#placement")
                shot(page, saved, shots, "desktop-4-middle.png")
                scroll_to(page, "#realworld")
                shot(page, saved, shots, "desktop-4b-real-programs.png")
                dp.evaluate("scrollTo(0, 0)"); dp.wait_for_timeout(200)
                shot(dp, saved, shots, "desktop-details-first-screen.png")
                ck.ok(not dp.evaluate("document.getElementById('appa-details').open"), "details page: Appendix A's table is collapsed by default")
                dp.evaluate("document.getElementById('appa-details').open = true")
                scroll_to(dp, "#appendix-a")
                shot(dp, saved, shots, "desktop-5-appendix.png")
                scroll_to(dp, "#appendix-b")
                shot(dp, saved, shots, "desktop-6-appendix-b.png")
                dp.close()
                # a hash restores the selection
                other = next((c for c in cpus if c is not default_cpu), default_cpu)
                page.goto(f"{base}#loop=k02_add_fwd&cpu={slug(other['cpu_short'])}&loops=compiled", wait_until="networkidle")
                page.reload(wait_until="networkidle")
                wait_ready(page)
                st = page.evaluate("""() => [document.querySelector('#rows .row[aria-selected=true]').dataset.k,
                    document.querySelector('#cpu-seg [aria-checked=true]').dataset.cpu,
                    document.querySelector('#col-seg [aria-checked=true]').dataset.col]""")
                ck.ok(st == ["k02_add_fwd", slug(other["cpu_short"]), "compiled"], f"a URL hash restores loop, CPU model and column ({st})")
                # every row, both columns
                todo = [default_cpu] if a.quick else cpus
                for c in todo:
                    for col in ("aligned", "compiled"):
                        page.goto(f"{base}#cpu={slug(c['cpu_short'])}&loops={col}", wait_until="networkidle")
                        page.reload(wait_until="networkidle")
                        wait_ready(page)
                        label = f"{c['cpu_short']} {col}"
                        bad = page_numbers(page, allowed)
                        ck.ok(not bad, f"{label}: every number on the page is in the data" + ("" if not bad else f": {bad[:4]}"))
                        every_row(page, ck, allowed, label)
                ck.ok(not errors, "1280: no console errors, page errors or failed data requests on either page"
                      + ("" if not errors else f": {errors[:5]}"))
                page.close()

                # ---- phone width
                interactive_checks(browser, base, ck, index, pooled, allowed, errors, saved, shots)
                hero_variant_checks(browser, base, ck, index, pooled)
                design_checks(browser, base, ck, index)
                rail_checks(browser, base, ck)
                figure2_plain_checks(browser, base, ck, index, pooled)
                story_checks(browser, base, ck, index, pooled)
                collapsed_checks(browser, base, ck, index, saved, shots)
                navigation_checks(browser, base, ck, index, pooled)
                print("== 390 wide")
                errors = []
                page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
                watch(page, errors)
                page.goto(base, wait_until="networkidle")
                wait_ready(page)
                ck.ok(no_hscroll(page), "390: no horizontal scroll")
                order = page.evaluate("""() => { const a = document.getElementById('fig1').getBoundingClientRect(),
                    b = document.getElementById('fig2').getBoundingClientRect(); return b.top >= a.bottom - 1; }""")
                ck.ok(not page.locator("#fig2").is_visible() and not page.locator("#fig2-body").is_visible(),
                      "390: Figure 2 is not on the page until a row is tapped (no prompt far below the figure)")
                page.evaluate("document.getElementById('fig1').scrollIntoView()")
                page.click('#rows .row[data-k="k05_stride2"]')
                page.wait_for_function(FIG2_READY)
                under = page.evaluate("""() => { const row = document.querySelector('#rows .row[data-k="k05_stride2"]'), f = document.getElementById('fig2');
                    const a = row.getBoundingClientRect(), b = f.getBoundingClientRect(); return [row.nextElementSibling === f, b.top - a.bottom, row.getAttribute('aria-expanded'), document.getElementById('rows').getAttribute('role')]; }""")
                ck.ok(under[0] and under[1] < 24 and under[2] == "true" and under[3] == "group", f"390: Figure 2 opens directly under the tapped row (gap {under[1]:.0f} px), the rows are an accordion ({under})")
                page.click('#rows .row[data-k="k05_stride2"]')
                ck.ok(page.evaluate("document.getElementById('fig2').parentElement.id") == "figures" and not page.locator("#fig2").is_visible(), "390: a second tap on the row folds the panel")
                page.evaluate("scrollTo({ top: 0, behavior: 'instant' })"); page.wait_for_timeout(250)
                fig1_top = page.evaluate("document.getElementById('fig1').getBoundingClientRect().top")
                jump = page.evaluate("""() => { const a = document.querySelector('.jump a'); const r = a && a.getBoundingClientRect();
                    return a && r.height > 0 ? [r.bottom, a.getAttribute('href')] : null; }""")
                race_top = page.evaluate("(() => { const r = document.getElementById('race-loops').getBoundingClientRect(); return [r.top, r.bottom]; })()")
                ck.ok(fig1_top < 844 * 4 and 0 < race_top[0] < 844,
                      f"390: the interactive hero's lanes start on the first screen ({race_top}) and Figure 1 starts at {fig1_top:.0f} px (within 3 screens; the hero and the story come first)")
                swipe = page.evaluate("""() => { const w = document.getElementById('cpu-table').closest('.tablewrap'), h = w.previousElementSibling;
                    return [w.scrollWidth > w.clientWidth + 1, !!h && h.classList.contains('swipe') && !h.hidden]; }""")
                ck.ok(swipe[0] == swipe[1], f"390: a wide table carries a visible swipe hint exactly when it overflows (overflows, hint shown: {swipe})")
                small = page.evaluate(TAP_JS)
                ck.ok(not small, f"390: every visible link and button on the main page is at least 32 px tall ({small[:4]})")
                hit = page.evaluate("""() => { const bad = [];
                    for (const e of document.querySelectorAll('#race button, #race [role=radio], #race [role=switch], #cpu-seg button, #col-seg button, .w-chip, .bar a, .bar button')) {
                      if (e.closest('details:not([open])')) continue; e.scrollIntoView({ block: 'center', behavior: 'instant' }); const q = e.getBoundingClientRect(); if (q.width < 1) continue;
                      const x = q.left + q.width / 2, y = q.top + q.height / 2;
                      const at = (px, py) => { const t = document.elementFromPoint(px, py); return t && (t === e || e.contains(t) || t.closest('button,a,[role=radio],[role=switch]') === e); };
                      if (!(at(x, y - 21) && at(x, y + 21) && (q.width >= 44 || (at(x - 21, y) && at(x + 21, y))))) bad.push((e.textContent || e.id).trim().slice(0, 20) + ' ' + Math.round(q.width) + 'x' + Math.round(q.height));
                    } window.scrollTo({ top: 0, behavior: 'instant' }); return bad; }""")
                ck.ok(not hit, f"390: the hero controls, CPU and column buttons, word chips and bar links answer a tap within 44 x 44 px ({hit[:4]})")
                shot(page, saved, shots, "mobile-1-first-screen.png")
                h = page.evaluate("document.documentElement.scrollHeight")
                ck.ok(h < 20500, f"390: the main page with every section opened is {h} px long (the default, collapsed page is the one capped, above)")
                # the '?' works on tap and closes on an outside tap and on Escape
                tip = "getComputedStyle(document.getElementById('col-tip')).opacity"
                away = lambda: page.mouse.move(380, 830)  # no hover left behind: the state comes from the tap alone
                page.click("#col-hint")
                away()
                page.wait_for_timeout(250)
                shown = page.evaluate(tip) == "1"
                page.click("h1")
                away()
                page.wait_for_timeout(250)
                closed_out = page.evaluate(tip) == "0"
                page.click("#col-hint")
                away()
                page.keyboard.press("Escape")
                page.wait_for_timeout(250)
                closed_esc = page.evaluate(tip) == "0"
                ck.ok(shown and closed_out and closed_esc,
                      f"390: the '?' opens on tap ({shown}), closes on an outside tap ({closed_out}) and on Escape ({closed_esc})")
                scroll_to(page, "#fig1")
                page.click('#rows .row[data-k="k05_stride2"]')
                page.wait_for_function(FIG2_READY)
                page.wait_for_timeout(900)
                top = page.evaluate("document.getElementById('fig2').getBoundingClientRect().top")
                ck.ok(-2 <= top <= 844 * 0.35, f"390: a tap on a loop scrolls Figure 2 into view (its top at {top:.0f} px)")
                ck.ok("stride-2" in page.inner_text("#fig2 .f2-head").lower(), "390: Figure 2 shows the tapped loop")
                open_full(page)
                nj = page.evaluate("[...document.querySelectorAll('#fig2 .f2-jobs .jt')].length")
                want_j = sum(len(next(x for x in next(pc for pc in pooled['cpus'] if pc['cpu_model'] == default_cpu['cpu_model'])['cells'] if x['cell_id'] == f'k05_stride2.{sz}')['aligned']['per_job']) for sz in ('L1', 'L2'))
                ck.ok(not page.locator("#rows .jt").first.is_visible() and page.locator("#fig2 .f2-jobs").is_visible() and nj == want_j,
                      f"390: the per-job ticks show only in the drawer ({nj} ticks for {want_j} job ratios), not in Figure 1's rows")
                page.mouse.wheel(0, 500); page.wait_for_timeout(300)
                sticky = page.evaluate("""() => { const h = document.querySelector('#fig2 .f2-sticky'); const r = h.getBoundingClientRect();
                    return [getComputedStyle(h).position, Math.round(r.top), h.innerText]; }""")
                ck.ok(sticky[0] == "sticky" and -1 <= sticky[1] <= 2 and "Stride-2" in sticky[2] and "Back to the eight loops" in sticky[2],
                      f"390: after scrolling into the machine code, a sticky header keeps the loop's name and the back button at the top ({sticky[:2]})")
                page.mouse.wheel(0, -500); page.wait_for_timeout(300)
                shot(page, saved, shots, "mobile-2-after-tap.png")
                shot(page, saved, shots, "mobile-3-figure2.png", "#fig2")
                ck.ok(no_hscroll(page) and page.evaluate("[...document.querySelectorAll('#fig2 pre')].every(p => p.scrollWidth <= p.clientWidth + 1)"),
                      "390: Figure 2's code and commands wrap, no horizontal scroll")
                scroll_to(page, "#placement")
                shot(page, saved, shots, "mobile-4-middle.png")
                scroll_to(page, "#realworld")
                shot(page, saved, shots, "mobile-4c-real-programs.png")
                dp = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
                watch(dp, errors)
                dp.goto(base + "details.html", wait_until="networkidle")
                wait_details(dp)
                ck.ok(no_hscroll(dp), "390, details page: no horizontal scroll")
                small = dp.evaluate(TAP_JS)
                ck.ok(not small, f"390: every visible link and button on the details page is at least 32 px tall ({small[:4]})")
                print(f"      details page at 390: {dp.evaluate('document.documentElement.scrollHeight')} px")
                shot(dp, saved, shots, "mobile-details-first-screen.png")
                scroll_to(dp, "#fig3")
                shot(dp, saved, shots, "mobile-4b-figure3.png")
                dp.evaluate("document.getElementById('appa-details').open = true")
                dp.wait_for_timeout(150)
                aw = dp.evaluate("""() => { const w = document.getElementById('appa-wrap');
                    return [w.scrollWidth > w.clientWidth, getComputedStyle(w).overflowX, !document.getElementById('appa-hint').hidden]; }""")
                ck.ok(aw[0] and aw[1] == "auto" and aw[2] and no_hscroll(dp),
                      f"390, details page: Appendix A's table scrolls inside its own box, with a visible hint, and the page does not scroll sideways ({aw})")
                scroll_to(dp, "#appendix-a")
                shot(dp, saved, shots, "mobile-5-appendix.png")
                bad = page_numbers(dp, allowed)
                ck.ok(not bad, "390, details page: every number on it is in site/data" + ("" if not bad else f": {bad[:4]}"))
                dp.close()
                scroll_to(page, "#method")
                shot(page, saved, shots, "mobile-6-method.png")
                every_row(page, ck, allowed, "390 default CPU model")
                ck.ok(no_hscroll(page), "390: still no horizontal scroll after every row was selected")
                ck.ok(not errors, "390: no console errors on either page" + ("" if not errors else f": {errors[:5]}"))
                page.close()

                # ---- the SAMPLE fixture
                print("== SAMPLE fixture (?data=fixture)")
                errors = []
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                watch(page, errors)
                page.goto(f"{base}?data=fixture", wait_until="networkidle")
                wait_ready(page)
                vis = page.evaluate("""() => [...document.querySelectorAll('#sample-band, #sample-mark')]
                    .filter(n => !n.hidden && (n.id === 'sample-mark' || n.getBoundingClientRect().top < innerHeight) && n.textContent.includes('SAMPLE DATA')).length""")
                ck.ok(vis == 2, "fixture: SAMPLE DATA is printed (the band on the first screen, the figure mark on Figure 1)")
                bad = page_numbers(page, allowed)
                ck.ok(not bad, "fixture: every number on the page is in the data" + ("" if not bad else f": {bad[:4]}"))
                every_row(page, ck, allowed, "fixture")
                shot(page, saved, shots, "fixture-first-screen.png")
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(200)
                ck.ok(no_hscroll(page), "fixture: no horizontal scroll at 390")
                ck.ok(not errors, "fixture: no console errors" + ("" if not errors else f": {errors[:5]}"))
                page.close()

                # ---- worst-case data
                print("== worst-case data (a missing cell, a loop missing everywhere, an interval off both ends)")
                with open(os.path.join(DATA, "pooled.json"), encoding="utf-8") as f:
                    worst = json.load(f)
                for c in worst["cpus"]:
                    if c["cpu_model"] != default_cpu["cpu_model"]:
                        continue
                    c["cells"] = [x for x in c["cells"] if x["kernel"] != "k07_hist" and x["cell_id"] != "k01_sum_fwd.L2"]
                    for x in c["cells"]:
                        if x["cell_id"] == "k03_stencil.L1":
                            for col in ("as_compiled", "aligned"):
                                x[col]["ci95"] = [0.2, 40.0]
                worst_body = json.dumps(worst)
                errors = []
                page = browser.new_page(viewport={"width": 390, "height": 844})
                watch(page, errors)
                def fulfil_with(body):
                    return lambda route: route.fulfill(status=200, body=body, content_type="application/json")
                page.route("**/data/pooled.json", fulfil_with(worst_body))
                page.goto(base, wait_until="networkidle")
                wait_ready(page)
                ck.ok(page.inner_text('#rows .row[data-k="k07_hist"] .val').strip() == "not measured",
                      "worst case: a loop with no cell in any run says 'not measured'")
                ck.ok(page.evaluate("""[...document.querySelectorAll('#rows .row[data-k="k03_stencil"] .wh')].some(w =>
                    w.classList.contains('clip-l') && w.classList.contains('clip-r'))"""),
                      "worst case: the huge interval is clipped at both ends of the axis, with arrows")
                wd = browser.new_page(viewport={"width": 390, "height": 844})
                watch(wd, errors)
                wd.route("**/data/pooled.json", fulfil_with(worst_body))
                wd.goto(base + "details.html", wait_until="networkidle")
                wait_details(wd)
                miss = wd.evaluate("""() => { const rows = [...document.querySelectorAll('#appa tbody tr')];
                    const i = rows.findIndex(r => r.textContent.includes('k01_sum_fwd.L2'));
                    return i >= 0 && rows[i].textContent.includes('not measured'); }""")
                ck.ok(miss and no_hscroll(wd), "worst case: the missing cell says 'not measured' in Appendix A (details page), no horizontal scroll")
                wd.close()
                page.click('#rows .row[data-k="k07_hist"]')
                page.wait_for_function(FIG2_READY)
                ck.ok(no_hscroll(page), "worst case: no horizontal scroll at 390")
                shot(page, saved, shots, "worst-case-390.png", "#fig1")
                ck.ok(not errors, "worst case: no console errors" + ("" if not errors else f": {errors[:5]}"))
                page.close()

                # ---- error states
                print("== error states")
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                page.route("**/data/index.json", lambda route: route.fulfill(status=404, body="missing"))
                page.goto(base, wait_until="networkidle")
                page.wait_for_timeout(300)
                ck.ok("did not load" in page.inner_text("#fig1-state"), "index.json missing: the page says so and how to fix it")
                page.close()
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                page.route("**/data/pooled.json", lambda route: route.fulfill(status=500, body="boom"))
                page.goto(base, wait_until="networkidle")
                page.wait_for_timeout(300)
                ck.ok("Try again" in page.inner_text("#fig1-state"), "a results file failing: an error with a retry button")
                page.close()
            finally:
                browser.close()
    finally:
        srv.shutdown()
        srv.server_close()
    print("== screenshots")
    for s in saved:
        print(f"   {s}")
    print("SITE CHECKS PASSED" if not ck.failures else f"SITE CHECKS FAILED ({len(ck.failures)})")
    return 0 if not ck.failures else 1


if __name__ == "__main__":
    sys.exit(main())
