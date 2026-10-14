#!/usr/bin/env bash
# Install clang-N and libc++-N from apt.llvm.org on ubuntu-24.04 (noble). Usage: versions/install.sh N
# Source: https://apt.llvm.org/ (key https://apt.llvm.org/llvm-snapshot.gpg.key, repository
# http://apt.llvm.org/noble/ llvm-toolchain-noble-N). If the repository lacks a package the job fails
# loudly; nothing is substituted. Prints the installed versions.
set -euo pipefail
N="${1:?usage: install.sh N}"
case "$N" in (*[!0-9]*|"") echo "bad version $N" >&2; exit 2;; esac
sudo install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://apt.llvm.org/llvm-snapshot.gpg.key | sudo tee /etc/apt/keyrings/apt.llvm.org.asc >/dev/null
echo "deb [signed-by=/etc/apt/keyrings/apt.llvm.org.asc] http://apt.llvm.org/noble/ llvm-toolchain-noble-$N main" \
  | sudo tee "/etc/apt/sources.list.d/llvm-$N.list" >/dev/null
sudo apt-get update -qq
sudo apt-get install -y -qq "clang-$N" "libc++-$N-dev" "libc++abi-$N-dev" "libunwind-$N-dev" valgrind python3-numpy
"clang++-$N" --version
dpkg-query -W "clang-$N" "libc++-$N-dev" "libc++abi-$N-dev" "libunwind-$N-dev" valgrind
