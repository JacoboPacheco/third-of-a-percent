# Gaps, round 2 (hostile but fair review)

Written Tue Oct 13 2026. Read for this file: README.md, site/index.html (tag-stripped), readme-parts/DETAILS.md (grep), harness/criteria-v3.json (grep), harness/pool.py header, harness/run.py (grep), kernels/common.hpp, k04, k08, gaps/GAPS.md. NOT read in full: site/details.html, pool.py body, stats.py, the other kernels, claims-audit/CLAIMS-4.md. External: https://libcxx.llvm.org/Hardening.html loaded (fast = valid-element-access + valid-input-range; extensive adds non-null, non-overlapping-ranges, valid-deallocation and more; iterator bounds checks need an ABI option such as _LIBCPP_ABI_BOUNDED_ITERATORS, not just a mode; the page says nothing of vectorization or version history). LLVM release notes were NOT loaded for 19/20/21, so what changed after 18 is unverified. No WebSearch was run. Severity H/M/L. "Click" = needs the author's action (settings, billing, publishing). "Meas" = needs a new measurement.

## 1. Statistics

1. H. Repetitions are treated as independent. ABBA runs are consecutive processes on one VM, so noise (neighbour load, frequency) is autocorrelated; the bootstrap resamples reps independently (criteria-v3.json:48-49, "resamples of each side independently"). Intervals are likely too narrow; the project's own reruns land outside earlier intervals (the audit of stage S3). Fix: block bootstrap over ABBA blocks, or paired per-block ratios, recomputed from stored raw samples. Click no. Meas no.
2. M. Multiple comparisons: 8 kernels x 2 sizes x 2 columns x CPU models, many 95% intervals, no family-wise handling. The pattern rule is conservative on the "lose SIMD" side, but the "forward <= 2%" side needs every cell to pass; the headline "2.8x to 8.0x" is a min/max over cells (selected extremes). Fix: one sentence saying which claims are per-cell and that ranges are ranges, not intervals. Click no. Meas no.
3. M. Pooling is a geometric mean over per-job ratios with 3 to 5 jobs for most CPU models (criteria-v3.json:151 admits the outer bootstrap understates spread and percentiles are coarse). Job counts are printed, but 3-job intervals still look like intervals. Fix: for J<8 make per-job points the primary mark. Click no. Meas no.
4. M. The A/A floor moves 0.25 to 3.7% between jobs (the audit of stage S3); the pass threshold (2 x A/A half-width) depends on the noise it judges, and a noisy-A/A job is excluded, which is a selection step. Rules were written before the runs, but excluded/drawn per model is not shown beside Table 1. Fix: print it. Click no. Meas no.
5. L. 20 to 40 reps per side makes the median coarse (pool_check.py:29 notes a lumpy tail). Fix: a sensitivity row with Hodges-Lehmann or trimmed mean. Click no. Meas no.

## 2. Measurement validity

6. H. No frequency, turbo, or steal-time control recorded. grep of harness/run.py finds `taskset -c <cpu>` (default CPU "1", run.py:394) and lscpu, but no governor, MHz, or /proc/stat steal. On a shared VM vCPU 1 may share a core with a neighbour's thread; ABBA mitigates drift, not bursts. Fix: record steal and cpu MHz before and after each rep; flag reps with steal > 0; add a VM caveat line. Click no. Meas yes (going forward, or small rerun).
7. M. Same fixed vCPU on every job, topology unchecked. Fix: record per-CPU load before pinning, pick the idlest. Meas yes.
8. M. Kernels are easy and uniform: int32 only, `operator[]` everywhere (k04: `c[i] = a[i] * 2`), noinline function in a warm loop over the same data. Missing: float/double (reductions do not vectorize without fast-math), vector of structs, range-for and iterator loops (per the libc++ page iterator checks need an ABI option, so FAST exposure in real code may be narrower than operator[] loops suggest), span, string, std algorithms. The census partly covers this but counts loops, not shapes. Fix: an "exposure" paragraph with a 3-line test of which accesses FAST traps in libc++ 18, and a float kernel or two. Click no. Meas small.
9. M. Headline sizes are L1 and L2 only; RAM cells did not reproduce (`docs/dayone-results.md` and the later runs) and are dropped from N. Honest, but a reader asks about big arrays. Fix: state it on the page with the non-reproduced run. Meas yes to settle.
10. L. Checksum anti-optimisation is sound (BARRIER per call, checksum printed once; common.hpp). It is not verified here that check.py asserts NONE and FAST checksums are equal per pair. Fix: confirm and cite in DETAILS. Click no.
11. L. Wall clock over `iters` calls after one untimed warm-up; frequency ramp inside the first reps unknown. Covered by 6.

## 3. Claim wording a C++ engineer attacks

12. H. "Lose SIMD" is central. Attack: "SSE2 baseline only; -march=x86-64-v3 or -O3 differs". The page says baseline and an AVX2 sibling exists, but the hero reads general. Fix: put "clang 18, libc++ 18, -O2, SSE2" in the abstract's first sentence, not in the limits box. Click no.
13. H. Timing is libc++ 18 (Ubuntu noble libc++-18-dev). Google's post (Nov 2024) used a newer toolchain with PGO, and libc++ hardening has changed since 18 (how: UNVERIFIED, release notes not read). Clang 20 / libc++ 20 is compile-only for most checks. Fix: timed clang 20 or 21 column for the four headline kernels, or "18 only" in the title block. Meas yes (Actions billing). Click: billing.
14. M. FAST vs EXTENSIVE: the study times FAST; Google's deployed configuration and opt-outs differ (per ACM Queue, https://queue.acm.org/detail.cfm?id=3773097, as summarised in GAPS.md round 1; not re-read now). The "neither confirms nor contradicts" line is right; put "no PGO in the main timing" in the sentence beside the 0.30% rather than a later bullet.
15. M. README "GCC differs. With GCC 14's checks at -O3": GCC's `_GLIBCXX_ASSERTIONS` is a different mechanism from libc++ FAST, so it is not a like-for-like comparison. Fix: say "libstdc++ assertions". Click no.
16. M. Real-program numbers (README, "1.2% to 7.5%") sit near the 0.30% quote and read as a rebuttal; the "picked for their lost loops" disclosure is in a later bullet. Fix: same bullet. Click no.
17. L. "Status: in progress" and "v0.x" on a page linked from a resume read as unfinished. Author's call.

## 4. First 60 seconds

18. H. The served site/index.html has a "SAMPLE DATA ... a made-up file" banner and `&hellip;` placeholders in every number (data-v spans, filled by JS). With JS blocked, slow, or in a link preview or recruiter's phone reader, the first screen is a sample-data banner with blanks. Whether the banner hides on real data is UNVERIFIED (the page was not run). Fix: bake the real numbers into the static HTML at build time (check.py already computes them); JS only enhances; add Open Graph title and description. Click no. Meas no.
19. M. The best line ("2.8x to 8.0x slower in cache for loops that lose SIMD") is the first bullet under "What we found", after a six-line glossary. Fix: one verdict sentence above the glossary.
20. M. 13,119 px on a phone; Figure 1 comes after the abstract and the limits box. Fix: figure first, or a 3-bullet takeaway.
21. L. Glossary before the claim; most engineers know SIMD. Move it down.

## 5. What good comparables do that this does not

22. M. Pre-registration is weakened: rules v1 to v3 were loosened after seeing results (README admits it). The holdout is the answer but is mentioned only in the trust list ("matched on 7763 and 9V74, not 9V45"). Fix: put the holdout result in the abstract in one clause.
23. M. One-click reproduction is claimed (`gh workflow run measure.yml`) but no visible green run on the public repo. Fix: a README badge for the latest successful run. Click maybe (public repo settings, Actions billing).
24. M. Related work is thin in this round's reading: Google blog, ACM Queue, Carruth's post (https://chandlerc.blog/posts/2024/11/story-time-bounds-checking/), RFC (all from GAPS.md round 1). No arXiv search was made for bounds-check-overhead papers. Fix: a 5-line related-work with verified links (bounds-check elimination in Java, Go, Rust compilers).
25. L. No toggle for placement or PGO on the figure; the per-cell assembly drawer is already stronger than most write-ups.
26. L. Limits are scattered (README, page box, DETAILS). One threats-to-validity table (internal, external, construct) reads as paper-grade.

## Top 10 next tasks (ranked)

1. Bake real numbers into static HTML, drop the SAMPLE-DATA banner from the served first screen, add Open Graph tags (18). No click, no meas.
2. Block bootstrap or per-ABBA-block paired ratios from stored raw samples; report how much intervals widen (1). No meas.
3. First sentence next to 0.30%: clang 18, libc++ 18, -O2, SSE2, no PGO in the main timing, selected programs (12, 13, 14, 16).
4. Test and document which accesses FAST traps in libc++ 18 (operator[], iterator deref, range-for), cite the libc++ page, add an exposure paragraph; consider a float kernel (8).
5. Record steal time and CPU MHz per rep and add a VM caveat (6, 7). Needs Actions billing for the rerun.
6. Read LLVM 19/20/21 release notes, then time clang 20 or 21 on the four headline kernels (13). Needs Actions.
7. For J < 8 jobs make per-job points primary; print jobs excluded over drawn (3, 4).
8. Verdict sentence above the glossary; figure before abstract (19, 20, 21).
9. Reword the GCC bullet to libstdc++ assertions (15).
10. Related-work paragraph with verified links, one threats-to-validity table, holdout in the abstract (22, 24, 26).
