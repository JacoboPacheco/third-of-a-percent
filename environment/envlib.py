"""Parsers and small pure functions for the environment column (no compiler, no runner needed to test them).

Everything that reads /proc or /sys is split into "read the text" and "parse the text", so the tests feed
the parsers literal text.
"""
import os
import re

STAT_FIELDS = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")


def parse_proc_stat(text):
    """{'cpu': {...}, 'cpu1': {...}} from /proc/stat text; each value a dict of jiffies plus 'total'."""
    out = {}
    for line in text.splitlines():
        if not re.match(r"cpu\d*\s", line):
            continue
        parts = line.split()
        nums = [int(x) for x in parts[1:]]
        d = {k: (nums[i] if i < len(nums) else 0) for i, k in enumerate(STAT_FIELDS)}
        d["total"] = sum(d[k] for k in STAT_FIELDS)  # guest time is already inside user/nice
        out[parts[0]] = d
    return out


def stat_delta(before, after):
    return {k: after[k] - before[k] for k in before if k in after}


def parse_cpuinfo(text):
    """List of {'processor': int, 'model name': str, 'cpu MHz': float|None} per processor block."""
    blocks, cur = [], {}
    for line in text.splitlines() + [""]:
        if not line.strip():
            if cur:
                blocks.append(cur)
                cur = {}
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            cur[k.strip()] = v.strip()
    out = []
    for b in blocks:
        if "processor" not in b:
            continue
        mhz = None
        try:
            mhz = float(b.get("cpu MHz", ""))
        except ValueError:
            pass
        out.append({"processor": int(b["processor"]), "model name": b.get("model name"), "cpu MHz": mhz})
    return out


def mhz_of(cpuinfo_text, cpu):
    for b in parse_cpuinfo(cpuinfo_text):
        if b["processor"] == cpu:
            return b["cpu MHz"]
    return None


def parse_cpu_list(s):
    """'0-1,3' -> [0, 1, 3]; '' -> []."""
    out = []
    for part in s.strip().split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            out.extend(range(int(lo), int(hi) + 1))
        else:
            out.append(int(part))
    return out


def shares_core(pinned, driver, siblings_of_pinned):
    """True when the driver's vCPU is a hyperthread sibling of the pinned vCPU (never when they are the same
    vCPU, which is reported separately). siblings_of_pinned: parsed thread_siblings_list of the pinned vCPU."""
    return driver is not None and driver != pinned and driver in siblings_of_pinned


def parse_cgroup_cpu_max(text):
    """'max 100000' -> quota None; '200000 100000' -> cpus 2.0."""
    parts = text.split()
    if len(parts) != 2:
        return None
    period = int(parts[1])
    quota = None if parts[0] == "max" else int(parts[0])
    return {"quota_us": quota, "period_us": period, "cpus": (quota / period) if quota is not None else None}


def parse_kv(text):
    out = {}
    for line in text.splitlines():
        p = line.split()
        if len(p) == 2:
            try:
                out[p[0]] = int(p[1])
            except ValueError:
                pass
    return out


def driver_cpu(proc_self_stat_text):
    """The CPU a process last ran on: field 39 of /proc/<pid>/stat (comm may hold spaces and parens)."""
    rest = proc_self_stat_text[proc_self_stat_text.rindex(")") + 2:].split()
    return int(rest[36])  # rest starts at field 3 (state); field 39 is index 36


def slug(model):
    s = (model or "unknown-cpu").lower()
    s = re.sub(r"\((r|tm|c)\)", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "unknown-cpu"


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except OSError:
        return None


def job_facts(pinned):
    """Static facts of the machine (reads /proc and /sys; every file optional)."""
    cpu_base = "/sys/devices/system/cpu"
    facts = {"online": read_text(f"{cpu_base}/online"), "os_cpu_count": os.cpu_count()}
    try:
        facts["affinity"] = sorted(os.sched_getaffinity(0))
    except AttributeError:
        facts["affinity"] = None
    facts["kernel"] = read_text("/proc/sys/kernel/osrelease")
    info = parse_cpuinfo(read_text("/proc/cpuinfo") or "")
    facts["cpu_model"] = info[0]["model name"] if info else None
    facts["cpuinfo_mhz_before"] = [b["cpu MHz"] for b in info]
    facts["cpufreq"] = {}
    for name in ("scaling_governor", "scaling_driver", "scaling_cur_freq", "scaling_min_freq", "scaling_max_freq",
                 "cpuinfo_min_freq", "cpuinfo_max_freq", "cpuinfo_cur_freq", "boost"):
        t = read_text(f"{cpu_base}/cpu{pinned}/cpufreq/{name}")
        if t is not None:
            facts["cpufreq"][name] = t
    t = read_text(f"{cpu_base}/cpufreq/boost")
    if t is not None:
        facts["cpufreq"]["global_boost"] = t
    t = read_text(f"{cpu_base}/intel_pstate/no_turbo")
    if t is not None:
        facts["cpufreq"]["intel_pstate_no_turbo"] = t
    topo = {}
    for c in sorted({0, pinned}):
        topo[str(c)] = {"thread_siblings_list": read_text(f"{cpu_base}/cpu{c}/topology/thread_siblings_list"),
                        "core_id": read_text(f"{cpu_base}/cpu{c}/topology/core_id"),
                        "package_id": read_text(f"{cpu_base}/cpu{c}/topology/physical_package_id")}
    facts["topology"] = topo
    t = read_text("/sys/fs/cgroup/cpu.max")
    facts["cgroup_cpu_max"] = parse_cgroup_cpu_max(t) if t else None
    t = read_text("/sys/fs/cgroup/cpu.stat")
    facts["cgroup_cpu_stat"] = parse_kv(t) if t else None
    q = read_text("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    if q is not None:
        facts["cgroup_v1_cfs_quota_us"] = q
    return facts
