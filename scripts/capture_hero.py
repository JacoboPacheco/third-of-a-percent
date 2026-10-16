#!/usr/bin/env python3
"""Re-captures the README image (docs/hero.png) and the share card (site/og.png) from the page in site/.

    python scripts/capture_hero.py

Serves site/ on a free localhost port, opens the main page in headless Chromium (muted) at 1440x900 for the README image
and at 1200x630 for the share card, waits until the hero has finished its one run (the bars stop changing and the
"flip the check" hint is showing), and saves both pictures. It also writes docs/hero.json, which lists what the pages
showed when the pictures were taken: the dateline, the status badge, the CPU buttons, the job count and the ratio.
scripts/check_site.py compares that file with the live page and with site/data, so a change to the first screen or to
the data that is not followed by a new capture fails the check.

Needs the Python playwright package and its Chromium. Run it after any change to the first screen, the CPU list or
the pooled job counts, then look at both pictures before committing them.
"""
import functools
import http.server
import json
import os
import re
import sys
import threading

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, "site")
SHOTS = (("docs/hero.png", 1440, 900), ("site/og.png", 1200, 630))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def settle(pg, quiet_ms=600, limit_ms=12000):
    """Waits until the hero's bars have stopped changing and the hint pill is showing (or the limit passes)."""
    sig = "[...document.querySelectorAll('#race .ln-t > i')].map(i => getComputedStyle(i).clipPath).join('|')"
    last, still, waited = pg.evaluate(sig), 0, 0
    while waited < limit_ms:
        pg.wait_for_timeout(100)
        waited += 100
        cur = pg.evaluate(sig)
        still = still + 100 if cur == last else 0
        last = cur
        if still >= quiet_ms and pg.evaluate("document.getElementById('sw-hint').classList.contains('show')"):
            break
    pg.wait_for_timeout(300)


def facts(pg):
    return pg.evaluate("""() => ({
        dateline: document.querySelector('.hero .dateline').firstChild.textContent.trim(),
        badge: document.querySelector('.bar-wip .wip-long').textContent.trim(),
        cpu_tabs: [...document.querySelectorAll('#race-cpu button')].map(b => b.textContent.trim()),
        selected_cpu: document.querySelector('#race-cpu button[aria-checked="true"]').textContent.trim(),
        loop: document.querySelector('#race-loops button[aria-checked="true"] .tl').textContent.trim(),
        ratio: document.getElementById('race-ratio').textContent.trim(),
        jobs: +document.querySelector('#race-sub .rr-meta').textContent.match(/(\\d+) jobs/)[1],
    })""")


def main():
    from playwright.sync_api import sync_playwright
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    taken = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--mute-audio", "--disable-speech-api", "--autoplay-policy=user-gesture-required"])
            for rel, w, h in SHOTS:
                ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="no-preference")
                pg = ctx.new_page()
                pg.goto(base, wait_until="networkidle")
                pg.wait_for_function("document.querySelectorAll('#race-loops button').length === 8", timeout=20000)
                pg.wait_for_function("[...document.fonts].some(f => /Source Serif/.test(f.family) && f.status === 'loaded')", timeout=20000)
                settle(pg)
                now = facts(pg)
                if taken is not None and now != taken:
                    print("the two pictures disagree about what the page shows:", taken, now)
                    return 1
                taken = now
                path = os.path.join(REPO, *rel.split("/"))
                pg.screenshot(path=path, clip={"x": 0, "y": 0, "width": w, "height": h})
                print(f"wrote {rel} ({w}x{h})")
                ctx.close()
            browser.close()
    finally:
        srv.shutdown()
        srv.server_close()
    doc = dict(taken)
    doc["images"] = {rel: [w, h] for rel, w, h in SHOTS}
    with open(os.path.join(REPO, "docs", "hero.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote docs/hero.json:", json.dumps(taken, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
