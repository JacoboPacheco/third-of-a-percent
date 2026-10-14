# Environment: what the shared runner did while the timing ran, and does it move any ratio?

Written Tue Oct 13 2026 (time in the commit message), BEFORE any run. Exploratory and descriptive. No environment number from this study exists when this is committed.

## Question
Open gap: the harness pins one vCPU with `taskset` and uses ABBA order, but never recorded CPU frequency, steal time, the hyperthread topology, the governor, or the cgroup CPU limit. Every ratio on the page assumes the two builds saw the same machine. This column records the machine and asks, per CPU model, whether anything below could move a reported ratio.

## What is recorded
Once per job (`environment.json`, `facts`): `lscpu`, `/proc/cpuinfo` model name, flags of the first CPU not stored (size), kernel version, number of online CPUs (`/sys/devices/system/cpu/online`, `os.cpu_count()`), the driver's affinity mask, cgroup `cpu.max` and `cpu.stat` (v2, or v1 `cpu.cfs_quota_us`) if present, cpufreq files if present (`scaling_governor`, `scaling_driver`, `cpuinfo_min/max_freq`, `scaling_cur_freq`, `boost`, `intel_pstate/no_turbo`), `/sys/devices/system/cpu/cpu*/topology/thread_siblings_list` for the pinned vCPU (1) and the vCPU the Python driver runs on (read from `/proc/self/stat` at each sample, 0 expected), hypervisor line of lscpu.
Per timed process (`samples`): the `cpu1` and aggregate lines of `/proc/stat` before and after (user, system, iowait, steal, total jiffies; USER_HZ = 100, so one tick is 10 ms, coarse against a ~75 ms process), `cpu MHz` of the pinned vCPU from `/proc/cpuinfo` and `scaling_cur_freq` if present, read right after the process, and the side (NONE or FAST), cell, rep number and wall ns.
Timed: the same eight kernels (`kernels/`, built by `harness/run.py:build_kernel`, imported and unchanged), `-O2 -std=c++20 -stdlib=libc++`, NONE and FAST as-compiled, sizes L1 and L2, 20 processes per side per cell, ABBA, `taskset -c 1` through `run.run_bin`, iteration counts from `run.calibrate` on NONE only. No A/A, aligned, NOVEC or Cachegrind here: those are not needed to ask the question. Matrix of 10 jobs on ubuntu-24.04.

## Definitions fixed now ("large")
- Steal-affected process: its pinned-vCPU steal delta is at least one jiffy (10 ms). Job steal share: sum of steal deltas over sum of total deltas of the pinned vCPU, across all timed processes. LARGE steal: a job's steal share above 0.5 %.
- Frequency, two comparisons per job (medians of the per-process MHz readings): between the first and second half of the job's processes in time order, and between the NONE processes and the FAST processes. LARGE drift: a relative difference above 1 % in either comparison. Constant readings (a VM reporting the nominal MHz every time) are reported as "constant", not as evidence of no drift: `cpu MHz` inside a VM may be the host's nominal value.
- Shared core: the pinned vCPU 1 appears in the `thread_siblings_list` of the driver's vCPU. Reported per CPU model; a shared core is not by itself LARGE.
- Re-estimate: per CPU model, pool the processes of its jobs per cell, compute FAST/NONE (ratio of medians, percentile bootstrap, `harness/stats.py`) with every process and again without steal-affected processes. A cell's verdict MOVES when (a) the point ratio without them lies outside the interval of the full sample, or (b) its class flips: for the lost kernels (`k04_rev`, `k05_stride2`, `k08_matmul`) `ci95_lo` >= 1.5 (the `lost_ci_lo_min_ratio` of `harness/criteria-v3.json`), for the forward kernels (`k01_sum_fwd`, `k02_add_fwd`, `k03_stencil`) point ratio <= 1.02 (`forward_point_max_ratio`). `k06_gather` and `k07_hist` are reported, not classed. If fewer than 10 processes per side remain in a cell, the cell is "too few left" and not judged.
This is pooling by concatenating processes of a CPU model, not the two-level bootstrap of `harness/pool.py`; it is a descriptive check, not a new verdict.

## What would change the page text
Nothing changes unless, for some CPU model, a LARGE steal or LARGE drift is found AND at least one cell's verdict MOVES under the re-estimate. In that case a limits line naming the model is written separately; this column makes no edit itself (it owns only `environment/` and its workflow). If nothing is LARGE, or nothing moves, the result is one sentence for the limits part ("steal, frequency and core sharing were recorded on N jobs; none large enough to move a ratio") and nothing else. An environment with a shared core or a cgroup quota is reported as a fact, not a finding of harm. No rule is changed after a result.

## Limits
Jiffy-resolution steal; a guest's view of frequency and steal depends on the hypervisor (Azure Hyper-V on GitHub runners may report neither); one reading per process cannot see bursts inside it; 10 jobs draw whatever CPU models the pool gives; the effect of environment is measured on the as-compiled pair only; no causal claim from correlation of steal with ratio. 20 processes per side is the harness's old size (criteria-v3 uses 40); chosen to keep jobs short.

## Run
In the repository: `gh workflow run environment.yml`, then download the `environment-analysis` artifact (`analysis.json`, `report.txt`). Offline: `python environment/check.py`.
