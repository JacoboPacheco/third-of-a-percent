#!/usr/bin/env python3
"""The matrix-multiply d-sweep runner (rules: dsweep/PLAN.md; numbers: dsweep/analyze.py and harness/criteria-v3.json).

Builds kernels/k08_matmul.cpp four ways (NONE, FAST, and both with -falign-loops=64; harness/run.py also builds a
fifth, no-vectorize build that this sweep does not time), then times FAST against NONE at a ladder of matrix sizes d
that the runner's cache sizes decide (dsweep/analyze.py ladder(): the L1-resident fit ladder, the residue scan, the
bridge to the study L2 d, the study L2 d), each d as compiled and aligned, ABBA order, pinned, with a byte-identical
A/A at the middle d and Cachegrind instruction counts as a labelled secondary column. Writes <out>/dsweep.json
(kind "dsweep", schema_version 1) at the end, <out>/asm/, <out>/remarks/ and <out>/cachegrind/. While it runs it
appends every finished d to <out>/dsweep.partial.jsonl (removed once dsweep.json is written), so that a job that
aborts or is cancelled late keeps its timings; the analysis lists such a job and does not pool it. Everything that
is a rule lives in dsweep/analyze.py and harness/; this file builds and times.

Run on an ubuntu-24.04 or ubuntu-24.04-arm runner with clang-18, libc++-18-dev and valgrind from apt:

  python3 dsweep/sweep.py --job 1 --out out --build build/dsweep
  python3 dsweep/sweep.py --assume-caches 64,1024      # print the d ladder for a 64 KiB L1d and 1 MiB L2 and exit (no Linux needed)
"""
import argparse
import importlib.util
import json
import os
import random
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
HARNESS = os.path.join(REPO, "harness")
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)


def _sibling(name):
    """dsweep/<name>.py loaded as dsweep_<name>, so that another folder's analyze.py (layout-sweep/) is never picked up."""
    key = "dsweep_" + name
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


an = _sibling("analyze")
import placement  # noqa: E402
import pool  # noqa: E402
import run as hr  # noqa: E402  (harness/run.py: build_kernel, caches, runner_info, toolchain, calibrate, pair, instr_count)
import stats  # noqa: E402

LOOP_KEYS = ("start", "bytes", "insns", "simd", "start_mod64", "windows64", "extra_window", "crosses64")


def timing_order(job, ds):
    """The order in which the d values are timed: a fixed shuffle per job, stored in the file, so that a drift over
    the minutes of a job cannot line up with d."""
    order = sorted(ds)
    random.Random(f"dsweep|{job}").shuffle(order)
    return order


def _loop(lp):
    return {k: lp[k] for k in LOOP_KEYS}


_INTERLEAVE = re.compile(r"interleaved count: (\d+)")


def vector_step(vec):
    """(interleave count, elements per pass) of the marked loop from clang's remark "vectorized loop (vectorization
    width: W, interleaved count: I)": I and W*I, or (None, None) when the loop was not vectorized or clang did not
    say. The ladder of dsweep/PLAN.md steps d by 8; a NONE loop that takes a pass of a size that does not divide 8
    breaks the argument for holding the leftover count fixed, and validate_doc lists that as a file problem."""
    if not vec or not vec.get("vectorized") or not vec.get("width"):
        return None, None
    for msg in vec.get("remarks") or []:
        m = _INTERLEAVE.search(msg)
        if m:
            il = int(m.group(1))
            return il, int(vec["width"]) * il
    return None, None


def builds_record(info):
    """What the file stores about the four builds: hash, command, traps, clang's remark for the marked loop with the
    interleave count and the elements per pass it implies, every loop of kern_k08_matmul and the innermost ones
    (harness/placement.py), the hot loop (harness/pool.py hot_loop: the innermost loop with simd and the most bytes)."""
    out = {}
    for mode in an.MODES:
        b = info["builds"][mode]
        hot = pool.hot_loop(b["loops"])
        il, step = vector_step(b["vectorization"])
        out[mode] = {"sha256": b["sha256"], "command": b["command"], "traps": b["traps"], "asm_lines": b["asm_lines"],
                     "vectorization": b["vectorization"], "interleave": il, "elements_per_pass": step,
                     "loops": b["loops"], "inner_loops": [_loop(lp) for lp in placement.hot(b["loops"])],
                     "hot_loop": _loop(hot) if hot else None}
    return out


def make_point(d, roles, l1d_bytes, iters, one_call_ns, fp, ap, instr, instr_note, shas, summarize=stats.summarize):
    """One point of the file from the two timed pairs (harness/run.py pair() output). `summarize` is the within-job
    interval of harness/stats.py (injectable so that the tests need not run 10 000 resamples per pair)."""
    cols = {}
    for name, pr in (("as_compiled", fp), ("aligned", ap)):
        s = summarize(pr["a_ns"], pr["b_ns"])
        cols[name] = {"none_ns": pr["a_ns"], "fast_ns": pr["b_ns"], "order": pr["order"],
                      "checksum_match": bool(pr["checksum_match"]), "ratio": s["ratio"], "ci95": s["ci95"],
                      "half_width_pct": s["half_width_pct"]}
    same = bool(fp["checksum_match"] and ap["checksum_match"] and fp["a_checksums"] == ap["a_checksums"])
    return {"d": d, "roles": roles, "d_mod_8": d % an.MODULUS, "working_set_bytes": hr.working_set(an.KERNEL, d),
            "l1_resident": 12 * d * d <= l1d_bytes // 2, "iters": iters, "calibration_ns_one_call": one_call_ns,
            "binary_sha256": dict(shas), "checksums": fp["a_checksums"], "checksum_match": same, **cols, "instr": instr, "instr_note": instr_note}


def build_doc(*, smoke, reps, cpu, run, cache, lscpu, kernel, lad, order, builds, aa, points, seconds):
    """The dsweep.json document (schema_version 1) from its parts. The hashes of the plan, of the criteria file and
    of the code files (analyze.CODE_FILES) are those of the files as they stand when the sweep runs."""
    return {"kind": an.KIND, "schema_version": an.SCHEMA_VERSION, "plan_sha256": an.plan_sha256(),
            "criteria_sha256": an.criteria_sha256(), "code_sha256": an.code_sha256(),
            "criteria_file": an.CRITERIA_FILE, "smoke": smoke,
            "reps_per_side": reps, "pinned_cpu": cpu, "target_ns_per_process": hr.TARGET_NS, "run": run,
            "machine": {"cache_bytes": cache, "lscpu": lscpu}, "kernel": kernel, "ladder": lad,
            "timing_order": order, "builds": builds, "aa": aa, "points": points, "seconds": seconds}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--job", default="0")
    ap.add_argument("--out", default=os.path.join(REPO, "dsweep", "out"))
    ap.add_argument("--build", default=os.path.join(REPO, "build", "dsweep"))
    ap.add_argument("--reps", type=int, default=None,
                    help="processes per side (default: the criteria file's 40; any other value marks the file as a smoke file)")
    ap.add_argument("--cpu", default=os.environ.get("HARNESS_CPU", "1"))
    ap.add_argument("--no-cachegrind", action="store_true")
    ap.add_argument("--assume-caches", default=None, metavar="L1D_KIB,L2_KIB",
                    help="print the d ladder for these cache sizes and exit")
    a = ap.parse_args(argv)

    if a.assume_caches:
        try:
            l1_kib, l2_kib = (int(x) for x in a.assume_caches.split(","))
        except ValueError:
            raise SystemExit("dsweep: --assume-caches takes two integers, L1D_KIB,L2_KIB (for example 64,1024)")
        print(json.dumps(an.ladder(l1_kib * 1024, l2_kib * 1024), indent=1))
        return 0

    try:
        return run_sweep(a)
    except RuntimeError as e:  # harness/run.py's run_bin raises this when a kernel process fails
        raise SystemExit(f"dsweep: a timed process failed: {e}")


def append_partial(path, rec):
    """One JSON line, written and flushed at once, so that a job that aborts (or is cancelled) after its first timing
    keeps every d it finished in dsweep.partial.jsonl. The analysis lists such a job and never pools it."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass


def run_sweep(a):
    crit_reps = an.reps_per_side()
    reps = a.reps or crit_reps
    smoke = reps != crit_reps
    out_dir, build_dir = os.path.abspath(a.out), os.path.abspath(a.build)
    for d in (out_dir, os.path.join(out_dir, "asm"), os.path.join(out_dir, "remarks"),
              os.path.join(out_dir, "cachegrind"), build_dir):
        os.makedirs(d, exist_ok=True)
    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    cache = hr.caches()
    runner, lscpu = hr.runner_info(cache)
    server, repo, run_id = (os.environ.get(x) for x in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    run = {"id": run_id or ("local-" + started), "job": str(a.job), "commit": os.environ.get("GITHUB_SHA"),
           "workflow_run_url": f"{server}/{repo}/actions/runs/{run_id}" if run_id else None,
           "started_at": started, "runner": runner, "toolchain": hr.toolchain()}
    lad = an.ladder(cache["l1d"], cache["l2"])
    print(f"[runner] cpu_model: {runner['cpu_model']}  cores: {runner['cores']}  L1d {runner['l1d_kib']} KiB  "
          f"L2 {runner['l2_kib']} KiB  L3 {runner['l3_kib']} KiB", flush=True)
    print(f"[ladder] study L1 d {lad['study_l1_d']}, study L2 d {lad['study_l2_d']}, residue {lad['residue']} mod "
          f"{lad['modulus']}, fit {lad['fit']}, scan {lad['scan']}, bridge {lad['bridge']}, A/A at d = {lad['mid_d']}",
          flush=True)
    if len(lad["fit"]) < an.RULE["minimum_fit_points"]:
        print(f"WARNING: only {len(lad['fit'])} fit d values on this machine; the rule needs "
              f"{an.RULE['minimum_fit_points']}, so the analysis will say 'neither'. The points are timed anyway.", flush=True)
    if smoke:
        print(f"WARNING: {reps} repetitions per side instead of {crit_reps}: this file is marked as a smoke file and "
              "the analysis will not call it a result.", flush=True)

    # the four builds (harness/run.py build_kernel also builds the no-vectorize build, which is not timed here)
    info = hr.build_kernel(an.KERNEL, build_dir, out_dir)
    bins = {m: info["builds"][m]["binary"] for m in an.MODES}
    for m, path in bins.items():
        if not os.path.exists(path):
            raise SystemExit(f"dsweep: the {m} binary is missing after the build: {path}")
    with open(os.path.join(out_dir, "asm", f"{an.KERNEL}.diff"), "w", encoding="utf-8") as f:
        f.write(info["diff"])
    with open(os.path.join(out_dir, "asm", f"{an.KERNEL}.aligned.diff"), "w", encoding="utf-8") as f:
        f.write(info["diff_aligned"])
    builds = builds_record(info)
    for m in an.MODES:
        v = builds[m]["vectorization"]
        hot = builds[m]["hot_loop"]
        print(f"[build] {m}: vectorized={v['vectorized']} width={v['width']} traps={builds[m]['traps']} "
              f"hot loop={hot and (str(hot['insns']) + ' insns, simd=' + str(hot['simd']) + ', at ' + hot['start'])}", flush=True)
        if hot is None:
            print(f"WARNING: no innermost loop found in kern_{an.KERNEL} of the {m} build (objdump format?)", flush=True)

    # the A/A copy: the NONE binary against a byte-identical copy of itself
    copy = os.path.join(build_dir, f"{an.KERNEL}.none_copy")
    shutil.copyfile(bins["none"], copy)
    shutil.copymode(bins["none"], copy)
    if hr.sha256(copy) != hr.sha256(bins["none"]):
        raise SystemExit("dsweep: the A/A copy is not byte-identical to the NONE binary")

    # timing, in a per-job shuffled order of d
    roles = an.roles_of(lad)
    order = timing_order(a.job, list(roles))
    partial = os.path.join(out_dir, an.PARTIAL_NAME)
    with open(partial, "w", encoding="utf-8") as f:   # the header; the d values follow as they finish
        f.write(json.dumps({"kind": "dsweep-partial", "schema_version": an.SCHEMA_VERSION, "plan_sha256": an.plan_sha256(),
                            "code_sha256": an.code_sha256(), "smoke": smoke, "reps_per_side": reps, "run": run,
                            "ladder": lad, "timing_order": order, "points_expected": len(order)}) + "\n")
    points, aa_doc = {}, None
    for d in order:
        t = time.time()
        append_partial(partial, {"starting": d})
        iters, one = hr.calibrate(bins["none"], d, a.cpu)
        args = [d, iters]
        fp = hr.pair(bins["none"], bins["fast"], args, reps, a.cpu)
        apr = hr.pair(bins["none_a64"], bins["fast_a64"], args, reps, a.cpu)
        instr, note = None, "not taken (--no-cachegrind)"
        if not a.no_cachegrind:
            ir_n, why_n = hr.instr_count(bins["none"], an.KERNEL, d, out_dir, f"d{d}.none")
            ir_f, why_f = hr.instr_count(bins["fast"], an.KERNEL, d, out_dir, f"d{d}.fast")
            if ir_n and ir_f:
                instr, note = {"none": ir_n, "fast": ir_f, "ratio": ir_f / ir_n, "unit": "instructions per kernel call, not time"}, "ok"
            else:
                note = f"none: {why_n}; fast: {why_f}"
        pt = make_point(d, roles[d], cache["l1d"], iters, one, fp, apr, instr, note,
                        {m: builds[m]["sha256"] for m in an.MODES})
        append_partial(partial, {"point": pt})   # kept even when the check below stops the job
        if not pt["checksum_match"]:
            raise SystemExit(
                f"dsweep: at d = {d} the builds print different checksums (NONE {fp['a_checksums']}, FAST {fp['b_checksums']}, "
                f"aligned NONE {apr['a_checksums']}, aligned FAST {apr['b_checksums']}). A build that computes something else "
                "cannot be timed against another, so the sweep stops here.")
        if d == lad["mid_d"]:
            pr = hr.pair(bins["none"], copy, args, reps, a.cpu)
            s = stats.summarize(pr["a_ns"], pr["b_ns"])
            aa_doc = {"d": d, "binary_sha256": hr.sha256(bins["none"]), "n_per_side": reps, "iters": iters,
                      "a_ns": pr["a_ns"], "b_ns": pr["b_ns"], "order": pr["order"], "ratio": s["ratio"],
                      "ci95": s["ci95"], "half_width_pct": s["half_width_pct"]}
            append_partial(partial, {"aa": aa_doc})
            if not pr["checksum_match"]:
                raise SystemExit(f"dsweep: the A/A pair printed different checksums at d = {d}: {pr['a_checksums']} {pr['b_checksums']}")
            print(f"[aa] d={d} ratio {s['ratio']:.4f} half-width {s['half_width_pct']:.3f}%", flush=True)
        points[d] = pt
        c, al = pt["as_compiled"], pt["aligned"]
        print(f"[time] d={d} ({'+'.join(roles[d])}) iters={iters} fast/none {c['ratio']:.3f} "
              f"[{c['ci95'][0]:.3f}, {c['ci95'][1]:.3f}] aligned {al['ratio']:.3f} [{al['ci95'][0]:.3f}, {al['ci95'][1]:.3f}]"
              + (f" Ir {instr['none']}/{instr['fast']}" if instr else "") + f" {time.time() - t:.0f}s", flush=True)
    if aa_doc is None:
        raise SystemExit(f"dsweep: the A/A was not timed (the middle d {lad['mid_d']} is not in the ladder)")

    doc = build_doc(smoke=smoke, reps=reps, cpu=a.cpu, run=run, cache=cache, lscpu=lscpu,
                    kernel={"source": info["source"], "loop_line": info["loop_line"]}, lad=lad, order=order,
                    builds=builds, aa=aa_doc, points=[points[d] for d in sorted(points)],
                    seconds=round(time.time() - t0, 1))
    path = os.path.join(out_dir, "dsweep.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    probs = [p for p in an.validate_doc(doc, reps=reps) if not (smoke and p.startswith("a smoke file"))]
    if probs:
        raise SystemExit("dsweep: the file just written does not pass its own schema check:\n  " + "\n  ".join(probs))
    os.remove(partial)   # everything in it is in dsweep.json now
    print(f"[done] {len(points)} points in {doc['seconds']}s -> {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
