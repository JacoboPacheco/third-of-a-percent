"""For each function-level pass in a saved pipeline that runs before LoopVectorize, count the pointer loads that sit inside the innermost loop.

"Innermost loop" is the smallest natural loop that contains a store (the loop body is the back edge's source,
its header and everything that reaches the source without passing through the header).

The size() of a vector is `end - begin`, two pointer loads. When they are inside the loop, the
size is recomputed on every iteration; when they sit outside, it is loop invariant.
Usage: python loadtrack.py pipe_c19_fast pipe_c231_fast
"""
import re
import sys

import pipe_tools as pt

LABEL = re.compile(r"^([A-Za-z0-9_.$-]+):")


def parse(text):
    blocks, order, cur = {}, [], None
    for ln in text.splitlines():
        if "#dbg_" in ln or "@llvm.dbg" in ln:
            continue
        m = LABEL.match(ln)
        if m and not ln.startswith(" ") and "define" not in ln:
            cur = m.group(1)
            blocks[cur] = []
            order.append(cur)
            continue
        if ln.startswith("define"):
            cur = "entry"
            blocks[cur] = []
            order.append(cur)
            continue
        if cur is not None and ln.startswith("  "):
            blocks[cur].append(ln.strip())
    return blocks, order


def succs(insts):
    if not insts:
        return []
    t = insts[-1]
    if t.startswith("br "):
        return re.findall(r"label %([A-Za-z0-9_.$-]+)", t)
    return []


def innermost_loop(blocks, order):
    if not order:
        return None
    S = {b: succs(blocks[b]) for b in order}
    P = {b: [] for b in order}
    for b, ss in S.items():
        for s in ss:
            if s in P:
                P[s].append(b)
    entry = order[0]
    dom = {b: set(order) for b in order}
    dom[entry] = {entry}
    changed = True
    while changed:
        changed = False
        for b in order:
            if b == entry or not P[b]:
                continue
            nd = set.intersection(*[dom[p] for p in P[b]]) | {b}
            if nd != dom[b]:
                dom[b], changed = nd, True
    loops = []
    for u, ss in S.items():
        for v in ss:
            if v in dom[u]:
                # natural loop of the back edge u -> v: v plus everything that reaches u without passing through v
                # (for a one-block loop u == v, nothing is walked: the loop is the block itself)
                body, work = {v}, []
                if u != v:
                    body.add(u)
                    work.append(u)
                while work:
                    x = work.pop()
                    for p in P[x]:
                        if p not in body:
                            body.add(p)
                            work.append(p)
                loops.append((v, body))
    withstore = [(h, b) for h, b in loops if any(i.startswith("store ") for x in b for i in blocks[x])]
    if not withstore:
        return None
    return min(withstore, key=lambda hb: len(hb[1]))


def track(name):
    """Rows (pass index, pass name, blocks in the loop, pointer loads in it) for the passes that run before LoopVectorizePass."""
    rows = []
    for idx, p in enumerate(pt.passes(name)):
        if pt.pass_name(p).startswith("LoopVectorizePass"):
            break
        if "unnamed loop" in p["name"] or "[module]" in p["name"] or "(_Z" in p["name"]:
            continue
        txt = pt.ir_text(p["after"])
        blocks, order = parse(txt)
        lp = innermost_loop(blocks, order)
        if lp is None:
            continue
        h, body = lp
        loads = sum(1 for x in body for i in blocks[x] if re.search(r"= load ptr, ptr ", i))
        rows.append((idx, pt.pass_name(p), len(body), loads))
    return rows


if __name__ == "__main__":
    for n in sys.argv[1:]:
        rows = track(n)
        print("==", n)
        last = None
        for idx, nm, nb, ld in rows:
            if (nb, ld) != last:
                print("  after pass #%d %-34s innermost loop: %d blocks, %d pointer loads inside" % (idx, nm, nb, ld))
                last = (nb, ld)
