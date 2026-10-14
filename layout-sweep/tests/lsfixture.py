"""Synthetic layout-sweep results (no compiler, no runner): a job document with chosen ratios per placement."""
import random

import analyze as an
import stats

CPU = "FAKE EPYC 0000 64-Core Processor"


def hot(start, extra=False, simd=True):
    return {"start": start, "start_mod64": start % 64, "bytes": 31, "windows64": 2 if extra else 1,
            "min_windows64": 1, "extra_window": extra, "crosses64": extra, "simd": simd}


STEP = [4]


def build(kernel, pad_id, mode, vec, extra=False):
    i = int(pad_id[1:]) if pad_id.startswith("p") else 0
    fn = 0x401000 + STEP[0] * i
    return {"sha256": f"{kernel}.{pad_id}.{mode}", "fn_addr": fn, "hot": hot(fn + (0x20 if mode == "none" else 0x28), extra),
            "vectorized": vec, "traps": 0 if mode == "none" else 3, "command": "x"}


def make_job(job, kernels, cpu=CPU, size="L1", reps=20, aa_sd=0.004, noise=0.004, run_id="1",
             checksum_ok=True, smoke=False, ci=False, break_mech=False, mode="fine"):
    """kernels: {kernel: {"vec": (none_vec, fast_vec), "ratio": f(pad_id) -> float}}."""
    rng = random.Random(f"fixture|{job}")
    n, step = (16, 4) if mode == "fine" else (4, 16)
    pads = an.pad_ids(n)
    STEP[0] = step
    builds, cells = {}, []
    for k, spec in kernels.items():
        pl = {}
        for pid in pads + an.REFS:
            extra = spec.get("extra", lambda p: False)(pid)
            pl[pid] = {"pad_bytes": an.pad_bytes(pid, step) if pid in pads else None,
                       "none": build(k, pid, "none", spec["vec"][0]),
                       "fast": build(k, pid, "fast", spec["vec"][1], extra)}
        if break_mech:
            pl["p07"]["fast"]["fn_addr"] += 16
        builds[k] = {"loop_line": 6, "placements": pl}
        cell = {"cell_id": f"{k}.{size}", "kernel": k, "size_class": size, "n": 1000, "iters": 100,
                "order": pads + an.REFS, "placements": {}}
        for pid in pads + an.REFS:
            base = 1000.0 * rng.uniform(0.98, 1.02)  # host speed differs per job; the ratio does not
            none = [base * rng.lognormvariate(0, noise) for _ in range(reps)]
            fast = [base * spec["ratio"](pid) * rng.lognormvariate(0, noise) for _ in range(reps)]
            p = {"none_ns": none, "fast_ns": fast, "checksum_match": checksum_ok, "order": "ABBA" * (reps // 2),
                 "ratio": stats.ratio_of_medians(none, fast), "ci95": [0.0, 0.0]}
            if ci:
                p["ci95"] = list(stats.bootstrap_ratio_ci(none, fast, resamples=200))
            cell["placements"][pid] = p
        a = [1000.0 * rng.lognormvariate(0, aa_sd) for _ in range(reps)]
        b = [1000.0 * rng.lognormvariate(0, aa_sd) for _ in range(reps)]
        cell["aa"] = {"a_ns": a, "b_ns": b, "checksum_match": True, "order": "ABBA" * (reps // 2), "half_width_pct": 0.0}
        cells.append(cell)
    return {"kind": "layout-sweep", "schema": 1, "smoke": smoke, "criteria_sha256": "x",
            "run": {"id": run_id, "job": str(job), "started": "t", "runner": {"cpu_model": cpu}},
            "mechanism": {"mode": mode, "step_bytes": step, "placements": n, "flags": [], "probe": []}, "reps_per_side": reps,
            "pinned_cpu": "1", "builds": builds, "cells": cells}


def idx(p):
    return int(p[1:]) if p[0] == "p" and p[1:].isdigit() else 0


FLAT = {"vec": (True, True), "ratio": lambda p: 1.0}
BAD_HALF = {"vec": (True, True), "ratio": lambda p: 1.6 if idx(p) % 2 else 1.0, "extra": lambda p: idx(p) % 2 == 1}
LOST = {"vec": (True, False), "ratio": lambda p: 4.0}
