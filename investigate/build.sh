#!/usr/bin/env bash
# Builds every k02_add_fwd variant for the investigation into <out dir> (default investigate/build).
# Each variant changes ONE thing against the harness builds (same compiler, same flags):
#   none, fast           exactly the harness commands (sha256 must equal the measured binaries)
#   none_a64, fast_a64   + -falign-loops=64   (every loop starts on a 64-byte boundary)
#   none_il1             NONE + -mllvm -force-vector-interleave=1 (the FAST loop shape, without the check)
#   fast_il2             FAST + -mllvm -force-vector-interleave=2 (the NONE loop shape, with the check)
#   probe_none, probe_fast  investigate/k02_probe.cpp: the same kernel, placement of a, b, c controlled
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${1:-investigate/build}
mkdir -p "$OUT"
CXX=clang++-18
COMMON="-O2 -std=c++20 -stdlib=libc++"
NONE="-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE"
FAST="-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"
REM="-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize"
SRC=kernels/k02_add_fwd.cpp
A64="-falign-loops=64"
b() {
  local name=$1; shift
  if ! $CXX $COMMON "$@" $REM -o "$OUT/$name" "${SRC_OVERRIDE:-$SRC}" 2> "$OUT/$name.remarks.txt"; then
    tail -n 20 "$OUT/$name.remarks.txt"; return 1
  fi
}
b none $NONE
b fast $FAST
b none_a64 $NONE $A64
b fast_a64 $FAST $A64
b none_il1 $NONE -mllvm -force-vector-interleave=1
b fast_il2 $FAST -mllvm -force-vector-interleave=2
SRC_OVERRIDE=investigate/k02_probe.cpp b probe_none $NONE
SRC_OVERRIDE=investigate/k02_probe.cpp b probe_fast $FAST
cd "$OUT"
sha256sum none fast none_a64 fast_a64 none_il1 fast_il2 probe_none probe_fast | tee sha256.txt
for v in none fast none_a64 fast_a64 none_il1 fast_il2 probe_none probe_fast; do
  echo "== $v: $(grep -h 'k02_add_fwd.cpp:6:.*vectorized loop' $v.remarks.txt | sed 's/.*remark: //')"
  objdump -d --no-show-raw-insn "$v" | awk '/<_Z[0-9]+kern_k02_add_fwd/{k=1} k&&/^$/{k=0} k' > "$v.kern.s"
done
