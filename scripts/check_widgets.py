#!/usr/bin/env python3
"""Checks the three interactive widgets in site/widgets/ on the standalone page site/widgets-demo.html.

    python scripts/check_widgets.py [--shots DIR] [--regen]

- site/widgets/placements.json (per-placement ratios the placement widget reads next to data/layout.json)
  must equal a fresh derivation from the analysis files that layout.json lists as its sources
  (--regen rewrites it).
- Serves site/ on a free localhost port and opens the demo page with headless Chromium (muted, no speech) at
  1280 and 390 px wide, each once normally and once with prefers-reduced-motion emulated. On every pass:
  all three widgets mount with no console errors, page errors or failed requests; no horizontal scroll;
  buttons and selects at least 32 px tall at 390.
- placement: for every CPU model, loop and size, the big number equals the data's ratio for the chosen
  placement (3 decimals), each of the four stops shows its own ratio, the four stops are tap targets and the arrow keys are an extra
  and dragging does nothing, the radio groups move with the arrow keys, the caption says the in-between positions are not
  measured and the drawing is schematic.
- mitigation: for every loop shape, rewrite and CPU model, the two range labels equal the data (2 decimals),
  the code panel shows the data's code, the toggle switches it, the belt animates (and is static under
  reduced motion).
- programs: for every CPU model, build column and PGO choice, every row's value equals the data (3 decimals),
  a model or series with too few jobs says so, the tooltip carries the exact numbers (4 decimals) on hover
  and on keyboard focus, sorting orders the rows.
- a failed fetch shows a one-line message (data file blocked) in each widget.
Screenshots go to --shots (default: a temporary folder); their paths are printed.
Exit code 0 only if every check passed. Needs the Python playwright package and its Chromium.
"""
import argparse
import functools
import glob
import http.server
import json
import os
import re
import sys
import tempfile
import threading

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, "site")
DATA = os.path.join(SITE, "data")
SIDE = os.path.join(SITE, "widgets", "placements.json")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def best_cpus(layout):
    """One entry per CPU model, the one with the most jobs (same rule as widgets/placement.js)."""
    best = {}
    for c in layout["cpus"]:
        o = best.get(c["cpu_model"])
        if o is None or c["jobs"] > o["jobs"]:
            best[c["cpu_model"]] = c
    return list(best.values())


def derive_sidecar():
    layout = load(os.path.join(DATA, "layout.json"))
    cells = {}
    for c in best_cpus(layout):
        found = None
        for src in layout["sources"]:
            d = load(os.path.join(REPO, src))
            for b in d["cpus"]:
                if b["cpu_model"] == c["cpu_model"] and b["jobs"] == c["jobs"] and list(b["runs"]) == list(c["runs"]):
                    found = b
        if found is None:
            continue
        for cell in found["cells"]:
            key = f"{c['cpu_model']}|{c['jobs']}|{cell['kernel']}|{cell['size_class']}"
            cells[key] = {pid: {"ratio": v["ratio"], "ci95": v["ci95"], "fast_start_mod64": v["fast_start_mod64"],
                                "none_start_mod64": v["none_start_mod64"], "fast_extra_window": v["fast_extra_window"],
                                "none_extra_window": v["none_extra_window"], "jobs": len(v["per_job"])}
                          for pid, v in cell["placements"].items()}
    return {"note": "per-placement pooled FAST/NONE ratios, from the analysis files that layout.json lists as sources; "
                    "regenerate with: python scripts/check_widgets.py --regen",
            "sources": layout["sources"], "cells": cells}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    handler = functools.partial(Quiet, directory=SITE)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class Checker:
    def __init__(self):
        self.n = 0
        self.bad = []

    def ok(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
            print("  FAIL", msg)
        return cond


def f(v, d):
    return f"{v:.{d}f}"


def show_range(r):
    a, b = f(r["min"], 2), f(r["max"], 2)
    return (a if a == b else f"{a}–{b}") + "×"


def watch(page, errors):
    page.on("console", lambda m: errors.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on("requestfailed", lambda r: errors.append(f"requestfailed: {r.url}"))
    page.on("response", lambda r: errors.append(f"http {r.status}: {r.url}") if r.status >= 400 else None)


def radio(page, widget, group, value):
    page.locator(f'.w3-{widget} [role=radiogroup][aria-label="{group}"] [data-v="{value}"]').click()


def check_pass(browser, base, ck, width, reduced, shots, saved):
    tag = f"{width}{'-reduced' if reduced else ''}"
    print(f"== {tag}")
    layout = load(os.path.join(DATA, "layout.json"))
    side = load(SIDE)
    mit = load(os.path.join(DATA, "mitigate.json"))
    rw = load(os.path.join(DATA, "realworld.json"))
    pgo = load(os.path.join(DATA, "pgo.json"))
    ctx = browser.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce" if reduced else "no-preference")
    page = ctx.new_page()
    errors = []
    watch(page, errors)
    page.goto(base + "widgets-demo.html", wait_until="networkidle")
    page.wait_for_selector("html[data-ready='1']")
    for w, sel in (("placement", ".pl-num"), ("mitigation", ".mi-brow"), ("programs", ".pr-row")):
        ck.ok(page.locator(f".w3-{w} {sel}").count() > 0, f"{tag}: {w} mounted")
    ck.ok(page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{tag}: no horizontal scroll (scrollWidth {page.evaluate('document.documentElement.scrollWidth')})")

    # ------------------------------------------------------------------ placement
    cpus = best_cpus(layout)
    full = len(cpus) * 8
    n_done = 0
    for ci, c in enumerate(cpus):
        radio(page, "placement", "CPU model", ci)
        for row in c["rows"]:
            radio(page, "placement", "Loop", row["kernel"])
            radio(page, "placement", "Working-set size", row["size"])
            cell = side["cells"].get(f"{c['cpu_model']}|{c['jobs']}|{row['kernel']}|{row['size']}")
            if cell is None:
                ck.ok(False, f"{tag}: no sidecar cell for {c['cpu_short']} {row['kernel']} {row['size']}")
                continue
            plac = sorted(cell.values(), key=lambda p: p["fast_start_mod64"])
            slot = int(page.get_attribute(".w3-placement .pl-bar.fast-bar", "aria-valuenow")) - 1
            shown = page.inner_text(".w3-placement .pl-num")
            ck.ok(shown == f(plac[slot]["ratio"], 3) + "×", f"{tag}: placement {c['cpu_short']} {row['kernel']} {row['size']} slot {slot}: shows {shown}, data {f(plac[slot]['ratio'], 3)}")
            n_done += 1
    ck.ok(n_done == full, f"{tag}: placement covered {n_done} of {full} cells")
    # stops show their own ratio
    radio(page, "placement", "CPU model", 0)
    radio(page, "placement", "Loop", "k02_add_fwd")
    radio(page, "placement", "Working-set size", "L1")
    c0 = cpus[0]
    cell = side["cells"][f"{c0['cpu_model']}|{c0['jobs']}|k02_add_fwd|L1"]
    plac = sorted(cell.values(), key=lambda p: p["fast_start_mod64"])
    nstops = page.locator(".w3-placement .pl-stop").count()
    ck.ok(nstops == 4, f"{tag}: four stops ({nstops})")
    seen = []
    for i in range(nstops):
        page.locator(".w3-placement .pl-stop").nth(i).click()
        seen.append(page.inner_text(".w3-placement .pl-num"))
        ck.ok(seen[-1] == f(plac[i]["ratio"], 3) + "×", f"{tag}: stop {i} shows {seen[-1]}, data {f(plac[i]['ratio'], 3)}")
        ck.ok(page.get_attribute(".w3-placement .pl-stop >> nth=%d" % i, "aria-pressed") == "true", f"{tag}: stop {i} pressed")
    ck.ok(len(set(seen)) > 1, f"{tag}: forward add swings across the stops ({seen})")
    # slider by keyboard
    page.locator(".w3-placement .pl-stop").nth(0).click()
    page.locator(".w3-placement .pl-bar.fast-bar").focus()
    page.keyboard.press("ArrowRight")
    ck.ok(page.get_attribute(".w3-placement .pl-bar.fast-bar", "aria-valuenow") == "2", f"{tag}: slider ArrowRight moves to stop 2")
    page.keyboard.press("End")
    ck.ok(page.get_attribute(".w3-placement .pl-bar.fast-bar", "aria-valuenow") == "4", f"{tag}: slider End moves to stop 4")
    page.keyboard.press("Home")
    ck.ok(page.get_attribute(".w3-placement .pl-bar.fast-bar", "aria-valuenow") == "1", f"{tag}: slider Home moves to stop 1")
    # no dragging: the bar does not move under a drag; the four stops are tap targets that act at once
    page.locator(".w3-placement .pl-bar.fast-bar").scroll_into_view_if_needed()
    bb = page.locator(".w3-placement .pl-bar.fast-bar").bounding_box()
    lane = page.locator(".w3-placement .pl-lane").first.bounding_box()
    page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
    page.mouse.down()
    page.mouse.move(lane["x"] + lane["width"] * (60 / 96), bb["y"] + bb["height"] / 2, steps=8)
    page.mouse.up()
    ck.ok(page.get_attribute(".w3-placement .pl-bar.fast-bar", "aria-valuenow") == "1", f"{tag}: dragging the bar does nothing (no sliders; got {page.get_attribute('.w3-placement .pl-bar.fast-bar', 'aria-valuenow')})")
    page.locator(".w3-placement .pl-stop").nth(3).click()
    ck.ok(page.get_attribute(".w3-placement .pl-bar.fast-bar", "aria-valuenow") == "4", f"{tag}: tapping the fourth stop selects it at once")
    page.locator(".w3-placement .pl-stop").nth(0).click()
    ck.ok(page.get_attribute(".w3-placement .pl-bar.fast-bar", "aria-valuenow") == "1", f"{tag}: tapping the first stop selects it")
    # radio arrow keys
    page.locator(".w3-placement [aria-label='Loop'] [aria-checked='true']").focus()
    before = page.get_attribute(".w3-placement [aria-label='Loop'] [aria-checked='true']", "data-v")
    page.keyboard.press("ArrowRight")
    after = page.get_attribute(".w3-placement [aria-label='Loop'] [aria-checked='true']", "data-v")
    ck.ok(before != after, f"{tag}: radio ArrowRight changes the loop ({before} to {after})")
    # tab order reaches a control
    page.locator(".w3-placement [aria-label='CPU model'] [aria-checked='true']").focus()
    page.keyboard.press("Tab")
    ck.ok(page.evaluate("document.activeElement && document.activeElement.closest('.w3-placement') !== null"), f"{tag}: Tab stays among the placement controls")
    cap = page.inner_text(".w3-placement .pl-caption")
    ck.ok("NOT measured" in cap and "schematic" in cap and "snaps to the nearest measured stop" in cap, f"{tag}: placement caption says what is not measured")
    # reverse stays high
    radio(page, "placement", "Loop", "k04_rev")
    rv = float(page.inner_text(".w3-placement .pl-num").rstrip("×"))
    ck.ok(rv > 3, f"{tag}: the reverse loop stays high ({rv})")
    radio(page, "placement", "Loop", "k02_add_fwd")
    radio(page, "placement", "Working-set size", "L1")
    radio(page, "placement", "CPU model", 0)
    page.locator(".w3-placement .pl-stop").nth(0).click()
    shot(page, ".w3-placement", f"placement-{tag}-a", shots, saved)
    page.locator(".w3-placement .pl-stop").nth(2).click()
    shot(page, ".w3-placement", f"placement-{tag}-b", shots, saved)
    radio(page, "placement", "Loop", "k04_rev")
    shot(page, ".w3-placement", f"placement-{tag}-rev", shots, saved)

    # ------------------------------------------------------------------ mitigation
    cpuopts = ["all"] + mit["cpus"]
    n_m = 0
    for si, sh in enumerate(mit["shapes"]):
        radio(page, "mitigation", "Loop shape", si)
        vmap = {v["variant"]: v for v in sh["variants"]}
        orig = vmap["orig"]
        ck.ok(page.locator(".w3-mitigation select").input_value() == sh["recommended"], f"{tag}: {sh['shape']}: the recommended rewrite is selected first")
        for v in sh["variants"]:
            if v["variant"] == "orig":
                continue
            page.locator(".w3-mitigation select").select_option(v["variant"])
            codes = [t.rstrip("\n") for t in page.locator(".w3-mitigation .mi-line").all_inner_texts()]
            ck.ok([c.strip() for c in codes] == [c.strip() or "" for c in v["code"]], f"{tag}: {sh['shape']}/{v['variant']}: code panel shows the data's code")
            for cpu in cpuopts:
                radio(page, "mitigation", "CPU model", cpu)
                vals = page.locator(".w3-mitigation [data-range]").all_inner_texts()
                if cpu == "all":
                    ro, rv = orig["range"], v["range"]
                else:
                    ro = orig["per_cpu_range"].get(cpu, {}).get("both")
                    rv = v["per_cpu_range"].get(cpu, {}).get("both")
                exp = [show_range(r) for r in (ro, rv) if r]
                ck.ok(vals == exp, f"{tag}: {sh['shape']}/{v['variant']}/{cpu}: bars {vals}, data {exp}")
                n_m += 1
        radio(page, "mitigation", "CPU model", "all")
    # toggle
    radio(page, "mitigation", "Loop shape", 0)
    page.locator(".w3-mitigation select").select_option("pre")
    radio(page, "mitigation", "Show the loop", "before")
    codes = [t.strip() for t in page.locator(".w3-mitigation .mi-line").all_inner_texts()]
    ck.ok(codes == [c.strip() for c in mit["shapes"][0]["variants"][0]["code"]], f"{tag}: toggle shows the original loop")
    shot(page, ".w3-mitigation", f"mitigation-{tag}-before", shots, saved)
    radio(page, "mitigation", "Show the loop", "after")
    shot(page, ".w3-mitigation", f"mitigation-{tag}-after", shots, saved)
    rules = page.inner_text(".w3-mitigation .mi-rules")
    ck.ok(mit["headline_rule"] in rules and str(mit["usable_jobs"]) in rules, f"{tag}: the rule for 'better' and the usable-job count are quoted from the data")
    # variants added after the first run carry that chip
    radio(page, "mitigation", "Loop shape", 1)
    page.locator(".w3-mitigation select").select_option("span_il2")
    ck.ok("added after the first timed run" in page.inner_text(".w3-mitigation .mi-chips"), f"{tag}: span_il2 is marked as added after the first timed run")
    # belt: animated normally, static under reduced motion
    radio(page, "mitigation", "Loop shape", 0)
    page.locator(".w3-mitigation select").select_option("pre")
    page.locator(".w3-mitigation .mi-belt").first.scroll_into_view_if_needed()
    page.wait_for_timeout(700)
    on1 = page.locator(".w3-mitigation .mi-belt >> nth=1 >> .mi-cell.on").count()
    page.wait_for_timeout(700)
    on2 = page.locator(".w3-mitigation .mi-belt >> nth=1 >> .mi-cell.on").count()
    heads = page.locator(".w3-mitigation .mi-cell.head").count()
    if reduced:
        ck.ok(on1 == on2 and heads == 0 and page.locator(".w3-mitigation .mi-playrow button:visible").count() == 0,
              f"{tag}: belt is static under reduced motion ({on1}, {on2}, heads {heads})")
    else:
        top = page.locator(".w3-mitigation .mi-belt >> nth=0 >> .mi-cell.on").count()
        ck.ok(on1 != on2 or top > 0, f"{tag}: belt animates ({on1} then {on2})")
        page.locator(".w3-mitigation .mi-playrow button").click()
        page.wait_for_timeout(4500)
        a = page.locator(".w3-mitigation .mi-belt >> nth=1 >> .mi-cell.on").count()
        page.wait_for_timeout(600)
        b = page.locator(".w3-mitigation .mi-belt >> nth=1 >> .mi-cell.on").count()
        ck.ok(a == b and page.locator(".w3-mitigation .mi-playrow button").inner_text() == "Replay", f"{tag}: the belt runs once, rests on its final frame, and Replay is offered ({a}, {b})")

    # ------------------------------------------------------------------ programs
    groups = {g["cpu_short"]: g for g in rw["timing"]["groups"]}
    pg = {c["cpu_short"]: c for c in pgo["cpus"]}
    shorts = list(groups) + [c for c in pg if c not in groups]
    minj = rw["minimum_jobs"]
    ids = [r["row"] for r in rw["rows"]]
    n_p = 0
    for mi, short in enumerate(shorts):
        radio(page, "programs", "CPU model", mi)
        np_ok = short in groups and groups[short]["enough"] and groups[short]["jobs"] >= minj
        pg_ok = short in pg and pg[short]["enough"] and pg[short]["jobs"] >= minj
        for col in ("fast", "aligned"):
            radio(page, "programs", "Build", col)
            for ser in ("np", "pgo", "both"):
                radio(page, "programs", "Profile-guided optimization", ser)
                want = ["np", "pgo"] if ser == "both" else [ser]
                avail = [s for s in want if (np_ok if s == "np" else pg_ok)]
                msgs = page.locator(".w3-programs .pr-msg").all_inner_texts()
                ck.ok(len(msgs) == len(want) - len(avail), f"{tag}: {short}/{col}/{ser}: {len(msgs)} messages for {len(want) - len(avail)} missing series")
                for m in msgs:
                    ck.ok("too few jobs" in m or "no " in m, f"{tag}: {short}/{col}/{ser}: message says why: {m}")
                rows = page.locator(".w3-programs .pr-row")
                if not avail:
                    ck.ok(rows.count() == 0, f"{tag}: {short}/{col}/{ser}: no rows without a reading")
                    continue
                ck.ok(rows.count() == len(ids), f"{tag}: {short}/{col}/{ser}: {rows.count()} rows")
                for i, rid in enumerate(ids):
                    got = rows.nth(i).locator(".pr-val > span").all_inner_texts()
                    exp = []
                    for s in avail:
                        if s == "np":
                            r = groups[short]["rows"][rid][col]["ratio"]
                        else:
                            r = next(x for x in pg[short]["rows"] if x["row"] == rid)["pgo"][col]["ratio"]
                        pre = ("◆ " if s == "pgo" else "● ") if len(avail) == 2 else ""
                        exp.append(pre + f(r, 3) + "×")
                    ck.ok(got == exp, f"{tag}: {short}/{col}/{ser}/{rid}: shows {got}, data {exp}")
                    n_p += 1
    # reading strings: exactly the data's
    radio(page, "programs", "CPU model", 0)
    radio(page, "programs", "Build", "fast")
    radio(page, "programs", "Profile-guided optimization", "np")
    readings = page.locator(".w3-programs .pr-row .pr-val small").all_inner_texts()
    g0 = groups[shorts[0]]
    exp = []
    for rid in ids:
        r = g0["rows"][rid]
        exp.append(f"{r['reading']}, at most {f(r['at_most_pct'], 2)}%" if r["at_most_pct"] is not None else r["reading"])
    ck.ok(readings == exp, f"{tag}: reading strings are the data's own ({readings} vs {exp})")
    ck.ok(any(x.startswith("not detectable") for x in readings), f"{tag}: 'not detectable' appears as the data words it")
    # tooltip on hover and on focus
    first = page.locator(".w3-programs .pr-row").first
    first.scroll_into_view_if_needed()
    first.hover()
    tip = page.locator(".w3-programs .pr-tip")
    ck.ok(tip.is_visible(), f"{tag}: tooltip shows on hover")
    t = tip.inner_text()
    r0 = g0["rows"][ids[0]]
    ck.ok(f(r0["fast"]["ratio"], 4) in t and f(r0["aligned"]["ratio"], 4) in t and f"{g0['jobs']} jobs" in t, f"{tag}: tooltip carries the exact numbers and the job count")
    ck.ok(r0["text"] in t, f"{tag}: tooltip carries the data's reading text")
    page.mouse.move(2, 2)
    ck.ok(not tip.is_visible(), f"{tag}: tooltip hides on leave")
    page.locator(".w3-programs [aria-label='Profile-guided optimization'] [aria-checked='true']").focus()
    page.keyboard.press("Tab")
    ck.ok(page.evaluate("document.activeElement.classList.contains('pr-row') || !!document.activeElement.closest('.w3-programs')"), f"{tag}: Tab moves on")
    page.locator(".w3-programs .pr-row").nth(2).focus()
    ck.ok(tip.is_visible(), f"{tag}: tooltip shows on keyboard focus")
    page.keyboard.press("Escape")
    ck.ok(not tip.is_visible(), f"{tag}: Escape hides the tooltip")
    # share markers
    shares = page.locator(".w3-programs .pr-share").all_inner_texts()
    ck.ok(len(shares) == len(ids) and sum("no lost loop" in s for s in shares) == sum(1 for r in rw["rows"] if r["control"]), f"{tag}: a share marker (or 'no lost loop') under every row")
    ck.ok(any(f"{f(r['lines_none'], 2)}%" in s for r in rw["rows"] if not r["control"] for s in shares), f"{tag}: share markers print the data's percentages")
    # sort
    page.locator(".w3-programs select").select_option("ratio")
    order = [x.split("×")[0] for x in page.locator(".w3-programs .pr-row .pr-val > span").all_inner_texts()]
    vals = [float(x) for x in order]
    ck.ok(vals == sorted(vals, reverse=True), f"{tag}: sorted by cost, high to low ({vals})")
    shot(page, ".w3-programs", f"programs-{tag}-a", shots, saved)
    radio(page, "programs", "Profile-guided optimization", "both")
    page.locator(".w3-programs select").select_option("listed")
    shot(page, ".w3-programs", f"programs-{tag}-both", shots, saved)
    foot = page.inner_text(".w3-programs .w-foot")
    ck.ok("chosen because they contain lost loops" in foot and "training input is the timed input" in foot, f"{tag}: caveats footer")
    radio(page, "programs", "CPU model", 1)
    shot(page, ".w3-programs", f"programs-{tag}-cpu2", shots, saved)

    # ------------------------------------------------------------------ touch targets and errors
    if width <= 480:
        small = page.evaluate("""() => [...document.querySelectorAll('.w3 button, .w3 select')].filter(b => b.getBoundingClientRect().height > 0 && b.getBoundingClientRect().height < 32).map(b => b.textContent.trim().slice(0, 20) + ' ' + Math.round(b.getBoundingClientRect().height))""")
        ck.ok(not small, f"{tag}: every button and select is at least 32 px tall ({small[:5]})")
    over = page.evaluate("""() => [...document.querySelectorAll('.w3')].filter(w => w.scrollWidth > w.clientWidth + 1).map(w => w.className + ' ' + w.scrollWidth + '>' + w.clientWidth)""")
    ck.ok(not over, f"{tag}: no widget overflows its box ({over})")
    ck.ok(page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{tag}: still no horizontal scroll after use")
    ck.ok(not errors, f"{tag}: no console errors, page errors or failed requests {errors[:4]}")
    ctx.close()


def shot(page, sel, name, shots, saved):
    loc = page.locator(sel).first
    loc.scroll_into_view_if_needed()
    page.wait_for_timeout(450)
    path = os.path.join(shots, name + ".png")
    loc.screenshot(path=path)
    saved.append(path)


def check_errors(browser, base, ck):
    """A blocked data file shows a one-line message and nothing else breaks."""
    print("== failed fetches")
    for blocked, widget in (("layout.json", "placement"), ("mitigate.json", "mitigation"), ("realworld.json", "programs"), ("pgo.json", "programs")):
        ctx = browser.new_context(viewport={"width": 800, "height": 700})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.route(f"**/data/{blocked}", lambda r: r.fulfill(status=404, body="no"))
        page.goto(base + "widgets-demo.html", wait_until="networkidle")
        page.wait_for_selector("html[data-ready='1']")
        page.wait_for_timeout(300)
        msg = page.locator(f".w3-{widget} .w-err")
        ck.ok(msg.count() == 1 and blocked in msg.inner_text(), f"blocked {blocked}: {widget} shows one error line ({msg.all_inner_texts()})")
        ck.ok(not errs, f"blocked {blocked}: no uncaught page errors {errs}")
        ctx.close()


def check_hero_variants(browser, base, ck):
    """The hero's four presentations share the page with the widgets and the style sheet: every one must leave the
    page without console errors or horizontal scroll, with the three widget placeholders mounted."""
    print("== hero variants beside the widgets")
    for v in (1, 2, 3, 4):
        for w, h in ((1280, 900), (390, 844)):
            errs = []
            pg = browser.new_page(viewport={"width": w, "height": h})
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f"{base}index.html#hero={v}", wait_until="networkidle")
            pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=15000)
            pg.evaluate("document.querySelectorAll('.sec-more[aria-expanded=false]').forEach(b => b.click())")  # the module sections start folded; the widgets in them mount on opening
            pg.evaluate("document.querySelectorAll('.wd').forEach(d => { d.open = true; })")
            pg.wait_for_function("document.querySelectorAll('.widget.mounted').length === 3", timeout=15000)
            ck.ok(pg.evaluate("document.getElementById('race').dataset.hv") == str(v) and not errs, f"hero {v} at {w}: the page loads with the widgets mounted and no console errors ({errs[:2]})")
            ck.ok(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"hero {v} at {w}: no horizontal scroll")
            if v == 4:  # the default hero (lanes, Reproduce box) must not hide or cover a widget
                ck.ok(pg.evaluate("document.querySelectorAll('#race-loops button').length === 8 && document.querySelectorAll('#race .ln-t.on').length === 8"), f"hero 4 at {w}: eight lanes, each with its checked bar, beside the widgets")
            pg.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default=None)
    ap.add_argument("--regen", action="store_true")
    a = ap.parse_args()
    fresh = derive_sidecar()
    if a.regen:
        with open(SIDE, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(fresh, fh, indent=1)
            fh.write("\n")
        print("wrote", SIDE)
    ck = Checker()
    ck.ok(load(SIDE) == fresh, "site/widgets/placements.json equals a fresh derivation (run with --regen if the layout data changed)")
    if ck.bad:
        print("\n".join(ck.bad))
        return 1
    shots = a.shots or tempfile.mkdtemp(prefix="widgets-shots-")
    os.makedirs(shots, exist_ok=True)
    from playwright.sync_api import sync_playwright
    srv = serve()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    saved = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--mute-audio", "--disable-speech-api", "--autoplay-policy=user-gesture-required"])
            try:
                for width in (1280, 390):
                    for reduced in (False, True):
                        check_pass(browser, base, ck, width, reduced, shots, saved)
                check_errors(browser, base, ck)
                check_hero_variants(browser, base, ck)
            finally:
                browser.close()
    finally:
        srv.shutdown()
    print(f"\n{ck.n} checks, {len(ck.bad)} failed")
    for s in saved:
        print("shot", s)
    if ck.bad:
        print("FAILED")
        return 1
    print("ALL WIDGET CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
