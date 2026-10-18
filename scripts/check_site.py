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
     PHONE_DEFAULT_CAP px long at 390 by default (collapsed), and under PHONE_ALL_OPEN_BACKSTOP with every section opened (a backstop;
     both constants and the lengths last measured are at the top of this file); links to the repository only to the public copy, no run links;
   - the Arm column (arm_checks): section 6a (a gist, then Figure 7 and its readout behind the Details button) and section 6d with
     Tables 12 and 13 (details) equal to site/data/arm64.json recomputed in Python at their printed precision; the verdict is
     reported as INCONCLUSIVE with the missed cell named, never as a map; the matrix-multiply mechanism is labelled 'consistent with'
     and 'not tested'; Figure 7's rows, marks, click, arrow keys, Home and End, and the aligned / as compiled switch; a text
     equivalent; the stale 'No arm64' limit gone; the Reproduce command for the Arm runner; section 10's Arm addition is two
     sentences; no number typed into the two new sections' HTML; no sideways scroll and finger-sized rows at 390 px; no console errors;
   - the replication (replication_checks): Figure 8 in section 1 (six rows in the stored order, each set's word and job count, the inside counts, the
     title's counts, a readout per row with the flip cells and placement numbers, the keys) and the account with Table 14 on the details page equal to
     site/data/replication.json recomputed in Python; and the row-length sweep (dsweep_checks): the sentence in section 6a, the account, Figure 9 (panels,
     points, toggle, readout, keys) and Table 15 equal to site/data/dsweep.json recomputed in Python (the instruction line by least squares);
     no number typed into their HTML, no workflow-run link, finger-sized controls and no sideways scroll at 390 and 320 px;
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
   - docs/hero.png and site/og.png (pictures of the first screen) are the size they claim, and docs/hero.json (what
     they were taken from, written by scripts/capture_hero.py) equals what the first screen shows and what site/data
     says; the work-in-progress marking shows at every phone width from 320 px; neither page scrolls sideways from
     320 px; an Intel model's no-verdict note shows on a phone; the hero's lane names are never cut; the hint pill
     never sits on other parts; the page's counts of lost jobs, the 29-loop tally and the newer-toolchain baseline
     are tied to the files they come from;
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
Exit code 0 only if every check passed. Needs the Python playwright package and its Chromium. The pages ask Google Fonts for two
typefaces; when fonts.googleapis.com does not answer (probed once at the start) the check answers those requests itself instead of
reading the refusal as a page error, and runs on the system fonts. SITE_CHECK_FONTS=online|offline|auto forces it.
Two checks need the web fonts and are expected to FAIL on the system fonts (FONT_DEPENDENT_CHECKS, below): the hero first-view checks at
1440x900, "hero 4 at 1440x900: the whole finding" and "1440x900: the whole finding is in the first view", because the system fonts are taller and
push the bottom of the hero race to about 921 px in a 900 px window. So a run that cannot reach the network is complete only with those two failing
and nothing else (the last line says so); the full result, and the page lengths, are the run with the fonts online (the same as the CI runner).
"""
import argparse
import functools
import glob
import http.server
import hashlib
import html
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import threading

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, "site")
DATA = os.path.join(SITE, "data")
RW_NAMES_PY = {"lightgbm_default": "LightGBM (default)", "lightgbm_multiclass": "LightGBM (multiclass)", "lightgbm_linear": "LightGBM (linear)", "draco": "Draco", "tinydnn": "tiny-dnn", "spectra": "Spectra", "meshopt": "meshoptimizer (control)", "fmt": "{fmt} (control)"}
# Phone page lengths at 390 px wide. The default (collapsed) page is the one that is capped: it is the page a reader meets.
# The all-open length is a backstop only, so that the text behind the Details buttons cannot grow without anyone noticing.
# Last measured on Windows with the web fonts, after the related-work summary and one sentence of section 10 were shortened (by 157 px):
# 7995 px by default, 23983 px with every section opened (it was 24140 before).
# The backstop was 20632 + margin (21000) before the Arm column, 23750 for the column as first built (measured 23305),
# and is 24200 now. It is not raised: text added to the main page is paid for by cutting text elsewhere. The default cap has not moved.
PHONE_DEFAULT_CAP = 10500
PHONE_ALL_OPEN_BACKSTOP = 24200
# The checks that measure the hero's first view against the web fonts: on the system fonts (no network, SITE_CHECK_FONTS=offline) the race is
# taller than a 900 px window and they fail by design. Each entry is the start of the check's message; README.md and readme-parts/DETAILS.md say
# how many there are, and tests/test_readme_numbers.py ties that number to this tuple.
FONT_DEPENDENT_CHECKS = ("hero 4 at 1440x900: the whole finding", "1440x900: the whole finding is in the first view")
FONTS_BLOCKED = False  # set by main(): True when the font requests were answered locally
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


# The pages load two typefaces from Google Fonts. A check run with no route to those hosts (offline, a firewall) read every blocked
# request as a page error and failed dozens of checks that say nothing about the page. SITE_CHECK_FONTS picks what the browser does:
#   auto (default)  probe fonts.googleapis.com once; if it does not answer, serve the font requests empty from here
#   online          let the pages load the fonts (what a reader gets; needs the network)
#   offline         always serve the font requests empty from here (no network, system fonts; line wraps differ from a run with the fonts)
# No assertion changes: with the requests answered locally nothing fails, so there is no error to ignore.
FONT_HOSTS = re.compile(r"https://fonts\.(googleapis|gstatic)\.com/")


def fonts_reachable(timeout=4):
    import urllib.request
    try:
        with urllib.request.urlopen("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono", timeout=timeout) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def _empty_font_response(route):
    if "googleapis" in route.request.url:
        route.fulfill(status=200, content_type="text/css", body="/* served empty by scripts/check_site.py: no request to a font host */")
    else:
        route.fulfill(status=204, body="")


def block_font_hosts(browser):
    """Every page and context the browser makes from now on gets its font requests answered locally."""
    orig_page, orig_ctx = browser.new_page, browser.new_context

    def new_page(**kw):
        pg = orig_page(**kw)
        pg.context.route(FONT_HOSTS, _empty_font_response)
        return pg

    def new_context(**kw):
        c = orig_ctx(**kw)
        c.route(FONT_HOSTS, _empty_font_response)
        return c
    browser.new_page, browser.new_context = new_page, new_context


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


NEAR = 0.005  # a map is "narrow" when a forward cell's aligned interval end is within this of the limit (twin of NEAR in site/app.js)


def close_calls(c, pooled):
    """The Python twin of closeCalls() in site/app.js, derived from pooled.json and index.json, not copied from the page: a CPU
    model whose verdict is a map but whose counted forward cell nearest the limit ends within NEAR of it, or whose left-out
    placement-sensitive cell would miss the limit by less than NEAR if it were counted. [(cell id, aligned interval end, left out)]."""
    if not c["enough"] or c["form"] != "map":
        return []
    pc = next(q for q in pooled["cpus"] if q["cpu_model"] == c["cpu_model"])
    lim = 1 + pc["verdict"]["forward_limit_pct"] / 100
    ps = {q["cell_id"] for q in c["placement_sensitive"]}
    out = []
    for x in pc["cells"]:
        if x["class"] != "kept" or x["size_class"] not in ("L1", "L2") or not x["aligned"]:
            continue
        hi = x["aligned"]["ci95"][1]
        if x["cell_id"] not in ps and hi <= lim and lim - hi < NEAR:
            out.append((x["cell_id"], hi, False))
        elif x["cell_id"] in ps and x["aligned"]["ratio"] <= lim and hi > lim and hi - lim < NEAR:
            out.append((x["cell_id"], hi, True))
    return out


def lim_of(c, pooled):
    """1 + the forward limit the model's verdict used (1.02 for a 2% limit)."""
    return 1 + next(q for q in pooled["cpus"] if q["cpu_model"] == c["cpu_model"])["verdict"]["forward_limit_pct"] / 100


def left_out_above(c, pooled):
    """The placement-sensitive forward cells a model leaves out of its forward test that stay above the limit when aligned: [(cell id, ratio)]."""
    pc = next(q for q in pooled["cpus"] if q["cpu_model"] == c["cpu_model"])
    lim = 1 + pc["verdict"]["forward_limit_pct"] / 100
    ps = {q["cell_id"] for q in c["placement_sensitive"]}
    return [(x["cell_id"], x["aligned"]["ratio"]) for x in pc["cells"]
            if x["cell_id"] in ps and x["class"] == "kept" and x["size_class"] in ("L1", "L2") and x["aligned"] and x["aligned"]["ratio"] > lim]


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


def pick_cpu(pg, slug):
    """Choose the hero's CPU model the way a reader does at this width: tap its tab, or, where the five tabs give way to the quiet line
    'Measured on ...' (variant 4 up to 640 px), choose it from that line's menu."""
    if pg.evaluate("getComputedStyle(document.getElementById('race-cpu')).display") == "none":
        pg.select_option("#race-cpu-sel", slug)
    else:
        pg.click(f'#race-cpu [data-cpu="{slug}"]')


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
        pick_cpu(pg, other["slug"])
        pg.wait_for_timeout(250)
        ck.ok(f"{fx(worst(other['cpu_model']))}×" in pg.inner_text("#band-worst"), f"{w}: the band's worst loop follows the CPU chip ({other['cpu_short']}: {fx(worst(other['cpu_model']))}×)")
        pick_cpu(pg, index["default_cpu"])
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
    for w, h, cap in ((1440, 900, None), (390, 844, PHONE_DEFAULT_CAP)):
        pg = browser.new_page_plain(viewport={"width": w, "height": h})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        n = pg.evaluate("document.querySelectorAll('.sec-more').length")
        closed = pg.evaluate("[...document.querySelectorAll('.sec-body')].filter(b => b.hidden).length")
        ck.ok(n >= 9 and closed == n, f"{w}: every section starts collapsed, one button each to open ({closed} of {n})")
        r = pg.evaluate("(() => { const r = document.getElementById('race').getBoundingClientRect(), s = document.querySelector('.hero .scope').getBoundingClientRect(), d = document.getElementById('bar-limits').getBoundingClientRect(), t = document.querySelector('.toc-btn').getBoundingClientRect(); return [r.bottom, s.bottom, d.bottom, d.top, t.bottom, t.top]; })()")
        lb = pg.evaluate("document.getElementById('race-loops').getBoundingClientRect().bottom")
        ck.ok((r[0] <= h or (w < 641 and lb <= h * 1.3)) and r[1] <= h and r[2] <= h and r[3] >= 0 and r[4] <= h and r[5] >= 0, f"{w}x{h}: the whole finding is in the first view: the race (on a phone its eight lanes, the caption a short scroll below), switch and ratio, the scope sentence, the Limits link and the Contents button ({r}, lanes end {lb:.0f})")
        menu = pg.evaluate("[...document.querySelectorAll('#toc-list li.toc-top a')].map(a => [a.textContent.trim(), a.getAttribute('href')])")
        ck.ok(menu == [["Limits: what this cannot tell you", "#cannot"], ["Full details: the separate page", "details.html"]], f"{w}: the Contents menu starts with the two header items that used to be separate links, Limits and Full details ({menu})")
        tb = pg.evaluate("""(() => { const b = document.querySelector('.toc-btn'), cs = getComputedStyle(b), r = b.getBoundingClientRect(), t = getComputedStyle(document.getElementById('race-sw'));
            const clear = (c) => c === 'rgba(0, 0, 0, 0)' || c === 'transparent';
            return [clear(cs.borderTopColor), clear(cs.backgroundColor), cs.textDecorationLine, Math.round(r.height), +b.matches('[aria-expanded="false"]'), !clear(t.backgroundColor), b.textContent.trim()]; })()""")
        ck.ok(tb[5] and tb[6] == "Contents" and ((w < 641 and tb[0] and tb[1] and tb[2] == "underline" and tb[3] >= 44 and tb[4])
                                              or (w >= 641 and not tb[0] and not tb[1])),
              f"{w}x{h}: the switch is the one filled control in the first view, and the Contents menu does not compete with it as a second outlined pill on a phone: there it is an underlined word like the links under the intro (no outline, no fill, still 44 px tall for a finger), and from 641 px up it keeps its outline ({tb})")
        fd = pg.evaluate("(() => { const a = document.querySelector('.hero .fine .fine-full'), r = a.getBoundingClientRect(), cs = getComputedStyle(a); return [a.textContent.trim(), a.getAttribute('href'), r.width > 0 && r.height > 0 && cs.visibility !== 'hidden', r.bottom, r.height]; })()")
        ck.ok(fd[:2] == ["Full details", "details.html"] and ((w < 641 and not fd[2]) or (w >= 641 and fd[2] and fd[3] <= h and fd[4] >= 32)),
              f"{w}x{h}: a plain 'Full details' link to the details page sits in the quiet link row of the first view on a wide screen (on a phone only the Contents menu holds it) ({fd})")
        aud = pg.evaluate("(() => { const a = document.querySelector('.hero .aud'), r = a.getBoundingClientRect(); return [a.textContent.trim(), r.bottom, r.height]; })()")
        head = pg.evaluate("""(() => { const q = (s) => document.querySelector(s).textContent.trim(), e = document.getElementById('race-head'), r = e.getBoundingClientRect();
            return [q('#race-head .rh-t'), q('#race-head .rh-off'), q('#race-head .rh-on'), q('#race-head .rh-num'), r.height > 0, r.bottom, e.textContent.includes('Grey bar'), document.querySelectorAll('#race-head i').length, e.hasAttribute('aria-hidden')]; })()""")
        ck.ok(aud[0] == "For C++ engineers deciding whether to turn on libc++’s bounds checks." and aud[2] > 0 and aud[1] <= h
              and head[:4] == ["Run time with the bounds check:", "off", "on", "times as long as off"] and head[4] and head[5] <= h and not head[6] and head[7] == 3 and not head[8],
              f"{w}x{h}: the first view names the audience, and the figure's own header says what it shows in a dozen words and three chips: what is timed ('Run time with the bounds check:'), the grey chip 'off', the coloured chip 'on', and over the numbers 'times as long as off' (the baseline named, in the switch's own words); the old sentence is gone, and the header is not hidden from assistive technology ({aud[0][:30]!r} ends at {aud[1]:.0f}; the header ends at {head[5]:.0f}; {head[:4]})")
        words = pg.evaluate("""(() => [document.querySelectorAll('.ln-lbl').length,
            /SIMD/.test(document.getElementById('race-head').textContent) || [...document.querySelectorAll('#race-loops button')].some(b => /SIMD/.test(b.textContent))])()""")
        ck.ok(words[0] == 0 and not words[1],
              f"{w}x{h}: no floating phrase sits on the bars (the figure header's two chips say which bar is which) and the word SIMD is in no chip or lane of the figure ({words})")
        sw0 = pg.evaluate("(() => { const on = document.querySelector('#race-head .rh-on'); return [on.textContent.trim(), +getComputedStyle(on).opacity, getComputedStyle(on, '::after').content]; })()")
        pg.click("#race-sw")
        pg.wait_for_timeout(250)
        sw1 = pg.evaluate("(() => { const on = document.querySelector('#race-head .rh-on'); return [+getComputedStyle(on).opacity, getComputedStyle(on, '::after').content, document.getElementById('race').classList.contains('is-on')]; })()")
        pg.click("#race-sw")
        pg.wait_for_timeout(250)
        sw2 = pg.evaluate("+getComputedStyle(document.querySelector('#race-head .rh-on')).opacity")
        ck.ok(sw0[0] == "on" and sw0[1] == 1 and sw0[2] in ("none", "normal") and sw1[0] < 0.6 and "hidden" in sw1[1] and not sw1[2] and sw2 == 1,
              f"{w}x{h}: the figure's header changes with the switch: the 'on' chip is lit, then dimmed and marked '(hidden)' with the check off, then lit again ({sw0}, {sw1}, {sw2})")
        if w >= 641:
            cpu = pg.evaluate("""(() => { const g = document.getElementById('race-cpu'), l = document.querySelector('#race .cpu-l'), sel = g.querySelector('[aria-checked="true"]'), cs = getComputedStyle(g), ss = getComputedStyle(sel);
                const lr = l.getBoundingClientRect();
                return [l.textContent.trim(), g.getAttribute('aria-label'), cs.backgroundColor, ss.backgroundColor, parseFloat(cs.borderRadius) > 6, ss.boxShadow !== 'none', lr.width > 0 && getComputedStyle(l).display !== 'none', l.getAttribute('aria-hidden')]; })()""")
            ck.ok(cpu[0] == "Measured on" and cpu[1] == "CPU model" and cpu[7] == "true" and cpu[2] != cpu[3] and cpu[4] and cpu[5] and (cpu[6] or (641 <= w <= 1040)),
                  f"{w}x{h}: the processor choice is a segmented control: a recessed rounded track with the chosen segment raised and a different colour, so the chosen name reads as a pressed button; 'Measured on' sits quietly beside it except from 641 to 1040 px, where there is no room, and the group is named 'CPU model' for a screen reader ({cpu})")
        else:
            # on a phone the five tabs are one quiet line: "Measured on" and the chosen model with a chevron, a menu on tap (the system's own picker)
            cpus_ = [c for c in index["cpus"] if c["enough"]]
            q = pg.evaluate("""(() => { const s = document.getElementById('race-cpu-sel'), l = document.querySelector('#race .cpu-l'), g = document.getElementById('race-cpu'), line = document.querySelector('#race .cpu-q'),
                now = line.querySelector('.cpu-now'), chev = line.querySelector('.cpu-chev'), t = document.getElementById('cpu-now-t'), cs = getComputedStyle(s), ls = getComputedStyle(line), r = s.getBoundingClientRect(), lr = l.getBoundingClientRect(), nr = now.getBoundingClientRect(), lnr = line.getBoundingClientRect();
                return [l.textContent.trim(), l.getAttribute('aria-hidden'), lr.width > 0 && getComputedStyle(l).display !== 'none', s.getAttribute('aria-label'), [...s.options].map(o => o.textContent.trim()), s.options[s.selectedIndex].textContent.trim(),
                  Math.round(lnr.height), now.getAttribute('aria-hidden'), t.textContent.trim(), getComputedStyle(chev).backgroundImage.startsWith('url(') && chev.getBoundingClientRect().width > 0,
                  ls.backgroundColor === 'rgba(0, 0, 0, 0)' && parseFloat(ls.borderTopWidth) === 0 && ls.boxShadow === 'none', getComputedStyle(g).display,
                  lr.right <= nr.left + 1 && Math.abs((lr.top + lr.height / 2) - (nr.top + nr.height / 2)) < 12,
                  r.left <= nr.left && r.right >= nr.right && r.top <= nr.top && r.bottom >= nr.bottom && cs.opacity === '0', Math.round(r.height)]; })()""")
            ck.ok(q[0] == "Measured on" and q[1] == "true" and q[2] and q[3] == "CPU model" and q[4] == [c["cpu_short"] for c in cpus_] and q[5] == q[8] == next(c["cpu_short"] for c in cpus_ if c["slug"] == index["default_cpu"])
                  and q[6] >= 44 and q[14] >= 44 and q[7] == "true" and q[9] and q[10] and q[11] == "none" and q[12] and q[13],
                  f"{w}x{h}: on a phone the processor choice is one quiet line: 'Measured on' and the chosen model with a chevron on a plain background (no tabs, no fill, no border, no shadow), 44 px tall, with the system's own menu named 'CPU model' laid invisibly over the whole line so a tap anywhere on it opens the picker; the menu lists every model, and the line shows the chosen one ({q})")
            pg.focus("#race-cpu-sel")
            pg.keyboard.press("ArrowDown")
            pg.wait_for_timeout(250)
            kb = pg.evaluate("[S.cpu, document.getElementById('race-cpu-sel').value, document.querySelector('#race-cpu [aria-checked=\"true\"]').dataset.cpu, document.getElementById('cpu-now-t').textContent.trim(), document.querySelector('#race-cpu [aria-checked=\"true\"]').textContent.trim()]")
            ck.ok(kb[0] != index["default_cpu"] and kb[0] == kb[1] == kb[2] and kb[3] == kb[4],
                  f"{w}x{h}: the quiet line works from the keyboard (the arrow key changes the model, the race follows, the line shows the new name, the hidden tabs agree) ({kb})")
            pick_cpu(pg, index["default_cpu"])
            pg.wait_for_timeout(200)
            ck.ok(pg.evaluate("S.cpu") == index["default_cpu"] and pg.input_value("#race-cpu-sel") == index["default_cpu"] and pg.inner_text("#cpu-now-t") == next(c["cpu_short"] for c in cpus_ if c["slug"] == index["default_cpu"]), f"{w}x{h}: choosing the default model from the menu puts it back, and the line shows its name again")
        wip0 = pg.evaluate("(() => { const b = document.getElementById('wip-btn'), n = document.getElementById('wip-note'); return [b.tagName, b.getAttribute('aria-expanded'), n.hidden, b.textContent.trim()]; })()")
        pg.click("#wip-btn")
        wip1 = pg.evaluate("""(() => { const n = document.getElementById('wip-note'), r = n.getBoundingClientRect(), b = document.getElementById('wip-btn');
            return [n.hidden, n.textContent.trim(), r.left >= 0 && r.right <= innerWidth && r.top >= 0 && r.bottom <= innerHeight, b.getAttribute('aria-expanded'), n.getAnimations().length]; })()""")
        hs = no_hscroll(pg)
        pg.keyboard.press("Escape")
        wip2 = pg.evaluate("[document.getElementById('wip-note').hidden, document.activeElement.id]")
        pg.click("#wip-btn")
        pg.evaluate("document.querySelector('.hero h1').click()")  # a click on the page itself, away from the chip and the note
        wip3 = pg.evaluate("document.getElementById('wip-note').hidden")
        ck.ok(wip0 == ["BUTTON", "false", True, "Work in progress"]
              and not wip1[0] and wip1[1].startswith("More runs are still being added") and "may change" in wip1[1] and wip1[1].count(".") == 1 and wip1[2] and wip1[3] == "true" and wip1[4] == 0
              and hs and wip2 == [True, "wip-btn"] and wip3,
              f"{w}x{h}: the 'Work in progress' chip is a button; one click shows one sentence that says what is unfinished (more runs, text still edited, numbers may change), instantly, inside the view with no sideways scroll; Escape closes it and returns focus, so does a click elsewhere ({wip0}, {wip1}, {wip2}, {wip3})")
        ck.ok(pg.inner_text("#race-ratio").endswith("×") and len(pg.query_selector_all("#race-loops button")) == 8, f"{w}: the first view prints a measured ratio and offers all eight loop chips")
        f1 = pg.evaluate("document.getElementById('fig1').getBoundingClientRect().top")
        ck.ok(f1 < h * 3, f"{w}: the clickable heatmap is within three screens (the contrast band and the mechanism demo come first; Figure 1 starts at {f1:.0f} px)")
        if cap:
            hh = pg.evaluate("document.documentElement.scrollHeight")
            ck.ok(hh < cap, f"{w}: the main page is {hh} px long by default (under {cap})")
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
            r = pg.evaluate("(() => { const q = (s) => document.querySelector(s).getBoundingClientRect(); return [q('#race').bottom, q('.hero .scope').bottom, q('.toc-btn').bottom, q('.toc-btn').top]; })()")
            if v == 4 and w < 641:  # all eight lanes with their ratios, then at most a short scroll to the caption
                lb = pg.evaluate("document.getElementById('race-loops').getBoundingClientRect().bottom")
                ck.ok(lb <= h * 1.3 and r[1] <= h and r[2] <= h and r[3] >= 0, f"{tag}: the eight lanes and the scope line are in the first view, the caption within a short scroll ({round(lb)} px)")
            else:
                ck.ok(r[0] <= h and r[1] <= h and r[2] <= h and r[3] >= 0, f"{tag}: the whole finding (loop tiles, switch, CPU choice, ratio, scope line, the Contents button with Limits and Full details) is in the first view ({[round(x) for x in r]})")
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
            pick_cpu(pg, other["slug"])
            w2 = want(opc, sel)
            ck.ok(w2 is None or pg.inner_text("#race-ratio") == w2, f"{tag}: one click on {other['cpu_short']} prints that model's pooled ratio ({pg.inner_text('#race-ratio')} vs {w2})")
            pick_cpu(pg, index["default_cpu"])
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
        # read the frame once the fade has ended and the picture has stopped changing (a slow runner can still be mid-fade
        # after a fixed delay); the three readings must still be identical
        rp.wait_for_function("document.getAnimations().length === 0", timeout=8000)
        a2 = settled_sig(rp)
        rp.wait_for_timeout(900)
        a3 = settled_sig(rp)
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


def check_derived_wording(ck, page, dp, index, pooled, cpus, t1r, rec):
    """The sentences app.js derives from the verdicts. Every CPU model with enough jobs is named with what the written
    rules said about it (re-derived here from pooled.json, not copied from the page), the run-to-run notes cover every
    model that had comparable runs, and nothing reads as if every model had a verdict. Also the pass-level wording."""
    fx = lambda v: f"{v:.1f}" if v >= 2 else f"{v:.2f}"  # noqa: E731
    pat = {r[0]: r[-1] for r in t1r}
    intel_p, stable_p = dp.inner_text("#intel-p"), dp.inner_text("#stable-p")
    other, method, limits = dp.inner_text("#otherdraws"), dp.inner_text("#method-full"), dp.inner_text("#limits-full")
    rep = [c for c in cpus if c["reproduction"] and c["reproduction"]["checked"]]
    ck.ok(bool(rep) and all(f"{c['reproduction']['outside']} of {c['reproduction']['checked']}" in rec and f"{c['reproduction']['max_gap_pct']:.1f}%" in rec
                           and c["cpu_short"] in rec and c["cpu_short"] in method for c in rep),
          f"run-to-run movement: the note beside Table 1 and the Method entry name every model with comparable runs ({[c['cpu_short'] for c in rep]}), with its count outside and its largest gap")
    ck.ok(all(c["cpu_short"] in stable_p for c in cpus)
          and all(f"{sum(1 for r in c['per_run'] if r['form'])} of its {len(c['per_run'])} runs" in stable_p for c in cpus if c["stability"] == "stable")
          and all(f"{c['jobs']} jobs in {len(c['per_run'])} runs" in stable_p for c in cpus if c["stability"] != "stable" and c["form"] != "inconclusive")
          and "enough jobs in each of its" not in stable_p and "give the same pattern pooled" not in stable_p,
          "pooling note: every model is named with how many of its runs could be judged alone; a model whose runs cannot be compared is not called stable")
    inc = [c for c in cpus if c["form"] == "inconclusive"]
    ck.ok(all(c["cpu_short"] in limits and "inconclusive" in limits and "inconclusive" in pat[c["cpu_short"]]
              and (c["cpu_short"] in intel_p or "Xeon" not in c["cpu_short"]) for c in inc)
          and all("cannot be compared" in pat[c["cpu_short"]] for c in cpus if c["form"] == "map" and c["stability"] != "stable")
          and all("the same in every run judged alone" in pat[c["cpu_short"]] for c in cpus if c["stability"] == "stable")
          and "too few for a verdict" not in intel_p and "All CPU models drawn with enough jobs are AMD" not in limits
          and "Few jobs on two models" not in limits and "the only model with enough jobs" not in method,
          f"models the written rules left inconclusive ({[c['cpu_short'] for c in inc]}) are named with that word in Table 1, section 1 and the Limits; a model whose runs cannot be compared says so; no stale 'too few' wording")
    for c in inc:
        pc = next(q for q in pooled["cpus"] if q["cpu_model"] == c["cpu_model"])
        lim = 1 + pc["verdict"]["forward_limit_pct"] / 100
        ps = {q["cell_id"] for q in c["placement_sensitive"]}
        miss = [x for x in pc["cells"] if x["class"] == "kept" and x["size_class"] in ("L1", "L2") and x["cell_id"] not in ps
                and x["aligned"] and (x["aligned"]["ratio"] > lim or x["aligned"]["ci95"][1] > lim)]
        ck.ok(bool(miss) and all(x["cell_id"] in c["why"] for x in miss)
              and all(f"up to {fx(x['aligned']['ci95'][1])}×" in pat[c["cpu_short"]] and f"interval {fx(x['aligned']['ci95'][0])} to {fx(x['aligned']['ci95'][1])}×" in intel_p for x in miss),
              f"{c['cpu_short']}: Table 1 and section 1 give the judged forward loops that miss the written rule, with their interval, as the harness's own reason says ({[x['cell_id'] for x in miss]})")
    ck.ok(not re.search(r"\buses\s*[,.]", other) and not other.lstrip().startswith(",") and "Table 8" in other and other.count("Xeon 8370C") >= 1,
          "the note beside Table 1 about models without a row reads as a sentence (no empty list)")
    # every Xeon model with a row is named in section 1 with what the rules said (a verdict or none); a model drawn too rarely is named with its pooled job count;
    # no sentence says every model with a verdict is AMD
    xe = [c for c in cpus if "Xeon" in c["cpu_short"]]
    note1 = page.text_content("#cpu-note")
    words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    withv = [c for c in cpus if c["form"] != "inconclusive"]
    n_intel_v = sum(1 for c in withv if c["cpu_short"] in index["intel_forward"]["cpus"])
    few_ok = all(f"{f['cpu_short']} came up in {f['jobs']} pooled job" in intel_p and "too few to judge" in intel_p for f in index["page"]["cpus_few"])
    ck.ok(bool(xe) and all(c["cpu_short"] in intel_p for c in xe)
          and all((f"{c['cpu_short']} has a verdict" in intel_p) == (c["form"] != "inconclusive") for c in xe)
          and few_ok and "Every CPU model with a verdict is AMD" not in limits and "Every model with a verdict is AMD" not in note1
          and f"{words[len(withv)].capitalize()} CPU models have a verdict: {words[len(withv) - n_intel_v]} AMD and {words[n_intel_v]} Intel" in note1
          and all(c["cpu_short"] in limits for c in withv),
          f"section 1 and the note beside Table 1 name every Xeon model with a row ({[c['cpu_short'] for c in xe]}) with what the rules said, name the models drawn too rarely ({[f['cpu_short'] for f in index['page']['cpus_few']]}), and no longer say every model with a verdict is AMD")
    # a map by a narrow margin: Table 1, section 1, the Limits and the main page's limits box give the cell and its interval end (three decimals), and only for those models
    narrow = [(c, close_calls(c, pooled)) for c in cpus]
    nm = [c for c, cc in narrow if cc]
    cannot = page.text_content("#cannot")
    ck.ok(bool(nm)
          and all(("narrowly" in pat[c["cpu_short"]]) == bool(cc) for c, cc in narrow)
          and all((lambda n_: (f"{n_[1]:.3f}×" in pat[c["cpu_short"]]) if not n_[2] else ("×" not in pat[c["cpu_short"]].split(";")[0]))(min(cc, key=lambda q: abs(q[1] - lim_of(c, pooled))))
                  for c, cc in narrow if cc)  # the nearest call: a counted cell sets the verdict and its number is in the row; a left-out cell only gets the word there
          and all(f"{c['cpu_short']} passes the forward rule by a narrow margin" in limits for c in nm)
          and all(f"{hi:.3f}×" in limits for c, cc in narrow for _, hi, _ in cc)
          and all(f"{c['cpu_short']}" in cannot for c in nm) and "narrowly (Table 1)" in cannot
          and all(f"{hi:.3f}×" in intel_p for c, cc in narrow if "Xeon" in c["cpu_short"] for _, hi, _ in cc),
          f"narrow passes ({[(c['cpu_short'], [(i_, round(h_, 4)) for i_, h_, _ in cc]) for c, cc in narrow if cc]}): Table 1, section 1, the Limits and the main page's limits box say so with the interval ends, and no other model is called narrow")
    # what the narrow pass stands on is in the repository: the same model with its earlier, smaller pool, and the block bootstrap
    with open(os.path.join(REPO, "robustness", "results.json"), encoding="utf-8") as f_:
        rb = json.load(f_)["datasets"]["s7"]["cpus"]
    with open(os.path.join(REPO, "results", "s6-pooled", "pooled.json"), encoding="utf-8") as f_:
        s6 = json.load(f_)
    x6 = next((q for q in s6["cpus"] if "6973P" in q["cpu_model"]), None)
    c69 = next((c for c in cpus if "6973P" in c["cpu_short"]), None)
    cell6 = next((x for x in x6["cells"] if x["cell_id"] == "k03_stencil.L2"), None) if x6 else None
    lim6 = 1 + x6["verdict"]["forward_limit_pct"] / 100 if x6 else None
    grew = dp.text_content("#pool-grew")
    ck.ok(x6 is not None and c69 is not None and x6["jobs"] == 6 and x6["verdict"]["form"] == "inconclusive" and c69["jobs"] == 7 and c69["form"] == "map"
          and cell6 is not None and cell6["aligned"]["ci95"][1] > lim6
          and all(rb[c["cpu_model"]]["methods"]["b"]["form"] == c["form"] and rb[c["cpu_model"]]["jobs"] == c["jobs"] for c in cpus)
          and "With six pooled jobs the Xeon 6973P-C was inconclusive" in grew and "Its seventh job moved that cell under the limit" in grew
          and "A block bootstrap leaves its form as pooled" in grew
          and f"a block bootstrap on the {index['pooled']['jobs']}-job pool leaves the verdict of every CPU model unchanged" in " ".join(cannot.split()),
          "the narrow pass's history is in the repository: the Xeon 6973P-C had 6 jobs and was inconclusive in results/s6-pooled (its stencil at L2 ended above the limit), has 7 and a map now; "
          "the block bootstrap (robustness/results.json, s7) gives every model's pooled form")
    # Figure 1: a model with no verdict says so beside the switcher, and so does a map that stands by a narrow margin (it names the
    # cells and their interval ends and says what the rule leaves out); the others show nothing there
    for c in cpus:
        page.click(f'#cpu-seg [data-cpu="{c["slug"]}"]')
        page.wait_for_timeout(120)
        vt = page.inner_text("#cpu-verdict").strip()
        cc = close_calls(c, pooled)
        if c["form"] == "inconclusive":
            ck.ok(f"No verdict for {c['cpu_short']}" in vt and "inconclusive" in vt and "Table 1" in vt, f"Figure 1, {c['cpu_short']}: the no-verdict note names it")
        elif cc:
            above = left_out_above(c, pooled)
            ck.ok(vt.startswith(f"{c['cpu_short']}: the pattern held, by a narrow margin") and "More in Table 1 and the details" in vt
                  and all(f"{hi:.3f}×" in vt for _, hi, _ in cc) and all(f"{fx(r_)}× aligned" in vt for _, r_ in above) and (not above or "left out as placement-sensitive" in vt),
                  f"Figure 1, {c['cpu_short']}: a map by a narrow margin says so, with the interval ends {[(i_, round(h_, 4)) for i_, h_, _ in cc]} and the left-out cells above the limit {above}")
        else:
            ck.ok(vt == "", f"Figure 1, {c['cpu_short']}: no verdict note")
    page.click(f'#cpu-seg [data-cpu="{index["default_cpu"]}"]')
    page.wait_for_timeout(120)
    # pass-level wording: observed or inferred on every statement, linked to the saved notes
    pl = dp.inner_text("#pl-list")
    hrefs = dp.evaluate("[...document.querySelectorAll('#why-full a, #method-full a, #limits-full a')].map(a => a.href)")
    why = page.text_content("#why")
    ck.ok(dp.locator("#passlevel").count() == 1 and pl.count("(observed") >= 6 and "inferred" in pl and "Nothing here is timed" in dp.inner_text("#why-full")
          and any(h.endswith("investigate/vectorizer/reverse-stride2/README.md") for h in hrefs)
          and any(h.endswith("investigate/vectorizer/matmul/README.md") for h in hrefs)
          and sum(1 for h in hrefs if h.endswith("#passlevel")) >= 2,
          "details: the pass-level evidence is its own subsection, every statement labelled observed or inferred, linked to the two saved notes and from the Method and the Limits")
    ck.ok("observed" in why and "inferred" in why and page.locator('#why a[href="details.html#passlevel"]').count() == 1
          and page.locator('.mech-note a[href="details.html#passlevel"]').count() == 1 and "observed" in page.text_content(".mech-note"),
          "main page: the mechanism sentences say what is observed and what is inferred and link to the pass-level evidence (section 2 and the demo's note)")


def png_size(path):
    """[width, height] from a PNG header, or None when the file is not a PNG."""
    with open(path, "rb") as f:
        head = f.read(24)
    return list(struct.unpack(">II", head[16:24])) if head[:8] == b"\x89PNG\r\n\x1a\n" else None


def hero_image_checks(browser, base, ck, index):
    """docs/hero.png (the README image) and site/og.png (the share card) are pictures of the first screen. docs/hero.json
    lists what that screen showed when they were taken (scripts/capture_hero.py writes it); it must equal what the page
    shows now and what site/data says, so a first screen or a job count that changed after the capture fails here."""
    print("== the pictures of the first screen: docs/hero.png, site/og.png")
    from capture_hero import facts
    with open(os.path.join(REPO, "docs", "hero.json"), encoding="utf-8") as f:
        side = json.load(f)
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    pg.wait_for_timeout(1200)
    live = facts(pg)
    pg.close()
    again = ": run python scripts/capture_hero.py, look at docs/hero.png and site/og.png, then commit them with docs/hero.json"
    diff = {k: (side.get(k), v) for k, v in live.items() if side.get(k) != v}
    ck.ok(not diff, "docs/hero.json (what the README image and the share card were taken from) equals what the first screen shows now"
          + ("" if not diff else f" {diff}{again}"))
    dflt = next(c for c in index["cpus"] if c["slug"] == index["default_cpu"])
    tabs = [c["cpu_short"] for c in index["cpus"] if c["enough"]]
    ck.ok(side["cpu_tabs"] == tabs and side["selected_cpu"] == dflt["cpu_short"] and side["jobs"] == dflt["jobs"],
          f"the pictures show every CPU model with enough jobs ({tabs}) and the default model's job count ({dflt['jobs']}) from site/data; docs/hero.json has {side['cpu_tabs']} and {side['jobs']}"
          + ("" if side["cpu_tabs"] == tabs and side["jobs"] == dflt["jobs"] else again))
    sizes = {rel: png_size(os.path.join(REPO, *rel.split("/"))) for rel in side["images"]}
    ck.ok(sizes == {"docs/hero.png": [1440, 900], "site/og.png": [1200, 630]} and side["images"] == sizes,
          f"docs/hero.png is 1440 x 900 and site/og.png 1200 x 630, as docs/hero.json says ({sizes})")
    with open(os.path.join(SITE, "index.html"), encoding="utf-8") as f:
        src = f.read()
    alt = re.search(r'og:image:alt" content="([^"]*)"', src)
    ck.ok('og:image:width" content="1200"' in src and 'og:image:height" content="630"' in src and alt and "work in progress" in alt.group(1).lower(),
          "the share card's declared size is 1200 x 630 and its alt text says the work is in progress")


def phone_checks(browser, base, ck, index):
    """Narrow screens and the hero's small layouts: a work-in-progress marking at every phone width and no sideways
    scroll on either page from 320 px, an Intel model's no-verdict note on a phone, lane names never cut at tablet
    widths, and the hint pill clear of other parts in every hero variant."""
    print("== narrow screens: the marking, sideways scroll, the no-verdict note, lane names, the hint pill")
    pg = browser.new_page_plain(viewport={"width": 390, "height": 800})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    no_mark, wide = [], []
    for w in (320, 340, 360, 375, 380, 381, 384, 387, 388, 390, 414, 480, 520, 521, 600, 640):
        pg.set_viewport_size({"width": w, "height": 800})
        pg.wait_for_timeout(120)
        shown = pg.evaluate("""() => [...document.querySelectorAll('.bar-wip .wip-long, .hero .dateline')].filter(e => {
            const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
            return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && /in progress/i.test(e.textContent); }).length""")
        if not shown:
            no_mark.append(w)
        if not no_hscroll(pg):
            wide.append(w)
    ck.ok(not no_mark, f"main page: a work-in-progress marking is visible at every phone width from 320 to 640 px (none at: {no_mark})")
    ck.ok(not wide, f"main page: no sideways scroll at any width from 320 to 640 px (scrolls at: {wide})")
    # an Intel model with no verdict: the note beside Figure 1's switcher is visible on a phone, after tapping the hero's tab
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(150)
    with open(os.path.join(DATA, "pooled.json"), encoding="utf-8") as f:
        pooled_ = json.load(f)
    for c in index["cpus"]:
        if not c["enough"]:
            continue
        pick_cpu(pg, c["slug"])
        pg.wait_for_timeout(150)
        box = pg.evaluate("(() => { const e = document.getElementById('cpu-verdict'), r = e.getBoundingClientRect(); return [e.textContent.trim(), r.width, r.height]; })()")
        ctl = pg.evaluate("(() => { const c = document.querySelector('#controls .ctl'); return [getComputedStyle(c).display, c.getBoundingClientRect().height]; })()")
        few = pg.evaluate("(() => { const e = document.getElementById('cpu-few'), r = e.getBoundingClientRect(); return [e.textContent.trim().length, getComputedStyle(e).display, r.height]; })()")
        if c["form"] == "inconclusive":
            ck.ok(box[0].startswith(f"No verdict for {c['cpu_short']}") and box[1] > 100 and box[2] > 20 and ctl[0] != "none",
                  f"390: with {c['cpu_short']} chosen (no verdict) the note is on screen beside Figure 1 ({box[0][:40]!r}, {round(box[1])} x {round(box[2])} px)")
        elif close_calls(c, pooled_):
            ck.ok(box[0].startswith(f"{c['cpu_short']}: the pattern held, by a narrow margin") and box[1] > 100 and box[2] > 20 and ctl[0] != "none",
                  f"390: with {c['cpu_short']} chosen (a map by a narrow margin) the note is on screen beside Figure 1 ({box[0][:40]!r}, {round(box[1])} x {round(box[2])} px)")
        else:
            ck.ok(box[0] == "" and ctl[0] == "none", f"390: with {c['cpu_short']} chosen (a verdict) the CPU row is not shown and leaves no gap ({ctl})")
        # the note about the models drawn too rarely is for the desktop; on a phone it is hidden (Table 1 and the limits name them), and it never makes a gap
        if index["page"]["cpus_few"]:
            ck.ok(few[0] > 0 and few[1] == "none" and few[2] == 0, f"390: with {c['cpu_short']} chosen the 'not shown' note about the models drawn too rarely is hidden and takes no room ({few})")
    pg.close()
    # the details page: no sideways scroll at phone widths, with every fold open
    dp = browser.new_page_plain(viewport={"width": 390, "height": 800})
    dp.goto(base + "details.html", wait_until="networkidle")
    wait_details(dp)
    dp.evaluate("document.querySelectorAll('details').forEach(d => { d.open = true; })")
    wide = []
    for w in (320, 340, 360, 375, 390):
        dp.set_viewport_size({"width": w, "height": 800})
        dp.wait_for_timeout(150)
        if not no_hscroll(dp):
            wide.append((w, dp.evaluate("document.documentElement.scrollWidth")))
    ck.ok(not wide, f"details page: no sideways scroll from 320 to 390 px with every fold open (scrolls at: {wide})")
    dp.close()
    # lane names in the default hero: never cut, at any width from a small tablet up
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
    cut = []
    for w in (641, 700, 768, 900, 1000, 1040, 1041, 1100, 1260, 1440):
        pg.set_viewport_size({"width": w, "height": 900})
        pg.wait_for_timeout(120)
        cut += [(w, t) for t in pg.evaluate("""() => [...document.querySelectorAll('#race-loops button')].filter(b => {
            const t = b.querySelector('.tl'), r = t.getBoundingClientRect(), br = b.getBoundingClientRect();
            return t.scrollWidth > t.clientWidth + 1 || r.top < br.top - 1 || r.bottom > br.bottom + 1; }).map(b => b.querySelector('.tl').textContent)""")]
    ck.ok(not cut, f"hero: every lane name fits its column, on one line or wrapped to two inside its lane, from 641 to 1440 px ({cut[:3]})")
    pg.close()
    # the one-time hint pill ("flip the check") never sits on the Replay button, the CPU buttons, the caption or the readout
    clash, said = [], {}
    for v in (1, 2, 3, 4):
        for w, h in ((1440, 900), (1024, 768), (800, 900), (390, 844), (340, 800)):
            pg = browser.new_page_plain(viewport={"width": w, "height": h})
            pg.goto(f"{base}#hero={v}", wait_until="networkidle")
            wait_ready(pg)
            pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
            seen = False
            for _ in range(8):  # the hint appears about 1.7 s after the page starts and stays for 9 s
                pg.wait_for_timeout(500)
                got = pg.evaluate("""() => { const sub = document.querySelector('#race-sw .sw-sub'), hint = document.getElementById('sw-hint'),
                      h = getComputedStyle(sub).display !== 'none' ? sub : hint, cs = getComputedStyle(h);  /* up to 640 px (variant 4) the line under the switch's label does the hint's work */
                    if (h === hint && (h.hidden || cs.display === 'none' || +cs.opacity < 0.5)) return null;
                    const a = h.getBoundingClientRect(), sw = document.getElementById('race-sw').getBoundingClientRect();
                    return [h.innerText.trim(), a.right <= sw.right + 0.5 && a.left >= sw.left - 0.5,
                      ['#race-replay', '#race-cpu', '#race-cpu-sel', '#race-cap', '#race .race-read'].filter(s => { const e = document.querySelector(s); if (!e) return false;
                      const b = e.getBoundingClientRect(); return a.left < b.right - 1 && a.right > b.left + 1 && a.top < b.bottom - 1 && a.bottom > b.top + 1; })]; }""")
                if got is not None:
                    seen = True
                    said[(v, w)] = got[0]
                    if got[2] or not got[1]:
                        clash.append((v, w, got[2], "outside its switch" if not got[1] else ""))
                    break
            pg.close()
    ck.ok(not clash, f"the 'flip the check' hint never overlaps the Replay button, the CPU buttons or menu, the caption or the readout, and stays inside its switch, in any hero variant at 1440, 1024, 800, 390 or 340 px ({clash[:3]})")
    # the hint says what to do, in words that fit the width: the first move and its action on a wide screen, the first move on a mid-size one;
    # on a phone (up to 640 px) the switch is a settings row and the plain sentence under its label says what a tap changes
    tap_off = "Tap to turn off and see each loop without it."
    want = {(4, 1440): "Start here: flip it off", (4, 1024): "Start here", (4, 800): "Start here", (4, 390): tap_off, (4, 340): tap_off}
    ck.ok(all(said.get(k) == t for k, t in want.items()),
          f"hero 4: the hint beside the switch reads 'Start here: flip it off' at 1440 and 'Start here' at 1024 and 800 px; on a phone the sentence under the switch's label reads '{tap_off}' at 390 and at 340 px ({ {k: said.get(k) for k in want} })")
    # the second move: after the first use the hint is gone while the check is on, and while the check is off it asks for the way back
    # ("the check is off" is a dead end otherwise: every row reads 1.00x and the only instruction is the small readout line), inside its switch;
    # on a phone the sentence under the label stays and flips with the state (it says what a tap changes in either state)
    tap_on = "Tap to turn on and see each loop with it."
    back_want = {1440: "Now flip it on", 1024: "Flip it on", 800: "Flip it on", 390: tap_on, 340: tap_on}
    back_bad = []
    for w, text in back_want.items():
        pg = browser.new_page_plain(viewport={"width": w, "height": 900})
        pg.goto(f"{base}#hero=4", wait_until="networkidle")
        wait_ready(pg)
        pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
        probe = """() => { const sub = document.querySelector('#race-sw .sw-sub'), hint = document.getElementById('sw-hint'), h = getComputedStyle(sub).display !== 'none' ? sub : hint,
              cs = getComputedStyle(h), a = h.getBoundingClientRect(), sw = document.getElementById('race-sw').getBoundingClientRect();
            return { shown: !h.hidden && cs.display !== 'none' && +cs.opacity > 0.5, text: h.innerText.trim(), inside: a.right <= sw.right + 0.5 && a.left >= sw.left - 0.5,
              clash: ['#race-replay', '#race-cpu', '#race-cpu-sel', '#race-cap', '#race .race-read'].filter(s => { const e = document.querySelector(s); if (!e) return false;
                const b = e.getBoundingClientRect(); return a.left < b.right - 1 && a.right > b.left + 1 && a.top < b.bottom - 1 && a.bottom > b.top + 1; }) }; }"""
        pg.wait_for_timeout(900)
        pg.click("#race-sw")                    # first use: the check is off
        pg.wait_for_timeout(700)
        off = pg.evaluate(probe)
        pg.click("#race-sw")                    # back on: the hint is gone for good
        pg.wait_for_timeout(700)
        on = pg.evaluate(probe)
        pg.keyboard.press("c")                  # the key does the same as the switch
        pg.wait_for_timeout(700)
        off2 = pg.evaluate(probe)
        on_ok = (on["shown"] and on["text"] == tap_off and on["inside"]) if w <= 640 else not on["shown"]
        if not (off["shown"] and off["text"] == text and off["inside"] and not off["clash"] and on_ok and off2["shown"] and off2["text"] == text):
            back_bad.append((w, off, on["shown"], off2["text"]))
        pg.close()
    ck.ok(not back_bad, f"hero 4: after the first use the hint is gone while the check is on, and while it is off asks 'Now flip it on' (1440) or 'Flip it on' (1024, 800); on a phone (390, 340) the sentence under the label flips with the state ('{tap_off}' with the check on, '{tap_on}' with it off), inside its switch and off every other control, also after the C key ({back_bad[:2]})")


def wording_checks(browser, base, ck, index):
    """Sentences typed into the page that state a count, tied to the files the count comes from: the jobs that never
    returned (counted from the results folders), the 29-loop tally (from the saved compiler output), the baseline of
    the newer-toolchain tables (results/s4-pooled), and the Reproduce text."""
    print("== wording tied to data: lost jobs, the 29-loop tally, newer-toolchain captions, the Reproduce text")
    per = index["criteria"]["jobs_per_run"]
    norm = lambda s: re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", s.replace("(R)", "").lower()))
    counts, by_cpu = {}, {}
    for r in index["pooled"]["runs"]:
        d = glob.glob(os.path.join(REPO, "results", f"*-run-{r['run_id']}"))
        got = [x for x in glob.glob(os.path.join(d[0], "results-*")) if os.path.exists(os.path.join(x, "results.json"))] if d else []
        counts[r["run_id"]] = len(got)
        for x in got:
            by_cpu.setdefault(r["run_id"], []).append(re.match(r"results-(.*)-j\d+$", os.path.basename(x)).group(1))
    # three groups of runs: the original ones (flagged in the data: the first pooled runs), the cut ones (a later run that returned fewer
    # jobs than it started) and the whole ones (a later run that returned every job again)
    orig = {r["run_id"] for r in index["pooled"]["runs"] if r["original"]}
    later = [i for i in counts if i not in orig]
    cut = [i for i in later if counts[i] < per]
    whole = [i for i in later if counts[i] >= per]
    started, returned = len(counts) * per, sum(counts.values())
    orig_back, cut_back, whole_back = (sum(counts[i] for i in g) for g in (orig, cut, whole))
    ck.ok(returned == index["pooled"]["jobs"] and all(counts[r["run_id"]] == r["jobs"] for r in index["pooled"]["runs"]),
          f"results folders: {returned} jobs returned in {len(counts)} runs, as site/data says ({index['pooled']['jobs']})")
    page = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    page.goto(base, wait_until="networkidle")
    wait_ready(page)
    dp = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    dp.goto(base + "details.html", wait_until="networkidle")
    wait_details(dp)
    lost_full, lost_short = dp.text_content("#lost-full").replace(" ", " "), page.text_content("#lost-li").replace(" ", " ")
    cpu_bits, ab = [], {}
    for c in index["cpus"]:
        if not c["enough"]:
            continue
        mine = norm(c["cpu_model"])
        a, b, w = (sum(1 for i in g for s in by_cpu.get(i, []) if s == mine) for g in (orig, cut, whole))
        cpu_bits.append(f"{c['cpu_short']} {a}, {b} and {w}")
        ab[c["cpu_short"]] = (a, b, w)
    top = max(ab, key=lambda k: ab[k][0])
    ids = [r["run_id"] for r in index["pooled"]["runs"]]
    ck.ok(orig and cut and whole and max(ids.index(i) for i in orig) < min(ids.index(i) for i in cut) and max(ids.index(i) for i in cut) < min(ids.index(i) for i in whole),
          "the original runs come first in the run list, then the cut runs, then the runs that returned every job again, so 'the first 30 jobs, the next 45, the last 20' is in run order")
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        wf = f.read()
    # the last runs: the Actions step records say every job finished its check step and uploaded, and the workflow's limit is the 45 minutes the page names
    with open(os.path.join(REPO, "tests", "data", "s7_job_steps.json"), encoding="utf-8") as f:
        steps = json.load(f)
    step_jobs = [j for r in steps["runs"] for j in r["jobs"]]
    ck.ok({str(r["run"]) for r in steps["runs"]} == set(whole) and len(step_jobs) == whole_back == len(whole) * per
          and all(j["conclusion"] == "success" and j["timing"] == "success" and j["check"] == "success" and j["upload"] == "success" for j in step_jobs),
          f"tests/data/s7_job_steps.json: the {len(whole)} last runs, {len(step_jobs)} jobs, every one succeeded in its timing, check and upload steps (the check step ran before the upload)")
    ck.ok(started > returned and f"{len(counts)} runs started {started} jobs and {returned} returned results" in lost_full
          and f"The {len(orig)} runs that pooled first (the original runs) returned all {per}." in lost_full
          and f"The next {len(cut)} started {len(cut) * per} and returned {cut_back}" in lost_full
          and f"The last {len(whole)} were started after that limit was raised to 45 minutes" in lost_full and "and all their jobs returned" in lost_full
          and f"jobs by model, in the {len(orig)} original runs, the {len(cut)} cut runs and the last {len(whole)}, " in lost_full
          and all(b in lost_full for b in cpu_bits) and "was not tested" in lost_full and "cancelled in the next one" in lost_full
          and "22 minutes" in lost_full and "22-minute" in wf and "timeout-minutes: 45" in wf and orig_back == index["pooled"]["original"]["jobs"],
          f"details, Limits: the jobs that never returned ({started - returned} of {started}) are counted from the results folders, in three groups of runs ({len(orig)} original, {len(cut)} cut, {len(whole)} last), with the jobs per CPU model ({cpu_bits}) and the cause the workflow records")
    ck.ok(f"{started - returned} of the {started} jobs started returned nothing" in lost_short and "the pool is uneven across CPU models" in lost_short
          and f"({top}: {ab[top][0]} of the first {orig_back}, {ab[top][1]} of the next {cut_back}, {ab[top][2]} of the last {whole_back})" in lost_short
          and "effect on the ratios was not tested" in lost_short and page.locator("#lost-li").is_visible(),
          "main page, Limits box: the same count, short, with the effect on the ratios marked untested")
    pool_dd = dp.inner_text("#method-full")
    ck.ok(f"All {index['pooled']['jobs']} jobs that returned results" in pool_dd and f"{started - returned} more were started and returned nothing" in pool_dd
          and "every returned job that drew it" in dp.inner_text("#terms-full") and "every returned job that drew it" in page.inner_text("#terms"),
          "details Method, Pooling, and the definition of 'pooled' on both pages: the pool is the jobs that returned results, and the jobs that did not are counted")
    # the 29-loop tally, from the saved compiler output
    with open(os.path.join(REPO, "investigate", "vectorizer", "reverse-stride2", "extracted", "scalar-evolution.txt"), encoding="utf-8") as f:
        scev = f.read()
    yes = no = proj = 0
    for sec in re.split(r"^## ", scev, flags=re.M)[1:]:
        head = sec.split("\n", 1)[0]
        if head.startswith("c18,") and "hardening FAST" in head:
            m = re.search(r"tally: computable and vectorized (\d+), not computable and not vectorized (\d+), mismatch (\d+)", sec)
            yes, no = yes + int(m.group(1)), no + int(m.group(2))
            if head.startswith("c18, kernels,"):
                proj = int(m.group(1)) + int(m.group(2))
    total = yes + no
    pl = dp.text_content("#pl-list").replace(" ", " ")
    ck.ok(total > proj > 0 and f"In these {total} loops, vectorized exactly when every exit has a count." in pl
          and f"Of {total} loops compiled with the checks on ({proj} of this project’s loops and {total - proj} hand-written test variants), all {yes} with a count for every exit were vectorized and none of the {no} with an uncounted exit was" in pl
          and "a count does not guarantee vectorization" in pl and "not a general rule" in pl,
          f"details, pass-level evidence: the count rule is scoped to the {total} loops of the saved tally ({proj} project loops, {total - proj} test variants; {yes} counted and vectorized, {no} not) and says a count does not guarantee vectorization")
    page.click('#rows .row[data-k="k04_rev"]')
    open_full(page)
    why = page.inner_text("#fig2 .f2-why").replace(" ", " ")
    ck.ok(f"In the {total} loops compiled for the pass-level study ({proj} of this project’s loops and {total - proj} hand-written test variants), clang vectorized exactly when every exit had a count (observed)" in why
          and "In every loop tried" not in why,
          "Figure 2, reverse loop: the count rule names its 29-loop set (and no longer says every loop tried)")
    note = page.text_content(".mech-note").replace(" ", " ")
    ck.ok("In the reverse and stride-2 loops the check is an exit clang cannot count (observed" in note and "in the forward loops it can" in note
          and "Matrix multiply is rejected on cost" in note and "inferred" in note,
          "section 2, the demo's note: the uncounted exit is scoped to the reverse and stride-2 loops; the forward loops and matrix multiply are named as different")
    # the newer-toolchain tables: the clang 18 column comes from the original pool the rules named
    with open(os.path.join(REPO, "results", "s4-pooled", "pooled.json"), encoding="utf-8") as f:
        s4 = json.load(f)
    n_orig = sum(c["jobs"] for c in s4["cpus"])
    ck.ok(set(s4["runs"]) == orig and n_orig == orig_back == index["pooled"]["original"]["jobs"] and len(orig) == index["pooled"]["original"]["runs"]
          and index["pooled"]["original"]["source"] == "results/s4-pooled/pooled.json",
          f"results/s4-pooled is the pool of the original runs, the ones the page's data flags as original ({len(orig)} runs, {n_orig} jobs)")
    with open(os.path.join(DATA, "versions.json"), encoding="utf-8") as f:
        ver = json.load(f)
    caps = dp.evaluate("[...document.querySelectorAll('#ver-tables .tcap')].map(p => p.textContent)")
    tables = [(t, i, c) for t in ver["toolchains"] for i, c in enumerate(t["cpus"])]
    good_caps = 0
    for (t, i, c), cap in zip(tables, caps):
        jobs = next((x["jobs"] for x in s4["cpus"] if x["cpu_model"] == c["cpu_model"]), 0)
        if c["in_clang18_pool"]:
            says = (f"in the original {n_orig}-job pool ({jobs} job{'' if jobs == 1 else 's'} of this model)" in cap
                    and f"not in the {index['pooled']['jobs']}-job pool used elsewhere on this page" in cap)
        else:
            says = f"the original {n_orig}-job pool has no jobs on this CPU model" in cap
        good_caps += (f"Table V{t['version']}.{i + 1}." in cap and says
                      and "same CPU model’s pooled result from the main study" not in cap and "no clang 18 pool exists" not in cap)
    ck.ok(len(caps) == len(tables) > 0 and good_caps == len(tables),
          f"details 6b: every table caption names the clang 18 column's pool (the original {n_orig}-job pool, with this model's jobs in it) or says the model is not in it ({good_caps} of {len(tables)})")
    # the Reproduce text says what the command does
    box = page.text_content("#repro-box").replace(" ", " ")
    sec = page.text_content("#reproduce").replace(" ", " ")
    ck.ok("Check every number" in page.text_content("#repro-btn") and "clone of the repository" in box and "Python 3 and numpy" in box and "about an hour" in box
          and "does not measure anything new" in box and "Playwright" in box
          and "clone of the repository" in sec and "Python 3 and numpy" in sec and "about an hour" in sec and "it measures nothing new" in sec,
          "the Reproduce button and section 11 say the command re-checks the stored results, in a clone, with Python 3 and numpy, in about an hour, and measures nothing new")
    page.close()
    dp.close()


ARM_KERNEL_NAMES = {
    "k01_sum_fwd": "Forward sum", "k02_add_fwd": "Forward add, two arrays", "k03_stencil": "Stencil, three neighbours",
    "k04_rev": "Reverse loop", "k05_stride2": "Stride-2 loop", "k06_gather": "Gather through an index",
    "k07_hist": "Histogram", "k08_matmul": "Matrix multiply, inner loop",
}
ARM_SHORT_NAMES = {
    "k01_sum_fwd": "forward sum", "k02_add_fwd": "forward add", "k03_stencil": "stencil", "k04_rev": "reverse",
    "k05_stride2": "stride-2", "k06_gather": "gather", "k07_hist": "histogram", "k08_matmul": "matrix multiply",
}
ARM_CLASS_WORDS = {"lost": "loses SIMD", "kept": "keeps SIMD", "off_axis": "off the axis"}
ARM_VERBS = {"lost": "loses SIMD under the check", "kept": "keeps SIMD", "off_axis": "is not vectorized in either build"}


def arm_checks(browser, base, ck, index, allowed, saved, shots):
    """The Arm column, tied to site/data/arm64.json: section 6a and Figure 7 on the main page, section 6d with Tables 12 and 13 on the
    details page. Every printed value is recomputed here from the data file (not read back from the page's own code): the verdict form
    (INCONCLUSIVE, not a map, with the missed cell named), the 16-cell table, the compiler facts per loop, the floors, the matrix-multiply
    reading (marked as consistent with, and not tested), the plan against the result, the limits, the Reproduce command, the figure's
    rows, marks, readout, clicks and keys, a text equivalent, no sideways scroll at 390 px, no console errors, and no stale sentence."""
    print("== the Arm column: section 6a and Figure 7 (main), section 6d and Tables 12 and 13 (details)")
    with open(os.path.join(DATA, "arm64.json"), encoding="utf-8") as f:
        arm = json.load(f)
    lr_ = lambda v: f"{v:.2f}" if v >= 2 else f"{v:.3f}"  # noqa: E731
    fx_ = lambda v: f"{v:.1f}" if v >= 2 else f"{v:.2f}"  # noqa: E731
    norm = lambda s: " ".join(s.replace(" ", " ").split())  # noqa: E731

    def pct_s(v):
        return "0%" if v == 0 else f"{v:.4f}%" if v < 0.01 else f"{v:.3f}%" if v < 0.1 else f"{v:.2f}%" if v < 1 else f"{v:.1f}%"

    def iv(c):
        a, b = lr_(c["ci95"][0]), lr_(c["ci95"][1])
        return f"{lr_(c['ratio'])}×" if a == b else f"{lr_(c['ratio'])}× ({a} to {b})"

    def range_x(lo, hi):
        a, b = fx_(lo), fx_(hi)
        return f"{a}×" if a == b else f"{a}–{b}×"

    def cell_name(cid):
        k, sz = cid.split(".")
        return f"the {ARM_SHORT_NAMES[k]} loop at the {sz} size"

    def join_and(xs):
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

    with open(os.path.join(DATA, "dsweep.json"), encoding="utf-8") as f:
        ds_arm = next(m for m in json.load(f)["models"] if m["cpu_short"] == arm["cpu_short"])  # the row-length sweep's Arm model (its word is named in 6d's matrix-multiply paragraph)
    cells = {c["cell_id"]: c for c in arm["cells"]}
    kern = {k["kernel"]: k for k in arm["kernels"]}
    x86 = arm["x86"]["cells"]
    x86name = arm["x86"]["model"]["cpu_short"]
    V, M, SM = arm["verdict"], arm["machine"], arm["summary"]
    ver = lambda s: re.search(r"\d+\.\d+\.\d+", s).group(0)  # noqa: E731
    clang, libcxx = f"clang {ver(M['toolchain']['clang'])}", f"libc++ {ver(M['toolchain']['libcxx_package'])}"
    missed = [cells[i] for i in V["forward_missed"]]

    def med(k):
        xs = sorted((x86[f"{k}.{sz}"].get("aligned") or x86[f"{k}.{sz}"]["as_compiled"])["ratio"] for sz in ("L1", "L2") if f"{k}.{sz}" in x86)
        return (xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2) if xs else -1

    order = sorted((k["kernel"] for k in arm["kernels"]), key=lambda k: -med(k))
    ck.ok(index["sections"].get("arm64") == "data/arm64.json" and V["form"] == "inconclusive" and arm["criteria"]["same_as_x86_pool"],
          f"the Arm file is registered in index.json and its pooled verdict form is {V['form']!r}, under the same rule file as the x86-64 pool")

    # ---- the main page, every section open, 1280 wide
    errors = []
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    watch(pg, errors)
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_function("document.querySelectorAll('#arm-rows .row').length === 8 && document.getElementById('arm-read').textContent.length > 0", timeout=20000)
    pg.wait_for_timeout(300)
    where = pg.evaluate("""() => { const s = [...document.querySelectorAll('.body section[id]')].map(x => x.id), i = s.indexOf('arm');
        const h = document.querySelector('#arm > h2 .secno'); return [s[i - 1], s[i + 1], h && h.textContent.trim()]; }""")
    ck.ok(where == ["siblings", "realworld", "6a"], f"main page: Arm is section 6a, between section 6 and the real programs ({where})")
    gist = norm(pg.inner_text("#arm .gist"))
    lost_rng = f"{fx_(SM['lost']['min'])}× to {fx_(SM['lost']['max'])}×"
    f1 = arm["forward_loops"]["L1"]["as_compiled"]
    SS_ = arm["seed_sensitivity"]
    DC_ = SS_["deciding_cell"]
    ck.ok(f"{arm['cpu_short']}, {arm['jobs']} jobs" in gist and lost_rng in gist and f"{lr_(f1['min'])}× to {lr_(f1['max'])}× at L1" in gist
          and "inconclusive" in gist and "reverse and stride-2 lose SIMD" in gist and f"by a margin of {DC_['margin_over_limit']:.4f}" in gist
          and "that most other bootstrap seeds reverse" in gist and DC_["alt_draws"] - DC_["alt_at_or_above_limit"] > DC_["alt_draws"] / 2 and len(gist.split()) <= 50,
          f"6a gist: the core and job count, the lost-SIMD range ({lost_rng}), the forward range at L1, the verdict form 'inconclusive' with its margin and the statement that most other seeds reverse it (true in the data), in at most 50 words ({len(gist.split())})")
    what = norm(pg.inner_text("#arm-what"))
    ck.ok(f"{len(arm['runs'])} runs of {arm['criteria']['jobs_per_run']} jobs" in what and f"a {M['cpu_model']} core" in what and clang in what and libcxx in what and "FAST mode at -O2" in what
          and "unchanged" in what and "other byte counts on the x86-64 models" in what and pg.evaluate("document.querySelectorAll('#arm-what code.nowrap').length") == 1
          and pg.evaluate("getComputedStyle(document.querySelector('#arm-what code.nowrap')).whiteSpace") == "nowrap",
          "6a: what ran (runs, jobs per run, the one core type, the toolchain, FAST mode in a non-breaking -O2, rules unchanged, and that the x86-64 working sets have other byte counts) from the data")
    why = norm(pg.inner_text("#arm-why"))
    mc = missed[0]
    aa_l2 = arm["noise"]["identical_binary_aa"]["L2"]["pooled"]
    ck.ok(len(missed) == 1 and cell_name(mc["cell_id"]) in why and f"a ratio of {lr_(mc['aligned']['ratio'])}× aligned" in why
          and f"from {lr_(mc['aligned']['ci95'][0])} to {lr_(mc['aligned']['ci95'][1])}×, past the {fx_(V['limit'])}× limit" in why
          and f"That miss is {DC_['margin_over_limit']:.4f}" in why
          and f"({DC_['alt_draws'] - DC_['alt_at_or_above_limit']} of {DC_['alt_draws']} put it under the limit, at a median of {lr_(DC_['alt_hi']['median'])})" in why
          and f"even an identical binary against itself spreads by ±{pct_s(aa_l2['half_width_pct'])}" in why
          and "these data cannot separate inconclusive from a map at this cell" in why and "section 6d" in why
          and "is a map" not in why and "holds" not in why and "the jobs disagree" not in why and "A/A floor" not in why,
          f"6a: the reason for INCONCLUSIVE names the missed cell ({mc['cell_id']}) with its ratio and interval, says the margin is inside the bootstrap's seed noise and that an identical binary spreads as widely at L2, and does not blame the jobs or the L1 A/A floor")
    mm = cells["k08_matmul.L1"]
    mmx = x86["k08_matmul.L1"]
    mtxt = norm(pg.inner_text("#arm-mm"))
    ck.ok(kern["k08_matmul"]["class"] == "kept" and mmx["class"] == "lost" and f"costs {fx_(mm['as_compiled']['ratio'])}× at L1 ({fx_(mm['aligned']['ratio'])}× aligned)" in mtxt
          and f"against {fx_(mmx['as_compiled']['ratio'])}× on {x86name}, where the same loop loses SIMD" in mtxt and "Where the extra time goes is not shown." not in mtxt,
          "6a: the matrix-multiply sentence gives the Arm and the x86-64 numbers from the data; the stale 'Where the extra time goes is not shown.' is gone (the row-length sweep's sentence replaces it, checked in dsweep_checks)")
    # the more-link names section 6d, and the caption's Table 12 link goes to the table's own caption
    ck.ok(pg.evaluate("document.querySelectorAll('#arm a[href=\"details.html#arm-full\"]').length") == 1 and pg.evaluate("document.querySelectorAll('#arm-cap a[href=\"details.html#arm-t1-cap\"]').length") == 1
          and "section 6d" in pg.inner_text("#arm .more-link"), "6a: the more-link names section 6d of the details page, and the caption's 'Table 12' links to that table's caption")
    bad = page_numbers(pg, allowed, "#arm") + page_numbers(pg, allowed, "#arm-avg")
    ck.ok(not bad, "6a and the Arm paragraph of section 10: every number printed is in the data" + ("" if not bad else f": {bad[:4]}"))

    # ---- Figure 7: rows, marks, text equivalent
    rows = pg.evaluate("[...document.querySelectorAll('#arm-rows .row')].map(b => b.dataset.k)")
    ck.ok(rows == order, f"Figure 7: eight rows in Figure 1's order (by the {x86name} aligned ratio): {rows}")
    bad_rows = []
    for k in order:
        info = pg.evaluate("""(k) => { const r = document.querySelector('#arm-rows .row[data-k="' + k + '"]');
            return [r.className, r.querySelectorAll('.mk').length, r.querySelectorAll('.mk.ps').length, r.querySelectorAll('.wh').length, r.querySelectorAll('.xm').length,
                    r.querySelector('.val').textContent, r.getAttribute('aria-label'), r.getAttribute('role')]; }""", k)
        rs = [cells[f"{k}.{sz}"]["aligned"]["ratio"] for sz in ("L1", "L2")]
        nps = sum(1 for sz in ("L1", "L2") if cells[f"{k}.{sz}"]["placement_sensitive"])
        cls = {"lost": "c-lost", "kept": "c-kept", "off_axis": "c-none"}[kern[k]["class"]]
        ok_ = (cls in info[0].split() and info[1] == 2 and info[2] == nps and info[3] == 2 and info[4] == 2 and info[5] == range_x(min(rs), max(rs))
               and {"lost": "loses SIMD", "kept": "keeps SIMD", "off_axis": "no SIMD in either build"}[kern[k]["class"]] in info[6]
               and "on Arm" in info[6] and ARM_KERNEL_NAMES[k] in info[6] and x86name in info[6] and info[7] == "option")
        if not ok_:
            bad_rows.append((k, info))
    ck.ok(not bad_rows, f"Figure 7: every row has its class colour, two Arm marks and two intervals, two {x86name} bars, the aligned range as its value, the placement-sensitive rings, and an aria-label that says the class and both machines ({bad_rows[:1]})")
    # the figure names the model it is drawn against, defines both columns, and does not follow Figure 1's CPU buttons
    cap7 = norm(pg.inner_text("#arm-cap"))
    ticks_before = pg.evaluate("[...document.querySelectorAll('#arm-rows .xm')].map(e => Math.round(e.getBoundingClientRect().left))")
    cpu_btns = pg.evaluate("[...document.querySelectorAll('#cpu-seg button')].map(b => [b.dataset.cpu, b.getAttribute('aria-checked') === 'true'])")
    others = [b for b in cpu_btns if not b[1]]
    cpu_now = next(b[0] for b in cpu_btns if b[1])
    if others:
        pg.evaluate("document.getElementById('fig1').scrollIntoView()")
        pg.click(f'#cpu-seg button[data-cpu="{others[0][0]}"]')
        pg.wait_for_timeout(300)
    ticks_after = pg.evaluate("[...document.querySelectorAll('#arm-rows .xm')].map(e => Math.round(e.getBoundingClientRect().left))")
    ck.ok(norm(pg.inner_text("#arm-fig-title")) == f"Eight loops on an Arm core, beside {x86name}" and "Figure 1" not in pg.inner_text("#arm-fig-title")
          and "every hot loop on a 64-byte boundary (aligned)" in cap7 and "the code as clang laid it out (as compiled)" not in cap7
          and "Aligned: every hot loop starts on a 64-byte boundary in both builds" in pg.evaluate("document.getElementById('arm-cap').textContent")
          and "As compiled: the binaries exactly as clang emitted them" in pg.evaluate("document.getElementById('arm-cap').textContent")
          and f"The grey ticks are always {x86name}, the page’s default model; they do not follow Figure 1’s CPU buttons" in cap7
          and bool(others) and ticks_before == ticks_after and len(ticks_before) == 16,
          f"Figure 7: the title and caption name {x86name} (the grey ticks' model), define aligned and as compiled, and the ticks do not move when Figure 1's CPU button changes ({len(others)} other models offered)")
    if others:
        pg.click(f'#cpu-seg button[data-cpu="{cpu_now}"]')
        pg.wait_for_timeout(200)
    shapes =pg.evaluate("""() => { const o = {}; for (const r of document.querySelectorAll('#arm-rows .row')) { const c = [...r.classList].find(x => x.startsWith('c-')), i = r.querySelector('.name i'), m = r.querySelector('.mk.l1'), s = getComputedStyle(i);
        o[c] = [s.transform, s.borderRadius, getComputedStyle(m).transform, i.getAttribute('title'), i.getAttribute('aria-hidden')]; } return o; }""")
    sig = {k: (v[0], v[1]) for k, v in shapes.items()}
    ck.ok(len(sig) == 3 and len(set(sig.values())) == 3 and all(v[3] for v in shapes.values()) and shapes["c-lost"][0] != "none" and shapes["c-lost"][2] != "none" and shapes["c-kept"][2] == "none",
          f"Figure 7: the loop's class is a shape as well as a colour (diamond, circle, square) on the name dot and on the marks, and the dot carries a title ({sig})")
    geo = pg.evaluate("""() => { const sel = document.querySelector('#arm-rows .row[aria-selected=true]'), out = {};
        const lum = (rgb) => { const v = rgb.match(/[\\d.]+/g).slice(0, 3).map(Number).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
        const cr = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
        const tick = sel.querySelector('.xm.l1'), tl2 = sel.querySelector('.xm.l2');
        out.contrastFill = cr(getComputedStyle(tick).backgroundColor, getComputedStyle(sel).backgroundColor);
        out.contrastRing = cr(getComputedStyle(tl2).boxShadow.match(/rgb[^)]*\\)/)[0], getComputedStyle(sel).backgroundColor);
        out.bad = [];
        for (const r of document.querySelectorAll('#arm-rows .row')) { const a = r.querySelector('.xm.l1').getBoundingClientRect(), b = r.querySelector('.mk.l1').getBoundingClientRect(), c = r.querySelector('.xm.l2').getBoundingClientRect(), d = r.querySelector('.mk.l2').getBoundingClientRect();
          if (!(a.top < b.top - 2 && a.bottom > b.top && c.bottom > d.bottom + 2 && c.top < d.bottom && getComputedStyle(r.querySelector('.xm.l1')).zIndex === '1')) out.bad.push(r.dataset.k); }
        return out; }""")
    ck.ok(geo["contrastFill"] >= 3 and geo["contrastRing"] >= 3 and not geo["bad"],
          f"Figure 7: the grey ticks are at least 3:1 against the selected row ({geo['contrastFill']:.2f}, ring {geo['contrastRing']:.2f}) and stand out of their dots, drawn above them ({geo['bad']})")
    ck.ok(pg.evaluate("(() => { const l = document.getElementById('arm-rows'); return l.getAttribute('role') === 'listbox' && /arrow keys/.test(l.getAttribute('aria-label')) && document.getElementById('arm-read').getAttribute('aria-live') === 'polite'; })()")
          and pg.evaluate("document.querySelectorAll('#arm-rows .row[tabindex=\"0\"]').length") == 1 and "Figure 7." in pg.inner_text("#arm-cap") and "Select a row" in pg.inner_text("#arm-cap"),
          "Figure 7: a listbox with one tab stop, a live readout and a caption that says how to select; the numbers are also in Table 12 (text equivalent)")
    # the default selection and the readout
    sel = pg.evaluate("document.querySelector('#arm-rows .row[aria-selected=true]').dataset.k")
    ro = lambda: pg.evaluate("""() => [document.querySelector('#arm-read .ar-head').textContent, [...document.querySelectorAll('#arm-read .ar-tbl tbody tr')].map(r => [...r.children].map(c => c.textContent)),
                                       document.querySelector('#arm-read .ar-note').textContent]""")  # noqa: E731
    head, trs, note = ro()
    c1, c2 = cells["k04_rev.L1"]["aligned"], cells["k04_rev.L2"]["aligned"]
    ck.ok(sel == "k04_rev" and head.startswith("Reverse loop loses SIMD under the check on Arm and on " + x86name)
          and trs[0] == [arm["cpu_short"], iv(c1), iv(c2)] and trs[1] == [x86name, iv(x86["k04_rev.L1"]["aligned"]), iv(x86["k04_rev.L2"]["aligned"])]
          and f"{kern['k04_rev']['builds']['none']['neon_instructions']} without the checks, {kern['k04_rev']['builds']['fast']['neon_instructions']} with them" in note
          and kern["k04_rev"]["builds"]["fast"]["why_not_vectorized"] in note,
          f"Figure 7: the reverse loop is selected first and its readout is the data's (aligned L1 {iv(c1)}, {x86name} {iv(x86['k04_rev.L1']['aligned'])}, NEON counts, the compiler's remark)")
    # a loop that is not vectorized in either build: the compiler's remark is the checked build's alone, and the checks-off reason is said to be unshown
    off_ok = []
    for kk in [k_ for k_ in order if kern[k_]["class"] == "off_axis"]:
        pg.click(f'#arm-rows .row[data-k="{kk}"]')
        _, _, note_ = ro()
        f_, n_ = kern[kk]["builds"]["fast"], kern[kk]["builds"]["none"]
        off_ok.append(note_.startswith(f"Not vectorized in either build. Clang’s remark with the checks on: “{f_['why_not_vectorized']}”; its reason with the checks off is not shown here. "
                                       f"The listing grows from {n_['asm_lines']} to {f_['asm_lines']} lines.")
                      and "The L2 figure is the rougher of the two" in note_ and note_.endswith("(details page, section 6d)."))
    ck.ok(len(off_ok) >= 2 and all(off_ok), f"Figure 7: gather and histogram say the remark is the checked build's alone and that the checks-off reason is not shown ({len(off_ok)} readouts), and every readout flags L2 as the rougher size")
    # click a row: matrix multiply
    pg.click('#arm-rows .row[data-k="k08_matmul"]')
    head, trs, note = ro()
    m1, m2 = cells["k08_matmul.L1"], cells["k08_matmul.L2"]
    ck.ok(pg.evaluate("document.querySelector('#arm-rows .row[aria-selected=true]').dataset.k") == "k08_matmul"
          and head.startswith(f"Matrix multiply, inner loop keeps SIMD on Arm; on {x86name} it loses SIMD under the check.")
          and trs[0] == [arm["cpu_short"], iv(m1["aligned"]), iv(m2["aligned"])] and trs[1][1] == iv(x86["k08_matmul.L1"]["aligned"])
          and "Placement-sensitive at L1 and L2" in note and f"{m1['placement']['d']['ratio']:.3f} and {m2['placement']['d']['ratio']:.3f}" in note
          and f"The SIMD loop is the same {kern['k08_matmul']['simd_loop']['as_compiled']['fast_instructions']} instructions with the checks off and on, with the same opcodes;" in note
          and f"the listing grows from {kern['k08_matmul']['builds']['none']['asm_lines']} to {kern['k08_matmul']['builds']['fast']['asm_lines']} lines." in note,
          "Figure 7: a click on matrix multiply moves the selection and the readout: keeps SIMD on Arm, loses it on the x86-64 model, same SIMD loop, placement-sensitive with its two ratios")
    # the column toggle: as compiled
    pg.click('#arm-col-seg button[data-col="compiled"]')
    rs = [cells[f"k08_matmul.{sz}"]["as_compiled"]["ratio"] for sz in ("L1", "L2")]
    head, trs, note = ro()
    ck.ok(pg.get_attribute('#arm-col-seg button[data-col="compiled"]', "aria-checked") == "true"
          and pg.inner_text('#arm-rows .row[data-k="k08_matmul"] .val').strip() == range_x(min(rs), max(rs))
          and trs[0][1] == iv(m1["as_compiled"]) and "as compiled" in pg.inner_text("#arm-cap") and "as compiled" in pg.get_attribute('#arm-rows .row[data-k="k08_matmul"]', "aria-label"),
          f"Figure 7: the 'as compiled' button redraws every row and the readout ({range_x(min(rs), max(rs))}, {iv(m1['as_compiled'])})")
    # keys: the toggle (arrow keys) and the rows (arrows, Home, End)
    pg.focus('#arm-col-seg button[aria-checked="true"]')
    pg.keyboard.press("ArrowLeft")
    ck.ok(pg.get_attribute('#arm-col-seg button[data-col="aligned"]', "aria-checked") == "true" and pg.evaluate("document.activeElement.dataset.col") == "aligned",
          "Figure 7: the arrow keys move the aligned / as compiled switch")
    pg.focus('#arm-rows .row[aria-selected="true"]')
    seq = []
    for key in ("ArrowUp", "ArrowDown", "End", "Home", "ArrowUp"):
        pg.keyboard.press(key)
        seq.append(pg.evaluate("[document.querySelector('#arm-rows .row[aria-selected=true]').dataset.k, document.activeElement.dataset.k]"))
    i8 = order.index("k08_matmul")
    ck.ok(seq == [[order[i8 - 1]] * 2, [order[i8]] * 2, [order[-1]] * 2, [order[0]] * 2, [order[0]] * 2],
          f"Figure 7: the arrow keys, Home and End move the selection and the focus together, without wrapping ({[s[0] for s in seq]})")
    # the link resolves
    pg.goto(base + "details.html#arm-full", wait_until="networkidle")
    pg.wait_for_function("document.querySelectorAll('#arm-t1 tbody tr').length === 16", timeout=20000)
    top = pg.evaluate("document.getElementById('arm-full').getBoundingClientRect().top")
    ck.ok(-5 <= top < 900, f"the link to details.html#arm-full lands on section 6d (its top at {top:.0f} px)")
    shot(pg, saved, shots, "arm-details-1280.png", "#arm-full")
    pg.close()
    # the caption's 'Table 12' link lands where the table is, not a screen above it (the details page loads its text after the browser's jump)
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(base + "details.html#arm-t1-cap", wait_until="networkidle")
    pg.wait_for_function("document.querySelectorAll('#arm-t1 tbody tr').length === 16", timeout=20000)
    pg.wait_for_timeout(600)
    land = pg.evaluate("(() => { const c = document.getElementById('arm-t1-cap').getBoundingClientRect(), w = document.getElementById('arm-t1-wrap').getBoundingClientRect(); return [Math.round(c.top), Math.round(w.top), Math.round(w.bottom)]; })()")
    ck.ok(-5 <= land[0] < 450 and land[1] < 900 and land[2] > 300, f"the link to details.html#arm-t1-cap lands on Table 12's caption with the table below it on screen (caption top {land[0]}, table top {land[1]}, bottom {land[2]})")
    pg.close()
    # the same two links in a browser that does not keep the target in place while the page above it grows (scroll anchoring off:
    # Chromium on the Linux runner stayed where its first jump left it, with the target 17,000 px below the screen)
    no_anchor = "document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = '*{overflow-anchor:none !important}'; document.head.append(s); })"
    for frag, probe in (("arm-full", "document.getElementById('arm-full').getBoundingClientRect().top"),
                        ("arm-t1-cap", "document.getElementById('arm-t1-cap').getBoundingClientRect().top")):
        pg = browser.new_page(viewport={"width": 1280, "height": 900})
        pg.add_init_script(no_anchor)
        pg.goto(base + "details.html#" + frag, wait_until="networkidle")
        pg.wait_for_function("document.querySelectorAll('#arm-t1 tbody tr').length === 16", timeout=20000)
        top = pg.evaluate(f"Math.round({probe})")
        ck.ok(-5 <= top < 450, f"the link to details.html#{frag} lands on its target when the browser does not follow it as the page grows (top at {top} px)")
        pg.close()
    # a reader who has scrolled is left where they are: the late landing never pulls them back
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    pg.add_init_script(no_anchor)
    pg.goto(base + "details.html#arm-full", wait_until="networkidle")
    pg.wait_for_function("document.querySelectorAll('#arm-t1 tbody tr').length === 16", timeout=20000)
    y0 = pg.evaluate("scrollY")
    pg.mouse.move(640, 450)
    pg.mouse.wheel(0, -1500)
    pg.wait_for_timeout(300)
    y1 = pg.evaluate("scrollY")
    pg.wait_for_timeout(1000)  # past the late landings (fonts, the 600 ms timer)
    y2 = pg.evaluate("scrollY")
    ck.ok(y1 < y0 - 800 and abs(y2 - y1) < 3, f"a reader who scrolled up from the linked section is not pulled back to it (scrollY {y0:.0f}, after the wheel {y1:.0f}, a second later {y2:.0f})")
    pg.close()

    # ---- the collapsed main page: one gist and a Details button; the figure behind it
    pg = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_function("document.querySelectorAll('#arm-rows .row').length === 8", timeout=20000)
    st = pg.evaluate("""() => { const s = document.getElementById('arm'), b = document.getElementById('sb-arm'), m = s.querySelector(':scope > .sec-more');
        return [s.querySelector(':scope > .gist').getBoundingClientRect().height > 0, b.hidden, m.textContent.trim(), m.getAttribute('aria-expanded')]; }""")
    ck.ok(st[0] and st[1] and st[2] == "Details" and st[3] == "false", f"6a, collapsed: the gist shows, the figure and text sit behind one Details button ({st})")
    pg.click("#arm .sec-more")
    pg.evaluate("document.getElementById('arm').scrollIntoView()")
    pg.wait_for_timeout(250)
    ck.ok(pg.is_visible("#arm-rows") and pg.is_visible("#arm-read") and pg.is_visible("#arm-col-seg"), "6a: the Details button opens Figure 7, its switch and its readout")
    pg.click('#arm-rows .row[data-k="k05_stride2"]')
    ck.ok(pg.evaluate("document.querySelector('#arm-rows .row[aria-selected=true]').dataset.k") == "k05_stride2" and "Stride-2 loop" in pg.inner_text("#arm-read .ar-head"),
          "6a, collapsed then opened: a click on a row works the same")
    shot(pg, saved, shots, "arm-fig-1280.png", "#arm")
    pg.close()

    # ---- the details page, 1280 wide
    errors_d = []
    dp = browser.new_page(viewport={"width": 1280, "height": 900})
    watch(dp, errors_d)
    dp.goto(base + "details.html", wait_until="networkidle")
    dp.wait_for_function("document.querySelectorAll('#arm-t1 tbody tr').length === 16 && document.querySelectorAll('#arm-t2 tbody tr').length === 8 && document.getElementById('arm-limits').textContent.length > 0", timeout=20000)
    order_ok = dp.evaluate("""() => { const a = document.getElementById('arm-full'), p = document.getElementById('environment-full'), n = document.getElementById('realworld-full');
        return [!!(p.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING), !!(a.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING),
                document.querySelector('#arm-full h2 .secno').textContent.trim(), !!document.querySelector('#dall .dall-list a[href="#arm-full"]')]; }""")
    ck.ok(order_ok == [True, True, "6d", True], f"details: section 6d follows 6c and precedes section 7a, with a link in the 'All sections' list ({order_ok})")
    dp.evaluate("document.getElementById('arm-line-box').open = true")
    intro = norm(dp.inner_text("#arm-intro"))
    t = [__import__("datetime").datetime.fromisoformat(r["started_at"].replace("Z", "+00:00")) for r in arm["runs"]]
    spread = round((max(t) - min(t)).total_seconds() / 60)
    ck.ok(all(r["run_id"] in intro for r in arm["runs"]) and f"started within {spread} minutes" in intro and "ubuntu-24.04-arm" in intro and M["cpu_model"] in intro
          and f"{M['vcpus']} vCPUs" in intro and f"{M['l1d_kib']} KiB L1 data cache" in intro and f"kernel {M['kernel']}" in intro
          and "This section is the full account behind section 6a of the main page." in intro,
          "6d, what ran: the runner label, the three run ids, the core and its caches, and that this is the full account behind section 6a (the numbering differs between the pages)")
    build = norm(dp.inner_text("#arm-build"))
    basis = norm(dp.inner_text("#arm-basis"))
    mcs_ = arm["matmul_cost"]["sizes"]
    kib_ = lambda n: (f"{n / 1024:.1f}".rstrip("0").rstrip(".") + " MiB") if n >= 1024 else f"{n:g} KiB"  # noqa: E731
    ck.ok(build.startswith("Builds and sizes.") and f"built with {clang} and {libcxx}" in build and M["flags"]["common"] in build and "no -march flag" in build
          and f"{kib_(M['size_targets_bytes']['L1'] / 1024)} and {kib_(M['size_targets_bytes']['L2'] / 1024)}" in build
          and f"d = {mcs_['L1']['d']} and d = {mcs_['L2']['d']}" in build and "other byte counts on the x86-64 models" in build and "not the same number of bytes" in build,
          "6d, builds and sizes: the toolchain, the flags, the two working-set sizes and matrix-multiply d from the data, and that the same size class is not the same number of bytes on x86-64")
    ck.ok(basis.startswith("What is shared with the x86-64 study.") and f"The {M['reps_per_side']} repetitions a side" in basis and arm["criteria"]["file"] in basis
          and arm["criteria"]["sha256"][:12] in basis and "it may change" in basis and "unpublished development history" in basis
          and "committed after a two-kernel smoke run and after the three full runs were dispatched, and before any of their jobs finished" in basis
          and dp.evaluate("[...document.querySelectorAll('#arm-basis a')].some(a => a.href.endsWith('arm64/PLAN.md'))"),
          "6d, what is shared: the rule file and its hash, the plan's link and order (after the smoke run and the dispatch, before any job finished), the unpublished-history caveat, 'it may change'")
    # the order claim is tied to the files: the plan names the smoke run's two kernels, and its commit came after the smoke run and the dispatch and before the first job finished
    tl = json.load(open(os.path.join(REPO, "tests", "data", "s8_arm_timeline.json"), encoding="utf-8"))
    plan_head = open(os.path.join(REPO, "arm64", "PLAN.md"), encoding="utf-8").read().split("## Question")[0]
    seen_k = re.search(r"const ARM_SMOKE_SEEN = \[([^\]]*)\]", open(os.path.join(SITE, "app.js"), encoding="utf-8").read())
    seen_names = re.findall(r"'([^']+)'", seen_k.group(1)) if seen_k else []
    ck.ok(seen_names and all(n in plan_head for n in seen_names) and "the only Arm timing seen so far" in plan_head and tl["smoke"]["run"] == int(re.search(r"run (\d+)", plan_head).group(1)),
          f"6d: the kernels the page says the smoke run had already timed ({seen_names}) are the ones arm64/PLAN.md's first paragraph names, for the smoke run recorded in the timeline file")
    verdict = norm(dp.inner_text("#arm-verdict"))
    fr = V["forward_rule_cells"]
    judged = [c for c in fr if c["judged"]]
    ck.ok(verdict.startswith("Verdict under the written rules: inconclusive.") and "is a map" not in verdict
          and f"of the {len(fr)} cells whose loop keeps SIMD, {len(judged)} are judged" in verdict and f"and {sum(1 for c in judged if c['passes'])} pass" in verdict
          and cell_name(mc["cell_id"]) in verdict and f"({lr_(mc['aligned']['ratio'])}× aligned, interval {lr_(mc['aligned']['ci95'][0])} to {lr_(mc['aligned']['ci95'][1])}×)" in verdict
          and f"the smallest interval start is {lr_(SM['lost_ci_lo_min'])}×" in verdict and all(cell_name(q["cell_id"]) in verdict for q in SM["placement_sensitive"])
          and "neither a map nor a small cost everywhere" in verdict,
          "6d: the verdict in words is INCONCLUSIVE: the forward rule missed by the named cell (with ratio and interval), the lost-SIMD side met, the placement-sensitive cells listed and not judged")
    ck.ok(dp.evaluate("document.getElementById('arm-line').textContent") == V["line"] and dp.evaluate("document.getElementById('arm-line').closest('pre') !== null"),
          "6d: the pool's own verdict line is printed verbatim (in a pre, so its raw cell ids stay raw)")
    # how firm the verdict is: the seed and interval-method readings beside it, labelled as readings that replace nothing
    IM_ = arm["interval_methods"]
    seed = norm(dp.inner_text("#arm-seed"))
    sens = [norm(t_) for t_ in dp.evaluate("[...document.querySelectorAll('#arm-sens li')].map(l => l.textContent)")]
    send = norm(dp.inner_text("#arm-seed-end"))
    map_others = [m_ for m_ in IM_["methods"] if m_["form"] == "map"]
    his_ = [m_["deciding_cell"]["ci95"][1] for m_ in map_others]
    by_href = lambda sel, end: dp.evaluate(f"[...document.querySelectorAll('{sel} a')].some(a => a.href.endsWith('{end}'))")  # noqa: E731
    ck.ok(seed.startswith("How firm that is.") and f"The form turns on one cell: {cell_name(mc['cell_id'])}, aligned, ends at {lr_(DC_['stored_hi'])}× against the limit of {fx_(DC_['limit'])}×, a margin of {DC_['margin_over_limit']:.4f}" in seed
          and f"prefix {SS_['stored_seed']['prefix']}, {SS_['stored_seed']['resamples']:,} resamples" in seed and "so the stored verdict stays inconclusive" in seed
          and "unpublished development history, which the public repository cannot show" in seed and "replace nothing" in seed
          and by_href("#arm-seed", SS_["script"]) and by_href("#arm-seed", SS_["source"]) and by_href("#arm-seed", IM_["report"]) and by_href("#arm-seed", IM_["plan"]),
          "6d, how firm: the deciding cell's end and margin, the seed's prefix and resamples, the stored verdict kept, the unpublished-history caveat, links to the seed script, its data, the interval-methods report and plan")
    ck.ok(len(sens) == 3 and f"re-drawn under {DC_['alt_draws']} other seeds" in sens[0] and f"ends at a median of {lr_(DC_['alt_hi']['median'])} (5th to 95th percentile {lr_(DC_['alt_hi']['p05'])} to {lr_(DC_['alt_hi']['p95'])})" in sens[0]
          and f"{DC_['alt_at_or_above_limit']} of the {DC_['alt_draws']} end at or above the limit" in sens[0] and "the stored end is higher than all 400" in sens[0]
          and f"With {SS_['converged_resamples']:,} resamples it ends at {lr_(DC_['converged']['hi'])}, under the limit" in sens[0]
          and f"re-run under {SS_['full']['count']} of those seeds gives a map in {SS_['full']['forms']['map']} of them" in sens[1]
          and f"all {SS_['derived']['seeds']} is a map in {SS_['derived']['forms']['map']} and inconclusive in {SS_['derived']['forms']['inconclusive']}" in sens[1]
          and sens[2].startswith(f"{['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight'][len(map_others)]} other interval methods") and "all give a map" in sens[2]
          and f"between {lr_(min(his_))} and {lr_(max(his_))}" in sens[2] and "only the pool’s own bootstrap gives inconclusive" in sens[2] and "a check on the interval, not a replacement for the written rule" in sens[2],
          "6d, the three sensitivity readings: the 400-seed re-draw, the 40 full re-analyses and the derived forms, and the other interval methods; each number equals arm64.json and each is labelled a check, not a replacement")
    ck.ok(f"So these data cannot separate inconclusive from a map at this cell. That is not evidence that the forward add costs more than {V['forward_limit_pct']:g}% at L2: its ratio is {lr_(mc['aligned']['ratio'])}× aligned" in send
          and "an identical binary against itself spreads as widely at that size" in send,
          "6d: the closing sentence of that block says the data cannot separate inconclusive from a map and that the cell is not shown to cost more than 2%")
    # Table 12
    cap1 = norm(dp.inner_text("#arm-t1-cap"))
    ck.ok(cap1.startswith("Table 12.") and f"{arm['cpu_short']} ({arm['jobs']} jobs, {len(arm['runs'])} runs)" in cap1 and f"({arm['x86']['model']['jobs']} jobs of the {arm['x86']['jobs']}-job x86-64 pool)" in cap1
          and arm["instr_label"] in cap1 and "No-vectorize build" in cap1 and "Layout A/A" in cap1 and "‡ marks a placement-sensitive cell" in cap1
          and "its working sets have other byte sizes than the Arm ones" in cap1, "Table 12: caption names both machines with their job counts, defines instructions, the no-vectorize build, the layout A/A and the ‡ mark, and says the working sets differ in bytes")
    heads = dp.evaluate("[...document.querySelectorAll('#arm-t1 thead th')].map(h => h.textContent)")
    want_heads = ["Loop and size", "On Arm", "Arm, as compiled", "Arm, aligned", "Instructions, as compiled", "No-vectorize build", "Layout A/A half-width", f"{x86name}: SIMD", f"{x86name}, as compiled", f"{x86name}, aligned"]
    ck.ok(heads == want_heads and dp.evaluate("document.getElementById('arm-t1').getAttribute('aria-describedby')") == "arm-t1-cap"
          and dp.evaluate("document.getElementById('arm-t1-wrap').getAttribute('role')") == "region", f"Table 12: ten named columns, described by its caption, scrollable region ({heads})")
    got = dp.evaluate("[...document.querySelectorAll('#arm-t1 tbody tr')].map(r => [...r.children].map(c => c.innerText))")
    bad_t1 = []
    for row, c in zip(got, arm["cells"]):
        x = x86[c["cell_id"]]
        ivc = lambda d: f"{lr_(d['ratio'])}\n{lr_(d['ci95'][0])} to {lr_(d['ci95'][1])}"  # noqa: E731
        want = [None, ARM_CLASS_WORDS[c["class"]], ivc(c["as_compiled"]), ivc(c["aligned"]), lr_(c["instr_ratio"]["as_compiled"]),
                ivc(c["positive"]) if c.get("positive") else "none", pct_s(c["layout_aa"]["half_width_pct"]), ARM_CLASS_WORDS[x["class"]], ivc(x["as_compiled"]), ivc(x["aligned"])]
        first = row[0].replace("\n", " ")
        if not (first.startswith(f"{ARM_KERNEL_NAMES[c['kernel']]}, {c['size_class']}") and ("‡" in first) == c["placement_sensitive"] and row[1:] == want[1:]):
            bad_t1.append((c["cell_id"], row, want))
    tags = dp.evaluate("[...document.querySelectorAll('#arm-t1 tbody th .ps-mark')].map(s => [s.getAttribute('aria-label'), s.getAttribute('title')])")
    ck.ok(len(got) == len(arm["cells"]) == 16 and not bad_t1 and len(tags) == sum(1 for c in arm["cells"] if c["placement_sensitive"]) and all(t_ == ["placement-sensitive", "placement-sensitive"] for t_ in tags),
          f"Table 12: all 16 cells, in the data's order, every value equal to arm64.json at its printed precision, placement-sensitive cells carry a ‡ whose label says so ({bad_t1[:1]})")
    t1w = dp.evaluate("(() => { const w = document.getElementById('arm-t1-wrap'), r = w.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), innerWidth, w.scrollWidth, w.clientWidth]; })()")
    ck.ok(t1w[0] >= 0 and t1w[1] <= t1w[2] and t1w[3] <= t1w[4] + 1,
          f"Table 12 at 1280: the box sits inside the window and the ten columns fit without a sideways scroll (box {t1w[0]} to {t1w[1]} of {t1w[2]}, content {t1w[3]} in {t1w[4]})")
    # forward, floors
    fwd = norm(dp.inner_text("#arm-forward"))
    f1a, f1c = arm["forward_loops"]["L1"]["aligned"], arm["forward_loops"]["L1"]["as_compiled"]
    ps_f = [q for q in SM["placement_sensitive"] if q["cell_id"].split(".")[0] in arm["forward_loops"]["kernels"]]
    rep, lay, jh, sd = arm["reproduction"], arm["aa"]["layout_half_width_pct"], arm["aa"]["job_half_width_pct"], arm["between_job_sd"]
    miss_pred = all(kern[q["cell_id"].split(".")[0]]["prediction"]["placement_effect"] == "none" and kern[q["cell_id"].split(".")[0]]["prediction"]["placement_held"] is False for q in ps_f)
    FI_ = {c["cell_id"]: c for c in arm["forward_instr"]["cells"]}
    same_add = all(v["as_compiled"] and v["aligned"] for v in arm["forward_instr"]["added_same_at_both_sizes"].values())
    NZ_ = arm["noise"]
    iaa_ = NZ_["identical_binary_aa"]
    add1, add2, sten1, sum1 = FI_["k02_add_fwd.L1"], FI_["k02_add_fwd.L2"], FI_["k03_stencil.L1"], FI_["k01_sum_fwd.L1"]
    flip = lambda c: (c["as_compiled"]["ratio"] - 1) * (c["aligned"]["ratio"] - 1) < 0  # noqa: E731
    ck.ok(f"cost {lr_(f1c['min'])}× to {lr_(f1c['max'])}× as compiled and {lr_(f1a['min'])}× to {lr_(f1a['max'])}× aligned (Table 12)" in fwd
          and same_add and f"{sum1['as_compiled']['added']} for the sum, {add1['as_compiled']['added']} (aligned {add1['aligned']['added']}) for the add and {sten1['as_compiled']['added']} (aligned {sten1['aligned']['added']}) for the stencil, the same count at the L2 size" in fwd
          and f"an instruction ratio of {add1['as_compiled']['instr_ratio']:.4f} at L1 ({add1['elements']:,} elements) and {add2['as_compiled']['instr_ratio']:.4f} at L2 ({add2['elements']:,} elements)" in fwd
          and "that these instructions are the time cost fits the counts and was not tested" in fwd
          and all(cell_name(q["cell_id"]).lower() in fwd.lower() and f"{q['d']:.3f}" in fwd for q in ps_f) and miss_pred and "which the plan had predicted would not happen" in fwd
          and f"The A/A floor of {pct_s(arm['aa']['half_width_pct'])} is that of the forward add at L1 alone" in fwd and "the yardstick is the compiled ÷ aligned ratio" in fwd
          and all(f"{ARM_SHORT_NAMES[cells[q['cell_id']]['kernel']]} {lr_(cells[q['cell_id']]['as_compiled']['ratio'])}× compiled and {lr_(cells[q['cell_id']]['aligned']['ratio'])}× aligned"
                  + (" (it changes side of 1×, so no cost is claimed for it)" if flip(cells[q["cell_id"]]) else "") in fwd for q in ps_f)
          and any(flip(cells[q["cell_id"]]) for q in ps_f) and "At the L2 size" not in fwd,
          "6d, forward loops: the L1 ranges, the instructions the checks add (the same at both sizes), and the placement-sensitive cells judged by compiled ÷ aligned and not by the A/A floor, with the prediction that missed")
    l2t = norm(dp.inner_text("#arm-l2"))
    mixt = norm(dp.inner_text("#arm-mix"))
    aa2 = iaa_["L2"]
    sc_, mix_ = NZ_["same_cell_l2"], NZ_["mixture"]["by_size"]
    sh_ = lambda x: f"{x * 100:.1f}%"  # noqa: E731
    k4_, k5_ = cells["k04_rev.L2"], cells["k05_stride2.L2"]
    l2_cells = [c for c in arm["cells"] if c["kernel"] in arm["forward_loops"]["kernels"] and c["size_class"] == "L2"]
    ck.ok(l2t.startswith("Noise at the L2 size.") and f"Pooled over {aa2['jobs']} jobs it has a ratio of {lr_(aa2['pooled']['ratio'])} with an interval of {lr_(aa2['pooled']['ci95'][0])} to {lr_(aa2['pooled']['ci95'][1])} (a half-width of {pct_s(aa2['pooled']['half_width_pct'])}" in l2t
          and f"per job the ratio runs from {lr_(aa2['job_ratio_range'][0])} to {lr_(aa2['job_ratio_range'][1])}), and {aa2['jobs_above_rule_max']} of the {aa2['jobs']} jobs are above the {NZ_['rule_aa_half_width_max_pct']:g}% that the written rules allow an A/A (at L1: {iaa_['L1']['jobs_above_rule_max']})" in l2t
          and f"as wide as the checked cell it sits beside ({pct_s(sc_['aligned']['half_width_pct'])} aligned, {pct_s(sc_['as_compiled']['half_width_pct'])} as compiled)" in l2t
          and f"as the unchecked binary against its own re-aligned copy ({pct_s(sc_['layout_aa']['half_width_pct'])})" in l2t
          and "aligned intervals of " + join_and([f"{lr_(c['aligned']['ci95'][0])} to {lr_(c['aligned']['ci95'][1])}× ({ARM_SHORT_NAMES[c['kernel']]})" for c in l2_cells]) in l2t
          and f"Of the judged forward cells only {cell_name(mc['cell_id'])} misses the {fx_(V['limit'])}× limit" in l2t
          and f"{lr_(mc['aligned']['per_job_range'][0])}× to {lr_(mc['aligned']['per_job_range'][1])}×" in l2t
          and f"(a between-job standard deviation of {mc['aligned']['between_job_sd_pct']:.2f}%, aligned; {aa2['pooled']['between_job_sd_pct']:.2f}% for an identical binary at that size), where no cell at L1 spreads by more than {sd['l1_max_pct']:.2f}%" in l2t
          and l2t.endswith("is the width of L2 timing on this core, not a property of the check."),
          "6d, noise at the L2 size: the identical-binary A/A at L2 (ratio, interval, per-job range, jobs above the rule's 2%), as wide as the checked cell and the layout A/A, the forward cells' L2 intervals and the one miss with its between-job spread beside an identical binary's")
    ck.ok(mixt.startswith("What the samples at L2 look like.") and "The cause was not examined and no hardware counter was read" in mixt
          and f"more than {round(NZ_['slow_share'] * 100)}% longer than the fastest process of their series" in mixt
          and f"At L2 that share is {sh_(mix_['L2']['none']['share_slow'])} of the unchecked build’s processes and {sh_(mix_['L2']['fast']['share_slow'])} of the checked build’s ({sh_(mix_['L1']['none']['share_slow'])} and {sh_(mix_['L1']['fast']['share_slow'])} at L1)" in mixt
          and f"it reaches {round(mix_['L2']['none']['cell_share_max'] * 100)}% and {round(mix_['L2']['fast']['cell_share_max'] * 100)}%" in mixt
          and f"including the lost loops’ {lr_(k4_['as_compiled']['ratio'])}× and {lr_(k5_['as_compiled']['ratio'])}× at that size" in mixt and "are therefore less stable estimates than the L1 ones" in mixt,
          "6d, the samples at L2: the per-process slow-share mixture at both sizes, no cause claimed, and the L2 medians (including the lost loops') called less stable")
    fl = norm(dp.inner_text("#arm-floors"))
    tiny = sum(1 for m in rep["misses"] if m["gap_pct"] < 0.01)

    def widest(sz):
        best = max(((c[col]["half_width_pct"], c["cell_id"], col) for c in arm["cells"] if c["size_class"] == sz for col in ("as_compiled", "aligned")))
        return best[0], best[1], "aligned" if best[2] == "aligned" else "as compiled"

    w1_, w2_ = widest("L1"), widest("L2")
    ck.ok(f"is timed on the forward add at the L1 size; pooled over {arm['aa']['jobs']} jobs, it has a half-width of {pct_s(arm['aa']['half_width_pct'])}" in fl and f"{pct_s(jh['median'])} at the median ({pct_s(jh['min'])} to {pct_s(jh['max'])})" in fl
          and "That is the floor of that one cell, not of the core" in fl
          and f"the widest interval of a measured cell is ±{pct_s(w1_[0])} at L1 ({cell_name(w1_[1])}, {w1_[2]}) and ±{pct_s(w2_[0])} at L2 ({cell_name(w2_[1])}, {w2_[2]})" in fl
          and f"from {pct_s(lay['min'])} to {pct_s(lay['max'])}" in fl and f"{sd['l1_max_pct']:.2f}% at L1" in fl and f"{sd['l2_max_pct']:.1f}% at L2" in fl
          and f"{rep['outside']} of {rep['checked']} comparisons" in fl and f"by at most {rep['max_gap_pct']:.1f}%" in fl and f"{tiny} of them by less than 0.01%" in fl,
          "6d, floors: the A/A named as the floor of one cell (the forward add at L1) beside the widest intervals at both sizes, the layout A/A range, the between-job spread at both sizes and the run-to-run comparison, from the data")
    lyt = norm(dp.inner_text("#arm-layout"))
    LV_ = {r["cell_id"]: r for r in arm["layout_vs_placement"]["rows"]}

    def lside(cid):
        r = LV_[cid]
        return f"{lr_(r['layout_aa']['ratio'])} against a D of {lr_(r['d']['ratio'])}" + (", which is on the other side of 1×" if (r["layout_aa"]["ratio"] - 1) * (r["d"]["ratio"] - 1) < 0 else "")

    ck.ok(lyt.startswith("Placement, and what the layout A/A can see.") and f"built with {M['flags']['align']}, so it moves only the unchecked build’s loops" in lyt
          and f"at L1 the stencil has a layout A/A of {lside('k03_stencil.L1')}, gather {lside('k06_gather.L1')}, and matrix multiply {lside('k08_matmul.L1')}" in lyt
          and f"At {join_and([cell_name(c_) for c_ in arm['layout_vs_placement']['d_excludes_1_layout_aa_includes_1']])} the interval of D excludes 1 while that of the layout A/A does not" in lyt
          and "a quiet layout A/A does not show that a cell is free of placement effects here" in lyt and "was not examined" in lyt,
          "6d, placement: the layout A/A moves only the unchecked build, and on this core it disagrees with compiled ÷ aligned at the stencil, gather and matrix-multiply cells named from the data; what 64-byte windows mean on Arm was not examined")
    # Table 13
    cap2 = norm(dp.inner_text("#arm-t2-cap"))
    heads2 = dp.evaluate("[...document.querySelectorAll('#arm-t2 thead th')].map(h => h.textContent)")
    ck.ok(cap2.startswith("Table 13.") and f"all {arm['build_facts']['jobs']} jobs produced identical hashes, listings, diffs and compiler remarks" in cap2 and arm["build_facts"]["all_agree"]
          and "come from the saved listings (the .s files) of one job" in cap2
          and heads2 == ["Loop", "In the plan", "Clang’s remark, checks on", "NEON instructions, off → on", "SIMD loop, off → on", "Listing lines, off → on", "Check traps, on"],
          "Table 13: caption says all 30 jobs agree (true in the data), seven named columns")

    def plan_words(k):
        p = k["prediction"]
        if not p["class"] and not p["placement_effect"]:
            return "no prediction"
        parts = []
        if p["class"]:
            parts.append(f"{p['class']} ({'held' if p['class_held'] else 'did not hold'})")
        if p["placement_effect"]:
            parts.append(f"{'no placement effect' if p['placement_effect'] == 'none' else p['placement_effect']} ({'held' if p['placement_held'] else 'did not hold'})")
        return "; ".join(parts)

    got2 = dp.evaluate("[...document.querySelectorAll('#arm-t2 tbody tr')].map(r => [...r.children].map(c => c.textContent))")
    bad_t2 = []
    for row, k in zip(got2, arm["kernels"]):
        n, f_, s = k["builds"]["none"], k["builds"]["fast"], k["simd_loop"]["as_compiled"]
        remark = f"vectorized, width {f_['width']}, interleave {f_['interleave']}" if f_["vectorized"] else (f_["why_not_vectorized"] or "not vectorized")
        simd = "none" if s["none_instructions"] is None else f"{s['none_instructions']} → {'none' if s['fast_instructions'] is None else s['fast_instructions']}{', same opcodes' if s['same_opcodes'] else ''}"
        want = [ARM_KERNEL_NAMES[k["kernel"]], plan_words(k), remark, f"{n['neon_instructions']} → {f_['neon_instructions']}", simd, f"{n['asm_lines']} → {f_['asm_lines']}", str(f_["traps"])]
        if row != want:
            bad_t2.append((row, want))
    ck.ok(len(got2) == 8 and not bad_t2, f"Table 13: eight loops, every count, remark and plan entry equal to arm64.json ({bad_t2[:1]})")
    # matrix multiply
    mt = norm(dp.inner_text("#arm-matmul"))
    mk_ = kern["k08_matmul"]
    ck.ok(f"{lr_(m1['as_compiled']['ratio'])}× at L1 as compiled ({lr_(m1['aligned']['ratio'])}× aligned)" in mt and f"{lr_(m2['as_compiled']['ratio'])}× at L2 ({lr_(m2['aligned']['ratio'])}× aligned)" in mt
          and f"{m1['placement']['d']['ratio']:.3f} and {m2['placement']['d']['ratio']:.3f}" in mt and f"{fx_(mmx['as_compiled']['ratio'])}× and {fx_(x86['k08_matmul.L2']['as_compiled']['ratio'])}×" in mt
          and f"{mk_['builds']['fast']['asm_lines']} lines against {mk_['builds']['none']['asm_lines']}" in mt and f"{lr_(m1['instr_ratio']['as_compiled'])}× the instructions at L1" in mt
          and "Observed in the checked build’s full listing (the .s file) and its L1 diff (the diff)" in mt and f"fits the listing and the counts at L1; the row-length sweep at the end of this section tests whether the extra time per inner call is fixed, and its word is “{ds_arm['word']}”" in mt and "it was not tested" not in mt and "Nothing here times the SIMD loop alone" in mt and "is not established here" in mt
          and f"the SIMD loop has the same {mk_['simd_loop']['as_compiled']['fast_instructions']} instructions with the same opcodes in both builds" in mt and "brk #0x1" in mt
          and "sit before the SIMD loop and in the scalar loop, none inside the SIMD loop. The diff drops those jump targets, so they are read from the full listing" in mt
          and "is inferred" not in mt and "does not show their targets" not in mt
          and f"{lr_(m1['instr_ratio']['as_compiled'])}× the instructions at L1 (Cachegrind) for {lr_(m1['as_compiled']['ratio'])}× the time, and {lr_(m2['instr_ratio']['as_compiled'])}× the instructions at L2 for {lr_(m2['as_compiled']['ratio'])}× the time" in mt
          and f"d = {mcs_['L1']['d']} at L1 and d = {mcs_['L2']['d']} at L2, so the SIMD loop runs {mcs_['L1']['whole_passes']} and {mcs_['L2']['whole_passes']} passes of {arm['matmul_cost']['vector_pass_elements']} elements per row and the scalar loop is left {mcs_['L1']['d_mod_pass']} and {mcs_['L2']['d_mod_pass']}" in mt
          and f"the gather loop executes {lr_(cells['k06_gather.L1']['instr_ratio']['as_compiled'])}× and {lr_(cells['k06_gather.L2']['instr_ratio']['as_compiled'])}× the instructions at the two sizes but costs {lr_(cells['k06_gather.L1']['as_compiled']['ratio'])}× and {lr_(cells['k06_gather.L2']['as_compiled']['ratio'])}×" in mt
          and "do not say whether the row length, the cache level or both is why matrix multiply costs so much less at L2; the row-length sweep times other d" in mt and "no other d was timed" not in mt
          and dp.evaluate("[...document.querySelectorAll('#arm-matmul a')].some(a => a.href.endsWith('k08_matmul.L1.diff'))")
          and dp.evaluate("[...document.querySelectorAll('#arm-matmul a')].some(a => a.href.endsWith('asm/k08_matmul.fast.s'))"),
          "6d, matrix multiply: the Arm and x86-64 numbers from the data, the listing facts labelled observed (including where the trap branches sit, read from the full listing), the mechanism labelled as fitting the counts and not tested, the confound between row length and cache level stated with the gather loop's example, and links to the diff and the full listing")
    nv = norm(dp.inner_text("#arm-novec"))
    rv = cells["k04_rev.L1"]
    ck.ok(f"costs {lr_(rv['positive']['ratio'])}× at the reverse loop’s L1 size, against {lr_(rv['as_compiled']['ratio'])}× with the checks on: about {round(SM['novec_rev_share_pct'])}%" in nv and "(inferred)" in nv,
          "6d, no-vectorize control: the reverse loop's yardstick and the share of the extra time, labelled inferred")
    pl = norm(dp.inner_text("#arm-plan"))
    pred = [k for k in arm["kernels"] if k["prediction"]["class"]]
    held = [k for k in pred if k["prediction"]["class_held"]]
    plc = [k for k in arm["kernels"] if k["prediction"]["placement_effect"]]
    plm = [k for k in plc if not k["prediction"]["placement_held"]]
    blind_ = [k for k in pred if k["kernel"] not in seen_names]
    blind_held = [k for k in blind_ if k["prediction"]["class_held"]]
    seen_plc = [ARM_SHORT_NAMES[k["kernel"]] for k in plc if k["kernel"] in seen_names]
    ck.ok(f"named the class of {len(pred)} loops, and {len(held)} of {len(pred)} held" in pl and len(seen_names) == 2
          and "was committed after a two-kernel smoke run and before the full runs had finished, by commit times in the author’s unpublished development history." in pl
          and f"Not all of those were blind: the smoke run had already timed {join_and([ARM_SHORT_NAMES[n_] for n_ in seen_names])} on this core (the plan quotes both figures), so those two predictions were made with the result in view, and {len(blind_held)} of the {len(blind_)} others held" in pl
          and join_and([ARM_SHORT_NAMES[k["kernel"]] for k in plm]) in pl and "did not (flagged placement-sensitive at L1)" in pl and "It made no prediction for gather and histogram" in pl
          and seen_plc and f"{join_and(seen_plc)} had been timed in the smoke run when that was written" in pl and "that prediction was not blind" not in pl
          and dp.evaluate("[...document.querySelectorAll('#arm-plan a')].some(a => a.href.endsWith('arm64/PLAN.md'))"),
          f"6d, against the plan: {len(held)} of {len(pred)} class predictions held, two of them (the smoke run's two kernels) made with the result in view and {len(blind_held)} of the {len(blind_)} blind ones held; the placement prediction missed for {[k['kernel'] for k in plm]}, and the forward add's was written after its smoke timing; no prediction for gather and histogram")
    lim = norm(dp.inner_text("#arm-limits"))
    ck.ok("One core type (" + M["cpu_model"] in lim and f"{arm['jobs']} jobs in {len(arm['runs'])} runs from one day" in lim and clang[0].upper() + clang[1:] in lim and libcxx in lim
          and "No real programs, no profile-guided builds and no other compilers or libc++ versions were timed on Arm" in lim and "no steal or frequency record" in lim
          and "the layout A/A moves only the unchecked build’s loops, so it did not see placement shifts that the compiled ÷ aligned ratio shows (above): neither is a verified placement control on this core" in lim
          and "the layout A/A is the control that applies to both" not in lim
          and "says nothing about Apple, AWS or other Arm cores, about other Arm compilers, or about Google’s services" in lim,
          "6d, limits: one core type, one image, 30 jobs from one day, clang 18 only, no programs, no steal record, no verified placement control on Arm (the layout A/A is blind to what compiled ÷ aligned shows), and no claim about other Arm cores, compilers or Google")
    bad = page_numbers(dp, allowed, "#arm-full")
    ck.ok(not bad, "6d: every number printed is in the data" + ("" if not bad else f": {bad[:4]}"))
    # the other sentences changed because of the Arm column: no stale 'no arm64', scoped x86-64 sentences, the Reproduce command, the limits
    dtext = norm(dp.evaluate("document.body.textContent"))
    mp = browser.new_page(viewport={"width": 1280, "height": 900})
    mp.goto(base, wait_until="networkidle")
    mp.wait_for_function("document.querySelectorAll('#arm-rows .row').length === 8 && document.getElementById('arm-avg').textContent.length > 40", timeout=20000)
    mtext = norm(mp.evaluate("document.body.textContent"))
    ck.ok("No arm64" not in dtext + mtext and "not timed on Arm" not in dtext + mtext and "Baseline x86-64, plus one Arm column." in dtext
          and f"Section 6d: the {arm['jobs']} jobs of the {len(arm['runs'])} Arm runs" in dtext and "(ud2 on x86-64, brk #0x1 on Arm)" in dtext
          and "Among the x86-64 models, the forward loops are near 1× on the AMD models only" in dtext and "on the baseline x86-64 of the main timing" in dtext,
          "details: the stale 'No arm64' limit is replaced, the jobs sentence lists the Arm pool, the trap instruction is named per architecture, the AMD-only sentence is scoped to the x86-64 models")
    mp.evaluate("document.querySelectorAll('details.fold').forEach(d => { d.open = true; })")  # the limits box is folded by default
    cb = mp.evaluate("[...document.querySelectorAll('#cannot li')].map(l => l.innerText.replace(/\\s+/g, ' '))")
    ck.ok(len(cb) == 5 and f"Arm: one core type ({arm['cpu_short']}), {arm['jobs']} jobs on shared machines, {clang} only; no real programs, profile-guided builds or other compilers were timed there (section 6a)." in cb[2]
          and "SSE2" in cb[2] and "on x86-64 one xmm register" in mtext and "NEON, Arm’s version of the same idea" in mtext,
          "main page: the Limits box keeps its five lines and carries the Arm clause in the toolchain line; the SIMD sentence says x86-64 and points to NEON")
    avg = norm(mp.inner_text("#arm-avg span[data-v=armAvg]"))
    sentences = re.split(r"(?<![0-9])\.\s+(?=[A-Z])", avg)
    wid = max((c for c in arm["cells"] if c["kernel"] in arm["forward_loops"]["kernels"] and c["size_class"] == "L2"), key=lambda c: c["aligned"]["half_width_pct"])
    # Trimmed on Oct 17 to make room for the replication figure and the row-length sentence in section 6a (the all-open length budget):
    # the clause on the two placement-sensitive loops and the fixed instruction count per call, the cell's name beside the widest L2 interval and the
    # seed count are gone from this paragraph (6a and section 6d carry them); the A/A floor stays tied to the forward add, the L2 widths stay, and the verdict stays 'inconclusive'.
    ck.ok(len(sentences) == 2 and "neither confirms nor contradicts the 0.30% average" in sentences[0]
          and sentences[0].startswith(f"On {arm['cpu_short']} the three forward loops cost {lr_(f1['min'])}× to {lr_(f1['max'])}× at L1, as compiled, against an A/A floor of ±{pct_s(arm['aa']['half_width_pct'])} (forward add only)")
          and f"At L2 the widest forward interval (±{pct_s(wid['aligned']['half_width_pct'])}) and an identical binary against itself (±{pct_s(aa_l2['half_width_pct'])}) are too wide to resolve 0.30%" in sentences[1]
          and "the pooled verdict is inconclusive, on a margin most other seeds reverse (section 6a)" in sentences[1]
          and DC_["alt_draws"] - DC_["alt_at_or_above_limit"] > DC_["alt_draws"] / 2,
          f"section 10: the Arm addition is two sentences, says it neither confirms nor contradicts the average, ties the A/A floor to the forward add, and gives the widest forward interval at L2 beside an identical binary's, the verdict form and that most other seeds reverse the margin (true in the data) ({len(sentences)} sentences)")
    wf_text = open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8").read()
    try:
        import yaml
    except ImportError:
        yaml = None
    if yaml is not None:
        wf = yaml.safe_load(wf_text)
        on_ = wf.get("on", wf.get(True))  # PyYAML reads the key `on` as the boolean True
        rin = on_["workflow_dispatch"]["inputs"]["runner"]
        wired = (rin.get("type") == "choice" and rin.get("default") == "ubuntu-24.04" and rin.get("options") == ["ubuntu-24.04", "ubuntu-24.04-arm"]
                 and wf["jobs"]["measure"]["runs-on"] == "${{ inputs.runner }}")
    else:
        print("   note PyYAML is not installed: measure.yml's runner wiring is read with patterns (pip install pyyaml for the parsed check)")
        wired = (re.search(r"runner:\s*\n(?:\s+.*\n)*?\s+type: choice\n\s+options: \[\"ubuntu-24\.04\", \"ubuntu-24\.04-arm\"\]\n\s+default: \"ubuntu-24\.04\"", wf_text) is not None
                 and re.search(r"^  measure:\n    runs-on: \$\{\{ inputs\.runner \}\}$", wf_text, re.M) is not None)
    ck.ok(mp.inner_text("#cmd-measure-arm").strip() == f"{index['repo']['measure_command']} -f runner=ubuntu-24.04-arm" and mp.is_visible('#cmd-measure-arm ~ *, .cmdline:has(#cmd-measure-arm) .copy') and wired,
          "Reproduce: the Arm command is shown with a Copy button, and measure.yml has a choice input 'runner' (x86-64 default, the Arm label as the other option) that the measure job's runs-on reads")
    # section markup carries no typed numbers: everything numeric in the two new sections comes from the data
    with open(os.path.join(SITE, "index.html"), encoding="utf-8") as f:
        src = f.read()
    with open(os.path.join(SITE, "details.html"), encoding="utf-8") as f:
        dsrc = f.read()
    typed = []
    for name, text in (("index.html #arm", src.split('<section id="arm">')[1].split("</section>")[0]), ("details.html #arm-full", dsrc.split('<section id="arm-full">')[1].split("</section>")[0])):
        plain = re.sub(r"<[^>]+>", " ", text)
        plain = re.sub(r"6a|6d|x86-64|Figure [179]|Table 1[235]|ubuntu-24\.04-arm|Neoverse-N2|&[a-z]+;|arm64/PLAN\.md|data/arm64\.json", " ", plain)
        typed += [(name, m) for m in re.findall(r"\d+(?:\.\d+)?", plain)]
    ck.ok(not typed, f"the two new sections' HTML types no number: every figure is filled from site/data ({typed[:4]})")
    ck.ok(not errors and not errors_d, "Arm: no console errors, page errors or failed data requests on either page" + ("" if not (errors or errors_d) else f": {(errors + errors_d)[:4]}"))
    mp.close()
    dp.close()

    # ---- phone: nothing scrolls sideways, rows and buttons are finger-sized, the readout is on screen
    errors_p = []
    for scheme in ("light", "dark"):
        pp = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme=scheme)
        watch(pp, errors_p)
        pp.goto(base, wait_until="networkidle")
        pp.wait_for_function("document.querySelectorAll('#arm-rows .row').length === 8", timeout=20000)
        pp.evaluate("document.getElementById('arm').scrollIntoView()")
        pp.wait_for_timeout(250)
        small = pp.evaluate("""() => [...document.querySelectorAll('#arm-rows .row, #arm-col-seg button, #arm .sec-more, #arm .more-link a')].map(e => { const r = e.getBoundingClientRect(); return [e.className || e.tagName, Math.round(r.height), Math.round(r.width)]; })
                                  .filter(x => x[1] < 32 || x[2] > 390)""")
        ck.ok(no_hscroll(pp) and not small, f"390 ({scheme}): Section 6a does not scroll sideways, and its rows, switch and links are at least 32 px tall and fit ({small[:3]})")
        tk = pp.evaluate("""() => { const q = (e) => e.getBoundingClientRect(), out = [];
            for (const r of document.querySelectorAll('#arm-rows .row')) { const t = r.querySelector('.track'), a = q(t); for (const m of r.querySelectorAll('.xm, .mk')) { const b = q(m); if (b.left < a.left - 2 || b.right > a.right + 2) out.push(r.dataset.k); } }
            return out; }""")
        ck.ok(not tk, f"390 ({scheme}): Figure 7's marks and ticks stay inside their track ({tk[:3]})")
        pp.click('#arm-rows .row[data-k="k08_matmul"]')
        pp.wait_for_timeout(150)
        vis = pp.evaluate("(() => { const r = document.getElementById('arm-read').getBoundingClientRect(); return [r.width > 200, r.right <= innerWidth + 1, r.left >= -1]; })()")
        ck.ok(all(vis) and "Matrix multiply" in pp.inner_text("#arm-read .ar-head"), f"390 ({scheme}): a tap on a row shows its numbers in the readout, inside the screen")
        shot(pp, saved, shots, f"arm-fig-390-{scheme}.png", "#arm")
        pp.close()
        dp = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme=scheme)
        watch(dp, errors_p)
        dp.goto(base + "details.html", wait_until="networkidle")
        dp.wait_for_function("document.querySelectorAll('#arm-t1 tbody tr').length === 16", timeout=20000)
        dp.evaluate("document.querySelectorAll('#arm-full details').forEach(d => { d.open = true; })")
        dp.wait_for_timeout(150)
        w = dp.evaluate("[...document.querySelectorAll('#arm-t1-wrap, #arm-t2-wrap')].map(w => [w.scrollWidth > w.clientWidth, getComputedStyle(w).overflowX])")
        ck.ok(no_hscroll(dp) and all(x[0] and x[1] == "auto" for x in w) and dp.evaluate("document.getElementById('arm-line').scrollWidth <= document.getElementById('arm-line').parentElement.clientWidth + 1"),
              f"390 ({scheme}) details: Tables 12 and 13 scroll inside their own boxes, the verbatim verdict line wraps, and the page does not scroll sideways ({w})")
        stick = dp.evaluate("""() => [...document.querySelectorAll('#arm-t1-wrap, #arm-t2-wrap')].map(w => { w.scrollLeft = w.scrollWidth; const r = w.getBoundingClientRect(), th = w.querySelector('tbody th').getBoundingClientRect(), hd = w.querySelector('thead th').getBoundingClientRect();
            return [Math.round(th.left - r.left), Math.round(hd.left - r.left), Math.round(th.width), Math.round(r.width), w.scrollLeft > 0]; })""")
        ck.ok(all(s[4] and 0 <= s[0] <= 4 and 0 <= s[1] <= 4 and s[2] <= 0.5 * s[3] for s in stick),
              f"390 ({scheme}) details: when Tables 12 and 13 are scrolled to their right end the loop's name stays in view (left edge, heading and label up to half the box) ({stick})")
        shot(dp, saved, shots, f"arm-details-390-{scheme}.png", "#arm-full")
        dp.close()
    ck.ok(not errors_p, "Arm, 390: no console errors" + ("" if not errors_p else f": {errors_p[:3]}"))


REP_NUM_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
REP_SAY = {"none": "not drawn", "few": "too few jobs", "map": "a map", "holds": "a small cost everywhere", "inc": "inconclusive"}


def utc_text_py(s):
    return s.replace("T", " ").replace("Z", " UTC")


def utc_clock_py(s):
    return s[11:19] + " UTC"


LONG_MONTHS_PY = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def long_date_py(s):
    return f"{int(s[8:10])} {LONG_MONTHS_PY[int(s[5:7]) - 1]} {s[:4]}"


def prov_history_py(P):
    """The sentence that says when the public history begins and what that leaves unchecked (site/app.js renderProvenance), from index.json's provenance."""
    return (f"The public history begins on {long_date_py(P['public_history']['first_commit_utc'])}, after the runs of s1 to s4, the holdout and the rewrite, "
            "so for those that order cannot be checked from public records.")


def min_sec_py(n):
    m, s = divmod(n, 60)
    u = lambda k, w: f"{k} {w}{'' if k == 1 else 's'}"  # noqa: E731
    return (f"{u(m, 'minute')} {u(s, 'second')}" if s else u(m, "minute")) if m else u(s, "second")


def prov_replication_py(P):
    """The replication plan's order of events as the page words it (site/app.js provReplication), from index.json's provenance."""
    R = P["replication"]
    lags = [R["first_run_lag_s"]] + [v for v in R["arm_run_lags_s"].values() if v < 120]
    return (f"the commit time, {utc_text_py(R['plan_commit_utc'])}, is {R['margin_s']} seconds before the first record’s start ({utc_clock_py(R['first_record_start_utc'])}), "
            f"and a run’s first record starts {min(lags)} to {max(lags)} seconds after the run is created (the first of these runs and two of the three Arm runs of the day before), "
            "so the margin lies within the range of the start lags and the order cannot be shown (the commit time is read on the author’s clock, the run times on GitHub’s and the runner’s).")


def prov_dsweep_py(P):
    """The d-sweep plan's public record as the page words it (site/app.js provDsweep)."""
    D = P["dsweep"]
    return (f"The public record is the temporary branch {D['branch']}: its commit {D['commit']} holds the plan file (the stored hash) together with the sweep code, "
            f"with the commit time {utc_clock_py(D['commit_utc'])} ({D['commit_utc'][:10]}), {min_sec_py(D['gap_s'])} before the first record started ({utc_clock_py(D['first_record_start_utc'])}); "
            "whether the plan was written before the code cannot be seen there.")


def num_word_py(n):
    return REP_NUM_WORDS[n] if n < len(REP_NUM_WORDS) else str(n)


def cap_py(t):
    return t[:1].upper() + t[1:]


def jobs_py(n):
    return f"{n} job{'' if n == 1 else 's'}"


def join_and_py(xs):
    return "".join(xs) if len(xs) <= 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def pct_s_py(v):
    return "0%" if v == 0 else f"{v:.4f}%" if v < 0.01 else f"{v:.3f}%" if v < 0.1 else f"{v:.2f}%" if v < 1 else f"{v:.1f}%"


def lr_py(v):
    return f"{v:.2f}" if v >= 2 else f"{v:.3f}"


def fx_py(v):
    return f"{v:.1f}" if v >= 2 else f"{v:.2f}"


def cell_name_py(cid):
    k, sz = cid.split(".")
    return f"the {ARM_SHORT_NAMES[k]} loop at the {sz} size"


def rep_kind(s):
    """The word class of one pooled set, from the stored form (not from the page's code): a map, inconclusive, too few jobs, or not drawn."""
    if not s or not s["jobs"]:
        return "none"
    if not s["enough"]:
        return "few"
    return "map" if s["form"] == "map" else "holds" if s["form"] == "holds_everywhere" else "inc"


def rep_with(s):
    return f"{REP_SAY[rep_kind(s)]} ({jobs_py(s['jobs'] if s else 0)})"


# Figure 8 on the main page calls the two sets "first" and "second" everywhere; set A, B and C belong to Table 14 on the details page
REP_SETS = {"earlier": "the first set", "replication": "the second set", "secondary": "both together"}


def rep_edge(R, r):
    """A different word that comes from the placement exemption switching between the sets (the flipped cells have different roles), not from a new cost."""
    f = next((x for x in R["arch"][r["arch"]]["flips"] if x["slug"] == r["slug"]), None)
    return bool(f) and all(c["earlier"]["role"] != c["replication"]["role"] for c in f["cells"])


def rep_title_py(R, rows):
    """Figure 8's title, recomputed from the stored words of the models that could be tested in both sets."""
    t = [r for r in rows if r["testable"]]
    same = [r for r in t if rep_status(r) == "same"]
    flip = [r for r in t if rep_status(r) == "flipped"]
    tail = f"; {len(flip)} {'flipped at a rule’s edge' if flip and all(rep_edge(R, r) for r in flip) else 'changed word'}" if flip else ""
    return f"Second set: same word on {len(same)} of {len(t)} models{tail}"


def first_diff(got, want):
    """Where two strings part, for a failure message ('' when they are equal)."""
    if got == want:
        return ""
    i = next((k for k, (a, b) in enumerate(zip(got, want)) if a != b), min(len(got), len(want)))
    return f"differs at {i}: page ...{got[max(0, i - 30):i + 50]!r} / expected ...{want[max(0, i - 30):i + 50]!r}"


def form_words_py(f):
    return "a map" if f == "map" else "a small cost everywhere" if f == "holds_everywhere" else "inconclusive"


def rep_status(r):
    """'same', 'flipped' or 'not testable', recomputed from the two words: the stored status must agree."""
    e, p = r["earlier"], r["replication"]
    if not (e and e["enough"] and p and p["enough"]):
        return "not testable"
    return "same" if e["form"] == p["form"] else "flipped"


def rep_aligned(r):
    """The plan counts the aligned ratios inside the earlier interval; the stored count has both columns, so a model's cells are half its points."""
    cells = r["inside"]["checked"] // 2
    return cells - sum(1 for m in r["inside"]["misses"] if m["column"] == "aligned"), cells


def rep_role(x):
    P = x["placement"]
    ci = f"{P['d_ci95'][0]:.3f} to {P['d_ci95'][1]:.3f}"
    if x["role"] == "exempt_placement_sensitive":
        return f"left out of the forward test as placement-sensitive (compiled ÷ aligned {ci}, which excludes 1 by {P['d_misses_one_by']:.4f})"
    miss = f", and it misses the {fx_py(x['limit'])}× limit by {x['aligned_hi_over_limit']:.4f}" if x.get("passes_forward_rule") is False else ""
    return f"judged (compiled ÷ aligned {ci}, which includes 1){miss}"


def rep_flip_text(R, arch, slug, names=None):
    A = R["arch"][arch]
    f = next((x for x in A["flips"] if x["slug"] == slug), None)
    if not f:
        return ""
    n = names or A["names"]
    return " ".join(
        f"{cap_py(cell_name_py(c['cell_id']))}, aligned: {c['earlier']['aligned']['ratio']:.3f}× in {n['earlier']} and {c['replication']['aligned']['ratio']:.3f}× in {n['replication']}; "
        f"its interval ends at {c['earlier']['aligned']['ci95'][1]:.4f} and {c['replication']['aligned']['ci95'][1]:.4f}, against the {fx_py(c['earlier']['limit'])}× limit. "
        f"In {n['earlier']} it is {rep_role(c['earlier'])}; in {n['replication']} it is {rep_role(c['replication'])}."
        for c in f["cells"])


def rep_drawn(models_drawn, shorts):
    return join_and_py([f"{shorts.get(m, m)} {n}" for m, n in sorted(models_drawn.items(), key=lambda kv: -kv[1])])


STICKY_JS = """(sel) => { const w = document.querySelector(sel); w.scrollLeft = w.scrollWidth; const r = w.getBoundingClientRect(), th = w.querySelector('tbody th').getBoundingClientRect(), hd = w.querySelector('thead th').getBoundingClientRect(), hint = w.previousElementSibling;
    return { th_left: Math.round(th.left - r.left), hd_left: Math.round(hd.left - r.left), th_w: Math.round(th.width), box_w: Math.round(r.width), scrolled: w.scrollLeft > 0, hint: !!hint && hint.classList.contains('swipe') && !hint.hidden && hint.getBoundingClientRect().height > 0 }; }"""


def sticky_ok(g):
    """A wide table scrolled to its right end keeps its row label in view (left edge, heading too, label at most half the box) and shows the swipe hint."""
    return g["scrolled"] and 0 <= g["th_left"] <= 4 and 0 <= g["hd_left"] <= 4 and g["th_w"] <= 0.5 * g["box_w"] and g["hint"]


FIG9_JS = """() => {
  const n = (e, a) => Number(e.getAttribute(a));
  const t = document.createElement('i'); t.style.background = 'var(--paper)'; document.body.append(t); const paper = getComputedStyle(t).backgroundColor; t.remove();
  const keys = [...document.querySelectorAll('#ds-cap .ds-key')].map((k) => { const cs = getComputedStyle(k); return { cls: k.classList.contains('ds-aligned') ? 'aligned' : 'as_compiled', bg: cs.backgroundColor, border: cs.borderTopWidth, bcol: cs.borderTopColor, next: (k.nextSibling ? k.nextSibling.textContent.trim().slice(0, 7) : '') }; });
  const panels = [...document.querySelectorAll('#ds-panels svg')].map((s) => {
    const band = s.querySelector('rect.ds-band');
    return { slug: s.dataset.slug,
      grid: [...s.querySelectorAll('line.ds-grid')].map((l) => [n(l, 'y1'), n(l, 'y2')]),
      ticks: [...s.querySelectorAll('text.ds-tick')].map((e) => ({ x: n(e, 'x'), y: n(e, 'y'), a: e.getAttribute('text-anchor'), t: e.textContent })),
      band: band ? [n(band, 'x'), n(band, 'width'), n(band, 'y'), n(band, 'height')] : null,
      circles: [...s.querySelectorAll('circle.ds-pt')].map((c) => { const cs = getComputedStyle(c); return { d: Number(c.dataset.d), col: c.classList.contains('ds-aligned') ? 'aligned' : 'as_compiled', cx: n(c, 'cx'), cy: n(c, 'cy'), fitted: c.classList.contains('fitted'), sel: c.classList.contains('sel'), fill: cs.fill, stroke: cs.stroke }; }),
      lines: [...s.querySelectorAll('polyline.ds-line')].map((l) => ({ col: l.classList.contains('ds-aligned') ? 'aligned' : 'as_compiled', pts: l.getAttribute('points').trim().split(/\\s+/).map((q) => q.split(',').map(Number)) })) };
  });
  return { paper, keys, panels };
}"""


def fig9_geometry(g, models, view, ns_of):
    """Everything Figure 9 draws, read back from the SVG and compared with the stored data: the y axis (value 0 lowest, labels at the right lines), the x axis, every point of
    both columns (as compiled, aligned) at its stored value, the fit band's two ends, each joined line through the fit ladder, which points are marked as fitted, the axis title,
    and the computed fill of filled and hollow points against the caption's key swatches. Returns a list of problems (empty when everything agrees)."""
    bad = []
    cols = ["as_compiled", "aligned"] if view == "ns" else ["as_compiled"]
    val = (lambda r, c: ns_of(r, c)) if view == "ns" else (lambda r, c: r["extra_instr_per_inner"])
    if [p["slug"] for p in g["panels"]] != [m["slug"] for m in models]:
        return [("panels", [p["slug"] for p in g["panels"]])]
    for p, m in zip(g["panels"], models):
        who = m["cpu_short"]
        gys = sorted(y for y, _ in p["grid"])
        yl = [(t["y"] - 4, float(t["t"])) for t in p["ticks"] if t["a"] == "end"]  # a label's baseline sits 4 px below its grid line
        xl = [(t["x"], float(t["t"])) for t in p["ticks"] if t["a"] == "middle" and re.fullmatch(r"\d+(\.\d+)?", t["t"])]
        title = [t["t"] for t in p["ticks"] if t["a"] == "middle" and not re.fullmatch(r"\d+(\.\d+)?", t["t"])]
        if len(yl) < 3 or len(xl) < 3:
            bad.append((who, "too few tick labels", len(yl), len(xl)))
            continue
        if title != ["d, the row length"]:
            bad.append((who, "axis title", title))
        if sorted(y for y, _ in yl) != [round(q, 6) for q in gys] and any(min(abs(y - q) for q in gys) > 0.01 for y, _ in yl):
            bad.append((who, "a y label is not on its grid line"))
        yl.sort(key=lambda t: t[1])
        (y0, v0), (y1, v1) = yl[0], yl[-1]
        if not (v0 == 0 and y0 > y1 and y0 == max(y for y, _ in yl)):
            bad.append((who, "y axis is not 0 at the bottom with larger values higher", yl[:2]))
            continue
        by = (y1 - y0) / (v1 - v0)
        if any(abs(y - (y0 + by * v)) > 0.05 for y, v in yl):
            bad.append((who, "y labels are not evenly spaced"))
        xl.sort(key=lambda t: t[1])
        (x0, d0), (x1, d1) = xl[0], xl[-1]
        bx = (x1 - x0) / (d1 - d0)
        if bx <= 0 or any(abs(x - (x0 + bx * d)) > 0.05 for x, d in xl):
            bad.append((who, "x axis is not increasing and evenly spaced"))
            continue
        px = lambda d: x0 + bx * d  # noqa: E731
        py = lambda v: y0 + by * v  # noqa: E731
        rows = {r["d"]: r for r in m["rows"]}
        got = {(c["d"], c["col"]): c for c in p["circles"]}
        if len(p["circles"]) != len(rows) * len(cols) or set(got) != {(d, c) for d in rows for c in cols}:
            bad.append((who, "points are not one per row length and column", len(p["circles"])))
            continue
        for (d, c), q in got.items():
            r = rows[d]
            if abs(q["cx"] - px(d)) > 0.1 or abs(q["cy"] - py(val(r, c))) > 0.1:
                bad.append((who, f"point d={d} {c} is at ({q['cx']:.1f}, {q['cy']:.1f}), stored value puts it at ({px(d):.1f}, {py(val(r, c)):.1f})"))
        want_fit = {r["d"] for r in m["rows"] if "fit" in r["roles"] or "study_l1" in r["roles"]}
        if {c["d"] for c in p["circles"] if c["fitted"]} != want_fit:
            bad.append((who, "the points marked as fitted are not the fit ladder"))
        fit = [r for r in m["rows"] if "fit" in r["roles"]]
        if p["band"] is None or abs(p["band"][0] - px(fit[0]["d"])) > 0.1 or abs(p["band"][0] + p["band"][1] - px(fit[-1]["d"])) > 0.1 or abs(p["band"][2] - min(gys)) > 0.1 or abs(p["band"][2] + p["band"][3] - max(gys)) > 0.1:
            bad.append((who, "the shaded band does not run from the first to the last fit row length over the full height", p["band"]))
        if sorted(l["col"] for l in p["lines"]) != sorted(cols):
            bad.append((who, "joined lines", [l["col"] for l in p["lines"]]))
        for l in p["lines"]:
            want = [(px(r["d"]), py(val(r, l["col"]))) for r in fit]
            if len(l["pts"]) != len(want) or any(abs(a - b) > 0.15 or abs(c - e) > 0.15 for (a, c), (b, e) in zip(l["pts"], want)):
                bad.append((who, f"the {l['col']} line does not run through the fit ladder at its stored values", len(l["pts"]), len(want)))
    keys = {k["cls"]: k for k in g["keys"]}
    fills = {(c["col"]): c["fill"] for p in g["panels"] for c in p["circles"] if c["fitted"] and not c["sel"]}  # the chosen point is drawn in the highlight colour
    if view == "ns":
        order = [(k["cls"], k["next"]) for k in g["keys"]]
        if order != [("as_compiled", "filled)"), ("aligned", "hollow)")] or set(keys) != {"as_compiled", "aligned"}:
            bad.append(("caption", "the key swatches are not as compiled (filled) then aligned (hollow)", order))
        elif not (fills["as_compiled"] != g["paper"] and fills["aligned"] == g["paper"] and keys["as_compiled"]["bg"] == fills["as_compiled"] and keys["aligned"]["bg"] == g["paper"]
                  and keys["aligned"]["border"] == "2px" and keys["aligned"]["bcol"] == next(c["stroke"] for p in g["panels"] for c in p["circles"] if c["fitted"] and not c["sel"] and c["col"] == "aligned")):
            bad.append(("caption", "a swatch and the points it names are drawn differently (the caption says as compiled is filled, aligned hollow)", fills, {k: v["bg"] for k, v in keys.items()}))
    return bad


REP_GEOM_JS = """() => {
  const f = document.getElementById('fig-rep'), rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
  const head = f.querySelector('.rep-head'), rows = [...f.querySelectorAll('#rep-rows .row')];
  const R = (e) => e.getBoundingClientRect(), bad = [];
  const track = (e) => getComputedStyle(e).gridTemplateColumns.split(' ').map(parseFloat);
  const apart = (a, b, what) => { if (b.left < a.right - 0.5) bad.push(what); };
  const line = (els, what) => { const rs = els.map((e) => R(e)).filter((r) => r.width > 0).sort((a, b) => a.left - b.left); for (let i = 1; i < rs.length; i++) if (Math.abs(rs[i].top - rs[i - 1].top) < 4) apart(rs[i - 1], rs[i], what); };
  if (getComputedStyle(head).display !== 'none') { const sp = [...head.children]; for (const s of sp) if (s.scrollWidth > s.clientWidth + 1) bad.push('header word ' + s.textContent + ' overflows'); line(sp, 'header words overlap'); }
  for (const r of rows) {
    const rr = R(r);
    if (r.scrollWidth > r.clientWidth + 1) bad.push(r.dataset.slug + ' row overflows');
    for (const c of r.children) { const cr = R(c); if (c.scrollWidth > c.clientWidth + 1) bad.push(r.dataset.slug + ' ' + c.className + ' overflows'); if (cr.left < rr.left - 1 || cr.right > rr.right + 1) bad.push(r.dataset.slug + ' ' + c.className + ' leaves the row'); }
    line([...r.children], r.dataset.slug + ' cells overlap');
    for (const g of r.querySelectorAll('.rg')) { const gr = R(g); line([...g.children], r.dataset.slug + ' mark and count overlap'); for (const k of g.children) { const kr = R(k); if (kr.left < gr.left - 1 || kr.right > gr.right + 1) bad.push(r.dataset.slug + ' mark or count leaves its cell'); } }
    const bar = r.querySelector('.rbar'), rn = r.querySelector('.rn');
    if (bar && rn && getComputedStyle(bar).display !== 'none') apart(R(bar), R(rn), r.dataset.slug + ' bar and count overlap');
  }
  const stackedLabels = rows.length ? rows.flatMap((r) => [...r.children].slice(1).map((c) => getComputedStyle(c, '::before').content)) : [];
  return { fig_w: f.clientWidth, rem, rows: rows.map((r) => ({ slug: r.dataset.slug, h: Math.round(R(r).height) })), bad,
    row_tracks: rows.length ? track(rows[0]) : [], head_tracks: track(head), head_display: getComputedStyle(head).display, row_display: rows.length ? getComputedStyle(rows[0]).display : '', labels: stackedLabels };
}"""


def replication_checks(browser, base, ck, index, allowed, saved, shots):
    """The second set of runs (data/replication.json): Figure 8 on the main page (section 1) and the account with Table 14 on the details page.
    Everything printed is recomputed here from the data file: the six rows in the stored order, each set's word and job count, the inside counts (both
    columns, and the aligned column alone), the title's counts from the recomputed statuses, the readout per row (the flip cells with their placement
    numbers, the not-testable model, the Arm cell), the account's paragraphs and Table 14. Also: the readout is hidden until a row is chosen, the keys,
    no number typed into the new HTML, no workflow-run link, finger-sized rows and no sideways scroll at 390 and 320 px, no console errors."""
    print("== the replication: Figure 8 (main page, section 1) and the account with Table 14 (details page)")
    with open(os.path.join(DATA, "replication.json"), encoding="utf-8") as f:
        R = json.load(f)
    norm = lambda s: " ".join(s.replace(" ", " ").split())  # noqa: E731
    shorts = {r["cpu_model"]: r["cpu_short"] for r in R["rows"]}
    rows = [r for r in R["rows"] if r["earlier"] and r["earlier"]["enough"]]  # the models with a verdict in the first set
    X, AR, P, Q, crit = R["arch"]["x86"], R["arch"]["arm"], R["pools"], R["questions"], R["criteria"]
    ck.ok(index["sections"].get("replication") == "data/replication.json" and R["plan"] == "replication/PLAN.md" and crit["minimum_jobs"] == 3
          and all(r["status"] == rep_status(r) for r in R["rows"]) and all(r["testable"] == (r["status"] != "not testable") for r in R["rows"]),
          "the replication file is registered in index.json, names replication/PLAN.md, and every row's stored status equals the status recomputed from its two words")
    same_n = [r for r in rows if r["status"] == "same"]
    flip_n = [r for r in rows if r["status"] == "flipped"]
    ck.ok(len(rows) == 6 and sum(1 for r in rows if r["arch"] == "arm") == 1 and len(same_n) + len(flip_n) + sum(1 for r in rows if r["status"] == "not testable") == len(rows)
          and X["totals"]["flipped"] + AR["totals"]["flipped"] == len(flip_n) and X["totals"]["same_form"] + AR["totals"]["same_form"] == len(same_n),
          f"the data have six models with a first-set verdict (five x86-64 and the Arm core): {len(same_n)} same word, {len(flip_n)} different, the rest not testable; the per-architecture totals agree")

    # ---- the main page, every section open, 1280 wide
    errors = []
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    watch(pg, errors)
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_function("document.querySelectorAll('#rep-rows .row').length > 0 && document.getElementById('rep-cap').textContent.length > 20", timeout=20000)
    pg.wait_for_timeout(300)
    where = pg.evaluate("""() => { const f = document.getElementById('fig-rep'), n = f.nextElementSibling;
        return [f.parentElement.closest('section[id]').id, f.previousElementSibling.id, n.className, n.querySelector('a').getAttribute('href')]; }""")
    ck.ok(where == ["result", "cpu-note", "more-link", "details.html#holdout-full"],
          f"main page: Figure 8 sits in section 1, after Table 1's note and before the holdout link to details.html#holdout-full ({where})")
    title = norm(pg.inner_text("#rep-title"))
    want_title = rep_title_py(R, rows)
    ck.ok(title == want_title and "cost" not in title and len(same_n) + len(flip_n) == sum(1 for r in rows if r["testable"]),
          f"Figure 8's title counts the models that could be tested in both sets, from the stored words, and names a flip by what it is without saying the cost changed: {want_title!r} (page: {title!r})")
    lab8 = pg.get_attribute("#rep-rows", "aria-label")
    ck.ok(lab8 == "CPU models: the verdict word on the first set of runs, on the second set and on both together. Use the arrow keys to select one.",
          f"Figure 8's list label, word for word: it names the first set, the second set and both together, so a swapped or reduced label fails ({lab8!r})")
    lines8 = pg.evaluate("(() => { const t = document.getElementById('rep-title'), cs = getComputedStyle(t); return Math.round(t.getBoundingClientRect().height / parseFloat(cs.lineHeight)); })()")
    ck.ok(lines8 == 1, f"Figure 8's title is one line at 1280 wide ({lines8})")
    head = pg.evaluate("[...document.querySelectorAll('#fig-rep .rep-head span')].map(s => s.textContent)")
    key = norm(pg.inner_text("#rep-key"))
    ck.ok(head == ["", "first", "second", "both", "inside"] and key == "map inconclusive too few jobs n = jobs"
          and pg.evaluate("[...document.querySelectorAll('#rep-key .rg')].map(g => g.className.replace('rg ', ''))") == ["g-map", "g-inc", "g-few"],
          f"Figure 8 labels its columns (first, second, both, inside) and keys the three marks and the job count ({head}, {key!r})")
    cap = norm(pg.inner_text("#rep-cap"))
    want_cap = (f"Figure 8. A set is one batch of runs. Inside: of {rows[0]['inside']['checked']} pooled ratios, those of the second set in the first set’s 95% interval (Table 14). "
                "“Both” is secondary.")
    ck.ok(cap == want_cap and pg.evaluate("[...document.querySelectorAll('#rep-cap a')].map(a => [a.getAttribute('href'), a.textContent.replace(/\\s/g, ' ')])") == [["details.html#rep-t-cap", "Table 14"]],
          "Figure 8's caption defines a set and 'Inside' with the 32 from the data in the same two names the title, heads and readout use (first, second), says 'Both' is secondary, and links to Table 14's caption")
    arm_link = pg.evaluate("(() => { const n = document.getElementById('arm-rep-link'); const a = n && n.querySelector('a'); return [n ? n.textContent.replace(/\\s+/g, ' ').trim() : null, a ? a.getAttribute('href') : null]; })()")
    Qa = Q["arm_cell"]
    want_link = f"A second set {'repeats the word, weakly' if Qa['repeated'] else 'read'}: {form_words_py(Qa['replication_form'])} (Figure 8)."
    ck.ok(arm_link == [want_link, "#fig-rep"] and pg.evaluate("document.getElementById('arm-rep-link').closest('#arm') !== null"),
          f"section 6a: one sentence tells the reader a second set of Arm runs read the same word on the same cell and calls it a weak repeat, and links to Figure 8 ({arm_link})")
    got = pg.evaluate("""() => [...document.querySelectorAll('#rep-rows .row')].map(b => ({ slug: b.dataset.slug, name: b.querySelector('.name').textContent, role: b.getAttribute('role'), sel: b.getAttribute('aria-selected'),
        tab: b.tabIndex, gap: b.classList.contains('rep-gap'), label: b.getAttribute('aria-label'), glyphs: [...b.querySelectorAll('.rg')].map(g => [g.className.replace('rg ', ''), g.querySelector('b').textContent]),
        inside: b.querySelector('.rn').textContent, bar: b.querySelector('.rbar i') ? b.querySelector('.rbar i').style.width : null })) """)
    bad = []
    for g, r in zip(got, rows):
        gl = [[f"g-{rep_kind(s)}", str(s["jobs"]) if s and s["jobs"] else "–"] for s in (r["earlier"], r["replication"], r["secondary"])]
        ins = f"{r['inside']['inside']}/{r['inside']['checked']}" if r["inside"] else "–"
        n = REP_SETS
        lab = f"{r['cpu_short']}: {n['earlier']}: {rep_with(r['earlier'])}; {n['replication']}: {rep_with(r['replication'])}; {n['secondary']}: {rep_with(r['secondary'])}; " + (f"{ins.replace('/', ' of ')} pooled ratios of the second set inside the first set’s interval" if r["inside"] else "not testable")
        if (g["slug"], g["name"], g["role"], g["sel"], g["glyphs"], g["inside"], g["label"]) != (r["slug"], r["cpu_short"], "option", "false", gl, ins, lab):
            bad.append((g["slug"], g["glyphs"], g["inside"], g["label"], lab))
    ck.ok(len(got) == len(rows) and not bad, f"Figure 8: six rows in the stored order, each with its three marks and job counts, the inside count and a full spoken label, recomputed from the data ({bad[:1]})")
    ck.ok([g["gap"] for g in got] == [r["arch"] == "arm" for r in rows], "Figure 8: the Arm row (and only it) is set off from the x86-64 rows by a gap")
    ck.ok(sum(1 for g in got if g["tab"] == 0) == 1 and not pg.evaluate("document.getElementById('rep-read').hidden === false"), "Figure 8: one row is in the tab order and the readout is hidden until a row is chosen")
    for r, g in zip(rows, got):
        if r["inside"]:
            want_w = 100 * r["inside"]["inside"] / r["inside"]["checked"]
            if abs(float(g["bar"].rstrip("%")) - want_w) > 0.06:
                ck.ok(False, f"Figure 8: the inside bar of {r['cpu_short']} is {g['bar']}, the data say {want_w:.1f}%")
    # ---- the readout of every row
    bad_read, all_read = [], []
    for r in rows:
        pg.click(f'#rep-rows .row[data-slug="{r["slug"]}"]')
        pg.wait_for_timeout(60)
        txt = norm(pg.inner_text("#rep-read"))
        all_read.append(txt)
        n = REP_SETS
        A_ = X if r["arch"] == "x86" else AR
        want = [f"{r['cpu_short']} {cap_py(n['earlier'])}: {rep_with(r['earlier'])}; {n['replication']}: {rep_with(r['replication'])}; {n['secondary']}: {rep_with(r['secondary'])}."]
        if r["inside"]:
            a, c = rep_aligned(r)
            want.append(f"{r['inside']['inside']} of {r['inside']['checked']} pooled ratios of {n['replication']} lie inside the 95% interval of {n['earlier']} (aligned alone {a} of {c}); the largest difference between two ratios is {pct_s_py(r['inside']['max_abs_point_diff_pct'])}.")
        if r["status"] == "flipped":
            want.append("The different word is a placement-exemption edge, not a change of cost. " + rep_flip_text(R, r["arch"], r["slug"], REP_SETS))
        if not r["testable"]:
            # the count comes from the stored pooled set (secondary.jobs), and must equal the first set's jobs plus the second set's
            sj, ej, pj = r["secondary"]["jobs"], r["earlier"]["jobs"], (r["replication"]["jobs"] if r["replication"] else 0)
            want.append(f"{cap_py(n['replication'])} drew {jobs_py(pj)} of it ({crit['minimum_jobs']} are needed), so whether the first reading repeats is not answered either way. Pooled with it, the {jobs_py(sj)} ({ej} of {n['earlier']} and {pj} of {n['replication']}) read {REP_SAY[rep_kind(r['secondary'])]}.")
            m_ = re.search(r"both together: [a-z ]+ \((\d+) jobs?\)", txt)
            m2 = re.search(r"Pooled with it, the (\d+) jobs?", txt)
            if not (m_ and m2 and m_.group(1) == m2.group(1) and int(m2.group(1)) == ej + pj == sj):
                bad_read.append((r["slug"], "the pooled count in the note is not the pooled count in the head", [m_ and m_.group(1), m2 and m2.group(1), ej, pj, sj]))
        if r["arch"] == "arm":
            c = AR["named_cells"][0]
            below = c["earlier"]["aligned"]["ratio"] < 1 and c["replication"]["aligned"]["ratio"] < 1
            want.append(f"Both sets are decided by one cell, {cell_name_py(c['cell_id'])}, aligned: it ends at {c['earlier']['aligned']['ci95'][1]:.4f} in {n['earlier']} and {c['replication']['aligned']['ci95'][1]:.4f} in {n['replication']}, "
                        f"against the {fx_py(c['earlier']['limit'])}× limit, with ratios of {c['earlier']['aligned']['ratio']:.3f} and {c['replication']['aligned']['ratio']:.3f}. Pooled ({n['secondary']}) it ends at {c['secondary']['aligned']['ci95'][1]:.4f}: the ratio is about the same, the interval narrower. "
                        f"Both ends sit near the limit{' while both ratios are below 1' if below else ''}, so a second inconclusive is a weak repeat of the word, not independent confirmation of an effect (section 6a).")
            if pg.evaluate("[...document.querySelectorAll('#rep-read a')].map(a => a.getAttribute('href'))") != ["#arm"]:
                bad_read.append((r["slug"], "the Arm readout does not link back to section 6a", None))
        shown = pg.evaluate("(() => { const b = document.getElementById('rep-read'); return [!b.hidden, document.querySelector('#rep-rows .row[aria-selected=true]').dataset.slug]; })()")
        if not (shown == [True, r["slug"]] and txt == " ".join(want) and (r["status"] == "flipped") == ("placement-exemption edge" in txt) and (not r["testable"]) == ("not answered either way" in txt)):
            bad_read.append((r["slug"], shown, [w for w in want if w not in txt][:1], txt[:60]))
    ck.ok(not bad_read, f"Figure 8: choosing a row shows its readout, word for word as built from the data: that row's words, the inside counts (both columns and aligned alone), the largest difference, and for the flipped rows the cell, its ratios, interval ends, limit and placement numbers; for the untestable model 'not answered either way' with the pooled job count taken from the stored pooled set and equal to the head's; for the Arm row the deciding cell, the weak-repeat sentence and the link back to section 6a ({bad_read[:1]})")
    ck.ok(not re.search(r"\bset [ABC]\b|first pool|sets A and B", " ".join(all_read) + " " + title + " " + cap), "Figure 8, caption and every readout use only 'first' and 'second' for the two sets: set A, B and C and 'the first pool' stay in Table 14")
    bad_numbers = page_numbers(pg, allowed, "#fig-rep")
    ck.ok(not bad_numbers, "Figure 8 with a readout open: every number printed is in the data" + ("" if not bad_numbers else f": {bad_numbers[:4]}"))
    pg.click(f'#rep-rows .row[data-slug="{rows[-1]["slug"]}"]')
    pg.wait_for_timeout(60)
    ck.ok(pg.evaluate("document.getElementById('rep-read').hidden") and pg.evaluate("document.querySelectorAll('#rep-rows .row[aria-selected=true]').length") == 0, "Figure 8: choosing the chosen row again closes the readout")
    # ---- keys
    pg.evaluate("document.querySelector('#rep-rows .row').focus()")
    pg.keyboard.press("ArrowDown")
    k1 = pg.evaluate("document.querySelector('#rep-rows .row[aria-selected=true]').dataset.slug")
    pg.keyboard.press("End")
    k2 = pg.evaluate("document.querySelector('#rep-rows .row[aria-selected=true]').dataset.slug")
    pg.keyboard.press("Home")
    k3 = pg.evaluate("document.querySelector('#rep-rows .row[aria-selected=true]').dataset.slug")
    pg.keyboard.press("ArrowDown"); pg.keyboard.press("ArrowUp")
    k4 = pg.evaluate("document.querySelector('#rep-rows .row[aria-selected=true]').dataset.slug")
    ck.ok([k1, k2, k3, k4] == [rows[1]["slug"], rows[-1]["slug"], rows[0]["slug"], rows[0]["slug"]], f"Figure 8: the arrow keys, Home and End move the selection through the six rows ({[k1, k2, k3, k4]})")
    # ---- markup types no number; no workflow-run link
    with open(os.path.join(SITE, "index.html"), encoding="utf-8") as f:
        src = f.read()
    with open(os.path.join(SITE, "details.html"), encoding="utf-8") as f:
        dsrc = f.read()
    fig_src = src.split('<figure class="fig rep-fig" id="fig-rep">')[1].split("</figure>")[0]
    det_src = dsrc.split('<h3 id="replication-full">')[1].split("</section>")[0]
    typed = []
    for name, text in (("index.html #fig-rep", fig_src), ("details.html #replication-full", det_src)):
        plain = re.sub(r"<[^>]+>", " ", text)
        plain = re.sub(r"Figure 8|Table 14|x86-64|&[a-z]+;", " ", plain)
        typed += [(name, m) for m in re.findall(r"\d+(?:\.\d+)?", plain)]
    ck.ok(not typed, f"the new replication HTML types no number: every figure is filled from site/data ({typed[:4]})")
    ck.ok("/actions/runs" not in fig_src + det_src and pg.evaluate("document.querySelectorAll('#fig-rep a[href*=\"actions\"]').length") == 0, "the replication blocks link to no workflow run")
    ck.ok(not errors, "Figure 8, 1280: no console errors, page errors or failed data requests" + ("" if not errors else f": {errors[:3]}"))
    pg.close()

    # ---- the details page
    errors_d = []
    dp = browser.new_page(viewport={"width": 1280, "height": 900})
    watch(dp, errors_d)
    dp.goto(base + "details.html", wait_until="networkidle")
    dp.wait_for_function("document.querySelectorAll('#rep-table tbody tr').length > 0", timeout=20000)
    dp.evaluate("document.querySelectorAll('details.fold').forEach(d => { d.open = true; })")
    dp.wait_for_timeout(200)
    txt = {i: norm(dp.inner_text("#" + i)) for i in ("rep-what", "rep-count", "rep-x86", "rep-flips", "rep-6973", "rep-arm", "rep-headline", "rep-t-cap", "rep-limits")}
    order = dp.evaluate("[...document.querySelectorAll('#replication-full ~ *')].filter(n => !n.classList.contains('scroll-hint')).map(n => n.id || n.tagName).slice(0, 10)")
    ck.ok(order[:10] == ["rep-what", "rep-count", "rep-x86", "rep-flips", "rep-6973", "rep-arm", "rep-headline", "rep-t-cap", "DIV", "rep-limits"]
          and dp.evaluate("document.getElementById('replication-full').previousElementSibling.tagName") == "DIV",
          f"details: the replication account follows the holdout table in the order what, count, x86-64, flips, 6973P-C, Arm, headline, Table 14, limits ({order})")
    q6, am = Q["xeon_6973pc"], AR["named_cells"][0]
    thin = max(q6["earlier_closest_forward"]["margin"], am["earlier"]["aligned_hi_over_limit"])
    red = [i for i in ("39012986182", "39013000285") if i in P["x86"]["replication"]["run_ids"]]  # the two combine runs that went red on pool_check (they ran in the second x86-64 set)
    want_what = (f"Why a second set, and how it is read. Two readings rested on a forward cell whose interval ended within {thin:.4f} of the limit, the Arm core’s and the Xeon 6973P-C’s, so more runs were requested. "
                 f"The plan (replication/PLAN.md) was committed in the author’s unpublished development history, by the author’s account before the runs were dispatched, and this repository cannot show that order: {prov_replication_py(index['provenance'])} "
                 "The hash stored with the comparison shows the file’s integrity, not when it was written. "
                 f"It fixes the reading: each set is pooled on its own, by the same code under the same rule file ({crit['file']}), and for each cell it asks whether the second set’s pooled aligned ratio lies inside the first set’s 95% interval, reported as a share, whatever comes out. "
                 f"The rule file was not changed after a result (every record stores its hash), and by the author’s account neither were the pooling code and the statistics; one consistency check (harness/pool_check.py) was changed afterwards to sample only models with at least {crit['minimum_jobs']} jobs, "
                 f"after {num_word_py(len(red))} combine runs ({join_and_py(red)}) went red on it for models with fewer, and no verdict uses such a model. "
                 f"{cap_py(X['names']['replication'])} is {len(P['x86']['replication']['run_ids'])} more x86-64 runs ({P['x86']['replication']['jobs']} jobs), drawn by GitHub from the same pool of machines; "
                 f"{AR['names']['replication']} is {len(P['arm']['replication']['run_ids'])} more Arm runs ({P['arm']['replication']['jobs']} jobs). "
                 "The pooled forms of the two sets together are secondary: the sets were requested after a borderline reading, so the stopping point depended on the data, and they never replace a set read alone. "
                 "The earlier pools’ stored verdicts are unchanged. No further runs will be made for these questions.")
    ck.ok(txt["rep-what"] == want_what and len(red) == 2,
          f"details, 'Why a second set', word for word: the plan committed before the dispatch in unpublished history, with the commit time, the margin to the first record's start and the start lag, all from the records (the margin lies within the range of the lags, so the order cannot be shown, and the three clocks are named) and a hash that shows integrity only; what the plan asks (the second set's aligned ratio inside the first set's interval, as a share, whatever comes out); the one consistency check changed afterwards and the two red runs by id; set sizes from the data; the pooled forms secondary; no further runs ({first_diff(txt['rep-what'], want_what)})")
    alx = [rep_aligned(r) for r in R["rows"] if r["arch"] == "x86" and r["inside"]]
    ala = [rep_aligned(r) for r in R["rows"] if r["arch"] == "arm" and r["inside"]]
    cells_n = rows[0]["inside"]["checked"] // 2
    want_count = (f"How points are counted. The plan asks whether each cell’s pooled aligned ratio lies inside the earlier interval. The stored count compares both columns, as compiled and aligned, with the earlier pool’s 95% interval: "
                  "the point-inside-interval test of harness/pool.py, which this page also uses to compare one run with another. The both-column form was written into replication/compare.py "
                  f"after the sets’ data were in, so a model has {cells_n} cells and {2 * cells_n} points. Counted on the aligned column alone, as the plan asked: Arm {sum(a for a, _ in ala)} of {sum(c for _, c in ala)}, x86-64 {sum(a for a, _ in alx)} of {sum(c for _, c in alx)}. "
                  "The count is descriptive: a second set’s pooled ratio carries its own noise, so fewer than 95% of its points are expected inside the first set’s interval even when nothing has changed, and the share mostly follows interval width and set size; no expected count is claimed. "
                  f"{AR['totals']['point_diff_under_1pct']} of {AR['totals']['points_checked']} Arm points and {X['totals']['point_diff_under_1pct']} of {X['totals']['points_checked']} x86-64 points differ from the earlier pooled ratio by under 1%, "
                  f"and the largest differences are {pct_s_py(AR['totals']['max_abs_point_diff_pct'])} (Arm) and {pct_s_py(X['totals']['max_abs_point_diff_pct'])} (x86-64).")
    ck.ok(txt["rep-count"] == want_count and "holdout" not in txt["rep-count"],
          f"details, 'How points are counted', word for word: both columns, harness/pool.py as the source of the test (no holdout-column precedent), the both-column form written after the data, the aligned column alone beside it ({sum(a for a, _ in ala)} of {sum(c for _, c in ala)} on Arm, {sum(a for a, _ in alx)} of {sum(c for _, c in alx)} on x86-64), the count called descriptive with no expected count claimed, the under-1% counts ({first_diff(txt['rep-count'], want_count)})")
    xs = txt["rep-x86"]
    x_same = [r["cpu_short"] for r in rows if r["arch"] == "x86" and r["status"] == "same"]
    x_flip = [r["cpu_short"] for r in rows if r["arch"] == "x86" and r["status"] == "flipped"]
    want_xs = (f"x86-64, set C. {P['x86']['replication']['jobs']} jobs drew {rep_drawn(P['x86']['replication']['models_drawn'], shorts)}. "
               f"Of the {num_word_py(X['totals']['testable_models'])} models with at least {crit['minimum_jobs']} jobs in both sets, {num_word_py(len(x_same))} gave the same verdict word ({join_and_py(x_same)}) and {num_word_py(len(x_flip))} a different one ({join_and_py(x_flip)}). "
               f"{X['totals']['points_inside']} of {X['totals']['points_checked']} pooled ratios lie inside the first pool’s interval.")
    ck.ok(xs == want_xs, f"details, x86-64, word for word: the machines set C drew, the models with the same and a different word, and the inside count, recomputed from the data ({first_diff(xs, want_xs)})")
    fl = txt["rep-flips"]
    want_fl = (f"The {num_word_py(len(X['flips']))} different words are one edge, not a change of cost. The placement test leaves a forward cell out of the 2% test when its compiled ÷ aligned interval excludes 1 and its hot loop sits differently in the two as-compiled builds, and judges it otherwise. "
               + " ".join(f"{f['cpu_short']}: {rep_flip_text(R, 'x86', f['slug'])}" for f in X["flips"])
               + " Neither cell’s cost changed between the sets; the model’s word depends on which side of the test the cell lands.")
    ck.ok(fl == want_fl and len(X["flips"]) == len(flip_n) == 2,
          f"details, the two flips, word for word: the placement test's full rule (the compiled ÷ aligned interval excludes 1 and the hot loop sits differently), each cell with both sets' aligned ratios, interval ends, the limit and the placement numbers, framed as the exemption's edge, not a change of cost ({first_diff(fl, want_fl)})")
    s6 = txt["rep-6973"]
    r6 = next(r for r in R["rows"] if r["slug"] == q6["slug"])
    missed = (q6["secondary_cause"]["forward_missed"] or [None])[0]
    miss_txt = f": {cell_name_py(missed['cell_id'])} ends at {missed['aligned_ci95'][1]:.4f}" + (", a cell that was placement-sensitive, and so left out, in the first pool and is judged with the extra job" if missed["cell_id"] in r6["earlier"]["placement_sensitive"] and missed["cell_id"] not in r6["secondary"]["placement_sensitive"] else "") + ". " if missed else ". "
    want6 = (f"{q6['cpu_short']} cannot be tested. {cap_py(X['names']['replication'])} drew {jobs_py(q6['replication_jobs'])} of it ({q6['minimum_jobs']} are needed), so it has no verdict there, and the question the plan asked of it, whether its borderline {re.sub('^a ', '', REP_SAY[rep_kind(r6['earlier'])])} repeats, is not answered either way. "
             f"In {X['names']['earlier']} ({q6['earlier_jobs']} jobs) it is {REP_SAY[rep_kind(r6['earlier'])]}, with {cell_name_py(q6['earlier_closest_forward']['cell_id'])} ending nearest the limit, at {q6['earlier_closest_forward']['aligned_hi']:.4f}. "
             f"Pooled with {X['names']['replication']}’s {jobs_py(q6['replication_jobs'])} ({q6['secondary_jobs']} jobs) it reads {REP_SAY[rep_kind(r6['secondary'])]}" + miss_txt + "That pooled word is secondary and rests on this one added job.")
    ck.ok(not q6["testable"] and s6 == want6, f"details, the Xeon 6973P-C, word for word: not testable (set C drew {q6['replication_jobs']} of the {q6['minimum_jobs']} jobs needed), the plan's question not answered either way, the first pool's nearest cell at {q6['earlier_closest_forward']['aligned_hi']:.4f}, the pooled word secondary ({first_diff(s6, want6)})")
    sa = txt["rep-arm"]
    n_arm = AR["names"]
    rn2 = next(r for r in R["rows"] if r["arch"] == "arm" and r["testable"])
    v3_ = next((r for r in R["rows"] if r["arch"] == "arm" and not r["earlier"]), None)
    rep_tail = (f", as {n_arm['earlier']} was" + (", and on the same cell that decided the first reading" if Q["arm_cell"]["replication_names_the_same_cells"] else "")) if Q["arm_cell"]["repeated"] else f", where {n_arm['earlier']} was {REP_SAY[rep_kind(rn2['earlier'])]}"
    want_a = (f"Arm. {cap_py(n_arm['replication'])} is {P['arm']['replication']['jobs']} jobs: {rep_drawn(P['arm']['replication']['models_drawn'], shorts)}" + (f"; the {v3_['cpu_short']} job has no verdict" if v3_ else "")
              + f". Read alone it is {REP_SAY[rep_kind(rn2['replication'])]}{rep_tail}: {cell_name_py(am['cell_id'])}, aligned, ends at {am['replication']['aligned']['ci95'][1]:.4f} in {n_arm['replication']} and at {am['earlier']['aligned']['ci95'][1]:.4f} in {n_arm['earlier']}, "
              f"against the {fx_py(am['earlier']['limit'])}× limit, with ratios below 1 ({am['replication']['aligned']['ratio']:.3f} and {am['earlier']['aligned']['ratio']:.3f}). "
              f"{cap_py(n_arm['secondary'])} pooled ({rn2['secondary']['jobs']} {rn2['cpu_short']} jobs) read {REP_SAY[rep_kind(rn2['secondary'])]}, the cell ending at {am['secondary']['aligned']['ci95'][1]:.4f} with a ratio of {am['secondary']['aligned']['ratio']:.3f}: "
              "the ratio is about the same in all three, and only the interval narrows with more jobs. That pooled word is secondary.")
    ck.ok(am["cell_id"] == "k02_add_fwd.L2" and sa == want_a and "30 N2 jobs" not in sa and "30 Neoverse-N2 jobs" not in sa,
          f"details, Arm, word for word: set B's mix of cores (never called 30 Neoverse-N2 jobs), its word read alone, the one deciding cell with both sets' interval ends and ratios, and the pooled word named secondary ({first_diff(sa, want_a)})")
    hd = txt["rep-headline"]
    H = X["headline"]
    ok_e = H["replication_enough_range"]
    rep_models = [m["cpu_short"] for m in H["replication"] if m["enough"]]
    out0 = H["outside_stored_range"][0] if H["outside_stored_range"] else None
    pm = lambda v: v if isinstance(v, str) else f"{v:.1f}"  # noqa: E731
    want_h = (f"The headline range. The loops that lose SIMD cost {pm(H['page_range']['printed_min'])}× to {pm(H['page_range']['printed_max'])}× in cache on the first pool. "
              f"In {X['names']['replication']}, the {num_word_py(len(rep_models))} models with at least {crit['minimum_jobs']} jobs ({join_and_py(rep_models)}) give {ok_e['min']:.3f}× to {ok_e['max']:.3f}× (both columns, both sizes)"
              + (f"; the cell furthest below the first pool’s minimum ({H['page_range']['min']:.4f}×) is {cell_name_py(out0['cell_id'])} of {shorts[out0['cpu_model']]}, {'aligned' if out0['column'] == 'aligned' else 'as compiled'}, at {out0['ratio']:.4f}×" if out0 else "")
              + ". " + ("Some cells lie outside the printed range." if H["outside_printed_range"] else f"Nothing in set C lies outside the printed {pm(H['page_range']['printed_min'])}× to {pm(H['page_range']['printed_max'])}×."))
    ck.ok(hd == want_h, f"details, the headline range, word for word: the first pool's printed range, set C's own range ({ok_e['min']:.3f}× to {ok_e['max']:.3f}×) from the models with enough jobs, the cell nearest below the minimum, and whether anything lies outside the printed range ({first_diff(hd, want_h)})")
    tab = dp.evaluate("[...document.querySelectorAll('#rep-table tbody tr')].map(tr => [...tr.children].map(c => c.textContent.replace(/\\s+/g, ' ').trim()))")
    heads = dp.evaluate("[...document.querySelectorAll('#rep-table thead th')].map(c => c.textContent.trim())")
    cell_t = lambda s: f"{REP_SAY[rep_kind(s)]}, {jobs_py(s['jobs'])}" if s else "not drawn"  # noqa: E731
    want_tab = []
    for r in R["rows"]:
        if r["inside"]:
            a, c = rep_aligned(r)
            ins, dmax = f"{r['inside']['inside']} of {r['inside']['checked']} ({a} of {c})", pct_s_py(r["inside"]["max_abs_point_diff_pct"])
        else:
            ins, dmax = "–", "–"
        want_tab.append([r["cpu_short"], cell_t(r["earlier"]), cell_t(r["replication"]), cell_t(r["secondary"]), ins, dmax, {"same": "same word", "flipped": "different word", "not testable": "not testable"}[r["status"]]])
    heads_want = ["CPU model", "First set", "Second set", "Both together (secondary)", "Pooled ratios inside the first set’s interval (aligned alone)", "Largest difference", "Status"]
    ck.ok(tab == want_tab and heads == heads_want, f"Table 14: {len(R['rows'])} rows (every CPU model in the file) with the three words and job counts, the inside counts (aligned alone in brackets), the largest difference and the status, equal to the data, under exactly these seven column heads ({heads}; {[(a, b) for a, b in zip(tab, want_tab) if a != b][:1]})")
    h3_rep = dp.evaluate("document.getElementById('replication-full').textContent.trim()")
    aria14 = dp.evaluate("document.querySelector('#rep-table').closest('.tablewrap').getAttribute('aria-label')")
    ck.ok(h3_rep == "Replication: a second set of runs" and aria14 == "Table 14, the replication per CPU model; scrolls sideways on a narrow screen, the model stays in view",
          f"the replication's heading and Table 14's region label, word for word ({h3_rep!r}, {aria14!r})")
    cp = txt["rep-t-cap"]
    want_cp = (f"Table 14. Per CPU model: the verdict word and job count in the first set, the second set and both together (secondary), how many of the model’s {2 * cells_n} pooled ratios (both columns) lie inside the first set’s 95% interval (aligned alone in brackets), "
               f"and the largest difference between a first-set and a second-set ratio. x86-64: the first set is the {P['x86']['earlier']['jobs']}-job pool, the second set is set C; Arm: set A and set B, {P['arm']['earlier']['jobs']} jobs each. "
               f"A model with fewer than {crit['minimum_jobs']} jobs in a set has no verdict there.")
    ck.ok(cp == want_cp, f"Table 14's caption, word for word: both columns counted, the aligned count in brackets, the sets named with their sizes (and set A, B and C mapped to first and second here), the 3-job minimum ({first_diff(cp, want_cp)})")
    lim = txt["rep-limits"]
    want_lim = (f"Limits. The machines in each set are drawn by GitHub, not chosen, so the sets hold few jobs of the rarer models ({rep_drawn(P['x86']['replication']['models_drawn'], shorts)} in set C). "
                "Nothing here tests another compiler, another libc++ version or other cores, and the inside count is descriptive: no expected count is claimed. The stored verdicts of the first sets are unchanged.")
    ck.ok(lim == want_lim, f"details, the replication's limits, word for word: the machines are drawn by GitHub (set C's mix named), no other compiler, libc++ or core, the inside count descriptive with no expected count claimed, the first sets' verdicts unchanged ({first_diff(lim, want_lim)})")
    bad_n = []
    for i in txt:
        bad_n += unknown_numbers(dp.evaluate(f"(() => ({PAGE_TEXT_JS})(document.getElementById('{i}')))()"), allowed)
    bad_n += unknown_numbers(dp.evaluate(f"(() => ({PAGE_TEXT_JS})(document.getElementById('rep-table')))()"), allowed)
    ck.ok(not bad_n, "details: every number in the replication account and Table 14 is in the data" + ("" if not bad_n else f": {bad_n[:4]}"))
    bad_w = [w_ for w_ in ("the truth", "proves", "confirmed", "[object", "undefined", "NaN") if any(w_ in t for t in txt.values())]
    ck.ok(not bad_w, f"details: the replication account uses none of the words 'the truth', 'proves', 'confirmed' and prints no JavaScript placeholder ({bad_w})")
    ck.ok(not errors_d, "details, 1280: no console errors, page errors or failed data requests" + ("" if not errors_d else f": {errors_d[:3]}"))
    dp.close()

    # ---- phone widths
    errors_p = []
    for width in (390, 320):
        pp = browser.new_page(viewport={"width": width, "height": 844}, device_scale_factor=2)
        watch(pp, errors_p)
        pp.goto(base, wait_until="networkidle")
        pp.wait_for_function("document.querySelectorAll('#rep-rows .row').length > 0", timeout=20000)
        pp.evaluate("document.getElementById('fig-rep').scrollIntoView()")
        pp.wait_for_timeout(250)
        small = pp.evaluate("""() => [...document.querySelectorAll('#rep-rows .row, #fig-rep a')].map(e => { const r = e.getBoundingClientRect(); return [e.className || e.tagName, Math.round(r.height), Math.round(r.right)]; })
                                .filter(x => x[1] < 32 || x[2] > innerWidth)""")
        ck.ok(no_hscroll(pp) and not small, f"{width}: Figure 8 does not scroll sideways, and its rows and links are at least 32 px tall and fit ({small[:3]})")
        pp.click('#rep-rows .row[data-slug="neoverse-n2"]')
        pp.wait_for_timeout(120)
        vis = pp.evaluate("(() => { const r = document.getElementById('rep-read').getBoundingClientRect(); return [r.width > 200, r.right <= innerWidth + 1, r.left >= -1]; })()")
        clip = pp.evaluate("[...document.querySelectorAll('#rep-rows .row')].filter(r => r.scrollWidth > r.clientWidth + 1).map(r => r.dataset.slug)")
        ck.ok(all(vis) and not clip, f"{width}: a tap on a row shows its readout inside the screen and no row's contents overflow it ({clip})")
        lines_t = pp.evaluate("(() => { const t = document.getElementById('rep-title'), cs = getComputedStyle(t); return Math.round(t.getBoundingClientRect().height / parseFloat(cs.lineHeight)); })()")
        ck.ok(lines_t <= 2, f"{width}: Figure 8's title takes at most two lines ({lines_t})")
        shot(pp, saved, shots, f"rep-fig-{width}.png", "#fig-rep")
        pp.close()
    # ---- larger text: the columns are in rem, so they grow with the text, and a container query picks the layout; nothing collides
    for width, fs in ((1440, 100), (390, 100), (1440, 150), (1440, 200), (390, 150), (390, 200), (320, 100), (320, 150), (320, 200)):
        tp = browser.new_page(viewport={"width": width, "height": 900})
        watch(tp, errors_p)
        tp.goto(base, wait_until="networkidle")
        tp.wait_for_function("document.querySelectorAll('#rep-rows .row').length > 0", timeout=20000)
        if fs != 100:
            tp.add_style_tag(content=f"html{{font-size:{fs}% !important}}")
        tp.wait_for_timeout(300)
        g = tp.evaluate(REP_GEOM_JS)
        w_rem = g["fig_w"] / g["rem"]
        level = 0 if w_rem > 20.5 else 1 if w_rem > 17.25 else 2
        rem = g["rem"]
        want_tracks = [2.625 * rem] * 3 + [4.125 * rem] if level == 0 else [2.25 * rem] * 3 + [2.5 * rem]
        tracks_ok = level == 2 or (len(g["row_tracks"]) == 5 and all(abs(a - b) < 1.0 for a, b in zip(g["row_tracks"][1:], want_tracks)) and g["head_tracks"] == g["row_tracks"])
        stacked_ok = level != 2 or (g["head_display"] == "none" and g["row_display"] == "flex" and g["labels"] == ['"first"', '"second"', '"both"', '"inside"'] * len(g["rows"]))
        ck.ok(g["rows"] and tracks_ok and stacked_ok and not g["bad"],
              f"Figure 8 at {width} wide and {fs}% text (layout {['full grid', 'compact grid', 'stacked cells'][level]}, figure {w_rem:.1f} rem wide): "
              + ("the count columns are " + ("2.625 and the inside column 4.125" if level == 0 else "2.25 and the inside column 2.5") + f" rem, so they grow with the text (tracks {[round(x) for x in g['row_tracks']]}); " if level < 2 else "the header is dropped and each cell carries its own label; ")
              + f"no header word, row, glyph, count or inside bar overflows or overlaps another ({g['bad'][:2]})")
        if (width, fs) in ((1440, 100), (390, 100)):
            ck.ok(level == 0 and [round(x) for x in g["row_tracks"][1:]] == [42, 42, 42, 66] and g["rows"][0]["h"] >= 32,
                  f"Figure 8 at {width} wide and normal text keeps its full grid with columns of 42, 42, 42 and 66 px ({g['row_tracks']})")
        tp.close()
    for width in (390, 320):
        dp = browser.new_page(viewport={"width": width, "height": 844}, device_scale_factor=2)
        watch(dp, errors_p)
        dp.goto(base + "details.html", wait_until="networkidle")
        dp.wait_for_function("document.querySelectorAll('#rep-table tbody tr').length > 0", timeout=20000)
        w_ = dp.evaluate("(() => { const w = document.getElementById('rep-table').closest('.tablewrap'); return [w.scrollWidth > w.clientWidth, getComputedStyle(w).overflowX]; })()")
        ck.ok(no_hscroll(dp) and w_[0] and w_[1] == "auto", f"{width} details: Table 14 scrolls inside its own box and the page does not scroll sideways ({w_})")
        st = dp.evaluate(STICKY_JS, "#rep-t-cap ~ .tablewrap")
        ck.ok(sticky_ok(st), f"{width} details: scrolled to its right end, Table 14 keeps the CPU model in view (left edge, heading too, at most half the box) and shows the swipe hint ({st})")
        dp.close()
    ck.ok(not errors_p, "the replication, 390 and 320: no console errors" + ("" if not errors_p else f": {errors_p[:3]}"))


def dsweep_checks(browser, base, ck, index, allowed, saved, shots):
    """The row-length sweep (data/dsweep.json): one sentence in section 6a (main page), the full account, Figure 9 and Table 15 in section 6d (details).
    Recomputed here from the data file, not from the page's code: the two models' words (the weak x86-64 control and Neoverse-N2's 'neither' with its two
    columns), each column's fixed share and interval, the rule's bands, the ns figures with the column they belong to, the instruction counts (the line
    in the remainder from a least-squares fit, the multiple-of-8 row with its ratio), Table 15's rows, Figure 9's panels, points, toggle, readout and keys."""
    print("== the row-length sweep: one sentence in 6a (main), the account, Figure 9 and Table 15 in 6d (details)")
    with open(os.path.join(DATA, "dsweep.json"), encoding="utf-8") as f:
        D = json.load(f)
    norm = lambda s: " ".join(s.replace(" ", " ").split())  # noqa: E731
    Rl = D["rule"]
    ms = [m for m in D["models"] if m.get("word") and m["word"] != "too few jobs"]
    A = next(m for m in ms if m["arch"] == "aarch64")
    Xm = next(m for m in ms if m["arch"] == "x86_64")
    rws = lambda m, role: [r for r in m["rows"] if role in r["roles"]]  # noqa: E731
    ns = lambda r, c: r[c]["excess_ns_per_inner"]  # noqa: E731
    plain = {"H1": "changes little", "H2": "grows with d", "falls": "falls", "neither": "fits none of the words"}
    ck.ok(index["sections"].get("dsweep") == "data/dsweep.json" and D["plan"] == "dsweep/PLAN.md" and len(D["plan_sha256"]) == 64 and len(ms) == 2
          and A["word"] == "neither" and not A["columns_agree"] and Xm["word"] == "H2" and Xm["columns_agree"]
          and A["columns"]["as_compiled"]["word"] == "falls" and A["columns"]["aligned"]["word"] == "H1",
          f"the sweep file is registered, names dsweep/PLAN.md with its sha256, has two models with a word ({Xm['cpu_short']}: {Xm['word']}, {A['cpu_short']}: {A['word']} with the columns {A['columns']['as_compiled']['word']} and {A['columns']['aligned']['word']})")
    # ---- main page: the 6a sentence
    errors = []
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    watch(pg, errors)
    pg.goto(base, wait_until="networkidle")
    pg.wait_for_function("document.querySelectorAll('#arm-rows .row').length === 8 && document.getElementById('arm-mm').textContent.includes('sweep')", timeout=20000)
    fa = rws(A, "fit")
    f1 = lambda v: f"{v:.1f}"  # noqa: E731
    want = (f"A row-length sweep, judged by the rule in its plan, gave “{A['word']}”: as compiled the extra time per inner call {plain[A['columns']['as_compiled']['word']]} ({f1(ns(fa[0], 'as_compiled'))} to {f1(ns(fa[-1], 'as_compiled'))} ns), "
            f"aligned it {plain[A['columns']['aligned']['word']]} ({f1(ns(fa[0], 'aligned'))} to {f1(ns(fa[-1], 'aligned'))} ns) over the fitted row lengths (section 6d).")
    mm = norm(pg.inner_text("#arm-mm"))
    ck.ok(want in mm and "Where the extra time goes is not shown." not in mm and mm.count("sweep") == 1 and "section 6d" in mm,
          f"6a: one sentence names the row-length sweep, says it was judged by the rule in its plan (no claim about when the rule was written), gives the word “{A['word']}” and both columns' behaviour with their ns ranges (each naming its column), replacing the stale 'not shown' ({want[:60]}…)")
    ck.ok(not page_numbers(pg, allowed, "#arm-mm"), "6a: the sweep sentence's numbers are in the data")
    ck.ok(not errors, "6a sweep sentence: no console errors" + ("" if not errors else f": {errors[:3]}"))
    pg.close()

    # ---- details page
    errors_d = []
    dp = browser.new_page(viewport={"width": 1280, "height": 900})
    watch(dp, errors_d)
    dp.goto(base + "details.html", wait_until="networkidle")
    dp.wait_for_function("document.querySelectorAll('#ds-t tbody tr').length > 0 && document.querySelectorAll('#ds-panels svg').length === 2", timeout=20000)
    dp.evaluate("document.querySelectorAll('details.fold').forEach(d => { d.open = true; })")
    dp.wait_for_timeout(200)
    ids = ("ds-q", "ds-ran", "ds-out", "ds-shape", "ds-instr", "ds-scope", "ds-t-cap", "ds-limits")
    txt = {i: norm(dp.inner_text("#" + i)) for i in ids}
    pos = dp.evaluate("""() => { const h = document.getElementById('dsweep-full'), s = h.closest('section'); const lim = document.getElementById('arm-limits');
        return [s.id, !!(lim.compareDocumentPosition(h) & Node.DOCUMENT_POSITION_FOLLOWING), [...document.querySelectorAll('#dsweep-full ~ *')].filter(n => !n.classList.contains('scroll-hint')).map(n => n.id || n.tagName).slice(0, 9)]; }""")
    ck.ok(pos[0] == "arm-full" and pos[1] and pos[2] == ["ds-q", "ds-ran", "ds-out", "fig-ds", "ds-shape", "ds-instr", "ds-scope", "ds-t-cap", "ds-t-wrap"],
          f"details: the sweep follows the Arm section's limits, inside section 6d, in the order question, what ran, outcome, Figure 9, the numbers, instructions, scope of the headline range, Table 15 ({pos})")
    q = txt["ds-q"]
    fitA = [rws(A, "fit")[0]["d"], rws(A, "fit")[-1]["d"]]
    want_q = (f"The question. On {A['cpu_short']}, matrix multiply keeps its NEON loop in both builds and the checked build still costs {A['published']['L1']:.3f}× at L1 (d = {A['ladder']['study_l1_d']}). "
              "The listing shows compares and selects before the NEON loop and a checked scalar loop for the leftover elements, which the matrix-multiply paragraph above reads as a set-up cost paid once per inner call (an inner call is one run of the innermost loop over d elements); that reading was inferred, and this sweep tests it. "
              f"Three accounts are written in the plan (dsweep/PLAN.md, sha256 {D['plan_sha256'][:8]}…). It was drafted before the sweep code, revised while the code was written and tested and once more after a review of the plan and the code, which changed the deciding statistic, "
              "and committed alone, before the code commit and before the first run, in the author’s unpublished development history, which this repository does not contain and so cannot show that order. "
              f"{prov_dsweep_py(index['provenance'])} The hash is stored in every dsweep.json of the runs and shows the plan was not edited after the runs. "
              "H1, a fixed extra cost per inner call, predicts the same extra time per inner call at every d. H2, a cost per element, predicts extra time in proportion to d. “Falls” is extra time that is smaller at the longer rows. "
              f"The rule reads the fixed share of the extra time at the study size, fitted over the L1-resident row lengths that leave the same remainder modulo {A['ladder']['modulus']} as the study size (d = {fitA[0]} to {fitA[1]} on {A['cpu_short']}): "
              f"H1 when the share and its 95% interval lie inside {Rl['h1_share_band'][0]} to {Rl['h1_share_band'][1]}, H2 inside −0.2 to 0.2, “falls” above {Rl['falls_share_above']}, anything else “neither”. "
              "It is applied twice, to the code as compiled and with every hot loop aligned to 64 bytes; when the two disagree the word is “neither” and both are stated.")
    ck.ok(q == want_q and "before any run" not in q and "written first" not in q,
          f"details, the question, word for word: the plan's account of its own history (drafted before the code, revised twice, committed alone before the first run in unpublished history, the public record a commit of the branch dsweep-smoke with the code and its time against the first record's start, hash shows no edit after the runs), the two accounts and 'falls', the rule's bands from the data, the fit ladder, both columns, and that disagreement gives 'neither' with both words stated ({first_diff(q, want_q)})")
    ck.ok(abs(Rl["h2_share_band"][0] + 0.2) < 1e-9 and abs(Rl["h2_share_band"][1] - 0.2) < 1e-9 and Rl["h1_share_band"] == [0.8, 1.2] and Rl["falls_share_above"] == 1.2 and Rl["minimum_jobs"] == 3,
          "the rule's bands in the data are the ones the plan wrote (H1 0.8 to 1.2, H2 -0.2 to 0.2, falls above 1.2, 3 jobs)")
    ran = txt["ds-ran"]
    commits = sorted({r["commit"] for r in D["runs"]})
    name_of = lambda cm: next((m["cpu_short"] for m in D["models"] + D["too_few_jobs"] if m["cpu_model"] == cm), cm)  # noqa: E731
    run_txt = "; ".join(f"run {r['run_id']}, {jobs_py(r['jobs'])} ({join_and_py([f'{name_of(k)} {n}' for k, n in r['models'].items()])})" for r in D["runs"])
    want_ran = (f"What ran. {cap_py(num_word_py(len(D['runs'])))} runs of the sweep workflow, from {'one commit' if len(commits) == 1 else str(len(commits)) + ' commits'} ({', '.join(c[:7] for c in commits)}) of the temporary branch dsweep-smoke, "
                "where the sweep workflow file is named ci.yml because a dispatchable workflow must already exist on the default branch (the branch is kept because the run records name the commit): "
                f"{run_txt}. A CPU model needs {Rl['minimum_jobs']} jobs to get a word, so " + join_and_py([f"{m['cpu_short']} ({jobs_py(m['jobs'])})" for m in D["too_few_jobs"]]) + (" gets none" if len(D["too_few_jobs"]) == 1 else " get none")
                + f". The timing, the pooling and the intervals are the main study’s. The identical-binary A/A has a half-width of {pct_s_py(Xm['aa']['half_width_pct'])} on {Xm['cpu_short']} and {pct_s_py(A['aa']['half_width_pct'])} on {A['cpu_short']}, against the {Rl['aa_half_width_max_pct']:g}% the rule allows.")
    ck.ok(ran == want_ran and sum(r["jobs"] for r in D["runs"]) == D["jobs"] and "dispatched" not in ran,
          f"details, what ran, word for word: the runs, jobs and commit from the data, the temporary branch and why its workflow file is named ci.yml, the CPU models too small for a word, and both A/A half-widths against the rule's limit ({first_diff(ran, want_ran)})")
    cw = lambda m, c: f"“{m['columns'][c]['word']}” (fixed share {m['columns'][c]['share']:.3f}, 95% interval {m['columns'][c]['share_ci95'][0]:.3f} to {m['columns'][c]['share_ci95'][1]:.3f})"  # noqa: E731
    out = txt["ds-out"]
    both_gt1 = A["columns"]["as_compiled"]["share"] > 1 and A["columns"]["aligned"]["share"] > 1
    want_out = (f"Outcome, as the written rule fixed it. {Xm['cpu_short']}: {Xm['word']} in both columns: as compiled {cw(Xm, 'as_compiled')}, aligned {cw(Xm, 'aligned')}. "
                "The extra time per inner call grows with d there. That is the plan’s weak control, because the loop loses SIMD under the check on x86-64 and neither account was written for it; it gave the word the plan expected, and nothing more is claimed. "
                f"{A['cpu_short']}: {A['word']}, because the two columns disagree: as compiled {cw(A, 'as_compiled')}, aligned {cw(A, 'aligned')}." + (" Both shares are above 1, so this is not a mixture." if both_gt1 else "")
                + " A word that does not survive moving the loops is not claimed.")
    ck.ok(out == want_out and Xm["word"] == "H2" and Xm["columns_agree"] and not A["columns_agree"],
          f"details, the outcome, word for word: {Xm['cpu_short']} {Xm['word']} (the weak control, nothing more claimed) and {A['cpu_short']} {A['word']} because the columns disagree, with each column's word, fixed share and interval from the data ({first_diff(out, want_out)})")
    near = lambda v: f"{v:.2f}"  # noqa: E731

    def arm_series(c):
        rest = [ns(r, c) for r in fa[2:]]
        br, l2 = rws(A, "bridge"), rws(A, "study_l2")[0]
        return (f"{' and '.join(f'{near(ns(r, c))} ns at d = {r['d']}' for r in fa[:2])}, then between {near(min(rest))} and {near(max(rest))} ns from d = {fa[2]['d']} to d = {fa[-1]['d']}; "
                f"beyond the L1-resident rule (context, fitted nowhere) {', '.join(f'{near(ns(r, c))} ns at d = {r['d']}' for r in br)} and {near(ns(l2, c))} ns at the study L2 size, d = {l2['d']}")
    sh = txt["ds-shape"]
    rest_ac = [ns(r, "as_compiled") for r in fa[2:]]
    flat = A["columns"]["as_compiled"]["word"] == "falls" and all(ns(r, "as_compiled") > max(rest_ac) for r in fa[:2]) and (max(rest_ac) - min(rest_ac)) / min(rest_ac) < 0.05
    l2a = rws(A, "study_l2")[0]
    fx_rows = rws(Xm, "fit")
    l2x = rws(Xm, "study_l2")[0]
    want_sh = [f"Extra time per inner call (checked minus unchecked) on {A['cpu_short']}, as compiled: {arm_series('as_compiled')}. Aligned: {arm_series('aligned')}.",
               f"d = {l2a['d']} leaves a remainder of {l2a['d_mod_8']} where the ladder leaves {A['ladder']['residue']}, so the change from d = {rws(A, 'bridge')[-1]['d']} to d = {l2a['d']} mixes the L2 size with the remainder.",
               f"On {Xm['cpu_short']} the extra time grows with d: as compiled {near(ns(fx_rows[0], 'as_compiled'))} ns at d = {fx_rows[0]['d']} and {near(ns(fx_rows[-1], 'as_compiled'))} ns at d = {fx_rows[-1]['d']} (aligned {near(ns(fx_rows[0], 'aligned'))} and {near(ns(fx_rows[-1], 'aligned'))}), and {near(ns(l2x, 'as_compiled'))} ns at the study L2 size, d = {l2x['d']}; the ratio rises from {fx_rows[0]['as_compiled']['ratio']:.2f} to {fx_rows[-1]['as_compiled']['ratio']:.2f}.",
               f"did not match the observed ratio at the smallest d on {A['cpu_short']} ({fa[0]['as_compiled']['ratio']:.2f} as compiled): the written rule decides, and the table’s size did not hold."]
    if flat:
        want_sh.append(f"The word “falls” as compiled rests on the first two row lengths; from d = {fa[2]['d']} the values are flat, which is a fact about the points and not a second verdict.")
    want_shape = ("What the numbers show, without the word. " + want_sh[0] + " " + (want_sh[4] + " " if flat else "") + want_sh[1] + " " + want_sh[2] + " The plan’s illustrative table of ratios under H1 and H2 " + want_sh[3])
    ck.ok(sh == want_shape and ns(fx_rows[-1], "as_compiled") > ns(fx_rows[0], "as_compiled") and flat,
          f"details, what the numbers show, word for word: every ns figure names its column; {A['cpu_short']}'s values at the first two row lengths, the flat run after, the bridge and the study L2 size (context, fitted nowhere); the 'falls' word resting on d = {fa[0]['d']} and {fa[1]['d']} stated as a fact about the points; {Xm['cpu_short']}'s growth; the plan's illustrative table not holding ({first_diff(sh, want_shape)})")
    # the instruction line in the remainder: a least-squares fit in pure Python
    pts = [(r["d_mod_8"], r["extra_instr_per_inner"]) for r in A["rows"] if ("scan" in r["roles"] or "study_l1" in r["roles"]) and r["d_mod_8"] != 0]
    n_ = len(pts)
    sx, sy = sum(p[0] for p in pts), sum(p[1] for p in pts)
    sxx, sxy = sum(p[0] * p[0] for p in pts), sum(p[0] * p[1] for p in pts)
    slope = (n_ * sxy - sx * sy) / (n_ * sxx - sx * sx)
    icpt = (sy - slope * sx) / n_
    fits_line = n_ >= 4 and all(abs(icpt + slope * r - e) < 0.6 for r, e in pts)
    ei = [round(r["extra_instr_per_inner"]) for r in fa]
    r0 = next((r for r in A["rows"] if r["d_mod_8"] == 0 and "scan" in r["roles"]), None)
    ins = txt["ds-instr"]
    want_ins = ("Instruction counts (secondary: instructions, not time). Cachegrind counts the extra instructions the checked build runs per inner call: "
                + (f"{ei[0]} at every row length of the fit ladder" if len(set(ei)) == 1 else f"{min(ei)} to {max(ei)} over the fit ladder") + f" on {A['cpu_short']}"
                + (f"; over the remainder scan and the study size it is {round(icpt)} + {round(slope)} × r, where r is d modulo {A['ladder']['modulus']} (r = 1 to {A['ladder']['modulus'] - 1})" if fits_line else "")
                + (f", and at a multiple of {A['ladder']['modulus']} (d = {r0['d']}) it is {round(r0['extra_instr_per_inner'])}, with a time ratio of {r0['as_compiled']['ratio']:.2f}×" if r0 else "")
                + f". On {Xm['cpu_short']} they grow with d, by about {Xm['instructions']['fit']['slope']:.1f} for each added element over the ladder. The counts are exact for the listing and say nothing about time by themselves.")
    ck.ok(ins == want_ins and fits_line and r0 is not None and len(set(ei)) == 1,
          f"details, instruction counts, word for word: {ei[0]} extra instructions per inner call at every fitted d, the straight line {round(icpt)} + {round(slope)} × r in the remainder (recomputed by least squares), the multiple-of-8 row (d = {r0['d'] if r0 else '?'}) with its time ratio, {Xm['cpu_short']}'s slope, labelled 'instructions, not time' ({first_diff(ins, want_ins)})")
    # the scope of the headline range (finding: the range is for the study's sizes; this sweep shows the cost depends on the row length)
    lost = index["page"]["lost"]
    x_rows = Xm["rows"]
    x12, xl1 = fx_rows[0], rws(Xm, "study_l1")[0]
    x_past = next((r for r in rws(Xm, "bridge") if r["working_set_bytes"] > Xm["l1d_kib"] * 1024), None)
    want_scope = (f"Scope of the headline range. The range in section 1, {lost['min']:.1f}× to {lost['max']:.1f}×, is for the study’s sizes. This sweep shows that for matrix multiply on {Xm['cpu_short']} the cost depends on the row length: "
                  f"as compiled {fx_py(x12['as_compiled']['ratio'])}× at d = {x12['d']}, {fx_py(xl1['as_compiled']['ratio'])}× at the study’s d = {xl1['d']}"
                  + (f" and {fx_py(x_past['as_compiled']['ratio'])}× at d = {x_past['d']} ({x_past['working_set_bytes']:,} bytes, past the {Xm['l1d_kib']} KiB L1 data cache)" if x_past else "")
                  + f", so {lost['min']:.1f}× is not a floor for row lengths the study did not time.")
    scope = txt["ds-scope"]
    ck.ok(scope == want_scope and x_past is not None and x12["as_compiled"]["ratio"] < lost["min"] < x_past["as_compiled"]["ratio"] and len(x_rows) > 3,
          f"details, scope of the headline range, word for word: the range printed in section 1 is for the study's sizes, and {Xm['cpu_short']}'s matrix-multiply ratios at the smallest row length, the study's and one past L1 come from the data and straddle it ({first_diff(scope, want_scope)})")
    sweep_hits = [i for i in ("ds-q", "ds-ran", "ds-out", "ds-shape", "ds-instr", "ds-limits") if "the study’s sizes" in txt[i]]
    ck.ok(not sweep_hits and scope.count("the study’s sizes") == 1, f"the sweep's account says 'the study’s sizes' once, in the scope paragraph, and nowhere else ({sweep_hits})")
    lim = txt["ds-limits"]
    max_hw = max(((r[c]["ci95"][1] - r[c]["ci95"][0]) / 2 / r[c]["ratio"]) * 100 for r in A["rows"] for c in ("as_compiled", "aligned"))
    want_lim = (f"Limits. The {A['cpu_short']} result is {num_word_py(A['runs'])} run of {num_word_py(A['jobs'])} jobs on one core type, so its intervals (at most ±{pct_s_py(max_hw)}) cannot show run-to-run or host-to-host spread. "
                "The aligned column uses a loop-alignment flag, and the placement controls are not verified on this core (the Limits paragraph of this section), so it is not a pure placement control; this is why both columns are reported. "
                "The sweep reads no hardware counters, so it cannot say where the cycles go. One kernel, one compiler (clang 18, FAST mode) and one flag set; nothing here is said about other cores. "
                + join_and_py([m["cpu_short"] for m in D["too_few_jobs"]]) + " drew too few jobs for a word. No further runs will be made for this question.")
    ck.ok(lim == want_lim and A["runs"] == 1,
          f"details, the sweep's limits, word for word: one run of six near-identical jobs on one core type (its intervals cannot show run-to-run spread), the aligned column not a pure placement control (so both are reported), no hardware counters, one kernel and compiler, the models that drew too few jobs, no further runs ({first_diff(lim, want_lim)})")
    # Table 15
    tab = dp.evaluate("[...document.querySelectorAll('#ds-t tbody tr')].map(tr => [...tr.children].map(c => c.textContent.replace(/\\s+/g, ' ').trim()))")
    heads = dp.evaluate("[...document.querySelectorAll('#ds-t thead th')].map(c => c.textContent.trim())")
    role_w = {"fit": "fit", "scan": "remainder scan", "bridge": "bridge", "study_l1": "study L1 size", "study_l2": "study L2 size"}
    iv = lambda c: f"{lr_py(c['ratio'])}× ({lr_py(c['ci95'][0])} to {lr_py(c['ci95'][1])})"  # noqa: E731
    want_t = [[f"{m['cpu_short']}, d = {r['d']}", ", ".join(role_w[q_] for q_ in r["roles"]), iv(r["as_compiled"]), near(ns(r, "as_compiled")), iv(r["aligned"]), near(ns(r, "aligned")), str(round(r["extra_instr_per_inner"])),
               f"{r['placement_d']:.3f}{' ‡' if r['placement_sensitive'] else ''}"] for m in ms for r in m["rows"]]
    heads_want = ["Model and row length", "Role", "As compiled: ratio (95% interval)", "As compiled: extra ns per inner call", "Aligned: ratio (95% interval)", "Aligned: extra ns per inner call", "Extra instructions per inner call", "Compiled ÷ aligned"]
    ck.ok(tab == want_t and heads == heads_want,
          f"Table 15: all {len(heads_want)} column heads word for word (a swapped pair of columns would relabel correct numbers), and {len(want_t)} rows (every row length of both models) with both columns' ratio, interval and extra ns, the extra instructions and compiled ÷ aligned with ‡ where placement-sensitive, equal to the data ({[(a, b) for a, b in zip(tab, want_t) if a != b][:1]})")
    cp = txt["ds-t-cap"]
    want_cp = ("Table 15. Every row length timed: the pooled ratio of checked ÷ unchecked with its 95% interval and the extra time per inner call, as compiled and aligned; Cachegrind’s extra instructions per inner call (counted, not timed); "
               "compiled ÷ aligned, with ‡ where the written placement test calls the length placement-sensitive (fitted nowhere, as on the main study; the placement fields were defined for x86-64 fetch windows). "
               f"{D['jobs']} jobs; {A['cpu_short']} is one run of {A['jobs']} jobs.")
    ck.ok(cp == want_cp, f"Table 15's caption, word for word: both columns, the instruction counts labelled counted not timed, the ‡ meaning, the job totals ({first_diff(cp, want_cp)})")
    aria15 = dp.evaluate("document.getElementById('ds-t-wrap').getAttribute('aria-label')")
    h3_ds = dp.evaluate("document.getElementById('dsweep-full').textContent.trim()")
    ck.ok(aria15 == "Table 15, every row length timed in the row-length sweep; scrolls sideways on a narrow screen, the model and row length stay in view" and h3_ds == "Matrix multiply: a row-length sweep",
          f"Table 15's region label and the sweep's heading, word for word ({aria15!r}, {h3_ds!r})")
    # Figure 9
    fig = dp.evaluate("""() => { const f = document.getElementById('fig-ds'); return { seg: [...f.querySelectorAll('#ds-met-seg button')].map(b => [b.dataset.met, b.getAttribute('aria-checked')]), role: f.querySelector('#ds-met-seg').getAttribute('role'),
        panels: [...f.querySelectorAll('#ds-panels svg')].map(s => ({ slug: s.dataset.slug, circles: s.querySelectorAll('circle').length, fitted: s.querySelectorAll('circle.fitted').length, lines: s.querySelectorAll('polyline').length, tab: s.getAttribute('tabindex'), label: s.getAttribute('aria-label') })),
        titles: [...f.querySelectorAll('.ds-ptitle')].map(t => t.textContent.replace(/\\s+/g, ' ').trim()), title: document.getElementById('ds-title').textContent }; }""")
    n_fit = {m["slug"]: len([r for r in m["rows"] if "fit" in r["roles"] or "study_l1" in r["roles"]]) for m in ms}
    ck.ok(fig["seg"] == [["ns", "true"], ["instr", "false"]] and fig["role"] == "radiogroup" and [p["slug"] for p in fig["panels"]] == [m["slug"] for m in ms]
          and all(p["circles"] == 2 * len(m["rows"]) and p["fitted"] == 2 * n_fit[m["slug"]] and p["lines"] == 2 and p["tab"] == "0" and "arrow keys" in p["label"] for p, m in zip(fig["panels"], ms))
          and fig["titles"] == [f"{m['cpu_short']} {m['word']}{'' if m['columns_agree'] else ' (columns disagree)'}, {jobs_py(m['jobs'])}" for m in ms] and "extra time per inner call against the row length d" in fig["title"],
          f"Figure 9: a time/instructions switch, one panel per model with a word, a point per row length and column (filled as compiled, hollow aligned), the fitted ladder marked, a joined line per column, focusable, titled with each model's word and job count ({[(p['circles'], p['fitted']) for p in fig['panels']]})")
    # a click on a point selects its row length; the readout follows
    arm_d = [r["d"] for r in A["rows"]]
    target = rws(A, "bridge")[1]
    dp.click(f'#ds-panels svg[data-slug="{A["slug"]}"] circle[data-d="{target["d"]}"]', force=True)
    dp.wait_for_timeout(80)
    rd = norm(dp.inner_text("#ds-read"))
    col = lambda r, c, nm: f"{nm} {lr_py(r[c]['ratio'])}× ({lr_py(r[c]['ci95'][0])} to {lr_py(r[c]['ci95'][1])}), {near(ns(r, c))} ns extra per inner call"  # noqa: E731
    want_rd = (f"{A['cpu_short']}, d = {target['d']} ({', '.join(role_w[q_] for q_ in target['roles'])}, remainder {target['d_mod_8']}): {col(target, 'as_compiled', 'as compiled')}; {col(target, 'aligned', 'aligned')}. "
               f"{round(target['extra_instr_per_inner'])} extra instructions per inner call (counted, not timed). Compiled ÷ aligned {target['placement_d']:.3f}{', placement-sensitive' if target['placement_sensitive'] else ''}.")
    sel = dp.evaluate("[...document.querySelectorAll('#ds-panels circle.sel')].map(c => [c.dataset.d, c.closest('svg').dataset.slug])")
    ck.ok(rd == want_rd and sel and all(s == [str(target["d"]), A["slug"]] for s in sel), f"Figure 9: a click on the point at d = {target['d']} reads its row: both columns' ratio, interval and extra ns, the extra instructions (counted, not timed), compiled ÷ aligned ({rd[:70]}…)")
    dp.evaluate(f"document.querySelector('#ds-panels svg[data-slug=\"{A['slug']}\"]').focus()")
    dp.keyboard.press("End")
    e1 = dp.evaluate("document.querySelector('#ds-panels svg[data-slug=\"" + A["slug"] + "\"] circle.sel').dataset.d")
    dp.keyboard.press("Home")
    e2 = dp.evaluate("document.querySelector('#ds-panels svg[data-slug=\"" + A["slug"] + "\"] circle.sel').dataset.d")
    dp.keyboard.press("ArrowRight")
    e3 = dp.evaluate("document.querySelector('#ds-panels svg[data-slug=\"" + A["slug"] + "\"] circle.sel').dataset.d")
    ds_sorted = sorted(arm_d)
    ck.ok([e1, e2, e3] == [str(ds_sorted[-1]), str(ds_sorted[0]), str(ds_sorted[1])], f"Figure 9: End, Home and the right arrow move the selection along the row lengths ({[e1, e2, e3]})")
    sel_d = lambda: dp.evaluate("document.querySelector('#ds-panels svg[data-slug=\"" + A["slug"] + "\"] circle.sel').dataset.d")  # noqa: E731
    dp.click("#ds-next")
    n1 = sel_d()
    dp.evaluate("document.getElementById('ds-prev').click()")  # a click by script, so a button that is wrongly disabled fails the check rather than waiting
    dp.evaluate("document.getElementById('ds-prev').click()")
    n2, prev_off = sel_d(), dp.evaluate("document.getElementById('ds-prev').disabled")
    dp.evaluate(f"document.querySelector('#ds-panels svg[data-slug=\"{A['slug']}\"]').focus()")
    dp.keyboard.press("End")
    n3, next_off = sel_d(), dp.evaluate("document.getElementById('ds-next').disabled")
    rd3 = norm(dp.inner_text("#ds-read"))
    step_g = dp.get_attribute(".ds-step", "aria-label")
    ck.ok([n1, n2, n3] == [str(ds_sorted[2]), str(ds_sorted[0]), str(ds_sorted[-1])] and prev_off and next_off and rd3.startswith(f"{A['cpu_short']}, d = {ds_sorted[-1]} (") and step_g == "Step through the row lengths of the chosen panel"
          and dp.inner_text("#ds-prev").strip() == "← Shorter row" and dp.inner_text("#ds-next").strip() == "Longer row →",
          f"Figure 9: the step buttons move the selection one row length at a time from the chosen one and the readout follows; each is disabled at its end ({[n1, n2, n3]}, {prev_off}, {next_off})")
    dp.click("#ds-met-seg button[data-met=instr]")
    dp.wait_for_timeout(120)
    fig2 = dp.evaluate("""() => ({ seg: [...document.querySelectorAll('#ds-met-seg button')].map(b => b.getAttribute('aria-checked')), circles: [...document.querySelectorAll('#ds-panels svg')].map(s => s.querySelectorAll('circle').length),
        lines: [...document.querySelectorAll('#ds-panels svg')].map(s => s.querySelectorAll('polyline').length), cap: document.getElementById('ds-cap').textContent.replace(/\\s+/g, ' '), title: document.getElementById('ds-title').textContent,
        ticks: [...document.querySelectorAll('#ds-panels svg')].map(s => Math.max(...[...s.querySelectorAll('.ds-tick')].map(t => Number(t.textContent)).filter(x => !isNaN(x)))) })""")
    ymax = max(r["extra_instr_per_inner"] for r in Xm["rows"])
    ck.ok(fig2["seg"] == ["false", "true"] and fig2["circles"] == [len(m["rows"]) for m in ms] and fig2["lines"] == [1, 1] and "The instructions the checks add to one inner call (Cachegrind: counted, not timed)" in fig2["cap"]
          and "extra instructions per inner call against the row length d" in fig2["title"] and fig2["ticks"][0] >= ymax * 0.7,
          f"Figure 9: the instructions view shows one point per row length, one line, a caption that says counted, not timed, and a title that says instructions ({fig2['circles']}, {fig2['lines']})")
    g9i = fig9_geometry(dp.evaluate(FIG9_JS), ms, "instr", ns)
    ck.ok(not g9i, f"Figure 9, instructions view: each point at its stored extra-instruction count, the axes, the band and the joined line read back from the SVG ({g9i[:2]})")
    dp.click("#ds-met-seg button[data-met=ns]")
    dp.wait_for_timeout(120)
    g9 = fig9_geometry(dp.evaluate(FIG9_JS), ms, "ns", ns)
    ck.ok(not g9, f"Figure 9, time view, 1280 wide: both y axes run from 0 at the bottom with the labels on their lines; every point of both columns sits at its stored extra ns (aligned apart from as compiled); the band runs from the first to the last fit row length; each joined line goes through the fit ladder; "
                  f"the fitted points are the ladder; the filled and hollow points match the caption's swatches ({g9[:2]})")
    cp9 = norm(dp.inner_text("#ds-cap"))
    ck.ok(cp9.startswith("Figure 9.") and "as compiled (" in cp9 and "filled) and aligned (" in cp9 and "hollow)" in cp9
          and dp.evaluate("document.querySelectorAll('#ds-cap .ds-key').length") == 2
          and "[object" not in cp9 and "The shaded band is the ladder the rule fits (" in cp9 and f"d = {fitA[0]} to {fitA[1]} on {A['cpu_short']}" in cp9 and "fitted nowhere" in cp9 and "Table 15" in cp9
          and dp.evaluate("[...document.querySelectorAll('#ds-cap a')].map(a => a.getAttribute('href'))") == ["#ds-t-cap"],
          "Figure 9's caption names both columns' marks, the shaded fit ladder with its d range per model, 'fitted nowhere' for the rest, and links to Table 15")
    # numbers, typed numbers, run links, wording
    bad_n = []
    for i in ids:
        bad_n += unknown_numbers(dp.evaluate(f"(() => ({PAGE_TEXT_JS})(document.getElementById('{i}')))()"), allowed)
    for i in ("fig-ds", "ds-t"):
        bad_n += unknown_numbers(dp.evaluate(f"(() => ({PAGE_TEXT_JS})(document.getElementById('{i}')))()"), allowed)
    ck.ok(not bad_n, "details: every number in the sweep's account, Figure 9, its readout and Table 15 is in the data" + ("" if not bad_n else f": {bad_n[:4]}"))
    with open(os.path.join(SITE, "details.html"), encoding="utf-8") as f:
        dsrc = f.read()
    blk = dsrc.split('<h3 id="dsweep-full">')[1].split("</section>")[0]
    plain_blk = re.sub(r"Figure 9|Table 15|x86-64|&[a-z]+;", " ", re.sub(r"<[^>]+>", " ", blk))
    typed = re.findall(r"\d+(?:\.\d+)?", plain_blk)
    ck.ok(not typed, f"the sweep's HTML types no number: every figure is filled from site/data ({typed[:4]})")
    runs_in_links = dp.evaluate("[...document.querySelectorAll('#dsweep-full ~ * a, #ds-ran a')].map(a => a.href).filter(h => /actions|runs/.test(h))")
    ck.ok(not runs_in_links and all(r["run_id"] in txt["ds-ran"] for r in D["runs"]) and "/actions/runs" not in blk, f"the sweep names its run ids as plain text and links to no workflow run ({runs_in_links[:2]})")
    bad_w = [w_ for w_ in ("the truth", "proves", "confirmed", "[object", "undefined", "NaN") if any(w_ in t for t in txt.values())]
    ck.ok(not bad_w, f"details: the sweep's account uses none of the words 'the truth', 'proves', 'confirmed' and prints no JavaScript placeholder ({bad_w})")
    ck.ok(not errors_d, "details sweep, 1280: no console errors, page errors or failed data requests" + ("" if not errors_d else f": {errors_d[:3]}"))
    dp.close()
    # ---- phone widths
    errors_p = []
    for width in (390, 320):
        pp = browser.new_page(viewport={"width": width, "height": 844}, device_scale_factor=2)
        watch(pp, errors_p)
        pp.goto(base + "details.html", wait_until="networkidle")
        pp.wait_for_function("document.querySelectorAll('#ds-panels svg').length === 2", timeout=20000)
        pp.evaluate("document.getElementById('fig-ds').scrollIntoView()")
        pp.wait_for_timeout(250)
        m_ = pp.evaluate("""() => { const f = document.getElementById('fig-ds').getBoundingClientRect(); return { fig: [Math.round(f.left), Math.round(f.right)], svgs: [...document.querySelectorAll('#ds-panels svg')].map(s => { const r = s.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top)]; }),
            btn: [...document.querySelectorAll('#ds-met-seg button')].map(b => Math.round(b.getBoundingClientRect().height)),
            step: [...document.querySelectorAll('.ds-step button')].map(b => { const r = b.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), Math.round(r.left), Math.round(r.right)]; }), w: document.getElementById('ds-t').closest('.tablewrap').scrollWidth > document.getElementById('ds-t').closest('.tablewrap').clientWidth }; }""")
        stacked = m_["svgs"][1][2] > m_["svgs"][0][2]
        ck.ok(no_hscroll(pp) and all(s[0] >= -1 and s[1] <= width + 1 for s in m_["svgs"]) and stacked and all(b >= 32 for b in m_["btn"]) and m_["w"],
              f"{width}: Figure 9's two panels stack and stay inside the screen, its switch is at least 32 px tall, Table 15 scrolls in its own box, and the page does not scroll sideways ({m_})")
        g9p = fig9_geometry(pp.evaluate(FIG9_JS), ms, "ns", ns)
        ck.ok(not g9p, f"{width}: Figure 9 read back from the SVG agrees with the stored values at this width too ({g9p[:2]})")
        st15 = pp.evaluate(STICKY_JS, "#ds-t-wrap")
        ck.ok(sticky_ok(st15), f"{width}: scrolled to its right end, Table 15 keeps the model and row length in view (left edge, heading too, at most half the box) and shows the swipe hint ({st15})")
        ck.ok(len(m_["step"]) == 2 and all(w_ >= 44 and h_ >= 44 and l_ >= 0 and r_ <= width for w_, h_, l_, r_ in m_["step"]),
              f"{width}: Figure 9's two step buttons (shorter row, longer row) are at least 44 px wide and tall and inside the screen, so a touch reader can pick a row length ({m_['step']})")
        shot(pp, saved, shots, f"ds-fig-{width}.png", "#fig-ds")
        pp.close()
    pw = browser.new_page(viewport={"width": 1440, "height": 900})
    watch(pw, errors_p)
    pw.goto(base + "details.html", wait_until="networkidle")
    pw.wait_for_function("document.querySelectorAll('#ds-panels svg').length === 2", timeout=20000)
    bad_sc = []
    for width, height in ((1440, 900), (1280, 800), (1100, 800), (1024, 768), (800, 600), (761, 800), (390, 844), (320, 568), (1024, 768)):
        pw.set_viewport_size({"width": width, "height": height})
        pw.wait_for_timeout(500)  # the redraw follows a change of the box's width after 120 ms
        sc = pw.evaluate("""() => [...document.querySelectorAll('#ds-panels svg')].map(s => { const q = s.getBoundingClientRect(), t = s.querySelector('.ds-tick'); return [Number(s.getAttribute('width')), q.width / Number(s.getAttribute('width')), Math.round(s.closest('.ds-panel').getBoundingClientRect().top), Math.round(q.left), parseFloat(getComputedStyle(t).fontSize) * q.width / Number(s.getAttribute('width'))]; })""")
        two = width > 760
        if not (len(sc) == 2 and all(0.98 <= x[1] <= 1.02 and x[4] >= 11.5 for x in sc) and ((sc[0][2] == sc[1][2] and sc[1][3] > sc[0][3]) if two else sc[1][2] > sc[0][2])):
            bad_sc.append((width, height, [(x[0], round(x[1], 3), round(x[4], 1)) for x in sc]))
    ck.ok(not bad_sc, f"Figure 9 is drawn at scale 1 (its tick labels at their full size, at least 11.5 px) at 1440, 1280, 1100, 1024x768, 800, 761, 390 and 320 wide, including after the window is resized, two panels side by side above 760 px and stacked below ({bad_sc[:2]})")
    pw.close()
    ck.ok(not errors_p, "the sweep, 390 and 320: no console errors" + ("" if not errors_p else f": {errors_p[:3]}"))


PROV_GROUPS = {  # the groups of result records the page's provenance account counts (site/data/index.json provenance), by glob
    "early": ["results/s1-run-*/results.json", "results/s2-run-*/results.json", "results/s3-run-*/results-*/results.json",
              "results/s3-audit-run-*/results-*/results.json", "results/s4-run-*/results-*/results.json", "results/s4-smoke-*/results-*/results.json"],
    "holdout": ["results/s5-holdout/runs/*/results-*/results.json"],
    "rewrite": ["results/mitigate-run-*/mitigate-*/results.json"],
    "s6": ["results/s6-run-*/results-*/results.json"],
    "s7": ["results/s7-run-*/results-*/results.json"],
    "arm": ["results/s8-arm-run-*/results-*/results.json"],
    "s9": ["results/s9-run-*/results-*/results.json", "results/s9-arm-run-*/results-*/results.json"],
    "dsweep": ["results/s10-dsweep-run-*/dsweep-*/dsweep.json"],
}


def _parse_utc(s):
    import datetime
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)


ORDER_CLAIMS_JS = """(raw) => {
  // The claim class: something committed, written, fixed, registered, listed, set or planned before something else (or beforehand), in advance,
  // or pre-registered. The file name PREREGISTRATION.md is a name and not a claim. It is read in every element, not in a list of block tags:
  // the deepest element whose text matches is taken, and its sentence block (a paragraph, list item, table cell, caption, term or chip) is the
  // unit that must carry the qualifier. `raw` is the served HTML text (read as a document, no script run): the text a reader gets without script.
  const BLOCK = 'p, li, dd, dt, td, th, caption, figcaption, summary, blockquote, h2, h3, h4, .tcap, .w-chip';
  const re = /\\b(?:committed|written|fixed|registered|listed|set|planned)\\b[^.]{0,40}\\bbefore(?:hand)?\\b|\\bin advance\\b|pre-?regist(?!ration\\.md)/i;
  const root = raw ? new DOMParser().parseFromString(raw, 'text/html') : document;
  const says = (n) => re.test(n.textContent);
  const deepest = [...root.body.querySelectorAll('*')].filter((n) => !/^(SCRIPT|STYLE)$/.test(n.tagName) && says(n) && ![...n.children].some(says));
  return [...new Set(deepest.map((n) => n.closest(BLOCK) || n))].map((b) => ({
    id: b.id || '', chip: b.classList.contains('w-chip'),
    text: b.textContent.replace(/\\s+/g, ' ').trim(),
    qualified: /unpublished development history/.test(b.textContent) || !!b.querySelector('a[href$="#prov-full"]')}));
}"""


def provenance_checks(browser, base, ck, index):
    """What the page says about the order of events and about where the result records came from: every statement is
    tied to the records (recounted here from results/, not read from index.json), to the times in the two recorded
    fixtures, and to the words the page prints (word for word); the old flat wording is gone from both pages."""
    print("== provenance: what the public record shows, and what it cannot")
    P = index["provenance"]
    crit = os.path.join(REPO, index["criteria"]["file"])
    with open(crit, "rb") as f:
        crit_sha = hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    recs, firsts = {}, {}
    for gid, pats in PROV_GROUPS.items():
        files = sorted(x for p in pats for x in glob.glob(os.path.join(REPO, p)))
        docs = []
        for x in files:
            with open(x, encoding="utf-8") as fh:
                d = json.load(fh)
            r = dict(d["run"] if isinstance(d.get("run"), dict) else d)
            r.setdefault("criteria_sha256", d.get("criteria_sha256"))  # the d-sweep records keep it beside `run`, the others inside it
            docs.append(r)
        recs[gid] = (files, docs)
        firsts[gid] = min((r["started_at"] for r in docs if r.get("started_at")), default=None)
    groups = {g["id"]: g for g in P["groups"]}
    ck.ok(list(groups) == list(PROV_GROUPS) and all(groups[g]["records"] == len(recs[g][0]) > 0 for g in PROV_GROUPS),
          "provenance: the groups of records and their counts are the ones in results/ ("
          + ", ".join(f"{g} {len(recs[g][0])}" for g in PROV_GROUPS) + ")")
    pub_first = P["first_public_run_id"]
    ids = lambda g: [int(re.search(r"/runs/(\d+)$", r.get("workflow_run_url") or r.get("url") or "").group(1)) for r in recs[g][1] if (r.get("workflow_run_url") or r.get("url"))]  # noqa: E731
    open_groups = [g for g in PROV_GROUPS if ids(g) and all(i >= pub_first for i in ids(g))]
    shut_groups = [g for g in PROV_GROUPS if ids(g) and all(i < pub_first for i in ids(g))]
    ck.ok(open_groups == ["s6", "s7", "arm", "s9", "dsweep"] and shut_groups == ["early", "holdout", "rewrite"]
          and all(groups[g]["links"] == {"records": len(ids(g)), "open": len(ids(g)) if g in open_groups else 0} for g in PROV_GROUPS)
          and all("third-of-a-percent-public" in r["workflow_run_url"] for r in recs["holdout"][1]),
          "provenance: the run links open only for the records of s6 to s10 (run ids from the public repository's first run on; the earlier groups' ids come before it, and the holdout's links name the earlier, now private, repository)")
    cm = lambda g: sum(1 for r in recs[g][1] if (r.get("criteria_sha256") or "") == crit_sha)  # noqa: E731
    s4_records = len(glob.glob(os.path.join(REPO, "results/s4-run-*/results-*/results.json"))) + len(glob.glob(os.path.join(REPO, "results/s4-smoke-*/results-*/results.json")))
    ck.ok(all(groups[g]["criteria_match"] == cm(g) for g in PROV_GROUPS)
          and all(cm(g) == len(recs[g][0]) for g in ("holdout", "s6", "s7", "arm", "s9", "dsweep"))
          and cm("early") == s4_records and cm("early") < len(recs["early"][0]) and cm("rewrite") == 0,
          "provenance: every record of s4 to s10 stores the hash of the rule file now in the repository (s4 and its smoke run inside the first group), none of s1 to s3 and none of the rewrite runs does")
    own = {g: sorted({(r.get("commit") or "")[:7] for r in recs[g][1]}) for g in PROV_GROUPS}
    where = {c["commit"]: c["where"] for g in P["groups"] for c in g["commits"]}
    ck.ok(all(sorted(c["commit"] for c in groups[g]["commits"]) == own[g] and sum(c["records"] for c in groups[g]["commits"]) == len(recs[g][0]) for g in PROV_GROUPS)
          and all(where[c] is None for g in ("early", "holdout", "rewrite") for c in own[g])
          and {c: where[c] for g in ("s6", "s7", "s9") for c in own[g]} == {"293b6b9": "main", "60f487d": "main", "32ab03c": "main"}
          and own["arm"] == ["6176991"] and where["6176991"] == "arm-smoke" and own["dsweep"] == ["8c874ec"] and where["8c874ec"] == "dsweep-smoke",
          "provenance: the commit each group's records stamp, and where the public repository holds it (s6, s7, s9 on main; the Arm and d-sweep runs on the kept branches arm-smoke and dsweep-smoke; every other stamped commit absent)")
    # the recorded times against the two fixtures written when they were read (tests/data)
    with open(os.path.join(REPO, "tests", "data", "s8_arm_timeline.json"), encoding="utf-8") as f:
        tl = json.load(f)
    with open(os.path.join(REPO, "tests", "data", "s9_s10_provenance.json"), encoding="utf-8") as f:
        pv = json.load(f)
    arm_lag = {}
    for rid, d in ((r["id"], r) for r in recs["arm"][1]):
        arm_lag[str(rid)] = min(arm_lag.get(str(rid), d["started_at"]), d["started_at"])
    fx_lag = {str(r["run"]): int((_parse_utc(arm_lag[str(r["run"])]) - _parse_utc(r["created_at"])).total_seconds()) for r in tl["full_runs"]}
    R = P["replication"]
    plan_utc = _parse_utc(pv["replication_plan"]["author_date"]).strftime("%Y-%m-%dT%H:%M:%SZ")
    s9_first = min(r["started_at"] for r in recs["s9"][1])
    first_run = min((r for r in recs["s9"][1] if str(r["id"]) == "39012918474"), key=lambda r: r["started_at"])["started_at"]
    start_lags = [R["first_run_lag_s"]] + [v for v in R["arm_run_lags_s"].values() if v < 120]  # the lags the page states, as it states them (the queued third Arm run is left out and said so)
    ck.ok(fx_lag == {k: v for k, v in R["arm_run_lags_s"].items()} and R["plan_commit_utc"] == plan_utc and R["first_record_start_utc"] == s9_first
          and R["margin_s"] == int((_parse_utc(s9_first) - _parse_utc(plan_utc)).total_seconds()) and R["first_run_lag_s"] == int((_parse_utc(first_run) - _parse_utc(R["first_run_created_utc"])).total_seconds())
          and min(start_lags) <= R["margin_s"] <= max(start_lags),
          f"provenance: the replication plan's commit time ({plan_utc}), the first record's start and the start lags equal the records and tests/data (margin {R['margin_s']} s, lags {sorted(R['arm_run_lags_s'].values())} and {R['first_run_lag_s']} s); the margin lies within the range of the start lags ({min(start_lags)} to {max(start_lags)} s), so the order of the commit and the dispatch cannot be shown")
    Dp = P["dsweep"]
    ds_first = min(r["started_at"] for r in recs["dsweep"][1])
    ck.ok(Dp["commit_utc"] == pv["dsweep_public"]["date"] and pv["dsweep_public"]["first_commit_with_plan_and_code"] == Dp["commit"]
          and Dp["first_record_start_utc"] == ds_first and Dp["gap_s"] == int((_parse_utc(ds_first) - _parse_utc(Dp["commit_utc"])).total_seconds()) > 0
          and Dp["branch"] == pv["dsweep_branch"]["branch"] and Dp["plan_sha256_equal"] is True,
          f"provenance: the d-sweep plan's public commit {Dp['commit']} and its time equal tests/data/s9_s10_provenance.json, and precede the first record's start by {Dp['gap_s']} s")
    # when the public history begins: the fixture (read from the GitHub API), and the records: every record of the earlier groups started before
    # the first public commit and every record of the later groups after it, so the sentence "after the runs of s1 to s4, the holdout and the
    # rewrite" is a statement about the records, not a remark
    PH, phf = P["public_history"], pv["public_history"]
    every = [r.get("started_at") for g in PROV_GROUPS for r in recs[g][1]]
    before = max(r["started_at"] for g in ("early", "holdout", "rewrite") for r in recs[g][1])
    after = min(r["started_at"] for g in ("s6", "s7", "arm", "s9", "dsweep") for r in recs[g][1])
    ck.ok(all(every) and PH == {"first_commit": phf["first_commit"], "first_commit_utc": phf["author_date"]} and before < phf["author_date"] < after
          and phf["author_date"][:10] == "2026-10-14",
          f"provenance: the public history begins with {phf['first_commit']} at {phf['author_date']} (tests/data), after the last record of s1 to s4, the holdout and the rewrite started ({before}) and before the first of s6 to s10 ({after})")
    # the rule file in the public commits the later records stamp: the fixture's blob hash is the hash of the file as it is now
    rf = pv["rule_file_in_public_commits"]
    with open(crit, "rb") as f:
        raw = f.read().replace(b"\r\n", b"\n")
    blob = hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()
    stamped = {c for g in ("s6", "s7", "s9") for c in own[g]}
    ck.ok(rf["file"] == index["criteria"]["file"] and rf["git_blob_sha1"] == blob and stamped and stamped <= set(rf["commits"]) and phf["first_commit"] in rf["commits"],
          f"provenance: the rule file as it is now is the blob {blob[:7]} that the public commits {', '.join(rf['commits'])} hold, and the commits the records of s6, s7 and s9 stamp ({', '.join(sorted(stamped))}) are among them")
    with open(os.path.join(DATA, "holdout.json"), encoding="utf-8") as f:
        H = json.load(f)
    hs = min(r["started_at"] for r in recs["holdout"][1])
    gap = int((_parse_utc(H["preregistration_committed_utc"]) - _parse_utc(H["first_job_start_utc"])).total_seconds())
    ck.ok(H["first_job_start_utc"] == hs and H["jobs"] == len(recs["holdout"][0]) and H["jobs_with_rule_hash"] == cm("holdout") == H["jobs"] and H["rule_file"] == index["criteria"]["file"]
          and gap > 0,
          f"provenance: the holdout's plan commit time ({H['preregistration_committed_utc']}) is {gap} s AFTER the first holdout job started ({hs}), so the records do not show the plan came first; every one of the {H['jobs']} jobs records the rule file's hash")
    # the page
    page = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    page.goto(base, wait_until="networkidle")
    wait_ready(page)
    dp = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    dp.goto(base + "details.html", wait_until="networkidle")
    wait_details(dp)
    total = sum(g["records"] for g in P["groups"])
    matched = sum(g["criteria_match"] for g in P["groups"])
    gone = sum(groups[g]["records"] for g in ("early", "holdout", "rewrite"))
    in_main = sum(groups[g]["records"] for g in ("s6", "s7", "s9"))
    linked = sum(g["links"]["records"] for g in P["groups"])
    opened = sum(g["links"]["open"] for g in P["groups"])
    want_prov = [
        "The rule files, plans and expectations named on this page were committed in the author’s unpublished development history before the runs they govern. "
        f"{prov_history_py(P)} The hashes stored in the result files show that the rule files did not change after the runs: "
        f"{matched} of the {total} result records store the sha256 of {index['criteria']['file']} as it is now, all the records of s4 to s10 and none of the older ones (s1 to s3, judged under earlier versions of the rules) or of the rewrite runs (judged under their own rule file).",
        f"The commit stamped in a record names the code that produced it. The {gone} records of s1 to s4, the holdout and the rewrite runs name commits of the unpublished history that this repository does not contain, so the code at those commits cannot be recovered from it; "
        f"the {in_main} records of s6, s7 and s9 name commits in this repository’s history, which hold the rule file as it is now. The {groups['arm']['records']} Arm records name {own['arm'][0]} and the {groups['dsweep']['records']} d-sweep records name {own['dsweep'][0]}, "
        f"commits on the temporary public branches {where[own['arm'][0]]} and {where[own['dsweep'][0]]}, which are kept for that reason.",
        f"Run links in the records open only for the runs of s6 to s10 ({opened} of {linked} links): the earlier runs were made before this repository existed, in repositories that are not public. "
        f"The commit and run facts here were read from the GitHub API on {P['read_on']}."]
    got_prov = dp.evaluate("[...document.querySelectorAll('#prov-full p')].map(p => p.innerText.replace(/\\s+/g, ' ').trim())")
    ck.ok(got_prov == want_prov, f"details, 'What the public record shows', word for word: the order cannot be checked here, the hash count, the commits and where they are, the run links, the date the facts were read ({first_diff(' | '.join(got_prov), ' | '.join(want_prov))})")
    # the text the details page holds before its script runs (what a reader sees without the script) gives the same account of the public history
    with open(os.path.join(SITE, "details.html"), encoding="utf-8") as f:
        static_prov = re.search(r'<dd id="prov-full"><p>(.*?)</p></dd>', f.read(), re.S)
    static_text = _squash(html.unescape(static_prov.group(1))) if static_prov else ""
    want_static = ("The rule files, plans and expectations were committed in the author’s unpublished development history before the runs they govern. "
                   + prov_history_py(P).rstrip(".") + "; what the result records show is listed here when the page loads.")
    ck.ok(static_text == want_static,
          f"details, 'What the public record shows', the text served before the script runs: the same account of the public history ({first_diff(static_text, want_static)})")
    ck.ok(dp.evaluate("document.querySelector('#prov-full').previousElementSibling.textContent.trim()") == "What the public record shows"
          and dp.evaluate("!!document.querySelector('#method-full #prov-full')"),
          "details: the account sits in the method section under its own heading")
    # the holdout paragraph
    ho = dp.inner_text('[data-v="holdoutText"]').replace("\xa0", " ")
    n_runs = {2: "Two", 3: "Three", 4: "Four"}[len(H["runs"])]
    want_ho = (f"The plan for this run (PREREGISTRATION.md) carries the commit time {utc_text_py(H['preregistration_committed_utc'])}, from the author’s clock in unpublished development history; that is {gap} second{'' if gap == 1 else 's'} after the start of the first job it governs "
               f"({utc_text_py(H['first_job_start_utc'])}), so the records do not show which came first. "
               f"The file lists the {n_runs.lower()} run IDs, so the commit that holds this version came after those runs were created. "
               f"What can be checked is that all {H['jobs_with_rule_hash']} of the {H['jobs']} jobs record the sha256 of the rule file as it is in this repository; nothing in the records shows that the pooling code (harness/pool.py) was unchanged. "
               f"{n_runs} fresh runs ({H['jobs']} jobs) were pooled as the first runs were. Same pattern")
    # the plan file names the run IDs: they are the three runs of the holdout records
    with open(os.path.join(REPO, "results", "s5-holdout", "PREREGISTRATION.md"), encoding="utf-8") as f:
        listed = re.search(r"^Run IDs \([^)]*\): ([\d, ]+)\.\s*$", f.read(), re.M)
    listed = sorted(x.strip() for x in listed.group(1).split(",")) if listed else []
    ck.ok(ho.startswith(want_ho) and "before its first run started" not in ho and "were fixed first" not in ho
          and listed == sorted({str(r["id"]) for r in recs["holdout"][1]}) == sorted(str(x) for x in H["runs"]) and len(listed) == len(H["runs"]),
          f"details, holdout: the plan's commit time is stated as {gap} s after the first job's start, so the order is not claimed; the plan file lists the {len(listed)} run IDs of the records, so its commit followed the runs' creation; only the rule-file hash match is claimed, and not that the pooling code was unchanged ({first_diff(ho[:len(want_ho)], want_ho)})")
    # the other places that state an order
    tuned, tuned_full = page.inner_text("#tuned").replace("\xa0", " "), dp.inner_text("#tuned-full").replace("\xa0", " ")
    ck.ok(tuned.endswith("Every rule file was committed before the runs it judges, in the author’s unpublished development history (what the public record shows).")
          and page.evaluate("document.querySelector('#tuned a').getAttribute('href')") == "details.html#prov-full"
          and "in the author’s unpublished development history (these hashes name commits of that history, which this repository does not contain)" in tuned_full,
          "main page 'tuned?' and details 'tuned?': a rule file committed before the runs, in the author's unpublished history (the details page adds that this repository does not contain it); the main page links the account")
    cap = page.inner_text("#cpu-cap").replace("\xa0", " ")
    mc = page.inner_text("#mit-caveat").replace("\xa0", " ")
    rx = page.inner_text("#rw-expect").replace("\xa0", " ")
    ck.ok("by rules written before these runs (in the author’s unpublished development history; what the public record shows)" in cap
          and page.evaluate("document.querySelector('#cpu-cap a').getAttribute('href')") == "details.html#prov-full"
          and "the rule committed before the first timed run (in the author’s unpublished development history)" in mc
          and "expectations committed before any run (in the author’s unpublished development history), " in rx,
          "main page: Table 1's caption, the rewrite caveat and the real-programs expectations each say the order rests on the author's unpublished development history")
    # the pool's growth: the registered design and the runs added after the verdicts of the smaller pool were read, the sizes from the three pooled files
    sizes = []
    for pf in ("results/s4-pooled", "results/s6-pooled", "results/s7-pooled"):
        with open(os.path.join(REPO, pf, "pooled.json"), encoding="utf-8") as fh:
            pd = json.load(fh)
        sizes.append((len(pd["runs"]), len(pd["inputs"])))
    steps_text = _squash(dp.inner_text("#pool-steps").replace("\xa0", " "))
    want_steps = (f"The pool grew while the data were being read. The registered design was {num_word_py(sizes[0][0])} runs of {index['criteria']['jobs_per_run']} jobs ({sizes[0][1]} jobs). "
                  f"{cap_py(num_word_py(sizes[1][0] - sizes[0][0]))} more full runs ({sizes[1][1]} jobs in all), then {num_word_py(sizes[2][0] - sizes[1][0])} more ({sizes[2][1]}), were added after the verdicts of the earlier pool had been read, "
                  "with no written stopping rule. The verdicts of each pool, under several interval methods, are in the robustness report.")
    ck.ok(sizes == [(3, 30), (13, 75), (15, 95)] and steps_text == want_steps and dp.evaluate("document.querySelector('#pool-steps a').textContent") == "robustness report"
          and index["pooled"]["steps"] == [{"source": s, "runs": r, "jobs": j} for s, (r, j) in zip(("results/s4-pooled/pooled.json", "results/s6-pooled/pooled.json", "results/s7-pooled/pooled.json"), sizes)],
          f"details, limits: the pool grew from {sizes[0][1]} to {sizes[1][1]} to {sizes[2][1]} jobs (sizes read from the three pooled files) by runs added after the verdicts of the smaller pool were read, with no written stopping rule, and the verdicts of each pool are in the robustness report ({first_diff(steps_text, want_steps)})")
    mcf = dp.inner_text("#mit-caveat-full").replace("\xa0", " ")
    hist = dp.inner_text("#tuned-full").replace("\xa0", " ")
    hist_p = dp.evaluate("[...document.querySelectorAll('p')].filter((p) => p.querySelector('[data-v=\"v3Written\"]')).map((p) => ({text: p.textContent.replace(/\\s+/g, ' '), link: [...p.querySelectorAll('a')].map((a) => a.getAttribute('href'))}))")
    ck.ok("That rule, committed before the first timed run (in the author’s unpublished development history), would call a rewrite" in mcf
          and len(hist_p) == 1 and hist_p[0]["link"] == ["#prov-full"] and "These orders rest on the author’s unpublished development history (what the public record shows)." in hist_p[0]["text"]
          and "in the author’s unpublished development history (these hashes name commits of that history" in hist,
          "details: the rewrite caveat and the rule history each say that the order they state rests on the author's unpublished development history (the history paragraph links the account)")
    old = ["no public record shows that order", "before its first run started", "is not checkable from public records", "The rules and the code that pools jobs were fixed first",
           "public repository is one commit", "repository is a single commit", "repository has one commit"]
    texts = [page.inner_text("body"), dp.inner_text("body")]
    ck.ok(not any(o in t for t in texts for o in old), "both pages: the earlier flat wordings of the order (the holdout 'before its first run started', the replication's 27-second 'no public record' and the d-sweep's 'not checkable') are gone")
    # every sentence block (paragraph, list item, table cell, caption, term, chip) that says something was committed, written, fixed, registered, listed, set or
    # planned before something else, or beforehand, in advance, or pre-registered, says in the same block that this rests on the author's unpublished development
    # history, or links to the account of it (#prov-full). Read four ways per page: as the reader gets it, with every section opened (the widgets build their chips),
    # and as served, before any script runs (the text a reader without script gets).
    hits = {"main page": page.evaluate(ORDER_CLAIMS_JS), "details page": dp.evaluate(ORDER_CLAIMS_JS)}
    for name, url, wait in (("main page", base, wait_ready), ("details page", base + "details.html", wait_details)):
        full = browser.new_page(viewport={"width": 1280, "height": 900})  # the wrapper opens every section
        full.goto(url, wait_until="networkidle")
        wait(full)
        hits[name + ", every section opened"] = full.evaluate(ORDER_CLAIMS_JS)
        hits[name + ", served text"] = full.evaluate(ORDER_CLAIMS_JS, full.evaluate("async (u) => (await fetch(u)).text()", url))
        full.close()
    bare = {n: [h["text"][:110] for h in hs if not h["qualified"]] for n, hs in hits.items()}
    seen_ids = {n: {h["id"] for h in hs} for n, hs in hits.items()}
    ck.ok(all(hits[n] for n in hits) and not any(bare.values())
          and {"cpu-cap", "tuned", "mit-caveat", "rw-expect"} <= seen_ids["main page"] and {"tuned-full", "mit-caveat-full"} <= seen_ids["details page"]
          and {"cpu-cap", "tuned", "mit-caveat"} <= seen_ids["main page, served text"],
          f"both pages: each statement that something was committed, written, fixed, registered, listed, set or planned before the runs (or beforehand, in advance, pre-registered) names the author's unpublished development history or links to the account of it; "
          f"{', '.join(f'{len(hs)} in the {n}' for n, hs in hits.items())}; without: {bare}")
    page.close()
    dp.close()


def _squash(t):
    return re.sub(r"\s+", " ", t or "").strip()


def _miss(got, want):
    """Where a page text stops matching the sentence that contains it; empty when the sentence is in it."""
    return "" if want in got else first_diff(got, want)


def range_x_py(lo, hi):
    a, b = fx_py(lo), fx_py(hi)
    return f"{a}×" if a == b else f"{a}–{b}×"


def claims_scope_checks(browser, base, ck, index):
    """Each count and range the page prints says which jobs, columns and sets it covers, and the scope is recomputed here from
    results/ and the data files (not read back from the page's own code): the Intel count and what it leaves out, and the
    column of the programs' cost range."""
    print("== claims: the scope of each count and range")
    IF = index["intel_forward"]
    tails = ["8573C", "6973P-C", "8370C"]
    shorts = {t: next(c for c in IF["cpus"] if c.endswith(t)) for t in tails}
    set_c = []
    for f in sorted(glob.glob(os.path.join(REPO, "results", "s9-run-*", "results-*", "results.json"))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        m = d["run"]["runner"]["cpu_model"].upper()
        if "INTEL" not in m:
            continue
        cell = next(q for q in d["cells"] if q["cell_id"] == "k02_add_fwd.L1")
        set_c.append((shorts[next(t for t in tails if t in m)], cell["aligned"]["ratio"]))
    per_c = {c: sum(1 for s, _ in set_c if s == c) for c in sorted({s for s, _ in set_c})}
    SC = IF["set_c"]
    ck.ok(SC["jobs"] == len(set_c) > 0 and SC["per_cpu"] == per_c and abs(SC["aligned"]["min"] - min(v for _, v in set_c)) < 1e-12
          and abs(SC["aligned"]["max"] - max(v for _, v in set_c)) < 1e-12 and not any("s9-run-" in j["source"] for j in IF["jobs"]),
          f"the Intel rows (n = {len(IF['jobs'])}) leave out the {len(set_c)} Intel jobs of replication set C ({per_c}), which the data counts beside them ({SC['aligned']['min']:.4f} to {SC['aligned']['max']:.4f} aligned in the same cell)")
    page = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    page.goto(base, wait_until="networkidle")
    wait_ready(page)
    dp = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    dp.goto(base + "details.html", wait_until="networkidle")
    wait_details(dp)
    n_by = {c: sum(1 for j in IF["jobs"] if j["cpu_short"] == c) for c in IF["cpus"]}
    counts = join_and_py([f"{c} in {jobs_py(n)}" for c, n in n_by.items()])
    c_counts = join_and_py([f"{c} in {jobs_py(n)}" for c, n in per_c.items()])
    rng_if = f"{fx_py(IF['aligned']['min'])}–{fx_py(IF['aligned']['max'])}"
    want_note = (f"on the {len(IF['cpus'])} Intel models drawn ({counts}; earlier runs included, replication set C’s {len(set_c)} Intel jobs not counted), "
                 f"the forward add at L1 cost {rng_if}× aligned in every job.")
    note = _squash(page.text_content("#cpu-note"))
    ck.ok(want_note in note, f"Table 1's note counts the Intel jobs it covers ({len(IF['jobs'])}) and says it leaves out the {len(set_c)} of replication set C {_miss(note, want_note)}")
    want_p = (f"aligned in every one of {len(IF['jobs'])} jobs, in the earlier runs, the early trial run and the pooled runs. "
              f"The {len(set_c)} Intel jobs of replication set C ({c_counts}; Figure 8 in section 1) are not among these {len(IF['jobs'])}; "
              f"in the same cell they cost {range_x_py(min(v for _, v in set_c), max(v for _, v in set_c))} aligned.")
    ip = _squash(dp.text_content("#intel-p"))
    ck.ok(want_p in ip and ip.count("replication set C") == 1, f"section 6 (details) gives the same scope: {len(IF['jobs'])} jobs, and the set C Intel jobs and their range named once {_miss(ip, want_p)}")
    # the programs' cost range: both columns, as everywhere else on the page
    with open(os.path.join(DATA, "realworld.json"), encoding="utf-8") as f:
        rw = json.load(f)
    T = rw["timing"]
    main_g = next(g for g in T["groups"] if g["cpu_model"] == T["main_cpu"])
    small = [d["row"] for d in rw["rows"] if not d["control"] and d["lines_none"] < 1 and main_g["rows"][d["row"]]["reading"] == "detectably slower"]
    rs = [main_g["rows"][n][c]["ratio"] for n in small for c in ("fast", "aligned")]
    lo, hi = f"{(min(rs) - 1) * 100:.1f}%", f"{(max(rs) - 1) * 100:.1f}%"
    shr = _squash(page.text_content("#rw-share"))
    want_s = f"yet FAST costs them {lo} to {hi} across the two columns: consistent"
    elsewhere = f"{T['slow_min'] * 100 - 100:.1f}% to {T['slow_max'] * 100 - 100:.1f}%"
    ck.ok(len(small) >= 2 and want_s in shr and f"{lo} to {hi}" == elsewhere and elsewhere in _squash(page.text_content("#rw-finding")),
          f"section 7: the cost beside the instruction share is the range over both columns ({lo} to {hi}), the same range as the pooled range given in the finding {_miss(shr, want_s)}")
    # working sets larger than the cache: recounted from every results file that holds a RAM cell
    def cpu_tag(model):
        m = re.search(r"EPYC\s+(\S+)", model)
        return f"EPYC {m.group(1)}" if m else "Xeon " + re.search(r"(\d{4}\w*(?:-C)?)", model).group(1).upper()
    ram_jobs = []
    for pat in ("results/*/results.json", "results/*/*/results.json"):
        for f in sorted(glob.glob(os.path.join(REPO, pat))):
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            cells = {c["cell_id"]: c for c in d.get("cells", [])}
            if any(c.get("size_class") == "RAM" for c in cells.values()):
                ram_jobs.append((cpu_tag(d["run"]["runner"]["cpu_model"]), cells))
    rj = lambda cid: [c[cid]["ratio"] for _, c in ram_jobs]  # noqa: E731
    pairs, spread = {}, {}
    for key, cid in (("rev", "k04_rev.RAM"), ("stride2", "k05_stride2.RAM")):
        dis = tot = 0
        top = None
        for m in sorted({t for t, _ in ram_jobs}):
            cs = [c[cid] for t, c in ram_jobs if t == m]
            for i in range(len(cs)):
                for k in range(i + 1, len(cs)):
                    tot += 1
                    dis += cs[i]["ci95"][1] < cs[k]["ci95"][0] or cs[k]["ci95"][1] < cs[i]["ci95"][0]
            if len(cs) > 1:
                sp = (max(c["ratio"] for c in cs) / min(c["ratio"] for c in cs) - 1) * 100
                if top is None or sp > top[0]:
                    top = (sp, m)
        pairs[key], spread[key] = (int(dis), tot), top
    RM = index["ram_early"]
    ck.ok(RM["jobs"] == len(ram_jobs) == 13 and RM["rev"] == {"min": min(rj("k04_rev.RAM")), "max": max(rj("k04_rev.RAM"))}
          and RM["stride2"] == {"min": min(rj("k05_stride2.RAM")), "max": max(rj("k05_stride2.RAM"))}
          and RM["rev_l2"] == {"min": min(rj("k04_rev.L2")), "max": max(rj("k04_rev.L2"))}
          and (RM["pairs"]["rev"]["disjoint"], RM["pairs"]["rev"]["total"]) == pairs["rev"] and (RM["pairs"]["stride2"]["disjoint"], RM["pairs"]["stride2"]["total"]) == pairs["stride2"]
          and abs(RM["spread"]["rev"]["pct"] - spread["rev"][0]) < 1e-9 and RM["spread"]["rev"]["cpu_short"] == spread["rev"][1],
          f"the RAM-sized cells in index.json equal a recount of the {len(ram_jobs)} results files that hold them (reverse {min(rj('k04_rev.RAM')):.3f} to {max(rj('k04_rev.RAM')):.3f}, stride-2 {min(rj('k05_stride2.RAM')):.3f} to {max(rj('k05_stride2.RAM')):.3f}; same-model pairs with disjoint intervals {pairs})")
    rng = lambda lo, hi: range_x_py(lo, hi)  # noqa: E731
    want_ram = (f"A RAM-sized working set was timed only in the {len(ram_jobs)} early jobs (as compiled) and not in the pooled runs. "
                f"There the reverse loop cost {rng(min(rj('k04_rev.RAM')), max(rj('k04_rev.RAM')))} and the stride-2 loop {rng(min(rj('k05_stride2.RAM')), max(rj('k05_stride2.RAM')))}, depending on the CPU model, "
                f"against {rng(min(rj('k04_rev.L2')), max(rj('k04_rev.L2')))} for the reverse loop at the L2 size in the same jobs. "
                f"Jobs of one CPU model differed by up to {spread['rev'][0]:.0f}% (the reverse loop on the {spread['rev'][1]}), and in {pairs['rev'][0]} of the {pairs['rev'][1]} pairs of such jobs the reverse loop’s intervals did not overlap "
                f"(stride-2: {pairs['stride2'][0]} of {pairs['stride2'][1]}). Out of cache the cost was smaller in these jobs and differed by CPU model, so the headline range holds for data that fits in cache only.")
    want_ram_short = (f"The headline range is for data that fits in cache. RAM-sized data, timed only in the {len(ram_jobs)} early jobs, cost reverse "
                      f"{rng(min(rj('k04_rev.RAM')), max(rj('k04_rev.RAM')))}, stride-2 {rng(min(rj('k05_stride2.RAM')), max(rj('k05_stride2.RAM')))}, by CPU model.")
    got_ram = _squash(dp.text_content("#limits-full"))
    cannot = _squash(page.text_content("#cannot"))
    ck.ok(want_ram in got_ram and want_ram_short in cannot and "did not reproduce between the first runs" not in got_ram
          and max(rj("k04_rev.RAM")) < min(rj("k04_rev.L2")),
          f"limits: the out-of-cache sentence gives the recounted ranges, the same-model spread and the pairs that disagree, on the details page and in the main page's limits box, and says the headline range is for data that fits in cache ({_miss(got_ram, want_ram)}{_miss(cannot, want_ram_short)})")
    # related work: the NIST row says what the paper's hardware table says (a Dell Precision T5400 with two Xeon X5450 CPUs under Linux; the
    # paper calls it a PC, never a server or a workstation, and uses 'bare metal' only for a measurement it proposes), and the
    # ACM Queue row says how its text was read, because its address answers a scripted fetch with HTTP 403
    with open(os.path.join(DATA, "related.json"), encoding="utf-8") as f:
        rel = json.load(f)
    rsrc = {x["id"]: x for x in rel["sources"]}
    nist, queue = rsrc["nist"], rsrc["queue"]
    bare = re.compile(r"bare[\s-]*metal", re.I)
    rel_blob = json.dumps(rel, ensure_ascii=False)
    got_list = _squash(dp.text_content("#rel-list"))
    got_main = _squash(page.text_content("#related"))
    got_sum = _squash(page.text_content("#rel-summary"))
    nist_words = ["a PC with two Xeon X5450 CPUs", "Dell Precision T5400", "Xeon X5450", "Turbo Boost unsupported", "SpeedStep off", "63 runs per cell", "Linux"]
    not_the_papers = re.compile(r"\b(?:server|workstation)\b|dual[\s-]*(?:socket|die|processor|cpu)", re.I)  # "dual-socket" is an inference from "2 x Xeon X5450", not the paper's word
    ck.ok(not bare.search(rel_blob) and not bare.search(got_list) and not bare.search(got_main)
          and not not_the_papers.search(nist["measured"] + " " + nist["m_short"] + " " + nist["differs"])
          and all(w in nist["measured"] for w in nist_words) and "a PC with two Xeon X5450 CPUs" in nist["m_short"]
          and nist["differs"].startswith("A dedicated machine with frequency scaling off")
          and _squash(nist["measured"]) in got_list and _squash(nist["m_short"]) in got_main and _squash(nist["differs"]) in got_list,
          f"related work: the NIST row names the paper's setup ({', '.join(nist_words)}), calls the machine neither a server nor a workstation (the paper says PC) and nowhere says 'bare metal', in the data, on the main page and on the details page ({_miss(got_list, _squash(nist['measured']))})")
    unconfirmed = re.compile(r"(?:not confirmed|unconfirmed) from a (?:saved )?copy")
    how_read = lambda t: all(w in t for w in ("read in a browser", "HTTP 403", "scripted fetch")) and unconfirmed.search(t) is not None  # noqa: E731
    ck.ok(how_read(queue["measured"]) and queue["measured"].startswith("As reported") and how_read(rel["summary"])
          and _squash(queue["measured"]) in got_list and _squash(rel["summary"]) in got_sum
          and 100 <= len(got_sum.split()) <= 190,
          f"related work: the ACM Queue row and the summary say the article was read in a browser and that its address returned HTTP 403 to a scripted fetch, so its figures are not confirmed from a saved copy ({_miss(got_list, _squash(queue['measured']))}{_miss(got_sum, _squash(rel['summary']))}; {len(got_sum.split())} words)")
    page.close()
    dp.close()


def missed_forward_py(c, pooled):
    """The Python twin of missedForward() in site/app.js: the judged forward cells of a model that break the written rule (aligned point ratio or interval end above the limit)."""
    pc = next(q for q in pooled["cpus"] if q["cpu_model"] == c["cpu_model"])
    lim = 1 + pc["verdict"]["forward_limit_pct"] / 100
    ps = {q["cell_id"] for q in c["placement_sensitive"]}
    return [x for x in pc["cells"] if x["class"] == "kept" and x["size_class"] in ("L1", "L2") and x["cell_id"] not in ps and x["aligned"]
            and (x["aligned"]["ratio"] > lim or x["aligned"]["ci95"][1] > lim)]


def placement_scope_checks(browser, base, ck, index):
    """What the placement exemption does and does not settle, said where the labels are: Table 1's caption, the alignment tooltip and
    Figure 7's caption, and the details paragraph that names the largest cell it leaves out, the cell judged instead, the example
    where the aligned column still differs, and the margins. Every number is recomputed from index.json and the pooled file."""
    print("== placement: the exemption, the alignment claim and the margins")
    with open(os.path.join(REPO, index["pooled"]["source"]), encoding="utf-8") as f:
        pooled = json.load(f)
    good = [c for c in index["cpus"] if c["enough"]]
    allps = [(c, q) for c in good for q in c["placement_sensitive"]]
    big_c, big_q = max(allps, key=lambda cq: cq[1]["aligned_ratio"])
    judged = [(c, next(x for x in missed_forward_py(c, pooled) if x["cell_id"] == big_q["cell_id"])) for c in good
              if any(x["cell_id"] == big_q["cell_id"] for x in missed_forward_py(c, pooled))]
    ex_c, ex_q = max(((c, q) for c, q in allps if q["cell_id"] == "k03_stencil.L1"), key=lambda cq: abs(cq[1]["aligned_ratio"] - cq[1]["ratio"]))
    narrow = []
    for c in good:
        cc = close_calls(c, pooled)
        if cc:
            lim = lim_of(c, pooled)
            i, hi, left = min(cc, key=lambda q: abs(q[1] - lim))
            narrow.append((c, abs(hi - lim), left))
    lim_big = lim_of(big_c, pooled)
    ck.ok(big_q["aligned_ratio"] > lim_big and judged and all(x["aligned"]["ratio"] > lim_of(c, pooled) and x["aligned"]["ratio"] < big_q["aligned_ratio"] for c, x in judged)
          and all(c["form"] == "inconclusive" for c, _ in judged) and big_c["form"] != "inconclusive" and narrow
          and abs(ex_q["aligned_ratio"] - ex_q["ratio"]) > 0.04,
          f"placement: the data behind the paragraph hold: the largest cell left out ({big_c['cpu_short']} {big_q['cell_id']}, {big_q['aligned_ratio']:.3f}) is above the limit and above the "
          f"cell judged instead ({[(c['cpu_short'], round(x['aligned']['ratio'], 3)) for c, x in judged]}), whose model is inconclusive while the first has a verdict; the stencil at L1 differs between columns by more than 0.04 on {ex_c['cpu_short']}; narrow models {[c['cpu_short'] for c, _, _ in narrow]}")
    bare = lambda cid: cell_name_py(cid).replace("the ", "", 1)  # noqa: E731
    verdict_of = lambda c: "is inconclusive" if c["form"] == "inconclusive" else "has a verdict"  # noqa: E731
    p1 = (f"The exemption sets no limit on the size of the effect it leaves out. The largest cell it leaves out is {cell_name_py(big_q['cell_id'])} on the {big_c['cpu_short']}, {fx_py(big_q['aligned_ratio'])}× aligned, "
          f"and the {big_c['cpu_short']} {verdict_of(big_c)}"
          + (f"; the {join_and_py([f'{c['cpu_short']}’s {bare(big_q['cell_id'])}, {fx_py(x['aligned']['ratio'])}× aligned and not flagged,' for c, x in judged])} is judged, misses the limit, and the {judged[0][0]['cpu_short']} {verdict_of(judged[0][0])}" if judged else "")
          + ". The labels in Table 1 therefore describe the cells left after the exemption, not every forward cell; the cells left out and their aligned ratios are listed beside each label (Table 1, and Table 2 below).")
    p2 = (f"Aligning every hot loop to a 64-byte boundary removes one source of code-placement variation, not all of it: it fixes only where each hot loop starts, and the loop’s length, the position of its inner branches and of the code around it are left as compiled. "
          f"The {bare(ex_q['cell_id'])} on the {ex_c['cpu_short']} shows that the column still matters: {fx_py(ex_q['ratio'])}× as compiled, {fx_py(ex_q['aligned_ratio'])}× aligned.")
    bits = join_and_py([(f"{m:.4f} above it on the {c['cpu_short']} (a cell left out as placement-sensitive, which would miss the limit if counted)" if left else f"{m:.4f} below it on the {c['cpu_short']}") for c, m, left in narrow])
    p3 = (f"Several words rest on small margins. {'On the model' if len(narrow) == 1 else 'On the models'} called narrow in Table 1, the interval end nearest the forward limit lies {bits}. "
          "The intervals resample jobs and understate the spread between runs (“Run to run”, section 8), so these words can change with the jobs drawn or the seed. "
          "How the verdicts move with the interval method is in the robustness report and, for the Arm pool, how the stored verdict sits among other seeds is in the seed-sensitivity file.")
    page = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    page.goto(base, wait_until="networkidle")
    wait_ready(page)
    dp = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    dp.goto(base + "details.html", wait_until="networkidle")
    wait_details(dp)
    got = dp.evaluate("[...document.querySelectorAll('#ps-scope p')].map(p => p.textContent.replace(/\\s+/g, ' ').trim())")
    ck.ok(got == [p1, p2, p3], f"details, section 3: what the exemption does and does not settle, word for word ({first_diff(' | '.join(got), ' | '.join([p1, p2, p3]))})")
    links = dp.evaluate("[...document.querySelectorAll('#ps-scope p a')].map(a => [a.textContent, a.getAttribute('href')])")
    repo = index["repo"]["base"]
    want_links = [["“Run to run”, section 8", "#method-full"], ["robustness report", f"{repo}/blob/main/robustness/report.md"], ["seed-sensitivity file", f"{repo}/blob/main/arm64/seed-sensitivity.json"]]
    ck.ok(links == want_links and os.path.exists(os.path.join(REPO, "robustness", "report.md")) and os.path.exists(os.path.join(REPO, "arm64", "seed-sensitivity.json"))
          and dp.evaluate("!!document.getElementById('method-full')"),
          f"details, section 3: the links go to the Run to run entry, the robustness report and the seed-sensitivity file, which exist ({links})")
    cap = _squash(page.text_content("#cpu-cap"))
    tip = _squash(page.text_content("#col-tip"))
    armcap = _squash(page.evaluate("document.getElementById('arm-cap').textContent"))
    ck.ok("Placement-sensitive cells (section 3) are left out of the 2% test, with no limit on their size, and shown in their own column; the pattern describes only the cells left." in cap,
          f"Table 1's caption says the exemption sets no limit on the size of the cells it leaves out and the pattern describes only the cells left ({_miss(cap, 'Placement-sensitive cells (section 3) are left out of the 2%')})")
    ck.ok(tip == "Aligned: every hot loop starts on a 64-byte boundary. That removes one source of code-placement variation, not all of it (section 3). As compiled: the binary exactly as clang emitted it."
          and "Aligned: every hot loop starts on a 64-byte boundary in both builds. That removes one source of code-placement variation, not all of it (details, section 3). As compiled: the binaries exactly as clang emitted them." in armcap,
          "the alignment tooltip and Figure 7's caption say the 64-byte alignment removes one source of code-placement variation, not all of it")
    ck.ok(all("cannot sway the result" not in _squash(p.text_content("body")) for p in (page, dp)) and "where the code happens to land" not in _squash(page.text_content("body")),
          "both pages: 'cannot sway the result' is gone")
    page.close()
    dp.close()


def pages_workflow_checks(browser, base, ck, index):
    """The live page is published only after the ci workflow has passed on the commit (a push that the offline checks reject
    does not reach readers); the workflow still runs by hand."""
    print("== pages workflow: deploys only after a green ci run")
    import yaml
    with open(os.path.join(REPO, ".github", "workflows", "pages.yml"), encoding="utf-8") as f:
        pg = yaml.safe_load(f)
    with open(os.path.join(REPO, ".github", "workflows", "ci.yml"), encoding="utf-8") as f:
        ci = yaml.safe_load(f)
    on = pg.get("on", pg.get(True))  # YAML 1.1 reads the bare key `on` as the boolean True
    job = pg["jobs"]["deploy"]
    steps = job["steps"]
    checkout = next(s for s in steps if str(s.get("uses", "")).startswith("actions/checkout@"))
    ck.ok(set(on) == {"workflow_run", "workflow_dispatch"} and "push" not in on and "pull_request" not in on
          and on["workflow_run"] == {"workflows": [ci["name"]], "types": ["completed"], "branches": ["main"]},
          f"pages.yml: runs after the '{ci['name']}' workflow completes on main (and by hand), never on a bare push")
    cond = job.get("if", "")
    ck.ok("github.event.workflow_run.conclusion == 'success'" in cond and "github.event_name == 'workflow_dispatch'" in cond
          and cond.count("||") == 1 and "always()" not in cond,
          "pages.yml: the deploy job runs only for a successful ci run, or by hand")
    ck.ok("github.event.workflow_run.head_sha" in str(checkout.get("with", {}).get("ref", "")),
          "pages.yml: the page deployed is the commit whose ci run passed")
    ck.ok(any(str(s.get("uses", "")).startswith("actions/deploy-pages@") for s in steps) and (ci.get("on") or ci.get(True)).get("push") is not None,
          "pages.yml deploys the site folder, and ci.yml still runs on a push to main (what pages.yml waits for)")


SCROLLER_JS = """() => [...document.querySelectorAll('.tablewrap')].map(w => ({
    id: w.id || (w.querySelector('table') || {}).id || w.previousElementSibling?.id || '#' + [...document.querySelectorAll('.tablewrap')].indexOf(w),
    dims: [w.scrollWidth, w.clientWidth, w.scrollHeight, w.clientHeight], visible: w.offsetParent !== null,
    over: w.scrollWidth > w.clientWidth + 1 || w.scrollHeight > w.clientHeight + 1, sideways: w.scrollWidth > w.clientWidth + 1,
    tabindex: w.getAttribute('tabindex'), role: w.getAttribute('role'), label: w.getAttribute('aria-label') || '', made: w.dataset.reach || null }))"""


def access_checks(browser, base, ck, index):
    """Without JavaScript both pages say what is missing; with it, every table box that scrolls can be reached and named from the
    keyboard, at the widths where tables overflow, and a box that fits is not made a tab stop."""
    print("== access: no-JavaScript note, scrollable table boxes reachable from the keyboard")
    lost = index["page"]["lost"]
    ctx = browser.new_context(java_script_enabled=False, viewport={"width": 1280, "height": 900})
    for name, url in (("main page", base), ("details page", base + "details.html")):
        pg = ctx.new_page()
        pg.goto(url, wait_until="load")
        note = _squash(pg.inner_text(".ns-note")) if pg.locator(".ns-note").count() else ""
        ck.ok(note.startswith("JavaScript is off.") and "data files (site/data/*.json)" in note and "numbers are missing" in note and pg.locator(".ns-note").first.is_visible(),
              f"{name} with JavaScript off: a visible note says the sentences and tables are filled in from the data files and their numbers are missing ({note[:60]!r})")
        pg.close()
    pg = ctx.new_page()
    pg.goto(base, wait_until="load")
    gist = _squash(pg.inner_text("#result .gist"))
    ck.ok(f"take {lost['min']:.1f} to {lost['max']:.1f}× as long at the study’s sizes" in gist, f"main page with JavaScript off: the Result gist still carries the headline range from the data ({gist[:80]!r})")
    pg.close()
    ctx.close()
    seen = {"main": 0, "details": 0}
    for w_, h_ in ((768, 1024), (1024, 768), (1440, 900), (390, 844)):
        for key, url, ready in (("main", base, wait_ready), ("details", base + "details.html", wait_details)):
            pg = browser.new_page(viewport={"width": w_, "height": h_})
            pg.goto(url, wait_until="networkidle")
            ready(pg)
            pg.wait_for_timeout(400)
            boxes = pg.evaluate(SCROLLER_JS)
            vis = [b for b in boxes if b["visible"]]
            # a box that scrolls is a focusable region with a name (boxes that carry that markup in the page or in their widget keep it; the others get it while they overflow)
            bad = [b for b in vis if b["over"] and not (b["tabindex"] == "0" and b["role"] == "region" and len(b["label"]) >= 5)]
            extra = [b for b in vis if not b["over"] and b["made"]]
            seen[key] += sum(1 for b in vis if b["over"]) if w_ in (768, 1024) else 0
            ck.ok(len(vis) >= 3 and not bad and not extra,
                  f"{key} page at {w_} px: each of the {len(vis)} table boxes that scrolls ({sum(1 for b in vis if b['over'])}) is a named, focusable region and the others are left alone"
                  + ("" if not (bad or extra) else f": missing {[(b['id'], b['dims']) for b in bad][:4]}, needless {[(b['id'], b['dims']) for b in extra][:4]}"))
            if w_ in (768, 1024):
                side = pg.evaluate("""() => { const w = [...document.querySelectorAll('.tablewrap')].find(x => x.offsetParent !== null && x.scrollWidth > x.clientWidth + 1 && x.getAttribute('tabindex') === '0');
                    if (!w) return null; w.scrollLeft = 0; w.focus(); return [document.activeElement === w, w.id || w.querySelector('table').id]; }""")
                if side:
                    pg.keyboard.press("ArrowRight")
                    pg.keyboard.press("ArrowRight")
                    moved = pg.evaluate("document.activeElement.scrollLeft")
                    ck.ok(side[0] and moved > 0, f"{key} page at {w_} px: a table box ({side[1]}) takes focus and the arrow keys scroll it sideways (scrolled {moved:.0f} px)")
            pg.close()
    pg = browser.new_page(viewport={"width": 768, "height": 1024})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_timeout(300)
    at768 = pg.evaluate("(() => { const w = document.getElementById('cpu-table').closest('.tablewrap'); return [w.getAttribute('tabindex'), w.getAttribute('role'), w.getAttribute('aria-label')]; })()")
    pg.set_viewport_size({"width": 1440, "height": 900})
    pg.wait_for_timeout(500)
    at1440 = pg.evaluate("(() => { const w = document.getElementById('cpu-table').closest('.tablewrap'); return [w.getAttribute('tabindex'), w.getAttribute('role'), w.getAttribute('aria-label')]; })()")
    pg.close()
    ck.ok(at768[0] == "0" and at768[1] == "region" and at768[2] == "Table 1, scrollable" and at1440 == [None, None, None],
          f"Table 1's box becomes a named focusable region when the window is narrow ({at768}) and stops being a tab stop when it is widened again ({at1440})")
    ck.ok(seen["main"] >= 1 and seen["details"] >= 1,
          f"the keyboard checks are not empty: tables that scroll sideways exist at 768 and 1024 px on the main page ({seen['main']}) and the details page ({seen['details']})")


def _settle_scroll(pg, ms=1500):
    """Wait until the window has stopped scrolling (the page scrolls smoothly) and return the final scroll position."""
    return pg.evaluate("""(ms) => new Promise(res => { let last = -1, still = 0; const t0 = performance.now();
        const tick = () => { const y = scrollY; still = Math.abs(y - last) < 0.5 ? still + 1 : 0; last = y;
            if (still >= 6 || performance.now() - t0 > ms) res(y); else requestAnimationFrame(tick); }; tick(); })""", ms)


def nav_checks(browser, base, ck, index):
    """The details page is 54,000 to 67,000 px long: its Contents row has to stay in view while the reader scrolls, and a jump from it
    must land the section's heading below the row, not under it."""
    print("== ux: the details page keeps its Contents row in view")
    for w_, h_ in ((390, 844), (1440, 900)):
        pg = browser.new_page(viewport={"width": w_, "height": h_})
        pg.goto(base + "details.html", wait_until="networkidle")
        wait_details(pg)
        pg.wait_for_timeout(300)
        total = pg.evaluate("document.documentElement.scrollHeight")
        tops = []
        for frac in (0.1, 0.4, 0.75, 0.97):
            pg.evaluate("(y) => window.scrollTo({top: y, behavior: 'instant'})", int(total * frac))
            pg.wait_for_timeout(120)
            tops.append(pg.evaluate("(() => { const r = document.querySelector('.dnav-bar').getBoundingClientRect(); return [Math.round(r.top), Math.round(r.bottom), scrollY]; })()"))
        ck.ok(total > 20000 and all(-1 <= t[0] <= 1 and 20 <= t[1] <= 90 for t in tops),
              f"details page at {w_} px: the Contents row is at the top of the window after scrolling to 10, 40, 75 and 97% of its {total} px ({[(t[2], t[0], t[1]) for t in tops]})")
        pg.evaluate("window.scrollTo({top: document.documentElement.scrollHeight * 0.6, behavior: 'instant'})")
        pg.wait_for_timeout(120)
        link = pg.locator(".dnav a:not(.dgo)").nth(2)
        href = link.get_attribute("href")
        link.click()
        y = _settle_scroll(pg)
        pg.wait_for_timeout(300)
        land = pg.evaluate("(h) => { const t = document.querySelector(h); const b = document.querySelector('.dnav-bar').getBoundingClientRect(); const r = (t.querySelector('h2, h3') || t).getBoundingClientRect(); return [Math.round(r.top), Math.round(b.bottom)]; }", href)
        ck.ok(land[0] >= land[1] - 2 and land[0] < h_ * 0.5,
              f"details page at {w_} px: the Contents link {href} from deep in the page lands its heading ({land[0]} px from the top) below the Contents row (bottom {land[1]} px)")
        pg.close()


def textsize_checks(browser, base, ck, index):
    """A reader who sets the text to 125, 150 or 200% on a phone still gets a page that does not scroll sideways, a title that is not
    cut off, a top bar that fits and a Contents menu that opens inside the window. (The hero race on the main page has fixed lane
    columns and runs 2 to 12 px past a 390 or 320 px window at 200%: that case is not asserted for the main page.)"""
    print("== ux: larger text on a phone")
    cases = [("main page", "", w_, z) for w_ in (390, 320) for z in (125, 150)] + [("main page", "", 390, 200)] \
        + [("details page", "details.html", w_, z) for w_ in (390, 320) for z in (125, 150, 200)]
    for name, rel, w_, z in cases:
        pg = browser.new_page(viewport={"width": w_, "height": 800})
        pg.add_init_script(f"document.addEventListener('DOMContentLoaded', () => {{ document.documentElement.style.fontSize = '{z}%'; }})")
        pg.goto(base + rel, wait_until="networkidle")
        (wait_ready if not rel else wait_details)(pg)
        pg.wait_for_timeout(500)
        m = pg.evaluate("""() => { const h = document.querySelector('h1').getBoundingClientRect(), h1 = document.querySelector('h1'), bar = document.querySelector('.bar');
            return {W: innerWidth, doc: document.documentElement.scrollWidth, h1: [Math.round(h.left), Math.round(h.right), h1.scrollWidth - h1.clientWidth],
                    bar: bar ? [bar.scrollWidth - bar.clientWidth, Math.round(bar.getBoundingClientRect().height)] : null,
                    fs: parseFloat(getComputedStyle(document.documentElement).fontSize)}; }""")
        if name == "main page" and z == 200:
            # the hero race is outside what is asserted at 200%: check the bar and the Contents menu only
            fits_page = True
        else:
            fits_page = m["doc"] <= m["W"] + 1
        ok = fits_page and m["h1"][0] >= 0 and m["h1"][1] <= m["W"] + 1 and m["h1"][2] <= 1 and (m["bar"] is None or m["bar"][0] <= 1)
        ck.ok(ok and m["fs"] >= 16 * z / 100 - 0.5,
              f"{name} at {w_} px with the text at {z}%: no sideways page scroll (page {m['doc']} of {m['W']} px), the title is inside the window (h1 {m['h1'][0]} to {m['h1'][1]}), the top bar fits ({m['bar']})")
        if rel == "":
            pg.click(".toc-btn")
            pg.wait_for_timeout(150)
            ol = pg.evaluate("(() => { const r = document.querySelector('.toc ol').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.height)]; })()")
            ck.ok(ol[0] >= -1 and ol[1] <= w_ + 1 and ol[2] > 40,
                  f"main page at {w_} px with the text at {z}%: the Contents menu opens inside the window ({ol[0]} to {ol[1]} px of {w_})")
        pg.close()


_MARKS_JS = """() => { const nm = e => e.tagName.toLowerCase() + '.' + String(e.className).trim().replace(/\\s+/g, '.');
    const out = []; [...document.querySelectorAll('body *')].forEach((e, i) => { const s = getComputedStyle(e), b = e.getBoundingClientRect();
        if (s.display === 'none' || s.visibility === 'hidden' || b.width < 1 || b.height < 1 || e.closest('svg') || e.tagName === 'CANVAS') return;
        const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        if ((s.backgroundColor !== 'rgba(0, 0, 0, 0)' || s.backgroundImage !== 'none') && !own && b.width <= 140 && b.height <= 60)
            out.push([i, nm(e) + (e.className ? '' : ' < ' + nm(e.parentElement) + ' < ' + nm(e.parentElement.parentElement))]); });
    return out; }"""
_DRAWN_JS = """(idx) => { const all = [...document.querySelectorAll('body *')], bad = {};
    idx.forEach(([i, name]) => { const s = getComputedStyle(all[i]);
        const border = ['Top', 'Right', 'Bottom', 'Left'].some(d => parseFloat(s['border' + d + 'Width']) > 0 && s['border' + d + 'Style'] !== 'none');
        const outline = parseFloat(s.outlineWidth) > 0 && s.outlineStyle !== 'none';
        if (!(s.forcedColorAdjust === 'none' || border || outline)) bad[name] = (bad[name] || 0) + 1; });
    return bad; }"""


def forced_colors_checks(browser, base, ck, index):
    """Under forced colours (a Windows contrast theme) the browser paints every background in the canvas colour. A mark that is only a
    coloured box (a bar, a dot, a switch track, a legend chip) has to keep its colour or gain a border or outline, or it disappears and
    only the text is left. Found by comparing each painted, text-free mark in the normal rendering with the same element under forced colours."""
    print("== ux: forced colours")
    for name, rel in (("main page", ""), ("details page", "details.html")):
        pg = browser.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(base + rel, wait_until="networkidle")
        (wait_ready if not rel else wait_details)(pg)
        pg.wait_for_timeout(1500)
        pg.emulate_media(forced_colors="none")
        idx = pg.evaluate(_MARKS_JS)
        pg.emulate_media(forced_colors="active")
        pg.wait_for_timeout(300)
        bad = pg.evaluate(_DRAWN_JS, idx)
        ck.ok(len(idx) >= (200 if not rel else 50) and not bad,
              f"{name} under forced colours: each of the {len(idx)} painted marks (bars, dots, switch, legend chips) keeps its colour or an outline" + ("" if not bad else f": would vanish {dict(list(bad.items())[:6])}"))
        if not rel:
            sel = pg.evaluate("(() => { const r = document.querySelector('#rows .row[aria-selected=\"true\"]'); if (!r) return null; const s = getComputedStyle(r), b = getComputedStyle(r, '::before'); return [s.outlineStyle, parseFloat(s.outlineWidth), b.forcedColorAdjust]; })()")
            ck.ok(sel is not None and sel[0] != "none" and sel[1] >= 2 and sel[2] == "none",
                  f"main page under forced colours: the selected row in Figure 1 is marked by an outline and its edge bar keeps a system colour ({sel})")
        pg.close()


def tooltip_checks(browser, base, ck, index):
    """Both tooltips stay inside the window: the help box next to 'aligned / as compiled' (opened by its ? button) at every width from
    a phone to a wide desktop, and the box that follows the pointer over the Figure 1 dots."""
    print("== ux: tooltips stay inside the window")
    out = []
    for w_, h_ in ((320, 700), (390, 844), (641, 800), (680, 900), (768, 1024), (900, 800), (1024, 768), (1240, 800), (1280, 900), (1440, 900), (1920, 1080)):
        pg = browser.new_page(viewport={"width": w_, "height": h_})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        pg.evaluate("document.querySelector('#col-hint').scrollIntoView({block: 'center'})")
        pg.wait_for_timeout(250)
        pg.click("#col-hint")
        pg.wait_for_timeout(250)
        r = pg.evaluate("(() => { const r = document.getElementById('col-tip').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.bottom), getComputedStyle(document.getElementById('col-tip')).opacity]; })()")
        out.append((w_, r))
        pg.close()
    bad = [(w_, r) for w_, r in out if r[0] < 0 or r[1] > w_ or r[2] < 0 or r[4] != "1"]
    ck.ok(not bad, f"the help box beside 'aligned / as compiled' opens inside the window at all {len(out)} widths from 320 to 1920 px" + ("" if not bad else f": outside at {bad[:3]}"))
    seen = 0
    badtip = []
    for w_, h_ in ((390, 844), (768, 1024), (1024, 768), (1280, 900)):
        pg = browser.new_page(viewport={"width": w_, "height": h_})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        pg.evaluate("document.querySelector('#fig1').scrollIntoView()")
        pg.wait_for_timeout(300)
        for hnd in pg.query_selector_all("#rows .mk-hit"):
            bb = hnd.bounding_box()
            if not bb or bb["width"] == 0:
                continue
            pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
            pg.wait_for_timeout(40)
            r = pg.evaluate("(() => { const t = document.getElementById('tip'); if (t.hidden) return null; const r = t.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.bottom)]; })()")
            if r:
                seen += 1
                if r[0] < 0 or r[1] > w_ or r[2] < 0 or r[3] > h_:
                    badtip.append((w_, r))
        pg.mouse.move(2, 2)
        pg.close()
    ck.ok(seen >= 40 and not badtip, f"the box that follows the pointer over the Figure 1 dots stays inside the window ({seen} hovers at 390, 768, 1024 and 1280 px)" + ("" if not badtip else f": outside {badtip[:3]}"))


def dialog_checks(browser, base, ck, index):
    """The machine-code slide-over is a modal dialog: it says so, Tab and Shift+Tab stay inside it however many times they are pressed
    (it ends in a <summary>, which its own handler does not count), and Escape gives focus back to the control that opened it."""
    print("== ux: the machine-code dialog")
    ACT = "(() => { const a = document.activeElement; return [a ? a.tagName.toLowerCase() + '#' + a.id + ':' + [...document.querySelectorAll('#asm-panel *')].indexOf(a) : null, !!(a && a.closest('#asm-panel'))]; })()"
    for w_, h_ in ((1280, 900), (390, 844)):
        pg = browser.new_page(viewport={"width": w_, "height": h_})
        pg.goto(base, wait_until="networkidle")
        wait_ready(pg)
        pg.wait_for_timeout(500)
        opener = pg.locator(".rr-name").first
        opener_id = opener.get_attribute("id")
        opener.click()
        pg.wait_for_timeout(600)
        modal = pg.evaluate("[document.getElementById('asm-panel').hidden, document.getElementById('asm-panel').getAttribute('role'), document.getElementById('asm-panel').getAttribute('aria-modal')]")
        def walk(n):
            seen, outside = [], []
            for _ in range(n):
                pg.keyboard.press("Tab")
                a = pg.evaluate(ACT)
                seen.append(a[0])
                if not a[1]:
                    outside.append(a[0])
            pg.keyboard.press("Shift+Tab")
            return seen, outside, pg.evaluate(ACT)[1]
        seen1, out1, back1 = walk(30)          # the "Full listing and commands" part is closed: only the Close button and its summary can take focus
        pg.locator("#asm-panel summary").first.click()
        pg.wait_for_timeout(300)
        seen2, out2, back2 = walk(30)          # opened: its links and Copy buttons join, and Tab still never leaves the dialog
        ck.ok(modal == [False, "dialog", "true"] and not out1 and not out2 and back1 and back2 and len(set(seen1)) >= 2 and len(set(seen2)) >= 4,
              f"machine-code dialog at {w_} px: it is marked aria-modal, 30 presses of Tab stay inside it with the listing closed ({len(set(seen1))} controls) and open ({len(set(seen2))} controls), and Shift+Tab does too"
              + ("" if not (out1 or out2) else f" (left for {(out1 + out2)[:3]})") + ("" if modal == [False, 'dialog', 'true'] else f" ({modal})"))
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(500)
        after = pg.evaluate("document.activeElement.id")
        ck.ok(after == opener_id, f"machine-code dialog at {w_} px: Escape closes it and focus returns to the control that opened it (#{after})")
        pg.close()


def names_checks(browser, base, ck, index):
    """Accessible names, as the browser computes them: a section heading is its own words (the permalink inside it does not leak into
    the name), and the twelve 'Details' buttons each say which section they open, before and after a click."""
    print("== ux: accessible names")
    pg = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_timeout(500)
    heads = pg.evaluate("[...document.querySelectorAll('.body section[id] > h2')].map(h => [h.getAttribute('aria-label') || '', h.querySelector('.secno') ? h.querySelector('.secno').textContent : '', h.querySelector('.pil') ? h.querySelector('.pil').getAttribute('aria-label') : null])")
    leaked = pg.get_by_role("heading", level=2, name=re.compile("Link to")).count()
    ck.ok(len(heads) >= 10 and leaked == 0 and all(h[0] and h[0].startswith(h[1]) and h[2] and h[2].startswith("Link to section: ") and h[2][len("Link to section: "):] in h[0] for h in heads),
          f"main page: each of the {len(heads)} section headings is named by its own words, and the permalink inside it names the section ({heads[0][0]!r} and {heads[0][2]!r}; {leaked} headings with a name that contains 'Link to')")
    btns = pg.evaluate("[...document.querySelectorAll('.sec-more')].map(b => [b.textContent.trim(), b.getAttribute('aria-label')])")
    names = [b[1] for b in btns]
    byrole = pg.get_by_role("button", name=re.compile(r"^Details: ")).count()
    ck.ok(len(btns) >= 10 and len(set(names)) == len(names) and all(b[1] and b[1].startswith(b[0] + ": ") for b in btns) and byrole == len(btns),
          f"main page: the {len(btns)} section buttons have {len(set(names))} different accessible names, each starting with the visible text ({btns[0][1]!r}; {byrole} found by role and name)")
    first = pg.locator(".sec-more").first
    first.click()
    pg.wait_for_timeout(200)
    after = first.get_attribute("aria-label")
    ck.ok(after and after.startswith("Hide details: ") and after[len("Hide details: "):] == names[0][len("Details: "):],
          f"main page: after a click the first section button is named {after!r}, matching its visible text")
    pg.close()


_CONTRAST_JS = """() => {
  const parse = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return [0, 0, 0, 1]; const p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const lum = ([r, g, b]) => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const bgOf = e => { let acc = [255, 255, 255]; const chain = []; for (let a = e; a; a = a.parentElement) { const c = parse(getComputedStyle(a).backgroundColor); chain.push(c); if (c[3] >= 0.99) break; }
    for (let i = chain.length - 1; i >= 0; i--) { const c = chain[i]; acc = [0, 1, 2].map(k => c[k] * c[3] + acc[k] * (1 - c[3])); } return acc; };
  const opOf = e => { let o = 1; for (let a = e; a; a = a.parentElement) o *= parseFloat(getComputedStyle(a).opacity); return o; };
  let checked = 0; const bad = {};
  document.querySelectorAll('body *').forEach(e => {
    if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
    const s = getComputedStyle(e), b = e.getBoundingClientRect(); if (s.display === 'none' || s.visibility === 'hidden' || b.width < 1 || b.height < 1) return;
    if (e.closest('svg, canvas, script, style, noscript')) return;
    const fg = parse(s.color), bg = bgOf(e), o = opOf(e) * fg[3]; if (o < 0.1) return;   // a hidden-until-hover tip or permalink is not text on screen
    checked++;
    const mix = [0, 1, 2].map(i => fg[i] * o + bg[i] * (1 - o));
    const cr = (Math.max(lum(mix), lum(bg)) + .05) / (Math.min(lum(mix), lum(bg)) + .05);
    const px = parseFloat(s.fontSize), large = px >= 24 || (px >= 18.66 && parseInt(s.fontWeight) >= 700);
    if (cr < (large ? 3 : 4.5)) { const k = e.tagName.toLowerCase() + '.' + String(e.className).trim().replace(/\\s+/g, '.').slice(0, 36) + ' (' + cr.toFixed(2) + ', opacity ' + o.toFixed(2) + ')'; bad[k] = (bad[k] || 0) + 1; }
  });
  return {checked, bad}; }"""

_TARGETS_JS = """() => { const out = {}; const cells = {n: 0};
  document.querySelectorAll('button, a[href], select, input, summary, [role=button], [role=radio], [role=option], [role=switch], [role=tab], [tabindex="0"]').forEach(e => {
    const s = getComputedStyle(e), b = e.getBoundingClientRect(); if (s.display === 'none' || s.visibility === 'hidden' || b.width === 0 || b.height === 0) return;
    if (e.tagName === 'A' && s.display === 'inline') return;                       // a link inside running text is exempt
    let w = b.width, h = b.height; const a = getComputedStyle(e, '::after');
    if (a.content !== 'none' && a.position === 'absolute') { const l = parseFloat(a.left), r = parseFloat(a.right), t = parseFloat(a.top), bt = parseFloat(a.bottom);
      if (!isNaN(l) && !isNaN(r)) w = b.width - l - r; if (!isNaN(t) && !isNaN(bt)) h = b.height - t - bt; const ww = parseFloat(a.width), hh = parseFloat(a.height); if (!isNaN(ww) && ww > w) w = ww; if (!isNaN(hh) && hh > h) h = hh; }
    if (w < 24 - 0.5 || h < 24 - 0.5) { if (e.classList.contains('ce-cell')) { cells.n++; return; }
      const k = e.tagName.toLowerCase() + '.' + String(e.className).trim().replace(/\\s+/g, '.').slice(0, 30) + ' ' + Math.round(w) + 'x' + Math.round(h) + ' "' + (e.textContent || '').trim().slice(0, 20) + '"'; out[k] = (out[k] || 0) + 1; } });
  return {bad: out, cells: cells.n}; }"""


def contrast_target_checks(browser, base, ck, index):
    """Text keeps 4.5:1 (3:1 for large text) against what is behind it, including text that is faded by opacity, and every control is a
    target of at least 24 by 24 px (WCAG 2.5.8; links inside running text are exempt). The one declared exception is the census grid of
    compiler versions: a dense grid of 14 px cells with one tab stop and the arrow keys, whose every cell is also a row of the table behind it."""
    print("== ux: contrast and target size")
    for name, rel, w_ in (("main page", "", 1280), ("main page", "", 390), ("details page", "details.html", 1280), ("details page", "details.html", 390)):
        pg = browser.new_page(viewport={"width": w_, "height": 900})
        pg.goto(base + rel, wait_until="networkidle")
        (wait_ready if not rel else wait_details)(pg)
        pg.wait_for_timeout(1500)
        c = pg.evaluate(_CONTRAST_JS)
        ck.ok(c["checked"] > 300 and not c["bad"], f"{name} at {w_} px: each of the {c['checked']} pieces of text passes 4.5:1 (3:1 when large)" + ("" if not c["bad"] else f": below {dict(list(c['bad'].items())[:5])}"))
        t = pg.evaluate(_TARGETS_JS)
        ck.ok(not t["bad"], f"{name} at {w_} px: every control is at least 24 x 24 px (the census grid's {t['cells']} cells are the declared exception)" + ("" if not t["bad"] else f": smaller {dict(list(t['bad'].items())[:5])}"))
        pg.close()


def _static_text(name):
    """The text a reader of the served file sees before any script runs: tags removed (inline ones without a gap), entities
    decoded, scripts and styles dropped, whitespace squashed. The no-script paragraphs are included."""
    with open(os.path.join(SITE, name), encoding="utf-8") as f:
        raw = f.read()
    body = raw[raw.index("<body"):]
    body = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", body, flags=re.S)
    body = re.sub(r"</?(?:span|b|em|i|code|a|strong|sub|sup|abbr|mark|kbd|output)\b[^>]*>", "", body)
    return _squash(html.unescape(re.sub(r"<[^>]+>", " ", body)))


def _head_meta(name):
    """{key: content} of the <meta> tags (by property or name) and the <link rel=canonical> of a served page."""
    with open(os.path.join(SITE, name), encoding="utf-8") as f:
        head = f.read().split("</head>")[0]
    out = {m.group(1): html.unescape(m.group(2)) for m in re.finditer(r'<meta (?:property|name)="([^"]+)" content="([^"]*)"', head)}
    can = re.search(r'<link rel="canonical" href="([^"]+)"', head)
    out["canonical"] = can.group(1) if can else None
    return out


def pinned_text_checks(browser, base, ck, index):
    """The sentences the page's claims rest on, and the numbers typed into them, are pinned to the files they come from. A flipped
    caveat ('neither confirms nor refutes' -> 'confirms'), a swapped scope word ('no profile-guided optimization in the main timing'),
    a verdict word, or a typed number ('0.82 to 1.06', 'at most 2%', 'an 8x loop', '96 functions') no longer passes unseen: each phrase
    below is required word for word in the served text, and every number in one is recomputed from site/data/ or the rule files.
    Change a phrase here together with the page. Also the meta tags and the Google link, which no rendered check reads."""
    print("== pinned text: caveats, scope words, typed numbers, meta tags and the source link")
    idx, det = _static_text("index.html"), _static_text("details.html")
    with open(os.path.join(DATA, "related.json"), encoding="utf-8") as f:
        rel = json.load(f)
    with open(os.path.join(DATA, "realworld.json"), encoding="utf-8") as f:
        rw = json.load(f)
    with open(os.path.join(DATA, "corpus.json"), encoding="utf-8") as f:
        corpus = json.load(f)
    with open(os.path.join(DATA, "versions.json"), encoding="utf-8") as f:
        ver = json.load(f)
    pg = index["page"]
    cr = index["criteria"]
    google = next(x for x in rel["sources"] if x["id"] == "google")
    lines_none = [r["lines_none"] for r in rw["rows"] if not r["control"]]
    libcxx_major = re.search(r"libc\+\+-(\d+)-dev", index["toolchain"]["libcxx_package"]).group(1)
    a35, b30 = (float(x) for x in re.search(r"from ([\d.]+)% to ([\d.]+)%", google["measured"]).groups())
    fwd = f"({fx_py(pg['forward']['aligned']['min'])} to {fx_py(pg['forward']['aligned']['max'])}×)"
    lost_hi = round(pg["lost"]["max"])
    # (page text, phrase, minimum occurrences, why it is pinned)
    pins = [
        (idx, "This study neither confirms nor refutes the average", 1, "the Google verdict sentence"),
        (idx, "No Google service was measured here.", 1, "scope of the Google comparison"),
        (idx, "says the cost stays small without it", 1, "what the Google post says about PGO"),
        (idx, "(an inference, not something this study tested)", 1, "the explanation of the average is labelled an inference"),
        (idx, "a handful of performance-critical code paths still use explicitly unsafe accesses", 1, "the Google post's own caveat"),
        (idx, "no profile-guided optimization in the main timing", 2, "the PGO scope of the main timing"),
        (idx, "by rules written before these runs", 1, "the rule order claim (the public record is stated beside it)"),
        (idx, f"libc++ {libcxx_major}’s vector iterators are not checked in FAST mode", 1, "why std::transform over reverse iterators is unsafe"),
        (idx, "Timed on few jobs (aligned)", 1, "the toolchain table's coverage"),
        (idx, "four 32-bit integers", 1, "what one SSE2 instruction holds"),
        (idx, fwd, 2, f"the forward range of the aligned column in the no-script line and the Result gist (index.json page.forward.aligned)"),
        (idx, f"stayed at most {cr['forward_ci_hi_floor_pct']:g}% above 1× (aligned, interval included)", 1, "Table 1's forward rule (criteria forward_ci_hi_floor_pct)"),
        (idx, f"are left out of the {cr['forward_ci_hi_floor_pct']:g}% test", 1, "Table 1's exemption (criteria forward_ci_hi_floor_pct)"),
        (idx, f"interval above {cr['lost_ci_lo_min_ratio']:g}× in both columns", 1, "Table 1's lost-loop rule (criteria lost_ci_lo_min_ratio)"),
        (idx, f"hold about {round(min(lines_none))} to {round(max(lines_none))}% of the instructions", 1, "the lost loops' instruction share (realworld.json lines_none, programs only)"),
        (idx, f"compiled into {corpus['examples'][0]['count']} functions counts {corpus['examples'][0]['count']} times", 1, "Figure 4's example (corpus.json examples[0].count)"),
        (idx, f"from {a35:.2f}% to {b30:.2f}%", 1, "Google's one-check fix (related.json, the post)"),
        (idx, google["name"], 1, "the Google post's date (related.json)"),
        (idx, f"{lost_hi}× loop", 2, "the heading and the sentence that put the average beside the slowest loop (page.lost.max)"),
        (det, "The mechanism is compile-only.", 1, "the pass-level evidence is compile-only"),
        (det, "the main timing used no profile-guided optimization", 1, "the PGO scope of the main timing"),
    ]
    bad = [(why, ph) for text, ph, n, why in pins if text.count(ph) < n]
    ck.ok(not bad, f"{len(pins)} load-bearing phrases and typed numbers are in the served text, word for word, each recomputed from the data where it states one"
          + ("" if not bad else f" (missing: {'; '.join(f'{ph!r} [{why}]' for why, ph in bad[:3])})"))
    # the same, for sentences that live in the scripts (the per-loop captions, the mechanism text) rather than the HTML
    srcs = {n: open(os.path.join(SITE, n), encoding="utf-8").read() for n in ("race.js", "app.js")}
    mm = ver["summary"]["matmul_main"]["L1"]
    js_pins = [
        ("race.js", "the compiler removes the check altogether", 1, "k01's caption"),
        ("race.js", "the check runs only on the leftover elements", 2, "k02's and k03's captions"),
        ("race.js", "Not vectorized in either build, so there is no SIMD to lose", 2, "k06's and k07's captions"),
        ("race.js", f"keep SIMD yet cost {mm['min']:.1f}× at L1 (EPYC 7763, timed); 23.1 and trunk lose it (compile-only)", 1, "k08's caption (versions.json summary.matmul_main)"),
        ("app.js", "found no iteration count for it (observed)", 1, "the reverse-loop mechanism is observed"),
        ("app.js", "clang vectorized exactly when every exit had a count (observed); that the count is what it needs is inferred", 1, "what the 29 compiled loops show and what they do not"),
        ("app.js", "Clang 19 to 21 price those compares at almost nothing and vectorize the loop (observed); that a change in clang 19 is the reason is inferred", 1, "the newer-clang finding and its inferred cause"),
    ]
    badj = [(why, ph) for f, ph, n, why in js_pins if srcs[f].count(ph) < n]
    ck.ok(not badj and abs(mm["min"] - mm["max"]) < 0.01,
          f"{len(js_pins)} captions and mechanism sentences in race.js and app.js are pinned word for word, the matrix-multiply figure from versions.json ({mm['min']:.2f} to {mm['max']:.2f})"
          + ("" if not badj else f" (missing: {'; '.join(f'{ph!r} [{why}]' for why, ph in badj[:3])})"))
    # meta tags, the Google link and the canonical addresses
    pages_url = "https://" + index["repo"]["base"].split("github.com/")[1].split("/")[0].lower() + ".github.io/" + index["repo"]["base"].rstrip("/").split("/")[-1] + "/"
    mi, md = _head_meta("index.html"), _head_meta("details.html")
    alt_want = f"drawn as {fx_py(pg['lost']['max'])} times as long"
    gl = []
    for n in ("index.html", "details.html"):
        with open(os.path.join(SITE, n), encoding="utf-8") as f:
            gl += re.findall(r'href="(https://security\.googleblog\.com[^"]*)"', f.read())
    ck.ok(f"({fx_py(index['claim']['google_pct'])}%)" in mi["description"]
          and alt_want in mi["og:image:alt"] and alt_want in md["og:image:alt"] and "work in progress" in md["og:image:alt"].lower()
          and mi["og:url"] == pages_url == mi["canonical"] and md["og:url"] == pages_url + "details.html" == md["canonical"]
          and mi["og:image"] == pages_url + "og.png" == md["og:image"] == mi["twitter:image"] == md["twitter:image"]
          and mi["twitter:card"] == md["twitter:card"] == "summary_large_image" and (md["og:image:width"], md["og:image:height"]) == ("1200", "630")
          and google["url"] == index["claim"]["url"] and all(u == google["url"] for u in gl),
          f"meta tags: the description's {fx_py(index['claim']['google_pct'])}% and the share card's '{alt_want}' equal the data; both pages declare their own canonical address "
          f"and share card from the repository name ({pages_url}); every link to the Google post ({len(gl)} in the served HTML) is the address in index.json and related.json")
    # the citation text: a bare % starts a comment in LaTeX, and the figure is the data's
    cp = browser.new_page_plain(viewport={"width": 1280, "height": 900})
    cp.goto(base, wait_until="networkidle")
    wait_ready(cp)
    cite = cp.text_content("#cmd-cite")
    cp.close()
    want_cite = f"Google's {index['claim']['google_pct']:.2f}\\% average}}"
    ck.ok(want_cite in cite and not re.search(r"(?<!\\)%", cite) and cite.count("{") == cite.count("}"),
          f"the BibTeX text escapes the percent sign and prints the data's figure ({want_cite!r})")
    # the matrix-multiply account on the details page types the compiler's own cost numbers; they come from the saved compiler logs
    mmd = os.path.join(REPO, "investigate", "vectorizer", "matmul")
    with open(os.path.join(mmd, "derived", "tables.md"), encoding="utf-8") as f:
        tab_a = f.read().split("## B.")[0]
    with open(os.path.join(mmd, "derived", "cost-table.md"), encoding="utf-8") as f:
        ctab = f.read()
    with open(os.path.join(mmd, "README.md"), encoding="utf-8") as f:
        mm_readme = f.read()
    rows_a = {}
    for ln in tab_a.splitlines():
        cells = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(cells) == 10 and re.match(r"(?:\d+\.\d+\.\d+|trunk)$", cells[0]):
            rows_a[cells[0]] = cells
    sec18 = re.search(r"^## clang 18\.1\.0 .*?(?=^## |\Z)", ctab, flags=re.M | re.S).group(0)
    cmp18 = {int(x) for x in re.findall(r"`%cmp\.i\d+ = icmp [^`]*` \| 1 \| (\d+) \|", sec18)}
    sums18 = re.search(r"\*\*sum\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\*", sec18)
    tgt = {k: int(re.search(rf"\| {re.escape(k)} \| (\d+) \|", mm_readme).group(1)) for k in ("`x86-64` (SSE2)", "`x86-64-v2` (SSE4.2)", "`x86-64-v3` (AVX2)")}
    unit, v2u, v3u = list(tgt.values())
    scalar, vec4 = int(sums18.group(1)), int(sums18.group(2))
    uni = {v: rows_a.get(v, [""] * 10) for v in ("19.1.0", "20.1.0", "21.1.0")}
    mm_want = [
        f"prices each of the two bounds-check compares at {unit} units at width 4, which puts the four-wide loop at {vec4} units against {4 * scalar} for four scalar iterations",
        f"{unit} at the baseline, {v2u} with SSE4.2, {v3u} with AVX2",
        "Clang 19 to 21 find the exit compares uniform, price each at 1 and vectorize the loop",
        "Clang 22 vectorizes it by another route; clang 23.1 and trunk reject it again as an early-exit loop with stores",
    ]
    mm_ok = (cmp18 == {unit} and rows_a.get("18.1.0", [""] * 10)[7] == f"{unit}/{unit}" and rows_a["18.1.0"][3].startswith("not vectorized")
             and all(r[7] == "1/1" and r[8] == "yes" and r[3].startswith("vectorized") for r in uni.values())
             and rows_a["22.1.0"][3].startswith("vectorized") and rows_a["23.1.0"][3].startswith("not vectorized") and rows_a["trunk"][3].startswith("not vectorized"))
    miss = [w for w in mm_want if w not in det]
    ck.ok(mm_ok and not miss, f"details, matrix-multiply account: the cost numbers typed into it ({unit} units per compare at width 4, {vec4} against {4 * scalar}, {unit}/{v2u}/{v3u} by target, 1 on clang 19 to 21) "
          f"and the per-version outcomes equal the saved compiler logs (derived/tables.md, cost-table.md, README F6)" + ("" if not miss else f" (missing: {miss[0]!r})"))
    # the job counts typed into the real-programs caveat are the pooled timing groups'
    gj = [g["jobs"] for g in rw["timing"]["groups"]]
    want_jobs = f"three AMD CPU models ({gj[0]}, {gj[1]} and {gj[2]} jobs;"
    ck.ok(len(gj) == 3 and want_jobs in det and all(g["enough"] for g in rw["timing"]["groups"]),
          f"details, caveats: the real-programs job counts per CPU model ({gj[0]}, {gj[1]}, {gj[2]}) equal realworld.json timing.groups")
    # the GCC version typed into the toolchain sentence is the one the sibling variants are named after
    with open(os.path.join(DATA, "siblings.json"), encoding="utf-8") as f:
        sib_txt = f.read()
    gcc_major = sorted({m.group(1) for m in re.finditer(r'"label": "GCC (\d+) -O[23], assertions"', sib_txt)})
    ck.ok(len(gcc_major) == 1 and f"GCC {gcc_major[0]} with assertions costs up to" in idx,
          f"section 6, toolchain sentence: the GCC major version typed in it ({gcc_major}) is the one in siblings.json's variant labels")
    # the footer note on both pages is a claim about the network: each page asks only its own host and the two font hosts
    from urllib.parse import urlparse
    font_note = "The pages load two typefaces from Google Fonts, so Google sees each visit; they make no other third-party request."
    seen = {}
    for name in ("index.html", "details.html"):
        np_ = browser.new_page_plain(viewport={"width": 1280, "height": 900})
        got = set()
        np_.on("request", lambda r, got=got: got.add(urlparse(r.url).netloc))
        np_.goto(base + name, wait_until="networkidle")
        if name == "index.html":
            wait_ready(np_)
            np_.click('#rows [data-k="k04_rev"]')
        else:
            wait_details(np_)
        np_.wait_for_timeout(600)
        seen[name] = {h for h in got if h}
        np_.close()
    own = urlparse(base).netloc
    extra = {n: sorted(h - {own, "fonts.googleapis.com", "fonts.gstatic.com"}) for n, h in seen.items()}
    ck.ok(idx.count(font_note) == 1 and det.count(font_note) == 1 and not any(extra.values()),
          f"both footers say the pages load two typefaces from Google Fonts and make no other third-party request; each page, loaded and used, asks only its own host and the font hosts"
          + ("" if not any(extra.values()) else f" (other hosts: {extra})"))


BAKED_NAMES = ["googlePct", "clang", "lostMin", "lostMax", "avx2Short", "intelRange", "c2Lost", "c2Vec", "fixMin", "fixMax", "rwSlowMin", "rwSlowMax",
               "jobsPerRun", "nRuns", "minJobs", "nJobs"]
# the one baked span that stays empty on purpose: the main page's headline line sits in the hero block, which is changed in its own files
BAKED_EMPTY_OK = {("intelRange", "headline")}
_SPANS_JS = """(names) => [...document.querySelectorAll('[data-v]')].filter(e => names.includes(e.dataset.v) && !e.closest('noscript'))
    .map(e => [e.dataset.v, e.textContent.trim(), (e.closest('[id]') || {}).id || ''])"""
_CLS_JS = """() => { window.__cls = 0; window.__shifts = [];
  new PerformanceObserver(l => { for (const e of l.getEntries()) { if (e.hadRecentInput) continue; window.__cls += e.value; window.__shifts.push(e.value); } }).observe({type: 'layout-shift', buffered: true}); }"""


def layout_stability_checks(browser, base, ck, index):
    """The page does not jump while it fills in. (1) The numbers that sit in the first screens are in the served HTML, and the script
    writes back the same text: a span that starts empty and ends up four words long moves every line after it. (2) The details page, cold,
    on a throttled CPU and without web fonts, shifts by less than 0.1 in total (the CLS threshold for 'good') at three widths."""
    print("== layout stability: baked numbers equal the rendered ones, and the details page does not jump")
    for name, ready in (("", wait_ready), ("details.html", wait_details)):
        off = browser.new_context(java_script_enabled=False).new_page()
        off.goto(base + name, wait_until="load")
        baked = off.evaluate(_SPANS_JS, BAKED_NAMES)
        off.close()
        on = browser.new_context().new_page()
        on.goto(base + name, wait_until="networkidle")
        ready(on)
        on.wait_for_timeout(500)
        shown = on.evaluate(_SPANS_JS, BAKED_NAMES)
        on.close()
        bad = [(b, s) for b, s in zip(baked, shown) if b[1] != s[1] and not (b[1] == "" and (b[0], b[2]) in BAKED_EMPTY_OK)]
        ck.ok(len(baked) == len(shown) >= 10 and not bad and sum(1 for b in baked if b[1]) >= 10,
              f"{name or 'index.html'}: the {len(baked)} numeric spans in the first screens and sections ({', '.join(BAKED_NAMES[:5])}, ...) carry the shown text in the served HTML"
              f"{'' if not bad else ' (differ: ' + '; '.join(f'{b[0]} in #{b[2]} is {b[1]!r}, shown {s[1]!r}' for b, s in bad[:4]) + ')'}")
    for w, h in ((1440, 900), (768, 1024), (390, 844)):
        ctx = browser.new_context(viewport={"width": w, "height": h})
        ctx.route(re.compile(r"https://fonts\.(googleapis|gstatic)\.com/"), lambda route: route.abort())
        pg = ctx.new_page()
        pg.add_init_script("(" + _CLS_JS + ")()")
        ctx.new_cdp_session(pg).send("Emulation.setCPUThrottlingRate", {"rate": 4})
        pg.goto(base + "details.html", wait_until="networkidle")
        wait_details(pg)
        pg.wait_for_timeout(2000)
        cls, n = pg.evaluate("[window.__cls, window.__shifts.length]")
        ctx.close()
        ck.ok(cls < 0.1, f"details page at {w}x{h}, cold, CPU 4x slower, no web fonts: layout shift {cls:.3f} in {n} shifts (under 0.1)")


def ref_link_checks(browser, base, ck, index):
    """A link to a reference or its citation (index.html#ref-queue, #cite-queue) lands on first load, with the section that holds it
    open: the reference list and the related-work table are built by the script after the browser has made its first jump, and
    the script that follows the hash runs before they exist. Run with scroll anchoring off, as in Chromium on the Linux runner."""
    print("== reference links: #ref-... and #cite-... land on a fresh load")
    no_anchor = "document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = '*{overflow-anchor:none !important}'; document.head.append(s); })"
    probe = """(f) => { const t = document.getElementById(f); if (!t) return null; const r = t.getBoundingClientRect();
      const e = document.elementFromPoint(Math.min(innerWidth - 2, r.left + Math.min(r.width, 40) / 2), r.top + Math.min(r.height, 20) / 2);
      return {top: Math.round(r.top), h: Math.round(r.height), shown: !!e && t.contains(e)}; }"""
    for w, h in ((1440, 900), (390, 844)):
        got = {}
        for frag in ("ref-queue", "cite-queue", "ref-google", "cite-google"):
            ctx = browser.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            pg.add_init_script(no_anchor)
            pg.goto(base + "#" + frag, wait_until="networkidle")
            wait_ready(pg)
            pg.wait_for_timeout(900)
            got[frag] = pg.evaluate(probe, frag)
            ctx.close()
        bad = {f: r for f, r in got.items() if not r or not r["shown"] or not (0 <= r["top"] < h * 0.6)}
        ck.ok(not bad, f"index.html#ref-... and #cite-... land on a fresh load at {w}x{h}, the target visible in the top of the window ({got})")


def live_region_checks(browser, base, ck, index):
    """Screen readers read a polite live region whole each time it changes. Figure 2 used to be one (about 4,000 characters per
    selection); now a one-line region announces the selected loop's headline and a pointer preview is not announced. No live
    region on the main page holds more than 600 characters."""
    print("== live regions: Figure 2 announces one line, none is long")
    pg = browser.new_page_plain(viewport={"width": 1440, "height": 900})
    pg.goto(base, wait_until="networkidle")
    wait_ready(pg)
    pg.wait_for_function("document.querySelectorAll('#rows [data-k]').length === 8", timeout=15000)
    pg.click('#rows [data-k="k04_rev"]')
    pg.wait_for_function("document.querySelector('#fig2-body .f2-big')", timeout=15000)
    pg.wait_for_function("!document.querySelector('#fig2-body .f2-why.muted')", timeout=20000)
    got = pg.evaluate("""() => ({live: document.getElementById('fig2-live').textContent, big: document.querySelector('#fig2-body .f2-big').textContent,
        name: document.querySelector('#fig2-body .f2-head').childNodes[0].textContent, cpu: document.querySelector('#fig2-body .f2-cpu .nw').textContent,
        fig2Live: document.getElementById('fig2').hasAttribute('aria-live'), inside: !!document.querySelector('#fig2 [aria-live]:not(#fig2-live)'),
        longest: Math.max(...[...document.querySelectorAll('[aria-live]:not([aria-live=off]), [role=status], [role=alert]')].map(e => e.textContent.trim().length))})""")
    want = f"{got['name']}: {got['big']} as long with the check on, at the smallest data size, {got['cpu']}. The machine code is below."
    before = got["live"]
    pg.hover('#rows [data-k="k08_matmul"]')
    pg.wait_for_timeout(700)
    after = pg.evaluate("document.getElementById('fig2-live').textContent")
    pg.close()
    ck.ok(got["live"] == want and not got["fig2Live"] and not got["inside"] and after == before and got["longest"] <= 600,
          f"Figure 2 is not a live region; its one-line announcement is the headline ({got['live']!r}), a pointer preview changes nothing, and the longest live region on the page has {got['longest']} characters (at most 600)")


def print_checks(browser, base, ck, index):
    """A printed copy (or a PDF) has the text of the page, not only what the reader had opened. Folded sections and closed
    <details> blocks print as if open, and the buttons that open them do not print. Fresh load, nothing opened, print media.
    The closed blocks are listed on screen first (only those the page shows at all: Figure 2's listing is not on a narrow page until
    a row is tapped) and each one's longest line of text must then be in the printed text."""
    print("== print: folded sections and closed details print their text")
    collect = """() => {
        const norm = (s) => s.replace(/\\s+/g, ' ').trim();
        const out = [];
        for (const d of document.querySelectorAll('details:not([open])')) {
            if (!d.checkVisibility()) continue;
            let best = '';
            const w = document.createTreeWalker(d, NodeFilter.SHOW_TEXT);
            for (let n = w.nextNode(); n; n = w.nextNode()) {
                const p = n.parentElement;
                if (!p || p.closest('summary, .scroll-hint, script, style, [hidden]')) continue;
                let shown = true;
                for (let e = p; e && e !== d; e = e.parentElement) if (getComputedStyle(e).display === 'none') { shown = false; break; }
                const t = norm(n.textContent);
                if (shown && t.length > best.length) best = t;
            }
            if (best.length >= 30) out.push(best.slice(0, 40));
        }
        return out;
    }"""
    probe = """(heads) => {
        const norm = (s) => s.replace(/\\s+/g, ' ').trim();
        const all = norm(document.body.innerText);
        const bodies = [...document.querySelectorAll('.sec-body')];
        const miss = heads.filter(t => !all.includes(t));
        const buttons = [...document.querySelectorAll('.sec-more')].filter(b => getComputedStyle(b).display !== 'none');
        return {bodies: bodies.length, hiddenBodies: bodies.filter(b => getComputedStyle(b).display === 'none').length,
                missing: miss.slice(0, 2), missingN: miss.length, buttons: buttons.length};
    }"""
    for name in ("index.html", "details.html"):
        pg = browser.new_page_plain(viewport={"width": 794, "height": 1123})
        pg.goto(base + name, wait_until="networkidle")
        if name == "index.html":
            pg.wait_for_function("document.querySelectorAll('#rows .row').length > 0", timeout=20000)
            pg.wait_for_function(FIG2_READY, timeout=10000)
        else:
            wait_details(pg)
        pg.wait_for_timeout(500)
        heads = pg.evaluate(collect)
        pg.emulate_media(media="print")
        pg.wait_for_timeout(300)
        r = pg.evaluate(probe, heads)
        pg.close()
        ck.ok(r["hiddenBodies"] == 0 and r["buttons"] == 0 and r["missingN"] == 0 and len(heads) >= 3 and (name == "details.html" or r["bodies"] >= 10),
              f"{name}, print media from a fresh load: {r['bodies']} folded section bodies, {r['hiddenBodies']} hidden; {r['buttons']} Details buttons print; "
              f"{len(heads) - r['missingN']} of {len(heads)} closed details blocks print their text" + ("" if not r["missingN"] else f" (missing: {r['missing']})"))


def ux_checks(browser, base, ck, index):
    print_checks(browser, base, ck, index)
    layout_stability_checks(browser, base, ck, index)
    ref_link_checks(browser, base, ck, index)
    live_region_checks(browser, base, ck, index)
    nav_checks(browser, base, ck, index)
    contrast_target_checks(browser, base, ck, index)
    names_checks(browser, base, ck, index)
    textsize_checks(browser, base, ck, index)
    forced_colors_checks(browser, base, ck, index)
    tooltip_checks(browser, base, ck, index)
    dialog_checks(browser, base, ck, index)


FOCUSED = {"provenance": provenance_checks, "claims": claims_scope_checks, "pages": pages_workflow_checks, "access": access_checks, "placement": placement_scope_checks, "ux": ux_checks, "stability": layout_stability_checks, "text": pinned_text_checks, "refs": ref_link_checks, "live": live_region_checks, "print": print_checks}  # check groups that take (browser, base, ck, index) and can run alone with --only


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # messages may quote page text
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default=None, help="folder for the screenshots (default: a temporary folder)")
    ap.add_argument("--quick", action="store_true", help="select every row on the default CPU model only")
    ap.add_argument("--arm-only", action="store_true", help="run only the Arm column's checks (to iterate on section 6a and 6d; the full run is the one that counts)")
    ap.add_argument("--only", action="append", default=[], choices=sorted(FOCUSED),
                    help="run only the named focused check group(s) (to iterate; the full run is the one that counts)")
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
            mode = os.environ.get("SITE_CHECK_FONTS", "auto").lower()
            if mode not in ("auto", "online", "offline"):
                print(f"   FAIL SITE_CHECK_FONTS must be auto, online or offline, not {mode!r}")
                return 2
            block = mode == "offline" or (mode == "auto" and not fonts_reachable())
            global FONTS_BLOCKED
            FONTS_BLOCKED = block
            print(f"== fonts: SITE_CHECK_FONTS={mode}; " + ("the font requests are answered locally (no network, system fonts): line wraps can differ from a run with the fonts"
                                                          if block else "the pages load their fonts from Google Fonts"))
            if block:
                block_font_hosts(browser)
            browser.new_page_plain = browser.new_page
            browser.new_page = lambda **kw: (lambda pg: (pg.add_init_script("window.__OPEN_ALL__ = true"), pg)[1])(browser.new_page_plain(**kw))
            if a.only:
                try:
                    for name in a.only:
                        FOCUSED[name](browser, base, ck, index)
                finally:
                    browser.close()
                print("FOCUSED CHECKS PASSED (not the full run)" if not ck.failures else f"FOCUSED CHECKS FAILED ({len(ck.failures)})")
                return 0 if not ck.failures else 1
            if a.arm_only:
                try:
                    arm_checks(browser, base, ck, index, allowed, saved, shots)
                    replication_checks(browser, base, ck, index, allowed, saved, shots)
                    dsweep_checks(browser, base, ck, index, allowed, saved, shots)
                finally:
                    browser.close()
                for s in saved:
                    print(f"   {s}")
                print("ARM CHECKS PASSED (not the full run)" if not ck.failures else f"ARM CHECKS FAILED ({len(ck.failures)})")
                return 0 if not ck.failures else 1
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
                # the note names the models with too few jobs; when every model drawn had enough jobs it is empty
                few_note = (all(f["cpu_short"] in few for f in index["page"]["cpus_few"]) and "too few to judge" in few
                            and page.evaluate("getComputedStyle(document.getElementById('cpu-few')).display") == "block"
                            and not page.evaluate("getComputedStyle(document.getElementById('cpu-few')).borderTopStyle !== 'none'")
                            ) if index["page"]["cpus_few"] else few.strip() == ""
                ck.ok(seg == [c["slug"] for c in cpus] and few_note,
                      f"Figure 1: the switcher offers the CPU models with at least {index['criteria']['minimum_jobs']} jobs ({seg}) and names the others as too few jobs (none left out: an empty note)")
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
                      and index["pooled"]["source"] in dp.inner_text("#appendix-b")
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
                check_derived_wording(ck, page, dp, index, pooled, cpus, t1r, rec)
                low = dp.inner_text("#fwd-low")
                # judged forward cells (not placement-sensitive) clearly below 1x aligned, on the models with enough jobs (the page lists these)
                low_cells = [(c["cpu_short"], x["cell_id"]) for c in cpus
                             for x in next(q for q in pooled["cpus"] if q["cpu_model"] == c["cpu_model"])["cells"]
                             if x["class"] == "kept" and x["size_class"] in ("L1", "L2")
                             and x["cell_id"] not in {q["cell_id"] for q in c["placement_sensitive"]} and x["aligned"]["ratio"] < 0.95]
                ck.ok((all(name in low for name, _ in low_cells) and "includes 1" in low and "slowdowns only" in low) if low_cells else low.strip() == "",
                      "beside Table 1: a judged forward loop clearly below 1x is explained (interval of compiled / aligned includes 1; the rule bounds slowdowns only); with none, there is no note")
                ip = dp.inner_text("#instr-p")
                ck.ok("not for every loop" in ip and "inferred" in ip and "same story" not in ip and "histogram" in ip,
                      "section 1: the instruction counts are said to agree for loops that lose SIMD, not for every loop, with the histogram and forward add as counter-examples, marked inferred")
                norm_ = lambda m: m.replace("Xeon Platinum ", "Xeon ")  # noqa: E731
                with open(os.path.join(DATA, "siblings.json"), encoding="utf-8") as f_:
                    sib_other = [m for m in (norm_(x) for x in json.load(f_)["cpus"]) if m not in [c["cpu_short"] for c in cpus]]
                prog_other = sorted({norm_(r["cpu_short"]) for r in index["programs"]["rows"]} - {c["cpu_short"] for c in cpus} - set(sib_other))
                sib_cap, other_draws = dp.inner_text("#sib-cap"), dp.inner_text("#otherdraws")
                ck.ok(all(w in dp.inner_text("#jobsets") for w in ("Section 5", "Section 6", "aligned", "as compiled"))
                      and (all(m in sib_cap for m in sib_other) if sib_other else "the same CPU models as Table 1" in sib_cap)
                      and all(m in other_draws for m in sib_other + prog_other),
                      "results: one note states which job set and column each part uses; Table 4's caption names the draws beyond Table 1 (or says it has the same models); the note beside Table 1 names every model without a row")
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
                ck.ok(f"Compiled only: the {CE_VER} compiler versions ({ce['counts']['compilers']} Compiler Explorer compiler ids) in section 6" in cbox and "the other setups on few jobs" in cbox and "Other compilers" in abstract and "compiled only" in abstract,
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
                f2t = page.inner_text("#fig2")
                ck.ok("no iteration count" in f2t and "second way out" in f2t and "(observed)" in f2t and "inferred" in f2t
                      and page.locator('#fig2 a[href="details.html#passlevel"]').count() >= 1,
                      "Figure 2: the compiler's remark explained in plain words (a second way out with no iteration count), the facts labelled observed or inferred, linked to the pass-level evidence")
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
                ck.ok(f"Of the {len(T['expect'])} expectations committed before any run (in the author’s unpublished development history), {len(held)} held" in ex and all(m_["row"] and f"{m_['fast']:.3f}" in ex for m_ in miss),
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
                # the note names the models with too few jobs; when every model drawn had enough jobs it is empty
                few_note = (all(f["cpu_short"] in few for f in index["page"]["cpus_few"]) and "too few to judge" in few
                            and page.evaluate("getComputedStyle(document.getElementById('cpu-few')).display") == "block"
                            and not page.evaluate("getComputedStyle(document.getElementById('cpu-few')).borderTopStyle !== 'none'")
                            ) if index["page"]["cpus_few"] else few.strip() == ""
                ck.ok(seg == [c["slug"] for c in cpus] and few_note,
                      f"Figure 1: the switcher offers the CPU models with at least {index['criteria']['minimum_jobs']} jobs ({seg}) and names the others as too few jobs (none left out: an empty note)")
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
                      and index["pooled"]["source"] in dp.inner_text("#appendix-b")
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
                check_derived_wording(ck, page, dp, index, pooled, cpus, t1r, rec)
                low = dp.inner_text("#fwd-low")
                # judged forward cells (not placement-sensitive) clearly below 1x aligned, on the models with enough jobs (the page lists these)
                low_cells = [(c["cpu_short"], x["cell_id"]) for c in cpus
                             for x in next(q for q in pooled["cpus"] if q["cpu_model"] == c["cpu_model"])["cells"]
                             if x["class"] == "kept" and x["size_class"] in ("L1", "L2")
                             and x["cell_id"] not in {q["cell_id"] for q in c["placement_sensitive"]} and x["aligned"]["ratio"] < 0.95]
                ck.ok((all(name in low for name, _ in low_cells) and "includes 1" in low and "slowdowns only" in low) if low_cells else low.strip() == "",
                      "beside Table 1: a judged forward loop clearly below 1x is explained (interval of compiled / aligned includes 1; the rule bounds slowdowns only); with none, there is no note")
                ip = dp.inner_text("#instr-p")
                ck.ok("not for every loop" in ip and "inferred" in ip and "same story" not in ip and "histogram" in ip,
                      "section 1: the instruction counts are said to agree for loops that lose SIMD, not for every loop, with the histogram and forward add as counter-examples, marked inferred")
                norm_ = lambda m: m.replace("Xeon Platinum ", "Xeon ")  # noqa: E731
                with open(os.path.join(DATA, "siblings.json"), encoding="utf-8") as f_:
                    sib_other = [m for m in (norm_(x) for x in json.load(f_)["cpus"]) if m not in [c["cpu_short"] for c in cpus]]
                prog_other = sorted({norm_(r["cpu_short"]) for r in index["programs"]["rows"]} - {c["cpu_short"] for c in cpus} - set(sib_other))
                sib_cap, other_draws = dp.inner_text("#sib-cap"), dp.inner_text("#otherdraws")
                ck.ok(all(w in dp.inner_text("#jobsets") for w in ("Section 5", "Section 6", "aligned", "as compiled"))
                      and (all(m in sib_cap for m in sib_other) if sib_other else "the same CPU models as Table 1" in sib_cap)
                      and all(m in other_draws for m in sib_other + prog_other),
                      "results: one note states which job set and column each part uses; Table 4's caption names the draws beyond Table 1 (or says it has the same models); the note beside Table 1 names every model without a row")
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
                ck.ok(f"Compiled only: the {CE_VER} compiler versions ({ce['counts']['compilers']} Compiler Explorer compiler ids) in section 6" in cbox and "the other setups on few jobs" in cbox and "Other compilers" in abstract and "compiled only" in abstract,
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
                f2t = page.inner_text("#fig2")
                ck.ok("no iteration count" in f2t and "second way out" in f2t and "(observed)" in f2t and "inferred" in f2t
                      and page.locator('#fig2 a[href="details.html#passlevel"]').count() >= 1,
                      "Figure 2: the compiler's remark explained in plain words (a second way out with no iteration count), the facts labelled observed or inferred, linked to the pass-level evidence")
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
                ck.ok(f"Of the {len(T['expect'])} expectations committed before any run (in the author’s unpublished development history), {len(held)} held" in ex and all(m_["row"] and f"{m_['fast']:.3f}" in ex for m_ in miss),
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
                dall_targets = dp.evaluate("[...document.querySelectorAll('#dall .dall-list a')].map(a => [a.textContent.trim(), !!document.querySelector(a.getAttribute('href'))])")
                dall_hrefs = dp.evaluate("[...document.querySelectorAll('#dall .dall-list a')].map(a => a.getAttribute('href'))")
                dall_want = ["#result-full", "#why-full", "#placement-full", "#layout-full", "#census-full", "#mitigate-full", "#siblings-full", "#arm-full", "#realworld-full",
                             "#pgo-full", "#programs-full", "#method-full", "#related-full", "#appendix-a", "#appendix-b", "#appendix-c", "#appendix-d"]
                byl, purp = dp.inner_text(".front .byline"), dp.inner_text("#details-purpose")
                crumb = dp.evaluate("(() => { const c = document.querySelector('.front .crumb'), h = document.querySelector('.front h1'); return c && h ? [c.getAttribute('href'), c.textContent.trim(), !!(c.compareDocumentPosition(h) & Node.DOCUMENT_POSITION_FOLLOWING)] : null; })()")
                lost_kernels = sorted({c_["cell_id"].split(".")[0] for cpu_ in pooled["cpus"] for c_ in cpu_["cells"] if c_["class"] == "lost"})
                clang_dp = "clang " + re.search(r"\d+\.\d+\.\d+", index["toolchain"]["clang"]).group(0)
                intel_dp = f"{index['intel_forward']['aligned']['min']:.2f}–{index['intel_forward']['aligned']['max']:.2f}"
                avx_dp = dp.text_content('#details-purpose span[data-v="avx2Short"]').strip()
                jump_dp = dp.evaluate("[...document.querySelectorAll('.dnav a:not(.dgo)')].map(a => [a.textContent.trim(), a.getAttribute('href'), !!document.querySelector(a.getAttribute('href'))])")
                dall_lab = dp.evaluate("Object.fromEntries([...document.querySelectorAll('#dall .dall-list a')].map(a => [a.getAttribute('href'), a.textContent.trim()]))")
                h2_of = dp.evaluate("Object.fromEntries(['#placement-full', '#realworld-full', '#method-full', '#appendix-a'].map(q_ => [q_, document.querySelector(q_ + ' h2').textContent.trim()]))")
                dgo_txt, res_h2 = dp.inner_text(".dnav a.dgo").strip(), dp.evaluate("document.querySelector('#result-full h2').lastChild.textContent.trim()")
                ck.ok(
                      # what the page holds, for whom, and the setting it is about; the main page is a breadcrumb above the title, said in words
                      "holds the full tables, runs and checks of a study of what bounds checks in C++’s standard library cost, loop by loop, for C++ engineers deciding whether to turn on libc++ hardening." in byl
                      and "not needed to follow the result" not in byl + purp and "work in progress" in byl.lower()
                      and crumb and crumb[0] == "index.html" and crumb[1].startswith("←") and "Main page" in crumb[1] and "short version" in crumb[1] and crumb[2]
                      and dp.locator('.front .byline a[href="index.html"]').count() == 0 and dp.inner_text("#repo-link") == "Code and data on GitHub"
                      # the box: Google's figure and why the title says it come first, then the numbers from the data, in words a reader follows
                      and f"Google reported that libc++’s bounds checks cost {index['claim']['google_pct']:.2f}% on average over whole services, a third of a percent: the title." in purp
                      and "This study times single loops, a different measurement. The cost depends on the loop." in purp and "neither confirms nor contradicts" not in purp
                      and f"{lost['min']:.1f}× to {lost['max']:.1f}× as long at the study’s two in-cache sizes, with the bounds check on as with it off, for reverse, stride-2 and matrix-multiply loops, which also stop running several elements per instruction." in purp
                      and purp.index("Google reported") < purp.index(f"{lost['min']:.1f}×") and "SIMD" not in purp
                      and lost_kernels == ["k04_rev", "k05_stride2", "k08_matmul"]
                      and f"on arrays that fit the processor’s cache ({clang_dp}, -O2):" in purp
                      and f"About the same, near 1×, for forward loops on the AMD CPU models (one AVX2 exception, {avx_dp}×); {intel_dp}× on Intel (forward add; section 1)." in purp
                      and avx_dp == page.text_content('#result .gist span[data-v="avx2Short"]').strip()
                      # one filled start link that says what it does (not the heading below it), four plain jumps with targets, the fold
                      and dgo_txt.startswith("Read the full numbers") and dgo_txt not in res_h2 and res_h2.strip() not in dgo_txt
                      and [(j[0], j[1]) for j in jump_dp] == [("Code placement", "#placement-full"), ("Real programs", "#realworld-full"), ("How it was measured", "#method-full"), ("Full data table", "#appendix-a")] and all(j[2] for j in jump_dp)
                      and dp.inner_text(".dnav .dlabel") == "or jump to"
                      and dall_hrefs == dall_want and all(t[1] for t in dall_targets) and all(f"{L}: " in dp.text_content("#dall .dall-list") for L in "ABCD")
                      and dp.get_attribute(".dnav a.dgo", "href") == "#result-full" and dp.locator(".dnav a").count() == 5
                      # one vocabulary: the fold's entry and the section's heading for each jump use the jump row's words
                      and all(dall_lab[j[1]].lower().endswith(j[0].lower()) and j[0].lower() in h2_of[j[1]].lower() for j in jump_dp),
                      "details page: the first screen says what the study holds and for whom (and the setting it is about), has the main page as a breadcrumb above the title (short version, interactive chart), opens the box with Google's figure and why the title says it, then the result in words (1x as long with the check on as off for reverse, stride-2 and matrix-multiply loops; about the same for forward loops on the AMD models with the AVX2 exception, and the Intel forward-add range, as the main page's headline gives it; arrays that fit the cache; the toolchain named) with every number from the data and no unexplained SIMD, offers one start link that is not the heading below it and four plain jumps with targets, and 'All sections' lists the 17 sections and appendices A to D in page order, each with a target on the page, and the jump row, the fold and the section headings use the same words for the four jumps (Code placement, Real programs, How it was measured, Full data table)")
                # the headline above Figure 1 and the 'cannot tell you' box under the abstract
                page.evaluate("scrollTo(0, 0)"); page.wait_for_timeout(150)
                hl = page.inner_text("#headline")
                hb = page.evaluate("(() => { const r = document.getElementById('headline').getBoundingClientRect(), f = document.getElementById('fig1').getBoundingClientRect(); return [r.bottom <= f.top + 1, true]; })()")
                ck.ok(f"take {lost['min']:.1f}× to {lost['max']:.1f}× as long at the study’s two in-cache sizes" in hl and "Loops that lose SIMD under the check" in hl
                      and f"{IFd['aligned']['min']:.2f}–{IFd['aligned']['max']:.2f}× on Intel (forward add)" in hl and "near 1× on the AMD models" in hl and all(hb),
                      f"one headline line sits directly above Figure 1 (the hero holds the first screen), from index.json, with the AMD and Intel qualifier ({hb})")
                # the same range, scoped to the study's sizes, wherever else the main page states it: the no-script line, the abstract bullet and the Result gist
                ns_txt = page.evaluate("[...document.querySelectorAll('noscript')].map(n => n.textContent).join(' ')")
                abs_txt = page.evaluate("[...document.querySelectorAll('li')].map(l => l.textContent.replace(/\\s+/g, ' '))")
                gist_txt = " ".join(page.text_content("#result .gist").split())
                ck.ok("times as long at the study’s two in-cache sizes" in ns_txt
                      and any(f"{lost['min']:.1f} to {lost['max']:.1f}× as long at the study’s two in-cache sizes for loops that lose SIMD" in t for t in abs_txt)
                      and f"{lost['min']:.1f} to {lost['max']:.1f}× as long at the study’s sizes;" in gist_txt,
                      "the headline range is scoped to the study's sizes in the no-script line, the abstract bullet and the Result gist, as in the headline and the details box")
                cb = page.evaluate("[...document.querySelectorAll('#cannot li')].map(l => l.innerText)")
                ck.ok(len(cb) == 5 and "robustness report" in cb[3] and "jobs started returned nothing" in cb[4] and "production average" in cb[0] and "picked for their lost loops" in cb[1] and "profile-guided optimization" in cb[1] and "not time" in cb[1]
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
                hero_image_checks(browser, base, ck, index)
                phone_checks(browser, base, ck, index)
                wording_checks(browser, base, ck, index)
                provenance_checks(browser, base, ck, index)
                claims_scope_checks(browser, base, ck, index)
                pages_workflow_checks(browser, base, ck, index)
                access_checks(browser, base, ck, index)
                placement_scope_checks(browser, base, ck, index)
                ux_checks(browser, base, ck, index)
                pinned_text_checks(browser, base, ck, index)
                arm_checks(browser, base, ck, index, allowed, saved, shots)
                replication_checks(browser, base, ck, index, allowed, saved, shots)
                dsweep_checks(browser, base, ck, index, allowed, saved, shots)
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
                    for (const e of document.querySelectorAll('#race button, #race select, #race [role=radio], #race [role=switch], #cpu-seg button, #col-seg button, .w-chip, .bar a, .bar button')) {
                      if (e.closest('details:not([open])')) continue; e.scrollIntoView({ block: 'center', behavior: 'instant' }); const q = e.getBoundingClientRect(); if (q.width < 1) continue;
                      const x = q.left + q.width / 2, y = q.top + q.height / 2;
                      const at = (px, py) => { const t = document.elementFromPoint(px, py); return t && (t === e || e.contains(t) || t.closest('button,a,[role=radio],[role=switch]') === e); };
                      if (!(at(x, y - 21) && at(x, y + 21) && (q.width >= 44 || (at(x - 21, y) && at(x + 21, y))))) bad.push((e.textContent || e.id).trim().slice(0, 20) + ' ' + Math.round(q.width) + 'x' + Math.round(q.height));
                    } window.scrollTo({ top: 0, behavior: 'instant' }); return bad; }""")
                ck.ok(not hit, f"390: the hero controls, CPU and column buttons, word chips and bar links answer a tap within 44 x 44 px ({hit[:4]})")
                shot(page, saved, shots, "mobile-1-first-screen.png")
                h = page.evaluate("document.documentElement.scrollHeight")
                # See PHONE_ALL_OPEN_BACKSTOP at the top of this file for the history of this number. The default, collapsed page is the one capped.
                ck.ok(h < PHONE_ALL_OPEN_BACKSTOP, f"390: the main page with every section opened is {h} px long (under the backstop of {PHONE_ALL_OPEN_BACKSTOP}; the default, collapsed page is the one capped, above)")
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
    if FONTS_BLOCKED and ck.failures:
        others = [f for f in ck.failures if not f.startswith(FONT_DEPENDENT_CHECKS)]
        print(f"   system fonts: {len(ck.failures) - len(others)} of the {len(ck.failures)} failures are the checks that need the web fonts (FONT_DEPENDENT_CHECKS)"
              + (", and nothing else failed" if not others else f"; {len(others)} other(s) failed"))
    return 0 if not ck.failures else 1


if __name__ == "__main__":
    sys.exit(main())
