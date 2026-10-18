### Neoverse-N2: neither

On Neoverse-N2 (6 jobs, 1 run pooled): neither. the two columns disagree: as compiled falls (fixed share 1.332 (95% 1.330 to 1.334), above 1.2: the excess per inner call is smaller at the larger d); aligned H1 (fixed share 1.090 (95% 1.089 to 1.091), inside 0.8 to 1.2: the excess per inner call is the same at every d). Moving the loops is the control that was varied, and a word that does not survive it is not claimed

- jobs 6, runs 39018966032
- as compiled: falls (fixed share 1.332 (95% 1.330 to 1.334), above 1.2: the excess per inner call is smaller at the larger d)
- aligned: H1 (fixed share 1.090 (95% 1.089 to 1.091), inside 0.8 to 1.2: the excess per inner call is the same at every d)
- A/A (the same binary against a copy, d = 36): ratio 0.9999, half-width 0.034%
- the rule's statistic, the excess per inner call in units of t_N(d_max) over the fit ladder [12, 20, 28, 36, 44, 52]: fixed 0.6914 [0.6906, 0.6921], per-element part at d_max -0.1724 [-0.1733, -0.1714]; fixed share 1.332 [1.330, 1.334]; growth of the fitted excess from d_min to d_max 0.796 [0.796, 0.798]; undefined resamples 0.0%
- time per inner call affine in d: median largest relative residual 0.0309 (limit 0.1); excess affine in d: 0.0599 (limit 0.15)
- y view (decides nothing), 1/(R-1) = 0.5122 + 0.02598 d, slope 95% [0.02592, 0.02603]; dilution Q = 2.261 [2.256, 2.265]
- inverse view (decides nothing), R - 1 = 0.3419 + 11.79/d (slope 95% [11.7, 11.85])

| d | role | d mod 8 | FAST/NONE as compiled [95%] | aligned [95%] | excess ns per inner call | placement D | extra instr per inner call (not time) | published |
|---|---|---|---|---|---|---|---|---|
| 12 | fit | 4 | 2.309 [2.304, 2.314] | 2.186 [2.186, 2.187] | 4.857 | 1.056 * | 77.22 | - |
| 20 | fit | 4 | 1.960 [1.959, 1.961] | 1.907 [1.906, 1.908] | 4.391 | 1.027 * | 77.12 | - |
| 28 | fit | 4 | 1.766 [1.765, 1.767] | 1.760 [1.760, 1.760] | 3.990 | 1.003 * | 77.08 | - |
| 36 | fit | 4 | 1.673 [1.672, 1.673] | 1.716 [1.715, 1.716] | 3.876 | 0.975 * | 77.06 | - |
| 44 | fit | 4 | 1.610 [1.609, 1.610] | 1.654 [1.654, 1.655] | 3.864 | 0.973 * | 77.05 | - |
| 45 | scan | 5 | 1.591 [1.590, 1.591] | 1.625 [1.625, 1.626] | 4.109 | 0.979 * | 85.05 | - |
| 46 | scan | 6 | 1.624 [1.623, 1.625] | 1.668 [1.667, 1.669] | 4.515 | 0.974 * | 93.05 | - |
| 47 | scan | 7 | 1.618 [1.617, 1.619] | 1.642 [1.641, 1.642] | 4.829 | 0.986 * | 101.05 | - |
| 48 | scan | 0 | 2.634 [2.633, 2.635] | 2.634 [2.633, 2.635] | 8.232 | 1.000 | 153.04 | - |
| 49 | scan | 1 | 1.497 [1.497, 1.498] | 1.553 [1.552, 1.553] | 2.890 | 0.964 * | 53.04 | - |
| 50 | scan | 2 | 1.523 [1.523, 1.524] | 1.565 [1.565, 1.566] | 3.239 | 0.973 * | 61.04 | - |
| 51 | scan | 3 | 1.533 [1.533, 1.534] | 1.577 [1.577, 1.577] | 3.534 | 0.972 * | 69.04 | - |
| 52 | fit+study_l1 | 4 | 1.548 [1.548, 1.549] | 1.589 [1.589, 1.589] | 3.881 | 0.974 * | 77.04 | 1.548 |
| 76 | bridge | 4 | 1.425 [1.424, 1.425] | 1.469 [1.469, 1.470] | 3.808 | 0.970 * | 77.03 | - |
| 108 | bridge | 4 | 1.337 [1.336, 1.338] | 1.362 [1.361, 1.362] | 3.908 | 0.982 * | 77.02 | - |
| 148 | bridge | 4 | 1.174 [1.174, 1.174] | 1.226 [1.225, 1.226] | 2.819 | 0.958 * | 77.01 | - |
| 209 | study_l2 | 1 | 1.016 [1.016, 1.016] | 1.018 [1.017, 1.018] | 0.462 | 0.999 * | 53.01 | 1.016 |

Rows with role fit enter the fit; scan, bridge and study_l2 are context. `*` marks a placement-sensitive d (criteria-v3 rule). Published = the pooled as-compiled ratio already published for this CPU model (a sanity reading, not a criterion).

