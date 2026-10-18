# k08 matrix multiply under libc++ FAST: why clang 18 does not vectorize it and clang 19 to 22 do

Compile-only study. Nothing here is timed. All results are for x86-64 baseline (SSE2) except where F6 says otherwise, `-O2`, one loop (`kern_k08_matmul`, `kernels/k08_matmul.cpp`), on Compiler Explorer's compilers (fetched 2026-10-15 and 2026-10-16 UTC).

## Question

With libc++ hardening mode FAST, the inner loop of `kern_k08_matmul` is not vectorized by clang 18 ("the cost-model indicates that vectorization is not beneficial"), is vectorized by clang 19 to 22, and is not vectorized again by clang 23.1 and trunk. On clang 16 and 17 the FAST macro adds no check (F1). For those two compilers this folder uses the hardening macro of their own libc++; its check compiles to a call, not a trap, and the loop is not vectorized there either (table below). `versions/MATMUL-EXPLAINED.md` leaves open why the decision changes, and whether the change is in the compiler or in the library headers. This folder tries to settle both.

## Answer in brief

Every statement carries a label: OBSERVED (a line, number or count in a saved file), INFERRED (reasoned from observations, the reasoning is given) or NOT ESTABLISHED. The findings section names the files.

| compiler | hardening macro | check compiles to | outcome at the loop | cost of each exit compare at VF 4 | exit compares found uniform |
|---|---|---|---|---|---|
| clang 16.0.0 | `_LIBCPP_ENABLE_ASSERTIONS=1` | call of `__libcpp_verbose_abort` | not vectorized: cost model, not beneficial | 14 | no |
| clang 17.0.1 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | call of `__libcpp_verbose_abort` | not vectorized: cost model, not beneficial | 14 | no |
| clang 18.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | not vectorized: cost model, not beneficial | 14 | no |
| clang 19.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | 1 | yes |
| clang 20.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | 1 | yes |
| clang 21.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | 1 | yes |
| clang 22.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | - | no |
| clang 23.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | not vectorized: early-exit loop with a store | - | no |
| trunk (assertions build, e633c7da8f) | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | not vectorized: early-exit loop with complex writes | - | no |

OBSERVED, from the assertions builds' `-debug-only=loop-vectorize` logs (`derived/tables.md`, table A). "VF 4" is the vectorizer's width-4 plan. A cost is in the cost model's own units. The dash means the compare is not in the loop any more (clang 22) or the log has no cost list (clang 23.1, trunk). The trunk row is `raw/dbg_atrunk_fast.json`; its remarks name the same install directory as the answers made with `-v` for revision `e633c7da8f` (`derived/revisions.txt`).

1. **Compiler, not library.** OBSERVED: the same outcome pattern appears with libc++ 18.1.0 headers on every compiler from clang 18 to trunk, with libc++ 19.1.0 headers on clang 18, and with no library header at all (F8).
2. **Clang 18 rejects on cost, not on legality.** OBSERVED: legality passes, the vectorizer builds a plan, and it prices each of the two non-latch bounds-check compares at 14 units at width 4. The logged width-4 total is 45 units against 44 for four scalar iterations (F2, F3). INFERRED: that one unit is what makes the scalar loop win; the profitability comparison itself was not read. OBSERVED: the 14 units depend on the target (SSE2 14, SSE4.2 6, AVX2 3), and a formula from the LLVM 18.1.0 source reproduces all seven logged compare costs; the number of legal-width pieces in that formula was fitted, not read (F6). OBSERVED: forced to width 4, clang 18 produces nearly the same code as clang 19 (F5).
3. **Clang 19 to 21 change the pricing.** OBSERVED: the two compares are found uniform and cost 1 each, the width-4 loop costs 16 units against 44, and the loop is vectorized (F4). Commit `b6a8f5486b` ("[LV] Consider all exit branch conditions uniform.", 2024-04-28) is in `llvmorg-19.1.0` and `llvmorg-19.1.7` and not in `llvmorg-18.1.0`, `llvmorg-18.1.3` or `llvmorg-18.1.8` (the last 18.1.x tag in the repository). INFERRED: this commit causes the change, from the agreement of its diff, the changed log lines and the changed numbers; no clang 18 build with only that commit exists to test (N1).
4. **Clang 22 takes another route.** OBSERVED: the clamped trip count (`llvm.umin`) is produced by IndVarSimplify, before the vectorizer, and the vectorizer sees a loop with no exit compares. With `-mllvm -indvars-predicate-loop-traps=false` (a hidden option that commit `39b0cbe69c`, 2025-10-16, adds; the commit is in `llvmorg-22.1.0` and `llvmorg-23.1.0`, not in `llvmorg-19.1.0`, `llvmorg-21.1.0` or `llvmorg-21.1.8`) clang 22.1.0 logs the clang 19 to 21 numbers and produces the clamp first inside LoopVectorize (F9). INFERRED: that commit is why clang 22 differs; the toggle is the option the commit adds, not a build without the commit.
5. **Clang 23.1 and trunk lose it again.** OBSERVED for clang 23.1 and for trunk revision `efd4965724`: the two pointer loads that compute `c.size()` stay inside the inner loop in the IR the vectorizer receives, the clamp never appears, and the vectorizer rejects the loop as an early-exit loop with stores (F10). OBSERVED in the library-free emulation only: reading the pointers and sizes into locals in the source, or declaring `c` `__restrict`, restores vectorization on clang 23.1 and trunk; the libc++ kernel itself was not rebuilt with either change. INFERRED, for the libc++ kernel: the chain in F10 (non-computable exit count, no predication, early-exit path). Why the optimizer stopped hoisting the loads is not established (N3). The two trunk builds are different revisions (`clang_trunk` `efd4965724`, `clang_assertions_trunk` `e633c7da8f`) and their rejection texts differ with the source compiled (F10).

## Method

- **Compilers.** Compiler Explorer (godbolt.org) ids: `clang1600`, `clang1701`, `clang1810`, `clang1910`, `clang2010`, `clang2110`, `clang2210`, `clang2310`, `clang_trunk`, and their assertions builds (`clang160assert` to `clang231assert`, `clang_assertions_trunk`). The id-to-name map is `derived/compilers-used.json`. Assertions builds are the only ones that print `-mllvm -debug-only=...` output; they are different binaries from the ones timed in the study. Build lines printed by `-v` are in `derived/revisions.txt`: `clang1810` and `clang181assert` both report `clang version 18.1.0rc` at LLVM revision `461274b81d` (a release candidate, not the final 18.1.0); `clang1910` and `clang191assert` both report `19.1.0` at `a4bf6cd7cf`; `clang_trunk` reports `24.0.0git` at `efd4965724` and `clang_assertions_trunk` `24.0.0git` at `e633c7da8f`, both installed in directories dated 20261015. The other ids were not asked for their revision.
- **Hardening macros.** Clang 18 and later: `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST` (`..._NONE` for the unchecked builds). The clang 16 assertions build uses `-D_LIBCPP_ENABLE_ASSERTIONS=1` and the clang 17 assertions build `-D_LIBCPP_ENABLE_HARDENED_MODE=1`, the macros `ce-sweep/README.md` uses for those versions. With the FAST macro, clang 16 and 17 vectorize the loop and the assembly has neither a `ud2` nor an abort call (`raw/fastmacro_c16.json`, `raw/fastmacro_c17.json`): the macro adds no check there. The check of the clang 16 and 17 builds compiles to calls of `std::__1::__libcpp_verbose_abort`: no `ud2`, 126 assembly lines, against one `ud2` and 77 lines for clang 18 (`derived/outcomes.tsv`, columns `asm_lines` and `ud2`). Their cost numbers equal clang 18's (14 per compare), which is why they appear in the same rows.
- **Flags.** `-O2 -march=x86-64 -stdlib=libc++`, the macro above, plus `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize`. Compiler Explorer puts `-g` first in every compile (`compilationOptions` in each raw file). The study's own builds have no `-g`. With `-g0` appended the vectorizer's log and remarks are identical for clang 18.1.0 and 19.1.0 once metadata ids are normalized (`derived/g0_comparison.txt`; the `!dbg` line locations stay, as `-Rpass` remarks need them).
- **Sources.** `src/k08_matmul.cpp` is the kernel copied verbatim. `src/emul_matmul.cpp` is the same loop with no library header: a three-pointer `Vec` with the layout of `std::vector<int32_t>` and a check `if (!(n < size_t(end - begin))) __builtin_trap()` that loads `begin_`/`end_` on every access. OBSERVED: the IR that clang 18 hands to the vectorizer for this loop and for the libc++ loop is the same shape; 3 of 81 normalized lines differ (6 lines removed or added), all of them the struct type name in the end-pointer address (`derived/ir_diff_libcxx_vs_library_free_c18.txt`, from `raw/pipe_c18_fast.json.gz` and `raw/pipe_emul_c18_abc.json.gz`). Three variants change one thing each: `emul_hoist.cpp`, `emul_restrict.cpp`, `emul32_matmul.cpp`.
- **Requests.** 94 compile requests to `POST /api/compiler/<id>/compile`, 1.5 s apart, every one answered with HTTP 200; `requests.tsv` lists them (cap 120). Each answer is saved with its exact request in `raw/<name>.json` (`.json.gz` for optimizer-pipeline answers), and `run_requests.py` re-sends only what is missing. Separately, `fetch_llvm_src.py` reads 15 files from `raw.githubusercontent.com` and 14 answers from `api.github.com` (public LLVM repository, fixed release tags) into `llvm-src/`.
- **Terms.** VF is the vector width in lanes. A cost "unit" is the vectorizer's own cost-model unit, not a cycle. An instruction is "uniform" when the cost model treats it as computed once per vector iteration instead of once per lane. A "check" is the `index < size` compare and trap that libc++'s hardened `operator[]` adds. "Clamp" is the `llvm.umin` that bounds the inner trip count by both sizes.
- **Labels.** OBSERVED means a line, a number or a count in a saved file; the file is named. INFERRED means reasoned from observations, and the reasoning is given. NOT ESTABLISHED means no saved file decides it. Quoted lines are the saved `text` fields with terminal colour codes removed.
- **Checks.** `python check.py` (offline) verifies that every saved answer matches today's request, that `derived/` is what `analyze.py` computes from `raw/`, and that each statement in the findings holds in the saved data (116 checks at the time of writing).

## Findings

### F1. The reproduction on a single kernel (OBSERVED)

`raw/base_c18_fast.json`: `<source>:11:7: remark: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]`. `raw/base_c19_fast.json`: `<source>:11:7: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]`. With the checks off both vectorize (`raw/base_c18_none.json`, `raw/base_c19_none.json`). Every FAST build in this folder with clang 18 or later that compiled keeps exactly one `ud2`, and the vector-register instruction count agrees with the remark (0 against 22; `derived/outcomes.tsv`, columns `ud2` and `simd_lines`). Clang 16 and 17 are not FAST builds: see Method, "Hardening macros". With the FAST macro they compile the loop vectorized and with no check at all (`raw/fastmacro_c16.json`, `raw/fastmacro_c17.json`: `vectorized loop (vectorization width: 4, interleaved count: 2)`, no `ud2`, no abort call).

### F2. Clang 18 accepts the loop and rejects it on cost (OBSERVED)

`raw/dbg_a18_fast.json` (assertions build, `-debug-only=loop-vectorize`):

- `LV: We can vectorize this loop (with a runtime bound check)!` (legality passed)
- `EMIT vp<%2> = EXPAND SCEV (1 + (({0,+,(-1 * %d)}<%for.body4> + ... umin_seq ((-1 + %d) umin ...` (abbreviated here; the line is in the file): the plan's trip count already folds both size checks into a clamped bound, as clang 19's plan does (`raw/dbg_a19_fast.json`).
- `LV: Scalar loop costs: 11.`, `LV: Vector loop of width 2 costs: 14.`, `LV: Vector loop of width 4 costs: 11.`, `LV: Selecting VF: 1.`, `LV: Vectorization is possible but not beneficial.`

So the remark's wording ("cost-model") is literal. `versions/MATMUL-EXPLAINED.md` reads it as an interpretation; here it is the log's own verdict. The same cost numbers appear for clang 16 and 17 (`raw/dbg_a16_fast.json`, `raw/dbg_a17_fast.json`); those builds use their own hardening macro and their check is an abort call, not a trap.

### F3. Where the cost comes from: the two exit compares (OBSERVED)

`derived/cost-table.md` lists every instruction's cost at VF 1 and VF 4. For clang 18.1.0 the sum at VF 4 is 45 and each of the two bounds-check compares costs 14, together 28 of the 45:

`LV: Found an estimated cost of 14 for VF 4 For instruction:   %cmp.i42 = icmp ugt i64 %sub.ptr.div.i.i41, %add10, !dbg !1507` (`raw/dbg_a18_fast.json`)

Four scalar iterations cost 4 x 11 = 44, so the width-4 loop is estimated one unit worse. The printed per-lane value is the integer quotient 45 / 4 = 11, equal to the scalar 11. INFERRED: this is why the vectorizer logs "not beneficial"; the profitability comparison itself was not read, and 45 against 44 is arithmetic on the logged numbers.

The IR that reaches the vectorizer is nearly the same in clang 18 and clang 19: the two dumps (`derived/ir_before_loopvectorize_c18_fast.ll`, `..._c19_fast.ll`, from `raw/pipe_c18_fast.json.gz`, `raw/pipe_c19_fast.json.gz`, 96 lines each, debug metadata removed) differ in 3 lines (3 removed, 3 added), all of them how the end pointer of a vector is addressed (`derived/ir_diff_before_loopvectorize_c18_c19.txt`). Both dumps contain three `llvm.trap` calls, two of them exits of the inner loop. INFERRED: the decision is made inside the vectorizer, because the same loop shape reaches it in both.

### F4. The change between 18 and 19 is in which compares count as uniform (OBSERVED, cause INFERRED)

OBSERVED in `raw/dbg_a19_fast.json`: the compares that feed the trap exits are now found uniform and cost 1 each:

- `LV: Found uniform instruction:   %cmp.i42 = icmp ugt i64 %sub.ptr.div.i.i41, %add10, !dbg !1506`
- `LV: Found an estimated cost of 1 for VF 4 For instruction:   %cmp.i42 = icmp ugt i64 %sub.ptr.div.i.i41, %add10, !dbg !1506`
- `LV: Vector loop of width 4 costs: 4.`, `LV: Selecting VF: 4.`, `LV: Loop requires scalar epilogue: multiple exits`

In `raw/dbg_a18_fast.json` the only compare found uniform is the latch's: `LV: Found uniform instruction:   %exitcond.not = icmp eq i64 %inc, %d, !dbg !1529`. In clang 19 the sum at VF 4 is 16 against 44 (`derived/cost-table.md`). Clang 20 and 21 show the same numbers (`raw/dbg_a20_fast.json`, `raw/dbg_a21_fast.json`).

OBSERVED in the LLVM source (`llvm-src/collectLoopUniforms_18.1.0.cpp.txt`, `..._19.1.0.cpp.txt`): the function that starts the uniform worklist reads, in 18.1.0, `auto *Cmp = dyn_cast<Instruction>(Latch->getTerminator()->getOperand(0));` and, in 19.1.0, loops over `TheLoop->getExitingBlocks(Exiting)`. The function is byte-identical between 18.1.0 and 18.1.3 and between 19.1.0 and 19.1.7 (`llvm-src/collectLoopUniforms_sha256.txt`), the versions timed in the study. It is also identical at the two LLVM revisions that Compiler Explorer's 18.1.0 and 19.1.0 builds report (`461274b81d` and `a4bf6cd7cf`, `derived/revisions.txt`) to the text at the tags 18.1.0 and 19.1.0, so the quoted function is the one in the builds that produced the logs (only this function's text was compared). In `getInstructionCost`, an instruction that is uniform after vectorization is costed with `VF = ElementCount::getFixed(1)`, i.e. as a scalar (`llvm-src/getInstructionCost_uniform_18.1.0.cpp.txt`, and the same in 19.1.0).

OBSERVED in `llvm-src/commit_b6a8f5486b.json`: Florian Hahn, 2024-04-28, "[LV] Consider all exit branch conditions uniform." Its message: "Previously we were overestimating the cost of values contributing to the other exits." Its diff is the change from the latch-only start to the loop over exiting blocks. `llvm-src/commit_in_tag.json` (GitHub compare API): the commit is in `llvmorg-19.1.0` and `llvmorg-19.1.7` and not in `llvmorg-18.1.0`, `llvmorg-18.1.3` or `llvmorg-18.1.8`; 18.1.8 is the last 18.1.x tag in the repository (same file, `tags_in_repository`).

INFERRED: this commit is what flips the decision. The support is that the diff, the changed log lines (compares become uniform), and the changed costs (14 to 1) all match what the commit message describes. Not done: a clang 18 build with only this commit, which Compiler Explorer does not offer. The search that found the commit listed the commits touching `LoopVectorize.cpp` between 2024-01-20 and 2024-07-25 and chose the one about exit-branch uniformity; that listing is not saved.

### F5. Forced to width 4, clang 18 emits clang 19's code (OBSERVED, reading INFERRED)

`raw/force_c18_fast.json` (`-mllvm -force-vector-width=4 -mllvm -force-vector-interleave=2`): `vectorized loop (vectorization width: 4, interleaved count: 2)`. Its assembly against clang 19's own choice (`raw/base_c19_fast.json`): 209 lines against 212, 27 lines removed or added (12 removed, 15 added; `derived/asm_diff_c19_vs_c18_forced.txt`). The differences are register choice (`r9` and `rdi` swap roles in one block), the order of a few instructions, two constants stored through a register (`xor eax, eax` then `mov qword ptr [rsp - 96], rax` instead of `mov qword ptr [rsp - 96], 0`) and one extra `mov rdi, r13`. INFERRED from this: clang 18's transformation and code generation for this loop are not the obstacle; the profitability decision is.

### F6. The decision depends on the target's 64-bit vector compare (OBSERVED, mechanism INFERRED)

Clang 18.1.0 with FAST and `-O2`, at three target levels (assertions build, `-debug-only=loop-vectorize`):

| `-march=` | cost of each exit compare at VF 4 | vector cost per lane | outcome | file |
|---|---|---|---|---|
| `x86-64` (SSE2) | 14 | 11 (scalar 11) | not vectorized | `raw/dbg_a18_fast.json` |
| `x86-64-v2` (SSE4.2) | 6 | 6 (scalar 11) | vectorized, width 4, interleave 1 | `raw/dbg_a18_fast_v2.json` |
| `x86-64-v3` (AVX2) | 3 | 3 at width 8 (scalar 11) | vectorized, width 8, interleave 1 | `raw/dbg_a18_fast_v3.json` |

OBSERVED in the LLVM 18.1.0 x86 cost tables (`llvm-src/x86_setcc_i64_18.1.0.txt`): the 64-bit vector compare entry (the first number of each entry is the one used below) is 5 in `SSE2CostTbl` for `v2i64` (`pcmpeqd/pcmpgtd expansion`), 1 in `SSE42CostTbl` for `v2i64` and 1 in `AVX2CostTbl` for `v4i64`. OBSERVED in `X86TTIImpl::getCmpSelInstrCost` (`llvm-src/x86_cmpsel_cost_18.1.0.txt`): for an unsigned vector compare (`ICMP_ULT`, `ICMP_UGT`) `ExtraCost = 2` (the sign-bit flip), and the table cost is returned as `LT.first * (ExtraCost + *KindCost)`. All seven compare costs the logs print at VF 2 and above equal that formula, where the number of legal-width pieces (`LT.first`) is the number of 128-bit (SSE) or 256-bit (AVX2) registers the vector needs (INFERRED: this factor was fitted to the logs, the legalization code was not read):

| target | VF | pieces (`LT.first`) | table entry | formula | logged cost |
|---|---|---|---|---|---|
| SSE2 | 2 | 1 | 5 | 1 x (2 + 5) | 7 |
| SSE2 | 4 | 2 | 5 | 2 x (2 + 5) | 14 |
| SSE4.2 | 2 | 1 | 1 | 1 x (2 + 1) | 3 |
| SSE4.2 | 4 | 2 | 1 | 2 x (2 + 1) | 6 |
| AVX2 | 2 | 1 | 1 (SSE4.2 `v2i64` entry) | 1 x (2 + 1) | 3 |
| AVX2 | 4 | 1 | 1 (AVX2 `v4i64` entry) | 1 x (2 + 1) | 3 |
| AVX2 | 8 | 2 | 1 (AVX2 `v4i64` entry) | 2 x (2 + 1) | 6 |

INFERRED: SSE2 has no 64-bit vector compare instruction, so the compare is expanded and priced high; this is why the loss is specific to the baseline target. It matches `ce-sweep/README.md` (matmul not lost at x86-64-v3 on clang 16 to 18) and extends it to SSE4.2 for clang 18.

### F7. One inner-loop check instead of two vectorizes on clang 18 (OBSERVED)

With `src/emul_matmul.cpp`, clang 18.1.0 vectorizes when only the check on `b[]` is on, or only the check on `c[]` (`raw/emul_c18_aB.json`, `raw/emul_c18_aC.json`: `vectorized loop (vectorization width: 4, interleaved count: 1)`) and does not when both are on (`raw/emul_c18_abc.json`). The log for one check (`raw/dbg_emul_a18_aB.json`): `LV: Scalar loop costs: 9.`, `LV: Vector loop of width 4 costs: 7.`. This is what F3 predicts: one 14-unit compare less makes the vector loop cheaper than the scalar loop. Clang 19 vectorizes all of these variants (`raw/emul_c19_aB.json`, `raw/emul_c19_aC.json`).

### F8. The library is not the cause (OBSERVED)

`derived/tables.md`, sections B and C.

- **No library header** (`src/emul_matmul.cpp`, all three checks on): not vectorized on clang 16, 17, 18, 23.1 and trunk; vectorized on clang 19, 20, 21 and 22. With the checks off it is vectorized on clang 18, 19 and 23.1 (`raw/emul_c18_none.json`, `raw/emul_c19_none.json`, `raw/emul_c231_none.json`). The asm line counts equal those of the libc++ builds (77, 209, 200, 72).
- **Library held at 18.1.0, compiler changed.** `-nostdinc++ -isystem /opt/compiler-explorer/clang-18.1.0/include/...` (the headers of Compiler Explorer's clang 18.1.0 install). `-H` shows the headers read: `raw/libswap_c19_lib18.json` lists `. /opt/compiler-explorer/clang-18.1.0/include/c++/v1/vector` for clang 19.1.0. Outcomes: clang 18 not vectorized; clang 19, 20, 21, 22 vectorized; clang 23.1 and trunk not vectorized, with the remark `loop not vectorized: Early exit loop with store but no supported condition load`.
- **Compiler held at 18.1.0, library changed.** With libc++ 19.1.0 headers (`raw/libswap_c18_lib19.json`, `-H` lists `/opt/compiler-explorer/clang-19.1.0/include/c++/v1/...`) clang 18 is still not vectorized. With libc++ 21.1.0 headers it does not compile: `error: use of undeclared identifier '__builtin_ctzg'` (`raw/libswap_c18_lib21.json`), so that pair is not testable.

The compiler version alone reproduces the whole pattern. Every one of the builds that has the checks on and compiled in these three groups contains exactly one `ud2` (the checks took effect).

### F9. Clang 22: the traps leave the loop before the vectorizer (OBSERVED, cause INFERRED)

`derived/first_umin.txt` (from the optimizer pipelines of `raw/pipe_c19_fast.json.gz`, `raw/pipe_c20_fast.json.gz`, `raw/pipe_c21_fast.json.gz`, `raw/pipe_c22_fast.json.gz`, `raw/pipe_c22_nopred.json.gz`): the first pass whose output contains an `llvm.umin` clamp is `LoopVectorizePass` in clang 19, 20 and 21 (pass #117, #118, #118), `IndVarSimplifyPass` (pass #63) in clang 22, and again `LoopVectorizePass` (pass #120) in clang 22 with `-mllvm -indvars-predicate-loop-traps=false`. In clang 19, 20, 21 and in clang 22 with the option off, the IR handed to the vectorizer has no clamp; in clang 22 by default it has (`derived/ir_before_loopvectorize_c22_fast.ll`: `%57 = call i64 @llvm.umin.i64(i64 %56, i64 %16)` before the inner loop, and an inner loop with a single exit).

OBSERVED in the logs (`derived/tables.md`, table E): clang 22.1.0 by default has no exit compares in the cost list and logs `LV: Scalar loop costs: 7.`, `LV: Vector loop of width 4 costs: 3.` (`raw/dbg_a22_fast.json`, `derived/cost-table.md`). With `-mllvm -indvars-predicate-loop-traps=false` (`raw/dbg_a22_nopred.json`) it logs the clang 19 to 21 numbers: scalar 11, width 2 costs 8, width 4 costs 4, the exit compares found uniform and costed 1 each, and `LV: Loop requires scalar epilogue: not exiting from latch block` (the reason clang 20 and 21 log; clang 19 logs `multiple exits`; clang 22 by default logs none). The loop is vectorized in both cases (`raw/pipe_c22_nopred.json.gz`: width 4, interleave 2).

OBSERVED in `llvm-src/commit_39b0cbe69c.json`: Florian Mayer, 2025-10-16, "[IndVarSimplify] Allow predicateLoopExit on some loops with thread-local writes (#155901)". Its message names bounds-check loops of the shape `bar[i] = foo[i] + 123;` and ends "This also allowed the loop to be vectorized." Its patch adds the hidden option `indvars-predicate-loop-traps` (default true) and replaces the unconditional `if (I.mayHaveSideEffects()) return false;`, which stopped the transformation for any loop that contains an instruction with side effects (every store among them), by an exception for simple stores whose exit block only traps. `llvm-src/indvars_predicate_traps.txt`: the option appears in the IndVarSimplify source of 22.1.0 and 23.1.0 and not in that of 19.1.0 or 21.1.0. `llvm-src/commit_in_tag.json`: the commit is in `llvmorg-22.1.0` and `llvmorg-23.1.0`, not in `llvmorg-19.1.0`, `llvmorg-21.1.0` or `llvmorg-21.1.8` (21.1.8 is the last 21.1.x tag in the repository).

INFERRED: this commit is why clang 22's vectorizer sees a different loop. The support is the pass-level evidence (the clamp first appears in IndVarSimplify), the commit text, and the toggle: with the option the commit adds switched off, clang 22.1.0 returns to the clang 19 to 21 behavior. Not done: a clang 22 build without the commit.

### F10. Clang 23.1 and trunk: the size loads of `c` stay in the loop

- **The rejection (OBSERVED).** `raw/dbg_a23_fast.json`: `LV: Not vectorizing: Early exit loop with store but no supported condition load.` (clang 23.1.0 assertions build). Assertions trunk, revision `e633c7da8f` (`raw/dbg_atrunk_fast.json`, `raw/rev_atrunk_fast.json`): `LV: Not vectorizing: Complex writes to memory unsupported in early exit loops.` Release trunk, `clang_trunk` revision `efd4965724`: the same kernel with trunk's own libc++ headers is rejected with `Cannot vectorize early exit loop with complex writes to memory` (`raw/pipe_ctrunk_fast.json.gz`); with libc++ 18.1.0 headers or with no library header it is rejected with `Early exit loop with store but no supported condition load` (`raw/libswap_ctrunk_lib18_v.json`, `raw/emul_ctrunk_abc_v.json`). So at one revision the text depends on the source compiled; why is not established (N9). The four older `clang_trunk` answers (made without `-v`) were re-sent with `-v`; each gives the same outcome and text as before.
- **The legality route (OBSERVED in the LLVM source).** `llvm-src/legality_23.1.0.txt`: when `isa<SCEVCouldNotCompute>(PSE.getBackedgeTakenCount())` and the loop has more than one exiting block, legality goes to `isVectorizableEarlyExitLoop()`. The route is also in 20.1.0 and 22.1.0 (`llvm-src/legality_20.1.0.txt`, `legality_22.1.0.txt`). In 19.1.0 a non-computable count is a plain rejection (`could not determine number of loop iterations`) with no early-exit route (`llvm-src/legality_19.1.0.txt`). The logs of clang 18, 19 and 22 show legality passing for the k08 loop.
- **The loop differs (OBSERVED for clang 23.1 and for trunk `efd4965724`).** The IR clang 23.1 hands to the vectorizer (`derived/ir_before_loopvectorize_c231_fast.ll`) has the two pointer loads and the subtraction that compute `c.size()` inside the inner loop (`%49 = load ptr, ptr %15`, `%50 = load ptr, ptr %0`); clang 19's and clang 22's have them before it. `derived/loads_in_loop.txt` (passes that run before the vectorizer): in every pass after the last one in which the loop holds the inlined bodies (4 blocks, 4 pointer loads inside), the innermost loop has 0 pointer loads inside for clang 19 and for clang 22, and 2 for clang 23.1 and for trunk. The clamp (`llvm.umin`) never appears before the vectorizer in clang 23.1 or trunk (`derived/first_umin.txt`).
- **LICM (OBSERVED).** `derived/licm_hoisting.txt` (from `raw/licm_a19_fast.json`, `raw/licm_a23_fast.json`, `raw/licm_atrunk_fast.json`): clang 19 hoists the loads of both `b` and `c` out of the inner loop (`%5 = load ptr, ptr %__end_.i.i46`, `%6 = load ptr, ptr %c`); clang 23.1 and assertions trunk (`e633c7da8f`) hoist those of `b` and not those of `c` (the address computation `%__end_.i.i.i46` is hoisted, the loads are not).
- **Counterfactuals (OBSERVED, library-free emulation only; `derived/tables.md`, section D).** Reading the data pointer and size of `b` and `c` into locals before the inner loop (`src/emul_hoist.cpp`): clang 19, 23.1 and trunk (`efd4965724`) vectorize (`raw/hoist_c19_bc.json`, `raw/hoist_c231_bc.json`, `raw/hoist_ctrunk_bc_v.json`); clang 18 still does not (`raw/hoist_c18_bc.json`). Declaring `c` `__restrict` (`src/emul_restrict.cpp`): clang 23.1 and trunk vectorize (`raw/restrict_c231_abc.json`, `raw/restrict_ctrunk_abc_v.json`); clang 18 does not. On clang 23.1, in both variants, the IR handed to the vectorizer contains the clamp, and the clamp first appears in IndVarSimplify, as in clang 22 (`derived/first_umin.txt`, from `raw/pipe_hoist_c231.json.gz` and `raw/pipe_restrict_c231.json.gz`). These two variants are not the libc++ kernel: a `std::vector` reference cannot simply be declared `__restrict`, and the libc++ kernel was not rebuilt with either change (N11). They are a fair stand-in only to the degree F8 shows the emulation reproduces the 18 / 19 / 23.1 pattern and F3 shows the same IR shape on clang 18.
- **Pointer TBAA (OBSERVED, reading INFERRED).** `-fno-pointer-tbaa` changes nothing on clang 23.1 (`raw/ptbaa_c231_off.json`: still rejected; `raw/ptbaa_c22_off.json`: clang 22 still vectorizes). In the optimized IR (`derived/tbaa_pointer_loads.txt`, from `raw/emitfull_c19_fast.json`, `raw/emitfull_c22_fast.json`, `raw/emitfull_c231_fast.json`) the tagged `load ptr` instructions of the kernel have access type `any pointer` in clang 19 (2 of 6 loads tagged) and `p1 int` in clang 22 (2 of 6) and clang 23.1 (6 of 6). INFERRED: the pointer-TBAA change falls between clang 19 and 22, not between 22 and 23.1.

INFERRED, for the libc++ kernel: on clang 23.1 and trunk the optimizer does not hoist `c`'s size loads; therefore the exit count of the `c` check is not computable, IndVarSimplify cannot predicate it, and the vectorizer's own legality sends the loop down the early-exit path, which refuses stores. The counterfactuals agree with this chain (they remove the in-loop loads or give the alias information, and the clamp then appears in IndVarSimplify). Each link is observed except that the missing predication is caused by the non-computable exit count (not shown by a log line), and the counterfactuals were run on the emulation.

### F11. Inconclusive: 32-bit indices (OBSERVED)

`src/emul32_matmul.cpp` uses `uint32_t` indices and sizes, to make the compare a 32-bit compare. Outcome unchanged on clang 18 and clang 19 (`raw/emul32_c18_abc.json`, `raw/emul32_c19_abc.json`). The log (`raw/dbg_emul32_a18_abc.json`) shows the optimizer widened the induction variable to `i64` (`%cmp.not.i43 = icmp ult i64 %13, %5`, cost 14), so the compare was still 64-bit. The experiment neither supports nor contradicts F6.

## What this settles in `versions/MATMUL-EXPLAINED.md`

- "That the exits are the reason for the 18 rejection is an interpretation: the remark says 'cost model', not 'legality'." Now observed: legality passed and the exits' compares are the cost (F2, F3).
- "Whether clang 18 at SSE2 lacks the clamp or rejects the loop before using it is not shown." Clang 18's plan already contains the clamped trip count (the `umin_seq` expression in `raw/dbg_a18_fast.json`) and rejects on cost (F2). In clang 19, 20 and 21 the clamp is first created inside `LoopVectorizePass` (pass-level observation for all three, F9), not by an earlier pass. The statement that clang 19 "turns the per-element checks into a bound on the trip count (check hoisting / loop predication...)" holds for clang 22 (IndVarSimplify), not for 19 to 21, where the vectorizer still receives the two trap exits (F3) and handles them itself.
- "At x86-64-v3 clang 18.1.0 already emits a similar structure." Explained by the compare cost at that target (F6).
- "Which LLVM change between 18 and 19 changed the vectorizer's decision": a candidate is identified and reasoned (F4, INFERRED).
- "Whether it is a libc++ change or an LLVM optimizer change": the compiler (F8).
- The note's inferences about the remaining 1.61x at L1 on clang 19 (prologue cost around a short vector body) are not tested here.

## Not established

- **N1.** That `b6a8f5486b` alone causes the 18 to 19 change. No build with only that commit exists to test; the evidence is agreement (F4).
- **N2.** Whether the timed toolchains (Ubuntu clang 18.1.3, apt.llvm.org clang 19.1.7) print these exact costs. The decision function is the same text in the upstream tags 18.1.0/18.1.3 and 19.1.0/19.1.7 (F4); distribution builds may carry patches, which were not checked. The timed outcomes (lost, kept) match; the costs come from Compiler Explorer's 18.1.0 and 19.1.0 assertions builds.
- **N3.** Why clang 23.1 and trunk do not hoist `c`'s size loads while clang 22 does. Candidates tested and excluded: pointer-type TBAA (F10). No LLVM change between 22.1.0 and 23.1.0 was identified, and no build in between was tested. Whether this is a regression, an intended change or a consequence of the early-exit work was not determined.
- **N4.** The reverse and stride-2 loops. They were not examined here.
- **N5.** Anything about time. The cost-model units are not cycles; the measured 1.61x at L1 on clang 19 is outside this study.
- **N6.** Other targets and levels: only x86-64 baseline `-O2` was examined, plus `-march=x86-64-v2` and `-v3` on clang 18 and 19 (F6; clang 19 only for the outcome, `raw/dbg_a19_fast_v2.json`, `raw/dbg_a19_fast_v3.json`). `ce-sweep/` has -O3, AVX2 and AArch64 outcomes without causes.
- **N7.** The effect of `-g` on compilers other than clang 18.1.0 and 19.1.0 (assertions builds), and on the pipeline and LICM answers. For the two compilers named, the log is identical with `-g0` appended (`derived/g0_comparison.txt`).
- **N8.** Intermediate compilers: only the Compiler Explorer builds listed in `derived/compilers-used.json` were used. Revisions were recorded for six of the ids (Method).
- **N9.** Why trunk's own libc++ headers give the rejection text "complex writes to memory" and libc++ 18.1.0 headers or no library give "no supported condition load", at one compiler revision (F10).
- **N10.** The value of the legalization factor `LT.first` in the cost formula: it was fitted to seven logged numbers, not read from the legalization code (F6).
- **N11.** The hoisting and `__restrict` counterfactuals on the libc++ kernel itself. They were run on the library-free emulation only (F10).

## Files

| path | what |
|---|---|
| `src/` | sources compiled: the kernel and four library-free variants |
| `ce.py`, `run_requests.py` | the cached Compiler Explorer client and the list of every request (`MANIFEST`) |
| `raw/` | every saved answer, with its request (`*.json`, `*.json.gz`) |
| `requests.tsv` | log of the 94 requests |
| `analyze.py`, `cost_table.py`, `lv_summary.py`, `pipe_tools.py`, `loadtrack.py` | offline analysis of `raw/` |
| `derived/` | outputs of the analysis: `tables.md` (outcome tables), `readme-table.md` (the table at the top of this file), `cost-table.md`, `outcomes.tsv`, `revisions.txt`, IR dumps and diffs, `first_umin.txt`, `loads_in_loop.txt`, `licm_hoisting.txt`, `tbaa_pointer_loads.txt`, `g0_comparison.txt` |
| `fetch_llvm_src.py`, `llvm-src/` | the LLVM passages quoted, commits, and tag containment (third-party material: `llvm-src/NOTICE` gives the source and the licence) |
| `check.py` | offline verification of the statements above |

To reproduce: `python run_requests.py` (sends only missing requests, 94 for an empty `raw/`), `python analyze.py`, `python fetch_llvm_src.py`, `python check.py`. Compiler Explorer's trunk builds move daily, so the trunk rows will drift; the version-numbered rows should not.
