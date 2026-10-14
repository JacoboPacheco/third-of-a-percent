# Claims audit 7: the contrast band, the mechanism demo, "How can 0.30% be true?", the hero captions and the section gists

Written Wed Oct 14 2026 against the working tree at commit f85511f. Scope: text a visitor reads on `site/index.html` that is new since `claims-audit/CLAIMS-6.md`: `#band`, `#mech` (explanation strings in `site/story.js`), `#average`, the hero captions (`CAP` and `WHAT` in `site/race.js`) and the section gists. Nothing under `site/` was edited; recommended wording is listed below. Classes: SUPPORTED, OVERSTATED (true, but said more strongly or more widely than the data), UNSUPPORTED (no data in the repository backs it, or the page's own detail text says otherwise), UNVERIFIABLE (cannot be checked from here).

Result: 46 claims. 37 SUPPORTED, 7 OVERSTATED, 1 UNSUPPORTED, 1 UNVERIFIABLE.

## Sources used

- Google post, read this session: `curl` returned the full page (147,441 bytes); the built-in fetch tool returned only the title and navigation. Quotes below are from the curl copy.
  - "Building on the successful deployment of hardened libc++ in Chrome in 2022, we've now made it default across our server-side production systems."
  - "Hardening libc++ resulted in an average 0.30% performance impact across our services (yes, only a third of a percent). This is due to both the compiler's ability to eliminate redundant checks during optimization, and the efficient design of hardened libc++."
  - "Techniques like profile-guided optimizations further improved performance, but even without those advanced techniques, the overhead of bounds checking remains minimal."
  - "we identified and fixed an unnecessary check, which led to a 15% reduction in overhead (reduced from 0.35% to 0.3%)".
  - The words CPU, latency and benchmark do not occur in the post. It says only that "extensive performance evaluations" were done.
- `site/data/pooled.json` (cells per CPU model), `site/data/realworld.json` (rows, timing groups), `site/data/corpus.json` (census totals), `site/data/cesweep.json` (54 clang rows), `site/data/mitigate.json` (recommended-rewrite ranges), `site/data/related.json`.
- `results/s3-audit-run-38127024171/results-amd-epyc-9v45-96-core-processor-j2/{remarks,asm}`: compiler remarks and assembly for the eight kernels (clang 18). `versions/MATMUL-EXPLAINED.md`. `site/details.html` lines 57 and 66.

## Numbers recomputed

| Number on the page | Recomputed from | Result |
|---|---|---|
| Band: 8.0x, reverse, EPYC 7763 | `pooled.json`, 7763, `k04_rev.L1`: aligned 8.01, as compiled 7.62; L2 7.78 and 7.67; the largest of the eight at L1 | matches (the default column is aligned) |
| Census 1: 1 lost of 593, 19 projects | `corpus.json` census1: 593 vectorized with checks off, 592 with checks on, lost 1, gained 0, projects 19 | matches |
| Census 1 origin of the 593 | `vectorized_by_origin` with checks off: libc++ 443, project 150; the 1 lost loop is in project code (leveldb) | new qualifier |
| Census 2: 444 of 4,968 | census2 totals: 4,968 with checks off, 4,535 with checks on, lost 444 (all in project code; LightGBM 331), gained 17; 444/4968 = 8.94% | matches |
| "about 0 to 6% of the instructions" | `realworld.json` rows, `lines_none` (Cachegrind, checks off, the lost loops' own source lines): spectra about 0.0, tiny-dnn 0.03%, LightGBM default 0.0006%, Draco 0.24%, LightGBM multiclass 0.51%, LightGBM linear 6.25% (maximum, flagged `approximate`). `funcs_none` (their whole functions) reaches 16.4% (tiny-dnn) | matches for lines; the share of functions is up to 16.4% |
| "1.2 to 7.5%" | EPYC 7763 (16 jobs), detectably slower rows, both columns: minimum 1.0115 (LightGBM default aligned), maximum 1.0754 (Draco as compiled) | matches for EPYC 7763 only |
| Same range on other models | EPYC 9V74 (3 jobs): LightGBM default 1.0095 and 1.0073, so 0.7% to 0.95%, below the printed minimum. EPYC 9V45 (5 jobs): up to 5.4% on Draco | the range is not model-independent |
| Section 5 gist, 0.99 to 1.09x | `mitigate.json`, recommended rewrite per shape: reverse 0.985 to 1.086, matrix multiply 0.992 to 1.002 | matches |
| Section 6 gist, "clang always loses reverse and strided" | `cesweep.json`: all 54 clang rows (majors 12 to 23) have `k04_rev` and `k05_stride2` lost; GCC 30 rows differ | matches |
| Section 1 gist, "near 1x ... when aligned" | `pooled.json` aligned L1: `k02_add_fwd` 0.84 (7763), 0.84 (9V45), 0.82 (9V74); `k03_stencil` 1.06 (7763), 1.02 (9V45) | see claim 41 |

## Every claim

### The contrast band (`#band`)

| # | Claim | Evidence | Class |
|---|---|---|---|
| 1 | "0.30% Google's reported average, over whole services" | the post's sentence: "average 0.30% performance impact across our services" | SUPPORTED |
| 2 | "8.0x ... reverse, EPYC 7763 ... one loop, same check" (the number) | `pooled.json` aligned L1 8.01; recomputed above | SUPPORTED |
| 3 | "This study's worst loop" | it is the largest of eight hand-written kernels, at the smallest working set, in the aligned column. Larger working sets were not compared for this label, and the eight were chosen by the study | OVERSTATED. Fix: "The slowest of this study's eight loops (reverse, EPYC 7763, array fits L1, aligned)" |
| 4 | "Same bounds check" | the study uses libc++ 18 `_LIBCPP_HARDENING_MODE_FAST`; the post says "hardened libc++" and does not name a mode or version | UNVERIFIABLE. Fix: "a comparable libc++ bounds check" |
| 5 | "This neither confirms nor contradicts Google's average" | no Google service measured; the real programs are not a sample of Google's | SUPPORTED |

### The mechanism demo (`#mech`, `story.js`)

| # | Claim | Evidence | Class |
|---|---|---|---|
| 6 | "SIMD: one instruction, four elements" | 32-bit integers in a 128-bit register; remarks "vectorization width: 4" for k02, k03, k04, k05, k08. The sum (k01) widens to 64-bit: "width: 2, interleaved count: 2", still four elements per pass | SUPPORTED. Optional fix: "four 32-bit elements" |
| 7 | "A check before every element can stop the compiler from grouping them" | reverse and stride-2 FAST remark "could not determine number of loop iterations"; packed instructions go from 6 and 4 (checks off) to 0 (checks on). Hedged with "can" | SUPPORTED |
| 8 | Note: "An illustration of the mechanism, inferred from the compiler's remarks and the machine code; steps are not time" | the label is present and right | SUPPORTED |
| 9 | Check off, loop not vectorized (gather, histogram): "one element per step" | remarks: `cannot identify array bounds` with checks off for k06 and k07 | SUPPORTED |
| 10 | Check off: "one Step handles four elements at once" (eight cells, two Steps) | true for the 32-bit kernels. The eight-cell row is a simplification: the stencil covers n-2 elements, stride-2 reads two inputs per output | SUPPORTED as an illustration |
| 11 | Check on, kept loops: "tests the sizes once before the loop ... the check only runs on leftover elements, and eight divide evenly by four"; sum: the check is removed | the checks-on assembly for k01 has 0 `ud2`; k02, k03 each have 1 `ud2`, reached only from the scalar remainder (compare, then jump to `ud2` after the vector loop); the vector body has `paddd` and no check | SUPPORTED (a reading of the assembly, which the page's Figure 2 also shows) |
| 12 | Check on, lost loops: "each element must pass the gate, which stops the program if the index is out of range" | checks-on assembly: `cmp` and a jump to `ud2` per element in the scalar loop | SUPPORTED |
| 13 | Reverse: "could not vectorize it once the check was inside: it no longer knows how many times the loop runs"; stride-2: "the same remark" | remarks, same file, same compiler: checks off "vectorized loop (width 4)", checks on "could not determine number of loop iterations", for both k04 and k05. The cause is shown by the contrast between two builds of the same source; the account of why the compiler cannot count is its own remark restated | SUPPORTED |
| 14 | Matrix multiply: "With the check inside, the compiler judged that vectorizing no longer pays (its own remark)" | the remark exists on clang 18 ("the cost-model indicates that vectorization is not beneficial"), but clang 19, 20 and 21 vectorize the same loop with the checks on (`versions/MATMUL-EXPLAINED.md`), and why clang 18 declines is stated there as inferred. The caption does not say clang 18 | OVERSTATED. Fix: "On clang 18, with the check inside, the compiler's own remark says vectorizing is not beneficial, so four at a time becomes one at a time (clang 19 to 21 keep SIMD here)." The cause of the clang 18 decision should be marked inferred |
| 15 | Gather and histogram, checks on: "each element passes the gate", "adds a compare and a jump to every pass" | assembly: `cmp`, `jbe` to `ud2` inside the loop for k06 (1 `ud2`); no vector instructions in either build | SUPPORTED |

### "How can 0.30% be true?" (`#average`)

| # | Claim | Evidence | Class |
|---|---|---|---|
| 16 | "An average cost of 0.30% across its services" | post sentence | SUPPORTED |
| 17 | "after hardened libc++ became the default in server-side production" | post: "we've now made it default across our server-side production systems" | SUPPORTED |
| 18 | "The post credits the compiler removing redundant checks and the design of the checks" | post: "the compiler's ability to eliminate redundant checks during optimization, and the efficient design of hardened libc++" | SUPPORTED |
| 19 | "adds that profile-guided optimization helps" | post: "Techniques like profile-guided optimizations further improved performance" | SUPPORTED |
| 20 | "and says the cost stays small without it" | post: "even without those advanced techniques, the overhead of bounds checking remains minimal". Related work on the same page records that the 2025 ACM Queue sequel (as reported) calls PGO critical and Carruth says the overhead would not be tolerable without it for most performance-sensitive workloads; the section does not mention that tension | SUPPORTED. Optional: add "Later accounts of the same rollout (ACM Queue 2025, Carruth) describe PGO as critical." |
| 21 | "one fix to an unneeded check ... moved the figure from 0.35% to 0.30%" | post: "fixed an unnecessary check ... (reduced from 0.35% to 0.3%)", which it calls a 15% reduction in overhead | SUPPORTED |
| 22 | "An average over whole services dilutes a slow loop" | arithmetic is true for any average, but it is offered as the explanation of the 0.30%. The study's own instruction shares do not support it: with the lost loops at 8.0x (Table 9's Amdahl estimate, share x 7.0) LightGBM linear would cost +44% and Draco +1.7%; the measured costs are 3.7 to 4.5% and 6.8 to 7.5%. LightGBM default has its lost loops at 0.0006% of instructions and still costs 1.2 to 1.8%. Dilution is not what the data tests | OVERSTATED. Fix: "An average over whole services can sit beside a slow loop if few services spend much time in such loops. What the programs timed here show is that where the cost shows up is not predicted by the lost loops' share of the instructions." Mark the dilution reading as inferred |
| 23 | "the loops that lose SIMD hold about 0 to 6% of the instructions" | `lines_none`: about 0 to 6.25%; the maximum is LightGBM linear, an `approximate` figure. It is the share of instructions executed with the checks off, the lost loops' own source lines only; their whole functions hold up to 16.4%. Instructions, not time | SUPPORTED. Fix: "(their own lines; up to 16% counting the functions around them)", and say "instructions executed, not time" |
| 24 | "the whole-program cost was 1.2 to 7.5% where detectable" | true on EPYC 7763 (16 jobs, both columns). On EPYC 9V74 (3 jobs) LightGBM default is 0.7% and 0.95% | OVERSTATED (unscoped). Fix: "on EPYC 7763, the model with the most jobs, 1.2 to 7.5%" |
| 25 | "Those programs were picked because they contain such loops, so that range is not an estimate for typical code" | `realworld/PLAN.md`; two controls (meshoptimizer, {fmt}) have no lost loops | SUPPORTED |
| 26 | "a service with few such loops would sit near zero" | the two programs without lost loops measured at most 0.4% (meshoptimizer, not detectable) and {fmt} 1.5 to 5.6% faster on EPYC 7763; but LightGBM default pays 1.2 to 1.8% with its lost loops at 0.0006% of instructions, so cost can appear without a large lost-loop share. A prediction, not a result | OVERSTATED. Fix: "a program with no such loops (the two controls here) showed no detectable cost on EPYC 7763; that is two programs, not a rule" |
| 27 | "How the 0.30% was computed (CPU time or latency, which services, which time window) is not in the part of the post read for this study" | the whole post was read: the words CPU, latency and benchmark do not occur in it, and it names no services list or window beyond "across our services". The phrase "the part ... read" implies a partial read | SUPPORTED as to content; the wording is stale. Fix: "The post does not say how the 0.30% was computed (CPU time or latency, which services, which time window)." |
| 28 | "No Google service was measured here" | none was | SUPPORTED |
| 29 | "it shows which loop shapes would push a program above it" | on EPYC 7763 five of six programs picked for lost loops cost 1.2 to 7.5%, all above 0.30%; "would" is a prediction for other programs | SUPPORTED, hedge optional: "can push" |
| 30 | Section 4 gist and the draft's "1 of 593 in general libraries" (the figure is in the section 4 gist and `census-p1`; the live `#average` text no longer repeats it) | census 1: 1 of 593 over 19 projects, counted as copies | SUPPORTED. Qualifier to add: 443 of the 593 vectorized loops are libc++'s own code, 150 are project code; the one lost loop is in project code (1 of 150) |
| 31 | Section 4 gist: "444 of 4,968 vectorized loops in numeric projects lose SIMD" | 444 of 4,968 (8.94%); 331 of the 444 are LightGBM | SUPPORTED |

### Hero captions (`race.js`)

| # | Claim | Evidence | Class |
|---|---|---|---|
| 32 | Forward sum: "Both builds are vectorized and, with the check on, the compiler removes the check altogether" | remarks: vectorized in both; 0 `ud2` in both builds | SUPPORTED |
| 33 | Forward add: "Both builds are vectorized; the check runs only on the leftover elements" | remark and assembly (check in the scalar remainder only) | SUPPORTED |
| 34 | Forward add, shown when the ratio is below 0.95: "Below 1x is code placement (section 3)" | `site/details.html` line 66: aligned, the forward add is faster with the checks on because clang unrolls the checked loop to four numbers per pass instead of eight, and the unchecked loop forced to four per pass was just as fast; "the speed-up comes from the compiler's unrolling choice, not from the check", and why it is faster is inferred. Section 3 (placement) explains the as-compiled cost above 1x, not the aligned cost below 1x. The hero's default column is aligned | UNSUPPORTED. Fix: "Below 1x: the checked build's SIMD loop handles fewer numbers per pass and happens to run faster here (section 3; why is inferred)." |
| 35 | Stencil: "the compiler tests the sizes once before the SIMD loop, so the check runs only on the leftover elements" | remark width 4, 12 packed instructions in both builds, 1 `ud2` | SUPPORTED |
| 36 | Reverse: "The compiler could not vectorize it once the check was inside: it no longer knows how many times the loop runs" | remark; see claim 13 | SUPPORTED |
| 37 | Stride-2: "The same remark as the reverse loop" | same remark text on k05 | SUPPORTED |
| 38 | Gather and histogram: "Not vectorized in either build ... the check adds a compare and a jump to every pass" | remarks (not vectorized, checks off and on); assembly | SUPPORTED |
| 39 | Generic captions: lost "steps one element at a time, with a check before each"; kept "the check only rides on the leftover tail"; none "No SIMD in either build" | assembly and remarks, as above (matrix multiply scalar loop: two checks per element) | SUPPORTED |
| 40 | Matrix multiply: "With the check inside, the compiler judged that vectorizing no longer pays (its own remark)" | same as claim 14; clang 19 to 21 vectorize it | OVERSTATED. Same fix as claim 14 |

### Section gists

| # | Claim | Evidence | Class |
|---|---|---|---|
| 41 | Section 1: "forward loops that keep it stay near 1x on the AMD models when aligned" | aligned L1: forward sum 1.00; stencil 1.00 to 1.02, but 1.06 on EPYC 7763; forward add 0.82 to 0.84 on all three AMD models (16 to 18% faster, not near 1x). The headline above the figure carries "one exception"; this gist does not | OVERSTATED. Fix: "stay at about 1x (0.82x to 1.06x) on the AMD models when aligned" |
| 42 | Section 2: "SIMD does several array elements per instruction. A check inside the loop can stop the compiler from using it." | as claim 7 | SUPPORTED |
| 43 | Section 3: "A forward loop looked slow on some CPUs because of where its code landed, not because of the check." | `investigate/FINDINGS.md`: with `-falign-loops=64` FAST/NONE is 0.82 to 1.0 on the three AMD models; the body of section 3 labels the hardware reason inferred | SUPPORTED (add "as compiled") |
| 44 | Section 5: "brings the reverse and matrix-multiply loops back to 0.99 to 1.09x with checks still on" | `mitigate.json`: reverse `pre` 0.985 to 1.086, matrix multiply `rowptr` 0.992 to 1.002; each rewrite passes the too-short-input safety test; 5 of 24 reverse cells left out for their own A/A | SUPPORTED |
| 45 | Section 6: "clang always loses the reverse and strided loops; GCC differs" (compile-only) | all 54 clang rows (majors 12 to 23); GCC -O2 loses none, -O3 loses the reverse and matrix-multiply loops in all 15 rows | SUPPORTED |
| 46 | Section 7: "Six real programs timed whole; where the slowdown is detectable it is 1.2 to 7.5% with checks on, on the model with the most jobs" | EPYC 7763, 16 jobs; recomputed | SUPPORTED |

## Statements of mechanism that should carry an "inferred" label

1. Claim 22 (dilution explains the small average): inferred, and the study's own instruction shares do not predict the measured cost.
2. Claims 14 and 40 (why clang 18 declines to vectorize matrix multiply): `versions/MATMUL-EXPLAINED.md` calls the cause inferred, and not bisected between clang 18 and 19; the caption states it as fact and omits the compiler version.
3. Claim 34 (why the aligned forward add is faster): `details.html` says inferred; the hero caption says "code placement".
4. Claim 11 and 13 (the compiler "tests the sizes once", "no longer knows how many times the loop runs"): the first is read from the assembly and the second restates the compiler's own remark; both are supported, and the demo note already says "inferred ... from the remarks and the machine code".

## Recommended text changes (none applied)

- `#band` label: "The slowest of this study's eight loops (reverse, EPYC 7763, array fits L1, aligned)"; band sentence: "a comparable libc++ bounds check" in place of "same bounds check".
- `#average`: reword the dilution sentence and the "near zero" sentence (claims 22, 26); scope "1.2 to 7.5%" to EPYC 7763; replace "is not in the part of the post read for this study" with "the post does not say how the 0.30% was computed"; optionally add that later accounts (ACM Queue 2025, Carruth) call PGO critical.
- `race.js` `CAP.k08_matmul.lost` and `story.js` explanation for matrix multiply: name clang 18 and note that clang 19 to 21 vectorize it.
- `race.js` `CAP.k02_add_fwd.keptBelow`: replace "code placement" with the unrolling account of `details.html` line 66.
- Section 1 gist: give the 0.82x to 1.06x range or add the exceptions.
- Census gist or `census-p1`: note that 443 of the 593 vectorized loops in census 1 are inside libc++ and the lost loop is in project code (1 of 150).
