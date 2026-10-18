### AMD EPYC 7763 64-Core Processor: H2

On AMD EPYC 7763 64-Core Processor (9 jobs, 2 runs pooled): H2. fixed share 0.032 (95% 0.027 to 0.035), inside -0.2 to 0.2: the excess per inner call is proportional to d

- jobs 9, runs 39018969973, 39018974239
- as compiled: H2 (fixed share 0.032 (95% 0.027 to 0.035), inside -0.2 to 0.2: the excess per inner call is proportional to d)
- aligned: H2 (fixed share 0.040 (95% 0.037 to 0.043), inside -0.2 to 0.2: the excess per inner call is proportional to d)
- A/A (the same binary against a copy, d = 28): ratio 1.0000, half-width 0.061%
- the rule's statistic, the excess per inner call in units of t_N(d_max) over the fit ladder [12, 20, 28, 36]: fixed 0.06887 [0.05815, 0.07527], per-element part at d_max 2.097 [2.076, 2.135]; fixed share 0.032 [0.027, 0.035]; growth of the fitted excess from d_min to d_max 2.821 [2.804, 2.849]; undefined resamples 0.0%
- time per inner call affine in d: median largest relative residual 0.0163 (limit 0.1); excess affine in d: 0.0224 (limit 0.15)
- y view (decides nothing), 1/(R-1) = 0.7392 + -0.008069 d, slope 95% [-0.008216, -0.007962]; dilution Q = 0.699 [0.692, 0.703]
- inverse view (decides nothing), R - 1 = 2.402 + -10.9/d (slope 95% [-11.31, -10.67])

| d | role | d mod 8 | FAST/NONE as compiled [95%] | aligned [95%] | excess ns per inner call | placement D | extra instr per inner call (not time) | published |
|---|---|---|---|---|---|---|---|---|
| 12 | fit | 4 | 2.545 [2.542, 2.550] | 2.544 [2.541, 2.550] | 6.101 | 1.000 | 93.76 | - |
| 20 | fit | 4 | 2.733 [2.723, 2.750] | 2.850 [2.819, 2.874] | 9.247 | 0.959 * | 167.28 | - |
| 28 | fit | 4 | 3.002 [2.991, 3.023] | 3.017 [3.015, 3.018] | 13.011 | 0.995 | 240.49 | - |
| 29 | scan | 5 | 2.717 [2.704, 2.742] | 2.834 [2.832, 2.835] | 12.740 | 0.959 * | 241.51 | - |
| 30 | scan | 6 | 2.915 [2.907, 2.929] | 3.328 [3.216, 3.479] | 13.606 | 0.876 * | 255.52 | - |
| 31 | scan | 7 | 2.775 [2.757, 2.798] | 2.891 [2.889, 2.892] | 13.714 | 0.960 * | 256.54 | - |
| 32 | scan | 0 | 3.384 [3.366, 3.416] | 3.359 [3.355, 3.367] | 15.503 | 1.008 * | 290.55 | - |
| 33 | scan | 1 | 3.177 [3.165, 3.199] | 3.147 [3.145, 3.149] | 15.522 | 1.010 * | 286.57 | - |
| 34 | scan | 2 | 3.150 [3.137, 3.174] | 3.133 [3.132, 3.134] | 15.843 | 1.005 * | 298.58 | - |
| 35 | scan | 3 | 3.089 [3.077, 3.112] | 3.213 [3.210, 3.215] | 16.107 | 0.962 * | 299.59 | - |
| 36 | fit+study_l1 | 4 | 3.183 [3.167, 3.211] | 3.187 [3.184, 3.194] | 16.802 | 0.999 | 313.60 | 3.190 |
| 52 | bridge | 4 | 3.392 [3.373, 3.426] | 3.456 [3.454, 3.460] | 24.281 | 0.981 * | 459.73 | - |
| 76 | bridge | 4 | 4.169 [4.157, 4.182] | 3.787 [3.676, 3.945] | 44.859 | 1.101 * | 678.81 | - |
| 100 | bridge | 4 | 4.012 [4.001, 4.028] | 3.989 [3.987, 3.990] | 55.796 | 1.006 * | 897.86 | - |
| 147 | study_l2 | 3 | 3.785 [3.769, 3.812] | 3.798 [3.796, 3.800] | 76.549 | 0.997 | 1321.90 | 3.790 |

Rows with role fit enter the fit; scan, bridge and study_l2 are context. `*` marks a placement-sensitive d (criteria-v3 rule). Published = the pooled as-compiled ratio already published for this CPU model (a sanity reading, not a criterion).

### AMD EPYC 9V45 96-Core Processor: too few jobs

On AMD EPYC 9V45 96-Core Processor (2 jobs, 1 run pooled): too few jobs. 2 job(s) of this CPU model; the minimum is 3

- jobs 2, runs 39018969973
- as compiled: too few jobs (2 job(s) of this CPU model; the minimum is 3)
- aligned: too few jobs (2 job(s) of this CPU model; the minimum is 3)
- A/A (the same binary against a copy, d = 29): ratio 1.0013, half-width 0.834%
- the rule's statistic, the excess per inner call in units of t_N(d_max) over the fit ladder [13, 21, 29, 37, 45]: fixed -0.2009 [-0.2238, -0.1805], per-element part at d_max 4.201 [4.16, 4.26]; fixed share -0.050 [-0.056, -0.045]; growth of the fitted excess from d_min to d_max 3.950 [3.893, 4.010]; undefined resamples 0.0%
- time per inner call affine in d: median largest relative residual 0.1627 (limit 0.1); excess affine in d: 0.0783 (limit 0.15)
- y view (decides nothing), 1/(R-1) = 0.5827 + -0.00839 d, slope 95% [-0.008665, -0.008129]; dilution Q = 0.433 [0.418, 0.448]
- inverse view (decides nothing), R - 1 = 4.858 + -39.87/d (slope 95% [-41.6, -38.2])

| d | role | d mod 8 | FAST/NONE as compiled [95%] | aligned [95%] | excess ns per inner call | placement D | extra instr per inner call (not time) | published |
|---|---|---|---|---|---|---|---|---|
| 13 | fit | 5 | 2.853 [2.828, 2.874] | 2.884 [2.843, 2.907] | 4.588 | 0.989 | 94.86 | - |
| 21 | fit | 5 | 3.717 [3.698, 3.744] | 2.689 [2.641, 2.774] | 10.583 | 1.382 * | 168.31 | - |
| 29 | fit | 5 | 4.642 [4.576, 4.722] | 3.426 [3.376, 3.481] | 14.971 | 1.355 * | 241.51 | - |
| 37 | fit | 5 | 4.947 [4.814, 5.065] | 3.832 [3.758, 3.900] | 18.707 | 1.291 * | 314.61 | - |
| 38 | scan | 6 | 4.556 [4.514, 4.591] | 3.707 [3.665, 3.747] | 18.614 | 1.229 * | 328.62 | - |
| 39 | scan | 7 | 4.649 [4.614, 4.688] | 3.719 [3.685, 3.792] | 19.132 | 1.250 * | 329.63 | - |
| 40 | scan | 0 | 4.730 [4.699, 4.761] | 3.701 [3.664, 3.727] | 19.436 | 1.278 * | 363.64 | - |
| 41 | scan | 1 | 4.625 [4.581, 4.662] | 3.649 [3.617, 3.676] | 19.660 | 1.268 * | 359.65 | - |
| 42 | scan | 2 | 4.628 [4.563, 4.739] | 3.695 [3.662, 3.734] | 20.322 | 1.252 * | 371.66 | - |
| 43 | scan | 3 | 4.719 [4.668, 4.775] | 3.770 [3.739, 3.821] | 20.528 | 1.252 * | 372.67 | - |
| 44 | scan | 4 | 4.878 [4.793, 4.974] | 3.957 [3.874, 4.034] | 21.127 | 1.233 * | 386.68 | - |
| 45 | fit+study_l1 | 5 | 4.826 [4.773, 4.904] | 3.919 [3.880, 3.938] | 21.478 | 1.231 * | 387.68 | 4.836 |
| 69 | bridge | 5 | 4.605 [4.540, 4.669] | 3.901 [3.874, 3.928] | 30.497 | 1.180 * | 606.80 | - |
| 93 | bridge | 5 | 4.479 [4.430, 4.510] | 4.397 [4.355, 4.433] | 38.259 | 1.019 * | 825.85 | - |
| 141 | bridge | 5 | 4.283 [4.248, 4.319] | 4.312 [4.240, 4.419] | 54.821 | 0.993 | 1263.90 | - |
| 209 | study_l2 | 1 | 4.101 [4.022, 4.163] | 4.085 [4.045, 4.145] | 78.921 | 1.004 | 1892.93 | 4.118 |

Rows with role fit enter the fit; scan, bridge and study_l2 are context. `*` marks a placement-sensitive d (criteria-v3 rule). Published = the pooled as-compiled ratio already published for this CPU model (a sanity reading, not a criterion).

### INTEL(R) XEON(R) PLATINUM 8573C: too few jobs

On INTEL(R) XEON(R) PLATINUM 8573C (1 job, 1 run pooled): too few jobs. 1 job(s) of this CPU model; the minimum is 3

- jobs 1, runs 39018969973
- as compiled: too few jobs (1 job(s) of this CPU model; the minimum is 3)
- aligned: too few jobs (1 job(s) of this CPU model; the minimum is 3)
- A/A (the same binary against a copy, d = 29): ratio 0.9991, half-width 0.287%
- the rule's statistic, the excess per inner call in units of t_N(d_max) over the fit ladder [13, 21, 29, 37, 45]: fixed -0.6381 [-0.6519, -0.6298], per-element part at d_max 3.441 [3.424, 3.469]; fixed share -0.228 [-0.232, -0.225]; growth of the fitted excess from d_min to d_max 7.876 [7.764, 8.056]; undefined resamples 0.0%
- time per inner call affine in d: median largest relative residual 0.2345 (limit 0.1); excess affine in d: 0.2495 (limit 0.15)
- y view (decides nothing), 1/(R-1) = 1.015 + -0.01566 d, slope 95% [-0.01602, -0.01543]; dilution Q = 0.383 [0.375, 0.388]
- inverse view (decides nothing), R - 1 = 3.207 + -29.19/d (slope 95% [-29.62, -28.92])

| d | role | d mod 8 | FAST/NONE as compiled [95%] | aligned [95%] | excess ns per inner call | placement D | extra instr per inner call (not time) | published |
|---|---|---|---|---|---|---|---|---|
| 13 | fit | 5 | 2.153 [2.136, 2.166] | 1.889 [1.881, 1.892] | 5.537 | 1.140 * | 94.86 | - |
| 21 | fit | 5 | 2.619 [2.603, 2.634] | 2.517 [2.514, 2.519] | 10.011 | 1.040 * | 168.31 | - |
| 29 | fit | 5 | 2.874 [2.864, 2.884] | 2.693 [2.687, 2.699] | 13.567 | 1.068 * | 241.51 | - |
| 37 | fit | 5 | 3.112 [3.101, 3.139] | 2.899 [2.892, 2.907] | 18.297 | 1.073 * | 314.61 | - |
| 38 | scan | 6 | 3.152 [3.142, 3.174] | 3.011 [3.003, 3.022] | 18.478 | 1.047 * | 328.62 | - |
| 39 | scan | 7 | 2.950 [2.941, 2.960] | 2.788 [2.782, 2.796] | 18.107 | 1.058 * | 329.63 | - |
| 40 | scan | 0 | 3.272 [3.255, 3.287] | 3.219 [3.210, 3.232] | 19.749 | 1.016 * | 363.64 | - |
| 41 | scan | 1 | 3.142 [3.085, 3.164] | 3.075 [3.063, 3.080] | 19.717 | 1.022 * | 359.65 | - |
| 42 | scan | 2 | 4.035 [4.022, 4.049] | 3.106 [3.054, 3.175] | 27.658 | 1.299 * | 371.66 | - |
| 43 | scan | 3 | 4.082 [4.067, 4.099] | 3.105 [3.094, 3.114] | 29.553 | 1.314 * | 372.67 | - |
| 44 | scan | 4 | 4.261 [4.231, 4.285] | 3.588 [3.470, 3.690] | 29.917 | 1.187 * | 386.68 | - |
| 45 | fit+study_l1 | 5 | 4.196 [4.183, 4.217] | 3.180 [3.092, 3.317] | 32.250 | 1.320 * | 387.68 | - |
| 69 | bridge | 5 | 3.923 [3.913, 3.930] | 3.210 [3.202, 3.224] | 41.490 | 1.222 * | 606.80 | - |
| 117 | bridge | 5 | 3.729 [3.717, 3.736] | 3.315 [3.289, 3.329] | 64.291 | 1.125 * | 1044.88 | - |
| 181 | bridge | 5 | 3.606 [3.596, 3.621] | 3.618 [3.609, 3.625] | 95.620 | 0.997 | 1628.92 | - |
| 295 | study_l2 | 7 | 3.521 [3.515, 3.526] | 3.480 [3.475, 3.485] | 146.205 | 1.012 * | 2665.95 | - |

Rows with role fit enter the fit; scan, bridge and study_l2 are context. `*` marks a placement-sensitive d (criteria-v3 rule). Published = the pooled as-compiled ratio already published for this CPU model (a sanity reading, not a criterion).

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

