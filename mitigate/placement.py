"""Where the loops of a compiled function sit: start, length, and whether they cross a 64-byte line.

Stage S3. The investigation (investigate/FINDINGS.md, run 38119645255) found that the FAST/NONE
ratio of k02_add_fwd on some CPUs (1.6x on EPYC 7763 and 9V74) came from a 31-byte SIMD loop that
straddled a 64-byte boundary, not from the bounds check. So every build now records where its
loops landed. The idea is investigate/loops.py; the code is copied here (investigate/ stays the record).

A loop is a backward conditional jump inside the function; its body runs from the jump target to
the first byte after the jump. For each loop:
  start, end (hex strings), bytes, start_mod64, crosses64 (the body touches two or more 64-byte
  windows), windows64 (how many it touches), min_windows64 (the fewest a body this long can touch),
  extra_window (windows64 > min_windows64: the placement costs a fetch window it does not need),
  insns, simd (an %xmm register in the body), innermost (no other loop lies inside it).
"Hot" loops are the innermost ones; outer ones are listed for completeness.
"""
import re

_INSN = re.compile(r"^\s*([0-9a-f]+):\s*(.*)$")
_JCC = re.compile(r"^(j(?!mp)\w+)\s+([0-9a-f]+)\s+<")


def instructions(lines):
    """(address, text) for every instruction line of `objdump -d --no-show-raw-insn` output."""
    out = []
    for ln in lines:
        m = _INSN.match(ln)
        if m and m.group(2).strip():
            out.append((int(m.group(1), 16), m.group(2).strip()))
    return out


def loops(lines):
    """The loops of one function, given its objdump lines (harness/asm.function_lines)."""
    insns = instructions(lines)
    found = []
    for i, (addr, text) in enumerate(insns):
        m = _JCC.match(text)
        if not m:
            continue
        tgt = int(m.group(2), 16)
        if tgt > addr:
            continue
        end = insns[i + 1][0] if i + 1 < len(insns) else addr + 2  # first byte after the jump
        body = [t for a, t in insns if tgt <= a < end]
        n = end - tgt
        windows = (end - 1) // 64 - tgt // 64 + 1
        min_windows = (n + 63) // 64
        found.append({"start": hex(tgt), "end": hex(end), "bytes": n, "start_mod64": tgt % 64,
                      "crosses64": windows > 1, "windows64": windows, "min_windows64": min_windows,
                      "extra_window": windows > min_windows, "insns": len(body),
                      "simd": any("%xmm" in t for t in body)})
    for lp in found:
        s, e = int(lp["start"], 16), int(lp["end"], 16)
        lp["innermost"] = not any(o is not lp and s <= int(o["start"], 16) and int(o["end"], 16) <= e
                                  and (o["start"], o["end"]) != (lp["start"], lp["end"]) for o in found)
    return found


def hot(loop_list):
    """The innermost loops only."""
    return [lp for lp in loop_list if lp["innermost"]]


def summary(loop_list):
    """A compact line for logs: start/bytes for each innermost loop, X when it crosses 64 bytes,
    + when that crossing costs a window the loop does not need."""
    parts = []
    for lp in hot(loop_list):
        mark = ("+" if lp["extra_window"] else "X") if lp["crosses64"] else ""
        parts.append(f"{lp['start']}/{lp['bytes']}B{'s' if lp['simd'] else ''}{mark}")
    return " ".join(parts) or "-"


def binary_summary(objdump_lines):
    """For a whole program: how many innermost loops the .text has, and how many of them cross a
    64-byte boundary or waste a fetch window. Functions are split at objdump's blank lines."""
    funcs, cur = [], []
    for ln in objdump_lines:
        if not ln.strip():
            if cur:
                funcs.append(cur)
            cur = []
        else:
            cur.append(ln)
    if cur:
        funcs.append(cur)
    total = crossing = extra = simd = simd_crossing = 0
    for f in funcs:
        for lp in hot(loops(f)):
            total += 1
            crossing += lp["crosses64"]
            extra += lp["extra_window"]
            simd += lp["simd"]
            simd_crossing += lp["simd"] and lp["crosses64"]
    return {"innermost_loops": total, "crosses64": crossing, "extra_window": extra,
            "simd_loops": simd, "simd_crosses64": simd_crossing}
