# Why clang does not vectorize the reverse and stride-2 loops under libc++ FAST

Compile-only notes. Nothing here was timed. Every compile ran on the public Compiler Explorer API
(godbolt.org). Every answer is saved in `raw/`, and `python verify.py` checks the quotations below
against those files without any network access.

## Question

With libc++ hardening mode FAST, the project's reverse loop (`k04_rev`) and stride-2 loop
(`k05_stride2`) are not vectorized by clang 18.1.0 (x86-64 baseline, `-O2`). With the checks off (NONE)
both are vectorized. The forward loops bounded by `size()` stay vectorized. The only message is one line,
"could not determine number of loop iterations". This folder looks for the pass and the analysis result
behind that line, tests the project's up-front-check rewrites against it, and compares clang 19, 20, 21
and trunk.

Labels used below: **OBSERVED** (a quotation from a saved raw file, with the file named, or a number
`verify.py` recomputes from the raw files), **INFERRED** (a reading that needs knowledge beyond the saved
files, with its basis stated), **NOT ESTABLISHED**. Statements about how LLVM works internally that rest on
knowledge of its source code are INFERRED: no LLVM source file is saved here.

## Short answer

Setup for every sentence: clang 18.1.0, x86-64 baseline (SSE2), `-O2`, libc++ FAST, int32 elements, unless
the sentence names another version. Items 2 to 6 contain inferred parts, marked there. The findings (F1 to F10)
hold the evidence.

1. A FAST check is a branch inside the loop to a block that calls `llvm.trap` and ends in `unreachable`.
   Each such branch is one more exit of the loop (F2, F4).
2. Over the 29 loops compiled with FAST on clang 18.1.0, a loop was vectorized exactly when ScalarEvolution
   had an exit count for every exit: all 16 loops with a count for every exit were vectorized, and none of
   the 13 loops with an uncounted exit was (F4). The second half restates the remark, which says the iteration
   count could not be determined. The first half is the independent one. In hand-written IR where only the
   expression of the bound changes, the loop vectorizer of `opt` 18.1.0 vectorized the loop exactly when the
   exit had a count, in all 14 functions (F7). INFERRED, from knowledge of the LLVM source: the vectorizer
   needs a backedge-taken count, which exists only when every exit has one; it is the smallest of the exit
   counts. In the forward loops bounded by `size()` the counts of the trap exits enter the vector trip count, and the traps stay
   in the scalar remainder (F3).
3. In the reverse and stride-2 loops, at least one exit has no count (`***COULDNOTCOMPUTE***`), so the
   backedge-taken count is unpredictable. The loop-access analysis prints that SCEV could not compute the exit
   count, and the remark follows that line (F4). INFERRED: the remark is that analysis's report.
4. **Reverse loop.** `IndVarSimplify` replaces the check by a test on the counter's first value. The branch on
   that loop-invariant condition stays inside the loop, and its exit has no count (F5). INFERRED: the counter
   only decreases, so the original check could only fail on the first iteration. `SimpleLoopUnswitch` runs
   earlier in the pipeline than `IndVarSimplify`, no unswitching pass runs between `IndVarSimplify` and the
   vectorizer, and the final assembly keeps the branch in the loop. Running loop unswitching just before the
   vectorizer on the saved IR makes the reverse loop vectorize on clang 18, 20 and trunk. Inserting one
   `simple-loop-unswitch<no-nontrivial;trivial>` pass into the full -O2 pipeline of `opt` 18.1.0, after the
   `indvars` group or just before the vectorizer, does the same on the front end's IR. The stride-2 loop does
   not change in either test (F5, F6).
5. **Stride-2 loop.** The two checks compare `2*i` and `2*i+1` with the size of `a`, and neither has a count.
   The size of a vector is an arithmetic shift of a pointer difference, and the unsigned range ScalarEvolution
   prints for it starts below zero (INFERRED reading: the range wraps around zero). In hand-written C++ with
   one check, limiting the bound (a mask, `std::min` or `__builtin_assume`) or writing the check on the counter
   gives a count and the loop vectorizes. With two checks, the mask gives all three exits a count. The mask also changes the compare the compiler builds, so
   these tests alone do not separate a range effect from a compare-form effect. In hand-written IR with one
   fixed compare form, a bound with a known unsigned maximum (`and`, `lshr`, `umin`) gets a count on `opt`
   18.1.0, 20.1.0 and trunk, and a full-range or `ashr` bound does not. The rule inside ScalarEvolution
   that this points to is INFERRED; it was not observed directly (F7).
6. The project's up-front-check rewrites (F8). Reverse: the in-loop checks of `v_rev_pre` and `v_rev_span` are
   proved true by `ConstraintElimination` and deleted by `LoopSimplifyCFG`, which leaves one counted exit
   (INFERRED reason: the up-front check dominates the loop). Raw pointers (`v_rev_raw`, `v_s2_raw`) leave no
   check in the loop. Stride-2 with `std::span` (`v_s2_span`): one check stays in the loop, and its exit has a
   count. Its bound is an `lshr exact`, which INFERRED is why, in line with the hand-written IR of F7. A
   precondition on `a.size() / 2` or `2 * n` (`v_s2_pre`, `v_s2_pre_mul`) leaves both stride-2 checks, and
   neither has a count.
7. Clang 19.1.0 prints the same message. Clang 20.1.0, 21.1.0 and trunk print other remarks, which contain
   "early exit loop"; the debug output of clang 20.1.0 uses the word "uncountable". The loops still fail on
   every version tried. For the reverse, stride-2 and forward add loops, the IR before the vectorizer on 19.1.0,
   20.1.0 and trunk has the same blocks, operations and trap branches as on 18.1.0 apart from spelling (trunk
   also has `llvm.assume` calls), and the same two loops have uncounted exits on 19.1.0, 20.1.0 and trunk (F9).
8. The loop-shape effect does not depend on libc++ writing the check. Hand-written in-loop traps on raw
   pointers give the same result on clang 18.1.0: reverse and stride-2 lost, forward kept (F10).

## Setup

| item | value |
|---|---|
| compilers (Compiler Explorer ids) | `clang1810` 18.1.0 (an 18.1.0 release candidate, see Not established), `clang1910` 19.1.0, `clang2010` 20.1.0, `clang2110` 21.1.0, `clang_trunk`; assertion builds `clang181assert` (18.1.0) and `clang201assert` (20.1.0); `opt1810`, `opt1910`, `opt2010`, `opttrunk` |
| flags | `-O2 -std=c++20 -march=x86-64 -stdlib=libc++ -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST` (or `..._NONE`), `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize` |
| debug info | Compiler Explorer adds `-g`. Runs that print IR add `-g0` after it. The remarks of the 11 pairs of runs with and without `-g0` are identical |
| sources | `sources/kernels.cpp`: the project's `k01` to `k05` loop functions, copied verbatim (`make_sources.py --check`). `sources/variants.cpp`, `sources/variants2.cpp`, `sources/variants3.cpp`: the variants of F7, F8 and F10. `sources/handwritten/s2-bound.ll`: hand-written IR (F7) |
| libc++ | the one Compiler Explorer ships with each compiler. Only the hardening macro taking effect was checked: on clang 18.1.0 the FAST build has one `ud2` in each of the four checked project loop functions (`k02` to `k05`) and none in the forward sum, and the NONE build has none (`raw/A-c18-kernels-fast.json`, `raw/A-c18-kernels-none.json`). The trap call of the forward sum is removed by `JumpThreadingPass` (`extracted/pass-events-clang18-fast.txt`) |
| trunk | Compiler Explorer's trunk compiler. Version line recorded on 2026-10-16 at 00:41 UTC: clang 24.0.0git, commit `efd49657`, installed in a directory named `clang-trunk-20261015` (`raw/V-ctrunk-version.json`); `opt` trunk prints LLVM 24.0.0git without a commit (`raw/V-opttrunk-version.json`). The trunk answers of groups A, B, E and F were fetched on 2026-10-16 from 00:00:10 to 00:09:56 UTC (`fetched_at` in each raw file), before the version lines. Whether one build served all of them is NOT ESTABLISHED (`extracted/trunk-versions.txt`) |

Raw file names: `A-` clang remarks, `B-` IR printed before the loop vectorizer
(`-mllvm -print-before=loop-vectorize`), `C-` the pass pipeline viewer (IR before and after every pass, gzip),
`D-` assertion builds with `-mllvm -debug-only=...`, `E-` `opt -passes=print<scalar-evolution>` on the IR of
group B, `F-` `opt` running the loop vectorizer alone or after loop unswitching on the IR of group B, `G-` the
full -O2 pipeline of `opt` 18.1.0 on the front end's IR, `H-` `opt` on hand-written IR, `V-` the version line of
trunk.

## Findings

### F1. The remark, with the checks off and on (OBSERVED)

- `raw/A-c18-kernels-none.json`: ``<source>:23:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]`` is the reverse loop, and ``<source>:27:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]`` is the stride-2 loop.
- `raw/A-c18-kernels-fast.json`: ``<source>:23:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]`` and ``<source>:27:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]``.
- `raw/A-c18-kernels-fast.json`: the forward add loop keeps SIMD: ``<source>:15:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]``.

### F2. IR just before the loop vectorizer, clang 18.1.0 FAST (OBSERVED)

Each check is a conditional branch to a block with a trap. All dumps: `extracted/ir-before-loop-vectorizer-clang18-fast.txt`. For every loop of this folder, `extracted/checks-in-loops.txt` lists each trap branch, its exit count and the instructions that compute its condition.

- Reverse loop, `raw/B-c18-kernels-fast-ir.json`: ``%20 = icmp ult i64 %19, %18, !dbg !95`` is computed before the loop (it compares `n - 1` with the size of `c`). Inside the loop: ``br i1 %20, label %26, label %25, !dbg !98, !prof !100``. The failing target holds ``tail call void @llvm.trap(), !dbg !98``. No `phi` is among the instructions that compute `%20`, so the condition does not depend on the loop counter (`extracted/checks-in-loops.txt`, `kern_k04_rev`).
- Forward add loop, `raw/B-c18-kernels-fast-ir.json`: two trap branches on the counter itself, ``%32 = icmp eq i64 %31, %19, !dbg !43`` and ``%35 = icmp eq i64 %31, %26, !dbg !46``.
- Stride-2 loop, `raw/B-c18-kernels-fast-ir.json`: two trap branches on derived values, ``%24 = shl i64 %23, 1, !dbg !114``, ``%25 = icmp ugt i64 %18, %24, !dbg !115`` and ``%29 = icmp ugt i64 %18, %28, !dbg !118`` (`%28` is `%24` or 1).
- With the checks off, `raw/B-c18-kernels-none-ir.json`: the reverse loop has a single exit, ``br i1 %22, label %13, label %15, !dbg !94, !llvm.loop !105``.

So the three FAST loops have three different kinds of extra exit: a test of the counter against a
loop-invariant value (forward), a loop-invariant test with no counter in it (reverse), and tests of
`2*i` and `2*i|1` (stride-2).

### F3. Forward loops bounded by `size()`: the exit counts go into the vector trip count (OBSERVED, reading INFERRED)

- `raw/A-c18-kernels-fast.json`, assembly of the forward add: ``cmovae  r10, rdx`` and ``cmovae  r10, rcx`` clamp one value in `r10` against two sizes.
- `raw/A-c18-kernels-fast.json`, same function: the vector loop `.LBB1_9` holds no trap. The function's only ``ud2`` follows the scalar remainder loop (`extracted/asm-clang18.txt`).
- INFERRED reading: `r10` is the smallest of the three exit counts, which is what ScalarEvolution reports in F4.
- Clang 20.1.0's debug output is consistent with this reading. For k02 and k03 it prints ``LV: Loop requires scalar epilogue: not exiting from latch block`` in `raw/D-c20assert-kernels-fast-lv.json`. The line says only that a scalar epilogue is needed because an exit is not the latch. It does not show where the traps are or how the vector trip count is formed.

### F4. ScalarEvolution: which exits have a count (OBSERVED, links INFERRED)

`opt -passes=print<scalar-evolution>` (same release as the compiler) on the IR of F2. The exits are named
by the basic-block names of `sources/ir/*.ll`. Full table: `extracted/scalar-evolution.txt`.

- Forward add, `raw/E-c18-kernels-fast-scev.json`: ``Loop %bb30: <multiple exits> backedge-taken count is (%17 umin_seq %24 umin_seq (-1 + (1 umax %10)))``. Every exit has a count.
- Reverse loop, `raw/E-c18-kernels-fast-scev.json`: ``Loop %bb23: <multiple exits> Unpredictable backedge-taken count.`` and ``exit count for bb23: ***COULDNOTCOMPUTE***``. The latch exit has one: ``exit count for bb26: (-1 + %9)<nsw>``.
- Stride-2 loop, `raw/E-c18-kernels-fast-scev.json`: ``Loop %bb22: <multiple exits> Unpredictable backedge-taken count.``. Both trap exits, ``exit count for bb22: ***COULDNOTCOMPUTE***`` and ``exit count for bb27: ***COULDNOTCOMPUTE***``, have none.
- Reverse loop with the checks off, `raw/E-c18-kernels-none-scev.json`: ``Loop %bb15: backedge-taken count is (-1 + %9)<nsw>``. One exit, with a count.

The loop-access analysis prints the same fact in the assertion build, and the remark of F1 follows it. `raw/D-c18assert-kernels-fast-lv-laa.json`, one run with `-debug-only=loop-vectorize,loop-accesses`: ``LAA: Found a loop in _Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_: for.body`` is followed by ``LAA: SCEV could not compute the loop exit count.``. The remark ``could not determine number of loop iterations`` comes next, then ``LV: Can't vectorize due to memory conflicts`` (order in `extracted/debug-output.txt`). The stride-2 loop gets the same sequence. No other loop of that run prints the ``LAA: SCEV could not compute the loop exit count.`` line.
INFERRED: the remark of F1 is that analysis's report. The basis is the order of the messages, the two loops that print the line being the two loops named by the remark, and the matching wording; the link itself comes from knowledge of the LLVM source.

Correlation over every loop compiled with FAST on clang 18.1.0, 29 loops (5 project loops, 14 loops of
`sources/variants.cpp`, 4 of `sources/variants2.cpp`, 6 of `sources/variants3.cpp`): 16 loops have a count for
every exit and all 16 are vectorized. 13 loops have an exit without a count and none of the 13 is vectorized.
Clang 19.1.0, 20.1.0 and trunk, project loops: 3 and 2, no exception. Clang 20.1.0, `variants.cpp`: 7 and 7.
Checks off, clang 18.1.0: 5 loops, all counted and vectorized. Table: `extracted/scalar-evolution.txt` (the
`tally` lines).
How much this shows. The "not counted, not vectorized" half is the fact the remark states in other words, so it
is not independent evidence. The "counted, vectorized" half is independent. Neither half shows that a count is
required: that is the INFERRED reading of item 2. A one-factor test of the link, with the same loop and only the
bound changed, is in F7. F6 removes the uncounted exit (it hoists the branch) instead of giving it a count.

On clang 18.1.0 the line `LV: We can vectorize this loop!` is printed for the reverse and stride-2 loops
although legality then fails: it stands between `LV: Can't vectorize due to memory conflicts` and
`LV: Not vectorizing: Cannot prove legality.` (`extracted/debug-output.txt`). Why it is printed there is
NOT ESTABLISHED.

### F5. The reverse loop: `IndVarSimplify` turns the check into a loop-invariant branch (OBSERVED)

- `raw/C-c18-kernels-fast-pipeline.json.gz`, reverse loop, IR before `IndVarSimplifyPass`: the check is a compare of the counter, ``%24 = icmp ugt i64 %18, %23`` and ``br i1 %24, label %26, label %25``. After the pass, the compare is made once before the loop and the branch uses it: ``%20 = icmp ult i64 %19, %18`` and ``br i1 %20, label %27, label %26``. Both listings: `extracted/pipeline-clang18-fast.txt`.
- `raw/D-c18assert-kernels-fast-indvars.json`, assertion build: ``Unknown exit count: Replacing   %cmp.i11 = icmp ugt i64 %sub.ptr.div.i.i10, %dec, !dbg !30 with   %cmp.i11.first_iter = icmp ult i64 %4, %sub.ptr.div.i.i10, !dbg !26``. The compare is the reverse loop's check (`%dec` is the decremented counter). It is the only line of that kind in the output.
- The pipeline order, `raw/C-c18-kernels-fast-pipeline.json.gz`: ``SimpleLoopUnswitchPass on <unnamed loop>`` runs at position 43, ``IndVarSimplifyPass on <unnamed loop>`` at 49, and ``LoopVectorizePass on _Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_`` at 90. No unswitching pass runs between 49 and 90 (`verify.py` checks this). The textual pipeline of `opt` 18.1.0 has the same order: one `simple-loop-unswitch` before the `indvars` group (`extracted/full-pipeline-unswitch.txt`).
- The final assembly keeps the invariant compare inside the loop, `raw/A-c18-kernels-fast.json`: ``lea     rdi, [rcx - 1] .LBB3_2: cmp     rdi, rsi jae     .LBB3_5``. The register `rdi` is set once, before the label `.LBB3_2` of the loop, and the compare and the jump to the `ud2` run on every iteration (`extracted/asm-clang18.txt`).

INFERRED: SCEV has no exit count for the original compare because its counter only decreases while the
test is "counter below size", and the exit count of a condition that does not depend on the counter cannot be
expressed. The pass reports "Unknown exit count" before it rewrites. The loops of
`sources/variants.cpp` support the reading: `v_rev_j` (the counter counts up, the index `n - 1 - j` counts
down) fails in the same way, and `v2_rev_masked` (the size of `c` masked, see F7) still has no count
(`extracted/scalar-evolution.txt`).

### F6. Unswitching before the vectorizer makes the reverse loop vectorize (OBSERVED)

Two experiments, each with the `opt` of the same release as the compiler.

**On the saved IR before the vectorizer.** The input is the text of the dump of F2 as a module, with debug
locations (`!dbg`), TBAA, branch weights (`!prof`), loop metadata (`!llvm.loop`) and call-site attribute groups
removed, and `!srcloc`, `!noundef`, `!nonnull`, `!range` and `!align` metadata removed too (none of these five
occurs in the dumps). Function attributes and instruction flags are kept (`extract.py`, `sanitize`;
`extracted/ir-metadata-removed.txt`).

- `raw/F-c18-kernels-fast-lv-only.json`, loop vectorizer alone: ``remark: <unknown>:0:0: loop not vectorized: could not determine number of loop iterations`` appears twice, and only `kern_k04_rev` and `kern_k05_stride2` have no `vector.body` block in the output. This reproduces the compiler's decision for all five loops, so the saved IR is a fair input.
- `raw/F-c18-kernels-fast-unswitch-then-lv.json`, `loop-mssa(simple-loop-unswitch),loop-vectorize`: the same remark appears once. `kern_k04_rev` now has a `vector.body` block. `kern_k05_stride2` does not.

| compiler | loop vectorizer alone | unswitch, then vectorizer |
|---|---|---|
| clang 18.1.0 (`opt1810`) | reverse not vectorized, stride-2 not vectorized | reverse **vectorized**, stride-2 not vectorized |
| clang 20.1.0 (`opt2010`) | same | same |
| trunk (`opttrunk`) | same | same |

All other loops (sum, add, stencil) are vectorized in both columns. Details: `extracted/unswitch-before-vectorizer.txt`.

**In the full -O2 pipeline.** `raw/G-opt1810-print-O2-pipeline.json` holds the textual pipeline of `opt` 18.1.0
(`-passes=default<O2> -print-pipeline-passes`). It is run on the IR clang 18.1.0 prints with
`-O2 -disable-llvm-passes` (`raw/G-c18-kernels-fast-frontend-ir.json`), with all metadata kept. Three runs:
unchanged (control), with `loop-mssa(simple-loop-unswitch<no-nontrivial;trivial>)` inserted right after
`loop(loop-idiom,indvars,loop-deletion,loop-unroll-full)`, and with it inserted just before
`loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>`. The parameters `no-nontrivial;trivial`
are the pass's own: INFERRED reading, trivial unswitching only.

| function | control | unswitch after `indvars` | unswitch before the vectorizer |
|---|---|---|---|
| `kern_k01_sum_fwd`, `kern_k02_add_fwd`, `kern_k03_stencil` | vectorized | vectorized | vectorized |
| `kern_k04_rev` | not vectorized | **vectorized** | **vectorized** |
| `kern_k05_stride2` | not vectorized | not vectorized | not vectorized |

- `raw/G-opt1810-full-O2-control.json`: ``remark: <unknown>:0:0: loop not vectorized: could not determine number of loop iterations`` appears twice. The control reproduces the compiler's decisions for the five loops.
- `raw/G-opt1810-full-O2-unswitch-after-indvars.json`: the same remark appears once, and `kern_k04_rev` has a `vector.body` block. The remark ``remark: <unknown>:0:0: vectorized loop (vectorization width: 4, interleaved count: 2)`` appears twice in this run (the stencil and the reverse loop) and once in the control.
- Details, with the remarks of each run: `extracted/full-pipeline-unswitch.txt`.

What these show: the invariant branch inside the loop is what stops the vectorizer of the reverse loop, and
hoisting it is enough, on the saved IR and in the full pipeline of `opt` 18.1.0 with all metadata kept.
What they do not show: that clang's own driver would produce the same code (the pipeline is the text `opt`
prints, and the control reproduces the compiler's five decisions), or that LLVM would accept the extra pass in
its default pipeline.

### F7. The stride-2 loop: no count for `2*i` and `2*i+1`; what gives one (OBSERVED, rule INFERRED)

**Hand-written C++ loops** on raw pointers with in-loop `__builtin_trap` checks, clang 18.1.0 FAST
(`sources/variants2.cpp`, `sources/variants3.cpp`). The `REQUIRE(n <= SIZE_MAX / 2)` guard tells the compiler
that `2*n` cannot wrap: the `shl` in `v2_s2_guard` has `nuw`, and the `shl` of `kern_k05_stride2` has not
(`extracted/checks-in-loops.txt`). "Mask" is `a.size() & (SIZE_MAX >> 1)`, which changes nothing for a real vector.

| function | in-loop checks | bound | clang 18.1.0 | compare of the check in the IR before the vectorizer |
|---|---|---|---|---|
| `v2_s2_guard` (guard) | one, `2*i+1 >= an` | size | not vectorized | `(2*i)\|1` against the size, unsigned `<` |
| `v2_s2_guard_masked` (guard) | one | mask | vectorized | counter `==` `(size >> 1)` masked |
| `v2_s2_masked` | one | mask | vectorized | counter `==` `(size >> 1)` masked |
| `v3_one_plain` | one | size | not vectorized | `(2*i)\|1` against the size, unsigned `<` |
| `v3_one_half` | one, written `i >= an / 2` | size | vectorized | counter `==` `(size >> 1)` |
| `v3_one_min` | one | `std::min(size, 2^40)` | vectorized | counter `==` `(min >> 1)` |
| `v3_one_assume` | one | size, assumed `< 2^40` | vectorized | counter `==` `(size >> 1)` |
| `v3_two_plain` | two, `2*i` and `2*i+1` | size | not vectorized | both `<` against the size |
| `v3_two_masked` | two | mask | vectorized | both counter `==` form |
| `v2_rev_masked` (reverse loop) | one, `i >= cn` | mask on `c.size()` | not vectorized | loop-invariant compare |

- `raw/A-c18-variants2-fast.json`: ``<source>:21:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]`` (`v2_s2_guard`), ``<source>:34:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]`` (`v2_s2_guard_masked`), ``<source>:46:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]`` (`v2_s2_masked`), ``<source>:57:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]`` (`v2_rev_masked`).
- `raw/A-c18-variants3-fast.json`: ``<source>:19:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]`` (`v3_one_plain`), ``<source>:31:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]`` (`v3_one_half`), ``<source>:43:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]`` (`v3_one_min`), ``<source>:56:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]`` (`v3_one_assume`), ``<source>:68:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]`` (`v3_two_plain`), ``<source>:81:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]`` (`v3_two_masked`).
- `raw/E-c18-variants2-fast-scev.json`: without the mask, ``exit count for bb25: ***COULDNOTCOMPUTE***``. With it, ``exit count for bb27: (zext i62 (trunc i64 (%15 /u 2) to i62) to i64)``.
- `raw/E-c18-variants3-fast-scev.json`, two checks without the mask: ``exit count for bb22: ***COULDNOTCOMPUTE***`` and ``exit count for bb27: ***COULDNOTCOMPUTE***``. With the mask, all three exits have a count: ``exit count for bb26: ((1 + (zext i63 (trunc i64 %12 to i63) to i64))<nuw> /u 2)`` and ``exit count for bb31: ((zext i63 (trunc i64 %12 to i63) to i64) /u 2)``.
- The compare form changes with the mask. `raw/B-c18-variants2-fast-ir.json`, `v2_s2_guard`: ``%29 = icmp ult i64 %28, %16``, with `%28` the counter shifted left by one and or-ed with 1. `v2_s2_guard_masked`: ``%29 = icmp eq i64 %28, %22``, with `%28` the counter itself and `%22` the masked halved size. The instructions that compute each condition: `extracted/checks-in-loops.txt`. So the C++ tests above change two things at once, the range of the bound and the form of the compare. `v3_one_half` has the counter form with a full-range bound, and it has a count.
- The size comes from a pointer difference, `raw/E-c18-variants2-fast-scev.json`: ``%9 = ashr exact i64 %8, 2``. The range ScalarEvolution prints for it, same file: ``%9 U: [-2305843009213693952,2305843009213693952) S: [-2305843009213693952,2305843009213693952)``. The halved masked bound is a different value, ``%19 = and i64 %18, 4611686018427387903 --> (zext i62 (trunc i64 (%15 /u 2) to i62) to i64) U: [0,4611686018427387904)`` in the same file.
- The span variant of the project's rewrites (F8) also has a count. `raw/E-c18-variants-fast-scev.json`: ``exit count for bb29: ((1 umax (((-1 * (ptrtoint ptr %4 to i64)) + (ptrtoint ptr %3 to i64)) /u 2)) /u 2)``.
- Its bound is a logical shift, not an arithmetic one, `raw/B-c18-variants-fast-ir.json`: ``%20 = lshr exact i64 %8, 1, !dbg !278``. A logical shift of a byte count has an unsigned maximum below 2^63. INFERRED: that is why this variant has a count.

**Hand-written IR with one fixed compare form** (`sources/handwritten/s2-bound.ll`, written by
`make_s2_bound.py`). One stride-2 loop, one check `bound > ((i << 1) | 1)` as an unsigned compare, the same in
all 14 functions. Only the expression of the bound differs, and whether the shift has `nuw`. Result
(`extracted/handwritten-bound.txt`): the same on `opt` 18.1.0, 20.1.0 and trunk, and the same with and without
`nuw`.

| bound | exit count | loop vectorizer of `opt` 18.1.0 |
|---|---|---|
| the argument as it is (`full`) | none | not vectorized |
| `ashr` of the argument by 2 | none | not vectorized |
| `ashr exact (end - begin), 2` (`ptr_ashr`, the bound of `k05`) | none | not vectorized |
| `lshr` of the argument by 1 | yes | vectorized |
| `and` with 2^62 - 1 | yes | vectorized |
| `umin` with 2^40 | yes | vectorized |
| `lshr exact (end - begin), 1` (`ptr_lshr`, the bound of `v_s2_span`) | yes | vectorized |

- `raw/H-opt1810-s2-bound-scev.json`: ``Loop %loop: <multiple exits> Unpredictable backedge-taken count.`` for the functions with no count, and for example ``exit count for loop: ((1 umax (zext i62 (trunc i64 %an to i62) to i64)) /u 2)`` for the `and` bound.
- `raw/H-opt1810-s2-bound-lv.json`: the loop vectorizer alone vectorizes the 8 functions with a count and not the other 6. The remark ``remark: <unknown>:0:0: vectorized loop (vectorization width: 4, interleaved count: 1)`` appears 8 times in it, and the remark ``remark: <unknown>:0:0: loop not vectorized: could not determine number of loop iterations`` appears 6 times (`verify.py` counts both).

This is the same-form evidence for the bound: with the compare form held fixed, a bound with a known unsigned
maximum gives the exit a count and a full-range or `ashr` bound does not, and the vectorizer's decision follows
the count. The shift flag `nuw` makes no difference to the result.

OBSERVED: a limited bound, or a check written on the counter, separates "no count" from "count" in the C++
loops, and the masked reverse loop stays uncounted.
INFERRED reading of the printed ranges: a lower end below zero in an unsigned range (`U:`) stands for a range that
wraps around zero, so the unmasked size can be as large as 2^64 - 1, and ScalarEvolution cannot exclude that
the stride-2 counter passes the bound by wrapping. That is a rule of the `<` exit-count computation in
ScalarEvolution. It comes from knowledge of LLVM and was not seen in any saved output
(`raw/D-c18assert-kernels-fast-scev.json`, a `-debug-only=scalar-evolution` run, printed nothing). The
reverse loop has a different cause (F5). Which pass changes the compare into the counter form when the bound
has a limited range is NOT ESTABLISHED; only the result is observed.

### F8. The up-front-check rewrites (OBSERVED)

Variants of `sources/variants.cpp`, clang 18.1.0 FAST. `pre`, `span` and `raw` are the project's rewrites
of `mitigate/src/`. Full table for five clang versions: `extracted/remarks.txt`.

| function | what it does | clang 18.1.0 FAST | SCEV |
|---|---|---|---|
| `v_rev_pre` | `REQUIRE(c.size() >= n)`, then the same `operator[]` loop | vectorized 4x2 | one exit, counted |
| `v_rev_span` | `std::span(c).first(n)` | vectorized 4x2 | one exit, counted |
| `v_rev_raw` | `REQUIRE`, then raw pointers | vectorized 4x2 | one exit, counted |
| `v_rev_fwd` | the same loop counting up | vectorized 4x2 | all exits counted |
| `v_s2_pre` | `REQUIRE(a.size() / 2 >= n)`, then `operator[]` | not vectorized | two exits uncounted |
| `v_s2_pre_mul` | `REQUIRE(n <= SIZE_MAX / 2 && 2 * n <= a.size())` | not vectorized | two exits uncounted |
| `v_s2_span` | `std::span(a).first(2 * n)` | vectorized 4x1 | one trap exit, counted |
| `v_s2_raw` | `REQUIRE(a.size() / 2 >= n)`, then raw pointers | vectorized 4x2 | one exit, counted |

- `raw/A-c18-variants-fast.json`: ``<source>:21:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]`` (`v_rev_pre`), ``<source>:79:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]`` (`v_s2_pre`), ``<source>:86:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]`` (`v_s2_pre_mul`), ``<source>:95:3: remark: vectorized loop (vectorization width: 4, interleaved count: 1) [-Rpass=loop-vectorize]`` (`v_s2_span`).
- `raw/E-c18-variants-fast-scev.json`, `v_rev_pre`: ``Loop %bb23: backedge-taken count is (-1 + %16)<nsw>``. The loop has one exit.
- Reverse, why the rewrites work, `raw/C-c18-variants-fast-pipeline.json.gz` (counts per pass: `extracted/pass-events-clang18-fast.txt`): in `v_rev_pre`, `ConstraintEliminationPass` (position 35) turns the two in-loop trap conditions into ``br i1 true, label %26, label %25, !dbg !36, !prof !39``. In `v_rev_span` the same pass makes one `br i1 true` (0 to 1). In both, `LoopSimplifyCFGPass` (position 39) then removes the `br i1 true` branches and their trap calls from the loop snapshot (`v_rev_pre`: 2 to 0 branches, `v_rev_span`: 1 to 0 branches and 1 to 0 trap calls). INFERRED: the passes can prove the in-loop comparisons because the up-front check dominates the loop.
- `v_rev_raw` and `v_s2_raw` use raw pointers behind an up-front check. Their loops have a single exit and no trap branch (`extracted/checks-in-loops.txt`).
- `v_s2_span` keeps one trap branch in the loop. `raw/B-c18-variants-fast-ir.json`: ``%33 = icmp ugt i64 %20, %32``, and ``%20 = lshr exact i64 %8, 1, !dbg !278`` is the bound. SCEV has a count for that exit (the quotation of F7). `ConstraintEliminationPass` does not make any `br i1 true` in it (`extracted/pass-events-clang18-fast.txt`). INFERRED: the exit has a count because of its `lshr exact` bound, in line with the hand-written IR of F7. So "the in-loop checks become provably true and are deleted" holds for the reverse rewrites, not for `v_s2_span`.
- For `v_s2_pre` and `v_s2_pre_mul` both stride-2 trap exits stay, uncounted: `ConstraintEliminationPass` is not among the passes that change a `br i1 true` count (`extracted/pass-events-clang18-fast.txt`), and F4 shows both exits uncounted at the vectorizer. Their bound is an `ashr exact`, like the bound of `k05` (`extracted/checks-in-loops.txt`). Which proof step fails was not observed (NOT ESTABLISHED).
- `v_s2_span` has interleave 1 on clang 18.1.0 and interleave 2 on 19.1.0 and later (`extracted/remarks.txt`).

### F9. Clang 19, 20, 21 and trunk (OBSERVED)

Reverse (k04) and stride-2 (k05) under FAST. All five rows: vectorized with the checks off (4x2), not vectorized with the checks on.
Source: `raw/A-c1*-kernels-fast.json`, `raw/A-c2*-kernels-fast.json`, `raw/A-ctrunk-kernels-fast.json`; table `extracted/remarks.txt`.

| clang | reverse (k04) | stride-2 (k05) |
|---|---|---|
| 18.1.0 | could not determine number of loop iterations | could not determine number of loop iterations |
| 19.1.0 | could not determine number of loop iterations | could not determine number of loop iterations |
| 20.1.0 | Cannot vectorize early exit loop with writes to memory | Cannot vectorize early exit loop with more than one early exit |
| 21.1.0 | Cannot vectorize early exit loop with writes to memory | Cannot vectorize early exit loop with more than one early exit |
| trunk | Cannot vectorize early exit loop with complex writes to memory | Cannot vectorize early exit loop with complex writes to memory |

- `raw/A-c19-kernels-fast.json`: ``<source>:23:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]``.
- `raw/A-c20-kernels-fast.json`: ``<source>:23:3: remark: loop not vectorized: Cannot vectorize early exit loop with writes to memory [-Rpass-analysis=loop-vectorize]`` and ``<source>:27:3: remark: loop not vectorized: Cannot vectorize early exit loop with more than one early exit [-Rpass-analysis=loop-vectorize]``.
- `raw/A-ctrunk-kernels-fast.json`: ``<source>:23:3: remark: loop not vectorized: Cannot vectorize early exit loop with complex writes to memory [-Rpass-analysis=loop-vectorize]``.
- `raw/A-ctrunk-variants-fast.json`: on trunk the loops with a hand-written check print a third wording, ``Early exit loop with store but no supported condition load``.
- Clang 20.1.0 assertion build, `raw/D-c20assert-kernels-fast-lv.json`: the reverse loop gets ``LV: Not vectorizing: Writes to memory unsupported in early exit loops.`` and the stride-2 loop gets ``LV: Not vectorizing: Loop has too many uncountable exits.``.
- INFERRED reading of "uncountable": it means an exit without a ScalarEvolution count. The word is the property F4 shows, and the loop that gets that line (the stride-2 loop) has two uncounted exits in `extracted/scalar-evolution.txt` (c20 sections).
- The IR before the vectorizer for the project loops, 18.1.0 against 19.1.0, 20.1.0 and trunk, `extracted/ir-shape-across-compilers.txt`. Each function is reduced to its instruction lines with these spellings made equal: no metadata, no `llvm.assume` calls, `ptrtoaddr` as `ptrtoint`, `inbounds nuw` as `inbounds`, the vector's member access as a byte offset, `icmp ugt a, b` as `icmp ult b, a`. Then the reverse loop, the stride-2 loop and the forward add loop are identical on all four compilers: same blocks, same operations, same compare operands, same trap branches. Without the normalization the files differ in spelling, for example `raw/B-c20-kernels-fast-ir.json`: ``%25 = icmp ult i64 %24, %18, !dbg !125`` (stride-2), where clang 18.1.0 has `icmp ugt` with the operands swapped (F2). Trunk also has `llvm.assume` calls with `separate_storage` operand bundles in the project loop functions (2 in the reverse function, 3 in the stride-2 function) and `ptrtoaddr` where the others have `ptrtoint`. The stencil differs in small ways on 19.1.0, 20.1.0 and trunk, and the forward sum on trunk (the order of the operands of two `phi` nodes); the file lists them.
- ScalarEvolution: the same exits are uncounted on 19, 20 and trunk. `raw/E-c20-kernels-fast-scev.json`: ``Loop %bb23: <multiple exits> Unpredictable backedge-taken count.``. Counts for all five project loops and the 14 variants: `extracted/scalar-evolution.txt`.
- The unswitch test of F6 gives the same table on 20 and trunk.

OBSERVED: between 19 and 20 the wording of the remarks changes and the decision does not.
INFERRED: the new text appears because clang 20 treats a loop whose exits cannot be counted as a candidate for
early-exit vectorization, and these two loops do not qualify (stores in the loop; two uncounted exits). The basis
is the wording only.

### F10. Checks written by hand behave the same (OBSERVED)

`sources/variants.cpp`: loops with an in-loop `if (...) __builtin_trap();` on raw pointers. No libc++ hardening macro is involved in the check, and the answers do not depend on the macro. This shows that an in-loop trap check written by hand reproduces the loop-shape effect on clang 18.1.0. It does not show that the macro is irrelevant to the vector accesses the loops make: the vectors are still `std::vector` and their sizes are read from it.

- `raw/A-c18-variants-fast.json`: the reverse loop with a manual check is not vectorized, ``<source>:51:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]``. The forward loop with the same check is vectorized, ``<source>:62:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]``. The stride-2 loop with a manual check is not vectorized, ``<source>:112:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]``.
- The same three results with the macro set to NONE: `extracted/remarks.txt`, column "18.1.0 NONE" (functions `v_rev_manual`, `v_fwd_manual`, `v_s2_manual`).

## Mechanism, as far as the saved outputs support it

For clang 18.1.0, `-O2`, x86-64 baseline:

1. libc++ FAST turns each `operator[]` into a branch to `llvm.trap` (OBSERVED, F2). Each branch is an extra loop exit.
2. In all 29 loops tried, the loop was vectorized exactly when every exit had a ScalarEvolution count (OBSERVED, F4). INFERRED: the vectorizer needs a backedge-taken count, ScalarEvolution gives one only if every exit has an exit count, and the count is the smallest of the exit counts. The extra exits are then handled by the scalar remainder.
3. Reverse loop: after `IndVarSimplify`, the check is a loop-invariant condition with no exit count, left
   as a branch inside the loop (OBSERVED, F5). Hoisting it (loop unswitching) before the vectorizer is enough to
   vectorize the loop (OBSERVED, F6).
4. Stride-2 loop: the checks on `2*i` and `2*i+1` against `size()` have no exit count (OBSERVED). A limited
   bound, or a check written on the counter, gives one (OBSERVED, F7). With the compare form fixed, a bound with a
   known unsigned maximum gives one (OBSERVED, hand-written IR). The rule inside ScalarEvolution is INFERRED.
5. With no backedge-taken count, the loop-access analysis prints that SCEV could not compute the exit
   count, and the vectorizer prints "could not determine number of loop iterations" (INFERRED link between
   the two, see F4). From clang 20 the remarks for the same two loops use "early exit" wording (OBSERVED, F9).

## Not established

- **The exact ScalarEvolution rule that refuses the stride-2 exits.** F7 shows, with the compare form fixed,
  which bounds get a count on three `opt` versions. The rule itself (a check that the counter cannot wrap past
  the bound) comes from knowledge of LLVM, not from a saved output.
- **Whether the vectorizer requires an exit count for every exit.** The folder shows the correlation of F4 and the
  one-factor test of F7. The necessity is INFERRED from knowledge of the LLVM source.
- **Which pass turns the compare into the counter form when the bound has a limited range** (F7), and why
  `LV: We can vectorize this loop!` is printed for the two rejected loops on clang 18.1.0 (F4).
- **Why ScalarEvolution has no count for the reverse check before `IndVarSimplify`.** The pass reports
  "Unknown exit count". The reason (a decreasing counter) is inferred from the variants of F5.
- **Which step of the proof fails for `v_s2_pre` and `v_s2_pre_mul`.** Only the outcome is observed.
- **Why the default pipeline has no unswitching after `IndVarSimplify`, and whether LLVM would accept it.**
  Neither the LLVM history nor the release notes were read. F6 inserts one pass into the text of the pipeline
  that `opt` prints; clang's own driver was not changed.
- **Whether metadata removal changes anything.** The `opt` inputs of groups E and F have debug, TBAA, branch-weight
  and loop metadata removed. The control (the vectorizer alone reproduces the compiler's decision for all five
  loops on all three compilers) and the full-pipeline runs of F6, which keep all metadata, are the support for using
  that IR. A difference for other loops is not excluded.
- **Whether a newer clang will vectorize these loops.** Trunk (see the Setup table for its build) does not. Its
  wording ("Early exit loop with store but no supported condition load") suggests that some early-exit loops with
  stores are handled and these are not (an inference from the wording). No LLVM commit was identified.
- **Whether the timed compiler gives the same output.** The saved answers come from Compiler Explorer's
  `clang1810`, which prints `clang version 18.1.0rc` at revision `461274b81d` (`raw/G-c18-kernels-fast-frontend-ir.json`,
  `../matmul/derived/revisions.txt`): a release candidate, not the final 18.1.0 and not the Ubuntu 18.1.3 that the
  timed runs used. The timed build gave the same remark, "could not determine number of loop iterations", for the
  reverse and stride-2 loops (`dayone/results/run-38116223923/remarks.k04_rev.fast.txt` and `remarks.k05_stride2.fast.txt`).
  Its IR and the other output quoted in this folder were not compared with the timed build.
- **Other settings.** Not tested here: `-O3`, AVX2, AArch64, GCC, other element types, other libc++ versions
  than the ones Compiler Explorer ships. (`ce-sweep/` has the compile-only sweep over these; it does not
  look at passes.) The matrix-multiply loop is not covered here.
- **Speed.** No timing was done. A lost vectorization is a compile-time fact; what it costs is in the
  main study.
- **`v_s2_one`** (one checked read per element) is not vectorized with the checks off either (cost model,
  `extracted/remarks.txt`), so it is not a lost loop. It is in the tally of F4 for its FAST decision only.

## Reproduce

```
python make_sources.py --check     # sources/kernels.cpp equals the project's kernels/
python make_s2_bound.py --check    # sources/handwritten/s2-bound.ll is what the script writes
python fetch.py --dry-run          # lists every request; raw/ already holds all answers
python verify.py                   # checks the quotations and numbers of this file against raw/
python excerpts.py                 # rebuilds extracted/
```

To rebuild `raw/` from nothing (this sends requests, 1.5 s apart, at most 120 in one run), empty `raw/` and run
`python fetch.py`, then `python extract.py ir`, then `python fetch.py` twice more. Some requests use files made
from earlier answers: the IR modules `sources/ir/*.ll` (groups E and F, and the front end's IR for group G) and the
pipeline text of group G, which the three full-pipeline runs contain. The first run sends the 53 requests that
need no such file (the experiments of the other groups and the two listings), the second the 16 requests of
groups E and F and the pipeline text, the third the 3 full-pipeline runs, and the fourth sends none.
`python replay_check.py` replays this sequence offline, with the saved answers standing in for the network, and
checks that it rebuilds all 72 answers of `raw/`.

Sending and saving use only the Python standard library. `fetch.py` sends a request only when
`raw/<name>.json` is missing or the stored request differs; a differing request under an existing name stops
with an error unless the code is told to replace it. `verify.py` checks that every saved answer was made by the
request `experiments.py` defines now.

## Requests

85 requests in total (`request-index.json`): 83 compiles and 2 listings (the C++ and the LLVM IR compiler
lists, `raw/compilers-cpp-ids.json`, `raw/compilers-llvm-ids.json`). 72 answers are kept in `raw/`. The
other 13 requests were repeats: 11 were sent again after a source file or an IR file was changed (the older
answers were replaced), and 2 were a first probe and a repeat of it with empty arguments (both answers
discarded). One request at a time, at least 1.5 s apart, a User-Agent that names the project, no HTTP 429,
no key.

## Files

| path | content |
|---|---|
| `raw/` | every Compiler Explorer answer (JSON; answers over 1 MB are gzip) with the request that produced it |
| `sources/kernels.cpp`, `variants.cpp`, `variants2.cpp`, `variants3.cpp` | the C++ sources compiled |
| `sources/ir/*.ll` | the IR dumps of group B as modules `opt` can read, and the front end's IR of group G (made by `extract.py ir`) |
| `sources/handwritten/s2-bound.ll` | the hand-written IR of F7 (made by `make_s2_bound.py`) |
| `extracted/` | readable text made from `raw/` by `excerpts.py` (each file lists its inputs) |
| `ce.py`, `fetch.py`, `experiments.py` | the client, the sender, and the list of requests |
| `make_sources.py`, `make_s2_bound.py`, `extract.py`, `excerpts.py`, `verify.py`, `replay_check.py` | source generation, IR extraction, excerpts, checks, the offline replay of the rebuild |
| `request-index.json` | every request sent, in order |
