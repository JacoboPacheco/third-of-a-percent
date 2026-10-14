/* Third of a Percent: the paper's figures and every number in its prose, read from data/ (written by
   scripts/build_site_data.py). Nothing numeric is typed into this file or into index.html. */
'use strict';

const S = {
  ix: null, pooled: null, fixture: false, cpu: null, col: 'aligned', sel: null,
  builds: {}, asm: {}, token: 0, rowEls: new Map(), mit: null, sib: null, cor: null, mitSel: null,
};
const KERNEL_NAMES = {
  k01_sum_fwd: 'Forward sum',
  k02_add_fwd: 'Forward add, two arrays',
  k03_stencil: 'Stencil, three neighbours',
  k04_rev: 'Reverse loop',
  k05_stride2: 'Stride-2 loop',
  k06_gather: 'Gather through an index',
  k07_hist: 'Histogram',
  k08_matmul: 'Matrix multiply, inner loop',
};
const SHORT_NAMES = {
  k01_sum_fwd: 'forward sum', k02_add_fwd: 'forward add', k03_stencil: 'stencil', k04_rev: 'reverse',
  k05_stride2: 'stride-2', k06_gather: 'gather', k07_hist: 'histogram', k08_matmul: 'matrix multiply',
};
const SHAPE_NAMES = { m04_rev: 'Reverse', m05_stride2: 'Stride-2', m06_gather: 'Gather', m08_matmul: 'Matrix multiply' };
const PROJECT_NAMES = { lightgbm: 'LightGBM', stockfish: 'Stockfish', 'llama.cpp': 'llama.cpp', 'whisper.cpp': 'whisper.cpp', draco: 'Draco', spectra: 'Spectra', 'tiny-dnn': 'tiny-dnn' };
function cellName(id) { // 'k03_stencil.L1' -> 'the stencil loop at the L1 size' (the exact id stays in the tables)
  const [k, sz] = id.split('.');
  return `the ${SHORT_NAMES[k] || k} loop at the ${sz} size`;
}
function perPass(remarks) { // numbers handled per pass of a vectorized loop, from clang's own remark
  const m = (remarks || []).map((r) => r.match(/vectorization width: (\d+), interleaved count: (\d+)/)).find(Boolean);
  return m ? Number(m[1]) * Number(m[2]) : null;
}
const IN_CACHE = ['L1', 'L2'];
const DOMAIN = [0.7, 10];
const TICKS = [1, 2, 4, 8];

// Two pages share this script: the main paper (data-page="main") and details.html (data-page="details").
// An element that lives on the other page resolves to a detached stand-in, so every renderer can run on both.
const PAGE = (document.body && document.body.dataset.page) || 'main';
function standIn() { const d = document.createElement('div'); d.innerHTML = '<table><thead></thead><tbody></tbody></table>'; return d; }
const $ = (id) => document.getElementById(id) || standIn();
const has = (id) => !!document.getElementById(id);
function el(tag, attrs, ...kids) {
  const n = document.createElement(tag);
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else if (k === 'style') n.setAttribute('style', v);
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) n.append(k.nodeType ? k : document.createTextNode(String(k)));
  return n;
}
const code = (t) => el('code', { text: t });
function srcLine(t) { // a C++ loop line that may wrap only between the for(...) header's parts and the body
  const nb = (x) => x.replace(/ /g, ' ');
  const i = t.indexOf('(');
  if (!t.startsWith('for') || i < 0) return nb(t);
  let depth = 0, close = -1;
  for (let j = i; j < t.length; j++) {
    if (t[j] === '(') depth++;
    else if (t[j] === ')' && --depth === 0) { close = j; break; }
  }
  if (close < 0) return nb(t);
  const head = nb(t.slice(0, close + 1)).replace(/; /g, '; ');
  return `${head} ${nb(t.slice(close + 1).trim())}`;
}

/* ---------- formatting ---------- */
function fx(v) { // a ratio: 1 decimal from 2x up, 2 below
  if (v == null || !isFinite(v)) return 'n/a';
  return v >= 2 ? v.toFixed(1) : v.toFixed(2);
}
function rangeX(lo, hi) {
  const a = fx(lo), b = fx(hi);
  return a === b ? `${a}×` : `${a}–${b}×`;
}
const rng = (r) => (r ? rangeX(r.min, r.max) : 'n/a');
const pct = (v, d = 1) => (v == null ? 'n/a' : v.toFixed(d));
const num = (v) => Number(v).toLocaleString('en-US');
function joinAnd(xs) {
  if (xs.length <= 1) return xs.join('');
  return xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];
}
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const cpuShortOf = (m) => { const e = S.ix.cpus.find((c) => c.cpu_model === m); return e ? e.cpu_short : m; };

/* ---------- data ---------- */
async function getJSON(path) {
  const r = await fetch(path, { cache: 'no-cache' });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}
async function getText(path) {
  if (S.asm[path] !== undefined) return S.asm[path];
  const r = await fetch(path, { cache: 'no-cache' });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  S.asm[path] = await r.text();
  return S.asm[path];
}
function cpuList() {
  if (S.fixture) return [{ cpu_short: S.ix.fixture.cpu_model, cpu_model: S.ix.fixture.cpu_model, slug: slug(S.ix.fixture.cpu_model), jobs: 1, runs: 1, asm: null, sample: true }];
  return S.ix.cpus.filter((c) => c.enough);
}
function currentCpu() { return cpuList().find((c) => c.slug === S.cpu) || cpuList()[0]; }
function pooledOf(model) { return S.pooled && S.pooled.cpus.find((c) => c.cpu_model === model); }
function cellOf(pc, id) { return pc && pc.cells.find((c) => c.cell_id === id); }
function column(cell) { return !cell ? null : (S.col === 'aligned' ? cell.aligned : cell.as_compiled); }
function role(cell) { return cell.class === 'lost' ? 'lost' : cell.class === 'kept' ? 'kept' : 'none'; }
const ROLE_WORDS = { lost: 'loses SIMD under the check', kept: 'keeps SIMD', none: 'no SIMD in either build' };

/* ---------- URL state ---------- */
function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  return { loop: h.get('loop'), cpu: h.get('cpu'), loops: h.get('loops') };
}
let hashLive = false; // the URL hash stays as the reader found it until the first click
function writeHash() {
  if (!hashLive) return;
  const h = new URLSearchParams();
  if (S.sel) h.set('loop', S.sel);
  if (S.cpu) h.set('cpu', S.cpu);
  h.set('loops', S.col);
  const hv = new URLSearchParams(location.hash.slice(1)).get('hero');
  if (hv) h.set('hero', hv); // keep the hero variant the reader chose
  history.replaceState(null, '', `${location.pathname}${location.search}#${h}`);
}

/* ---------- scale ---------- */
function pos(v) {
  const [lo, hi] = DOMAIN;
  const t = (Math.log(v) - Math.log(lo)) / (Math.log(hi) - Math.log(lo));
  return { p: Math.max(0, Math.min(1, t)) * 100, clipL: t < 0, clipR: t > 1 };
}
function axisInto(box, title) {
  box.replaceChildren();
  const tr = el('div', { class: 'axis-track' });
  for (const t of TICKS) tr.append(el('span', { class: 'tick', style: `left:${pos(t).p}%`, text: `${t}×` }));
  box.append(el('div', { class: 'axis-pad' }, title ? el('span', { class: 'axis-title' }, title) : null), tr, el('div', { class: 'axis-pad' }));
}

/* ---------- prose numbers ---------- */
function setV(key, val) {
  for (const n of document.querySelectorAll(`[data-v="${key}"]`)) n.textContent = val;
}
const NUM_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
const numWord = (n) => NUM_WORDS[n] || String(n);
const capFirst = (t) => t.replace(/^./, (c) => c.toUpperCase());
// a share as words when it is close to a simple fraction, else as a percentage
const shareWords = (x) => (Math.abs(x - 0.75) <= 0.03 ? 'about three quarters' : Math.abs(x - 0.5) <= 0.03 ? 'about half' : `${Math.round(x * 100)}%`);
function writtenWhen(s) { const m = (s || '').match(/^(.*?\d{2}:\d{2}\s+[A-Z]{2,4})/); return m ? m[1] : null; }
function fillStatic() {
  const ix = S.ix, pg = ix.page, cr = ix.criteria;
  // Repository files: a link into the public repository (REPO_BASE in the builder); plain monospace text if it is empty.
  const base = ix.repo.base || '';
  const repoPath = { criteriaUrl: cr.file, planUrl: 'corpus/PLAN2.md', pooledUrl: ix.pooled.source, findingsUrl: 'investigate/FINDINGS.md', robustnessUrl: 'robustness/report.md', repoUrl: '' };
  for (const n of [...document.querySelectorAll('[data-href]')]) {
    const k = n.dataset.href;
    if (k === 'claimUrl') { n.href = ix.claim.url; continue; }
    const path = repoPath[k] ?? '';
    if (base) { n.href = path ? `${base}/blob/main/${path}` : base; continue; }
    const span = el('span', { class: 'repo-path' });
    const hasCode = n.querySelector('code');
    span.append(...n.childNodes);
    if (!hasCode && path) span.append(' (', el('code', null, path), ')');
    if (!path) span.append(' (repository)');
    n.replaceWith(span);
  }
  for (const n of document.querySelectorAll('[data-title="criteriaFile"]')) n.title = `${cr.file} in the repository`;
  const rl = document.getElementById('repo-link');
  if (rl && base) rl.href = base;
  else if (rl) rl.replaceWith(el('span', null, `${rl.textContent} (repository)`));
  const good = ix.cpus.filter((c) => c.enough);
  const tc = ix.toolchain || {};
  const ver = (s) => ((s || '').match(/\d+\.\d+\.\d+/) || [''])[0];
  const v = {
    googlePct: ix.claim.google_pct.toFixed(2),
    nKernels: String(Object.keys(cr.kernels).length),
    nJobs: String(ix.pooled.jobs),
    nRuns: String(ix.pooled.runs.length),
    jobsPerRun: String(cr.jobs_per_run),
    minJobs: String(cr.minimum_jobs),
    reps: String(cr.reps_per_side),
    resamples: num(cr.resamples),
    nCpusEnough: String(pg.cpus_enough),
    lostMin: pg.lost.min.toFixed(1),
    lostMax: pg.lost.max.toFixed(1),
    fwdMin: fx(pg.forward.aligned.min),
    fwdMax: fx(pg.forward.aligned.max),
    fwdCompiledMax: fx(pg.forward.compiled.max),
    k02Max: fx(pg.forward.compiled_max_cell.ratio),
    instrMin: fx(pg.lost_instr.min), instrMax: fx(pg.lost_instr.max),
    aaCeil: cr.aa_half_width_max_pct.toFixed(0),
    aaMin: pct(Math.min(...good.map((c) => c.aa_half_width_pct)), 2),
    aaMax: pct(Math.max(...good.map((c) => c.aa_half_width_pct)), 2),
    commonFlags: tc.common_flags || '',
    clang: `clang ${ver(tc.clang)}`,
    libcxx: `libc++ ${ver(tc.libcxx_package)}`,
    criteriaFile: cr.file,
  };
  const repro = good.find((c) => c.reproduction && c.reproduction.checked > 0);
  v.reproCpu = repro ? repro.cpu_short : 'n/a';
  v.reproOut = repro ? String(repro.reproduction.outside) : 'n/a';
  v.reproChecked = repro ? String(repro.reproduction.checked) : 'n/a';
  v.reproGap = repro && repro.reproduction.max_gap_pct != null ? repro.reproduction.max_gap_pct.toFixed(1) : 'n/a';
  const psAll = good.flatMap((c) => c.placement_sensitive.map((q) => [q, c]));
  v.psSummary = psAll.length
    ? `On the CPU models with enough jobs, ${joinAnd([...new Set(psAll.map((x) => cellName(x[0].cell_id)))])} are placement-sensitive (${psAll.length} cases over the ${good.length} models). As compiled they run ${rangeX(Math.min(...psAll.map((x) => x[0].ratio)), Math.max(...psAll.map((x) => x[0].ratio)))}; aligned, ${rangeX(Math.min(...psAll.map((x) => x[0].aligned_ratio)), Math.max(...psAll.map((x) => x[0].aligned_ratio)))}. They are left out of the 2% test.`
    : 'No forward cell is placement-sensitive on the CPU models with enough jobs.';
  // stability across runs, per CPU model
  const stable = good.filter((c) => c.stability === 'stable');
  const na = good.filter((c) => c.stability !== 'stable');
  const parts = [];
  if (stable.length) parts.push(`${joinAnd(stable.map((c) => c.cpu_short))}, with enough jobs in each of its ${stable[0].per_run.length} runs, gives the same pattern in every run alone and pooled`);
  if (na.length) {
    const js = na.flatMap((c) => c.per_run.map((r) => r.jobs));
    parts.push(`${joinAnd(na.map((c) => c.cpu_short))} give the same pattern pooled, but with ${Math.min(...js)} to ${Math.max(...js)} jobs per run their runs cannot be judged one by one`);
  }
  for (const f of pg.cpus_few) parts.push(`${f.cpu_short} drew ${f.jobs} job${f.jobs > 1 ? 's' : ''}, too few to judge`);
  v.stableText = `${joinAnd(parts)}.`;
  v.fewText = pg.cpus_few.length ? `the one other model drawn, ${joinAnd(pg.cpus_few.map((f) => f.cpu_short))}, came up in ${joinAnd(pg.cpus_few.map((f) => String(f.jobs)))} job${pg.cpus_few.every((f) => f.jobs === 1) ? '' : 's'}, too few to judge.` : 'every model drawn had enough jobs.';
  // the day-one record and the criteria history
  const d1 = ix.method.dayone[0], d2 = ix.method.dayone[1];
  if (d1 && d1.missed.length) {
    const m = d1.missed[0];
    v.d1Limit = String(d1.limit);
    v.d1MissPp = m.miss_pp.toFixed(3);
    v.d1Hi = m.ci95_hi.toFixed(5);
    v.d1Cell = cellName(m.cell_id);
  }
  if (d2) v.d1RerunCells = joinAnd(d2.missed.map((m) => `${cellName(m.cell_id)} (by ${m.miss_pp.toFixed(3)} points${m.code_identical ? ', with identical machine code in both builds' : ''})`));
  const v2 = ix.method.criteria_files.find((c) => c.file.endsWith('criteria-v2.json'));
  const v3 = ix.method.criteria_files.find((c) => c.file === cr.file);
  v.v2File = v2 ? v2.file : '';
  const w2 = v2 && writtenWhen(v2.written), w3 = v3 && writtenWhen(v3.written);
  v.v2Written = w2 ? `written on ${w2}, after the first test runs existed and before the first full run` : 'written after the first test runs';
  v.v3Written = w3 ? `written on ${w3}, after every earlier run and the audit existed, and committed before the first pooled run` : 'written after the earlier runs';
  // whole programs (the earlier runs)
  const P = ix.programs;
  v.jsonTraps = P.traps_fast.json != null ? String(P.traps_fast.json) : 'n/a';
  v.fmtTraps = P.traps_fast.fmt != null ? String(P.traps_fast.fmt) : 'n/a';
  v.progMin = pct(P.at_most_pct.min); v.progMax = pct(P.at_most_pct.max);
  v.progAaMin = pct(P.aa_pct.min); v.progAaMax = pct(P.aa_pct.max);
  v.progRuns = joinAnd(P.runs.map((r) => `the ${r.label}`));
  // the forward add, faster when aligned
  const k02 = good.map((c) => [c.cpu_short, cellOf(pooledReal(c.cpu_model), 'k02_add_fwd.L1')]).filter((x) => x[1] && x[1].aligned);
  const faster = k02.filter((x) => x[1].aligned.ratio < 1);
  v.k02FasterCpus = faster.length ? joinAnd(faster.map((x) => x[0])) : 'no CPU model';
  v.k02FasterRange = faster.length ? rangeX(Math.min(...faster.map((x) => x[1].aligned.ratio)), Math.max(...faster.map((x) => x[1].aligned.ratio))) : 'n/a';
  const dflt = ix.cpus.find((c) => c.slug === ix.default_cpu);
  const kc = cellOf(pooledReal(dflt.cpu_model), 'k02_add_fwd.L1');
  const hot = kc && kc.placement && kc.placement.hot_fast;
  v.k02Bytes = hot ? String(hot.bytes) : 'n/a';
  v.k02Start = hot ? hot.start : 'n/a';
  // the rule history, from the criteria files' commits and the day-one runs
  const cf = ix.method.criteria_files;
  const fileOf = (suffix) => cf.find((c) => c.file.endsWith(suffix));
  const f0 = fileOf('dayone/criteria.json'), f1 = fileOf('harness/criteria.json'), f2 = fileOf('criteria-v2.json'), f3 = fileOf('criteria-v3.json');
  const r1 = ix.method.v1_forward_rule;
  v.v1RuleText = r1 ? `a point ratio of at most ${r1.point_max}× and an interval end of at most 1 + the larger of ${r1.ci_floor_pct.toFixed(0)}% and ${r1.aa_multiplier === 2 ? 'twice' : `${r1.aa_multiplier} times`} the job’s own A/A noise` : 'a looser ceiling';
  const dRuns = ix.method.dayone;
  const afterRuns = f1 && f1.added_at && dRuns.every((r) => r.started_at && r.started_at < f1.added_at);
  v.v1When = afterRuns ? 'committed after both day-one runs had started, and before the first harness run' : 'committed before the first harness run';
  const nMiss = dRuns.map((r) => r.missed.length);
  const ident = dRuns.some((r) => r.missed.some((m) => m.code_identical));
  v.tunedText = `Partly, and openly: v1, v2 and v3 each followed earlier results; only v1 loosened a threshold; none came after the pooled runs. The day-one rule demanded every forward loop’s interval end below ${d1 ? d1.limit : 'n/a'}×. Both day-one runs missed it: ${nMiss[0] === 1 ? 'one cell' : `${nMiss[0]} cells`} in the first (an interval ending at ${d1 && d1.missed[0] ? d1.missed[0].ci95_hi.toFixed(5) : 'n/a'}), ${nMiss[1] === 1 ? 'one' : nMiss[1] === 2 ? 'two' : nMiss[1]} in the rerun${ident ? ', one of them a loop whose checked and unchecked machine code is identical' : ''}. So it said no-go, and that no-go stays on record below. The first harness rules, ${afterRuns ? 'committed after both runs, ' : ''}replaced the ceiling with ${v.v1RuleText}. The second version added the aligned column, the layout A/A and placement-sensitive cells, after the first harness results had shown the forward add missing the original rule as compiled; the third replaced the placement-sensitive rule and pooled jobs per CPU model, after those runs and an audit.`;
  // a judged forward loop clearly below 1x (the rule bounds slowdowns only)
  const lows = [];
  for (const c of good) {
    const pc = pooledReal(c.cpu_model);
    const ps = new Set(c.placement_sensitive.map((q) => q.cell_id));
    for (const x of (pc ? pc.cells : [])) {
      if (x.class !== 'kept' || !IN_CACHE.includes(x.size_class) || ps.has(x.cell_id) || !x.aligned || x.aligned.ratio >= 0.95) continue;
      lows.push([c, x]);
    }
  }
  v.fwdLow = lows.length ? lows.map(([c, x]) => {
    const d = x.placement && x.placement.d;
    return `One judged forward loop sits well below 1×: on ${c.cpu_short}, ${cellName(x.cell_id)} runs ${fx(x.aligned.ratio)}× aligned and ${fx(x.as_compiled.ratio)}× as compiled, so the checked build is faster in both columns. It is not flagged as placement-sensitive because ${d ? `its compiled ÷ aligned ratio is ${d.ratio.toFixed(3)} with an interval from ${d.ci95[0].toFixed(3)} to ${d.ci95[1].toFixed(3)}, which includes 1: alignment does not move it` : 'alignment does not move it'}. The 2% rule bounds slowdowns only, so a faster checked build passes it; why this loop is faster there was not established.`;
  }).join(' ') : '';
  // instructions against time on the default model
  const ic = pooledReal(dflt0().cpu_model);
  const pair = (id) => { const x = cellOf(ic, id); return x && x.aligned && x.aligned_instr ? [x.aligned_instr.ratio, x.aligned.ratio] : null; };
  const h = pair('k07_hist.L1'), ad = pair('k02_add_fwd.L1');
  v.instrCpu = dflt0().cpu_short;
  v.histInstr = h ? h[0].toFixed(2) : 'n/a'; v.histTime = h ? h[1].toFixed(2) : 'n/a';
  v.addInstr = ad ? ad[0].toFixed(2) : 'n/a'; v.addTime = ad ? ad[1].toFixed(2) : 'n/a';
  // whole programs, in plain words
  const prr = (k, f) => { const xs = P.rows.map((r) => r.programs[k]).filter(Boolean).map((q) => q[f]); return xs.length ? [Math.min(...xs), Math.max(...xs)] : null; };
  const jA = prr('json', 'at_most_pct'), fA = prr('fmt', 'at_most_pct'), aa = [P.aa_pct.min, P.aa_pct.max];
  const pr = (r) => (r ? `${pct(r[0])}% to ${pct(r[1])}%` : 'n/a');
  const above = (k) => P.rows.filter((r) => r.programs[k] && r.programs[k].ci95[0] > 1);
  const nProg = (k) => P.rows.filter((r) => r.programs[k]).length;
  const aboveJ = above('json'), aboveF = above('fmt');
  const rowName = (r) => `${r.cpu_short} (${r.run_label})`;
  const clearJ = aboveJ.filter((r) => (r.programs.json.ci95[0] - 1) * 100 > r.programs.json.aa_pct); // lower interval end above the job's own noise floor
  const floorSay = clearJ.length === aboveJ.length ? 'In all of them the lower end of the interval is also above the job’s noise floor.' : clearJ.length ? `The lower end of the interval is also above the job’s noise floor in the ${joinAnd(clearJ.map((r) => r.programs.json.ratio.toFixed(3)))} ${clearJ.length > 1 ? 'rows' : 'row'} only.` : 'In none of them is the lower end of the interval above the job’s noise floor.';
  const progAbove = aboveJ.length ? ` For json, ${aboveJ.length} of ${nProg('json')} job rows have an interval that excludes 1 (it lies wholly above 1): ${joinAnd(aboveJ.map((r) => { const q = r.programs.json; return `${rowName(r)} ${q.ratio.toFixed(3)}, interval ${q.ci95[0].toFixed(3)} to ${q.ci95[1].toFixed(3)}, noise floor ${q.aa_pct.toFixed(2)}%`; }))}. ${floorSay} The other json rows${aboveF.length ? '' : ' and every fmt row'} include 1 or lie below it.` : '';
  v.progSum = `In the earlier runs (the pooled runs timed no programs), turning the checks on made nlohmann/json at most ${pr(jA)} slower depending on the job, and fmt at most ${pr(fA)}, once each job’s noise floor (${pr(aa)}) is accounted for. Those bounds are no tighter than the noise, so for the rows whose interval includes 1 they say the cost is small, not how small.${progAbove}`;
  // Intel models: the forward add at L1, aligned, in every job (no verdict)
  const IF = ix.intel_forward;
  v.intelRange = IF && IF.jobs.length ? rangeX(IF.aligned.min, IF.aligned.max).replace('×', '') : 'n/a';

  for (const [k, val] of Object.entries(v)) setV(k, val);
  // the commits, as code
  const rc = $('rule-commits');
  const item = (label, f, extra) => (f && f.added_commit ? [label, ' ', code(f.added_commit), ...(extra || [])] : [label]);
  rc.replaceChildren(...[
    item('the day-one rule', f0, [' (before any run)']), ['; '], item('the first harness rules', f1), ['; '], item('the second version', f2), ['; '],
    item('the third', f3, f3 && f3.last_commit && f3.last_commit !== f3.added_commit ? [', corrected in ', code(f3.last_commit), ' before any pooled run'] : []),
  ].flat());
  // main page: what changed after results were seen
  if (document.getElementById('tuned')) {
    const s1 = (ix.s1_forward || [])[0];
    $('tuned').replaceChildren(`Partly, and openly. The rule files v1, v2 and v3 each followed earlier results; only v1 loosened a threshold (after the day-one runs failed the original rule), and none came after the pooled runs. v2 added the aligned column and the placement-sensitive treatment after the first harness run showed the forward add missing the original rule`,
      s1 ? ` (as compiled it ran ${s1.ratio.toFixed(2)}× [${s1.ci95[0].toFixed(3)}, ${s1.ci95[1].toFixed(3)}] on ${s1.cpu_short}, run ${s1.run_id})` : '', `. Every rule file was committed before the runs it judges.`);
  }
  // the original rule applied to the pooled forward-add and stencil cells, as compiled
  const ol = $('orig-rule');
  ol.replaceChildren();
  const lim = d1 ? d1.limit : null;
  for (const id of ['k02_add_fwd.L1', 'k02_add_fwd.L2', 'k03_stencil.L1', 'k03_stencil.L2']) {
    const parts = good.map((c) => { const x = cellOf(pooledReal(c.cpu_model), id); return x ? [c.cpu_short, x.as_compiled.ci95[1]] : null; }).filter(Boolean);
    if (!parts.length || lim == null) continue;
    const miss = parts.filter((q) => q[1] >= lim), pass = parts.filter((q) => q[1] < lim);
    ol.append(el('li', null, el('b', null, `${cellName(id).replace(/^the /, '').replace(/^./, (ch) => ch.toUpperCase())}: `),
      miss.length ? `misses on ${joinAnd(miss.map((q) => `${q[0]} (upper end ${q[1].toFixed(3)})`))}` : '',
      miss.length && pass.length ? '; ' : '',
      pass.length ? `passes on ${joinAnd(pass.map((q) => `${q[0]} (${q[1].toFixed(3)})`))}` : '', '.'));
  }
  $('cmd-measure').textContent = ix.repo.measure_command;
  $('cmd-check').textContent = ix.repo.check_command;
  const few = pg.cpus_few;
  $('cpu-few').textContent = !S.fixture && few.length ? `Not shown: ${joinAnd(few.map((f) => `${f.cpu_short}, drawn in ${f.jobs} job${f.jobs > 1 ? 's' : ''}`))}, too few to judge.` : '';
}
let REAL_POOLED = null;
function dflt0() { return S.ix.cpus.find((c) => c.slug === S.ix.default_cpu); }
function pooledReal(model) { return REAL_POOLED && REAL_POOLED.cpus.find((c) => c.cpu_model === model); }

async function fillK02Pass() { // section 3 and Figure 3: per-pass counts of the forward add loop, aligned builds
  const c = S.ix.cpus.find((x) => x.slug === S.ix.default_cpu);
  let off = null, on = null;
  try {
    const b = S.builds[c.asm.builds] || (S.builds[c.asm.builds] = await getJSON(c.asm.builds));
    const kb = b.kernels.k02_add_fwd || {};
    off = perPass((kb.none_a64 || kb.none || {}).remarks);
    on = perPass((kb.fast_a64 || kb.fast || {}).remarks);
  } catch (err) { /* left as n/a; the check flags it */ }
  setV('k02PerPassOff', off == null ? 'n/a' : String(off));
  setV('k02PerPassOn', on == null ? 'n/a' : String(on));
}

/* ---------- section 1 and 3 tables ---------- */
function patternWords(c) {
  if (!c.enough) return `too few jobs (${c.jobs}; ${S.ix.criteria.minimum_jobs} needed)`;
  const held = c.form === 'map' ? 'held' : c.form === 'holds_everywhere' ? 'small cost everywhere' : 'inconclusive';
  return c.stability === 'stable' ? `${held}, the same in every run` : `${held} pooled; too few jobs per run to compare runs`;
}
function renderCpuTable() {
  const tb = $('cpu-table').querySelector('tbody');
  tb.replaceChildren();
  for (const c of S.ix.cpus) {
    const name = c.enough
      ? el('button', { type: 'button', class: 'linkbtn', onclick: () => { selectCpu(c.slug); $('figures').scrollIntoView({ behavior: smooth() }); } }, c.cpu_short)
      : c.cpu_short;
    tb.append(el('tr', { class: c.enough ? null : 'muted-row' },
      el('th', { scope: 'row' }, name),
      el('td', { class: 'num' }, `${c.jobs} in ${c.runs} run${c.runs > 1 ? 's' : ''}`),
      el('td', { class: 'num' }, c.enough ? rng(c.lost_aligned) : '–'),
      el('td', { class: 'num' }, c.enough ? rng(c.lost_compiled) : '–'),
      el('td', { class: 'num' }, c.enough ? rng(c.forward_judged_aligned) : '–'),
      el('td', null, !c.enough ? '–' : c.placement_sensitive.length
        ? c.placement_sensitive.map((q) => `${SHORT_NAMES[q.cell_id.split('.')[0]] || q.cell_id.split('.')[0]} ${q.cell_id.split('.')[1]}: ${fx(q.aligned_ratio)}×`).join('; ') : 'none'),
      el('td', null, patternWords(c))));
  }
}
function renderPsTable() {
  const tb = $('ps-table').querySelector('tbody');
  tb.replaceChildren();
  const rows = [];
  for (const c of S.ix.cpus.filter((x) => x.enough)) for (const p of c.placement_sensitive) rows.push([p, c]);
  rows.sort((a, b) => a[0].cell_id.localeCompare(b[0].cell_id));
  let last = null;
  for (const [p, c] of rows) {
    const [k, sz] = p.cell_id.split('.');
    const first = p.cell_id !== last;
    last = p.cell_id;
    tb.append(el('tr', { class: first ? 'grp' : null },
      el('th', { scope: 'row' }, first ? `${KERNEL_NAMES[k] || k}, ${sz}` : ''),
      el('td', null, c.cpu_short),
      el('td', { class: 'num' }, `${fx(p.ratio)}×`), el('td', { class: 'num' }, `${fx(p.aligned_ratio)}×`),
      el('td', { class: 'num' }, `${p.d.toFixed(3)} [${p.d_ci95[0].toFixed(3)}, ${p.d_ci95[1].toFixed(3)}]`)));
  }
}
function renderProgTable() {
  const tb = $('prog-table').querySelector('tbody');
  tb.replaceChildren();
  for (const r of S.ix.programs.rows) {
    const p = r.programs;
    const cell = (q, k) => (q ? `${pct(q[k])}%` : 'n/a');
    tb.append(el('tr', null,
      el('td', null, `${r.run_label}, ${r.job}`), el('td', null, r.cpu_short),
      el('td', { class: 'num' }, cell(p.json, 'at_most_pct')), el('td', { class: 'num muted' }, cell(p.json, 'aa_pct')),
      el('td', { class: 'num' }, cell(p.fmt, 'at_most_pct')), el('td', { class: 'num muted' }, cell(p.fmt, 'aa_pct'))));
  }
}
function renderMini() {
  const box = $('mini');
  box.replaceChildren();
  for (const c of S.ix.cpus.filter((x) => x.enough)) {
    const cell = cellOf(pooledReal(c.cpu_model), 'k02_add_fwd.L1');
    if (!cell) continue;
    const tr = el('div', { class: 'track' }, el('span', { class: 'one', style: `left:${pos(1).p}%` }));
    const draw = (col, cls) => {
      const a = pos(col.ci95[0]), b = pos(col.ci95[1]), m = pos(col.ratio);
      tr.append(el('span', { class: 'rng', style: `left:${a.p}%;width:${Math.max(0, b.p - a.p)}%;top:50%` }));
      tr.append(el('span', { class: `mk ${cls}`, style: `left:${m.p}%;top:50%` }));
    };
    draw(cell.as_compiled, 'ac');
    if (cell.aligned) draw(cell.aligned, 'al');
    box.append(el('div', { class: 'mrow' }, el('span', null, c.cpu_short), tr,
      el('span', { class: 'val' }, `${fx(cell.as_compiled.ratio)}× → ${cell.aligned ? `${fx(cell.aligned.ratio)}×` : 'n/a'}`)));
  }
  axisInto($('mini-axis'));
}
function renderAppB() {
  const tb = $('appb').querySelector('tbody');
  tb.replaceChildren();
  for (const r of S.ix.pooled.runs) {
    let first = true;
    for (const c of S.ix.cpus) {
      const pr = c.per_run.find((x) => x.run_id === r.run_id);
      if (!pr) continue;
      tb.append(el('tr', { class: first ? 'grp' : null },
        el('td', null, first ? (r.workflow_run_url ? el('a', { href: r.workflow_run_url }, `run ${r.run_id}`) : `run ${r.run_id}`) : ''),
        el('td', null, c.cpu_short), el('td', { class: 'num' }, String(pr.jobs)),
        el('td', null, pr.form === 'map' ? 'held' : pr.form ? pr.form : `too few jobs in this run alone (${S.ix.criteria.minimum_jobs} needed)`)));
      first = false;
    }
  }
  const tc = $('appb-cpu').querySelector('tbody');
  tc.replaceChildren();
  const lim = 2, lo = 1.5, minJ = S.ix.criteria.minimum_jobs;
  for (const c of S.ix.cpus) {
    const form = !c.enough ? 'inconclusive' : c.form === 'map' ? 'map (the pattern held)' : c.form === 'inconclusive' ? 'inconclusive' : 'small cost everywhere';
    const rule = !c.enough
      ? `Fewer than ${minJ} jobs pooled, so no verdict is drawn.`
      : c.form === 'map'
        ? `Every judged forward loop sits at most ${lim}% above 1× (aligned, interval included), and every loop that loses SIMD has its whole interval above ${lo}× in both columns.${c.placement_sensitive.length ? ` ${c.placement_sensitive.length} placement-sensitive cell${c.placement_sensitive.length > 1 ? 's' : ''} listed, not judged.` : ''}`
        : 'At least one condition of the pattern failed; see the pooled file.';
    tc.append(el('tr', { class: c.enough ? null : 'muted-row' },
      el('th', { scope: 'row' }, c.cpu_short), el('td', { class: 'num' }, String(c.jobs)), el('td', null, form),
      el('td', { class: 'num' }, c.n ? `${fx(c.n.median)}× (${rangeX(c.n.min, c.n.max)})` : '–'),
      el('td', { class: 'num' }, c.x_pct != null ? `${c.x_pct.toFixed(2)}% above 1×` : '–'),
      el('td', null, rule)));
  }
}
function renderAppA() {
  const cpu = currentCpu();
  $('appa-cpu').textContent = cpu.cpu_short;
  const pc = pooledOf(cpu.cpu_model);
  const t = $('appa');
  t.querySelector('thead').replaceChildren(el('tr', null, ...['Cell', 'SIMD', 'As compiled', 'Aligned', 'Instr. ratio', 'Jobs', 'Spread between jobs']
    .map((h, i) => el('th', { scope: 'col', class: i >= 2 ? 'num' : null }, h))));
  const tb = t.querySelector('tbody');
  tb.replaceChildren();
  const iv = (c) => (c ? `${c.ratio.toFixed(3)} [${c.ci95[0].toFixed(3)}, ${c.ci95[1].toFixed(3)}]` : 'n/a');
  const ps = new Set(((pc && pc.verdict.placement_sensitive) || []).map((p) => p.cell_id));
  let n = 0;
  for (const k of Object.keys(S.ix.criteria.kernels)) for (const sz of IN_CACHE) {
    const id = `${k}.${sz}`;
    const c = cellOf(pc, id);
    if (!c) { tb.append(el('tr', null, el('th', { scope: 'row' }, code(id)), el('td', { colspan: 6, class: 'muted' }, 'not measured'))); continue; }
    n++;
    const sd = c.aligned && c.aligned.between_job_sd_pct != null ? `${c.aligned.between_job_sd_pct.toFixed(2)}%` : '–';
    const ins = c.aligned_instr && c.aligned_instr.ratio != null ? c.aligned_instr.ratio.toFixed(3) : c.instr && c.instr.ratio != null ? c.instr.ratio.toFixed(3) : 'not counted';
    tb.append(el('tr', null, el('th', { scope: 'row' }, code(id), ps.has(id) ? el('span', { class: 'ps-tag' }, ' placement-sensitive') : null),
      el('td', null, ROLE_WORDS[role(c)]),
      el('td', { class: 'num' }, iv(c.as_compiled)), el('td', { class: 'num' }, iv(c.aligned)),
      el('td', { class: 'num' }, ins), el('td', { class: 'num' }, String((c.aligned || c.as_compiled).jobs)), el('td', { class: 'num' }, sd)));
  }
  $('appa-count').textContent = `${n} cells, pooled over ${pc ? pc.jobs : 0} job${pc && pc.jobs > 1 ? 's' : ''}`;
  updateScrollHints();
}
function updateScrollHints() { // the 'swipe sideways' lines show only while a table is wider than its box
  for (const [wrap, hint] of [['appa-wrap', 'appa-hint'], ['sib-wrap', 'sib-hint']]) {
    const w = $(wrap);
    if (!w) continue;
    const over = w.scrollWidth > w.clientWidth + 1;
    if ($(hint)) $(hint).hidden = !over;
    w.classList.toggle('overflowing', over);
    w.classList.toggle('at-end', w.scrollLeft + w.clientWidth >= w.scrollWidth - 2);
  }
  for (const w of document.querySelectorAll('.tablewrap:not(#appa-wrap):not(#sib-wrap)')) {
    let h = w.previousElementSibling;
    if (!h || !h.classList.contains('swipe')) {
      h = el('p', { class: 'scroll-hint swipe', 'aria-hidden': 'true' }, 'Swipe the table sideways');
      w.before(h);
      w.addEventListener('scroll', updateScrollHints, { passive: true });
    }
    const over = w.offsetParent !== null && w.scrollWidth > w.clientWidth + 1;
    h.hidden = !over;
    w.classList.toggle('overflowing', over);
    w.classList.toggle('at-end', w.scrollLeft + w.clientWidth >= w.scrollWidth - 2);
  }
}
/* The clause that keeps the lost-SIMD explanation in proportion: the NOVEC build (vectorization switched off by hand,
   no checks, pooled, L1, as compiled) against the checked build's extra time. Empty when the data has no such control.
   Mirrored in scripts/build_site_data.py (heroWhat); check_site.py compares the two. */
function novecClause(k, pc, brief) {
  const pos = pc && pc.positive && pc.positive[`${k}.L1`];
  const cell = cellOf(pc, `${k}.L1`);
  if (!pos || !cell || !cell.as_compiled || !(cell.as_compiled.ratio > 1)) return '';
  const share = 100 * (pos.ratio - 1) / (cell.as_compiled.ratio - 1);
  const w = share >= 30 && share <= 37 ? 'about a third' : `about ${Math.round(share)}%`;
  if (brief) return ` Switching SIMD off by hand costs ${fx(pos.ratio)}× (${w} of the as-compiled extra); the rest is the compare and jump (inferred).`; // the hero's caption has room for one clause
  return ` Vectorization switched off by hand, with no checks, makes it ${fx(pos.ratio)}× as long at the L1 size: ${w} of the extra time as compiled. The rest is presumably the compare and jump on every element (inferred).`;
}
function fillCpuProse() { // section 2's footnote, from the selected CPU model's pooled numbers
  const cpu = currentCpu();
  const pc = pooledReal(cpu.cpu_model) || pooledReal(S.ix.cpus.find((c) => c.slug === S.ix.default_cpu).cpu_model);
  const pos_ = pc && pc.positive && pc.positive['k04_rev.L1'];
  const rev = cellOf(pc, 'k04_rev.L1');
  setV('novecRev', pos_ ? fx(pos_.ratio) : 'n/a');
  setV('fastRev', rev ? fx(rev.as_compiled.ratio) : 'n/a');
  setV('novecCpu', pc ? cpuShortOf(pc.cpu_model) : 'n/a');
  const ce = S.ix.cpus.find((c) => pc && c.cpu_model === pc.cpu_model);
  setV('novecShare', ce && ce.novec_rev_share_pct != null ? ce.novec_rev_share_pct.toFixed(0) : 'n/a');
  setV('novecRest', ce && ce.novec_rest_pct != null ? ce.novec_rest_pct.toFixed(1) : 'n/a');
}

/* ---------- Figure 1 ---------- */
function rowData() {
  const pc = pooledOf(currentCpu().cpu_model);
  const ps = new Set(((pc && pc.verdict.placement_sensitive) || []).map((p) => p.cell_id));
  const out = [];
  for (const k of Object.keys(S.ix.criteria.kernels)) {
    const pts = [];
    let r = null;
    for (const sz of IN_CACHE) {
      const cell = cellOf(pc, `${k}.${sz}`);
      if (!cell) continue;
      if (!r) r = role(cell);
      const col = column(cell);
      if (!col) continue;
      pts.push({ sz, ratio: col.ratio, ci: col.ci95, jobs: col.jobs, perJob: col.per_job || [], ps: ps.has(cell.cell_id) });
    }
    const rs = pts.map((p) => p.ratio).sort((a, b) => a - b);
    const med = rs.length ? (rs.length % 2 ? rs[(rs.length - 1) / 2] : (rs[rs.length / 2 - 1] + rs[rs.length / 2]) / 2) : -1;
    out.push({ k, role: r || 'none', pts, med, lo: rs[0], hi: rs[rs.length - 1], ps: pts.filter((p) => p.ps).map((p) => p.sz) });
  }
  if (!S.order) { // sorted once, on the default CPU model's aligned ratios; never re-sorted on a switch
    const ref = S.fixture ? pc : (pooledReal(dflt0().cpu_model) || pc);
    const med = (k) => { const xs = IN_CACHE.map((sz) => cellOf(ref, `${k}.${sz}`)).filter((c) => c && (c.aligned || c.as_compiled)).map((c) => (c.aligned || c.as_compiled).ratio).sort((a, b) => a - b); return xs.length ? (xs.length % 2 ? xs[(xs.length - 1) / 2] : (xs[xs.length / 2 - 1] + xs[xs.length / 2]) / 2) : -1; };
    S.order = Object.keys(S.ix.criteria.kernels).sort((a, b) => med(b) - med(a));
  }
  out.sort((a, b) => S.order.indexOf(a.k) - S.order.indexOf(b.k));
  return out;
}
function aaHalfWidth() { // the selected model's byte-identical A/A, pooled: the timing noise floor
  const pc = pooledOf(currentCpu().cpu_model);
  return pc && pc.aa && pc.aa.half_width_pct != null ? pc.aa.half_width_pct : null;
}
function aaBand(hw) { // drawn at least 5 px wide so a band of a tenth of a percent stays visible
  const a = pos(1 - hw / 100).p, b = pos(1 + hw / 100).p;
  return el('span', { class: 'aa-band', style: `left:calc(${(a + b) / 2}% - max(2.5px, ${(b - a) / 2}%));width:max(5px, ${b - a}%)`, title: `A/A: ±${hw.toFixed(2)}%` });
}
function jobsLine(r) { // the drawer's per-job strip (phones show the per-job marks only here)
  if (!r.pts.some((p) => p.perJob.length)) return null;
  const hw = aaHalfWidth();
  return el('div', { class: 'f2-jobs' }, el('p', { class: 'f2-jobs-t' }, `Every job’s own ratio (ticks) and the pooled ratio (dark bar), ${S.col === 'aligned' ? 'aligned' : 'as compiled'}${hw != null ? `; the faint band at 1× is this model’s A/A half-width, ±${hw.toFixed(2)}%` : ''}:`),
    ...r.pts.filter((p) => p.perJob.length).map((p) => {
      const tr = el('div', { class: 'track' });
      for (const t of TICKS) tr.append(el('span', { class: t === 1 ? 'one' : 'gl', style: `left:${pos(t).p}%` }));
      if (hw != null) tr.append(aaBand(hw));
      for (const v of p.perJob) tr.append(el('span', { class: `jt jt-big ${p.sz.toLowerCase()}`, style: `left:${pos(v).p}%;top:50%` }));
      tr.append(el('span', { class: 'f2-pool', style: `left:${pos(p.ratio).p}%`, title: `pooled ${fx(p.ratio)}×` }));
      return el('div', { class: 'f2-jrow' }, el('span', { class: 'f2-jlab' }, `${p.sz}, ${p.perJob.length} jobs`), tr,
        el('span', { class: 'f2-jval' }, rangeX(Math.min(...p.perJob), Math.max(...p.perJob))),
        el('span', { class: 'f2-pooled' }, `Pooled ${fx(p.ratio)}× (95% interval ${fx(p.ci[0])} to ${fx(p.ci[1])}).`));
    }));
}
function renderFig1() {
  const box = $('rows');
  const rows = rowData();
  S.rows = rows;
  if (!S.sel || !rows.some((r) => r.k === S.sel)) S.sel = (rows.find((r) => r.k === 'k04_rev') || rows[0]).k;
  const before = new Map();
  for (const [k, n] of S.rowEls) if (n.isConnected) before.set(k, n.getBoundingClientRect().top);
  const frag = [];
  for (const r of rows) {
    let b = S.rowEls.get(r.k);
    if (!b) {
      b = el('button', { type: 'button', class: 'row', role: 'option', 'data-k': r.k });
      b.addEventListener('click', () => {
        if (matchMedia(NARROW).matches && S.sel === r.k && $('fig2').classList.contains('open') && $('fig2').parentElement === $('rows')) { closeInlineFig2(true); return; } // a second tap folds the panel
        clearTimeout(S.pvT); S.pv = null; // a click pins this row: no pending preview of another may overwrite it
        $('fig2').classList.add('open'); select(r.k, true, true); showFig2IfBelow();
      });
      b.addEventListener('pointerenter', (e) => { // a mouse over a row previews its machine code in the side panel; a click pins it
        if (e.pointerType !== 'mouse' || matchMedia(NARROW).matches) return;
        clearTimeout(S.pvT);
        S.pvT = setTimeout(() => { if (S.pv !== r.k) { S.pv = r.k; renderFig2(); } }, 90);
      });
      S.rowEls.set(r.k, b);
    }
    b.className = `row c-${r.role}`;
    const src = S.ix.kernel_source && S.ix.kernel_source[r.k];
    const track = el('div', { class: 'track' });
    for (const t of TICKS) track.append(el('span', { class: t === 1 ? 'one' : 'gl', style: `left:${pos(t).p}%` }));
    const aaHw = aaHalfWidth();
    if (aaHw != null) track.append(aaBand(aaHw));
    for (const p of r.pts) {
      const y = `calc(50% ${p.sz === 'L1' ? '-' : '+'} 5px)`; // L1 lane above, L2 lane below
      for (const v of p.perJob) track.append(el('span', { class: `jt ${p.sz.toLowerCase()}`, style: `left:${pos(v).p}%;top:${y}` }));
      const a = pos(p.ci[0]), c = pos(p.ci[1]), m = pos(p.ratio);
      track.append(el('span', { class: `wh${a.clipL ? ' clip-l' : ''}${c.clipR ? ' clip-r' : ''}`, style: `left:${a.p}%;width:${Math.max(0, c.p - a.p)}%;top:${y}` }));
      track.append(el('span', { class: `mk ${p.sz.toLowerCase()}${p.ps ? ' ps' : ''}`, style: `left:${m.p}%;top:${y}` }));
      const hit = el('span', { class: 'mk-hit', style: `left:${m.p}%;top:${y}` });
      hit.addEventListener('mouseenter', (e) => showTip(e, p, r));
      hit.addEventListener('mousemove', moveTip);
      hit.addEventListener('mouseleave', hideTip);
      track.append(hit);
    }
    const val = r.pts.length ? el('span', { class: 'val' }, rangeX(r.lo, r.hi)) : el('span', { class: 'val na' }, 'not measured');
    b.replaceChildren(
      el('span', { class: 'lab' }, el('span', { class: 'name' }, el('i', { 'aria-hidden': 'true' }), KERNEL_NAMES[r.k] || r.k,
        r.ps.length ? el('span', { class: 'ps-mark', title: `placement-sensitive at ${r.ps.join(' and ')}`, 'aria-label': `placement-sensitive at ${r.ps.join(' and ')}` }, '‡') : null),
        src ? el('code', { class: 'src', text: srcLine(src.text) }) : null),
      track, val);
    b.setAttribute('aria-label', `${KERNEL_NAMES[r.k] || r.k}, ${ROLE_WORDS[r.role]}, ${r.pts.length ? rangeX(r.lo, r.hi) + ' as long with checks on' : 'not measured'}`);
    frag.push(b);
  }
  const f2 = $('fig2'), wasInline = f2.parentElement === box;
  if (wasInline) $('figures').append(f2);
  box.replaceChildren(...frag);
  if (wasInline && matchMedia(NARROW).matches) placeFig2Inline();
  markSelected();
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    for (const [k, n] of S.rowEls) {
      if (!before.has(k)) continue;
      const d = before.get(k) - n.getBoundingClientRect().top;
      if (Math.abs(d) < 1) continue;
      n.classList.remove('moving');
      n.style.transform = `translateY(${d}px)`;
      requestAnimationFrame(() => requestAnimationFrame(() => { n.classList.add('moving'); n.style.transform = ''; }));
    }
  }
  axisInto($('axis'), 'time with checks on ÷ without, log scale');
  const cpu = currentCpu();
  const pc = pooledOf(cpu.cpu_model);
  const jobs = pc ? pc.jobs : 0;
  const open = $('fig1-cap').querySelector('details') ? $('fig1-cap').querySelector('details').open : false;
  $('fig1-cap').replaceChildren(el('b', null, 'Figure 1.'),
    ` How much longer each loop takes with libc++’s checks on, on ${cpu.cpu_short}${S.fixture ? ' (SAMPLE DATA)' : ''}, ${S.col === 'aligned' ? 'every hot loop aligned' : 'as compiled'}, data in cache. `,
    el('span', { class: 'key key-fill', 'aria-hidden': 'true' }), ' Filled dot: data sized to fit L1. ',
    el('span', { class: 'key key-open', 'aria-hidden': 'true' }), ' Hollow ring: sized to fit L2. Colour: ',
    el('span', { class: 'key key-lost', 'aria-hidden': 'true' }), ' loses SIMD under the check, ',
    el('span', { class: 'key key-kept', 'aria-hidden': 'true' }), ' keeps SIMD, ',
    el('span', { class: 'key key-none', 'aria-hidden': 'true' }), ' no SIMD in either build. Select a row to see its machine code.',
    el('details', { class: 'cap-more', open: open || null }, el('summary', null, 'How to read the marks'),
      `Rows keep one order, by cost on ${S.fixture ? 'the first model' : `${dflt0().cpu_short}, aligned`}. `,
      jobs > 1 ? `Each mark is the pooled ratio of ${jobs} jobs in ${pc.runs.length} run${pc.runs.length > 1 ? 's' : ''}; ` : 'One job, so each mark is that job’s ratio; ',
      'the thin lines are 95% intervals that include the spread between jobs, often narrower than the mark. ',
      el('span', { class: 'key key-jt', 'aria-hidden': 'true' }), ' Tiny ticks above the L1 dot and below the L2 ring: each job’s own ratio. ',
      ...(aaHalfWidth() != null ? [el('span', { class: 'key key-aa', 'aria-hidden': 'true' }), ` Faint band at 1×: this model’s A/A half-width (±${aaHalfWidth().toFixed(2)}%, a binary timed against a byte-identical copy), drawn at least 5 px wide. `] : []),
      '‡ and a dashed ring mark a placement-sensitive cell, where code placement and not the check moves the ratio (section 3). ',
      el('span', { class: 'tnote-i' }, `Jobs: the pooled runs, ${S.ix.pooled.jobs} jobs, sizes L1 and L2.`)));
}
function markSelected() {
  const narrow = matchMedia(NARROW).matches, box = $('rows'), open = $('fig2').classList.contains('open');
  // wide: one listbox, the panel beside it. narrow: an accordion, the panel opens directly under the tapped row
  if (narrow) { box.setAttribute('role', 'group'); box.setAttribute('aria-label', 'Loop shapes, in a fixed order. Select one to open its machine code under it.'); }
  else { box.setAttribute('role', 'listbox'); box.setAttribute('aria-label', 'Loop shapes, in a fixed order. Use the arrow keys to select one.'); }
  for (const [k, n] of S.rowEls) {
    const on = k === S.sel;
    if (narrow) {
      n.setAttribute('role', 'button'); n.removeAttribute('aria-selected');
      n.setAttribute('aria-expanded', on && open && $('fig2').parentElement === box ? 'true' : 'false');
      n.setAttribute('aria-controls', 'fig2');
      n.setAttribute('aria-pressed', on ? 'true' : 'false');
    } else {
      n.setAttribute('role', 'option'); n.removeAttribute('aria-expanded'); n.removeAttribute('aria-controls'); n.removeAttribute('aria-pressed');
      n.setAttribute('aria-selected', on ? 'true' : 'false');
    }
    n.tabIndex = on ? 0 : -1;
  }
}
function placeFig2Inline() { // narrow screens: the machine code sits directly under the selected row
  const row = S.rowEls.get(S.sel), f2 = $('fig2');
  if (!row || !row.isConnected) return;
  row.after(f2);
  markSelected();
}
function closeInlineFig2(focusRow) {
  const f2 = $('fig2');
  f2.classList.remove('open');
  if (f2.parentElement === $('rows')) $('figures').append(f2);
  markSelected();
  const b = S.rowEls.get(S.sel); if (b && focusRow) b.focus({ preventScroll: true });
}
const NARROW = '(max-width: 1040px)'; // Figure 2 sits under Figure 1 at this width (style.css)
const smooth = () => (matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth');
function showFig2IfBelow() { // a tap on a loop on a narrow screen opens its machine code directly under the row
  if (!matchMedia(NARROW).matches) return;
  placeFig2Inline();
  const row = S.rowEls.get(S.sel);
  if (row) row.scrollIntoView({ behavior: smooth(), block: 'start' });
}
function select(k, focus, pointer) {
  if (S.sel === k) { if (focus) S.rowEls.get(k).focus({ preventScroll: !!pointer }); return; }
  hashLive = true;
  S.sel = k;
  markSelected();
  if (matchMedia(NARROW).matches && $('fig2').parentElement === $('rows')) placeFig2Inline();
  if (focus) S.rowEls.get(k).focus({ preventScroll: !!pointer });
  writeHash();
  renderFig2();
}
function onRowsKey(e) {
  const keys = ['ArrowDown', 'ArrowUp', 'Home', 'End'];
  if (!keys.includes(e.key) || !S.rows || !e.target.closest || !e.target.closest('.row')) return;
  e.preventDefault();
  const order = S.rows.map((r) => r.k);
  let i = order.indexOf(S.sel);
  if (e.key === 'ArrowDown') i = Math.min(order.length - 1, i + 1);
  if (e.key === 'ArrowUp') i = Math.max(0, i - 1);
  if (e.key === 'Home') i = 0;
  if (e.key === 'End') i = order.length - 1;
  select(order[i], true);
}

/* tooltip */
function showTipNodes(e, nodes) {
  const t = $('tip');
  t.replaceChildren(...nodes);
  t.hidden = false;
  moveTip(e);
}
function showTip(e, p, r) {
  showTipNodes(e, [el('b', null, `${KERNEL_NAMES[r.k]}, ${p.sz}`), el('br'),
    `${fx(p.ratio)}× (95%: ${fx(p.ci[0])} to ${fx(p.ci[1])})`, el('br'),
    `pooled, ${p.jobs} job${p.jobs > 1 ? 's' : ''}, ${S.col === 'aligned' ? 'aligned' : 'as compiled'}${p.ps ? ', placement-sensitive' : ''}`]);
}
function moveTip(e) {
  const t = $('tip');
  const w = t.offsetWidth, h = t.offsetHeight;
  let x = e.clientX + 14, y = e.clientY - h - 10;
  if (x + w > innerWidth - 8) x = e.clientX - w - 14;
  if (y < 8) y = e.clientY + 16;
  t.style.left = `${Math.max(8, x)}px`;
  t.style.top = `${y}px`;
}
function hideTip() { $('tip').hidden = true; }

/* ---------- Figure 2: the machine code ---------- */
function parseListing(text) {
  const out = [];
  for (const line of text.split('\n')) {
    const m = line.match(/^\s*([0-9a-f]+):\s+(.*)$/);
    if (!m) continue;
    const ins = m[2].replace(/\s*<[^>]*>/, '').trim();
    const parts = ins.split(/\s+/);
    const mnem = parts[0];
    const ops = ins.slice(mnem.length).trim();
    const tm = /^j[a-z]*$/.test(mnem) && ops.match(/^([0-9a-f]+)$/);
    out.push({
      addr: parseInt(m[1], 16), hex: m[1], mnem, ops, target: tm ? parseInt(tm[1], 16) : null,
      simd: /%[xy]mm/.test(ins), pad: /^(nop|data16|xchg|cs)/.test(mnem) && !/ud2/.test(ins), trap: mnem === 'ud2',
    });
  }
  return out;
}
function analyse(lines) {
  const loops = [];
  for (const l of lines) if (l.target != null && l.target <= l.addr) loops.push({ start: l.target, end: l.addr });
  const inner = loops.filter((a) => !loops.some((b) => b !== a && b.start >= a.start && b.end <= a.end && (b.end - b.start) < (a.end - a.start)));
  const inLoop = (L) => lines.filter((x) => x.addr >= L.start && x.addr <= L.end);
  for (const L of inner) { const ls = inLoop(L); L.n = ls.length; L.simd = ls.some((x) => x.simd); }
  const simdInner = inner.filter((L) => L.simd).sort((a, b) => b.n - a.n);
  const hot = simdInner[0] || inner.slice().sort((a, b) => b.n - a.n)[0] || null;
  const traps = new Set(lines.filter((x) => x.trap).map((x) => x.addr));
  const checks = [];
  lines.forEach((x, i) => {
    if (x.target == null || !traps.has(x.target)) return;
    let j = i - 1;
    while (j >= 0 && lines[j].pad) j--;
    const pair = j >= 0 && /^(cmp|test)/.test(lines[j].mnem) ? [lines[j].addr, x.addr] : [x.addr];
    checks.push(pair);
  });
  return { lines, inner, hot, traps, checks };
}
function excerpt(an) {
  const keep = new Set();
  const addRange = (L) => { for (const x of an.lines) if (x.addr >= L.start && x.addr <= L.end) keep.add(x.addr); };
  if (an.hot) addRange(an.hot);
  for (const pair of an.checks) {
    for (const a of pair) keep.add(a);
    const L = an.inner.find((q) => pair[0] >= q.start && pair[pair.length - 1] <= q.end);
    if (L && L.n <= 16) addRange(L);
  }
  for (const a of an.traps) keep.add(a);
  return keep;
}
function sameCode(a, b) {
  if (a.length !== b.length) return false;
  return a.every((x, i) => x.mnem === b[i].mnem && x.ops === b[i].ops);
}
function plainRemark(remarks) {
  const rs = remarks || [];
  const vec = rs.map((r) => r.match(/vectorization width: (\d+), interleaved count: (\d+)/)).find(Boolean);
  if (vec) {
    const w = Number(vec[1]), n = Number(vec[2]);
    return `Vectorized: ${w} numbers per instruction${n > 1 ? `, ${w * n} per pass of the loop` : ''}.`;
  }
  if (rs.some((r) => r.includes('could not determine number of loop iterations'))) return 'Not vectorized: the compiler no longer knows how many times the loop runs, because the check may stop it early.';
  if (rs.some((r) => r.includes('vectorization is not beneficial'))) return 'Not vectorized: the compiler judged that SIMD would not pay off for this loop.';
  if (rs.length) return 'Not vectorized.';
  return 'The compiler made no remark about this loop.';
}
function whyLine(r, anOn, identical, bOn, width) {
  if (identical) return 'With the checks on, the compiler proved every index is in range and removed the check: both builds are the same machine code.';
  const hotHasCheck = anOn.hot && anOn.checks.some((p) => p[0] >= anOn.hot.start && p[p.length - 1] <= anOn.hot.end);
  const rs = (bOn && bOn.remarks) || [];
  const many = width ? `${width}-at-a-time` : 'SIMD';
  if (r.role === 'lost') {
    const nv = novecClause(r.k, pooledOf(currentCpu().cpu_model));
    if (rs.some((x) => x.includes('could not determine number of loop iterations')))
      return `The compiler could not vectorize this loop once the check was inside it: it no longer knows how many times the loop will run, because the check may stop it at any element. So the ${many} loop on the left becomes the one-at-a-time loop on the right.${nv}`;
    if (rs.some((x) => x.includes('vectorization is not beneficial')))
      return `With the checks inside the loop, the compiler judged that SIMD would no longer pay off, so the ${many} loop on the left becomes the one-at-a-time loop on the right, with a compare and a jump for every index it uses.${nv}`;
    return `With the checks on, the compiler did not vectorize this loop, so the ${many} loop on the left becomes the one-at-a-time loop on the right.${nv}`;
  }
  if (r.role === 'kept') return hotHasCheck
    ? 'Both builds are vectorized, and the check runs inside the SIMD loop.'
    : 'Both builds are vectorized. With the checks on, the compiler tests the sizes once before the SIMD loop and keeps the check out of it; the check only runs on the few elements left over at the end.';
  return 'Neither build is vectorized, so there is no SIMD to lose; the check adds a compare and a jump to every pass of the loop.';
}
function asmBlock(an, keep, opts) {
  const pre = el('pre', { class: 'asm' });
  const c = el('code');
  pre.append(c);
  let skipped = 0, simdNoted = false, checkNoted = 0;
  const checkEnds = new Set(an.checks.map((p) => p[p.length - 1]));
  const checkAddrs = new Set(an.checks.flat());
  const flush = () => { if (skipped) { c.append(el('span', { class: 'gap', text: `⋯ ${skipped} instruction${skipped > 1 ? 's' : ''} not shown` })); skipped = 0; } };
  const shown = an.lines.filter((x) => keep.has(x.addr) && !x.pad);
  const clsOf = (x) => (!x ? null : x.trap ? 'trap' : checkAddrs.has(x.addr) ? 'chk' : x.simd ? 'simd' : '');
  for (const x of an.lines) {
    if (!keep.has(x.addr)) { if (!x.pad) skipped++; continue; }
    if (x.pad) continue;
    flush();
    const cls = clsOf(x);
    const nx = shown[shown.indexOf(x) + 1];
    c.append(el('span', { class: `ln ${cls}` }, el('span', { class: 'ad', text: x.hex }), `${x.mnem.padEnd(7)} ${x.ops}`));
    if (cls === 'simd' && !simdNoted && clsOf(nx) !== 'simd') {
      simdNoted = true;
      c.append(el('span', { class: 'note', text: opts.width ? `SIMD: one instruction works on ${opts.width} numbers at once` : 'SIMD: one instruction, several numbers' }));
    }
    if (checkEnds.has(x.addr)) {
      c.append(el('span', { class: 'note', text: checkNoted === 0 ? 'the check: is the index still inside the vector? If not, jump to the trap' : 'another check' }));
      checkNoted++;
    }
    if (x.trap) c.append(el('span', { class: 'note', text: 'this trap stops the program (ud2, the instruction a failed check jumps to)' }));
  }
  flush();
  return pre;
}
function instrLine(r) { // Figure 2's small second mark: the Cachegrind instruction ratio, beside the time ratio
  const pc = pooledOf(currentCpu().cpu_model);
  const parts = [];
  for (const sz of IN_CACHE) {
    const c = cellOf(pc, `${r.k}.${sz}`);
    const ins = c && (S.col === 'aligned' ? c.aligned_instr : c.instr);
    if (ins && ins.ratio != null) parts.push(`${fx(ins.ratio)}× at ${sz}`);
  }
  if (!parts.length) return null;
  return el('p', { class: 'f2-instr' }, el('span', { class: 'instr-mk', 'aria-hidden': 'true' }),
    `Instructions executed, checks on ÷ off: ${joinAnd(parts)} `, el('em', null, '(instructions, not time; counted by Cachegrind, a tool that counts the instructions a program executes)'));
}
async function renderFig2() {
  const my = ++S.token;
  const body = $('fig2-body'), cap = $('fig2-cap');
  const shownK = S.pv && S.pv !== S.sel ? S.pv : S.sel;
  const r = (S.rows || []).find((q) => q.k === shownK);
  if (!r) { body.replaceChildren(); cap.replaceChildren(); return; }
  const cpu = currentCpu();
  const pc = pooledOf(cpu.cpu_model);
  const cell = cellOf(pc, `${r.k}.L1`) || cellOf(pc, `${r.k}.L2`);
  const src = S.ix.kernel_source && S.ix.kernel_source[r.k];
  const back = () => {
    if ($('fig2').parentElement === $('rows')) { const b0 = S.rowEls.get(S.sel); closeInlineFig2(true); if (b0) b0.scrollIntoView({ behavior: smooth(), block: 'center' }); return; }
    $('fig1').scrollIntoView({ behavior: smooth(), block: 'start' });
    const b = S.rowEls.get(S.sel); if (b) b.focus({ preventScroll: true });
  };
  const head = [
    el('div', { class: 'f2-sticky' }, el('span', { class: 'f2-sticky-name' }, KERNEL_NAMES[r.k]),
      el('button', { type: 'button', class: 'back-up', onclick: back }, '↑ Back to the eight loops')),
    shownK !== S.sel ? el('p', { class: 'f2-pv' }, 'Preview. Click the row to pin it.') : null,
    el('h3', { class: 'f2-head' }, `${KERNEL_NAMES[r.k]} `, el('span', { class: 'f2-ratio' }, r.pts.length ? `${rangeX(r.lo, r.hi)} as long with checks on, ${cpu.cpu_short}` : 'not measured')),
    instrLine(r),
    jobsLine(r),
    src ? el('p', { class: 'f2-src' }, code(srcLine(src.text))) : null,
  ].filter(Boolean);
  const aligned = S.col === 'aligned' && cell && cell.aligned;
  const sfx = aligned ? '_a64' : '';
  const f = cpu.asm;
  if (!f) {
    body.replaceChildren(...head, el('p', { class: 'f2-why' }, 'The SAMPLE file carries no assembly, so there is no machine code to show.'));
    cap.replaceChildren(el('b', null, 'Figure 2.'), ' The machine code, unavailable for SAMPLE DATA.');
    return;
  }
  body.replaceChildren(...head, el('p', { class: 'f2-why muted' }, 'Loading the machine code…'));
  let builds, offTxt, onTxt;
  try {
    builds = S.builds[f.builds] || (S.builds[f.builds] = await getJSON(f.builds));
    [offTxt, onTxt] = await Promise.all([getText(`${f.dir}${r.k}.none${sfx}.s`), getText(`${f.dir}${r.k}.fast${sfx}.s`)]);
  } catch (err) {
    if (my !== S.token) return;
    body.replaceChildren(...head, el('p', { class: 'f2-why err' }, `The machine code did not load (${err.message}).`));
    return;
  }
  if (my !== S.token) return;
  const kb = builds.kernels[r.k] || {};
  const bOff = kb[`none${sfx}`] || {}, bOn = kb[`fast${sfx}`] || {};
  const anOff = analyse(parseListing(offTxt)), anOn = analyse(parseListing(onTxt));
  const identical = sameCode(anOff.lines, anOn.lines);
  const wOff = (bOff.remarks || []).map((x) => x.match(/vectorization width: (\d+)/)).find(Boolean);
  const wOn = (bOn.remarks || []).map((x) => x.match(/vectorization width: (\d+)/)).find(Boolean);
  const widthOff = wOff ? Number(wOff[1]) : null, widthOn = wOn ? Number(wOn[1]) : null;
  const colBox = (title, flag, b, an, width, extra) => el('div', { class: 'f2-col' },
    el('h3', null, title), el('code', { class: 'flag', text: flag }),
    el('p', { class: 'remark' }, extra || plainRemark(b.remarks)),
    asmBlock(an, excerpt(an), { width }));
  const noCheck = !anOn.traps.size ? (identical ? 'Same machine code as on the left; no check is left.' : 'No check instruction is left in this function.') : null;
  const pOff = perPass(bOff.remarks), pOn = perPass(bOn.remarks);
  const faster = aligned && r.role === 'kept' && r.pts.length && r.lo < 0.95 && pOff && pOn && pOff > pOn
    ? el('p', { class: 'f2-why f2-faster' }, `Here the checked build is the faster one (below 1×). The check itself does not speed anything up: without it clang unrolls this SIMD loop to ${pOff} numbers per pass, with it to ${pOn}, and the investigation found the unchecked loop forced down to ${pOn} per pass just as fast. So the shorter loop is simply quicker on this CPU model at this size; why is inferred, since these machines expose no hardware counters (`, el('a', { href: '#k02-faster' }, 'section 3'), ').')
    : null;
  body.replaceChildren(...head,
    el('p', { class: 'f2-why' }, whyLine(r, anOn, identical, bOn, widthOff),
      !aligned && r.role === 'kept' && r.hi > 1.1 ? [' As compiled, this loop looks expensive; switch to aligned loops and most of it goes away: ', el('a', { href: '#placement' }, 'section 3'), ' explains why.'] : null),
    ...(faster ? [faster] : []),
    el('div', { class: 'f2-cols' },
      colBox('Checks off', '_LIBCPP_HARDENING_MODE_NONE', bOff, anOff, widthOff),
      colBox('Checks on', '_LIBCPP_HARDENING_MODE_FAST', bOn, anOn, widthOn, noCheck ? `${plainRemark(bOn.remarks)} ${noCheck}` : null)),
    cmdBlock(`${bOff.command}\n${bOn.command}`, `The exact build commands${aligned ? ', loops aligned' : ''} (run ${f.run_id}, job ${f.job}):`));
  const hidden = (an) => { const k = excerpt(an); return an.lines.filter((x) => !x.pad && !k.has(x.addr)).length; };
  const anySimd = anOff.lines.some((x) => x.simd) || anOn.lines.some((x) => x.simd);
  cap.replaceChildren(...[el('b', null, 'Figure 2.'),
    ` The hot loop of the ${KERNEL_NAMES[r.k].toLowerCase()} as clang compiled it${aligned ? ' with loops aligned' : ''}, checks off and on. `,
    anySimd ? [el('span', { class: 'sw-simd', 'aria-hidden': 'true' }), ' SIMD instructions, which work on several elements at once. '] : null,
    anOn.traps.size ? [el('span', { class: 'sw-chk', 'aria-hidden': 'true' }), ' The check and the trap it jumps to. '] : null,
    `Grey numbers are addresses; ${hidden(anOff)} and ${hidden(anOn)} instructions of the two functions are left out. The binaries are the same in every job of ${cpu.cpu_short}; these are from run ${f.run_id}, job ${f.job}.`].flat().filter((x) => x != null));
}
function cmdBlock(text, label) {
  const id = `cmd-${Math.random().toString(36).slice(2, 8)}`;
  return el('div', { class: 'f2-cmd' }, el('span', { class: 'lbl' }, label),
    el('div', { class: 'cmdline' }, el('pre', null, el('code', { id, text })), el('button', { type: 'button', class: 'copy', 'data-copy': id }, 'Copy')));
}

/* ---------- section 4: the census ---------- */
const CS_MAX = 20; // percent, the right end of Figure 4's linear scale
function renderCensus() {
  const C = S.cor, t1 = C.census1.totals, t2 = C.census2.totals, wo = C.census2.without_biggest;
  const t1a = C.census1_avx2.totals, t2a = C.census2_avx2.totals;
  const big = C.census2.projects[0];
  const v = {
    corpusClang: `clang ${((C.census2.toolchain || '').match(/\d+\.\d+\.\d+/) || [''])[0]} with libc++`,
    c1Projects: String(t1.projects), c2Projects: String(t2.projects),
    c1Lost: num(t1.lost), c1Vec: num(t1.none.vectorized), c2Lost: num(t2.lost), c2Vec: num(t2.none.vectorized),
    c2Pct: t2.lost_pct_of_vectorized.toFixed(1), c2LostU: num(t2.lost_unique_locations), c2VecU: num(t2.none.vectorized_unique),
    bigName: PROJECT_NAMES[big.name] || big.name, bigLost: num(big.lost), bigLostU: num(big.lost_unique), bigShare: shareWords(big.lost / t2.lost),
    woLost: num(wo.lost), woVec: num(wo.vectorized), woPct: wo.lost_pct.toFixed(1), woLostU: num(wo.lost_unique),
    c2WithLost: String(t2.projects_with_a_lost_loop), c2Evidence: num(t2.lost_with_index_evidence), c2EvidenceU: num(C.census2.lost_unique_with_evidence),
    c2aLost: num(t2a.lost), c2aVec: num(t2a.none.vectorized), c2aLostU: num(t2a.lost_unique_locations),
    c1aLost: num(t1a.lost), c1aVec: num(t1a.none.vectorized), c1aProjects: String(t1a.projects),
    c1aDropped: joinAnd((C.census1_avx2.dropped || []).map((d) => d.name)) || 'none',
    c2Ud2: num(t2.ud2_added), c2Text: t2.text_bytes_change_pct.toFixed(2),
  };
  const pats = C.census2.patterns;
  v.shapeText = pats.map((p) => `${p.detail.replace(/\s*\(.*\)$/, '')} (${p.class}; ${num(p.count)} copies, ${num(p.unique_locations)} location${p.unique_locations > 1 ? 's' : ''})`).join('; ');
  {
    const cc2 = C.census2.controls, cc2a = C.census2_avx2.controls, cc1 = C.census1.controls, cc1a = C.census1_avx2.controls;
    const checks = [cc1.determinism.pass && cc2.determinism.pass && cc2a.determinism.pass && cc1a.determinism.pass, cc2.kernels.pass, cc2a.kernels.pass, cc2.kernels.index_evidence_pass, cc2.remark_crosscheck.pass];
    const nFail = checks.filter((b) => !b).length;
    v.censusCtlSum = nFail
      ? `${checks.length - nFail} of ${checks.length} controls passed. ${cc2a.kernels.pass ? 'One control' : 'The AVX2 kernel control (the same kernels built for AVX2, a newer x86-64 instruction set with wider SIMD)'} failed as registered${cc2a.kernels.pass ? '' : ': with AVX2, some kernel loops the rule expected to lose SIMD keep it, and the rule was not changed afterwards'}.`
      : `All ${checks.length} controls passed.`;
  }
  const un = C.census2.patterns_unlabelled;
  v.shapeRest = un && un.count > 0
    ? `the remaining ${num(un.count)} copies (${num(un.unique_locations)} locations) of the ${num(t2.lost)} carry no shape label in the census data, so the shapes add up to the total`
    : 'together these add up to the total';
  for (const [k, val] of Object.entries(v)) setV(k, val);
  // Figure 4
  const scale = $('c-scale');
  scale.replaceChildren(...[0, 5, 10, 15, 20].map((t) => el('span', { class: 'tick', style: `left:${(t / CS_MAX) * 100}%`, text: `${t}%` })));
  const box = $('census-rows');
  box.replaceChildren();
  let lastCensus = null;
  for (const r of C.categories) {
    if (r.census === 0) continue;
    if (PAGE !== 'details' && r.census === 1 && !r.total) continue; // census 1 by category: details page
    if (r.census !== lastCensus) {
      box.append(el('div', { class: 'c-grp' }, r.census === 1 ? `Census 1: ${r.census === 1 ? t1.projects : ''} general libraries` : `Census 2: ${t2.projects} numeric projects, chosen before compiling`));
      lastCensus = r.census;
    }
    const pRaw = r.vectorized ? (100 * r.lost) / r.vectorized : 0;
    const pU = r.vectorized_unique ? (100 * r.lost_unique) / r.vectorized_unique : 0;
    const tr = el('div', { class: 'c-track' });
    for (const t of [5, 10, 15]) tr.append(el('span', { class: 'gl', style: `left:${(t / CS_MAX) * 100}%` }));
    if (pU > 0 || pRaw > 0) tr.append(el('span', { class: 'c-link', style: `left:${(Math.min(pRaw, pU) / CS_MAX) * 100}%;width:${(Math.abs(pRaw - pU) / CS_MAX) * 100}%` }));
    tr.append(el('span', { class: 'c-mk raw', style: `left:${(Math.min(pRaw, CS_MAX) / CS_MAX) * 100}%` }));
    tr.append(el('span', { class: 'c-mk uniq', style: `left:${(Math.min(pU, CS_MAX) / CS_MAX) * 100}%` }));
    const hit = el('span', { class: 'c-hit' });
    const tipNodes = () => [el('b', null, `${r.category}${r.total ? '' : `, census ${r.census}`}`), el('br'),
      `${num(r.lost)} of ${num(r.vectorized)} loop copies lost (${r.lost_pct.toFixed(2)}%)`, el('br'),
      `${num(r.lost_unique)} of ${num(r.vectorized_unique)} distinct locations`, el('br'),
      `${r.projects_with_lost} of ${r.projects} project${r.projects > 1 ? 's' : ''} with a lost loop`];
    hit.addEventListener('mouseenter', (e) => showTipNodes(e, tipNodes()));
    hit.addEventListener('mousemove', moveTip);
    hit.addEventListener('mouseleave', hideTip);
    tr.append(hit);
    const key = `${r.census}|${r.category}`;
    const projs = PAGE !== 'details' ? null : r.total ? C.by_category && Object.entries(C.by_category).filter(([kk]) => kk.startsWith(`${r.census}|`)).flatMap(([, rows]) => rows).sort((a, b) => b.lost - a.lost || b.vectorized - a.vectorized)
      : C.by_category && C.by_category[key];
    const row = el('div', { class: `c-row${r.total ? ' c-total' : ''}${projs ? ' c-click' : ''}`, 'data-key': key },
      el('span', { class: 'c-name' }, projs ? el('span', { class: 'c-caret', 'aria-hidden': 'true' }, '▸') : null, r.total ? 'all' : r.category, el('span', { class: 'c-np' }, ` (${r.projects})`)),
      tr,
      el('span', { class: 'val' }, `${num(r.lost)} of ${num(r.vectorized)}`, el('span', { class: 'c-u' }, `${num(r.lost_unique)} of ${num(r.vectorized_unique)} locations`)));
    box.append(row);
    if (projs) {
      const panel = el('div', { class: 'c-panel', hidden: '' });
      row.setAttribute('role', 'button'); row.setAttribute('tabindex', '0'); row.setAttribute('aria-expanded', 'false');
      const toggle = () => {
        const open = panel.hidden;
        if (open && !panel.firstChild) {
          panel.append(el('table', { class: 'tbl dense c-ptbl' },
            el('caption', null, `${r.total ? `Census ${r.census}, every project` : r.category}: loops that lose SIMD under the check, per project.`),
            el('thead', null, el('tr', null, el('th', { scope: 'col' }, 'Project'), el('th', { scope: 'col', class: 'num' }, 'Lost of vectorized'), el('th', { scope: 'col', class: 'num' }, 'Distinct locations, lost of vectorized'))),
            el('tbody', null, ...projs.map((q) => el('tr', null, el('th', { scope: 'row' }, PROJECT_NAMES[q.project] || q.project),
              el('td', { class: 'num' }, `${num(q.lost)} of ${num(q.vectorized)}`), el('td', { class: 'num' }, `${num(q.lost_unique)} of ${num(q.vectorized_unique)}`))))));
        }
        panel.hidden = !open;
        row.setAttribute('aria-expanded', open ? 'true' : 'false');
        row.querySelector('.c-caret').textContent = open ? '▾' : '▸';
        row.classList.toggle('on', open);
      };
      row.addEventListener('click', toggle);
      row.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
      box.append(panel);
    }
  }
  // examples
  const ex = $('census-examples');
  ex.replaceChildren();
  for (const e of (PAGE === 'details' ? C.examples : C.examples.slice(0, 1))) {
    const [file, line] = e.where.split(/:(?=\d+$)/);
    const name = PROJECT_NAMES[e.project] || e.project;
    const ev = e.evidence.startsWith('checked') ? `a libc++ check traced inside the loop (${joinAnd(e.messages.map((m) => `“${m}”`))})` : 'no check traced to the loop itself (it may sit in a helper the loop calls)';
    ex.append(el('figure', { class: 'ex' },
      el('figcaption', null, el('b', null, name), ' ', code(`${file.split('/').pop()}:${line}`), el('span', { class: 'ex-meta' },
        ` ${e.count > 1 ? `${e.count} copies` : 'one copy'}; ${e.class === 'other' ? e.detail : `${e.class}, ${e.detail}`}; ${ev}.`)),
      el('pre', { class: 'ex-src' }, el('code', { text: e.context.map((l) => l.replace(/^\s{0,8}/, '')).join('\n') }))));
  }
  // controls
  const ul = $('census-controls');
  ul.replaceChildren();
  const ok = (b) => el('span', { class: `pf ${b ? 'pass' : 'fail'}` }, b ? 'PASS' : 'FAIL');
  const c2 = C.census2.controls, c2a = C.census2_avx2.controls, c1 = C.census1.controls, c1a = C.census1_avx2.controls;
  const miss = c2a.kernels.misses.map((m) => `${SHORT_NAMES[m.kernel] || m.kernel} was expected ${m.expected} but is vectorized in ${m.status === 'both' ? 'both builds' : m.status}`);
  ul.append(
    el('li', null, ok(c1.determinism.pass && c2.determinism.pass && c2a.determinism.pass && c1a.determinism.pass), ' Determinism: each census ran twice on separate machines with byte-identical outputs.'),
    el('li', null, ok(c2.kernels.pass), ` Kernel control, baseline: the pipeline marks exactly the ${joinAnd(c2.kernels.lost_kernels.map((k) => SHORT_NAMES[k]))} loops as lost, as timed in Figure 1.`),
    el('li', null, ok(c2a.kernels.pass), ` Kernel control, AVX2, as registered: ${joinAnd(miss)}, so the rule written before the run fails; it was not changed afterwards.`),
    el('li', null, ok(c2.kernels.index_evidence_pass), ' Evidence method: each lost kernel loop shows the libc++ check inside its loop line.'),
    el('li', null, ok(c2.remark_crosscheck.pass), ' Remark cross-check: the vectorized loops in the optimization records equal the compiler’s printed remarks, per project.'));
  // Appendix D
  const tb = $('appd').querySelector('tbody');
  tb.replaceChildren();
  for (const p of C.census2.projects) tb.append(el('tr', null, el('th', { scope: 'row' }, PROJECT_NAMES[p.name] || p.name), el('td', null, p.category),
    el('td', { class: 'num' }, num(p.vectorized)), el('td', { class: 'num' }, num(p.lost)), el('td', { class: 'num' }, num(p.lost_unique)),
    el('td', { class: 'num' }, p.lost_with_index_evidence != null ? num(p.lost_with_index_evidence) : '–'), el('td', { class: 'num' }, num(p.ud2_added)),
    el('td', { class: 'num' }, `${p.text_change_pct >= 0 ? '+' : ''}${p.text_change_pct.toFixed(2)}%`)));
}

/* ---------- section 5: what to change ---------- */
const OUTCOME = { trapped: 'stops', returned: 'runs through' };
function variantLabel(v) { return v.variant === 'orig' ? '' : v.what; }
function renderMitigate() {
  const M = S.mit;
  const tb = $('mit-table').querySelector('tbody');
  tb.replaceChildren();
  $('mit-cpus').textContent = `${M.job_count} jobs on ${joinAnd(M.cpus)}.`;
  for (const sh of M.shapes) {
    const orig = sh.variants.find((v) => v.variant === 'orig');
    const best = sh.variants.find((v) => v.variant === sh.recommended);
    const on = S.mitSel === sh.kernel;
    const tr = el('tr', { class: `mit-row${on ? ' on' : ''}`, tabindex: '0', role: 'button', 'aria-expanded': on ? 'true' : 'false', 'data-k': sh.kernel,
      onclick: () => selectMit(sh.kernel), onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectMit(sh.kernel); } } },
    el('th', { scope: 'row' }, el('span', { class: 'mit-caret', 'aria-hidden': 'true' }, on ? '▾' : '▸'), ` ${SHAPE_NAMES[sh.kernel]}`),
    el('td', { class: 'num lostc', 'data-l': 'Original' }, rng(orig.range)),
    el('td', { class: 'mit-what', 'data-l': 'Best safe rewrite' }, best.what, best.safety_claim === 'REQUIRE only' ? el('span', { class: 'note-s' }, ' (safety rests on one check)') : null),
    el('td', { class: 'num', 'data-l': 'Rewrite' }, rng(best.range)),
    el('td', { 'data-l': 'Short input' }, best.short_fast.map((o) => OUTCOME[o] || o).join(', ')));
    tb.append(tr);
  }
  renderMitDetail();
  const rt = M.shapes.find((s) => s.kernel === 'm04_rev').variants.find((v) => v.variant === 'rtransform');
  setV('rtRange', rt ? rangeX(rt.range.min, rt.range.max).replace('×', '') : 'n/a');
  setV('rtOutcome', rt ? (rt.short_fast.includes('returned') ? 'returned instead of stopping' : 'stopped') : 'n/a');
  setV('mitAa', M.aa_max_pct.toFixed(0));
  setV('mitUsable', String(M.usable_jobs));
  setV('mitJobs', String(M.job_count));
  setV('mitUsableCpus', joinAnd(M.usable_cpus));
  const rev = M.shapes.find((s) => s.kernel === 'm04_rev');
  // the CPU model where the recommended reverse rewrite stays furthest above 1x (mitigate/README.md, Surprises)
  const recRev = rev.variants.find((v) => v.variant === rev.recommended);
  const worst = Object.entries(recRev.per_cpu_range).sort((a, b) => b[1].both.max - a[1].both.max)[0][0];
  const r9 = rev.variants.filter((v) => ['pre', 'span', 'raw'].includes(v.variant)).map((v) => v.per_cpu_range[worst]).filter(Boolean);
  setV('mit9v45', worst);
  setV('mit9v45Range', r9.length ? rangeX(Math.min(...r9.map((x) => x.both.min)), Math.max(...r9.map((x) => x.both.max))).replace('×', '') : 'n/a');
  // the abstract's 'back to x to y times': the recommended rewrites of the reverse and matrix-multiply loops
  const fix = M.shapes.filter((s) => s.kernel === 'm04_rev' || s.kernel === 'm08_matmul').map((s) => s.variants.find((v) => v.variant === s.recommended).range);
  setV('fixMin', fx(Math.min(...fix.map((r) => r.min))));
  setV('fixMax', fx(Math.max(...fix.map((r) => r.max))));
}
function selectMit(k) {
  S.mitSel = k;
  for (const tr of $('mit-table').querySelectorAll('.mit-row')) {
    const on = tr.dataset.k === k;
    tr.classList.toggle('on', on);
    tr.setAttribute('aria-expanded', on ? 'true' : 'false');
    tr.querySelector('.mit-caret').textContent = on ? '▾' : '▸';
  }
  renderMitDetail();
}
const MDOM = [0.5, 10];
function mpos(v) { const t = (Math.log(v) - Math.log(MDOM[0])) / (Math.log(MDOM[1]) - Math.log(MDOM[0])); return Math.max(0, Math.min(1, t)) * 100; }
function renderMitDetail() {
  const M = S.mit;
  const sh = M.shapes.find((s) => s.kernel === S.mitSel);
  const box = $('mit-detail');
  if (!sh) { box.replaceChildren(); return; }
  const orig = sh.variants.find((v) => v.variant === 'orig');
  const best = sh.variants.find((v) => v.variant === sh.recommended);
  const list = el('div', { class: 'mv-list' });
  const ax = el('div', { class: 'mv-axis' }, el('span', null), el('span', { class: 'mv-ticks' }, ...[0.5, 1, 2, 4, 8].map((t) => el('span', { class: 'tick', style: `left:${mpos(t)}%`, text: `${t}×` }))), el('span', null));
  list.append(ax);
  const sorted = sh.variants.slice().sort((a, b) => (a.variant === 'orig' ? -1 : b.variant === 'orig' ? 1 : a.range.max - b.range.max));
  for (const v of sorted) {
    const tr = el('div', { class: 'mv-track' }, el('span', { class: 'one', style: `left:${mpos(1)}%` }));
    const lanes = M.cpus.filter((c) => v.per_cpu_range[c]);
    lanes.forEach((c, i) => {
      const r = v.per_cpu_range[c].both;
      const y = `calc(50% + ${(i - (lanes.length - 1) / 2) * 5}px)`;
      tr.append(el('span', { class: `mv-bar ${v.keeps_safety ? (v.variant === 'orig' ? 'orig' : 'safe') : 'unsafe'}`, style: `left:${mpos(r.min)}%;width:${Math.max(0.6, mpos(r.max) - mpos(r.min))}%;top:${y}`, title: `${c}: ${rangeX(r.min, r.max)}` }));
    });
    const per = el('span', { class: 'mv-per' }, ...M.cpus.map((c) => {
      const r = v.per_cpu_range[c];
      return el('span', null, `${c.replace('EPYC ', '')}: ${r ? `${rangeX(r.both.min, r.both.max)} (${r.jobs} job${r.jobs > 1 ? 's' : ''})` : 'not run'}`);
    }));
    list.append(el('div', { class: `mv-row${v.variant === sh.recommended ? ' best' : ''}${v.variant === 'orig' ? ' orig' : ''}` },
      el('span', { class: 'mv-name' }, el('b', null, v.variant === 'orig' ? 'Original' : v.variant === sh.recommended ? 'Best safe' : ''), v.variant === 'orig' || v.variant === sh.recommended ? ' ' : '', variantLabel(v),
        el('span', { class: `mv-safe ${v.keeps_safety ? 'ok' : 'bad'}` }, v.keeps_safety ? (v.safety_claim === 'REQUIRE only' ? ' safe through one check' : ' safe') : ' UNSAFE: the short input ran through')),
      tr, per));
  }
  const codeBox = (title, v) => el('div', { class: 'mc' }, el('div', { class: 'mc-h' }, title), el('pre', { class: 'mc-src' }, el('code', { text: v.code.join('\n') })));
  box.replaceChildren(
    el('h3', { class: 'mit-h' }, `${SHAPE_NAMES[sh.kernel]}: every rewrite tried`),
    el('p', { class: 'small' }, `Checks on, time ÷ the original without checks, aligned. Each bar is one CPU model’s range over its jobs and both sizes (top to bottom: ${joinAnd(M.cpus)}). `,
      el('span', { class: 'key key-sq-safe', 'aria-hidden': 'true' }), ' keeps safety, ',
      el('span', { class: 'key key-sq-unsafe', 'aria-hidden': 'true' }), ' unsafe, ',
      el('span', { class: 'key key-sq-orig', 'aria-hidden': 'true' }), ' the original.'),
    list,
    el('div', { class: 'mc-pair' }, codeBox('Original', orig), codeBox(`Best safe rewrite: ${best.readability_cost}`, best)),
    el('p', { class: 'small' }, code('REQUIRE(x)'), ' is ', code('if (!(x)) __builtin_trap();'), ', the same trap instruction libc++ uses, kept in builds with checks off too. ',
      best.safety_claim === 'REQUIRE only' ? 'This rewrite uses raw pointers after that one check, so it is exactly as safe as that line is correct.' : 'libc++’s own checks still guard every access in this rewrite.'));
}

/* ---------- section 6: other toolchains ---------- */
const SIB_MAIN = ['k01_sum_fwd', 'k02_add_fwd', 'k03_stencil', 'k04_rev', 'k05_stride2', 'k06_gather', 'k07_hist', 'k08_matmul'];
function renderSiblings() {
  const B = S.sib;
  const t = $('sib-table');
  t.querySelector('thead').replaceChildren(el('tr', null, el('th', { scope: 'col' }, 'Setup'), ...SIB_MAIN.map((k) => el('th', { scope: 'col' }, SHORT_NAMES[k]))));
  const tb = t.querySelector('tbody');
  tb.replaceChildren();
  const TAG = { lost: 'lost', kept: 'kept', neither: 'none' };
  for (const r of B.rows) {
    tb.append(el('tr', { class: r.variant === 'clang18-fast' ? 'ref' : null }, el('th', { scope: 'row' }, r.label, r.note ? el('span', { class: 'sib-note' }, r.note) : null),
      ...SIB_MAIN.map((k) => {
        const c = r.cells[k];
        return el('td', { class: `sc s-${c.status}` }, el('span', { class: `tag t-${c.status}` }, TAG[c.status]), el('span', { class: 'sv' }, rng(c.range)));
      })));
  }
  const row = (v) => B.rows.find((r) => r.variant === v);
  const maxOf = (vs, ks) => Math.max(...vs.flatMap((v) => ks.map((k) => row(v).cells[k].range.max)));
  setV('sibMatmulMax', fx(maxOf(['clang20-fast', 'clang18v3-fast'], ['k08_matmul'])));
  setV('gccO2Max', fx(maxOf(['gcc14-O2-assert'], SIB_MAIN)));
  setV('c20MatmulMax', fx(maxOf(['clang20-fast'], ['k08_matmul'])));
  setV('avx2Exc', avx2Text());
  { const r_ = S.sib.rows.find((q) => q.variant === 'clang18v3-fast'); const pc_ = r_ && r_.cells.k02_add_fwd.per_cpu; const m_ = pc_ ? Math.max(...Object.entries(pc_).filter(([m]) => m.startsWith('EPYC')).map(([, v]) => v.L1.max)) : null; setV('avx2Short', m_ ? fx(m_) : 'n/a'); }
  const c18 = row('clang18-fast').cells.k02_add_fwd.per_cpu;
  const x69 = Object.entries(c18).find(([m]) => m.includes('6973P'));
  const v69 = x69 ? fx(x69[1].L1.max) : 'n/a';
  setV('sib6973', v69);
  const j69 = x69 ? x69[1].jobs : 0;
  setV('sib6973Jobs', `${j69} job${j69 === 1 ? '' : 's'}`);
  const IFc = S.ix.intel_forward && S.ix.intel_forward.jobs.length ? S.ix.intel_forward : null;
  const intelCounts = IFc ? joinAnd(IFc.cpus.map((c) => { const n = IFc.jobs.filter((j) => j.cpu_short === c).length; return `${c} in ${n} job${n === 1 ? '' : 's'}`; })) : '';
  setV('intelCounts', IFc ? `${IFc.cpus.length === 1 ? 'the one Intel model' : `the ${IFc.cpus.length} Intel models`} drawn (${intelCounts}; earlier runs, the S4 smoke run and the pooled runs)` : '');
  const IF = S.ix.intel_forward;
  setV('intelText', IF && IF.jobs.length
    ? `The forward loops are near 1× on the AMD models only (one exception: ${avx2Text()}). On ${IF.cpus.length === 1 ? 'the one Intel model' : `the ${IF.cpus.length} Intel models`} GitHub drew (${joinAnd(IF.cpus.map((c) => { const n = IF.jobs.filter((j) => j.cpu_short === c).length; return `${c} in ${n} job${n === 1 ? '' : 's'}`; }))}, too few for a verdict), the forward add at L1 cost ${rangeX(IF.aligned.min, IF.aligned.max)} aligned in every one of ${IF.jobs.length} jobs, in the earlier runs, the S4 smoke run and the pooled runs; the toolchain runs add a Xeon 6973P-C at ${v69}× in ${j69} job${j69 === 1 ? '' : 's'} (section 6).`
    : '');
  const o3 = row('gcc14-O3-assert').cells.k02_add_fwd.range;
  setV('gccO3AddMin', fx(o3.min)); setV('gccO3AddMax', fx(o3.max));
  setV('gccO3FwdMax', fx(maxOf(['gcc14-O3-assert'], ['k02_add_fwd', 'k03_stencil'])));
  setV('sibJobs', String(B.jobs)); setV('sibRuns', String(B.runs.length)); setV('sibExcluded', String(B.excluded));
  setV('sibThin', String(B.single_job_groups)); setV('sibGroups', String(B.groups));
  const norm = (m) => m.replace('Xeon Platinum ', 'Xeon ');
  const enoughNames = S.ix.cpus.filter((c) => c.enough).map((c) => c.cpu_short);
  const sibOther = B.cpus.map(norm).filter((m) => !enoughNames.includes(m));
  setV('sibExtraCpus', sibOther.length ? `which include ${joinAnd(sibOther)} beside the three EPYC models` : 'the same CPU models as Table 1');
  const progOther = [...new Set(S.ix.programs.rows.map((r) => norm(r.cpu_short)))].filter((m) => !enoughNames.includes(m) && !sibOther.includes(m));
  const pooledJobs = (m) => { const c = S.ix.cpus.find((x) => norm(x.cpu_short) === m); return c ? c.jobs : 0; };
  const all = [...sibOther, ...progOther];
  setV('otherDraws', all.length
    ? `Section 6 (Table 4, Appendix C) also uses ${joinAnd(sibOther)}${progOther.length ? `, and Table 8 uses ${joinAnd(progOther)}` : ''}. They have no row in Table 1 because each came up in fewer than the ${S.ix.criteria.minimum_jobs} pooled jobs a verdict needs (${all.map((m) => `${m}: ${pooledJobs(m) || 'none'}`).join('; ')}).`
    : '');
  // the five-row summary (main page): the three clang 18 libc++ modes share a row
  const GROUPS = [['Forward loops', ['k01_sum_fwd', 'k02_add_fwd', 'k03_stencil']], ['Reverse and stride-2', ['k04_rev', 'k05_stride2']],
    ['Matrix multiply', ['k08_matmul']], ['Gather and histogram', ['k06_gather', 'k07_hist']]];
  const SUMROWS = [['clang 18, libc++ FAST, EXTENSIVE or DEBUG', ['clang18-fast', 'clang18-extensive', 'clang18-debug']], ['clang 20, libc++ 20 FAST', ['clang20-fast']],
    ['clang 18, FAST, AVX2', ['clang18v3-fast']], ['GCC 14 -O2, assertions', ['gcc14-O2-assert']], ['GCC 14 -O3, assertions', ['gcc14-O3-assert']]];
  const st = $('sibsum-table');
  st.querySelector('thead').replaceChildren(el('tr', null, el('th', { scope: 'col' }, 'Setup'), ...GROUPS.map((g) => el('th', { scope: 'col' }, g[0]))));
  st.querySelector('tbody').replaceChildren(...SUMROWS.map(([label, vs]) => {
    const rs = vs.map(row).filter(Boolean);
    return el('tr', null, el('th', { scope: 'row' }, label), ...GROUPS.map(([, ks]) => {
      const cells = rs.flatMap((r) => ks.map((k) => [k, r.cells[k]]));
      const tags = [...new Set(cells.map(([, c]) => c.status))];
      const lo = Math.min(...cells.map(([, c]) => c.range.min)), hi = Math.max(...cells.map(([, c]) => c.range.max));
      const split = tags.length > 1 ? ` (${joinAnd(ks.filter((k) => rs.some((r) => r.cells[k].status !== tags[0])).map((k) => SHORT_NAMES[k]))} ${rs[0].cells[ks.find((k) => rs.some((r) => r.cells[k].status !== tags[0]))].status})` : '';
      return el('td', { class: 'sc' }, el('span', { class: `tag t-${tags[0]}` }, TAG[tags[0]]), split ? el('span', { class: 'sib-note' }, split.replace('neither', 'none')) : null, el('span', { class: 'sv' }, rangeX(lo, hi)));
    }));
  }));
  // Appendix C
  const ta = $('appc');
  ta.querySelector('thead').replaceChildren(el('tr', null, el('th', { scope: 'col' }, 'Setup'), el('th', { scope: 'col' }, 'Loop'), ...B.cpus.map((c) => el('th', { scope: 'col', class: 'num' }, c))));
  const tba = ta.querySelector('tbody');
  tba.replaceChildren();
  for (const r of B.rows) {
    let first = true;
    for (const k of B.kernels) {
      const c = r.cells[k];
      tba.append(el('tr', { class: first ? 'grp' : null }, el('th', { scope: 'row' }, first ? r.label : ''), el('td', null, SHORT_NAMES[k]),
        ...B.cpus.map((cpu) => {
          const p = c.per_cpu[cpu];
          return el('td', { class: 'num' }, p ? `${rng(p.L1)} / ${rng(p.L2)}, ${p.jobs} job${p.jobs > 1 ? 's' : ''}` : '–');
        })));
      first = false;
    }
  }
  updateScrollHints();
}

/* ---------- section 6: the compile-only sweep (ce-sweep/, no timing) ---------- */
const CE_ABBR = { k01_sum_fwd: 'sum', k02_add_fwd: 'add', k03_stencil: 'sten', k04_rev: 'rev', k05_stride2: 'strd', k06_gather: 'gath', k07_hist: 'hist', k08_matmul: 'mm' };
const CE_WORD = { lost: 'lost under the checks', kept: 'kept', none: 'not vectorized in either build' };
function ceState(v) { return v.none && !v.checked ? 'lost' : v.none && v.checked ? 'kept' : v.checked ? 'kept' : 'none'; }
function ceName(r) { return r.family === 'clang' ? `clang ${r.major || 'trunk'}` : `GCC ${r.major}`; }
function ceFull(r) { return r.family === 'clang' ? (r.version === 'trunk' ? 'clang trunk' : `clang ${r.version}`) : `GCC ${r.version}`; }
const ceOrder = (r) => (r.family === 'clang' ? 0 : 1000) + (r.major || 999);
const ceRemarkText = (r, k) => (r.remark[k] || '').replace(/^loop not vectorized: /, '');
function ceRanges(ms) { // [16,17,18] -> "16 to 18"
  const out = []; let a = null, b = null;
  const L = S.ce.summary.majors;
  for (const m of ms) {
    if (a != null && L.indexOf(m) === L.indexOf(b) + 1) { b = m; continue; }
    if (a != null) out.push([a, b]);
    a = b = m;
  }
  if (a != null) out.push([a, b]);
  return joinAnd(out.map(([x, y]) => (x === y ? String(x) : `${x} to ${y}`)));
}
function ceFindings() {
  const C = S.ce, R = C.rows, sm = C.summary, T = Object.keys(C.targets);
  const cl = R.filter((r) => r.family === 'clang'), gc = R.filter((r) => r.family === 'gcc');
  // matrix multiply per clang version: on which targets is it lost (any optimization level)?
  const vers = [...new Set(cl.map((r) => r.version))].sort((a, b) => ceOrder(cl.find((r) => r.version === a)) - ceOrder(cl.find((r) => r.version === b)));
  const mmSet = (v) => T.filter((t) => cl.some((r) => r.version === v && r.target === t && r.lost.includes('k08_matmul'))).join(',');
  const groups = [];
  for (const v of vers) {
    const set = mmSet(v), r0 = cl.find((r) => r.version === v);
    const g = groups[groups.length - 1];
    if (g && g.set === set) g.rows.push(r0); else groups.push({ set, rows: [r0] });
  }
  const label = (g) => {
    const ms = g.rows.filter((r) => r.major).map((r) => r.major), tr = g.rows.some((r) => !r.major);
    return `${ms.length ? ceRanges(ms) : ''}${tr ? (ms.length ? ' and trunk' : 'trunk') : ''}`;
  };
  const say = (g) => {
    if (!g.set) return `kept on ${label(g)} everywhere`;
    if (g.set === T.join(',')) return `lost everywhere on ${label(g)}`;
    const names = g.set.split(',').map((t) => (t === 'x86-64' ? 'baseline x86-64' : C.targets[t]));
    return `lost on clang ${label(g)} at ${joinAnd(names)} only`;
  };
  const trunk = cl.find((r) => r.version === 'trunk' && r.lost.includes('k08_matmul'));
  const armOnly = T.includes('aarch64') ? C.kernels.filter((k) => R.some((r) => r.target === 'aarch64' && r.lost.includes(k)
    && !R.some((q) => q.compiler_id !== r.compiler_id && q.family === r.family && q.major === r.major && q.opt === r.opt && q.target !== 'aarch64' && q.lost.includes(k)))) : [];
  const g3 = sm.gcc_o3_lost, n3 = sm.gcc_o3_rows;
  const every = C.kernels.filter((k) => g3[k] === n3);
  const addMiss = gc.filter((r) => r.opt === '-O3' && !r.lost.includes('k02_add_fwd'));
  const addMissMaj = [...new Set(addMiss.map((r) => r.major))];
  const addMissOff = addMiss.every((r) => !r.vec.k02_add_fwd.none);
  const gccO2Vec = gc.filter((r) => r.opt === '-O2').reduce((a, r) => a + C.kernels.filter((k) => r.vec[k].none).length, 0);
  const gccO2Cells = gc.filter((r) => r.opt === '-O2').length * C.kernels.length;
  const clv = [...new Set(cl.filter((r) => r.major).map((r) => r.major))];
  const short = `${sm.clang_rev_s2_lost === sm.clang_rows ? `all ${sm.clang_rows} clang rows lose the reverse and stride-2 loops` : `${sm.clang_rev_s2_lost} of ${sm.clang_rows} clang rows lose the reverse and stride-2 loops`}, and ${sm.clang_fwd_lost === 0 ? 'none loses a forward loop' : `${sm.clang_fwd_lost} lose a forward loop`}. Matrix multiply: ${groups.map(say).join(', ').replace(/^lost on clang /, 'lost on clang ')}. ${armOnly.length ? `Lost on AArch64 only: ${joinAnd(armOnly.map((k) => SHORT_NAMES[k]))}.` : 'No loop is lost on AArch64 only.'} GCC loses ${sm.gcc_o2_lost === 0 ? 'nothing' : sm.gcc_o2_lost} at -O2; at -O3 it loses the ${joinAnd(every.map((k) => SHORT_NAMES[k]))} loops in every version and the forward add in ${g3.k02_add_fwd} of ${n3} rows.`;
  return {
    short,
    matmul: groups.map(say).join('; '),
    clangRange: `clang ${ceRanges(clv)} and trunk`,
    revAll: sm.clang_rev_s2_lost === sm.clang_rows,
    text: `${sm.clang_rev_s2_lost === sm.clang_rows ? `The reverse and stride-2 loops lose vectorization under the checks in all ${sm.clang_rows} clang rows` : `The reverse and stride-2 loops lose vectorization under the checks in ${sm.clang_rev_s2_lost} of ${sm.clang_rows} clang rows`}, and ${sm.clang_fwd_lost === 0 ? 'no clang row loses a forward loop' : `${sm.clang_fwd_lost} clang rows lose a forward loop`}. `
      + `The matrix multiply depends on the version: ${groups.map(say).join('; ')}${trunk ? ` (“${ceRemarkText(trunk, 'k08_matmul')}”)` : ''}. `
      + `${armOnly.length ? `Lost on AArch64 only: ${joinAnd(armOnly.map((k) => SHORT_NAMES[k]))}.` : 'No loop is lost on AArch64 only.'} `
      + `GCC with assertions vectorizes ${gccO2Vec === 0 ? 'none of these loops' : `only ${gccO2Vec} of its ${gccO2Cells} loop builds`} at -O2 even with checks off, so ${sm.gcc_o2_lost === 0 ? 'nothing is lost' : `${sm.gcc_o2_lost} are lost`}; at -O3 it loses the ${joinAnd(every.map((k) => SHORT_NAMES[k]))} loops in every version, and the forward add too in ${g3.k02_add_fwd} of ${n3} rows`
      + `${addMiss.length && addMissOff ? ` (GCC ${joinAnd(addMissMaj.map(String))} does not vectorize it even with checks off)` : ''}.`,
  };
}
const ceTargets = () => ['x86-64', 'x86-64-v3', 'aarch64'].filter((t) => S.ce.targets[t]).concat(Object.keys(S.ce.targets).filter((t) => !['x86-64', 'x86-64-v3', 'aarch64'].includes(t)));
function cePanel(t) {
  const C = S.ce;
  const rows = C.rows.filter((r) => r.target === t && r.opt === S.ceO).sort((a, b) => ceOrder(a) - ceOrder(b));
  const grid = el('div', { class: 'ce-grid', role: 'grid', 'aria-label': `${C.targets[t]}, ${S.ceO}` });
  // a real grid: role=row wrappers (display: contents keeps the CSS grid layout) and one tab stop per grid; the arrow
  // keys move between the cells and the eight header links (roving tabindex), so a keyboard user passes the figure in one Tab
  const stops = []; // stops[row][col]: the focusable element at that place (row 0 = the header links)
  const hrow = el('div', { class: 'ce-row', role: 'row' }, el('span', { class: 'ce-corner', role: 'columnheader', 'aria-label': 'Compiler and version' }));
  stops.push(C.kernels.map((k) => {
    const a = el('a', { class: 'ce-h', href: C.links[k], target: '_blank', rel: 'noopener', tabindex: '-1', title: `${SHORT_NAMES[k]}: open this loop in Compiler Explorer (clang 18, checks off and on)`, 'aria-label': `${SHORT_NAMES[k]}: open this loop in Compiler Explorer` }, CE_ABBR[k]);
    hrow.append(el('span', { role: 'columnheader', class: 'ce-ch' }, a));
    return a;
  }));
  grid.append(hrow);
  let prev = null;
  for (const r of rows) {
    const gap = prev && prev !== r.family;
    prev = r.family;
    const row = el('div', { class: 'ce-row', role: 'row' }, el('span', { class: `ce-rl${gap ? ' ce-gap' : ''}`, role: 'rowheader' }, ceName(r)));
    const cellsOfRow = [];
    stops.push(cellsOfRow);
    grid.append(row);
    for (const k of C.kernels) {
      const st = ceState(r.vec[k]);
      const say = `${ceFull(r)}, ${C.targets[t]}, ${S.ceO}, ${SHORT_NAMES[k]}: ${CE_WORD[st]}`;
      const show = () => {
        for (const n of document.querySelectorAll('.ce-cell.on')) n.classList.remove('on');
        cell.classList.add('on');
        $('ce-remark').replaceChildren(el('b', null, `${say}. `), `Checks off: ${r.vec[k].none ? 'vectorized' : 'not vectorized'}; checks on: ${r.vec[k].checked ? 'vectorized' : 'not vectorized'}. Remark with checks on: “${ceRemarkText(r, k) || 'none'}”`);
      };
      const cell = el('span', { class: `ce-cell ce-${st}${gap ? ' ce-gap' : ''}`, role: 'gridcell', tabindex: '-1', 'aria-label': say, title: say, onmouseenter: show, onfocus: show, onclick: show });
      row.append(cell);
      cellsOfRow.push(cell);
    }
  }
  const at = (e) => { for (let i = 0; i < stops.length; i++) { const j = stops[i].indexOf(e); if (j >= 0) return [i, j]; } return null; };
  const rove = (e) => { for (const row of stops) for (const x of row) x.tabIndex = x === e ? 0 : -1; };
  if (stops[1]) rove(stops[1][0]);
  grid.addEventListener('focusin', (ev) => { if (at(ev.target)) rove(ev.target); });
  grid.addEventListener('click', (ev) => { const c = ev.target.closest('.ce-cell'); if (c) rove(c); });
  grid.addEventListener('keydown', (ev) => {
    const p = at(ev.target);
    if (!p || ev.altKey || ev.ctrlKey || ev.metaKey) return;
    let [i, j] = p;
    if (ev.key === 'ArrowRight') j = Math.min(stops[i].length - 1, j + 1);
    else if (ev.key === 'ArrowLeft') j = Math.max(0, j - 1);
    else if (ev.key === 'ArrowDown') i = Math.min(stops.length - 1, i + 1);
    else if (ev.key === 'ArrowUp') i = Math.max(0, i - 1);
    else if (ev.key === 'Home') j = 0;
    else if (ev.key === 'End') j = stops[i].length - 1;
    else return;
    ev.preventDefault();
    stops[i][j].focus();
  });
  const box = el('div', { class: 'ce-panel', 'data-t': t, hidden: false }, el('p', { class: 'ce-pt' }, C.targets[t]), grid);
  if (t !== S.ceT) box.classList.add('ce-off');
  return box;
}
function ceDraw() {
  const C = S.ce;
  $('ce-panels').replaceChildren(...ceTargets().map(cePanel));
  for (const b of $('ce-tseg').querySelectorAll('button')) { const on = b.dataset.t === S.ceT; b.setAttribute('aria-checked', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; }
  for (const b of $('ce-oseg').querySelectorAll('button')) { const on = b.dataset.o === S.ceO; b.setAttribute('aria-checked', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; }
}
/* ---------- layout sweep and PGO column (details page) ---------- */
const LAYOUT_WORD = { ROBUST: 'robust', MIXED: 'mixed', PLACEMENT_DEPENDENT: 'placement-dependent', HOLDS: 'cost holds', NOT_STABLE: 'not stable', INCONCLUSIVE: 'inconclusive', OFF_AXIS: 'off the axis' };
const lr = (v) => (v == null ? 'none' : v >= 2 ? v.toFixed(2) : v.toFixed(3));
function renderLayout() {
  const L = S.lay;
  if (!L || !L.cpus || !L.cpus.length) { $('layout-intro').replaceChildren('No layout sweep result is stored yet.'); return; }
  const good = L.cpus.filter((c) => c.enough), thin = L.cpus.filter((c) => !c.enough);
  const R = L.rules, res = L.residues;
  const jobsOf = (c) => `${c.jobs} job${c.jobs === 1 ? '' : 's'}`;
  setV('layoutIntro', `Every figure above times one placement of the hot loop: the one the compiler produced or the 64-byte aligned one. This sweep moves each kernel function by ${L.step_bytes} bytes at a time, ${L.placements} placements in all, so the hot loop starts at ${joinAnd(res.map(String))} bytes past a 64-byte boundary (a coarse sweep: the ${L.placements} placements the compiler can produce itself, not every placement). Four kernels (the forward sum, the forward add, the stencil and the reverse loop), sizes L1 and L2, ${R.reps_per_side} repetitions per side, pooled per CPU model like the main result. A forward cell passes at a placement when its pooled ratio is at most ${R.forward_point_max_ratio} and the upper end of its interval stays under ${1 + R.forward_ci_hi_floor_pct / 100} or ${R.forward_ci_hi_aa_multiplier} times that run’s own A/A half-width above 1, whichever is more; a cell is robust when all ${L.placements} placements pass and placement-dependent when at most ${R.dependent_max_pass} do. The rules were fixed before the run (an earlier attempt with 16 placements stopped at its probe step with no timing recorded, and the plan was amended to ${L.placements} placements before any timing existed). A CPU model needs ${R.min_jobs} jobs for a reading.`);
  const k = L.kernels || {};
  const rev = L.reverse;
  const dep = good.flatMap((c) => c.rows.filter((r) => r.verdict === 'PLACEMENT_DEPENDENT').map((r) => `${r.size} on ${c.cpu_short} (median ${lr(r.median)}, ${r.n_cost} of ${r.n_placements} placements cost, aligned ${lr(r.aligned)})`));
  const addRows = (pred) => good.filter((c) => c.rows.some((r) => r.kernel === 'k02_add_fwd' && r.size === 'L1' && pred(r))).map((c) => c.cpu_short);
  const swing = addRows((r) => r.verdict === 'MIXED' || r.verdict === 'PLACEMENT_DEPENDENT'), steady = addRows((r) => r.verdict === 'ROBUST');
  const add = good.flatMap((c) => c.rows.filter((r) => r.kernel === 'k02_add_fwd' && r.as_compiled != null && r.size === 'L1' && (r.verdict === 'MIXED' || r.verdict === 'PLACEMENT_DEPENDENT')).map((r) => `${c.cpu_short} ${lr(r.as_compiled)} as compiled, ${lr(r.aligned)} aligned`));
  setV('layoutFinding', `What it shows, on the CPU models with enough jobs (${joinAnd(good.map((c) => `${c.cpu_short}, ${jobsOf(c)}`))}): the reverse loop, which loses SIMD, stays ${rev ? rangeX(rev.min, rev.max) : 'none'} at every placement, so the loss itself does not depend on placement (the size of the cost does, within that range). The simple forward sum is robust (${k.k01_sum_fwd ? `${lr(k.k01_sum_fwd.min)} to ${lr(k.k01_sum_fwd.max)}` : 'none'} at every placement). The forward add swings with placement on ${joinAnd(swing)}, ${k.k02_add_fwd ? `${lr(k.k02_add_fwd.min)} to ${lr(k.k02_add_fwd.max)}` : 'none'} over the CPU models, and there its as-compiled placement is the slow one at L1 (${joinAnd(add)})${steady.length ? `; on ${joinAnd(steady)} it stays robust at L1 and does not cost` : ''}; the stencil is ${dep.length ? `placement-dependent at ${joinAnd(dep)}` : 'not placement-dependent here'}. So “forward loops stay near 1×” holds for the sum, and for the add and the stencil it depends on where the loop lands in memory.`);
  setV('layoutLimits', `Limits: ${L.placements} placements in steps of ${L.step_bytes} bytes (loop start at ${joinAnd(res.map(String))} modulo 64), not a full sweep; two sizes in cache; ${thin.map((c) => `${c.cpu_short} drew ${jobsOf(c)}, fewer than ${R.min_jobs}, so it is inconclusive`).join('; ')}${thin.length ? '; ' : ''}shared virtual machines; the hardware reason for any swing is inferred, not measured. Source: ${joinAnd(L.sources)}; rules: ${L.plan}.`);
  const box = $('layout-tables');
  box.replaceChildren();
  L.cpus.forEach((c, i) => {
    const claim = c.enough ? `forward claim ${LAYOUT_WORD[c.forward_claim] || c.forward_claim}; reverse control ${LAYOUT_WORD[c.lost_control] || c.lost_control}` : 'inconclusive (too few jobs)';
    box.append(
      el('p', { class: 'tcap' }, el('b', null, `Table L${i + 1}.`), ` ${c.cpu_short}, ${jobsOf(c)}: ${claim}. FAST ÷ NONE per loop and size: as compiled, aligned, then the minimum, median and maximum over the ${c.placements} placements, and how many placements pass the forward rule.`),
      el('div', { class: 'tablewrap boxed', tabindex: '0', role: 'region', 'aria-label': `Table L${i + 1}, scrolls sideways on a narrow screen` },
        el('table', { class: 'tbl dense' },
          el('thead', null, el('tr', null, ...['Loop', 'Size', 'As compiled', 'Aligned', 'Min', 'Median', 'Max', 'Pass', 'Verdict'].map((h, j) => el('th', { scope: 'col', class: j >= 2 && j <= 7 ? 'num' : null }, h)))),
          el('tbody', null, ...c.rows.map((r) => el('tr', null,
            el('th', { scope: 'row' }, r.name), el('td', null, r.size),
            el('td', { class: 'num' }, lr(r.as_compiled)), el('td', { class: 'num' }, lr(r.aligned)),
            el('td', { class: 'num' }, lr(r.min)), el('td', { class: 'num' }, lr(r.median)), el('td', { class: 'num' }, lr(r.max)),
            el('td', { class: 'num' }, r.class === 'kept' ? `${r.n_pass} of ${r.n_placements}` : 'loses SIMD, not judged'),
            el('td', null, LAYOUT_WORD[r.verdict] || r.verdict)))))));
  });
}
function renderPgo() {
  const P = S.pgo;
  if (!P || !P.cpus || !P.cpus.length) { $('pgo-intro').replaceChildren('No PGO result is stored yet.'); return; }
  const jobsOf = (c) => `${c.jobs} job${c.jobs === 1 ? '' : 's'}`;
  const main = P.cpus.filter((c) => c.enough && c.base_jobs >= P.minimum_jobs);
  const m = main[0];
  setV('pgoIntro', `The main timing of the real programs used no profile-guided optimization (PGO), and Google’s post says PGO helped. So all ${P.rows_built} rows (${P.programs_built} programs) were rebuilt twice, checks off and on, each with its own instrumented profile, then timed like the main study: ${P.jobs} jobs in ${P.runs.length} runs, pooled per CPU model, as compiled and aligned. A CPU model needs ${P.minimum_jobs} jobs for a reading.`);
  const slowRows = m ? m.rows.filter((r) => r.pgo.reading === 'detectably slower' && !/control/.test(r.name)) : [];
  const rs = slowRows.flatMap((r) => [r.pgo.fast.ratio, r.pgo.aligned.ratio]);
  const first = m ? m.rows.find((r) => r.row === 'lightgbm_default') : null;
  const cnt = (w) => (m ? m.rows.filter((r) => r.compare === w).length : 0);
  const vecN = P.builds.reduce((n, b) => n + b.vectorized_none, 0), vecF = P.builds.reduce((n, b) => n + b.vectorized_fast, 0), locs = P.builds.reduce((n, b) => n + b.locations, 0);
  const withB = (c) => `${c.cpu_short} (${jobsOf(c)} with PGO, ${c.base_jobs} without)`;
  const otherText = main.slice(1).map((o) => { const sl = o.rows.filter((r) => r.pgo.reading === 'detectably slower' && !/control/.test(r.name)); const ors = sl.flatMap((r) => [r.pgo.fast.ratio, r.pgo.aligned.ratio]); const oc = (w) => o.rows.filter((r) => r.compare === w).length; return ` On ${o.cpu_short}, ${sl.length} rows with lost loops are still detectably slower with the checks on${sl.length ? `, at ${lr(Math.min(...ors))} to ${lr(Math.max(...ors))}` : ''}; against the non-PGO ratios, PGO was lower in ${oc('PGO lower')} row${oc('PGO lower') === 1 ? '' : 's'}, higher in ${oc('PGO higher')} and not detectably different in ${oc('no difference detected')}.`; }).join('');
  setV('pgoFinding', m ? `${main.length === 1 ? `Only ${withB(m)} has` : `${joinAnd(main.map(withB))} have`} a reading on both sides. ${main.length === 1 ? 'There' : `On ${m.cpu_short}`}, PGO did not make the cost vanish: ${slowRows.length} rows with lost loops are still detectably slower with the checks on, at ${lr(Math.min(...rs))} to ${lr(Math.max(...rs))}${first ? `; only ${first.name} came to ${lr(first.pgo.fast.ratio)} as compiled (${first.pgo.reading === 'not detectable' ? `not detectable, at most ${pct(first.pgo.at_most_pct, 2)}%` : first.pgo.reading})` : ''}. Against the non-PGO ratios, PGO was lower in ${cnt('PGO lower')} row${cnt('PGO lower') === 1 ? '' : 's'}, higher in ${cnt('PGO higher')} and not detectably different in ${cnt('no difference detected')}.${otherText} PGO also left SIMD lost almost everywhere: of the ${locs} lost-loop locations listed for these programs, ${vecN} are vectorized in the PGO build without checks and ${vecF} with them.` : 'No CPU model has enough jobs on both sides for a reading.');
  const thin = P.cpus.filter((c) => !(c.enough && c.base_jobs >= P.minimum_jobs));
  setV('pgoLimits', `Limits: the training input is the timed input (same seeds, same sizes), which flatters PGO; clang’s instrumented profiles, not sampling profiles, no link-time optimization, one toolchain; ${thin.map((c) => `${c.cpu_short} has ${jobsOf(c)} with PGO and ${c.base_jobs ? `${c.base_jobs} without` : 'no non-PGO counterpart'}, so no comparison is read`).join('; ')}; PGO and non-PGO runs were not in the same jobs. Source: ${P.source}; baseline ${P.baseline}; rules ${P.plan}; report ${P.report}.`);
  setV('pgoBuilds', `PGO builds (check traps in the PGO builds, checks off and on; census lost-loop locations vectorized, checks off and on): ${P.builds.map((b) => `${b.program} ${b.traps_none} and ${b.traps_fast}; ${b.vectorized_none} and ${b.vectorized_fast} of ${b.locations}`).join('; ')}.`);
  const box = $('pgo-tables');
  box.replaceChildren();
  const cellT = (p) => (p ? el('td', { class: 'num' }, lr(p.ratio), el('span', { class: 'sib-note' }, `${lr(p.lo)} to ${lr(p.hi)}`)) : el('td', { class: 'num' }, 'not in pool'));
  const readT = (x) => (!x ? 'none' : x.reading === 'detectably slower' ? 'slower' : x.reading === 'detectably faster' ? 'faster' : x.reading === 'not detectable' ? `not detectable, at most ${pct(x.at_most_pct, 2)}%` : 'no reading');
  P.cpus.forEach((c, i) => {
    const note = c.enough ? '' : ` Too few jobs for a reading (minimum ${P.minimum_jobs}); the ratios are shown, not judged.`;
    box.append(
      el('p', { class: 'tcap' }, el('b', null, `Table P${i + 1}.`), ` ${c.cpu_short}: ${jobsOf(c)} with PGO, ${c.base_jobs ? `${c.base_jobs} without` : 'not in the non-PGO pool'}. FAST ÷ NONE per program, interval beneath, as compiled and aligned.${note}`),
      el('div', { class: 'tablewrap boxed', tabindex: '0', role: 'region', 'aria-label': `Table P${i + 1}, scrolls sideways on a narrow screen` },
        el('table', { class: 'tbl dense' },
          el('thead', null, el('tr', null, ...['Program', 'Without PGO, as compiled', 'Without PGO, aligned', 'PGO, as compiled', 'PGO, aligned', 'PGO reading', 'PGO against without'].map((h, j) => el('th', { scope: 'col', class: j >= 1 && j <= 4 ? 'num' : null }, h)))),
          el('tbody', null, ...c.rows.map((r) => el('tr', null,
            el('th', { scope: 'row' }, r.name), cellT(r.base && r.base.fast), cellT(r.base && r.base.aligned), cellT(r.pgo.fast), cellT(r.pgo.aligned),
            el('td', null, readT(r.pgo)), el('td', null, r.compare.replace(/^not compared \((.*)\)$/, 'not compared')))))))
    );
  });
}
/* ---------- newer toolchains (section 6b) and measurement environment (section 6c), details page ---------- */
const VER_CLASS = { lost: 'loses SIMD', kept: 'keeps SIMD', off_axis: 'off the axis' };
function verSpanOnCpu(V, cpu, kernel, size) { // the same cell on every toolchain for one CPU model
  const vs = V.toolchains.map((t) => { const c = t.cpus.find((x) => x.cpu_short === cpu); const x = c && c.cells.find((y) => y.kernel === kernel && y.size === size); return x ? x.ratio : null; }).filter((v) => v != null);
  return vs.length ? { min: Math.min(...vs), max: Math.max(...vs) } : null;
}
function renderVersions() {
  const V = S.ver;
  if (!V || !V.toolchains || !V.toolchains.length) { $('ver-intro').replaceChildren('No timed result for the newer toolchains is stored yet.'); return; }
  const T = V.toolchains, sm = V.summary, reps = S.ix.criteria.reps_per_side;
  const jobsOf = (n) => `${n} job${n === 1 ? '' : 's'}`;
  const enough = sm.enough;
  const mainCpu = enough.length ? enough[0].cpu_short : null;
  const mainJobs = joinAnd(enough.map((e) => String(e.jobs)));
  const thin = T.flatMap((t) => t.cpus.filter((c) => !c.enough).map((c) => c.jobs));
  const thinMin = Math.min(...thin), thinMax = Math.max(...thin);
  const tcName = (t) => `clang and libc++ ${t.clang}`;
  setV('verIntro', `The main study is clang ${S.ix.toolchain.clang.match(/\d+\.\d+\.\d+/)[0]} with Ubuntu’s libc++ 18, and section 6 timed other setups on few jobs. This column runs the main study’s harness unchanged on the same eight loops (as compiled and aligned, ${reps} processes a side, alternating order, one pinned CPU, in cache), under ${joinAnd(T.map(tcName))} from apt.llvm.org: ${sm.jobs} jobs in one run, ${sm.cpu_models} CPU models, ${T.length} toolchains. The rules were written before the run (${V.plan}). ${sm.all_probes_trap ? 'On every toolchain the checks trapped an out-of-range index in the probe, and a build without them ran clean.' : 'On some toolchain the probe did not trap; its rows are inconclusive.'} A loop holds when it loses SIMD and its interval’s lower end is at least ${fx(V.lost_lo)} in both columns at both sizes; a CPU model needs ${V.min_jobs} jobs on a toolchain for a verdict form.`);
  const rev7 = (s) => verSpanOnCpu(V, mainCpu, 'k04_rev', s), st7 = (s) => verSpanOnCpu(V, mainCpu, 'k05_stride2', s);
  const revR = { min: Math.min(...['L1', 'L2'].map((s) => rev7(s).min)), max: Math.max(...['L1', 'L2'].map((s) => rev7(s).max)) };
  const stR = { min: Math.min(...['L1', 'L2'].map((s) => st7(s).min)), max: Math.max(...['L1', 'L2'].map((s) => st7(s).max)) };
  const v21 = T[T.length - 1], c21 = mainCpu && v21.cpus.find((c) => c.cpu_short === mainCpu), r21 = c21 && c21.cells.find((x) => x.cell_id === 'k04_rev.L1');
  const first = T[0], c19 = mainCpu && first.cpus.find((c) => c.cpu_short === mainCpu), r19 = c19 && c19.cells.find((x) => x.cell_id === 'k04_rev.L1');
  setV('verFinding', `What held. The reverse loop and the stride-2 loop lose SIMD under the checks on ${sm.reverse_holds_all && sm.stride2_holds_all ? 'every toolchain and every CPU model that ran' : 'most rows'}, and the rule counts both as holding on all of them. Their cost, over every row and both sizes: reverse ${rangeX(sm.reverse_all.min, sm.reverse_all.max)}, stride-2 ${rangeX(sm.stride2_all.min, sm.stride2_all.max)}. ${mainCpu ? `On ${mainCpu}, the one model with enough jobs on each toolchain (${mainJobs} jobs): reverse ${rangeX(revR.min, revR.max)}, stride-2 ${rangeX(stR.min, stR.max)}.${r19 && r21 && Math.abs(r21.ratio - r19.ratio) > 0.5 ? ` The reverse loop is cheaper under ${v21.clang} (${fx(r21.ratio)}× at L1 against ${fx(r19.ratio)}× under ${first.clang}); it is still lost.` : ''}` : ''} The forward sum stays at ${rangeX(sm.sum_all.min, sm.sum_all.max)}.`);
  const m1 = sm.matmul_main.L1, m2 = sm.matmul_main.L2;
  const pcM = REAL_POOLED && mainCpu && REAL_POOLED.cpus.find((c) => cpuShortOf(c.cpu_model) === mainCpu);
  const c18 = ['L1', 'L2'].map((s) => cellOf(pcM, `k08_matmul.${s}`)), nv = ['L1', 'L2'].map((s) => pcM && pcM.positive && pcM.positive[`k08_matmul.${s}`]);
  const clang18Say = c18[0] && c18[1] && nv[0] && nv[1]
    ? ` On ${mainCpu} clang 18 costs ${fx(c18[0].as_compiled.ratio)}× at L1 and ${fx(c18[1].as_compiled.ratio)}× at L2 (pooled, ${c18[0].as_compiled.jobs} jobs), against ${fx(nv[0].ratio)}× and ${fx(nv[1].ratio)}× for the same loop built with no vectorization at all (the no-vectorize control), so only part of the clang 18 cost is the lost SIMD.` : '';
  const likeNoSimd = nv[0] && Math.abs(m1.max - nv[0].ratio) <= 0.05 ? ` (as slow as the no-vectorize build, ${fx(nv[0].ratio)}×)` : '';
  S.verMatmul = `What did not hold. Under clang 18 the checks make matrix multiply lose SIMD (its compiler remark says vectorizing is not beneficial with the checks inside), at ${rangeX(sm.matmul_clang18.min, sm.matmul_clang18.max)} on the same CPU models.${clang18Say} Clang 19 to 21 keep SIMD in both builds, so the rule written for this column counts it as not holding there; it is not free: on ${mainCpu || 'the CPU models with enough jobs'} the checks cost ${rangeX(m1.min, m1.max)} at L1${likeNoSimd} and ${rangeX(m2.min, m2.max)} at L2 on each of those toolchains; over all rows ${rangeX(sm.matmul.L1.min, sm.matmul.L1.max)} and ${rangeX(sm.matmul.L2.min, sm.matmul.L2.max)}. A plausible reason is that the inner loop is short and the checks add work around the vector body (inferred; versions/MATMUL-EXPLAINED.md). Why the vectorizer’s decision changed between clang 18 and 19 is not established: the change also appears on Compiler Explorer builds and with Ubuntu’s own clang 20 and libc++ 20, which narrows it but does not separate a compiler change from a library change.`;
  setV('verMatmul', S.verMatmul);
  setV('verForms', `Forms. Every toolchain is ${sm.forms.length === 1 ? sm.forms[0] : joinAnd(sm.forms)} under the written rule. ${mainCpu ? `${mainCpu} has ${mainJobs} jobs on clang ${T.map((t) => t.version).join(', ')} and is the only model with ${V.min_jobs} or more on each toolchain: the forward-loop rule is missed by matrix multiply, which costs more than the limit even aligned. ` : ''}Every other CPU model drew ${thinMin === thinMax ? jobsOf(thinMin) : `${thinMin} to ${thinMax} jobs`} on a toolchain, fewer than ${V.min_jobs}, so its rows are shown and no verdict is given. The page therefore reports rows, not a verdict per toolchain.`);
  setV('verLimits', `Limits: one run (${V.run_id}), so the run-to-run check that needs two runs was not possible; the 18 data are Ubuntu’s libc++ build and these are apt.llvm.org’s (Ubuntu’s own clang 20 gives the same matrix-multiply result as apt.llvm.org’s, so the package source is not what changed it; library and compiler are still not separated); the forward add’s large as-compiled cost under clang 18 on EPYC 7763 is not seen here (${fx(verSpanOnCpu(V, mainCpu, 'k02_add_fwd', 'L1').max)}× under every newer toolchain), the cause was not tested; the same eight loops, SSE2 baseline, no profile-guided optimization, no programs timed. Source: ${V.source}; report ${V.report}.`);
  const verRange = `${T[0].version} to ${T[T.length - 1].version}`;
  setV('verMain', `Timed too, clang and libc++ ${verRange}: the reverse and strided loops still lose SIMD; matrix multiply keeps SIMD there, though not for free, and the compile-only sweep loses it again on the newest compilers.`);
  setV('verCannot', `Clang and libc++ ${verRange} were timed on the eight loops only, with enough jobs on ${mainCpu ? `one CPU model (${mainCpu})` : 'no CPU model'}.`);
  setV('limVersions', `Clang and libc++ ${verRange} were timed on the eight loops only (section 6b): the reverse and stride-2 loops still lose SIMD, matrix multiply keeps SIMD there but is not free, and ${mainCpu ? `only ${mainCpu} has enough jobs on each toolchain` : 'no CPU model has enough jobs'}.`);
  const box = $('ver-tables');
  box.replaceChildren();
  T.forEach((t) => {
    const probe = t.probe_traps && t.probe_clean ? 'the checks trapped in the probe' : 'the probe did NOT trap: rows are inconclusive';
    box.append(el('h3', null, `clang and libc++ ${t.clang}: ${t.form}`),
      el('p', { class: 'small' }, `${jobsOf(t.jobs)} on ${t.cpus.length} CPU models; ${probe}; the compiler’s remarks say ${joinAnd(t.lost_by_remarks)} lose${t.lost_by_remarks.length === 1 ? 's' : ''} SIMD under the checks${t.matmul_vectorized_both ? ' and matrix multiply keeps it' : ''}.`));
    t.cpus.forEach((c, i) => {
      const kv = c.kernels.map((k) => `${k.name} ${k.holds ? 'holds' : 'does not hold'}`).join('; ');
      const hasBase = c.cells.some((x) => x.clang18 != null);
      const head = ['Loop', 'Size', 'Remarks say', 'As compiled', 'Aligned'].concat(hasBase ? ['clang 18, as compiled', 'Remarks under clang 18'] : []);
      const det = el('details', { class: 'more ver-cpu' },
        el('summary', null, `${c.cpu_short}, ${jobsOf(c.jobs)}: ${c.form}${c.why ? `, ${c.why}` : ''}`),
        el('p', { class: 'tcap' }, el('b', null, `Table V${t.version}.${i + 1}.`), ` ${c.cpu_short}, clang and libc++ ${t.clang}: ${kv}. A/A half-width ${pctS(c.aa_half_width_pct)}. FAST ÷ NONE per loop and size with the pooled 95% interval beneath; ${hasBase ? 'the clang 18 column is the same CPU model’s pooled result from the main study' : 'no clang 18 pool exists for this CPU model'}.`),
        el('div', { class: 'tablewrap boxed', tabindex: '0', role: 'region', 'aria-label': `Table V${t.version}.${i + 1}, scrolls sideways on a narrow screen` },
          el('table', { class: 'tbl dense' },
            el('thead', null, el('tr', null, ...head.map((h, j) => el('th', { scope: 'col', class: j >= 3 && j <= 5 ? 'num' : null }, h)))),
            el('tbody', null, ...c.cells.map((x) => el('tr', null,
              el('th', { scope: 'row' }, x.name), el('td', null, x.size), el('td', null, VER_CLASS[x.class] || x.class),
              el('td', { class: 'num' }, `${lr(x.ratio)} [${lr(x.lo)}, ${lr(x.hi)}]`), el('td', { class: 'num' }, `${lr(x.aligned)} [${lr(x.aligned_lo)}, ${lr(x.aligned_hi)}]`),
              hasBase ? el('td', { class: 'num' }, x.clang18 == null ? 'n/a' : lr(x.clang18)) : null,
              hasBase ? el('td', null, x.class18 ? VER_CLASS[x.class18] || x.class18 : 'n/a') : null))))));
      if (c.enough) det.open = false;
      box.append(det);
    });
  });
}
function renderEnvironment() {
  const E = S.env;
  if (!E || !E.models || !E.models.length) { $('env-intro').replaceChildren('No environment record is stored yet.'); return; }
  const sm = E.summary, M = E.models;
  const jobsOf = (n) => `${n} job${n === 1 ? '' : 's'}`;
  const mhz = M.flatMap((m) => m.jobs.map((j) => j.mhz_median));
  const per = M.map((m) => { const v = m.jobs.map((j) => j.mhz_median); return Math.min(...v) === Math.max(...v) ? `${Math.round(v[0])}` : `${Math.round(Math.min(...v))} to ${Math.round(Math.max(...v))}`; });
  setV('envIntro', `The harness pins one vCPU and times each pair in alternating order, but nothing recorded what the machine did meanwhile. This run times the eight loops (clang 18, as compiled, ${sm.reps_per_side} processes a side, both sizes) on ${sm.jobs} jobs (${joinAnd(M.map((m) => `${m.cpu_short}: ${jobsOf(m.n_jobs)}`))}) and records, for every timed process, the pinned vCPU’s steal time, its reported CPU MHz and the vCPU the Python driver was on, and, for every job, the topology, the kernel, the online CPUs, any cgroup CPU limit and any cpufreq files. The rules for “large” were written before the run (${E.plan}). Source: ${E.source}; report ${E.report}.`);
  setV('envFinding', `Steal: ${sm.processes_with_steal} of ${num(sm.processes)} timed processes saw a steal tick on the pinned vCPU, so the steal share was ${pctS(sm.steal_max_pct)} everywhere (large: above ${pctS(E.steal_large_pct)}). Frequency: the reported MHz drifted at most ${pctS(sm.half_drift_max_pct)} between the first and second half of a job and at most ${pctS(sm.side_drift_max_pct)} between the checks-off and checks-on processes (large: above ${pctS(E.drift_large_pct)}). Jobs with a large finding: ${sm.large_jobs}. Exclusion test: each model’s pooled FAST ÷ NONE per cell was recomputed without steal-affected processes; ${sm.excluded_processes} processes were left out, so no cell moved (${sm.cells_moved} of ${M.reduce((a, m) => a + m.cells, 0)}). That test could not have moved anything here, because no process had steal. The page’s verdict text therefore did not change.`);
  setV('envTopo', `Topology. The pinned vCPU has a hyperthread sibling, and the driver (the Python process that starts each timed run) was seen on that sibling after at least one process in ${sm.jobs_sharing_core} of ${sm.jobs} jobs; it was seen on the pinned vCPU itself in ${sm.jobs_driver_on_pinned}. The driver starts a run and waits for it to end, so it is not working while a loop is timed; what a shared core can matter for is anything else running on the sibling, for example the runner’s own services, and this run did not record that. It is a real feature of this setup, not something removed. Alternating the order of the two builds should give both the same neighbours on average, so it should largely cancel in an A/A and in a ratio; this run does not measure how much noise it adds or whether it cancels fully. No cgroup CPU limit was present (${sm.jobs_cgroup} jobs), and every job was a virtual machine with ${(() => { const m = /^(\d+)-(\d+)$/.exec(sm.online[0] || ''); return sm.online.length === 1 && m ? `${+m[2] - +m[1] + 1} vCPUs` : 'CPUs'; })()} (online list ${joinAnd(sm.online)}) on kernel ${joinAnd(sm.kernels)}.`);
  setV('envLimits', `Limits: the guest’s view only. A virtual machine may report a constant or nominal MHz and hide real frequency changes; here the reading was one constant value in ${sm.mhz_constant_jobs} of ${sm.jobs} jobs, but it comes from /proc/cpuinfo inside the guest, and the median reading differs between jobs (${M.map((m, i) => `${m.cpu_short} ${per[i]}`).join('; ')}). No cpufreq governor or boost files exist in these VMs (${sm.governor_files} jobs). Steal is counted in 10 ms ticks, coarse against a process of about ${sm.process_ms_median} ms (the median); bursts inside a process are invisible. ${sm.jobs} jobs draw whatever CPU models the pool gives: ${M.map((m) => `${m.cpu_short} ${jobsOf(m.n_jobs)}`).join(', ')}. Correlation only, no cause.`);
  setV('limEnv', `Steal, reported frequency and core sharing were recorded in a separate run of ${sm.jobs} jobs (section 6c), not in the runs behind the main figures: none was large enough to move a cell, a virtual machine’s reported frequency may hide real changes, and the driver was seen on the pinned vCPU’s hyperthread sibling in ${sm.jobs_sharing_core} of ${sm.jobs} jobs.`);
  const box = $('env-tables');
  box.replaceChildren();
  const head = ['Job', 'Processes timed', 'With steal', 'Steal share', 'Reported MHz (median)', 'Drift, first vs second half', 'Drift, off vs on', 'Driver seen on the pinned vCPU’s sibling', 'Driver seen on the pinned vCPU'];
  M.forEach((m, i) => {
    box.append(el('p', { class: 'tcap' }, el('b', null, `Table E${i + 1}.`), ` ${m.cpu_short}, ${jobsOf(m.n_jobs)}: one row per job. Exclusion test: ${m.cells} cells, ${m.excluded_processes} processes left out, ${m.cells_moved} cells moved.`),
      el('div', { class: 'tablewrap boxed', tabindex: '0', role: 'region', 'aria-label': `Table E${i + 1}, scrolls sideways on a narrow screen` },
        el('table', { class: 'tbl dense' },
          el('thead', null, el('tr', null, ...head.map((h, j) => el('th', { scope: 'col', class: j >= 1 && j <= 6 ? 'num' : null }, h)))),
          el('tbody', null, ...m.jobs.map((j) => el('tr', null,
            el('th', { scope: 'row' }, `Job ${j.job}`), el('td', { class: 'num' }, num(j.processes)), el('td', { class: 'num' }, String(j.processes_with_steal)),
            el('td', { class: 'num' }, pctS(j.steal_share_pct)), el('td', { class: 'num' }, String(Math.round(j.mhz_median))),
            el('td', { class: 'num' }, pctS(j.half_drift_pct)), el('td', { class: 'num' }, pctS(j.side_drift_pct)),
            el('td', null, j.shares_core ? 'yes' : 'no'), el('td', null, j.driver_on_pinned ? 'yes' : 'no')))))));
  });
}
function renderHoldout() {
  const H = S.ho;
  const judged = H.rows.filter((r) => r.reproduced != null);
  const same = judged.filter((r) => r.reproduced), diff = judged.filter((r) => !r.reproduced);
  const when = H.preregistration_committed_utc ? H.preregistration_committed_utc.replace('T', ' ').replace('Z', ' UTC') : 'before the runs';
  const formName = (f) => (f === 'map' ? 'Map' : f === 'inconclusive' ? 'Inconclusive' : f);
  const cell = (d) => (d ? `${formName(d.form)} (${d.jobs} job${d.jobs === 1 ? '' : 's'}${d.runs !== 3 ? `, ${d.runs} run${d.runs === 1 ? '' : 's'}` : ''})` : 'not drawn');
  const lost = (d) => (d && d.lost && d.enough ? `${rangeX(d.lost.min, d.lost.max)}, median ${fx(d.lost.median)}×` : 'none given');
  setV('holdoutShort', `A fresh holdout run: same pattern on ${joinAnd(same.map((r) => r.cpu_short))}${diff.length ? `, not on ${joinAnd(diff.map((r) => r.cpu_short))}` : ''}`);
  setV('holdoutText', `The rules and the code that pools jobs were fixed first, and the plan for this run was committed at ${when}, before its first run started. Then ${H.runs.length} fresh runs (${H.jobs} jobs) were measured and pooled with the same code. Same pattern on ${joinAnd(same.map((r) => r.cpu_short))}, with nearly the same numbers. ${diff.map((r) => `${r.cpu_short} did not reproduce as a pattern: ${cell(r.holdout).toLowerCase()} against ${cell(r.original).toLowerCase()} the first time; it had only ${r.holdout.jobs} jobs, and was already marked fragile`).join('; ')}${diff.length ? '. ' : ''}${H.rows.filter((r) => r.reproduced == null).map((r) => `${r.cpu_short} drew too few jobs both times (${r.original ? r.original.jobs : 0} and ${r.holdout ? r.holdout.jobs : 0}), so nothing is said about it`).join('; ')}. Nothing here tests another toolchain.`);
  $('holdout-table').querySelector('tbody').replaceChildren(...H.rows.map((r) => el('tr', null,
    el('th', { scope: 'row' }, r.cpu_short), el('td', null, cell(r.original)), el('td', null, cell(r.holdout)),
    el('td', { class: 'num' }, `${lost(r.original)} → ${lost(r.holdout)}`),
    el('td', null, r.reproduced == null ? 'no verdict either time' : r.reproduced ? 'yes' : 'no'))));
  setV('holdoutCap', `Table H. The first pooled runs against the holdout, per CPU model: verdict, jobs and the cost of the loops that lose SIMD in cache (aligned). Source: ${H.source} and ${H.original_source}; plan: ${H.preregistration}.`);
}
/* The timed clang 19 to 21 result for matrix multiply, next to the compile-only sweep's version-by-version finding: both
   sections must be loaded, so this runs once after every section has rendered. */
function renderMatmulVersions() {
  if (!S.ce || !S.ver || !S.verMatmul) return;
  const f = ceFindings(), tail = ` Compile-only (section 6, not timed), matrix multiply is ${f.matmul}: it depends on the compiler version.`;
  setV('verMatmul', S.verMatmul + tail);
  for (const n of document.querySelectorAll('[data-v="limVersions"]')) n.textContent += tail;
}
function renderCeSweep() {
  const C = S.ce;
  S.ceT = S.ceT || 'x86-64';
  S.ceO = S.ceO || '-O2';
  const f = ceFindings();
  setV('ceCompilers', String(C.counts.compilers));
  const gccR = `GCC ${ceRanges(C.summary.majors.filter((m) => C.rows.some((r) => r.family === 'gcc' && r.major === m)))}`;
  setV('ceFind', `Compiled only, not timed, on ${C.counts.compilers} compilers: ${f.short}`);
  setV('ceCap', `Compile-only: this says which loops lose vectorization, not what they cost. Each clang is paired with the libc++ Compiler Explorer provides (assumed to match). sten: stencil, strd: stride-2, gath: gather, mm: matrix multiply.`);
  setV('ceNote', `Every row of the compile-only sweep: ${C.counts.rows} rows (${C.counts.compilers} compilers, ${f.clangRange} with libc++ and ${gccR} with assertions, on three targets at -O2 and -O3), ${C.counts.cells} loop cells from ${C.counts.builds} builds. No timing: a cell says whether the loop is vectorized with the checks off and with them on. ${f.text}`);
  setV('ceTableCap', `Per compiler, target and optimization level: each loop lost under the checks, kept, or not vectorized in either build. Clang uses libc++ hardening (FAST; clang 16 and 17 use older macros, see the notes), GCC uses _GLIBCXX_ASSERTIONS. Compile-only; each clang version is paired with the libc++ Compiler Explorer provides (assumed to match).`);
  const tseg = $('ce-tseg'), oseg = $('ce-oseg');
  const radioKeys = (seg) => (e) => {
    const bs = [...seg.querySelectorAll('button')]; let i = bs.indexOf(document.activeElement);
    if (i < 0) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') i = (i + 1) % bs.length; else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') i = (i - 1 + bs.length) % bs.length; else return;
    e.preventDefault(); bs[i].click(); seg.querySelectorAll('button')[i].focus();
  };
  tseg.replaceChildren(...ceTargets().map((t) => el('button', { type: 'button', role: 'radio', 'data-t': t, onclick: () => { S.ceT = t; ceDraw(); } }, C.targets[t].replace(/ \(.*\)$/, ''))));
  oseg.replaceChildren(...['-O2', '-O3'].map((o) => el('button', { type: 'button', role: 'radio', 'data-o': o, onclick: () => { S.ceO = o; ceDraw(); } }, o)));
  tseg.onkeydown = radioKeys(tseg); oseg.onkeydown = radioKeys(oseg);
  ceDraw();
  // details: every row
  const tb = $('ce-table');
  tb.querySelector('thead').replaceChildren(el('tr', null, el('th', { scope: 'col' }, 'Compiler'), el('th', { scope: 'col' }, 'Target'), el('th', { scope: 'col' }, 'Opt.'),
    ...C.kernels.map((k) => el('th', { scope: 'col' }, el('a', { href: C.links[k], target: '_blank', rel: 'noopener', title: 'open this loop in Compiler Explorer' }, SHORT_NAMES[k])))));
  const TAG = { lost: 'lost', kept: 'kept', none: 'none' };
  const tg = ceTargets();
  const all = [...C.rows].sort((a, b) => ceOrder(a) - ceOrder(b) || tg.indexOf(a.target) - tg.indexOf(b.target) || a.opt.localeCompare(b.opt));
  tb.querySelector('tbody').replaceChildren(...all.map((r, i) => el('tr', { class: i && all[i - 1].version !== r.version ? 'grp' : null },
    el('th', { scope: 'row' }, ceFull(r)), el('td', null, C.targets[r.target].replace(/ \(.*\)$/, '')), el('td', null, r.opt),
    ...C.kernels.map((k) => { const st = ceState(r.vec[k]); return el('td', { class: 'ce-td', title: ceRemarkText(r, k) }, el('span', { class: `tag t-${st === 'none' ? 'neither' : st}` }, TAG[st])); }))));
  // details: per-version notes, from the rows
  const cl = C.rows.filter((r) => r.family === 'clang'), gc = C.rows.filter((r) => r.family === 'gcc');
  const macros = [...new Set(cl.map((r) => r.macro))].map((m) => { const ms = [...new Set(cl.filter((r) => r.macro === m).map((r) => r.major).filter(Boolean))]; const tr = cl.some((r) => r.macro === m && !r.major); return `${code(m).outerHTML} on clang ${ceRanges(ms)}${tr ? ' and trunk' : ''}`; });
  const gv = (t) => joinAnd([...new Set(gc.filter((r) => r.target === t).map((r) => r.version))]);
  const noVec = gc.filter((r) => r.opt === '-O3').filter((r) => ['k02_add_fwd', 'k03_stencil', 'k05_stride2'].every((k) => !r.vec[k].none));
  const notes = [
    `Checks macro: ${joinAnd(macros)}; GCC: ${code([...new Set(gc.map((r) => r.macro))].join(', ')).outerHTML}. Every row's macro had its expected effect: ${C.rows.every((r) => r.macro_effective) ? 'yes' : 'no'}.`,
    `GCC versions differ by target, as Compiler Explorer offers them: x86-64 ${gv('x86-64')}; AArch64 ${gv('aarch64')}.`,
    noVec.length ? `${joinAnd([...new Set(noVec.map((r) => ceFull(r)))])} at -O3 do${noVec.length === 1 ? 'es' : ''} not vectorize the forward add, the stencil or the stride-2 loop even with checks off, so nothing is lost there; ${joinAnd([...new Set(gc.filter((r) => r.opt === '-O3' && !noVec.includes(r) && ['k02_add_fwd', 'k03_stencil', 'k05_stride2'].every((k) => r.vec[k].none)).map((r) => `GCC ${r.major}`))])} vectorize all three with checks off.` : null,
    (() => { const c0 = C.rows.find((r) => C.control.row.startsWith(r.compiler_id + ' ') && C.control.row.includes(`, ${r.target}, ${r.opt},`)); return c0 ? `Control: ${ceFull(c0)}, ${C.targets[c0.target]}, ${c0.opt}, the nearest row to the timed study's setup, loses the ${joinAnd(C.control.observed_lost.map((k) => SHORT_NAMES[k]))} loops; ${C.control.ok ? 'the same three' : 'not the same loops'} that the timed study's builds lose.` : null; })(),
    'The AArch64 rows use the default armv8-a target (NEON only, no SVE). “trunk” is trunk as Compiler Explorer served it when the sweep ran.',
  ].filter(Boolean);
  $('ce-notes').replaceChildren(...notes.map((h) => { const li = el('li'); li.innerHTML = h; return li; }));
  updateScrollHints();
}

/* ---------- section 7: real programs ---------- */
const RW_MAX = 20; // percent, the right end of Figure 5's linear scale
function rwPct(v, approx) { return approx && v < 0.01 ? `${v.toFixed(3)}%` : pctS(v); } // LightGBM: no more digits than its log printed
function pctS(v) { return v === 0 ? '0%' : v < 0.01 ? `${v.toFixed(4)}%` : v < 0.1 ? `${v.toFixed(3)}%` : v < 1 ? `${v.toFixed(2)}%` : `${v.toFixed(1)}%`; }
const RW_NAMES = { lightgbm_default: 'LightGBM (default)', lightgbm_multiclass: 'LightGBM (multiclass)', lightgbm_linear: 'LightGBM (linear)', draco: 'Draco', tinydnn: 'tiny-dnn', spectra: 'Spectra', meshopt: 'meshoptimizer (control)', fmt: '{fmt} (control)' };
const rwR3 = (v) => v.toFixed(3);
const rwPctOver = (v) => `${((v - 1) * 100).toFixed(1)}%`;
function rwReading(m) {
  if (m.reading === 'detectably slower') return 'slower';
  if (m.reading === 'detectably faster') return 'faster';
  return `not detectable, at most ${m.at_most_pct.toFixed(1)}%`;
}
function rwTimeRow(name, m, extra) {
  const cell = (p) => el('td', { class: 'num' }, rwR3(p.ratio), el('span', { class: 'sib-note' }, `${rwR3(p.lo)} to ${rwR3(p.hi)}`));
  const aa = el('td', { class: 'num' }, `±${m.aa.half_width_pct.toFixed(2)}%`);
  return el('tr', null, el('th', { scope: 'row' }, RW_NAMES[name]), cell(m.fast), cell(m.aligned), aa,
    extra === 'layout' ? cell(m.layout) : el('td', null, rwReading(m)));
}
function renderRealworld() {
  const R = S.rw, T = R.timing;
  const prog = R.rows.filter((r) => !r.control);
  const main = T.groups.find((g) => g.cpu_model === T.main_cpu);
  const rest = T.groups.filter((g) => g.cpu_model !== T.main_cpu);
  const restJobs = rest.reduce((n, g) => n + g.jobs, 0);
  const slow = (g) => Object.entries(g.rows).filter(([, m]) => m.reading === 'detectably slower').map(([n]) => n);
  const pc = (v) => ((v - 1) * 100).toFixed(1);
  setV('rwSlowMin', pc(T.slow_min));
  setV('rwSlowMax', pc(T.slow_max));
  const projectsOf = (rows) => new Set(rows.map((r) => r.project)).size;
  const detected = prog.filter((r) => slow(main).includes(r.row));
  setV('rwWorkloads', numWord(prog.length));
  setV('rwWorkloadsCap', capFirst(numWord(prog.length)));
  setV('rwProjects', numWord(projectsOf(prog)));
  setV('rwDetect', numWord(detected.length));
  setV('rwDetectProjects', numWord(projectsOf(detected)));
  setV('rwOthers', numWord(T.groups.length - 1));
  setV('rwStatus', `${capFirst(numWord(prog.length))} program workloads (${numWord(projectsOf(prog))} projects: LightGBM three ways, Draco, tiny-dnn, Spectra) that contain lost loops and two controls that do not, each timed whole with the checks off (NONE) and on (FAST): ${T.jobs} jobs in ${R.runs.length} runs on GitHub’s shared machines. ${main.jobs} jobs drew an AMD ${main.cpu_short}, the model with the most jobs, so Table 9 is that model; the other ${restJobs} jobs (AMD ${joinAnd(rest.map((g) => g.cpu_short))}) are summarised below and tabulated on the details page.`);
  setV('rwTCap', `FAST ÷ NONE, whole program, AMD ${main.cpu_short}, ${main.jobs} jobs, 95% interval beneath. Aligned: both builds with every hot loop aligned to 64 bytes. A/A floor: the unchecked program against a copy of itself. A reading needs both columns to clear the floor.`);
  $('rw-time-table').querySelector('tbody').replaceChildren(...Object.keys(RW_NAMES).map((n) => rwTimeRow(n, main.rows[n])));
  const lostProgs = prog.map((r) => r.row);
  const slowLost = lostProgs.filter((n) => slow(main).includes(n));
  const notDet = lostProgs.filter((n) => !slow(main).includes(n));
  const fm = main.rows.fmt, mo = main.rows.meshopt;
  const otherText = rest.map((g) => {
    const sl = lostProgs.filter((n) => slow(g).includes(n));
    const rs = sl.flatMap((n) => [g.rows[n].fast.ratio, g.rows[n].aligned.ratio]);
    return `On AMD ${g.cpu_short} (${g.jobs} jobs), ${sl.length} of the ${lostProgs.length} were detectably slower, by ${pc(Math.min(...rs))}% to ${pc(Math.max(...rs))}% across the two columns; not detectable: ${joinAnd(lostProgs.filter((n) => !sl.includes(n)).map((n) => `${RW_NAMES[n]} (at most ${g.rows[n].at_most_pct.toFixed(1)}%)`))}.`;
  }).join(' ');
  setV('rwOther', `${otherText} So “${slowLost.length} of ${lostProgs.length}” holds on AMD ${main.cpu_short} only.`);
  setV('rwOtherShort', `The “${slowLost.length} of ${lostProgs.length}” holds on AMD ${main.cpu_short} only: ${rest.map((g) => `${lostProgs.filter((n) => slow(g).includes(n)).length} on ${g.cpu_short}`).join(' and ')} (details).`);
  setV('rwOtherNote', 'On the two other models fewer programs clear their own noise floor, and “not detectable” there means the interval is too wide to say, not that the cost is zero.');
  setV('rwFinding', `On AMD ${main.cpu_short}, ${slowLost.length} of the ${lostProgs.length} programs with lost loops ran detectably slower with the checks on, by ${pc(T.slow_min)}% to ${pc(T.slow_max)}% across the two columns; ${joinAnd(notDet.map((n) => RW_NAMES[n]))} was not detectable (at most ${main.rows[notDet[0]].at_most_pct.toFixed(1)}%), nor was the meshoptimizer control (at most ${mo.at_most_pct.toFixed(1)}%). The {fmt} control ran ${((1 - fm.fast.ratio) * 100).toFixed(1)}% to ${((1 - fm.aligned.ratio) * 100).toFixed(1)}% faster with the checks on, while aligning its unchecked build alone moved it ${pc(fm.layout.ratio)}%: a placement effect, not explained here and not interpreted.`);
  const lo = Math.min(...prog.map((r) => r.lines_none)), hi = Math.max(...prog.map((r) => r.lines_none));
  const fmax = Math.max(...prog.map((r) => r.funcs_none));
  const small = prog.filter((r) => r.lines_none < 1 && slow(main).includes(r.row));
  const lin = prog.find((r) => r.row === 'lightgbm_linear');
  setV('rwShare', `Cachegrind counts instructions, not time: the lost loops’ own lines hold ${rwPct(lo, false)} to ${rwPct(hi, false)} of what the programs execute (their functions up to ${pctS(fmax)}). For ${joinAnd(small.map((r) => RW_NAMES[r.row]))} that is under 1%, yet FAST costs them ${pc(Math.min(...small.map((r) => main.rows[r.row].fast.ratio)))}% to ${pc(Math.max(...small.map((r) => main.rows[r.row].fast.ratio)))}%: consistent with most of the cost being checks elsewhere, in loops that kept SIMD or in other code. Which checks account for this was not isolated, so no mechanism is claimed (LightGBM linear, at ${pctS(lin.lines_none)}, cannot be separated).`);
  const ex = T.expect, held = ex.filter((e) => e.held), miss = ex.filter((e) => !e.held);
  const why = (e) => `${RW_NAMES[e.row].replace(' (control)', '')}: expected ${e.low.toFixed(2)} to ${e.high.toFixed(2)}${e.call === 'probably not' || e.call === 'no' ? ' and undetectable' : ''}, got ${rwR3(e.fast)} and ${rwR3(e.aligned)}${e.reading === 'detectably slower' ? ', detectable' : ''}`;
  setV('rwExpect', `Of the ${ex.length} expectations committed before any run, ${held.length} held (range and detectable-or-not call, both columns; Table 11 on the details page). Missed: ${miss.map(why).join('; ')}.`);
  setV('rwLimits', `Limits: no profile-guided optimization in this timing (a separate PGO column, section 7c, did not make the cost vanish in most rows), shared virtual machines, one toolchain (clang 18, libc++ 18, -O2, x86-64 baseline), three AMD CPU models only, and programs picked because they contain lost loops, so not a sample of Google’s services. This neither confirms nor contradicts Google’s 0.30%.`);
  setV('rwOtherCap', `The other CPU models: ${rest.map((g) => `AMD ${g.cpu_short}, ${g.jobs} jobs in ${g.runs} runs`).join('; ')} (the second in Table 10c). Readings are summarised in section 7; with so few jobs the intervals understate the spread between machines. FAST ÷ NONE, interval beneath; Layout A/A: the unchecked binary aligned ÷ as compiled.`);
  setV('rwOther2Cap', rest[1] ? `AMD ${rest[1].cpu_short}, ${rest[1].jobs} jobs in ${rest[1].runs} runs. Same columns as Table 10.` : '');
  setV('rwAllCap', `All ${T.all.jobs} jobs pooled across CPU models. Descriptive only, since it mixes CPU models.`);
  for (const [id, g] of [['rw-other-table', rest[0]], ['rw-other2-table', rest[1]], ['rw-all-table', T.all]]) {
    if (!g) continue;
    $(id).querySelector('tbody').replaceChildren(...Object.keys(RW_NAMES).map((n) => rwTimeRow(n, g.rows[n], 'layout')));
  }
  setV('rwExpectCap', `Expectations written before any build or run (realworld/PLAN.md), checked against AMD ${main.cpu_short}. “Held” needs the as-compiled and aligned ratios inside the expected range and the detectable-or-not call to match.`);
  $('rw-expect-table').querySelector('tbody').replaceChildren(...ex.map((e) => el('tr', null,
    el('th', { scope: 'row' }, RW_NAMES[e.row]),
    el('td', null, `${e.low.toFixed(2)} to ${e.high.toFixed(2)}; detectable: ${e.call}`),
    el('td', { class: 'num' }, `${rwR3(e.fast)} / ${rwR3(e.aligned)} (${e.reading})`),
    el('td', null, e.held ? 'held' : `no: ${[!e.inside ? 'ratio outside the range' : null, !e.call_ok ? 'detectable-or-not call differs' : null].filter(Boolean).join('; ')}`))));
  setV('rwIntro', `${capFirst(numWord(prog.length))} workloads from ${numWord(projectsOf(prog))} census projects with lost loops, plus ${numWord(R.rows.length - prog.length)} controls without any, each built with the checks off (NONE) and on (FAST) and run once under Cachegrind, which counts the instructions one workload iteration executes (on profile builds with the same source and flags plus line tables: the machine code is byte-identical to the timed binaries except for LightGBM, whose shares are therefore approximate, marked ≈). Two LightGBM rows use options chosen to make lost loops run, and say so.`);
  setV('rwRuns', R.build_run);
  setV('rwOutputs', R.rows.every((r) => r.outputs_match) ? `every program’s output was identical with the checks off and on (exact checksums), and every census lost loop in these programs lost vectorization in these builds too (${joinAnd([...new Map(R.rows.filter((r) => r.lost_listed).map((r) => [r.project, `${r.project} ${r.lost_here_too} of ${r.lost_listed}`])).values()])}).` : 'some outputs differ; see the table.');
  setV('rwEstIntro', `If the lost loops’ share of the time equalled their share of the instructions (NONE) and they ran r times as long with the checks on, the program would take share × (r − 1) longer (Amdahl’s law: a part’s slowdown adds to the whole in proportion to that part’s share); here r = ${fx(R.est_ratio)}, the largest loop ratio in Figure 1, applied to the lines share (lower bound) and the functions share (upper bound). Table 9 is the test of this guess: for LightGBM (linear) the lines estimate (+${pctS(lin.est_lines_pct)}) is far above the measured ${pc(main.rows.lightgbm_linear.fast.ratio)}%, so these lost loops do not slow by the kernels’ factor here (why was not measured).`);
  setV('rwR', fx(R.est_ratio));
  setV('rwEstCaveat', 'It assumes instruction share approximates time share, which the kernels showed it need not.');
  // Figure 5
  $('rw-scale').replaceChildren(...[0, 5, 10, 15, 20].map((t) => el('span', { class: 'tick', style: `left:${(t / RW_MAX) * 100}%`, text: `${t}%` })));
  $('rw-rows').replaceChildren(...R.rows.map((r) => {
    const tr = el('div', { class: 'c-track' });
    for (const t of [5, 10, 15]) tr.append(el('span', { class: 'gl', style: `left:${(t / RW_MAX) * 100}%` }));
    if (!r.control) {
      const a = Math.min(r.lines_none, RW_MAX), b = Math.min(r.funcs_none, RW_MAX);
      tr.append(el('span', { class: 'c-link', style: `left:${(a / RW_MAX) * 100}%;width:${((b - a) / RW_MAX) * 100}%` }));
      tr.append(el('span', { class: 'c-mk raw', style: `left:${(a / RW_MAX) * 100}%`, title: `lines ${pctS(r.lines_none)}` }));
      tr.append(el('span', { class: 'c-mk uniq', style: `left:${(b / RW_MAX) * 100}%`, title: `functions ${pctS(r.funcs_none)}` }));
    }
    return el('div', { class: 'c-row' }, el('span', { class: 'c-name' }, `${r.approximate ? '≈ ' : ''}${r.project}`, el('span', { class: 'c-np' }, ` ${r.control ? '(control)' : r.row.startsWith('lightgbm_') ? `(${r.row.split('_')[1]})` : ''}`)), tr,
      el('span', { class: 'val' }, el('span', { class: 'v-r' }, `${r.instr_ratio.toFixed(3)}×`), el('span', { class: 'c-u' }, r.control ? 'no lost loop' : `lines ${rwPct(r.lines_none, r.approximate)}, functions ${rwPct(r.funcs_none, r.approximate)}`)));
  }));
  // Table 5
  $('rw-table').querySelector('tbody').replaceChildren(...R.rows.map((r) => el('tr', null,
    el('th', { scope: 'row' }, `${r.project}${r.row.startsWith('lightgbm_') ? ` (${r.row.split('_')[1]})` : ''}`, el('span', { class: 'sib-note' }, r.what)),
    el('td', { class: 'num' }, `${r.instr_ratio.toFixed(3)}×`),
    el('td', { class: 'num' }, r.control ? '–' : `${r.approximate ? '≈ ' : ''}${rwPct(r.lines_none, r.approximate)}`),
    el('td', { class: 'num' }, r.control ? '–' : `${r.approximate ? '≈ ' : ''}${rwPct(r.funcs_none, r.approximate)}`),
    el('td', { class: 'num' }, `${r.traps_none} / ${r.traps_fast}`),
    el('td', null, r.lost_listed ? `${r.lost_here_too} of ${r.lost_listed}` : 'none listed'))));
  const lab = (r) => `${r.project}${r.row.startsWith('lightgbm_') ? ` (${r.row.split('_')[1]})` : ''}`;
  $('rw-est-table').querySelector('tbody').replaceChildren(...R.rows.filter((r) => !r.control).map((r) => el('tr', null,
    el('th', { scope: 'row' }, lab(r)),
    el('td', { class: 'num' }, `${r.approximate ? '≈ ' : ''}+${rwPct(r.est_lines_pct, r.approximate)}`),
    el('td', { class: 'num' }, `${r.approximate ? '≈ ' : ''}+${rwPct(r.est_funcs_pct, r.approximate)}`))));
}
function avx2Text() { // the one AMD forward-add cell above 1.1x among the other setups: clang 18 built for AVX2
  const B = S.sib;
  const r = B && B.rows.find((q) => q.variant === 'clang18v3-fast');
  const pc = r && r.cells.k02_add_fwd.per_cpu;
  const hit = pc && Object.entries(pc).filter(([m]) => m.startsWith('EPYC')).sort((p, q) => q[1].L1.max - p[1].L1.max)[0];
  return hit ? `the forward add at ${fx(hit[1].L1.max)}× on ${hit[1].jobs === 1 ? 'one' : hit[1].jobs} ${hit[0]} job${hit[1].jobs === 1 ? '' : 's'} built for AVX2` : 'see section 6';
}
function renderRelated() {
  const R = S.rel;
  setV('relSummary', R.summary);
  setV('relNone', R.none_found);
  const byId = Object.fromEntries(R.sources.map((x) => [x.id, x]));
  const link = (x) => el('a', { class: 'url', href: x.url, rel: 'noopener' }, x.url.replace(/^https:\/\//, ''));
  const nref = (k) => R.main_rows.indexOf(k) + 1;
  $('rel-table').querySelector('tbody').replaceChildren(...R.main_rows.map((k) => byId[k]).filter(Boolean).map((x) => el('tr', null,
    el('th', { scope: 'row' }, x.short, el('a', { class: 'cite', id: x.id === 'google' ? null : `cite-${x.id}`, href: `#ref-${x.id}`, 'aria-label': `Reference ${nref(x.id)}` }, `[${nref(x.id)}]`), el('span', { class: 'rel-url' }, link(x))),
    el('td', null, x.m_short), el('td', null, x.d_short))));
  if (has('reflist')) {
    $('reflist').replaceChildren(...R.main_rows.map((k) => byId[k]).filter(Boolean).map((x) => el('li', { id: `ref-${x.id}` },
      el('span', { class: 'rn' }, `[${nref(x.id)}]`),
      el('span', null, x.name, '. ', el('a', { class: 'url', href: x.url, rel: 'noopener' }, new URL(x.url).hostname.replace(/^www\./, '')), ' ', el('a', { class: 'cite back', href: `#cite-${x.id}`, 'aria-label': 'Back to the citation' }, '↩')))));
  }
  $('rel-list').replaceChildren(...R.sources.map((x) => el('li', null,
    el('b', null, x.name), '. ', link(x), el('br'),
    el('span', null, x.measured), ' ', el('em', null, `How it relates: ${x.differs}`))));
  $('rel-notread').replaceChildren(el('b', null, 'Also relevant, not read in full'), ' (seen only in a search summary, so nothing is claimed about them here): ',
    ...R.not_read.flatMap((x, i) => [i ? '; ' : '', x.name, x.url ? [' (', link(x), ')'] : []].flat()), '.');
}
function renderProgSum() {
  const P = S.ix.programs;
  const tb = $('progsum-table').querySelector('tbody');
  tb.replaceChildren(...[['json', 'nlohmann/json parsing'], ['fmt', '{fmt} formatting']].map(([k, label]) => {
    const qs = P.rows.map((r) => r.programs[k]).filter(Boolean);
    if (!qs.length) return null;
    const at = qs.map((q) => q.at_most_pct), aa = qs.map((q) => q.aa_pct);
    return el('tr', null, el('th', { scope: 'row' }, label), el('td', { class: 'num' }, String(qs.length)),
      el('td', { class: 'num' }, `${pct(Math.min(...at))}% to ${pct(Math.max(...at))}%`), el('td', { class: 'num' }, `${pct(Math.min(...aa))}% to ${pct(Math.max(...aa))}%`));
  }).filter(Boolean));
}
function renderRuleList() {
  const cf = S.ix.method.criteria_files, r1 = S.ix.method.v1_forward_rule, d = S.ix.method.dayone;
  const f = (sfx) => cf.find((c) => c.file.endsWith(sfx));
  const f0 = f('dayone/criteria.json'), f1 = f('harness/criteria.json'), f2 = f('criteria-v2.json'), f3 = f('criteria-v3.json');
  const c = (x) => (x && x.added_commit ? code(x.added_commit) : 'n/a');
  $('rule-list').replaceChildren(
    el('li', null, 'Day-one rule (', c(f0), ', before any run): every forward loop’s interval end below ', `${d[0] ? d[0].limit : 'n/a'}×. Both day-one runs missed it; no-go, kept on record.`),
    el('li', null, 'First harness rules (', c(f1), ', after both day-one runs): ', r1 ? `point ratio at most ${r1.point_max}×, interval end at most 1 + the larger of ${r1.ci_floor_pct.toFixed(0)}% and twice the job’s A/A noise.` : 'a looser ceiling.'),
    el('li', null, 'Second version (', c(f2), ', after the first harness results): the aligned column, the layout A/A and placement-sensitive cells; no threshold changed.'),
    el('li', null, 'Third version (', c(f3), f3 && f3.last_commit && f3.last_commit !== f3.added_commit ? [', corrected in ', code(f3.last_commit)] : '', ', after those runs and an audit, before any pooled run): pooling per CPU model and a new placement-sensitive rule; no threshold changed.'),
    el('li', null, 'The census’s AVX2 kernel control failed as registered and is shown, not re-fitted.'));
}

/* ---------- controls ---------- */
function renderControls() {
  const seg = $('cpu-seg');
  seg.replaceChildren();
  for (const c of cpuList()) {
    seg.append(el('button', { type: 'button', role: 'radio', 'data-cpu': c.slug, 'aria-checked': c.slug === S.cpu ? 'true' : 'false', tabindex: c.slug === S.cpu ? '0' : '-1', title: `${c.cpu_model}: ${c.jobs} job${c.jobs > 1 ? 's' : ''} pooled`, onclick: () => selectCpu(c.slug) }, c.cpu_short));
  }
  const pc = pooledOf(currentCpu().cpu_model);
  const hasAligned = !!(pc && pc.cells.some((c) => c.aligned));
  for (const b of $('col-seg').querySelectorAll('button')) {
    b.setAttribute('aria-checked', b.dataset.col === S.col ? 'true' : 'false');
    b.tabIndex = b.dataset.col === S.col ? 0 : -1;
    b.disabled = b.dataset.col === 'aligned' && !hasAligned;
  }
}
function radioKeys(seg, attr, fn) {
  seg.addEventListener('keydown', (e) => {
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) return;
    const bs = [...seg.querySelectorAll('button:not(:disabled)')];
    let i = bs.findIndex((b) => b.getAttribute('aria-checked') === 'true');
    i = (i + (e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : -1) + bs.length) % bs.length;
    e.preventDefault();
    fn(bs[i].dataset[attr]);
    const nb = seg.querySelector(`[data-${attr}="${bs[i].dataset[attr]}"]`);
    if (nb) nb.focus();
  });
}
function selectCol(col) {
  if (col === S.col) return;
  hashLive = true;
  S.col = col;
  renderControls();
  writeHash();
  if (has('rows')) { renderFig1(); renderFig2(); }
}
function selectCpu(s) {
  if (s === S.cpu) return;
  hashLive = true;
  S.cpu = s;
  writeHash();
  showCpu();
}
function showCpu() {
  const pc = pooledOf(currentCpu().cpu_model);
  if (!pc || !pc.cells.some((c) => c.aligned)) S.col = 'compiled';
  renderControls();
  if (has('rows')) { renderFig1(); renderFig2(); }
  renderAppA();
  fillCpuProse();
}

/* ---------- loading ---------- */
async function loadPooled() {
  const state = has('fig1-state') ? $('fig1-state') : (has('load-state') ? $('load-state') : standIn());
  state.replaceChildren(el('span', null, 'Loading the pooled results…'));
  try {
    REAL_POOLED = await getJSON(S.ix.pooled.path);
    S.pooled = S.fixture ? await getJSON(S.ix.fixture.path) : REAL_POOLED;
  } catch (err) {
    state.replaceChildren(el('span', { class: 'err' }, `A results file did not load (${err.message}). `),
      el('button', { type: 'button', onclick: () => start() }, 'Try again'));
    return false;
  }
  state.replaceChildren();
  const sample = !!S.pooled.sample;
  $('sample-band').hidden = !sample;
  $('sample-mark').hidden = !sample;
  return true;
}
async function loadSection(path, key, render, boxId) {
  try {
    S[key] = await getJSON(path);
    render();
  } catch (err) {
    const box = $(boxId);
    if (box) box.prepend(el('p', { class: 'err' }, `This section’s data did not load (${err.message}).`));
  }
}

let started = false;
async function start() {
  if (!(await loadPooled())) return;
  const cpus = cpuList();
  const h = readHash();
  S.cpu = h.cpu && cpus.some((c) => c.slug === h.cpu) ? h.cpu : (S.fixture ? cpus[0].slug : S.ix.default_cpu);
  fillStatic();
  if (!started) {
    started = true;
    await fillK02Pass();
    renderCpuTable();
    renderPsTable();
    renderProgTable();
    renderMini();
    renderAppB();
    await Promise.all([
      loadSection(S.ix.sections.corpus, 'cor', renderCensus, 'census'),
      loadSection(S.ix.sections.mitigate, 'mit', renderMitigate, 'mitigate'),
      loadSection(S.ix.sections.siblings, 'sib', renderSiblings, 'siblings'),
      loadSection(S.ix.sections.realworld, 'rw', renderRealworld, 'realworld'),
      loadSection(S.ix.sections.related, 'rel', renderRelated, 'related'),
      loadSection(S.ix.sections.cesweep, 'ce', renderCeSweep, 'siblings'),
      loadSection(S.ix.sections.holdout, 'ho', renderHoldout, 'holdout-full'),
      loadSection(S.ix.sections.layout, 'lay', renderLayout, 'layout-full'),
      loadSection(S.ix.sections.pgo, 'pgo', renderPgo, 'pgo-full'),
      loadSection(S.ix.sections.versions, 'ver', renderVersions, 'versions-full'),
      loadSection(S.ix.sections.environment, 'env', renderEnvironment, 'environment-full'),
    ]);
    renderMatmulVersions();
    renderRuleList();
    renderProgSum();
    updateScrollHints();
  }
  showCpu();
  writeHash();
}

function buildChrome() {
  if (document.body.dataset.page !== 'main') return;
  const secs = [...document.querySelectorAll('.body section[id]')];
  const toc = $('toc-list');
  const links = [];
  for (const sec of secs) {
    const h = sec.querySelector('h2');
    if (!h) continue;
    const no = h.querySelector('.secno');
    const a = el('a', { href: `#${sec.id}` }, el('span', { class: 'tn' }, no ? no.textContent : ''), (no ? h.textContent.slice(no.textContent.length) : h.textContent).trim());
    links.push([sec, a]);
    toc.append(el('li', null, a));
    h.append(el('a', { class: 'pil', href: `#${sec.id}`, 'aria-label': `Link to ${h.textContent.trim()}` }, '¶'));
  }
  const nav = $('toc'), btn = nav.querySelector('.toc-btn');
  const setOpen = (o) => { nav.classList.toggle('open', o); btn.setAttribute('aria-expanded', o ? 'true' : 'false'); };
  btn.addEventListener('click', (e) => { e.stopPropagation(); setOpen(!nav.classList.contains('open')); });
  document.addEventListener('click', (e) => { if (!e.target.closest('#toc')) setOpen(false); else if (e.target.closest('#toc-list a')) setOpen(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
  const mark = () => {
    let cur = null;
    for (const [sec, a] of links) if (sec.getBoundingClientRect().top < innerHeight * 0.35) cur = a;
    for (const [, a] of links) a.classList.toggle('on', a === cur);
  };
  addEventListener('scroll', mark, { passive: true });
  mark();
  const base = (S.ix && S.ix.repo && S.ix.repo.base) || '';
  $('cmd-cite').textContent = `@misc{jacobopacheco2026thirdofapercent,
  author = {JacoboPacheco},
  title  = {Third of a Percent: bounds checks in C++'s standard library, measured loop by loop next to Google's 0.30% average},
  year   = {2026},
  note   = {Technical note, measurements complete October 2026. Code written by AI coding agents directed by the author},
  url    = {${base}}
}`;
}
async function init() {
  S.fixture = new URLSearchParams(location.search).get('data') === 'fixture';
  const h = readHash();
  if (h.loops === 'compiled' || h.loops === 'aligned') S.col = h.loops;
  if (h.loop) S.sel = h.loop;
  try {
    S.ix = await getJSON('data/index.json');
  } catch (err) {
    (has('fig1-state') ? $('fig1-state') : document.querySelector('.front')).append(el('span', { class: 'err' }, `The data did not load (data/index.json: ${err.message}). Run python scripts/build_site_data.py, then reload.`));
    return;
  }
  radioKeys($('cpu-seg'), 'cpu', selectCpu);
  if (has('rows')) {
    $('rows').addEventListener('keydown', onRowsKey);
    matchMedia(NARROW).addEventListener('change', (e) => { if (!e.matches && $('fig2').parentElement === $('rows')) { $('figures').append($('fig2')); } markSelected(); });
    $('rows').addEventListener('pointerleave', () => { clearTimeout(S.pvT); if (S.pv) { S.pv = null; renderFig2(); } });
    radioKeys($('col-seg'), 'col', selectCol);
    for (const b of $('col-seg').querySelectorAll('button')) b.addEventListener('click', () => selectCol(b.dataset.col));
    const hint = $('col-hint');
    const setTip = (open) => { hint.setAttribute('aria-expanded', open ? 'true' : 'false'); hint.parentElement.classList.toggle('open', open); };
    hint.addEventListener('click', (e) => { e.stopPropagation(); setTip(hint.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('click', (e) => { if (!e.target.closest('.hint-wrap')) setTip(false); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && hint.getAttribute('aria-expanded') === 'true') setTip(false); });
  }
  for (const d of document.querySelectorAll('details')) d.addEventListener('toggle', updateScrollHints);
  for (const w of ['appa-wrap', 'sib-wrap']) if (has(w)) $(w).addEventListener('scroll', updateScrollHints, { passive: true });
  addEventListener('resize', updateScrollHints);
  document.addEventListener('click', (e) => {
    const b = e.target.closest('.copy');
    if (!b) return;
    const t = $(b.dataset.copy);
    if (!t) return;
    const done = () => { b.textContent = 'Copied'; b.setAttribute('aria-live', 'polite'); setTimeout(() => { b.textContent = 'Copy'; }, 1200); };
    if (navigator.clipboard) navigator.clipboard.writeText(t.textContent).then(done, () => { b.textContent = 'Select and copy'; });
  });
  await start();
  buildChrome();
}
init();
