#!/usr/bin/env python3
"""Prints where the hot loops of kern_k02_add_fwd sit in a binary: start, end, length, start mod 64,
and whether the loop crosses a 32-byte or 64-byte boundary (the units AMD front ends fetch in).

A loop is a backward conditional jump; its body is from the jump target to the end of the jump.
Usage: python3 loops.py <binary> [<binary> ...]   -> one JSON line per binary.
"""
import json
import re
import subprocess
import sys


def loops(binary):
    out = subprocess.run(["objdump", "-d", "--no-show-raw-insn", binary], capture_output=True, text=True).stdout
    keep, lines = False, []
    for ln in out.splitlines():
        if re.match(r"^[0-9a-f]+ <_Z\d+kern_k02_add_fwd", ln):
            keep = True
            continue
        if keep:
            if not ln.strip():
                break
            lines.append(ln)
    insns = []
    for ln in lines:
        m = re.match(r"^\s*([0-9a-f]+):\s*(.*)$", ln)
        if m:
            insns.append((int(m.group(1), 16), m.group(2).strip()))
    res = []
    for i, (addr, text) in enumerate(insns):
        m = re.match(r"^j\w+\s+([0-9a-f]+)\s+<", text)
        if m and not text.startswith("jmp"):
            tgt = int(m.group(1), 16)
            if tgt <= addr:
                end = insns[i + 1][0] if i + 1 < len(insns) else addr + 2  # first byte after the jump
                body = [t for a, t in insns if tgt <= a < end]
                res.append({
                    "start": hex(tgt), "end": hex(end), "bytes": end - tgt, "start_mod64": tgt % 64,
                    "crosses32": (tgt // 32) != ((end - 1) // 32), "crosses64": (tgt // 64) != ((end - 1) // 64),
                    "insns": len(body), "simd": any("movdqu" in t for t in body),
                })
    return res


if __name__ == "__main__":
    for b in sys.argv[1:]:
        print(json.dumps({"binary": b, "loops": loops(b)}))
