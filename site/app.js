/* Third of a Percent: the paper's figures and every number in its prose, read from data/ (written by
   scripts/build_site_data.py). Nothing numeric is typed into this file or into index.html. */
'use strict';

const S = {
  ix: null, pooled: null, fixture: false, cpu: null, col: 'aligned', sel: null,
  builds: {}, asm: {}, token: 0, fullOpen: false, rowEls: new Map(), mit: null, sib: null, cor: null, mitSel: null,
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
// Jobs started against jobs that returned results, from the pooled run list alone. Three groups of runs: the original
// ones (the first pooled runs, flagged in the data; every job returned), the cut ones (a later run that returned fewer
// jobs than it started) and the whole ones (a later run that returned every job again).
function runLedger(ix) {
  const per = ix.criteria.jobs_per_run, runs = ix.pooled.runs;
  const orig = runs.filter((r) => r.original), later = runs.filter((r) => !r.original);
  const cut = later.filter((r) => r.jobs < per), whole = later.filter((r) => r.jobs >= per);
  const sum = (rs) => rs.reduce((a, r) => a + r.jobs, 0);
  const ids = (rs) => new Set(rs.map((r) => r.run_id));
  const oId = ids(orig), cId = ids(cut), wId = ids(whole);
  const inRuns = (c, s) => sum(c.per_run.filter((r) => s.has(r.run_id)));
  const started = runs.length * per;
  return { per, runs: runs.length, started, returned: ix.pooled.jobs, lost: started - ix.pooled.jobs,
    orig: orig.length, origJobs: sum(orig), origStarted: orig.length * per,
    cut: cut.length, cutStarted: cut.length * per, cutJobs: sum(cut),
    whole: whole.length, wholeStarted: whole.length * per, wholeJobs: sum(whole), oId,
    byCpu: ix.cpus.filter((c) => c.enough).map((c) => ({ cpu: c.cpu_short, inOrig: inRuns(c, oId), inCut: inRuns(c, cId), inWhole: inRuns(c, wId) })) };
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
function setVNodes(key, kids) { // like setV for a sentence that holds an element (a flag that must not break across lines)
  for (const n of document.querySelectorAll(`[data-v="${key}"]`)) n.replaceChildren(...kids.map((k) => (k && k.nodeType ? k.cloneNode(true) : document.createTextNode(String(k)))));
}
const NUM_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
const numWord = (n) => NUM_WORDS[n] || String(n);
const capFirst = (t) => t.replace(/^./, (c) => c.toUpperCase());
// a share as words when it is close to a simple fraction, else as a percentage
const shareWords = (x) => (Math.abs(x - 0.75) <= 0.03 ? 'about three quarters' : Math.abs(x - 0.5) <= 0.03 ? 'about half' : `${Math.round(x * 100)}%`);
function writtenWhen(s) { const m = (s || '').match(/^(.*?\d{2}:\d{2}\s+[A-Z]{2,4})/); return m ? m[1] : null; }
// The order in which plans and runs came is told from the records and from a few facts read from the GitHub API on a
// stated date (ix.provenance); the sentences below say what those show and what they cannot.
const utcText = (s) => s.replace('T', ' ').replace('Z', ' UTC');
const utcClock = (s) => `${s.slice(11, 19)} UTC`;
const LONG_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const longDate = (s) => `${Number(s.slice(8, 10))} ${LONG_MONTHS[Number(s.slice(5, 7)) - 1]} ${s.slice(0, 4)}`;
const minSec = (n) => {
  const m = Math.floor(n / 60), s = n % 60, u = (k, w) => `${k} ${w}${k === 1 ? '' : 's'}`;
  return m ? (s ? `${u(m, 'minute')} ${u(s, 'second')}` : u(m, 'minute')) : u(s, 'second');
};
function provReplication() {
  const RV = S.ix.provenance.replication, lags = [RV.first_run_lag_s, ...Object.values(RV.arm_run_lags_s).filter((x) => x < 120)];
  return `the commit time, ${utcText(RV.plan_commit_utc)}, is ${RV.margin_s} seconds before the first record’s start (${utcClock(RV.first_record_start_utc)}), and a run’s first record starts ${Math.min(...lags)} to ${Math.max(...lags)} seconds after the run is created (the first of these runs and two of the three Arm runs of the day before), so the margin lies within the range of the start lags and the order cannot be shown (the commit time is read on the author’s clock, the run times on GitHub’s and the runner’s).`;
}
// "What the public record shows": the rule files, plans and expectations were committed in the author's unpublished
// development history; the public history begins after the earlier runs, so that order cannot be checked here for them. The
// records show which rule file judged them, which commits they name and whether their run links can open.
function renderProvenance() {
  if (!has('prov-full')) return;
  const P = S.ix.provenance, groups = P.groups, sum = (gs, f) => gs.reduce((t, g) => t + f(g), 0), rec = (gs) => sum(gs, (g) => g.records);
  const gone = groups.filter((g) => g.commits.every((c) => !c.where));
  const inMain = groups.filter((g) => g.commits.every((c) => c.where === 'main'));
  const arm = groups.find((g) => g.id === 'arm'), ds = groups.find((g) => g.id === 'dsweep');
  const matched = sum(groups, (g) => g.criteria_match), total = rec(groups);
  const open = sum(groups, (g) => g.links.open), linked = sum(groups, (g) => g.links.records);
  const ac = arm.commits[0], dc = ds.commits[0];
  $('prov-full').replaceChildren(
    el('p', null, `The rule files, plans and expectations named on this page were committed in the author’s unpublished development history before the runs they govern. The public history begins on ${longDate(P.public_history.first_commit_utc)}, after the runs of s1 to s4, the holdout and the rewrite, so for those that order cannot be checked from public records. The hashes stored in the result files show that the rule files did not change after the runs: `,
      `${matched} of the ${total} result records store the sha256 of `, code(P.rule_file.file), ' as it is now, all the records of s4 to s10 and none of the older ones (s1 to s3, judged under earlier versions of the rules) or of the rewrite runs (judged under their own rule file).'),
    el('p', null, `The commit stamped in a record names the code that produced it. The ${rec(gone)} records of s1 to s4, the holdout and the rewrite runs name commits of the unpublished history that this repository does not contain, so the code at those commits cannot be recovered from it; the ${rec(inMain)} records of s6, s7 and s9 name commits in this repository’s history, which hold the rule file as it is now. The ${arm.records} Arm records name `, code(ac.commit), ` and the ${ds.records} d-sweep records name `, code(dc.commit),
      ', commits on the temporary public branches ', code(ac.where), ' and ', code(dc.where), ', which are kept for that reason.'),
    el('p', null, `Run links in the records open only for the runs of s6 to s10 (${open} of ${linked} links): the earlier runs were made before this repository existed, in repositories that are not public. The commit and run facts here were read from the GitHub API on ${P.read_on}.`));
}
// A map that stands by a narrow margin and does not survive other bootstrap seeds: the figures behind "undecided"
// (robustness/seed-sensitivity-x86.json for the seeds, robustness/aa-l2.json for the identical-binary A/A at L2), or null.
function undecidedFacts(c) {
  const R = S.ix.robustness, nc = nearestCall(c);
  if (!R || !nc || nc.left || c.form !== 'map') return null;
  const sm = R.seeds.models[c.cpu_model], cell = sm && sm.cells[nc.id];
  if (!cell || !sm.forms.inconclusive) return null;
  const aa = R.aa_l2.models[c.cpu_model];
  return { n: sm.seeds, inc: sm.forms.inconclusive, under: cell.converged_under, draws: cell.draws, l2: aa && aa.l2_pct > R.aa_l2.ceiling_pct ? aa.l2_pct : null };
}
function undecidedWords(c, short) { // '' unless the model's narrow map is undecided under other seeds
  const u = undecidedFacts(c);
  if (!u) return '';
  if (short) return `${u.inc} of ${u.n} other bootstrap seeds give an inconclusive verdict${u.l2 != null ? `, and an identical binary timed against itself at L2 has a half-width of ${u.l2.toFixed(2)}%` : ''}: best read as undecided.`;
  return `The ${c.cpu_short} margin is the stored seed’s alone: with ${u.draws.toLocaleString('en-US')} draws the end moves to ${Math.abs(u.under).toFixed(4)} ${u.under >= 0 ? 'below' : 'above'} the limit, ${u.inc} of ${u.n} other seeds give an inconclusive verdict${u.l2 != null ? `, and an identical binary timed against itself at L2 has a half-width of ${u.l2.toFixed(2)}% (the rule reads that pair at L1)` : ''}, so its map is best read as undecided.`;
}
// What the placement exemption does and does not settle (details, section 3). The labels in Table 1 describe the cells left
// after it; it sets no limit on the size of the effect it leaves out; aligning the loop starts removes one source of
// code-placement variation; several words rest on margins of a few thousandths.
function renderPsScope() {
  if (!has('ps-scope')) return;
  const good = S.ix.cpus.filter((c) => c.enough);
  const all = good.flatMap((c) => c.placement_sensitive.map((q) => ({ c, q })));
  if (!all.length) { $('ps-scope').hidden = true; return; }
  const big = all.reduce((a, x) => (x.q.aligned_ratio > a.q.aligned_ratio ? x : a));
  const judged = good.filter((c) => missedForward(c).some((x) => x.cell_id === big.q.cell_id)).map((c) => ({ c, x: missedForward(c).find((x) => x.cell_id === big.q.cell_id) }));
  const ex = all.filter((x) => x.q.cell_id === 'k03_stencil.L1').reduce((a, x) => (!a || Math.abs(x.q.aligned_ratio - x.q.ratio) > Math.abs(a.q.aligned_ratio - a.q.ratio) ? x : a), null);
  const narrow = good.map((c) => ({ c, n: nearestCall(c) })).filter((x) => x.n).map((x) => ({ c: x.c, m: x.n.margin, left: x.n.left }));
  const verdictOf = (c) => (c.form === 'inconclusive' ? 'is inconclusive' : 'has a verdict');
  const bare = (id) => cellName(id).replace(/^the /, '');
  const kids = [
    el('p', null, `The exemption sets no limit on the size of the effect it leaves out. The largest cell it leaves out is ${cellName(big.q.cell_id)} on the ${big.c.cpu_short}, ${fx(big.q.aligned_ratio)}× aligned, and the ${big.c.cpu_short} ${verdictOf(big.c)}`,
      judged.length ? `; the ${joinAnd(judged.map((j) => `${j.c.cpu_short}’s ${bare(big.q.cell_id)}, ${fx(j.x.aligned.ratio)}× aligned and not flagged,`))} is judged, misses the limit, and the ${judged[0].c.cpu_short} ${verdictOf(judged[0].c)}` : '',
      '. The labels in Table 1 therefore describe the cells left after the exemption, not every forward cell; the cells left out and their aligned ratios are listed beside each label (Table 1, and Table 2 below).'),
    ex ? el('p', null, `Aligning every hot loop to a 64-byte boundary removes one source of code-placement variation, not all of it: it fixes only where each hot loop starts, and the loop’s length, the position of its inner branches and of the code around it are left as compiled. The ${cellName(ex.q.cell_id).replace(/^the /, '')} on the ${ex.c.cpu_short} shows that the column still matters: ${fx(ex.q.ratio)}× as compiled, ${fx(ex.q.aligned_ratio)}× aligned.`) : null,
    narrow.length ? el('p', null, `Several words rest on small margins. ${narrow.length === 1 ? 'On the model' : 'On the models'} called narrow in Table 1, the interval end nearest the forward limit lies ${joinAnd(narrow.map((x) => (x.left ? `${x.m.toFixed(4)} above it on the ${x.c.cpu_short} (a cell left out as placement-sensitive, which would miss the limit if counted)` : `${x.m.toFixed(4)} below it on the ${x.c.cpu_short}`)))}.${narrow.map((x) => undecidedWords(x.c, false)).filter(Boolean).map((t) => ` ${t}`).join('')} The intervals resample jobs, so with few jobs these words can change with the jobs drawn or the seed (`,
      el('a', { href: '#method-full' }, '“Run to run”, section 8'), '). The ',
      repoNode('robustness/report.md', 'robustness report'), ' shows how the verdicts move with the interval method, and the seed-sensitivity files (', repoNode('robustness/seed-sensitivity-x86.json', 'x86-64'), ', ', repoNode('arm64/seed-sensitivity.json', 'Arm'), ') how the stored verdicts sit among other seeds.') : null,
  ];
  $('ps-scope').replaceChildren(...kids.filter(Boolean));
}
function provDsweep() {
  const D = S.ix.provenance.dsweep;
  return `The public record is the temporary branch ${D.branch}: its commit ${D.commit} holds the plan file (the stored hash) together with the sweep code, with the commit time ${utcClock(D.commit_utc)} (${D.commit_utc.slice(0, 10)}), ${minSec(D.gap_s)} before the first record started (${utcClock(D.first_record_start_utc)}); whether the plan was written before the code cannot be seen there.`;
}
function fillStatic() {
  const ix = S.ix, pg = ix.page, cr = ix.criteria;
  // Repository files: a link into the public repository (REPO_BASE in the builder); plain monospace text if it is empty.
  const base = ix.repo.base || '';
  const repoPath = { criteriaUrl: cr.file, planUrl: 'corpus/PLAN2.md', pooledUrl: ix.pooled.source, findingsUrl: 'investigate/FINDINGS.md', robustnessUrl: 'robustness/report.md', repoUrl: '',
    vecUrl: 'investigate/vectorizer/reverse-stride2/README.md', matmulVecUrl: 'investigate/vectorizer/matmul/README.md',
    lostloopsUrl: 'tools/lostloops/README.md', llWorkflowUrl: 'tools/lostloops/example-workflow.yml' };
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
    beLo: pg.break_even.at_min.share_pct.toPrecision(2), // section 10: the arithmetic at the two ends of that range
    beHi: pg.break_even.at_max.share_pct.toPrecision(2),
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
  // run-to-run movement of the pooled ratios: every model that had at least two runs with enough jobs to compare
  const reproM = good.filter((c) => c.reproduction && c.reproduction.checked > 0);
  const gapOf = (c) => (c.reproduction.max_gap_pct != null ? c.reproduction.max_gap_pct.toFixed(1) : 'n/a');
  // the count calibrated intervals would give (robustness/calibration.json), only where its counts are this pool's own
  const calOf = (c) => { const q = ix.robustness && ix.robustness.calibration.x86[c.cpu_model]; return q && q.outside === c.reproduction.outside && q.checked === c.reproduction.checked ? q : null; };
  const expOf = (c, long) => { const q = calOf(c); return q ? ` (${q.expected_outside.toFixed(1)} expected${long ? ' for calibrated intervals' : ''})` : ''; };
  v.reproText = reproM.length
    ? `on ${reproM[0].cpu_short}, ${reproM[0].reproduction.outside} of ${reproM[0].reproduction.checked}${expOf(reproM[0], true)} comparisons put one run’s pooled ratio outside another run’s interval, by at most ${gapOf(reproM[0])}%${reproM.slice(1).map((c) => `; on ${c.cpu_short}, ${c.reproduction.outside} of ${c.reproduction.checked}${expOf(c, false)}, by at most ${gapOf(c)}%`).join('')}.`
    : 'no model had enough jobs in two runs to compare them.';
  v.reproMethod = reproM.length
    ? `On ${joinAnd(reproM.map((c) => c.cpu_short))}, the ${reproM.length === 1 ? 'only model' : 'models'} with enough jobs in more than one run (a run needs ${cr.minimum_jobs} jobs of the model), a run’s pooled ratio fell outside another run’s pooled interval in ${joinAnd(reproM.map((c) => `${c.reproduction.outside} of ${c.reproduction.checked}`))} comparisons${reproM.length === 1 ? '' : ', respectively'}${reproM.every(calOf) ? `; exactly calibrated intervals would put about ${joinAnd(reproM.map((c) => calOf(c).expected_outside.toFixed(1)))} outside (robustness/calibration.json)` : ''}.`
    : 'No model had enough jobs in more than one run to compare runs.';
  // working sets larger than the cache: timed only in the early jobs, as compiled
  const RM = ix.ram_early;
  if (RM) {
    v.ramShort = `The headline range is for data that fits in cache. RAM-sized data, timed only in the ${RM.jobs} early jobs, cost reverse ${rangeX(RM.rev.min, RM.rev.max)}, stride-2 ${rangeX(RM.stride2.min, RM.stride2.max)}, by CPU model.`;
    v.ramText = `A RAM-sized working set was timed only in the ${RM.jobs} early jobs (as compiled) and not in the pooled runs. There the reverse loop cost ${rangeX(RM.rev.min, RM.rev.max)} and the stride-2 loop ${rangeX(RM.stride2.min, RM.stride2.max)}, depending on the CPU model, against ${rangeX(RM.rev_l2.min, RM.rev_l2.max)} for the reverse loop at the L2 size in the same jobs. Jobs of one CPU model differed by up to ${RM.spread.rev.pct.toFixed(0)}% (the reverse loop on the ${RM.spread.rev.cpu_short}), and in ${RM.pairs.rev.disjoint} of the ${RM.pairs.rev.total} pairs of such jobs the reverse loop’s intervals did not overlap (stride-2: ${RM.pairs.stride2.disjoint} of ${RM.pairs.stride2.total}). Out of cache the cost was smaller in these jobs and differed by CPU model, so the headline range holds for data that fits in cache only.`;
  }
  const psAll = good.flatMap((c) => c.placement_sensitive.map((q) => [q, c]));
  v.psSummary = psAll.length
    ? `On the CPU models with enough jobs, ${joinAnd([...new Set(psAll.map((x) => cellName(x[0].cell_id)))])} are placement-sensitive (${psAll.length} cases over the ${good.length} models). As compiled they run ${rangeX(Math.min(...psAll.map((x) => x[0].ratio)), Math.max(...psAll.map((x) => x[0].ratio)))}; aligned, ${rangeX(Math.min(...psAll.map((x) => x[0].aligned_ratio)), Math.max(...psAll.map((x) => x[0].aligned_ratio)))}. They are left out of the 2% test.`
    : 'No forward cell is placement-sensitive on the CPU models with enough jobs.';
  // stability across runs, per CPU model: a run gets a verdict of its own only with enough jobs of the model
  const minJ = cr.minimum_jobs;
  const stable = good.filter((c) => c.stability === 'stable');
  const na = good.filter((c) => c.stability !== 'stable');
  const naMap = na.filter((c) => c.form !== 'inconclusive'), naInc = na.filter((c) => c.form === 'inconclusive');
  const perRun = (c) => c.per_run.map((r) => r.jobs);
  const parts = [];
  if (stable.length) parts.push(`${joinAnd(stable.map((c) => `${c.cpu_short} (${runsJudged(c)} of its ${c.per_run.length} runs had ${minJ} or more of its jobs)`))} give${stable.length === 1 ? 's' : ''} the same pattern in every run that can be judged alone, and pooled`);
  for (const c of naMap) {
    const j = runsJudged(c), alone = c.per_run.filter((r) => r.form).map((r) => (r.form === 'map' ? 'a map' : r.form));
    parts.push(`${c.cpu_short} has ${c.jobs} jobs in ${c.per_run.length} runs of ${Math.min(...perRun(c))} to ${Math.max(...perRun(c))} jobs, and ${j === 0 ? `no run reached ${minJ} of them` : `only ${j === 1 ? 'one run' : `${j} runs`} reached ${minJ}${alone.length === 1 ? `, which alone was ${alone[0]}` : ''}`}, so its runs cannot be compared; pooled it is ${formWords(c.form)}`);
  }
  if (naInc.length) parts.push(`${joinAnd(naInc.map((c) => c.cpu_short))} (${jobsEach(naInc)}, at most ${Math.max(...naInc.flatMap(perRun))} in any run) ${naInc.length === 1 ? 'is' : 'are'} inconclusive pooled and cannot be judged run by run`);
  for (const f of pg.cpus_few) parts.push(`${f.cpu_short} drew ${f.jobs} job${f.jobs > 1 ? 's' : ''}, too few to judge`);
  v.stableText = `${parts.join('. ')}.`;
  // Intel and other models without a verdict, and thin coverage (details, Limits)
  const inc = good.filter((c) => c.form === 'inconclusive');
  const fewBits = [];
  if (pg.cpus_few.length) fewBits.push(`${pg.cpus_few.length === 1 ? 'the one other model' : 'the other models'} drawn, ${joinAnd(pg.cpus_few.map((f) => f.cpu_short))}, came up in ${joinAnd(pg.cpus_few.map((f) => String(f.jobs)))} job${pg.cpus_few.every((f) => f.jobs === 1) ? '' : 's'}, too few to judge`);
  if (inc.length) fewBits.push(`${joinAnd(inc.map((c) => c.cpu_short))} (${jobsEach(inc)}) ${inc.length === 1 ? 'is inconclusive and carries' : 'are inconclusive and carry'} no headline number`);
  v.fewText = fewBits.length ? `${fewBits.join('; ')}.` : 'every model drawn had enough jobs.';
  const withV = good.filter((c) => c.form !== 'inconclusive');
  const isIntel = (c) => !!(ix.intel_forward && ix.intel_forward.cpus.includes(c.cpu_short));
  const nIntelV = withV.filter(isIntel).length;
  v.verdictModels = `${capFirst(numWord(withV.length))} CPU model${withV.length === 1 ? ' has a verdict' : 's have a verdict'}: ${numWord(withV.length - nIntelV)} AMD and ${numWord(nIntelV)} Intel`;
  v.verdictNames = `${capFirst(numWord(withV.length))} CPU model${withV.length === 1 ? ' has a verdict' : 's have a verdict'} (${joinAnd(withV.map((c) => c.cpu_short))})`;
  const narrowM = good.filter((c) => closeCalls(c).length);
  const narrowBits = (c) => joinAnd(closeCalls(c).map((q) => `${q.left ? 'left-out ' : ''}${shortCell(q.id)} ${q.left ? 'would end' : 'ends'} at ${q.hi.toFixed(3)}× against ${limitWords(c)}${q.left ? ' if it were counted' : ''}`));
  v.narrowShort = narrowM.length ? `${joinAnd(narrowM.map((c) => c.cpu_short))} ${narrowM.length === 1 ? 'passes' : 'pass'} narrowly (Table 1); a narrow pass can change with the jobs drawn.` : '';
  v.narrowLong = narrowM.length ? `${narrowM.map((c) => `${c.cpu_short} passes the forward rule by a narrow margin (${narrowBits(c)})`).join('; ')}; a narrow pass can change with the jobs drawn.` : '';
  const thin = good.filter((c) => c.form === 'inconclusive' || c.stability !== 'stable');
  const thinInc = inc.length ? `${joinAnd(inc.map((c) => c.cpu_short))} ${inc.length === 1 ? 'has' : 'have'} ${[...new Set(inc.map((c) => c.jobs))].join(' or ')} jobs, in runs of at most ${Math.max(...inc.flatMap(perRun))}` : '';
  const thinMap = naMap.map((c) => `${c.cpu_short}’s ${c.jobs} jobs came in runs of ${Math.min(...perRun(c))} to ${Math.max(...perRun(c))}, so ${runsJudged(c) ? `only ${runsJudged(c)} of its ${c.per_run.length} runs` : 'none of its runs'} can be judged alone`);
  const xeons = ix.cpus.filter((c) => /xeon/i.test(c.cpu_model)); // "no Xeon model ..." holds only while no Xeon model has two runs of enough jobs
  const noXeonRuns = xeons.length > 0 && xeons.every((c) => runsJudged(c) < 2);
  v.thinText = thin.length ? `${[thinInc, ...thinMap].filter(Boolean).join('; ')}. With few jobs the sampled jobs may not contain the spread between machines, and these verdicts cannot be checked run against run${noXeonRuns ? ` (no Xeon model has two runs of ${cr.minimum_jobs} or more jobs)` : ''}.${v.narrowLong ? ` ${v.narrowLong}` : ''}`.replace(/^./, (ch) => ch.toUpperCase()) : 'Every model with a verdict was judged on at least as many jobs as the written rule needs, and its verdict held run by run.';
  // jobs that never returned, and which CPU models the returned ones are
  const L = runLedger(ix), topCpu = L.byCpu.reduce((a, c) => (!a || c.inOrig > a.inOrig ? c : a), null);
  const jobsS = (n) => `${n} job${n === 1 ? '' : 's'}`;
  const runsS = (n) => `${n} run${n === 1 ? '' : 's'}`;
  const shortBits = [`${topCpu ? topCpu.inOrig : 0} of the first ${L.origJobs}`, L.cut ? `${topCpu.inCut} of the next ${L.cutJobs}` : '', L.whole ? `${topCpu.inWhole} of the last ${L.wholeJobs}` : ''].filter(Boolean);
  v.lostShort = L.lost && topCpu ? `${L.lost} of the ${L.started} jobs started returned nothing, so the pool is uneven across CPU models (${topCpu.cpu}: ${shortBits.join(', ')}); the effect on the ratios was not tested.` : '';
  const groups = [`the ${L.orig} original runs`, L.cut ? `the ${L.cut} cut runs` : '', L.whole ? `the last ${L.whole}` : ''].filter(Boolean);
  v.lostLong = L.lost && topCpu ? `${L.runs} runs started ${L.started} jobs and ${L.returned} returned results. The ${runsS(L.orig)} that pooled first (the original runs) returned all ${L.per}.${L.cut ? ` The next ${L.cut} started ${L.cutStarted} and returned ${L.cutJobs}: each of the ${L.lost} jobs that returned nothing had finished its timing step and was cancelled in the next one, a check of the whole repository that the job ran on the machine before uploading its results, when the job time limit of that time (22 minutes) ran out (read from the workflow’s run records on GitHub).` : ''}${L.whole ? ` The last ${L.whole} were started after that limit was raised to 45 minutes, to see whether jobs return again, and were not chosen on their results; the check still ran before the upload in them, and all their jobs returned.` : ''} The workflow now uploads first and runs no such check. The cut does not touch the timing of the jobs that returned; it changes which CPU models are represented, and the ones that returned are not an even draw: jobs by model, in ${joinAnd(groups)}, ${L.byCpu.map((c) => `${c.cpu} ${joinAnd([c.inOrig, L.cut ? c.inCut : null, L.whole ? c.inWhole : null].filter((x) => x != null).map(String))}`).join('; ')}. The ${L.cut} cut runs therefore added ${jobsS(topCpu.inCut)} to ${topCpu.cpu}, which supplied ${topCpu.inOrig} of the ${L.origJobs} in the original runs, and ${jobsS(L.cutJobs - topCpu.inCut)} to the other models${L.whole ? `; the last ${L.whole} added ${topCpu.inWhole} and ${L.wholeJobs - topCpu.inWhole}` : ''}. Whether the lost jobs would have given different ratios was not tested.` : 'Every job started returned results.';
  v.lostPoolNote = L.lost ? ` (${L.lost} more were started and returned nothing; see the limits below)` : '';
  // how the kernel pool grew: the registered design and the runs added after (the sizes of the three pooled files)
  const ST = ix.pooled.steps;
  v.poolSteps = `The registered design was ${numWord(ST[0].runs)} runs of ${cr.jobs_per_run} jobs (${ST[0].jobs} jobs). ${capFirst(numWord(ST[1].runs - ST[0].runs))} more full runs (${ST[1].jobs} jobs in all), then ${numWord(ST[2].runs - ST[1].runs)} more (${ST[2].jobs}), were added after the verdicts of the earlier pool had been read, with no written stopping rule.`;
  v.pooledPath = ix.pooled.source;
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
  const bestPooled = good.reduce((a, c) => (!a || c.jobs > a.jobs ? c : a), null); // the model with the most jobs: the pooled kernel floor, for contrast with the single early jobs
  v.aaPoolJobs = bestPooled ? String(bestPooled.jobs) : 'n/a'; v.aaPoolCpu = bestPooled ? bestPooled.cpu_short : 'n/a'; v.aaPool = bestPooled ? pct(bestPooled.aa_half_width_pct, 1) : 'n/a';
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
  for (const id of ['fwd-low', 'lost-li']) { const p = document.getElementById(id); if (p) p.hidden = !p.textContent.trim(); } // no note, no empty paragraph
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
      s1 ? ` (as compiled it ran ${s1.ratio.toFixed(2)}× [${s1.ci95[0].toFixed(3)}, ${s1.ci95[1].toFixed(3)}] on ${s1.cpu_short}, run ${s1.run_id})` : '', `. Every rule file was committed before the runs it judges, in the author’s unpublished development history (`,
      el('a', { href: 'details.html#prov-full' }, 'what the public record shows'), ').');
  }
  renderProvenance();
  renderPsScope();
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
  $('cmd-measure-arm').textContent = `${ix.repo.measure_command} -f runner=${ARM_RUNNER}`;
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

/* ---------- verdict words: what the written rules said about a CPU model, in plain language ---------- */
const runsJudged = (c) => c.per_run.filter((r) => r.form).length; // runs with enough jobs of this model to get a verdict of their own
const jobsEach = (cs) => { const js = [...new Set(cs.map((c) => c.jobs))]; return js.length === 1 && cs.length > 1 ? `${js[0]} jobs each` : joinAnd(cs.map((c) => `${c.jobs} job${c.jobs === 1 ? '' : 's'}`)); };
const formWords = (f) => (f === 'map' ? 'a map' : f === 'holds_everywhere' ? 'a small cost everywhere' : 'inconclusive');
function missedForward(c) { // the judged forward cells that break the written rule (aligned: point ratio and interval end both within the limit)
  const pc = pooledOf(c.cpu_model);
  if (!pc || !pc.verdict) return [];
  const lim = 1 + (pc.verdict.forward_limit_pct != null ? pc.verdict.forward_limit_pct : 2) / 100;
  const ps = new Set(c.placement_sensitive.map((q) => q.cell_id));
  return pc.cells.filter((x) => x.class === 'kept' && IN_CACHE.includes(x.size_class) && !ps.has(x.cell_id) && x.aligned && (x.aligned.ratio > lim || x.aligned.ci95[1] > lim));
}
function limitWords(c) { const pc = pooledOf(c.cpu_model); return `${+(((pc && pc.verdict && pc.verdict.forward_limit_pct) || 2).toFixed(1))}%`; }
function missWords(c) { // '2% rule missed by …', in plain words, or '' when no judged forward cell breaks it
  const m = missedForward(c);
  return m.length ? joinAnd(m.map((x) => `${cellName(x.cell_id)} (${fx(x.aligned.ratio)}× aligned, interval ${fx(x.aligned.ci95[0])} to ${fx(x.aligned.ci95[1])}×)`)) : '';
}
function missShort(c) {
  const m = missedForward(c);
  return m.length ? joinAnd(m.map((x) => { const [k, sz] = x.cell_id.split('.'); return `${SHORT_NAMES[k] || k} ${sz} up to ${fx(x.aligned.ci95[1])}×`; })) : '';
}
/* A map that stands by a narrow margin: a model whose verdict is a map, but whose counted forward cell nearest the limit
   ends within NEAR of it (aligned, interval included), or whose left-out placement-sensitive forward cell would miss the
   limit by less than NEAR if it were counted. Each call carries the number, so the page can print it with three decimals. */
const NEAR = 0.005;
function closeCalls(c) {
  if (!c.enough || c.form !== 'map') return [];
  const pc = pooledOf(c.cpu_model);
  if (!pc || !pc.verdict) return [];
  const lim = 1 + (pc.verdict.forward_limit_pct != null ? pc.verdict.forward_limit_pct : 2) / 100;
  const ps = new Set(c.placement_sensitive.map((q) => q.cell_id));
  const out = [];
  for (const x of pc.cells) {
    if (x.class !== 'kept' || !IN_CACHE.includes(x.size_class) || !x.aligned) continue;
    const hi = x.aligned.ci95[1];
    if (!ps.has(x.cell_id) && hi <= lim && lim - hi < NEAR) out.push({ id: x.cell_id, hi, left: false });
    else if (ps.has(x.cell_id) && x.aligned.ratio <= lim && hi > lim && hi - lim < NEAR) out.push({ id: x.cell_id, hi, left: true });
  }
  return out;
}
// the placement-sensitive forward cells a model leaves out of its forward test and that stay above the limit aligned
function leftOutAbove(c) {
  const pc = pooledOf(c.cpu_model);
  if (!pc || !pc.verdict) return [];
  const lim = 1 + (pc.verdict.forward_limit_pct != null ? pc.verdict.forward_limit_pct : 2) / 100;
  const ps = new Set(c.placement_sensitive.map((q) => q.cell_id));
  return pc.cells.filter((x) => ps.has(x.cell_id) && x.class === 'kept' && IN_CACHE.includes(x.size_class) && x.aligned && x.aligned.ratio > lim);
}
const shortCell = (id) => { const [k, sz] = id.split('.'); return `${SHORT_NAMES[k] || k} ${sz}`; }; // 'k03_stencil.L2' -> 'stencil L2'
const limitX = (c) => `${(1 + parseFloat(limitWords(c)) / 100).toFixed(2)}×`; // '2%' -> '1.02×'
function nearestCall(c) { // the close call with the smallest margin to the limit, or null
  const lim = 1 + parseFloat(limitWords(c)) / 100;
  const cc = closeCalls(c).map((q) => ({ ...q, margin: Math.abs(q.hi - lim) })).sort((a, b) => a.margin - b.margin);
  return cc[0] || null;
}
function closeWords(c) { // '' when the map is not a close call
  const cc = closeCalls(c);
  if (!cc.length) return '';
  const lim = limitWords(c), ab = leftOutAbove(c);
  const counted = cc.filter((q) => !q.left), left = cc.filter((q) => q.left);
  const bits = [
    counted.length ? `${shortCell(counted[0].id)} ends at ${counted[0].hi.toFixed(3)}×${counted.slice(1).map((q) => ` and ${shortCell(q.id)} at ${q.hi.toFixed(3)}×`).join('')}, against the ${lim} limit` : '',
    ...left.map((q) => `left-out ${shortCell(q.id)} would end at ${q.hi.toFixed(3)}× against the ${lim} limit if it were counted`),
  ].filter(Boolean);
  const out = ab.length ? ` ${capFirst(joinAnd(ab.map((x) => `${shortCell(x.cell_id)} (${fx(x.aligned.ratio)}× aligned)`)))} ${ab.length === 1 ? 'is' : 'are'} left out as placement-sensitive (‡) and stay${ab.length === 1 ? 's' : ''} above the ${lim} limit aligned.` : '';
  return `the pattern held, by a narrow margin: ${bits.join('; ')}.${out}`;
}

/* ---------- section 1 and 3 tables ---------- */
function patternWords(c) {
  if (!c.enough) return `too few jobs (${c.jobs}; ${S.ix.criteria.minimum_jobs} needed)`;
  const held = c.form === 'map' ? 'held' : c.form === 'holds_everywhere' ? 'small cost everywhere' : 'inconclusive';
  const j = runsJudged(c), n = c.per_run.length;
  if (c.form === 'inconclusive') { const ms = missShort(c); return `${held}${ms ? `: ${ms}, over the ${limitWords(c)} limit` : ''}`; } // the reason, not the run count: no run of such a model was judged alone
  const nearest = nearestCall(c); // the one closest to the limit; Figure 1's note and the details name every one
  // a counted cell sets the verdict, so its number is printed (the row stays short); a left-out cell only needs the word, Figure 1's note and the details carry its number
  const narrow = nearest ? (nearest.left ? ', narrowly' : `, narrowly (${shortCell(nearest.id)} ends at ${nearest.hi.toFixed(3)}×, limit ${limitX(c)})`) : '';
  if (c.stability === 'stable') return `${held}${narrow}, the same in every run judged alone (${j} of ${n})`;
  const alone = [...new Set(c.per_run.filter((r) => r.form && r.form !== c.form).map((r) => formWords(r.form)))];
  return `${held}${narrow}; its runs cannot be compared (${j} of ${n} judged${alone.length ? `; ${j === 1 ? 'that one' : 'those'} alone ${j === 1 ? 'was' : 'were'} ${joinAnd(alone)}` : ''})`;
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
        ? `Every judged forward loop sits at most ${lim}% above 1× (aligned, interval included), and every loop that loses SIMD has its whole interval above ${lo}× in both columns.${c.placement_sensitive.length ? ` ${c.placement_sensitive.length} placement-sensitive cell${c.placement_sensitive.length > 1 ? 's' : ''} listed, not judged.` : ''}${closeWords(c) ? ` ${capFirst(closeWords(c))}` : ''}`
        : `${c.form === 'inconclusive' ? `Neither the pattern nor a small cost everywhere: ${missWords(c) ? `the ${limitWords(c)} rule is missed by ${missWords(c)}. ` : 'a condition failed (see the pooled file). '}` : 'At least one condition of the pattern failed; see the pooled file. '}The pattern needs every judged forward loop at most ${lim}% above 1× (aligned, interval included) and every loop that loses SIMD with its whole interval above ${lo}× in both columns${c.lost_ci_lo_min != null ? ` (here the smallest interval start is ${fx(c.lost_ci_lo_min)}×)` : ''}.${c.placement_sensitive.length ? ` ${c.placement_sensitive.length} placement-sensitive cell${c.placement_sensitive.length > 1 ? 's' : ''} listed, not judged.` : ''}`;
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
// A table box that scrolls (sideways, or up and down in a boxed one) has to be reachable from the keyboard: while it
// overflows it is a focusable region with a name taken from its table's caption; when it fits it is left alone.
function scrollerName(w) {
  for (let s = w.previousElementSibling, i = 0; s && i < 4; s = s.previousElementSibling, i++) {
    const b = s.classList.contains('tcap') ? s.querySelector('b') : null;
    if (b) return b.textContent.replace(/[.:]\s*$/, '').trim();
  }
  const cap = w.querySelector('caption');
  return cap ? cap.textContent.trim() : 'Table';
}
const scrollerOver = (w) => w.offsetParent !== null && (w.scrollWidth > w.clientWidth + 1 || w.scrollHeight > w.clientHeight + 1);
// a box's size changes after the last call (fonts, a section filled in later, a window resize): watch the boxes and their tables
const scrollerWatch = typeof ResizeObserver === 'function'
  ? new ResizeObserver((entries) => { for (const e of entries) { const w = e.target.closest('.tablewrap'); if (w) scrollerReach(w, scrollerOver(w)); } })
  : null;
function scrollerReach(w, over) {
  if (over) {
    if (!w.hasAttribute('tabindex')) { w.setAttribute('tabindex', '0'); w.dataset.reach = '1'; }
    if (w.dataset.reach) { w.setAttribute('role', 'region'); w.setAttribute('aria-label', `${scrollerName(w)}, scrollable`); }
  } else if (w.dataset.reach) {
    w.removeAttribute('tabindex'); w.removeAttribute('role'); w.removeAttribute('aria-label'); delete w.dataset.reach;
  }
}
function updateScrollHints() { // the 'swipe sideways' lines show only while a table is wider than its box
  for (const [wrap, hint] of [['appa-wrap', 'appa-hint'], ['sib-wrap', 'sib-hint']]) {
    const w = $(wrap);
    if (!w) continue;
    const over = w.scrollWidth > w.clientWidth + 1;
    if ($(hint)) $(hint).hidden = !over;
    w.classList.toggle('overflowing', over);
    w.classList.toggle('at-end', w.scrollLeft + w.clientWidth >= w.scrollWidth - 2);
    scrollerReach(w, scrollerOver(w));
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
    scrollerReach(w, scrollerOver(w));
  }
  if (scrollerWatch) for (const w of document.querySelectorAll('.tablewrap')) { scrollerWatch.observe(w); const t = w.querySelector('table'); if (t) scrollerWatch.observe(t); }
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
  { // both shares at the same precision, the rest taken from the rounded share so the two always add to 100
    const sh = ce && ce.novec_rev_share_pct != null && ce.novec_rest_pct != null ? Math.round(ce.novec_rev_share_pct) : null;
    setV('novecShare', sh != null ? String(sh) : 'n/a');
    setV('novecRest', sh != null ? String(100 - sh) : 'n/a');
  }
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
  return el('span', { class: 'aa-band', style: `left:calc(${(a + b) / 2}% - max(2.5px, ${(b - a) / 2}%));width:max(5px, ${b - a}%)`, title: `A/A at L1: ±${hw.toFixed(2)}%` });
}
function aaL2Say() { // '; ±0.36% at L2' where the identical binary is noisier at the L2 size (robustness/aa-l2.json), else ''
  const q = S.ix.robustness && S.ix.robustness.aa_l2.models[currentCpu().cpu_model], hw = aaHalfWidth();
  return q && hw != null && q.l2_pct > hw ? `; ±${q.l2_pct.toFixed(2)}% at L2` : '';
}
function jobsLine(r) { // the drawer's per-job strip (phones show the per-job marks only here)
  if (!r.pts.some((p) => p.perJob.length)) return null;
  const hw = aaHalfWidth();
  return el('div', { class: 'f2-jobs' }, el('p', { class: 'f2-jobs-t' }, `Every job’s own ratio (ticks) and the pooled ratio (dark bar), ${S.col === 'aligned' ? 'aligned' : 'as compiled'}${hw != null ? `; the faint band at 1× is this model’s A/A half-width at L1, ±${hw.toFixed(2)}%${aaL2Say()}` : ''}:`),
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
      ...(aaHalfWidth() != null ? [el('span', { class: 'key key-aa', 'aria-hidden': 'true' }), ` Faint band at 1×: this model’s A/A half-width at L1 (±${aaHalfWidth().toFixed(2)}%${aaL2Say()}; a binary timed against a byte-identical copy). `] : []),
      '‡ and a dashed ring mark a placement-sensitive cell: moving the loop’s code changes its ratio by more than noise (section 3), so the forward test leaves it out. It can still sit above 1× when aligned. ',
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
  if (y + h > innerHeight - 8) y = Math.max(8, innerHeight - h - 8);
  t.style.left = `${Math.min(Math.max(8, x), Math.max(8, innerWidth - w - 8))}px`;
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
  if (rs.some((r) => r.includes('could not determine number of loop iterations'))) return 'Not vectorized: clang could not work out how many times the loop runs.';
  if (rs.some((r) => r.includes('vectorization is not beneficial'))) return 'Not vectorized: the compiler’s cost estimate said the SIMD loop would be no better than the one-at-a-time loop.';
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
    const more = el('a', { href: 'details.html#passlevel' }, 'pass-level evidence');
    if (rs.some((x) => x.includes('could not determine number of loop iterations'))) {
      // what clang's own dumps show, loop by loop (compile-only, clang 18): each label says observed or inferred
      const detail = r.k === 'k04_rev'
        ? ' Here the check no longer depends on the loop counter, yet its branch stays inside the loop (observed). Adding a loop-unswitching pass just before the vectorizer makes the same release’s optimizer vectorize the saved loop (observed); clang runs no such pass at that point.'
        : r.k === 'k05_stride2'
          ? ' Here the two checks test twice the counter, and twice the counter plus one, against the vector’s size (observed). In hand-written code, a bound with a known upper limit gives both a count and a vectorized loop (observed); why the size has no such limit is inferred.'
          : '';
      return [`With the check inside, this loop has a second way out, and clang’s analysis found no iteration count for it (observed), so it did not vectorize the loop: the ${many} loop on the left becomes the one-at-a-time loop on the right.${detail} In the 29 loops compiled for the pass-level study (5 of this project’s loops and 24 hand-written test variants), clang vectorized exactly when every exit had a count (observed); that the count is what it needs is inferred. See the `, more, `.${nv}`];
    }
    if (rs.some((x) => x.includes('vectorization is not beneficial')))
      return [`Clang 18’s cost estimate for the ${many} loop, with the two bounds-check compares inside it, came out no better than the one-at-a-time loop, so it kept the one-at-a-time loop on the right, with a compare and a jump for every index it uses (observed in the compiler’s log, compile-only). Clang 19 to 21 price those compares at almost nothing and vectorize the loop (observed); that a change in clang 19 is the reason is inferred. See the `, more, `.${nv}`];
    return `With the checks on, the compiler did not vectorize this loop, so the ${many} loop on the left becomes the one-at-a-time loop on the right.${nv}`;
  }
  if (r.role === 'kept') return hotHasCheck
    ? 'Both builds are vectorized, and the check runs inside the SIMD loop.'
    : 'Both builds are vectorized. With the checks on, the compiler tests the sizes once before the SIMD loop and keeps the check out of it; the check only runs on the few elements left over at the end.';
  return 'Neither build is vectorized, so there is no SIMD to lose; the check adds a compare and a jump to every pass of the loop.';
}
const LITE_MAX = 8; // the plain view shows at most this many lines of one loop
function asmBlock(an, keep, opts) {
  const lite = !!opts.lite; // the plain view: only the marked lines, no addresses, no counts of what is left out
  const pre = el('pre', { class: lite ? 'asm-lite' : 'asm' });
  const c = el('code');
  pre.append(c);
  let skipped = 0, simdNoted = false, checkNoted = 0, any = false, simdShown = false, leftoverNoted = false;
  const checkEnds = new Set(an.checks.map((p) => p[p.length - 1]));
  const checkAddrs = new Set(an.checks.flat());
  const clsOf = (x) => (!x ? null : x.trap ? 'trap' : checkAddrs.has(x.addr) ? 'chk' : x.simd ? 'simd' : '');
  let truncAt = null; // lite: the last line kept before the cap; a bare "⋯" follows it (no count of what is left out)
  if (lite) {
    const inHot = (x) => !an.hot || (x.addr >= an.hot.start && x.addr <= an.hot.end);
    const keepL = an.lines.filter((x) => !x.pad && clsOf(x) && (clsOf(x) !== 'simd' || inHot(x)));
    const simdL = keepL.filter((x) => clsOf(x) === 'simd');
    const drop = new Set(simdL.slice(LITE_MAX).map((x) => x.addr));
    keep = new Set(keepL.filter((x) => !drop.has(x.addr)).map((x) => x.addr));
    if (drop.size) truncAt = simdL[LITE_MAX - 1].addr;
    if (opts.sample) { // identical builds: a few representative lines, not the sign-extension set-up that opens a vector loop
      const filler = /^(pxor|pcmp|punpck|pshuf|psra|psrl|psll|pmovsx|pmovzx|pand|por|movmsk)/;
      const seen = new Set(), pick = [];
      for (const x of simdL) if (!filler.test(x.mnem) && !seen.has(x.mnem)) { seen.add(x.mnem); pick.push(x); }
      let chosen = pick.slice(0, 3);
      for (const x of simdL) if (chosen.length < 3 && !filler.test(x.mnem) && !chosen.includes(x)) chosen.push(x); // too few kinds: more of the same, in order
      if (!chosen.length) chosen = simdL.slice(0, 3);
      chosen.sort((m, n) => m.addr - n.addr);
      keep = new Set(chosen.map((x) => x.addr));
      truncAt = chosen.length ? chosen[chosen.length - 1].addr : null;
    }
    if (!keep.size && an.hot) { // nothing is marked (no SIMD, no check): show the start of the hot loop, unmarked
      const hot = an.lines.filter((x) => !x.pad && x.addr >= an.hot.start && x.addr <= an.hot.end);
      for (const x of hot.slice(0, LITE_MAX)) keep.add(x.addr);
      if (hot.length > LITE_MAX) truncAt = hot[LITE_MAX - 1].addr;
    }
  }
  const flush = () => {
    if (skipped && lite) { if (any) c.append(el('span', { class: 'sep', 'aria-hidden': 'true' })); skipped = 0; }
    else if (skipped) { c.append(el('span', { class: 'gap', text: `⋯ ${skipped} instruction${skipped > 1 ? 's' : ''} not shown` })); skipped = 0; }
  };
  const shown = an.lines.filter((x) => keep.has(x.addr) && !x.pad);
  for (const x of an.lines) {
    if (!keep.has(x.addr)) { if (!x.pad) skipped++; continue; }
    if (x.pad) continue;
    flush();
    any = true;
    const cls = clsOf(x);
    // kept loops, check outside the SIMD loop: say the check lines belong to the loop over the leftover elements
    if (lite && opts.leftoverLabel && !leftoverNoted && simdShown && (cls === 'chk' || cls === 'trap')) {
      leftoverNoted = true;
      c.append(el('span', { class: 'gap leftover', text: 'then, for the leftover elements:' }));
    }
    if (cls === 'simd') simdShown = true;
    const nx = shown[shown.indexOf(x) + 1];
    const toStop = lite && x.target != null && an.traps.has(x.target); // the plain view names the trap STOP instead of showing its address
    const text = lite && x.trap ? `STOP:  ${x.mnem}` : `${x.mnem.padEnd(7)} ${toStop ? 'STOP' : x.ops}`;
    c.append(el('span', { class: `ln ${cls}` }, lite ? null : el('span', { class: 'ad', text: x.hex }), text));
    if (x.addr === truncAt) c.append(el('span', { class: 'gap', text: '⋯' }));
    if (!lite && cls === 'simd' && !simdNoted && clsOf(nx) !== 'simd') {
      simdNoted = true;
      c.append(el('span', { class: 'note', text: opts.width ? `SIMD: one instruction works on ${opts.width} numbers at once` : 'SIMD: one instruction, several numbers' }));
    }
    if (checkEnds.has(x.addr)) {
      const pair = an.checks.find((q) => q[q.length - 1] === x.addr);
      const cmpL = pair && pair.length === 2 ? an.lines.find((q) => q.addr === pair[0]) : null;
      const plainCheck = `the check: ${cmpL ? `${cmpL.mnem} compares two values, ` : ''}${x.mnem}: if it is out of range, jump to STOP`;
      c.append(el('span', { class: 'note', text: checkNoted === 0 ? (lite ? plainCheck : 'the check: is the index still inside the vector? If not, jump to the trap') : 'another check' }));
      checkNoted++;
    }
    if (x.trap) c.append(el('span', { class: 'note', text: lite ? 'this trap stops the program: ud2 is the instruction that halts it' : 'this trap stops the program (ud2, the instruction a failed check jumps to)' }));
  }
  if (!lite) flush();
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
  const hp = r.pts.find((q) => q.sz === 'L1') || r.pts[0]; // the plain view quotes one number: the smallest size's pooled ratio, as the hero does
  const top = [
    el('div', { class: 'f2-sticky' }, el('span', { class: 'f2-sticky-name' }, KERNEL_NAMES[r.k]),
      el('button', { type: 'button', class: 'back-up', onclick: back }, '↑ Back to the eight loops')),
    shownK !== S.sel ? el('p', { class: 'f2-pv' }, 'Preview. Click the row to pin it.') : null,
    el('h3', { class: 'f2-head' }, KERNEL_NAMES[r.k],
      el('span', { class: 'f2-ratio' }, hp ? [el('b', { class: 'f2-big' }, `${fx(hp.ratio)}×`), ' as long with the check on', el('span', { class: 'f2-cpu' }, ', at the smallest data size, ', el('span', { class: 'nw' }, cpu.cpu_short))] : 'not measured')),
  ].filter(Boolean);
  const fullHead = [ // everything the drawer showed before the plain view existed: it now sits behind one button; it starts at the instruction counts, the headline above is not repeated
    instrLine(r),
    el('p', { class: 'f2-range' }, r.pts.length ? `Both cache sizes: ${rangeX(r.lo, r.hi)} as long with checks on, ${cpu.cpu_short}` : 'not measured'),
    jobsLine(r),
    src ? el('p', { class: 'f2-src' }, code(srcLine(src.text))) : null,
  ].filter(Boolean);
  // The figure is not a live region (a selection rewrites about 4,000 characters, and a screen reader would read all of them);
  // this one line is, and a pointer preview is not announced.
  const live = $('fig2-live');
  if (live && shownK === S.sel) live.textContent = hp ? `${KERNEL_NAMES[r.k]}: ${fx(hp.ratio)}× as long with the check on, at the smallest data size, ${cpu.cpu_short}. The machine code is below.` : `${KERNEL_NAMES[r.k]}: not measured.`;
  const aligned = S.col === 'aligned' && cell && cell.aligned;
  const sfx = aligned ? '_a64' : '';
  const f = cpu.asm;
  if (!f) {
    body.replaceChildren(...top, el('p', { class: 'f2-why' }, 'The SAMPLE file carries no assembly, so there is no machine code to show.'));
    cap.replaceChildren(el('b', null, 'Figure 2.'), ' The machine code, unavailable for SAMPLE DATA.');
    return;
  }
  body.replaceChildren(...top, el('p', { class: 'f2-why muted' }, 'Loading the machine code…'));
  cap.replaceChildren();
  let builds, offTxt, onTxt;
  try {
    builds = S.builds[f.builds] || (S.builds[f.builds] = await getJSON(f.builds));
    [offTxt, onTxt] = await Promise.all([getText(`${f.dir}${r.k}.none${sfx}.s`), getText(`${f.dir}${r.k}.fast${sfx}.s`)]);
  } catch (err) {
    if (my !== S.token) return;
    body.replaceChildren(...top, el('p', { class: 'f2-why err' }, `The machine code did not load (${err.message}).`));
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
  const hotSimd = (an) => an.lines.some((x) => x.simd && !x.pad && (!an.hot || (x.addr >= an.hot.start && x.addr <= an.hot.end))); // from the lines the plain view shows, not any SIMD line in the function
  const hotCheck = (an) => !!an.hot && an.checks.some((q) => q[0] >= an.hot.start && q[q.length - 1] <= an.hot.end);
  const pace = (an, w) => (hotSimd(an) ? `${w ? `${w} numbers` : 'Several numbers'} at a time` : hotCheck(an) ? 'One number per pass, with a check each time' : 'One number at a time');
  const hotHasCheck = anOn.hot && anOn.checks.some((q) => q[0] >= anOn.hot.start && q[q.length - 1] <= anOn.hot.end);
  const liteCol = (title, an, w, sub, noCode, sample, leftoverLabel) => el('div', { class: 'f2-col' }, el('h3', null, title), el('p', { class: 'remark' }, sub), noCode ? null : asmBlock(an, null, { width: w, lite: true, sample, leftoverLabel }));
  const wAny = widthOff || widthOn;
  const nWord = wAny ? `${wAny} numbers` : 'several numbers';
  const onRemarks = (bOn && bOn.remarks) || [];
  const alHi = Math.max(0, ...IN_CACHE.map((sz) => { const q = cellOf(pc, `${r.k}.${sz}`); return q && q.aligned ? q.aligned.ratio : 0; })); // the same loop aligned: does alignment take the cost away?
  const asCompiledNote = !aligned && r.role === 'kept' && r.hi > 1.1
    ? (alHi > 0 && alHi - 1 > 0.5 * (r.hi - 1)
      ? [` As compiled, this loop looks expensive, and aligning the loops does not take it away on ${cpu.cpu_short} (${fx(alHi)}× aligned). `, el('a', { href: '#placement' }, 'Section 3'), ' explains the effect on the AMD models; no cause is given for this one.']
      : [' As compiled, this loop looks expensive; switch to aligned loops and most of it goes away: ', el('a', { href: '#placement' }, 'section 3'), ' explains why.']) : null;
  const limPct = (pc && pc.verdict && pc.verdict.forward_limit_pct) || 2;
  const leftOutNote = r.role === 'kept' && r.ps.length && r.hi > 1 + limPct / 100 && !identical
    ? ' Left out of the forward rule: code placement moves it (‡).' : '';
  // the plain sentence follows the compiler's own remark, as the full listing's sentence does: reverse and stride-2 could not count the iterations; matrix multiply (clang 18) was judged not worth it
  const lostSentence = onRemarks.some((x) => x.includes('could not determine number of loop iterations'))
    ? `With the check on, the compiler can no longer work on ${nWord} at a time, so the loop runs one number at a time.`
    : onRemarks.some((x) => x.includes('vectorization is not beneficial'))
      ? `With the check on, the compiler judged it not worth working on ${nWord} at a time with the check inside the loop, so the loop runs one number at a time.`
      : `With the check on, the compiler does not work on ${nWord} at a time, so the loop runs one number at a time.`;
  const plain = identical ? 'With the check on, the compiler proved the index is always in range and removed the check, so both versions are the same code.'
    : r.role === 'lost' ? lostSentence
    : r.role === 'kept' ? `Both versions work on ${wAny ? wAny : 'several'} numbers at a time. ${hotHasCheck ? 'The check runs inside that loop.' : 'With the check on, the compiler tests the sizes once before the loop, not inside it.'}${faster ? ' With the check on it is quicker here, but not because of the check (cause inferred).' : ''}`
    : 'Neither version works on several numbers at a time, so there is nothing to lose there; the check adds a compare and a jump for every number.';
  const hidden = (an) => { const k = excerpt(an); return an.lines.filter((x) => !x.pad && !k.has(x.addr)).length; };
  const techCap = [el('b', null, 'Figure 2.'),
    ` The inner loop as clang compiled it${aligned ? ', loops aligned' : ''}, with the checks off and on. Only the lines that matter are shown. `];
  const det = el('details', { class: 'f2-full', open: S.fullOpen || null },
    el('summary', { tabindex: '0' }, 'Full listing and commands'),
    el('div', { class: 'f2-full-body' }, ...fullHead,
      el('p', { class: 'f2-why' }, whyLine(r, anOn, identical, bOn, widthOff), asCompiledNote),
      ...(faster ? [faster] : []),
      el('div', { class: 'f2-cols' },
        colBox('Checks off', '_LIBCPP_HARDENING_MODE_NONE', bOff, anOff, widthOff),
        colBox('Checks on', '_LIBCPP_HARDENING_MODE_FAST', bOn, anOn, widthOn, noCheck ? `${plainRemark(bOn.remarks)} ${noCheck}` : null)),
      cmdBlock(`${bOff.command}\n${bOn.command}`, `The exact build commands${aligned ? ', loops aligned' : ''} (run ${f.run_id}, job ${f.job}):`),
      el('p', { class: 'f2-fullcap' }, ...techCap, `Grey numbers are addresses; ${hidden(anOff)} and ${hidden(anOn)} instructions of the two functions are left out. The binaries are the same in every job of ${cpu.cpu_short}; these are from run ${f.run_id}, job ${f.job}.`)));
  det.addEventListener('toggle', () => { S.fullOpen = det.open; });
  const sameBlock = identical && !anOn.traps.size; // identical code: one wide block, not a column of code beside an empty one
  body.replaceChildren(...top,
    el('p', { class: 'f2-plain' }, plain, leftOutNote, asCompiledNote),
    sameBlock
      ? el('div', { class: 'f2-cols f2-lite f2-same' }, liteCol('Checks off and on', anOff, widthOff, `Identical code with and without the check${hotSimd(anOff) ? `; ${pace(anOff, widthOff).toLowerCase()}` : ''}`, false, true))
      : el('div', { class: 'f2-cols f2-lite' },
        liteCol('Checks off', anOff, widthOff, pace(anOff, widthOff)),
        liteCol('Checks on', anOn, widthOn, pace(anOn, widthOn), false, false, r.role === 'kept' && !hotHasCheck)));
  const plainSimd = hotSimd(anOff) || hotSimd(anOn);
  cap.replaceChildren(...[
    plainSimd ? el('span', { class: 'f2-leg' }, el('span', { class: 'sw-simd', 'aria-hidden': 'true' }), ' Blue: several numbers per instruction') : null,
    anOn.traps.size ? el('span', { class: 'f2-leg' }, el('span', { class: 'sw-chk', 'aria-hidden': 'true' }), ' Yellow: the check and its trap (STOP)') : null,
    el('span', { class: 'f2-leg' }, 'Key lines only; the rest is in the full listing.'),
    det].flat().filter((x) => x != null));
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
      ? `${checks.length - nFail} of ${checks.length} controls passed. ${cc2a.kernels.pass ? 'One control' : 'The AVX2 kernel control (the same kernels built for AVX2, a newer x86-64 instruction set with wider SIMD)'} failed as registered${cc2a.kernels.pass ? '' : ': with AVX2, some loops the rule expected to lose SIMD keep it, and the rule was not changed afterwards'}.`
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
    el('li', null, ok(c2a.kernels.pass), ` Kernel control, AVX2, as registered: ${joinAnd(miss)}, so the rule written before the run (in the author’s unpublished development history) fails; it was not changed afterwards.`),
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
  { const c69 = S.ix.cpus.find((c) => c.enough && c.cpu_model.includes('6973P')), k69 = c69 && cellOf(pooledOf(c69.cpu_model), 'k02_add_fwd.L1');
    setV('sib6973Pooled', k69 && k69.aligned ? `the pooled timing of section 1 has ${c69.jobs} jobs of it, ${fx(k69.aligned.ratio)}× aligned` : 'no pooled timing of it'); }
  const IFc = S.ix.intel_forward && S.ix.intel_forward.jobs.length ? S.ix.intel_forward : null;
  const intelCounts = IFc ? joinAnd(IFc.cpus.map((c) => { const n = IFc.jobs.filter((j) => j.cpu_short === c).length; return `${c} in ${n} job${n === 1 ? '' : 's'}`; })) : '';
  setV('intelCounts', IFc ? `${IFc.cpus.length === 1 ? 'the one Intel model' : `the ${IFc.cpus.length} Intel models`} drawn (${intelCounts}; earlier runs included, replication set C’s ${IFc.set_c.jobs} Intel jobs not counted)` : '');
  const IF = S.ix.intel_forward;
  // the Intel models with enough pooled jobs have a row in Table 1; what the written rules said about each, and why
  const incl = S.ix.cpus.filter((c) => c.enough && IF && IF.cpus.includes(c.cpu_short));
  const xLo = incl.length ? Math.min(...incl.map((c) => c.lost_aligned.min)) : null, xHi = incl.length ? Math.max(...incl.map((c) => c.lost_aligned.max)) : null;
  const noPooled = IF ? IF.cpus.filter((m) => !S.ix.cpus.some((c) => c.enough && c.cpu_short === m)) : [];
  const pooledN = (m) => { const c = S.ix.cpus.find((x) => x.cpu_short === m); return c ? c.jobs : 0; };
  const intelModel = (c) => {
    const add = cellOf(pooledOf(c.cpu_model), 'k02_add_fwd.L1'), ps = c.placement_sensitive.some((q) => q.cell_id === 'k02_add_fwd.L1');
    const mx = Math.max(...c.per_run.map((r) => r.jobs));
    const head = `On the ${c.cpu_short} (${c.jobs} jobs in ${c.runs} runs, at most ${mx} in one run) `;
    if (c.form !== 'inconclusive') { // a verdict: say so, and say how narrow it is and what the rule leaves out
      const cw = closeWords(c), ab = leftOutAbove(c);
      return `${head}${cw || 'the pattern held'}${!cw && ab.length ? `; ${joinAnd(ab.map((x) => `${cellName(x.cell_id)} costs ${fx(x.aligned.ratio)}× aligned`))} but ${ab.length === 1 ? 'is' : 'are'} flagged placement-sensitive, so the rule leaves ${ab.length === 1 ? 'it' : 'them'} out` : ''}`.replace(/\.$/, '');
    }
    const miss = missWords(c), missAdd = missedForward(c).some((x) => x.cell_id === 'k02_add_fwd.L1');
    return `${head}${miss ? `the ${limitWords(c)} rule is missed by ${miss}${missAdd ? ', which is not flagged placement-sensitive' : ''}` : 'no judged forward loop misses the rule, yet the verdict is inconclusive (see the pooled file)'}${!missAdd && add && add.aligned ? `; the forward add at the L1 size costs ${fx(add.aligned.ratio)}× aligned${ps ? ' but is flagged placement-sensitive, so the rule leaves it out' : ''}` : ''}`;
  };
  const intelStatus = (c) => (c.form === 'inconclusive' ? 'came out inconclusive under the written rules, so no headline number is printed' : 'has a verdict');
  setV('intelText', IF && IF.jobs.length
    ? `Among the x86-64 models, the forward loops are near 1× on the AMD models only (one exception: ${avx2Text()}). On ${IF.cpus.length === 1 ? 'the one Intel model' : `the ${IF.cpus.length} Intel models`} GitHub drew (${joinAnd(IF.cpus.map((c) => { const n = IF.jobs.filter((j) => j.cpu_short === c).length; return `${c} in ${n} job${n === 1 ? '' : 's'}`; }))}), the forward add at L1 cost ${rangeX(IF.aligned.min, IF.aligned.max)} aligned in every one of ${IF.jobs.length} jobs, in the earlier runs, the early trial run and the pooled runs. The ${IF.set_c.jobs} Intel jobs of replication set C (${joinAnd(Object.entries(IF.set_c.per_cpu).map(([c, n]) => `${c} in ${n} job${n === 1 ? '' : 's'}`))}; Figure 8 in section 1) are not among these ${IF.jobs.length}; in the same cell they cost ${rangeX(IF.set_c.aligned.min, IF.set_c.aligned.max)} aligned.${incl.length ? ` ${joinAnd(incl.map((c) => c.cpu_short))} ${incl.length === 1 ? 'has' : 'have'} enough pooled jobs for a row in Table 1: ${incl.map((c) => `${c.cpu_short} ${intelStatus(c)}`).join('; ')}. ${incl.map(intelModel).join('. ')}. The loops that lose SIMD cost ${rangeX(xLo, xHi)} aligned on ${incl.length === 1 ? 'it' : incl.length === 2 ? 'both' : 'all'}${xLo >= S.ix.page.lost.min && xHi <= S.ix.page.lost.max ? ', inside the range the AMD models give' : ''}.` : ''}${noPooled.length ? ` ${capFirst(joinAnd(noPooled.map((m) => `${m} came up in ${pooledN(m) ? `${pooledN(m)} pooled job${pooledN(m) === 1 ? '' : 's'}, too few to judge` : 'no pooled job'}`)))}.` : ''} The toolchain runs add one more Xeon 6973P-C reading (section 6): ${v69}× in ${j69} job${j69 === 1 ? '' : 's'}.`
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
  const where = [sibOther.length ? `Section 6 (Table 4, Appendix C) also uses ${joinAnd(sibOther)}` : '', progOther.length ? `Table 8 uses ${joinAnd(progOther)}` : ''].filter(Boolean);
  setV('otherDraws', all.length
    ? `${where.join(', and ')}. ${all.length === 1 ? 'It has' : 'They have'} no row in Table 1 because ${all.length === 1 ? 'it' : 'each'} came up in fewer than the ${S.ix.criteria.minimum_jobs} pooled jobs a verdict needs (${all.map((m) => `${m}: ${pooledJobs(m) || 'none'}`).join('; ')}).`
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
function ceVersionCount(C) { // distinct compiler versions in the sweep: family and major version, trunk kept apart (x86 and AArch64 ids of one version count once)
  return new Set(C.rows.map((r) => `${r.family}-${r.version === 'trunk' ? 'trunk' : r.major}`)).size;
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
  setV('layoutIntro', `Every figure above times one placement of the hot loop: the one the compiler produced or the 64-byte aligned one. This sweep moves each kernel function by ${L.step_bytes} bytes at a time, ${L.placements} placements in all, so the hot loop starts at ${joinAnd(res.map(String))} bytes past a 64-byte boundary (a coarse sweep: the ${L.placements} placements the compiler can produce itself, not every placement). Four kernels (the forward sum, the forward add, the stencil and the reverse loop), sizes L1 and L2, ${R.reps_per_side} repetitions per side, pooled per CPU model like the main result. A forward cell passes at a placement when its pooled ratio is at most ${R.forward_point_max_ratio} and the upper end of its interval stays under ${1 + R.forward_ci_hi_floor_pct / 100} or ${R.forward_ci_hi_aa_multiplier} times that run’s own A/A half-width above 1, whichever is more; a cell is robust when all ${L.placements} placements pass and placement-dependent when at most ${R.dependent_max_pass} do. The rules were fixed before the run, in the author’s unpublished development history (an earlier attempt with 16 placements stopped at its probe step with no timing recorded, and the plan was amended to ${L.placements} placements before any timing existed). A CPU model needs ${R.min_jobs} jobs for a reading.`);
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
  const T = V.toolchains, sm = V.summary, reps = S.ix.criteria.reps_per_side, LG = runLedger(S.ix);
  const jobsOf = (n) => `${n} job${n === 1 ? '' : 's'}`;
  const enough = sm.enough;
  const mainCpu = enough.length ? enough[0].cpu_short : null;
  const mainJobs = joinAnd(enough.map((e) => String(e.jobs)));
  const thin = T.flatMap((t) => t.cpus.filter((c) => !c.enough).map((c) => c.jobs));
  const thinMin = Math.min(...thin), thinMax = Math.max(...thin);
  const tcName = (t) => `clang and libc++ ${t.clang}`;
  setV('verIntro', `The main study is clang ${S.ix.toolchain.clang.match(/\d+\.\d+\.\d+/)[0]} with Ubuntu’s libc++ 18, and section 6 timed other setups on few jobs. This column runs the main study’s harness unchanged on the same eight loops (as compiled and aligned, ${reps} processes a side, alternating order, one pinned CPU, in cache), under ${joinAnd(T.map(tcName))} from apt.llvm.org: ${sm.jobs} jobs in one run, ${sm.cpu_models} CPU models, ${T.length} toolchains. The rules were written before the run, in the author’s unpublished development history (${V.plan}). ${sm.all_probes_trap ? 'On every toolchain the checks trapped an out-of-range index in the probe, and a build without them ran clean.' : 'On some toolchain the probe did not trap; its rows are inconclusive.'} A loop holds when it loses SIMD and its interval’s lower end is at least ${fx(V.lost_lo)} in both columns at both sizes; a CPU model needs ${V.min_jobs} jobs on a toolchain for a verdict form.`);
  const alSpan = (kernel, size) => { // the same cells, loops aligned: the second column of the ranges quoted as compiled
    const vs = T.flatMap((t) => t.cpus.flatMap((c) => c.cells.filter((x) => x.kernel === kernel && (!size || x.size === size) && x.aligned != null).map((x) => x.aligned)));
    return vs.length ? { min: Math.min(...vs), max: Math.max(...vs) } : null;
  };
  const alSum = alSpan('k01_sum_fwd'), alM1 = alSpan('k08_matmul', 'L1'), alM2 = alSpan('k08_matmul', 'L2');
  const asAl = (r) => (r ? ` (${rangeX(r.min, r.max)} aligned)` : '');
  const rev7 = (s) => verSpanOnCpu(V, mainCpu, 'k04_rev', s), st7 = (s) => verSpanOnCpu(V, mainCpu, 'k05_stride2', s);
  const revR = { min: Math.min(...['L1', 'L2'].map((s) => rev7(s).min)), max: Math.max(...['L1', 'L2'].map((s) => rev7(s).max)) };
  const stR = { min: Math.min(...['L1', 'L2'].map((s) => st7(s).min)), max: Math.max(...['L1', 'L2'].map((s) => st7(s).max)) };
  const v21 = T[T.length - 1], c21 = mainCpu && v21.cpus.find((c) => c.cpu_short === mainCpu), r21 = c21 && c21.cells.find((x) => x.cell_id === 'k04_rev.L1');
  const first = T[0], c19 = mainCpu && first.cpus.find((c) => c.cpu_short === mainCpu), r19 = c19 && c19.cells.find((x) => x.cell_id === 'k04_rev.L1');
  setV('verFinding', `What held. The reverse loop and the stride-2 loop lose SIMD under the checks on ${sm.reverse_holds_all && sm.stride2_holds_all ? 'every toolchain and every CPU model that ran' : 'most rows'}, and the rule counts both as holding on all of them. Their cost, over every row and both sizes: reverse ${rangeX(sm.reverse_all.min, sm.reverse_all.max)}, stride-2 ${rangeX(sm.stride2_all.min, sm.stride2_all.max)}. ${mainCpu ? `On ${mainCpu}, the one model with enough jobs on each toolchain (${mainJobs} jobs): reverse ${rangeX(revR.min, revR.max)}, stride-2 ${rangeX(stR.min, stR.max)}.${r19 && r21 && Math.abs(r21.ratio - r19.ratio) > 0.5 ? ` The reverse loop is cheaper under ${v21.clang} (${fx(r21.ratio)}× at L1 against ${fx(r19.ratio)}× under ${first.clang}); it is still lost.` : ''}` : ''} The forward sum stays at ${rangeX(sm.sum_all.min, sm.sum_all.max)} as compiled${asAl(alSum)}.`);
  const m1 = sm.matmul_main.L1, m2 = sm.matmul_main.L2;
  const pcM = REAL_POOLED && mainCpu && REAL_POOLED.cpus.find((c) => cpuShortOf(c.cpu_model) === mainCpu);
  const c18 = ['L1', 'L2'].map((s) => cellOf(pcM, `k08_matmul.${s}`)), nv = ['L1', 'L2'].map((s) => pcM && pcM.positive && pcM.positive[`k08_matmul.${s}`]);
  const clang18Say = c18[0] && c18[1] && nv[0] && nv[1]
    ? ` On ${mainCpu} clang 18 costs ${fx(c18[0].as_compiled.ratio)}× at L1 and ${fx(c18[1].as_compiled.ratio)}× at L2 (pooled, ${c18[0].as_compiled.jobs} jobs), against ${fx(nv[0].ratio)}× and ${fx(nv[1].ratio)}× for the same loop built with no vectorization at all (the no-vectorize control), so only part of the clang 18 cost is the lost SIMD.` : '';
  const likeNoSimd = nv[0] && Math.abs(m1.max - nv[0].ratio) <= 0.05 ? ` (as slow as the no-vectorize build, ${fx(nv[0].ratio)}×)` : '';
  S.verMatmul = `What did not hold. Under clang 18 the checks make matrix multiply lose SIMD (its compiler remark says vectorizing is not beneficial with the checks inside), at ${rangeX(sm.matmul_clang18.min, sm.matmul_clang18.max)} on the same CPU models.${clang18Say} Clang 19 to 21 keep SIMD in both builds, so the rule written for this column counts it as not holding there; it is not free: on ${mainCpu || 'the CPU models with enough jobs'} the checks cost ${rangeX(m1.min, m1.max)} at L1${likeNoSimd} and ${rangeX(m2.min, m2.max)} at L2 on each of those toolchains; over all rows, as compiled, ${rangeX(sm.matmul.L1.min, sm.matmul.L1.max)}${asAl(alM1)} at L1 and ${rangeX(sm.matmul.L2.min, sm.matmul.L2.max)}${asAl(alM2)} at L2. A plausible reason is that the inner loop is short and the checks add work around the vector body (inferred; versions/MATMUL-EXPLAINED.md). Why the vectorizer’s decision changed between clang 18 and 19 is not established: the change also appears on Compiler Explorer builds and with Ubuntu’s own clang 20 and libc++ 20, which narrows it but does not separate a compiler change from a library change.`;
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
      const hasBase = c.cells.some((x) => x.clang18 != null), og = S.ix.cpus.find((x) => x.cpu_short === c.cpu_short);
      const ogJobs = og ? og.per_run.filter((r) => LG.oId.has(r.run_id)).reduce((a, r) => a + r.jobs, 0) : 0;
      const head = ['Loop', 'Size', 'Remarks say', 'As compiled', 'Aligned'].concat(hasBase ? ['clang 18, as compiled', 'Remarks under clang 18'] : []);
      const det = el('details', { class: 'more ver-cpu' },
        el('summary', null, `${c.cpu_short}, ${jobsOf(c.jobs)}: ${c.form}${c.why ? `, ${c.why}` : ''}`),
        el('p', { class: 'tcap' }, el('b', null, `Table V${t.version}.${i + 1}.`), ` ${c.cpu_short}, clang and libc++ ${t.clang}: ${kv}. A/A half-width ${pctS(c.aa_half_width_pct)}. FAST ÷ NONE per loop and size with the pooled 95% interval beneath; ${hasBase ? `the clang 18 column is this CPU model’s pooled result in the original ${LG.origJobs}-job pool${og ? ` (${jobsOf(ogJobs)} of this model)` : ''}, the baseline the rules named before the run, not in the ${S.ix.pooled.jobs}-job pool used elsewhere on this page, so a figure can differ slightly` : `the original ${LG.origJobs}-job pool has no jobs on this CPU model, so it has no clang 18 column`}.`),
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
  setV('envIntro', `The harness pins one vCPU and times each pair in alternating order, but nothing recorded what the machine did meanwhile. This run times the eight loops (clang 18, as compiled, ${sm.reps_per_side} processes a side, both sizes) on ${sm.jobs} jobs (${joinAnd(M.map((m) => `${m.cpu_short}: ${jobsOf(m.n_jobs)}`))}) and records, for every timed process, the pinned vCPU’s steal time, its reported CPU MHz and the vCPU the Python driver was on, and, for every job, the topology, the kernel, the online CPUs, any cgroup CPU limit and any cpufreq files. The rules for “large” were written before the run, in the author’s unpublished development history (${E.plan}). Source: ${E.source}; report ${E.report}.`);
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
/* ---------- the Arm column: section 6a (main page) and 6d (details page), read from data/arm64.json ---------- */
const ARM_RUNNER = 'ubuntu-24.04-arm'; // the runner label measure.yml offers beside its x86-64 default
const ARM_SMOKE_SEEN = ['k04_rev', 'k02_add_fwd']; // the two kernels the plan's first paragraph says the smoke run had already timed (scripts/check_site.py ties this list to arm64/PLAN.md)
const ARM_CLASS = { lost: 'lost', kept: 'kept', off_axis: 'none' }; // Figure 1's colour classes
const ARM_WORDS = { lost: 'loses SIMD under the check', kept: 'keeps SIMD', off_axis: 'no SIMD in either build' };
const ARM_VERB = { lost: 'loses SIMD under the check', kept: 'keeps SIMD', off_axis: 'is not vectorized in either build' };
const ARM_SHORT = { lost: 'loses SIMD', kept: 'keeps SIMD', off_axis: 'off the axis' };
const kibWords = (n) => (n >= 1024 ? `${+(n / 1024).toFixed(1)} MiB` : `${n} KiB`);
const armVer = (s) => ((s || '').match(/\d+\.\d+\.\d+/) || [''])[0];
function repoNode(path, text) { // a link into the public repository; plain code while the repository address is not set
  const b = (S.ix.repo && S.ix.repo.base) || '';
  return b ? el('a', { href: `${b}/blob/main/${path}` }, text || path) : el('code', null, path);
}
const armPick = (c, col) => (c ? (col === 'aligned' ? c.aligned : c.as_compiled) : null);
function armIv(c) { // a ratio and, when its interval is wider than the printed digits, the 95% interval
  const a = lr(c.ci95[0]), b = lr(c.ci95[1]);
  return a === b ? `${lr(c.ratio)}×` : `${lr(c.ratio)}× (${a} to ${b})`;
}
function armData() {
  const A = S.arm;
  const cell = (id) => A.cells.find((c) => c.cell_id === id);
  return { A, cell, x86: (id) => A.x86.cells[id], kern: (k) => A.kernels.find((x) => x.kernel === k),
    lostK: A.kernels.filter((k) => k.class === 'lost').map((k) => k.kernel), missed: A.verdict.forward_missed.map(cell) };
}
function armOrder(A) { // Figure 1's row order: by the x86-64 default model's aligned ratio (median of the two sizes), largest first
  const med = (k) => { const xs = IN_CACHE.map((sz) => A.x86.cells[`${k}.${sz}`]).filter(Boolean).map((c) => (c.aligned || c.as_compiled).ratio).sort((a, b) => a - b); return xs.length ? (xs.length % 2 ? xs[(xs.length - 1) / 2] : (xs[xs.length / 2 - 1] + xs[xs.length / 2]) / 2) : -1; };
  return A.kernels.map((k) => k.kernel).sort((a, b) => med(b) - med(a));
}
/* the matrix-multiply sentence of section 6a; the row-length sweep's one sentence joins it once both data files are in (either may arrive first) */
function armMmFill() {
  if (!S.arm || !S.arm.cells) return;
  const D = armData(), x86name = D.A.x86.model.cpu_short;
  const mm = D.cell('k08_matmul.L1'), mmx = D.x86('k08_matmul.L1'), mmk = D.kern('k08_matmul');
  setV('armMm', mm && mmx && mmk && mmk.class === 'kept' && mmx.class === 'lost'
    ? `Matrix multiply is where the two differ most: on this core clang keeps its SIMD loop (NEON, Arm’s version) with the checks on, yet the function costs ${fx(mm.as_compiled.ratio)}× at L1 (${fx(mm.aligned.ratio)}× aligned), against ${fx(mmx.as_compiled.ratio)}× on ${x86name}, where the same loop loses SIMD. ${dsGist() || 'Where the extra time goes is not shown.'}`
    : `Matrix multiply costs ${fx(mm.as_compiled.ratio)}× at L1 on this core (${x86name}: ${fx(mmx.as_compiled.ratio)}×).`);
}
function armTexts() { // the sentences filled into [data-v] spans on both pages
  const D = armData(), A = D.A, V = A.verdict, M = A.machine, F1 = A.forward_loops.L1, SM = A.summary;
  const names = (ks) => joinAnd(ks.map((k) => SHORT_NAMES[k]));
  const clang = `clang ${armVer(M.toolchain.clang)}`, libcxx = `libc++ ${armVer(M.toolchain.libcxx_package)}`;
  const form = formWords(V.form), g = S.ix.claim.google_pct.toFixed(2);
  const opt = (M.flags.common.match(/-O\d/) || [''])[0];
  const x86name = A.x86.model.cpu_short;
  const SS = A.seed_sensitivity, DC = SS.deciding_cell, aaL2 = A.noise.identical_binary_aa.L2.pooled;
  const reversed = DC.alt_draws - DC.alt_at_or_above_limit; // other seeds that put the interval's end under the limit
  setV('armCore', A.cpu_short);
  const fwdL1 = `${lr(F1.as_compiled.min)}× to ${lr(F1.as_compiled.max)}×`;
  setV('armGist', `On an Arm core (${A.cpu_short}, ${A.jobs} jobs) ${names(D.lostK)} lose SIMD and take ${fx(SM.lost.min)}× to ${fx(SM.lost.max)}× as long in cache; forward loops cost ${fwdL1} at L1, as compiled. The written rules call this core ${form}, by a margin of ${DC.margin_over_limit.toFixed(4)} that most other bootstrap seeds reverse.`);
  setVNodes('armWhat', [`The same eight loops, repetitions and written rules ran unchanged on GitHub’s Arm runner (${A.runs.length} runs of ${A.criteria.jobs_per_run} jobs, ${M.jobs_agreeing === A.jobs ? 'every job' : `${M.jobs_agreeing} of ${A.jobs} jobs`} on a ${M.cpu_model} core, ${clang} and ${libcxx} in FAST mode at `, el('code', { class: 'nowrap' }, opt),
    `). The data is sized by the same rule, half of each core’s L1 data cache and of its L2: ${kibWords(M.size_targets_bytes.L1 / 1024)} and ${kibWords(M.size_targets_bytes.L2 / 1024)} here, other byte counts on the x86-64 models.`]);
  setV('armWhy', D.missed.length
    ? `The forward side of a map is missed by ${joinAnd(D.missed.map((c) => `${cellName(c.cell_id)} (a ratio of ${lr(c.aligned.ratio)}× aligned, but an interval from ${lr(c.aligned.ci95[0])} to ${lr(c.aligned.ci95[1])}×, past the ${fx(V.limit)}× limit)`))}. That miss is ${DC.margin_over_limit.toFixed(4)}, less than the movement of the interval’s end under other bootstrap seeds (${reversed} of ${DC.alt_draws} put it under the limit, at a median of ${lr(DC.alt_hi.median)}), and at that size even an identical binary against itself spreads by ±${pctS(aaL2.half_width_pct)}, so these data cannot separate ${form} from a map at this cell (section 6d).`
    : `The written rules call this core ${form}; the reason is on the details page, section 6d.`);
  armMmFill();
  const wid = A.cells.filter((c) => A.forward_loops.kernels.includes(c.kernel) && c.size_class === 'L2')
    .reduce((a, c) => (!a || c.aligned.half_width_pct > a.aligned.half_width_pct ? c : a), null);
  setV('armAvg', `On ${A.cpu_short} the three forward loops cost ${fwdL1} at L1, as compiled, against an A/A floor of ±${pctS(A.aa.half_width_pct)} (forward add only): three microbenchmarks, not Google’s services, so this neither confirms nor contradicts the ${g}% average. At L2 the widest forward interval (±${pctS(wid.aligned.half_width_pct)}) and an identical binary against itself (±${pctS(aaL2.half_width_pct)}) are too wide to resolve ${g}%, and the pooled verdict is ${form}, on a margin most other seeds reverse (section 6a).`);
  setV('armLimit', `Arm: one core type (${A.cpu_short}), ${A.jobs} jobs on shared machines, ${clang} only; no real programs, profile-guided builds or other compilers were timed there (section 6a).`);
  setV('armLimFull', `Arm is one added column (section 6d): one core type, ${A.jobs} jobs in ${A.runs.length} runs, ${clang} only, no real programs.`);
  setV('armJobsSet', `the ${A.jobs} jobs of the ${A.runs.length} Arm runs (a separate pool on one core type), as compiled and aligned`);
}
/* Figure 7 (main page): eight loops on the Arm core beside the x86-64 default model; a row opens its numbers underneath */
function armRenderRows() {
  const D = armData(), A = D.A, col = S.armCol, x86name = A.x86.model.cpu_short;
  const colName = col === 'aligned' ? 'aligned' : 'as compiled';
  const rows = S.armOrder.map((k) => {
    const kern = D.kern(k);
    const b = el('button', { type: 'button', class: `row arm-row c-${ARM_CLASS[kern.class]}`, role: 'option', 'data-k': k });
    b.addEventListener('click', () => armSelect(k, false));
    const track = el('div', { class: 'track' });
    for (const t of TICKS) track.append(el('span', { class: t === 1 ? 'one' : 'gl', style: `left:${pos(t).p}%` }));
    const ratios = [], xr = [], ps = [], xms = [];
    for (const sz of IN_CACHE) {
      const c = D.cell(`${k}.${sz}`), a = armPick(c, col), x = armPick(D.x86(`${k}.${sz}`), col);
      const y = `calc(50% ${sz === 'L1' ? '-' : '+'} 5px)`;
      if (x) { xr.push(x.ratio); xms.push(el('span', { class: `xm ${sz.toLowerCase()}`, style: `left:${pos(x.ratio).p}%;top:${y}` })); } // drawn after the Arm marks, so a close value cannot hide it
      if (!a) continue;
      ratios.push(a.ratio);
      if (c.placement_sensitive) ps.push(sz);
      const lo = pos(a.ci95[0]), hi = pos(a.ci95[1]), m = pos(a.ratio);
      track.append(el('span', { class: `wh${lo.clipL ? ' clip-l' : ''}${hi.clipR ? ' clip-r' : ''}`, style: `left:${lo.p}%;width:${Math.max(0, hi.p - lo.p)}%;top:${y}` }),
        el('span', { class: `mk ${sz.toLowerCase()}${c.placement_sensitive ? ' ps' : ''}`, style: `left:${m.p}%;top:${y}` }));
    }
    track.append(...xms);
    const x1 = D.x86(`${k}.L1`);
    const xSay = xr.length ? `${x86name} ${rangeX(Math.min(...xr), Math.max(...xr))}${x1 && x1.class !== kern.class ? `, ${ARM_WORDS[x1.class]} there` : ''}` : `${x86name} not timed`;
    const psTxt = ps.length ? `placement-sensitive at ${joinAnd(ps)}` : '';
    b.append(el('span', { class: 'lab' }, el('span', { class: 'name' }, el('i', { 'aria-hidden': 'true', title: ARM_WORDS[kern.class] }), KERNEL_NAMES[k],
      ps.length ? el('span', { class: 'ps-mark', title: psTxt, 'aria-label': psTxt }, '‡') : null)),
    track, el('span', { class: 'val' }, ratios.length ? rangeX(Math.min(...ratios), Math.max(...ratios)) : 'none'));
    b.setAttribute('aria-label', `${KERNEL_NAMES[k]}, ${ARM_WORDS[kern.class]} on Arm, ${ratios.length ? rangeX(Math.min(...ratios), Math.max(...ratios)) : 'not measured'} as long with checks on, ${colName}${psTxt ? `, ${psTxt}` : ''}; ${xSay}`);
    return b;
  });
  $('arm-rows').replaceChildren(...rows);
  axisInto($('arm-axis'), 'time with checks on ÷ without, log scale');
  armMark();
}
function armMark() {
  for (const b of $('arm-rows').children) {
    const on = b.dataset.k === S.armSel;
    b.setAttribute('aria-selected', on ? 'true' : 'false');
    b.tabIndex = on ? 0 : -1;
  }
}
function armSelect(k, focus) {
  S.armSel = k;
  armMark();
  armRead();
  if (focus) { const b = $('arm-rows').querySelector(`[data-k="${k}"]`); if (b) b.focus(); }
}
function armSetCol(c) {
  if (c === S.armCol) return;
  S.armCol = c;
  for (const b of $('arm-col-seg').querySelectorAll('button')) b.setAttribute('aria-checked', b.dataset.col === c ? 'true' : 'false');
  armRenderRows();
  armRead();
  armCaption();
}
function armCaption() {
  const A = S.arm, x86name = A.x86.model.cpu_short, aligned = S.armCol === 'aligned';
  const key = (c) => el('span', { class: `key key-${c}`, 'aria-hidden': 'true' });
  const open = $('arm-cap').querySelector('details') ? $('arm-cap').querySelector('details').open : false;
  if (has('arm-fig-title')) $('arm-fig-title').textContent = `Eight loops on an Arm core, beside ${x86name}`; // the grey ticks are this model whatever Figure 1 shows
  $('arm-cap').replaceChildren(el('b', null, 'Figure 7.'),
    ` How much longer each loop takes with libc++’s checks on, on a ${A.cpu_short} Arm core (coloured marks) beside ${x86name} (`, key('xm'), key('xm-l2'), ` grey ticks), ${aligned ? 'every hot loop on a 64-byte boundary (aligned)' : 'the code as clang laid it out (as compiled)'}, data in cache. Colour and shape give the loop’s class on Arm: `,
    key('lost'), ' diamond: loses SIMD, ', key('kept'), ' circle: keeps SIMD, ', key('none'), ' square: no SIMD in either build. Select a row for its numbers; all ', String(A.cells.length), ' cells are in ',
    el('a', { href: 'details.html#arm-t1-cap' }, 'Table 12'), ` on the details page. The grey ticks are always ${x86name}, the page’s default model; they do not follow Figure 1’s CPU buttons.`,
    el('details', { class: 'cap-more', open: open || null }, el('summary', null, 'How to read the marks'),
      el('span', { class: 'key key-fill', 'aria-hidden': 'true' }), ' Filled dot: data sized to fit L1. ', el('span', { class: 'key key-open', 'aria-hidden': 'true' }), ` Hollow ring: sized to fit L2; timings at that size are noisier (an identical binary against itself spreads by ±${pctS(A.noise.identical_binary_aa.L2.pooled.half_width_pct)} there), so read a ring as rough. `,
      `The thin line is the 95% interval over ${A.jobs} jobs in ${A.runs.length} runs. A grey tick is the same loop and size class on ${x86name} (${A.x86.model.jobs} jobs, pooled; the working sets have other byte sizes): a filled one for L1 sticks out above the L1 dot, a hollow one for L2 below the ring, so a close value cannot hide it. ‡ and a dashed ring mark a placement-sensitive cell: moving the loop’s code changes its ratio by more than noise (section 3), so the forward test leaves it out. `,
      'Aligned: every hot loop starts on a 64-byte boundary in both builds. That removes one source of code-placement variation, not all of it (details, section 3). As compiled: the binaries exactly as clang emitted them. The switch moves the Arm marks and the grey ticks together and is separate from Figure 1’s. One core type: no claim about other Arm cores.'));
}
function armRead() {
  if (!has('arm-read')) return;
  const D = armData(), A = D.A, k = S.armSel, kern = D.kern(k), col = S.armCol, colName = col === 'aligned' ? 'aligned' : 'as compiled';
  const x86name = A.x86.model.cpu_short, x1 = D.x86(`${k}.L1`);
  const head = el('p', { class: 'ar-head' }, el('b', null, KERNEL_NAMES[k]), ' ',
    x1 && x1.class !== kern.class ? `${ARM_VERB[kern.class]} on Arm; on ${x86name} it ${ARM_VERB[x1.class]}.` : `${ARM_VERB[kern.class]} on Arm${x1 ? ` and on ${x86name}` : ''}.`);
  const get = (who, sz) => { const c = who === 'arm' ? armPick(D.cell(`${k}.${sz}`), col) : armPick(D.x86(`${k}.${sz}`), col); return c ? armIv(c) : 'none'; };
  const tbl = el('table', { class: 'tbl dense ar-tbl' },
    el('thead', null, el('tr', null, el('th', { scope: 'col' }, `Checks on ÷ off, ${colName}`), el('th', { scope: 'col', class: 'num' }, 'L1'), el('th', { scope: 'col', class: 'num' }, 'L2'))),
    el('tbody', null, ...[['arm', A.cpu_short], ['x86', x86name]].map(([who, nm]) => el('tr', null, el('th', { scope: 'row' }, nm), el('td', { class: 'num' }, get(who, 'L1')), el('td', { class: 'num' }, get(who, 'L2'))))));
  const n = kern.builds.none, f = kern.builds.fast, simd = kern.simd_loop.as_compiled;
  const bits = [];
  if (kern.class === 'lost') bits.push(`NEON instructions in the function: ${n.neon_instructions} without the checks, ${f.neon_instructions} with them. Clang’s remark with the checks on: “${f.why_not_vectorized}”.`);
  else if (kern.class === 'kept') bits.push(kern.diffs.L1.added === 0 && kern.diffs.L1.removed === 0
    ? `The two listings are identical (${n.asm_lines} lines, ${f.traps} check traps).`
    : `The SIMD loop is the same ${simd.fast_instructions} instructions with the checks off and on${simd.same_opcodes ? ', with the same opcodes' : ''}; the listing grows from ${n.asm_lines} to ${f.asm_lines} lines.`);
  else bits.push(`Not vectorized in either build. Clang’s remark with the checks on: “${f.why_not_vectorized}”; its reason with the checks off is not shown here. The listing grows from ${n.asm_lines} to ${f.asm_lines} lines.`);
  const pss = IN_CACHE.map((sz) => D.cell(`${k}.${sz}`)).filter((c) => c && c.placement_sensitive);
  if (pss.length) bits.push(`Placement-sensitive at ${joinAnd(pss.map((c) => c.size_class))} (compiled ÷ aligned ${joinAnd(pss.map((c) => c.placement.d.ratio.toFixed(3)))}): the written rule leaves ${pss.length === 1 ? 'that cell' : 'those cells'} out of the forward test.`);
  bits.push('The L2 figure is the rougher of the two: timings at that size are noisier, even for an identical binary (details page, section 6d).');
  $('arm-read').replaceChildren(head, tbl, el('p', { class: 'ar-note' }, bits.join(' ')), el('p', { class: 'ar-src' }, code(kern.source.text)));
}
function armFigure() {
  if (!has('arm-rows')) return;
  const A = S.arm;
  S.armOrder = armOrder(A);
  S.armCol = S.armCol || 'aligned';
  if (!S.armSel || !S.armOrder.includes(S.armSel)) S.armSel = S.armOrder[0];
  const seg = $('arm-col-seg');
  for (const b of seg.querySelectorAll('button')) { b.setAttribute('aria-checked', b.dataset.col === S.armCol ? 'true' : 'false'); b.addEventListener('click', () => armSetCol(b.dataset.col)); }
  radioKeys(seg, 'col', armSetCol);
  $('arm-rows').addEventListener('keydown', (e) => {
    const keys = ['ArrowDown', 'ArrowUp', 'Home', 'End'];
    if (!keys.includes(e.key) || !e.target.closest || !e.target.closest('.arm-row')) return;
    e.preventDefault();
    const order = S.armOrder;
    let i = order.indexOf(S.armSel);
    if (e.key === 'ArrowDown') i = Math.min(order.length - 1, i + 1);
    if (e.key === 'ArrowUp') i = Math.max(0, i - 1);
    if (e.key === 'Home') i = 0;
    if (e.key === 'End') i = order.length - 1;
    armSelect(order[i], true);
  });
  armRenderRows();
  armRead();
  armCaption();
}
/* Section 6d (details page): what ran, the verdict, every cell, what the compiler did, the floors, matrix multiply, the plan, the limits */
function armDetails() {
  if (!has('arm-full')) return;
  const D = armData(), A = D.A, V = A.verdict, M = A.machine, SM = A.summary, F1 = A.forward_loops.L1, F2 = A.forward_loops.L2;
  const names = (ks) => joinAnd(ks.map((k) => SHORT_NAMES[k]));
  const clang = `clang ${armVer(M.toolchain.clang)}`, libcxx = `libc++ ${armVer(M.toolchain.libcxx_package)}`;
  const form = formWords(V.form), x86name = A.x86.model.cpu_short;
  const t = A.runs.map((r) => Date.parse(r.started_at)), spread = Math.round((Math.max(...t) - Math.min(...t)) / 60000);
  const mcs = A.matmul_cost.sizes;
  $('arm-intro').replaceChildren(el('b', null, 'What ran. '), 'This section is the full account behind section 6a of the main page. The study’s measuring workflow, unchanged apart from a runner input, ran on GitHub’s Arm runner (', code(ARM_RUNNER),
    `): ${A.runs.length} runs of ${A.criteria.jobs_per_run} jobs (runs ${joinAnd(A.runs.map((r) => r.run_id))}, started within ${spread} minutes of each other), ${A.jobs} jobs in all. Every job drew the same core, ${M.cpu_model} (${M.vcpus} vCPUs, ${kibWords(M.l1d_kib)} L1 data cache, ${kibWords(M.l2_kib)} L2, ${M.os}, kernel ${M.kernel}).`);
  $('arm-build').replaceChildren(el('b', null, 'Builds and sizes. '), `The eight kernels were built with ${clang} and ${libcxx}: `,
    code(M.flags.common), ', no ', code('-march'), ' flag, libc++’s FAST mode (checks on) against NONE (checks off), each pair also built with every hot loop aligned to 64 bytes, plus a checks-off build with vectorization switched off as a control. ',
    `The working sets follow the x86-64 study’s rule, half of the L1 data cache and half of L2, which gives ${kibWords(M.size_targets_bytes.L1 / 1024)} and ${kibWords(M.size_targets_bytes.L2 / 1024)} here and other byte counts on the x86-64 models; matrix multiply uses d = ${mcs.L1.d} and d = ${mcs.L2.d}. So an L1 or L2 cell is the same size class on both architectures, not the same number of bytes.`);
  $('arm-basis').replaceChildren(el('b', null, 'What is shared with the x86-64 study. '), `The ${M.reps_per_side} repetitions a side in alternating order, the pinned CPU, the pooling and the written rules are the x86-64 study’s: `, code(A.criteria.file),
    A.criteria.same_as_x86_pool && A.criteria.sha256 === A.x86.criteria_sha256 ? `, the same file as for the x86-64 pool (sha256 ${A.criteria.sha256.slice(0, 12)}…), unchanged. ` : '. ',
    'The plan is ', repoNode(A.plan), '. It was committed after a two-kernel smoke run and after the three full runs were dispatched, and before any of their jobs finished; that commit time comes from the unpublished development history, which a reader of this repository cannot see, while the run times can be read from the Actions logs. This column is new and rests on three runs from one day; it may change.');
  // the verdict, in words, then the harness's own line
  const fr = V.forward_rule_cells, judged = fr.filter((c) => c.judged), passed = judged.filter((c) => c.passes);
  const psAbove = SM.placement_sensitive.filter((q) => q.aligned_ratio > V.limit);
  $('arm-verdict').replaceChildren(el('b', null, 'Verdict under the written rules: '), `${form}. `,
    A.runs.every((r) => r.form === V.form) ? `Each of the ${A.runs.length} runs judged alone (${A.criteria.jobs_per_run} jobs each) is ${form} too. ` : '',
    `The forward side of the rule is missed: of the ${fr.length} cells whose loop keeps SIMD, ${judged.length} are judged (aligned, interval included, at most ${V.forward_limit_pct}% above 1×) and ${passed.length} pass; ${joinAnd(D.missed.map((c) => `${cellName(c.cell_id)} does not (${lr(c.aligned.ratio)}× aligned, interval ${lr(c.aligned.ci95[0])} to ${lr(c.aligned.ci95[1])}×)`))}. `,
    V.lost_rule_cells.every((c) => c.passes) ? `The other side is met: every loop that loses SIMD (${names(D.lostK)}) has its whole interval above ${fx(V.lost_ci_lo_min_ratio)}× in both columns at both sizes; the smallest interval start is ${lr(SM.lost_ci_lo_min)}×. ` : '',
    `Placement-sensitive cells are listed separately and not judged: ${joinAnd(SM.placement_sensitive.map((q) => cellName(q.cell_id)))}.`,
    psAbove.length ? ` Counted, ${joinAnd(psAbove.map((q) => `${cellName(q.cell_id)} (${lr(q.aligned_ratio)}× aligned)`))} would also miss the limit.` : '',
    ` The rule file is the one the x86-64 pool used, byte for byte, so this core has neither a map nor a small cost everywhere under rules written before these runs (in the author’s unpublished development history).`);
  $('arm-line').textContent = V.line;
  // how firm the verdict is: the seed and interval-method readings, beside the stored verdict (which they do not replace)
  const SS = A.seed_sensitivity, DC = SS.deciding_cell, IM = A.interval_methods, mc = D.missed[0];
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const [fy, fm, fd] = SS.stored_seed.fixed_on.slice(0, 10).split('-').map(Number);
  const daysBefore = Math.round((Math.min(...t) - Date.parse(SS.stored_seed.fixed_on)) / 86400000);
  const mapOthers = IM.methods.filter((m) => m.form === 'map'), mapHi = mapOthers.map((m) => m.deciding_cell.ci95[1]);
  const steady = SS.derived.placement_sets.length === 1 && !SS.derived.lost_missed_any && SS.derived.positive_seen_in_all;
  const topWord = DC.stored_rank_from_top === 1 ? `the stored end is higher than all ${DC.alt_draws}` : `the stored end ranks ${DC.stored_rank_from_top} from the top of ${DC.alt_draws + 1}`;
  $('arm-seed').replaceChildren(el('b', null, 'How firm that is. '),
    `The form turns on one cell: ${cellName(mc.cell_id)}, aligned, ends at ${lr(DC.stored_hi)}× against the limit of ${fx(DC.limit)}×, a margin of ${DC.margin_over_limit.toFixed(4)}. That end is a bootstrap percentile and moves with the random seed. The pool’s seed (prefix ${SS.stored_seed.prefix}, ${num(SS.stored_seed.resamples)} resamples) was fixed on ${MONTHS[fm - 1]} ${fd}, about ${numWord(daysBefore)} days before the first Arm run, and the rule was applied as written, so the stored verdict stays ${form}. The date is in the unpublished development history, which the public repository cannot show. Three sensitivity readings sit beside it and replace nothing (seeds: `,
    repoNode(SS.script), ' writing ', repoNode(SS.source), '; interval methods: ', repoNode(IM.report), ', planned in ', repoNode(IM.plan), '):');
  $('arm-sens').replaceChildren(
    el('li', null, `The same interval re-drawn under ${DC.alt_draws} other seeds (same data, ${num(SS.alt_seeds.resamples)} resamples each) ends at a median of ${lr(DC.alt_hi.median)} (5th to 95th percentile ${lr(DC.alt_hi.p05)} to ${lr(DC.alt_hi.p95)}); ${DC.alt_at_or_above_limit} of the ${DC.alt_draws} end at or above the limit, and ${topWord}. With ${num(SS.converged_resamples)} resamples it ends at ${lr(DC.converged.hi)}${DC.converged.above_limit ? ', above' : ', under'} the limit.`),
    el('li', null, `The whole analysis re-run under ${SS.full.count} of those seeds gives a map in ${SS.full.forms.map || 0} of them; the verdict form derived from the re-drawn statistics for all ${SS.derived.seeds} is a map in ${SS.derived.forms.map || 0} and ${form} in ${SS.derived.forms.inconclusive || 0}${steady ? `, with the lost loops, the ${numWord(SS.derived.placement_sets[0].cells.length)} placement-sensitive cells and the positive control the same under every seed` : ''}.`),
    el('li', null, `${capFirst(numWord(mapOthers.length))} other interval methods (${mapOthers.map((m, i) => `${i && i === mapOthers.length - 1 ? 'and ' : ''}${m.name}`).join('; ')}) all give a map, the deciding cell ending between ${lr(Math.min(...mapHi))} and ${lr(Math.max(...mapHi))}; only the pool’s own bootstrap gives ${form}. They are a check on the interval, not a replacement for the written rule.`));
  $('arm-seed-end').textContent = `So these data cannot separate ${form} from a map at this cell. That is not evidence that the forward add costs more than ${V.forward_limit_pct}% at L2: its ratio is ${lr(mc.aligned.ratio)}× aligned, and an identical binary against itself spreads as widely at that size (below).`;
  // Table 12: every cell
  const ivc = (c) => (c ? el('td', { class: 'num' }, lr(c.ratio), el('span', { class: 'cell-iv' }, `${lr(c.ci95[0])} to ${lr(c.ci95[1])}`)) : el('td', { class: 'num' }, 'none'));
  const head1 = ['Loop and size', 'On Arm', 'Arm, as compiled', 'Arm, aligned', 'Instructions, as compiled', 'No-vectorize build', 'Layout A/A half-width', `${x86name}: SIMD`, `${x86name}, as compiled`, `${x86name}, aligned`];
  const numCol = new Set([2, 3, 4, 5, 6, 8, 9]);
  $('arm-t1-wrap').replaceChildren(el('table', { class: 'tbl dense arm-tbl', id: 'arm-t1', 'aria-describedby': 'arm-t1-cap' },
    el('thead', null, el('tr', null, ...head1.map((h, j) => el('th', { scope: 'col', class: numCol.has(j) ? 'num' : null }, h)))),
    el('tbody', null, ...A.cells.map((c) => {
      const x = D.x86(c.cell_id);
      return el('tr', null, el('th', { scope: 'row' }, `${KERNEL_NAMES[c.kernel]}, ${c.size_class}`, c.placement_sensitive ? el('span', { class: 'ps-mark', title: 'placement-sensitive', 'aria-label': 'placement-sensitive' }, ' ‡') : null),
        el('td', null, ARM_SHORT[c.class]), ivc(c.as_compiled), ivc(c.aligned), el('td', { class: 'num' }, lr(c.instr_ratio.as_compiled)), ivc(c.positive),
        el('td', { class: 'num' }, pctS(c.layout_aa.half_width_pct)), el('td', null, x ? ARM_SHORT[x.class] : 'none'), ivc(x && x.as_compiled), ivc(x && x.aligned));
    }))));
  setV('armT1Cap', `${A.cpu_short} (${A.jobs} jobs, ${A.runs.length} runs) beside ${x86name} (${A.x86.model.jobs} jobs of the ${A.x86.jobs}-job x86-64 pool): checks on ÷ checks off per loop and size, the pooled ratio with its 95% interval beneath. “Instructions” is the ratio of instructions executed (Cachegrind): ${A.instr_label}. “No-vectorize build” is the same loop built with vectorization off and no checks, against the checks-off build. “Layout A/A” is the half-width of the unchecked binary against itself rebuilt at a different loop alignment. ‡ marks a placement-sensitive cell, which the forward test leaves out. The ${x86name} columns repeat the pooled numbers behind Figure 1; its working sets have other byte sizes than the Arm ones.`);
  // forward loops
  const fwdPs = SM.placement_sensitive.filter((q) => A.forward_loops.kernels.includes(q.cell_id.split('.')[0]));
  const l2 = A.cells.filter((c) => A.forward_loops.kernels.includes(c.kernel) && c.size_class === 'L2');
  const fwdPredMiss = fwdPs.length > 0 && fwdPs.every((q) => { const p = D.kern(q.cell_id.split('.')[0]).prediction; return p.placement_effect === 'none' && p.placement_held === false; });
  const FI = A.forward_instr, fic = (id) => FI.cells.find((c) => c.cell_id === id);
  const sameAdd = Object.values(FI.added_same_at_both_sizes).every((v) => v.as_compiled && v.aligned); // the added instruction count per call is the same at L1 and L2
  const addA = fic('k02_add_fwd.L1'), addB = fic('k02_add_fwd.L2'), stenA = fic('k03_stencil.L1'), sumA = fic('k01_sum_fwd.L1');
  const iaa = A.noise.identical_binary_aa, aaL2 = iaa.L2.pooled;
  const flipSay = (c) => ((c.as_compiled.ratio - 1) * (c.aligned.ratio - 1) < 0 ? ' (it changes side of 1×, so no cost is claimed for it)' : '');
  $('arm-forward').replaceChildren(el('b', null, 'Forward loops. '),
    `At the L1 size the ${numWord(A.forward_loops.kernels.length)} forward loops cost ${lr(F1.as_compiled.min)}× to ${lr(F1.as_compiled.max)}× as compiled and ${lr(F1.aligned.min)}× to ${lr(F1.aligned.max)}× aligned (Table 12). `,
    sameAdd ? `Cachegrind counts the instructions the checks add to one call: ${sumA.as_compiled.added} for the sum, ${addA.as_compiled.added} (aligned ${addA.aligned.added}) for the add and ${stenA.as_compiled.added} (aligned ${stenA.aligned.added}) for the stencil, the same count at the L2 size. For the add that is an instruction ratio of ${addA.as_compiled.instr_ratio.toFixed(4)} at L1 (${num(addA.elements)} elements) and ${addB.as_compiled.instr_ratio.toFixed(4)} at L2 (${num(addB.elements)} elements), so the share of a call the checks take follows the array length; that these instructions are the time cost fits the counts and was not tested. ` : '',
    fwdPs.length ? `${capFirst(joinAnd(fwdPs.map((q) => `${cellName(q.cell_id)} (compiled ÷ aligned ${q.d.toFixed(3)})`)))} ${fwdPs.length === 1 ? 'is' : 'are'} placement-sensitive on this core${fwdPredMiss ? ', which the plan had predicted would not happen' : ''}; the rule leaves ${fwdPs.length === 1 ? 'that cell' : 'those cells'} out. The A/A floor of ${pctS(A.aa.half_width_pct)} is that of the forward add at L1 alone, and a byte-identical copy cannot see where a loop sits in memory, so for these the yardstick is the compiled ÷ aligned ratio: ${joinAnd(fwdPs.map((q) => { const c = D.cell(q.cell_id); return `${SHORT_NAMES[c.kernel]} ${lr(c.as_compiled.ratio)}× compiled and ${lr(c.aligned.ratio)}× aligned${flipSay(c)}`; }))}.` : '');
  // noise at the L2 size: the identical-binary A/A at L2 and the per-process mixture (descriptive; no cause is claimed)
  const NZ = A.noise, mix = NZ.mixture.by_size, sc = NZ.same_cell_l2, k4 = D.cell('k04_rev.L2'), k5 = D.cell('k05_stride2.L2');
  const sh = (x) => `${(x * 100).toFixed(1)}%`;
  $('arm-l2').replaceChildren(el('b', null, 'Noise at the L2 size. '),
    `The A/A control above is timed at the L1 size. The same byte-identical pair is also timed at L2, on the forward add. Pooled over ${iaa.L2.jobs} jobs it has a ratio of ${lr(aaL2.ratio)} with an interval of ${lr(aaL2.ci95[0])} to ${lr(aaL2.ci95[1])} (a half-width of ${pctS(aaL2.half_width_pct)}; per job the ratio runs from ${lr(iaa.L2.job_ratio_range[0])} to ${lr(iaa.L2.job_ratio_range[1])}), and ${iaa.L2.jobs_above_rule_max} of the ${iaa.L2.jobs} jobs are above the ${NZ.rule_aa_half_width_max_pct}% that the written rules allow an A/A (at L1: ${iaa.L1.jobs_above_rule_max}). That is as wide as the checked cell it sits beside (${pctS(sc.aligned.half_width_pct)} aligned, ${pctS(sc.as_compiled.half_width_pct)} as compiled) and as wide as the unchecked binary against its own re-aligned copy (${pctS(sc.layout_aa.half_width_pct)}). The forward cells at L2 are noisier than at L1: aligned intervals of ${joinAnd(l2.map((c) => `${lr(c.aligned.ci95[0])} to ${lr(c.aligned.ci95[1])}× (${SHORT_NAMES[c.kernel]})`))}. Of the judged forward cells only ${joinAnd(D.missed.map((c) => cellName(c.cell_id)))} misses the ${fx(V.limit)}× limit; its jobs’ own ratios run from ${lr(D.missed[0].aligned.per_job_range[0])}× to ${lr(D.missed[0].aligned.per_job_range[1])}× (a between-job standard deviation of ${D.missed[0].aligned.between_job_sd_pct.toFixed(2)}%, aligned; ${aaL2.between_job_sd_pct.toFixed(2)}% for an identical binary at that size), where no cell at L1 spreads by more than ${A.between_job_sd.l1_max_pct.toFixed(2)}%. So the width of the cell that decides the verdict is the width of L2 timing on this core, not a property of the check.`);
  $('arm-mix').replaceChildren(el('b', null, 'What the samples at L2 look like. '),
    `The cause was not examined and no hardware counter was read. What the samples show is that the process times at L2 are a mixture: a fast floor, and a share of processes that took more than ${Math.round(NZ.slow_share * 100)}% longer than the fastest process of their series. At L2 that share is ${sh(mix.L2.none.share_slow)} of the unchecked build’s processes and ${sh(mix.L2.fast.share_slow)} of the checked build’s (${sh(mix.L1.none.share_slow)} and ${sh(mix.L1.fast.share_slow)} at L1), and in a single cell it reaches ${Math.round(mix.L2.none.cell_share_max * 100)}% and ${Math.round(mix.L2.fast.cell_share_max * 100)}%. The L2 medians, including the lost loops’ ${lr(k4.as_compiled.ratio)}× and ${lr(k5.as_compiled.ratio)}× at that size (${SHORT_NAMES.k04_rev} and ${SHORT_NAMES.k05_stride2}, as compiled), are therefore less stable estimates than the L1 ones.`);
  // noise floors and run-to-run movement
  const rep = A.reproduction, lay = A.aa.layout_half_width_pct, jh = A.aa.job_half_width_pct, sd = A.between_job_sd;
  const layMax = A.cells.reduce((a, c) => (!a || c.layout_aa.half_width_pct > a.layout_aa.half_width_pct ? c : a), null);
  const worstMiss = rep.misses.reduce((a, m) => (!a || m.gap_pct > a.gap_pct ? m : a), null);
  const tiny = rep.misses.filter((m) => m.gap_pct < 0.01).length;
  const widest = (sz) => { let best = null; for (const c of A.cells) if (c.size_class === sz) for (const col of ['as_compiled', 'aligned']) { const h = c[col].half_width_pct; if (!best || h > best.h) best = { h, id: c.cell_id, col }; } return best; };
  const w1 = widest('L1'), w2 = widest('L2'), colSay = (c) => (c === 'aligned' ? 'aligned' : 'as compiled');
  $('arm-floors').replaceChildren(el('b', null, 'Noise floors and movement. '),
    `The A/A control (the unchecked binary against a byte-identical copy of itself) is timed on the forward add at the L1 size; pooled over ${A.aa.jobs} jobs, it has a half-width of ${pctS(A.aa.half_width_pct)}; per job it is ${pctS(jh.median)} at the median (${pctS(jh.min)} to ${pctS(jh.max)}). That is the floor of that one cell, not of the core: the widest interval of a measured cell is ±${pctS(w1.h)} at L1 (${cellName(w1.id)}, ${colSay(w1.col)}) and ±${pctS(w2.h)} at L2 (${cellName(w2.id)}, ${colSay(w2.col)}). The layout A/A (the unchecked binary against itself built at a different loop alignment) is less quiet: per cell its half-width runs from ${pctS(lay.min)} to ${pctS(lay.max)}, the largest at ${cellName(layMax.cell_id)}. `,
    `Between jobs, a cell’s ratio spreads by at most ${sd.l1_max_pct.toFixed(2)}% at L1 (${cellName(sd.l1_max_cell)}, ${sd.l1_max_column === 'aligned' ? 'aligned' : 'as compiled'}) and ${sd.l2_max_pct.toFixed(1)}% at L2 (${cellName(sd.l2_max_cell)}, ${sd.l2_max_column === 'aligned' ? 'aligned' : 'as compiled'}), as a standard deviation. `,
    `Run to run, ${rep.outside} of ${rep.checked} comparisons${(() => { const q = A.reproduction_calibration; return q && q.outside === rep.outside && q.checked === rep.checked ? ` (${q.expected_outside.toFixed(1)} expected for calibrated intervals)` : ''; })()} put one run’s pooled ratio outside another run’s interval, by at most ${rep.max_gap_pct.toFixed(1)}% (${cellName(worstMiss.cell_id)}); ${tiny} of them by less than 0.01%.`);
  // placement: what the layout A/A can and cannot see
  const LV = A.layout_vs_placement, lrow = (id) => LV.rows.find((r) => r.cell_id === id);
  const lst = lrow('k03_stencil.L1'), lga = lrow('k06_gather.L1'), lmm = lrow('k08_matmul.L1');
  const lside = (r) => `${lr(r.layout_aa.ratio)} against a D of ${lr(r.d.ratio)}${(r.layout_aa.ratio - 1) * (r.d.ratio - 1) < 0 ? ', which is on the other side of 1×' : ''}`;
  $('arm-layout').replaceChildren(el('b', null, 'Placement, and what the layout A/A can see. '), 'The layout A/A times the unchecked build against itself built with ', code(M.flags.align),
    `, so it moves only the unchecked build’s loops. The compiled ÷ aligned ratio (D in the data) moves both builds and is the placement control for the checked ÷ unchecked ratio. On this core the two disagree: at L1 the stencil has a layout A/A of ${lside(lst)}, gather ${lside(lga)}, and matrix multiply ${lside(lmm)}. At ${joinAnd(LV.d_excludes_1_layout_aa_includes_1.map(cellName))} the interval of D excludes 1 while that of the layout A/A does not. So a quiet layout A/A does not show that a cell is free of placement effects here. Whether 64-byte windows are the right unit on this core, and so whether the position of a loop against them explains the flagged cells, was not examined.`);
  // Table 13: what the compiler and the listings show
  const head2 = ['Loop', 'In the plan', 'Clang’s remark, checks on', 'NEON instructions, off → on', 'SIMD loop, off → on', 'Listing lines, off → on', 'Check traps, on'];
  const planWords = (k) => {
    const p = k.prediction;
    if (!p.class && !p.placement_effect) return 'no prediction';
    return [p.class ? `${p.class} (${p.class_held ? 'held' : 'did not hold'})` : '', p.placement_effect ? `${p.placement_effect === 'none' ? 'no placement effect' : p.placement_effect} (${p.placement_held ? 'held' : 'did not hold'})` : ''].filter(Boolean).join('; ');
  };
  $('arm-t2-wrap').replaceChildren(el('table', { class: 'tbl dense arm-tbl', id: 'arm-t2', 'aria-describedby': 'arm-t2-cap' },
    el('thead', null, el('tr', null, ...head2.map((h, j) => el('th', { scope: 'col', class: j >= 3 ? 'num' : null }, h)))),
    el('tbody', null, ...A.kernels.map((k) => {
      const n = k.builds.none, f = k.builds.fast, s = k.simd_loop.as_compiled;
      const remark = f.vectorized ? `vectorized, width ${f.width}, interleave ${f.interleave}` : (f.why_not_vectorized || 'not vectorized');
      const simdTxt = s.none_instructions == null ? 'none' : `${s.none_instructions} → ${s.fast_instructions == null ? 'none' : s.fast_instructions}${s.same_opcodes ? ', same opcodes' : ''}`;
      return el('tr', null, el('th', { scope: 'row' }, KERNEL_NAMES[k.kernel]), el('td', null, planWords(k)), el('td', null, remark),
        el('td', { class: 'num' }, `${n.neon_instructions} → ${f.neon_instructions}`), el('td', { class: 'num' }, simdTxt),
        el('td', { class: 'num' }, `${n.asm_lines} → ${f.asm_lines}`), el('td', { class: 'num' }, String(f.traps)));
    }))));
  setV('armT2Cap', `What the compiler and the listings show, per loop, as compiled. The counts come from the saved listings (the .s files) of one job; ${A.build_facts.all_agree ? `all ${A.build_facts.jobs} jobs produced identical hashes, listings, diffs and compiler remarks for every build` : 'the jobs do not all agree'}. “NEON instructions” counts them in the whole function; “SIMD loop” is the hot loop’s instruction count; a loop with no SIMD loop shows none. “Check traps” counts the trap instructions in the checked listing (a loop whose checks were proved away has none).`);
  armMatmul();
  // reverse loop: the no-vectorize control
  const rv = D.cell('k04_rev.L1');
  $('arm-novec').replaceChildren(el('b', null, 'The no-vectorize control. '),
    `Switching vectorization off by hand, with no checks, costs ${lr(rv.positive.ratio)}× at the reverse loop’s L1 size, against ${lr(rv.as_compiled.ratio)}× with the checks on: about ${Math.round(SM.novec_rev_share_pct)}% of the checked build’s extra time is the lost SIMD, and the rest is the compare and branch on each element (inferred). `,
    `The same control costs ${lr(Math.min(...A.cells.filter((c) => c.positive).map((c) => c.positive.ratio)))}× to ${lr(Math.max(...A.cells.filter((c) => c.positive).map((c) => c.positive.ratio)))}× across the ${A.cells.filter((c) => c.positive).length} cells of the loops that are vectorized without the checks (Table 12).`);
  // against the plan
  const pred = A.kernels.filter((k) => k.prediction.class), heldC = pred.filter((k) => k.prediction.class_held);
  const plc = A.kernels.filter((k) => k.prediction.placement_effect), plHeld = plc.filter((k) => k.prediction.placement_held), plMiss = plc.filter((k) => !k.prediction.placement_held);
  const noPred = A.kernels.filter((k) => !k.prediction.class), offc = (k) => D.cell(`${k.kernel}.L1`).as_compiled.ratio;
  const seen = (k) => ARM_SMOKE_SEEN.includes(k.kernel), blindP = pred.filter((k) => !seen(k)), blindHeld = blindP.filter((k) => k.prediction.class_held);
  $('arm-plan').replaceChildren(el('b', null, 'Against the plan. '), repoNode(A.plan),
    ` was committed after a two-kernel smoke run and before the full runs had finished, by commit times in the author’s unpublished development history. It named the class of ${pred.length} loops, and ${heldC.length} of ${pred.length} held (${names(pred.filter((k) => k.class === 'lost').map((k) => k.kernel))} lost; ${names(pred.filter((k) => k.class === 'kept').map((k) => k.kernel))} kept). Not all of those were blind: the smoke run had already timed ${names(ARM_SMOKE_SEEN)} on this core (the plan quotes both figures), so those ${numWord(pred.filter(seen).length)} predictions were made with the result in view, and ${blindHeld.length} of the ${blindP.length} others held. It predicted no placement effect for the forward loops: ${plHeld.length ? `${names(plHeld.map((k) => k.kernel))} held` : 'none held'}${plMiss.length ? `, ${names(plMiss.map((k) => k.kernel))} did not (flagged placement-sensitive at L1)` : ''}${plc.some(seen) ? `; ${names(plc.filter(seen).map((k) => k.kernel))} had been timed in the smoke run when that was written` : ''}. It made no prediction for ${names(noPred.map((k) => k.kernel))}, which cost ${joinAnd(noPred.map((k) => `${fx(offc(k))}×`))} at L1, as compiled.`);
  // limits
  const flags = Object.entries(M.isa_flags).filter(([, v]) => v).map(([f]) => f);
  $('arm-limits').replaceChildren(el('b', null, 'Limits. '),
    `One core type (${M.cpu_model}), one runner image (${M.os}, kernel ${M.kernel}), virtual machines whose neighbours are unknown, ${A.jobs} jobs in ${A.runs.length} runs from one day. ${capFirst(clang)} and ${libcxx} only${M.march_flag_in_builds ? '' : ', with no -march flag, so the builds target the compiler’s default Arm baseline'}${flags.includes('sve') ? ' (the cores also report SVE and SVE2, which these builds did not target)' : ''}. `,
    'No real programs, no profile-guided builds and no other compilers or libc++ versions were timed on Arm, and no steal or frequency record was made for these runs. The placement fields in the data (64-byte windows) were defined for x86-64 fetch windows and are computed for Arm without a check of what an Arm core fetches, and the layout A/A moves only the unchecked build’s loops, so it did not see placement shifts that the compiled ÷ aligned ratio shows (above): neither is a verified placement control on this core. ',
    'This says nothing about Apple, AWS or other Arm cores, about other Arm compilers, or about Google’s services.');
}
function armMatmul() { // the matrix-multiply paragraph of section 6d; it names the row-length sweep once data/dsweep.json is in
  if (!has('arm-matmul') || !S.arm || !S.arm.cells) return;
  const D = armData(), A = D.A, M = A.machine, x86name = A.x86.model.cpu_short, mcs = A.matmul_cost.sizes;
  const mk = D.kern('k08_matmul'), m1 = D.cell('k08_matmul.L1'), m2 = D.cell('k08_matmul.L2'), x1 = D.x86('k08_matmul.L1'), x2 = D.x86('k08_matmul.L2');
  const ms = mk.simd_loop.as_compiled, mb = mk.builds, mcL1 = mcs.L1, mcL2 = mcs.L2;
  const diffPath = `${mk.source_job}/asm/${mk.diffs.L1.file}`, fastPath = `${mk.source_job}/asm/${mk.kernel}.fast.s`;
  const gaL1 = D.cell('k06_gather.L1'), gaL2 = D.cell('k06_gather.L2');
  const ds = S.ds && S.ds.models.find((m) => m.cpu_short === A.cpu_short && dsWord(m)); // the sweep, once it has loaded
  $('arm-matmul').replaceChildren(el('b', null, 'Matrix multiply. '),
    mk.class === 'kept' && x1 && x1.class === 'lost'
      ? `Clang vectorized it in both builds on this core (its remark with the checks on: “${mb.fast.remarks[0].replace(/\s*\[-R[^\]]*\]$/, '')}”), and the SIMD loop in the listing is the same ${ms.fast_instructions} instructions with ${ms.same_opcodes ? 'the same opcodes' : 'different opcodes'} with the checks off and on. The function still costs ${lr(m1.as_compiled.ratio)}× at L1 as compiled (${lr(m1.aligned.ratio)}× aligned) and ${lr(m2.as_compiled.ratio)}× at L2 (${lr(m2.aligned.ratio)}× aligned), and both cells are placement-sensitive (compiled ÷ aligned ${m1.placement.d.ratio.toFixed(3)} and ${m2.placement.d.ratio.toFixed(3)}). On ${x86name} clang 18 loses SIMD on the same loop, at ${fx(x1.as_compiled.ratio)}× and ${fx(x2.as_compiled.ratio)}×. `
      : `It costs ${lr(m1.as_compiled.ratio)}× at L1 as compiled and ${lr(m2.as_compiled.ratio)}× at L2 on this core. `,
    'Observed in the checked build’s full listing (', repoNode(fastPath, 'the .s file'), ') and its L1 diff (', repoNode(diffPath, 'the diff'), `): the checked function is ${mb.fast.asm_lines} lines against ${mb.none.asm_lines}; the SIMD loop has the same ${ms.fast_instructions} instructions with ${ms.same_opcodes ? 'the same opcodes' : 'different opcodes'} in both builds; the extra lines are compare, select-minimum and branch instructions before the SIMD loop and, after it, a scalar loop with two compare-and-branch pairs per element. The conditional branches into the function’s one trap, `, code('brk #0x1'), `, sit before the SIMD loop and in the scalar loop, none inside the SIMD loop. The diff drops those jump targets, so they are read from the full listing. `,
    `The checked build executes ${lr(m1.instr_ratio.as_compiled)}× the instructions at L1 (Cachegrind) for ${lr(m1.as_compiled.ratio)}× the time, and ${lr(m2.instr_ratio.as_compiled)}× the instructions at L2 for ${lr(m2.as_compiled.ratio)}× the time. That the extra time comes from this surrounding code and not from the SIMD loop fits the listing and the counts at L1; ${ds ? `the row-length sweep at the end of this section tests whether the extra time per inner call is fixed, and its word is “${ds.word}”` : 'it was not tested'}. Between the two sizes three things change together: the cache level, the row length (d = ${mcL1.d} at L1 and d = ${mcL2.d} at L2, so the SIMD loop runs ${mcL1.whole_passes} and ${mcL2.whole_passes} passes of ${A.matmul_cost.vector_pass_elements} elements per row and the scalar loop is left ${mcL1.d_mod_pass} and ${mcL2.d_mod_pass}) and the instruction ratio. A change of cache level can move the time without moving the instruction ratio: the gather loop executes ${lr(gaL1.instr_ratio.as_compiled)}× and ${lr(gaL2.instr_ratio.as_compiled)}× the instructions at the two sizes but costs ${lr(gaL1.as_compiled.ratio)}× and ${lr(gaL2.as_compiled.ratio)}×. So these two sizes alone do not say whether the row length, the cache level or both is why matrix multiply costs so much less at L2; ${ds ? 'the row-length sweep times other d' : 'no other d was timed'}. Nothing here times the SIMD loop alone or profiles where the time goes, and these virtual machines expose no hardware counters. The plan expected matrix multiply not to be lost on this target, from the compile-only sweep; why the target matters is not established here.`);
}
function renderArm() {
  if (!S.arm || !S.arm.cells) return;
  armTexts();
  armFigure();
  armDetails();
  updateScrollHints();
}
function renderHoldout() {
  const H = S.ho;
  const judged = H.rows.filter((r) => r.reproduced != null);
  const same = judged.filter((r) => r.reproduced), diff = judged.filter((r) => !r.reproduced);
  const when = H.preregistration_committed_utc ? H.preregistration_committed_utc.replace('T', ' ').replace('Z', ' UTC') : 'before the runs';
  const formName = (f) => (f === 'map' ? 'Map' : f === 'inconclusive' ? 'Inconclusive' : f);
  const cell = (d) => (d ? `${formName(d.form)} (${d.jobs} job${d.jobs === 1 ? '' : 's'}${d.runs !== 3 ? `, ${d.runs} run${d.runs === 1 ? '' : 's'}` : ''})` : 'not drawn');
  const lost = (d) => (d && d.lost && d.enough ? `${rangeX(d.lost.min, d.lost.max)}, median ${fx(d.lost.median)}×` : 'none given');
  // Table 1 pools every run so far, the holdout compares only the first pooled runs with the fresh ones: say where a model stands now
  const now = (r) => { const c = S.ix.cpus.find((x) => x.cpu_short === r.cpu_short); return c ? `Table 1, which pools every run so far, now has ${c.jobs} jobs of it${c.enough ? ` and reads ${formWords(c.form)}` : ''}` : ''; };
  setV('holdoutShort', `A fresh holdout run: same pattern on ${joinAnd(same.map((r) => r.cpu_short))}${diff.length ? `, not on ${joinAnd(diff.map((r) => r.cpu_short))}` : ''}`);
  const gap = H.first_job_start_utc && H.preregistration_committed_utc ? Math.round((Date.parse(H.preregistration_committed_utc) - Date.parse(H.first_job_start_utc)) / 1000) : null;
  const first = H.first_job_start_utc ? H.first_job_start_utc.replace('T', ' ').replace('Z', ' UTC') : null;
  const order = gap == null ? 'The plan for this run was committed before the runs, in the author’s unpublished development history.'
    : `The plan for this run (PREREGISTRATION.md) carries the commit time ${when}, from the author’s clock in unpublished development history; that is ${gap} second${gap === 1 ? '' : 's'} ${gap >= 0 ? 'after' : 'before'} the start of the first job it governs (${first}), so the records do not show which came first. The file lists the ${numWord(H.runs.length)} run IDs, so the commit that holds this version came after those runs were created.`;
  setV('holdoutText', `${order} What can be checked is that all ${H.jobs_with_rule_hash} of the ${H.jobs} jobs record the sha256 of the rule file as it is in this repository${H.jobs_with_rule_hash === H.jobs ? '' : ' (not all do)'}; nothing in the records shows that the pooling code (harness/pool.py) was unchanged. ${capFirst(numWord(H.runs.length))} fresh runs (${H.jobs} jobs) were pooled as the first runs were. Same pattern on ${joinAnd(same.map((r) => r.cpu_short))}, with nearly the same numbers. ${diff.map((r) => `${r.cpu_short} did not reproduce as a pattern: ${cell(r.holdout).toLowerCase()} against ${cell(r.original).toLowerCase()} the first time; it had only ${r.holdout.jobs} jobs, and was already marked fragile (${now(r)})`).join('; ')}${diff.length ? '. ' : ''}${H.rows.filter((r) => r.reproduced == null).map((r) => `${r.cpu_short} drew too few jobs both times (${r.original ? r.original.jobs : 0} and ${r.holdout ? r.holdout.jobs : 0}), so nothing is said about it (${now(r)})`).join('; ')}. Nothing here tests another toolchain.`);
  $('holdout-table').querySelector('tbody').replaceChildren(...H.rows.map((r) => el('tr', null,
    el('th', { scope: 'row' }, r.cpu_short), el('td', null, cell(r.original)), el('td', null, cell(r.holdout)),
    el('td', { class: 'num' }, `${lost(r.original)} → ${lost(r.holdout)}`),
    el('td', null, r.reproduced == null ? 'no verdict either time' : r.reproduced ? 'yes' : 'no'))));
  setV('holdoutCap', `Table H. The first pooled runs against the holdout, per CPU model: verdict, jobs and the cost of the loops that lose SIMD in cache (aligned). Source: ${H.source} and ${H.original_source}; plan: ${H.preregistration}.`);
}
/* ---------- the replication: Figure 8 (main page, section 1) and its full account (details page, section 1), read from data/replication.json ---------- */
const REP_RED = ['39012986182', '39013000285']; // the two combine runs that went red on harness/pool_check.py (a model with fewer than 3 jobs); they must be runs of the second x86-64 set
const REP_SAY = { none: 'not drawn', few: 'too few jobs', map: 'a map', holds: 'a small cost everywhere', inc: 'inconclusive' };
const repKind = (s) => (!s || !s.jobs ? 'none' : !s.enough ? 'few' : s.form === 'map' ? 'map' : s.form === 'holds_everywhere' ? 'holds' : 'inc');
const repJobs = (n) => `${n} job${n === 1 ? '' : 's'}`;
const repWith = (s) => `${REP_SAY[repKind(s)]} (${repJobs(s ? s.jobs : 0)})`;
const d3 = (v) => v.toFixed(3), d4 = (v) => v.toFixed(4);
const repShown = () => S.rep.rows.filter((r) => r.earlier && r.earlier.enough); // the models with a verdict in the first set
// Figure 8 (main page) calls the two sets "first" and "second" everywhere; set A, B and C belong to Table 14 on the details page
const REP_SETS = { earlier: 'the first set', replication: 'the second set', secondary: 'both together' };
const repShort = (m) => { const r = S.rep.rows.find((x) => x.cpu_model === m); return r ? r.cpu_short : m; };
function repAligned(r) { // the plan counts aligned ratios; the stored count has both columns, so a model's cells are half of its points
  const cells = r.inside.checked / 2;
  return { n: cells - r.inside.misses.filter((m) => m.column === 'aligned').length, of: cells };
}
function repRole(x) { // what the placement exemption did to one forward cell in one pool
  const P = x.placement, ci = `${d3(P.d_ci95[0])} to ${d3(P.d_ci95[1])}`;
  return x.role === 'exempt_placement_sensitive'
    ? `left out of the forward test as placement-sensitive (compiled ÷ aligned ${ci}, which excludes 1 by ${d4(P.d_misses_one_by)})`
    : `judged (compiled ÷ aligned ${ci}, which includes 1)${x.passes_forward_rule === false ? `, and it misses the ${fx(x.limit)}× limit by ${d4(x.aligned_hi_over_limit)}` : ''}`;
}
function repFlip(arch, slug, names) { // the cell(s) behind a model's different word, in words; the main page passes REP_SETS, the details page the real set names
  const A = S.rep.arch[arch], f = A.flips.find((x) => x.slug === slug), nm = names || A.names;
  if (!f) return '';
  return f.cells.map((c) => `${capFirst(cellName(c.cell_id))}, aligned: ${d3(c.earlier.aligned.ratio)}× in ${nm.earlier} and ${d3(c.replication.aligned.ratio)}× in ${nm.replication}; its interval ends at ${d4(c.earlier.aligned.ci95[1])} and ${d4(c.replication.aligned.ci95[1])}, against the ${fx(c.earlier.limit)}× limit. In ${nm.earlier} it is ${repRole(c.earlier)}; in ${nm.replication} it is ${repRole(c.replication)}.`).join(' ');
}
const repEdge = (r) => { const f = S.rep.arch[r.arch].flips.find((x) => x.slug === r.slug); return !!f && f.cells.every((c) => c.earlier.role !== c.replication.role); }; // a different word that comes from the placement exemption switching, not from a new cost
function repTitleText() { // the word counts over the models that could be tested in both sets; a flip is named for what it is only when the data show the exemption switching
  const rows = repShown().filter((r) => r.testable), n = (st) => rows.filter((r) => r.status === st);
  const flipped = n('flipped'), edge = flipped.length > 0 && flipped.every(repEdge);
  return `Second set: same word on ${n('same').length} of ${rows.length} models${flipped.length ? `; ${flipped.length} ${edge ? 'flipped at a rule’s edge' : 'changed word'}` : ''}`;
}
function repGlyph(s) { return el('span', { class: `rg g-${repKind(s)}`, 'aria-hidden': 'true' }, el('i'), el('b', null, s && s.jobs ? String(s.jobs) : '–')); }
function repRenderRows() {
  const rows = repShown();
  const out = rows.map((r) => {
    const nm = REP_SETS, I = r.inside;
    const firstOfArch = r === rows.find((x) => x.arch === r.arch);
    const b = el('button', { type: 'button', class: `row rep-row st-${r.status.replace(/\W+/g, '-')}${firstOfArch && r.arch !== rows[0].arch ? ' rep-gap' : ''}`, role: 'option', 'data-slug': r.slug, 'aria-selected': 'false' });
    b.addEventListener('click', () => repSelect(S.repSel === r.slug ? null : r.slug, false));
    b.append(el('span', { class: 'lab' }, el('span', { class: 'name' }, r.cpu_short)), repGlyph(r.earlier), repGlyph(r.replication), repGlyph(r.secondary),
      I ? el('span', { class: 'rin', title: `${I.inside} of ${I.checked} pooled ratios of ${nm.replication} lie inside the 95% interval of ${nm.earlier}` },
        el('span', { class: 'rbar' }, el('i', { style: `width:${(100 * I.inside / I.checked).toFixed(1)}%` })), el('span', { class: 'rn' }, `${I.inside}/${I.checked}`))
        : el('span', { class: 'rin', title: 'not testable: too few jobs in the second set' }, el('span', { class: 'rn na' }, '–')));
    b.setAttribute('aria-label', `${r.cpu_short}: ${nm.earlier}: ${repWith(r.earlier)}; ${nm.replication}: ${repWith(r.replication)}; ${nm.secondary}: ${repWith(r.secondary)}; ${I ? `${I.inside} of ${I.checked} pooled ratios of the second set inside the first set’s interval` : 'not testable'}`);
    return b;
  });
  $('rep-rows').replaceChildren(...out);
  repMark();
}
function repMark() {
  const first = $('rep-rows').firstElementChild;
  for (const b of $('rep-rows').children) {
    const on = b.dataset.slug === S.repSel;
    b.setAttribute('aria-selected', on ? 'true' : 'false');
    b.tabIndex = on || (!S.repSel && b === first) ? 0 : -1;
  }
}
function repSelect(slug, focus) {
  S.repSel = slug;
  repMark();
  repRead();
  if (focus && slug) { const b = $('rep-rows').querySelector(`[data-slug="${slug}"]`); if (b) b.focus(); }
}
function repRead() {
  const box = $('rep-read'), r = S.rep.rows.find((x) => x.slug === S.repSel);
  if (!r) { box.hidden = true; box.replaceChildren(); return; }
  const nm = REP_SETS, I = r.inside, X = S.rep.arch[r.arch];
  const notes = [];
  if (I) {
    const al = repAligned(r);
    notes.push(`${I.inside} of ${I.checked} pooled ratios of ${nm.replication} lie inside the 95% interval of ${nm.earlier} (aligned alone ${al.n} of ${al.of}); the largest difference between two ratios is ${pctS(I.max_abs_point_diff_pct)}.`);
  }
  if (r.status === 'flipped') notes.push(`The different word is a placement-exemption edge, not a change of cost. ${repFlip(r.arch, r.slug, nm)}`);
  if (!r.testable) notes.push(`${capFirst(nm.replication)} drew ${repJobs(r.replication ? r.replication.jobs : 0)} of it (${S.rep.criteria.minimum_jobs} are needed), so whether the first reading repeats is not answered either way. Pooled with it, the ${repJobs(r.secondary ? r.secondary.jobs : 0)} (${r.earlier.jobs} of ${nm.earlier} and ${r.replication ? r.replication.jobs : 0} of ${nm.replication}) read ${REP_SAY[repKind(r.secondary)]}.`);
  if (r.arch === 'arm') {
    const c = X.named_cells[0], below = c.earlier.aligned.ratio < 1 && c.replication.aligned.ratio < 1;
    notes.push([`Both sets are decided by one cell, ${cellName(c.cell_id)}, aligned: it ends at ${d4(c.earlier.aligned.ci95[1])} in ${nm.earlier} and ${d4(c.replication.aligned.ci95[1])} in ${nm.replication}, against the ${fx(c.earlier.limit)}× limit, with ratios of ${d3(c.earlier.aligned.ratio)} and ${d3(c.replication.aligned.ratio)}. Pooled (${nm.secondary}) it ends at ${d4(c.secondary.aligned.ci95[1])}: the ratio is about the same, the interval narrower. Both ends sit near the limit${below ? ' while both ratios are below 1' : ''}, so a second inconclusive is a weak repeat of the word, not independent confirmation of an effect (`,
      el('a', { href: '#arm' }, 'section 6a'), ').']);
  }
  box.hidden = false;
  box.replaceChildren(el('p', { class: 'rp-head' }, el('b', null, r.cpu_short), ` ${capFirst(nm.earlier)}: ${repWith(r.earlier)}; ${nm.replication}: ${repWith(r.replication)}; ${nm.secondary}: ${repWith(r.secondary)}.`),
    ...notes.map((t) => el('p', { class: 'rp-note' }, t)));
}
function repCaption() {
  const rows = repShown(), I = rows.find((r) => r.inside).inside;
  const key = (k, t) => el('span', { class: 'rk' }, el('span', { class: `rg g-${k}`, 'aria-hidden': 'true' }, el('i')), ` ${t}`);
  $('rep-key').replaceChildren(key('map', 'map'), key('inc', 'inconclusive'), key('few', 'too few jobs'), el('span', { class: 'rk' }, 'n = jobs'));
  $('rep-cap').replaceChildren(el('b', null, 'Figure 8.'),
    ` A set is one batch of runs. Inside: of ${I.checked} pooled ratios, those of the second set in the first set’s 95% interval (`,
    el('a', { href: 'details.html#rep-t-cap' }, 'Table 14'), '). “Both” is secondary.');
}
function repFigure() {
  if (!has('rep-rows')) return;
  S.repSel = S.repSel || null;
  $('rep-title').textContent = repTitleText();
  repRenderRows();
  repCaption();
  repRead();
  $('rep-rows').addEventListener('keydown', (e) => {
    if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(e.key) || !e.target.closest || !e.target.closest('.rep-row')) return;
    e.preventDefault();
    const order = repShown().map((r) => r.slug);
    let i = order.indexOf(e.target.closest('.rep-row').dataset.slug); // from the row that has focus
    if (e.key === 'ArrowDown') i = Math.min(order.length - 1, i + 1);
    if (e.key === 'ArrowUp') i = Math.max(0, i - 1);
    if (e.key === 'Home') i = 0;
    if (e.key === 'End') i = order.length - 1;
    repSelect(order[i], true);
  });
}
/* the details page: the plan, the count, one paragraph per story, Table 14, the limits */
function repDetails() {
  if (!has('replication-full')) return;
  const R = S.rep, X = R.arch.x86, AR = R.arch.arm, P = R.pools, Q = R.questions, arm = AR.named_cells[0];
  const q6 = Q.xeon_6973pc, rows = R.rows, byS = (s) => rows.find((r) => r.slug === s);
  const drawn = (o) => joinAnd(Object.entries(o).sort((a, b) => b[1] - a[1]).map(([m, n]) => `${repShort(m)} ${n}`));
  const thin = Math.max(q6.earlier_closest_forward.margin, arm.earlier.aligned_hi_over_limit), red = REP_RED.filter((id) => P.x86.replication.run_ids.includes(id));
  $('rep-what').replaceChildren(el('b', null, 'Why a second set, and how it is read. '),
    `Two readings rested on a forward cell whose interval ended within ${d4(thin)} of the limit, the Arm core’s and the Xeon 6973P-C’s, so more runs were requested. The plan (`, repoNode(R.plan), `) was committed in the author’s unpublished development history, by the author’s account before the runs were dispatched, and this repository cannot show that order: ${provReplication()} The hash stored with the comparison shows the file’s integrity, not when it was written. It fixes the reading: each set is pooled on its own, by the same code under the same rule file (`, code(R.criteria.file),
    `), and for each cell it asks whether the second set’s pooled aligned ratio lies inside the first set’s 95% interval, reported as a share, whatever comes out. The rule file was not changed after a result (every record stores its hash), and by the author’s account neither were the pooling code and the statistics; one consistency check (`, repoNode('harness/pool_check.py'),
    `) was changed afterwards to sample only models with at least ${R.criteria.minimum_jobs} jobs, after ${numWord(red.length)} combine runs (${joinAnd(red)}) went red on it for models with fewer, and no verdict uses such a model. ${capFirst(X.names.replication)} is ${P.x86.replication.run_ids.length} more x86-64 runs (${P.x86.replication.jobs} jobs), drawn by GitHub from the same pool of machines; ${AR.names.replication} is ${P.arm.replication.run_ids.length} more Arm runs (${P.arm.replication.jobs} jobs). The pooled forms of the two sets together are secondary: the sets were requested after a borderline reading, so the stopping point depended on the data, and they never replace a set read alone. The earlier pools’ stored verdicts are unchanged. No further runs will be made for these questions.`);
  const al = (a) => rows.filter((r) => r.arch === a && r.inside).reduce((t, r) => { const x = repAligned(r); return [t[0] + x.n, t[1] + x.of]; }, [0, 0]);
  const alX = al('x86'), alA = al('arm'), cellsN = rows.find((r) => r.inside).inside.checked / 2;
  $('rep-count').replaceChildren(el('b', null, 'How points are counted. '),
    `The plan asks whether each cell’s pooled aligned ratio lies inside the earlier interval. The stored count compares both columns, as compiled and aligned, with the earlier pool’s 95% interval: the point-inside-interval test of `, repoNode('harness/pool.py'), `, which this page also uses to compare one run with another. The both-column form was written into `, repoNode('replication/compare.py'),
    ` after the sets’ data were in, so a model has ${cellsN} cells and ${2 * cellsN} points. Counted on the aligned column alone, as the plan asked: Arm ${alA[0]} of ${alA[1]}, x86-64 ${alX[0]} of ${alX[1]}. The count is descriptive: a second set’s pooled ratio carries its own noise, so fewer than 95% of its points are expected inside the first set’s interval even when nothing has changed, and the share mostly follows interval width and set size; no expected count is claimed. ${AR.totals.point_diff_under_1pct} of ${AR.totals.points_checked} Arm points and ${X.totals.point_diff_under_1pct} of ${X.totals.points_checked} x86-64 points differ from the earlier pooled ratio by under 1%, and the largest differences are ${pctS(AR.totals.max_abs_point_diff_pct)} (Arm) and ${pctS(X.totals.max_abs_point_diff_pct)} (x86-64).`);
  const sameN = rows.filter((r) => r.arch === 'x86' && r.status === 'same').map((r) => r.cpu_short), flipN = rows.filter((r) => r.arch === 'x86' && r.status === 'flipped').map((r) => r.cpu_short);
  $('rep-x86').replaceChildren(el('b', null, 'x86-64, set C. '),
    `${P.x86.replication.jobs} jobs drew ${drawn(P.x86.replication.models_drawn)}. Of the ${numWord(X.totals.testable_models)} models with at least ${R.criteria.minimum_jobs} jobs in both sets, ${numWord(X.totals.same_form)} gave the same verdict word (${joinAnd(sameN)}) and ${numWord(X.totals.flipped)} a different one (${joinAnd(flipN)}). ${X.totals.points_inside} of ${X.totals.points_checked} pooled ratios lie inside the first pool’s interval.`);
  $('rep-flips').replaceChildren(el('b', null, 'The two different words are one edge, not a change of cost. '),
    `The placement test leaves a forward cell out of the 2% test when its compiled ÷ aligned interval excludes 1 and its hot loop sits differently in the two as-compiled builds, and judges it otherwise. ${X.flips.map((f) => `${f.cpu_short}: ${repFlip('x86', f.slug)}`).join(' ')} Neither cell’s cost changed between the sets; the model’s word depends on which side of the test the cell lands.`);
  const ps = (s) => (s.placement_sensitive || []).map((id) => cellName(id));
  const missed = (q6.secondary_cause.forward_missed || [])[0];
  const r6 = byS(q6.slug);
  $('rep-6973').replaceChildren(el('b', null, `${q6.cpu_short} cannot be tested. `),
    `${capFirst(X.names.replication)} drew ${repJobs(q6.replication_jobs)} of it (${q6.minimum_jobs} are needed), so it has no verdict there, and the question the plan asked of it, whether its borderline ${REP_SAY[repKind(r6.earlier)].replace(/^a /, '')} repeats, is not answered either way. In ${X.names.earlier} (${q6.earlier_jobs} jobs) it is ${REP_SAY[repKind(r6.earlier)]}, with ${cellName(q6.earlier_closest_forward.cell_id)} ending nearest the limit, at ${d4(q6.earlier_closest_forward.aligned_hi)}. Pooled with ${X.names.replication}’s ${repJobs(q6.replication_jobs)} (${q6.secondary_jobs} jobs) it reads ${REP_SAY[repKind(r6.secondary)]}`,
    missed ? `: ${cellName(missed.cell_id)} ends at ${d4(missed.aligned_ci95[1])}${r6.earlier.placement_sensitive.includes(missed.cell_id) && !r6.secondary.placement_sensitive.includes(missed.cell_id) ? ', a cell that was placement-sensitive, and so left out, in the first pool and is judged with the extra job' : ''}. ` : '. ',
    'That pooled word is secondary and rests on this one added job.');
  const sets = AR.names, rN2 = rows.find((r) => r.arch === 'arm' && r.testable), v3 = rows.find((r) => r.arch === 'arm' && !r.earlier);
  $('rep-arm').replaceChildren(el('b', null, 'Arm. '),
    `${capFirst(sets.replication)} is ${P.arm.replication.jobs} jobs: ${drawn(P.arm.replication.models_drawn)}${v3 ? `; the ${v3.cpu_short} job has no verdict` : ''}. Read alone it is ${REP_SAY[repKind(rN2.replication)]}${Q.arm_cell.repeated ? `, as ${sets.earlier} was${Q.arm_cell.replication_names_the_same_cells ? ', and on the same cell that decided the first reading' : ''}` : `, where ${sets.earlier} was ${REP_SAY[repKind(rN2.earlier)]}`}: ${cellName(arm.cell_id)}, aligned, ends at ${d4(arm.replication.aligned.ci95[1])} in ${sets.replication} and at ${d4(arm.earlier.aligned.ci95[1])} in ${sets.earlier}, against the ${fx(arm.earlier.limit)}× limit, with ratios below 1 (${d3(arm.replication.aligned.ratio)} and ${d3(arm.earlier.aligned.ratio)}). ${capFirst(sets.secondary)} pooled (${rN2.secondary.jobs} ${rN2.cpu_short} jobs) read ${REP_SAY[repKind(rN2.secondary)]}, the cell ending at ${d4(arm.secondary.aligned.ci95[1])} with a ratio of ${d3(arm.secondary.aligned.ratio)}: the ratio is about the same in all three, and only the interval narrows with more jobs. That pooled word is secondary.`);
  const H = X.headline, okE = H.replication_enough_range, rep = H.replication.filter((m) => m.enough).map((m) => m.cpu_short);
  $('rep-headline').replaceChildren(el('b', null, 'The headline range. '),
    `The loops that lose SIMD cost ${H.page_range.printed_min}× to ${H.page_range.printed_max}× in cache on the first pool. In ${X.names.replication}, the ${numWord(rep.length)} models with at least ${R.criteria.minimum_jobs} jobs (${joinAnd(rep)}) give ${d3(okE.min)}× to ${d3(okE.max)}× (both columns, both sizes)${H.outside_stored_range.length ? `; the cell furthest below the first pool’s minimum (${d4(H.page_range.min)}×) is ${cellName(H.outside_stored_range[0].cell_id)} of ${repShort(H.outside_stored_range[0].cpu_model)}, ${H.outside_stored_range[0].column === 'aligned' ? 'aligned' : 'as compiled'}, at ${d4(H.outside_stored_range[0].ratio)}×` : ''}. ${H.outside_printed_range.length ? 'Some cells lie outside the printed range.' : `Nothing in set C lies outside the printed ${H.page_range.printed_min}× to ${H.page_range.printed_max}×.`}`);
  setV('repCap', `Per CPU model: the verdict word and job count in the first set, the second set and both together (secondary), how many of the model’s ${2 * cellsN} pooled ratios (both columns) lie inside the first set’s 95% interval (aligned alone in brackets), and the largest difference between a first-set and a second-set ratio. x86-64: the first set is the ${P.x86.earlier.jobs}-job pool, the second set is set C; Arm: set A and set B, ${P.arm.earlier.jobs} jobs each. A model with fewer than ${R.criteria.minimum_jobs} jobs in a set has no verdict there.`);
  const cell = (s) => (s ? `${REP_SAY[repKind(s)]}, ${repJobs(s.jobs)}` : 'not drawn');
  $('rep-table').querySelector('tbody').replaceChildren(...rows.map((r) => {
    const I = r.inside, a = I ? repAligned(r) : null;
    return el('tr', { class: I ? null : 'muted-row' }, el('th', { scope: 'row' }, r.cpu_short), el('td', null, cell(r.earlier)), el('td', null, cell(r.replication)), el('td', null, cell(r.secondary)),
      el('td', { class: 'num' }, I ? `${I.inside} of ${I.checked} (${a.n} of ${a.of})` : '–'), el('td', { class: 'num' }, I ? pctS(I.max_abs_point_diff_pct) : '–'),
      el('td', null, r.status === 'same' ? 'same word' : r.status === 'flipped' ? 'different word' : 'not testable'));
  }));
  $('rep-limits').replaceChildren(el('b', null, 'Limits. '),
    `The machines in each set are drawn by GitHub, not chosen, so the sets hold few jobs of the rarer models (${drawn(P.x86.replication.models_drawn)} in set C). Nothing here tests another compiler, another libc++ version or other cores, and the inside count is descriptive: no expected count is claimed. The stored verdicts of the first sets are unchanged.`);
}
function armRepLink() { // section 6a: one sentence that sends the reader to the second set of Arm runs
  if (!has('arm-rep-link') || !S.rep || !S.rep.questions) return;
  const Q = S.rep.questions.arm_cell;
  $('arm-rep-link').replaceChildren(` A second set ${Q.repeated ? 'repeats the word, weakly' : 'read'}: ${formWords(Q.replication_form)} (`, el('a', { href: '#fig-rep' }, 'Figure\u00a08'), ').');
}
function renderReplication() {
  if (!S.rep || !S.rep.rows) return;
  repFigure();
  repDetails();
  armRepLink();
  updateScrollHints();
}

/* ---------- the row-length sweep: one sentence in section 6a, the full account and Figure 9 in section 6d (details page), read from data/dsweep.json ---------- */
const DS_PLAIN = { H1: 'changes little', H2: 'grows with d', falls: 'falls', neither: 'fits none of the words' };
const DS_ROLE = { fit: 'fit', scan: 'remainder scan', bridge: 'bridge', study_l1: 'study L1 size', study_l2: 'study L2 size' };
const dsCol = (r, c) => (c === 'aligned' ? r.aligned : r.as_compiled);
const dsNs = (r, c) => dsCol(r, c).excess_ns_per_inner;
const dsRows = (m, role) => m.rows.filter((r) => r.roles.includes(role));
const dsWord = (m) => m.word && m.word !== 'too few jobs';
const ns2 = (v) => v.toFixed(2);
const sgn = (v) => String(v).replace('-', '−');
function dsGist() { // the sentence section 6a carries for the Arm core
  const m = S.ds && S.arm && S.ds.models.find((x) => x.cpu_short === S.arm.cpu_short);
  if (!m || !dsWord(m)) return '';
  const fit = dsRows(m, 'fit'), a = fit[0], z = fit[fit.length - 1], f1 = (v) => v.toFixed(1);
  return m.columns_agree
    ? `A sweep of the row length, judged by the rule in its plan, gave “${m.word}” in both columns (section 6d).`
    : `A row-length sweep, judged by the rule in its plan, gave “${m.word}”: as compiled the extra time per inner call ${DS_PLAIN[m.columns.as_compiled.word]} (${f1(dsNs(a, 'as_compiled'))} to ${f1(dsNs(z, 'as_compiled'))} ns), aligned it ${DS_PLAIN[m.columns.aligned.word]} (${f1(dsNs(a, 'aligned'))} to ${f1(dsNs(z, 'aligned'))} ns) over the fitted row lengths (section 6d).`;
}
function dsInstrLine(m) { // extra instructions per inner call over the remainder scan and the study size: a straight line in the remainder r, if it is one
  const pts = m.rows.filter((r) => (r.roles.includes('scan') || r.roles.includes('study_l1')) && r.d_mod_8 !== 0).map((r) => [r.d_mod_8, r.extra_instr_per_inner]);
  const n = pts.length, sx = pts.reduce((t, p) => t + p[0], 0), sy = pts.reduce((t, p) => t + p[1], 0), sxx = pts.reduce((t, p) => t + p[0] * p[0], 0), sxy = pts.reduce((t, p) => t + p[0] * p[1], 0);
  const den = n * sxx - sx * sx;
  if (n < 4 || den === 0) return null;
  const slope = (n * sxy - sx * sy) / den, icpt = (sy - slope * sx) / n;
  return pts.every(([r, e]) => Math.abs(icpt + slope * r - e) < 0.6) ? { icpt: Math.round(icpt), slope: Math.round(slope) } : null;
}
function dsDetails() {
  if (!has('dsweep-full') || !S.ds) return;
  const D = S.ds, R = D.rule, ms = D.models.filter(dsWord), mA = ms.find((m) => m.arch === 'aarch64'), mX = ms.find((m) => m.arch === 'x86_64');
  if (!mA || !mX) return;
  const nameOf = (cm) => (D.models.find((m) => m.cpu_model === cm) || D.too_few_jobs.find((m) => m.cpu_model === cm) || { cpu_short: cm }).cpu_short;
  const cw = (m, c) => { const x = m.columns[c]; return `“${x.word}” (fixed share ${x.share.toFixed(3)}, 95% interval ${x.share_ci95[0].toFixed(3)} to ${x.share_ci95[1].toFixed(3)})`; };
  const last = (a) => a[a.length - 1], fitA = dsRows(mA, 'fit'), fitX = dsRows(mX, 'fit');
  $('ds-q').replaceChildren(el('b', null, 'The question. '),
    `On ${mA.cpu_short}, matrix multiply keeps its NEON loop in both builds and the checked build still costs ${mA.published.L1.toFixed(3)}× at L1 (d = ${mA.ladder.study_l1_d}). The listing shows compares and selects before the NEON loop and a checked scalar loop for the leftover elements, which the matrix-multiply paragraph above reads as a set-up cost paid once per inner call (an inner call is one run of the innermost loop over d elements); that reading was inferred, and this sweep tests it. Three accounts are written in the plan (`,
    repoNode(D.plan), `, sha256 ${D.plan_sha256.slice(0, 8)}…). It was drafted before the sweep code, revised while the code was written and tested and once more after a review of the plan and the code, which changed the deciding statistic, and committed alone, before the code commit and before the first run, in the author’s unpublished development history, which this repository does not contain and so cannot show that order. ${provDsweep()} The hash is stored in every dsweep.json of the runs and shows the plan was not edited after the runs. H1, a fixed extra cost per inner call, predicts the same extra time per inner call at every d. H2, a cost per element, predicts extra time in proportion to d. “Falls” is extra time that is smaller at the longer rows. The rule reads the fixed share of the extra time at the study size, fitted over the L1-resident row lengths that leave the same remainder modulo ${mA.ladder.modulus} as the study size (d = ${fitA[0].d} to ${last(fitA).d} on ${mA.cpu_short}): H1 when the share and its 95% interval lie inside ${R.h1_share_band[0]} to ${R.h1_share_band[1]}, H2 inside ${sgn(R.h2_share_band[0])} to ${R.h2_share_band[1]}, “falls” above ${R.falls_share_above}, anything else “neither”. It is applied twice, to the code as compiled and with every hot loop aligned to 64 bytes; when the two disagree the word is “neither” and both are stated.`);
  const commits = [...new Set(D.runs.map((r) => r.commit))];
  $('ds-ran').replaceChildren(el('b', null, 'What ran. '),
    `${capFirst(numWord(D.runs.length))} runs of the sweep workflow, from ${commits.length === 1 ? 'one commit' : `${commits.length} commits`} (${commits.map((c) => c.slice(0, 7)).join(', ')}) of the temporary branch dsweep-smoke, where the sweep workflow file is named ci.yml because a dispatchable workflow must already exist on the default branch (the branch is kept because the run records name the commit): ${D.runs.map((r) => `run ${r.run_id}, ${repJobs(r.jobs)} (${joinAnd(Object.entries(r.models).map(([k, n]) => `${nameOf(k)} ${n}`))})`).join('; ')}. A CPU model needs ${R.minimum_jobs} jobs to get a word, so ${joinAnd(D.too_few_jobs.map((m) => `${m.cpu_short} (${repJobs(m.jobs)})`))} get${D.too_few_jobs.length === 1 ? 's' : ''} none. The timing, the pooling and the intervals are the main study’s. The identical-binary A/A has a half-width of ${pctS(mX.aa.half_width_pct)} on ${mX.cpu_short} and ${pctS(mA.aa.half_width_pct)} on ${mA.cpu_short}, against the ${R.aa_half_width_max_pct}% the rule allows.`);
  const both = mA.columns.as_compiled.share > 1 && mA.columns.aligned.share > 1;
  $('ds-out').replaceChildren(el('b', null, 'Outcome, as the written rule fixed it. '),
    `${mX.cpu_short}: ${mX.word}${mX.columns_agree ? ' in both columns' : ''}: as compiled ${cw(mX, 'as_compiled')}, aligned ${cw(mX, 'aligned')}.${mX.word === 'H2' ? ' The extra time per inner call grows with d there. That is the plan’s weak control, because the loop loses SIMD under the check on x86-64 and neither account was written for it; it gave the word the plan expected, and nothing more is claimed.' : ''} ${mA.cpu_short}: ${mA.word}, because the two columns disagree: as compiled ${cw(mA, 'as_compiled')}, aligned ${cw(mA, 'aligned')}.${both ? ' Both shares are above 1, so this is not a mixture.' : ''} A word that does not survive moving the loops is not claimed.`);
  // what the numbers show, without the word
  const near = (v) => v.toFixed(2);
  const arm = (c) => {
    const rest = fitA.slice(2).map((r) => dsNs(r, c)), br = dsRows(mA, 'bridge'), l2 = dsRows(mA, 'study_l2')[0];
    return `${fitA.slice(0, 2).map((r) => `${near(dsNs(r, c))} ns at d = ${r.d}`).join(' and ')}, then between ${near(Math.min(...rest))} and ${near(Math.max(...rest))} ns from d = ${fitA[2].d} to d = ${last(fitA).d}; beyond the L1-resident rule (context, fitted nowhere) ${br.map((r) => `${near(dsNs(r, c))} ns at d = ${r.d}`).join(', ')} and ${near(dsNs(l2, c))} ns at the study L2 size, d = ${l2.d}`;
  };
  const l2A = dsRows(mA, 'study_l2')[0], restAc = fitA.slice(2).map((r) => dsNs(r, 'as_compiled'));
  const flatFrom = mA.columns.as_compiled.word === 'falls' && fitA.slice(0, 2).every((r) => dsNs(r, 'as_compiled') > Math.max(...restAc)) && (Math.max(...restAc) - Math.min(...restAc)) / Math.min(...restAc) < 0.05;
  const l2X = dsRows(mX, 'study_l2')[0];
  $('ds-shape').replaceChildren(el('b', null, 'What the numbers show, without the word. '),
    `Extra time per inner call (checked minus unchecked) on ${mA.cpu_short}, as compiled: ${arm('as_compiled')}. Aligned: ${arm('aligned')}. ${flatFrom ? `The word “falls” as compiled rests on the first two row lengths; from d = ${fitA[2].d} the values are flat, which is a fact about the points and not a second verdict. ` : ''}d = ${l2A.d} leaves a remainder of ${l2A.d_mod_8} where the ladder leaves ${mA.ladder.residue}, so the change from d = ${last(dsRows(mA, 'bridge')).d} to d = ${l2A.d} mixes the L2 size with the remainder. On ${mX.cpu_short} the extra time grows with d: as compiled ${near(dsNs(fitX[0], 'as_compiled'))} ns at d = ${fitX[0].d} and ${near(dsNs(last(fitX), 'as_compiled'))} ns at d = ${last(fitX).d} (aligned ${near(dsNs(fitX[0], 'aligned'))} and ${near(dsNs(last(fitX), 'aligned'))}), and ${near(dsNs(l2X, 'as_compiled'))} ns at the study L2 size, d = ${l2X.d}; the ratio rises from ${fitX[0].as_compiled.ratio.toFixed(2)} to ${last(fitX).as_compiled.ratio.toFixed(2)}. The plan’s illustrative table of ratios under H1 and H2 did not match the observed ratio at the smallest d on ${mA.cpu_short} (${fitA[0].as_compiled.ratio.toFixed(2)} as compiled): the written rule decides, and the table’s size did not hold.`);
  const line = dsInstrLine(mA), r0 = mA.rows.find((r) => r.d_mod_8 === 0 && r.roles.includes('scan')), ei = fitA.map((r) => Math.round(r.extra_instr_per_inner));
  $('ds-instr').replaceChildren(el('b', null, 'Instruction counts (secondary: instructions, not time). '),
    `Cachegrind counts the extra instructions the checked build runs per inner call: ${ei.every((v) => v === ei[0]) ? `${ei[0]} at every row length of the fit ladder` : `${Math.min(...ei)} to ${Math.max(...ei)} over the fit ladder`} on ${mA.cpu_short}${line ? `; over the remainder scan and the study size it is ${line.icpt} + ${line.slope} × r, where r is d modulo ${mA.ladder.modulus} (r = 1 to ${mA.ladder.modulus - 1})` : ''}${r0 ? `, and at a multiple of ${mA.ladder.modulus} (d = ${r0.d}) it is ${Math.round(r0.extra_instr_per_inner)}, with a time ratio of ${r0.as_compiled.ratio.toFixed(2)}×` : ''}. On ${mX.cpu_short} they grow with d, by about ${mX.instructions.fit.slope.toFixed(1)} for each added element over the ladder. The counts are exact for the listing and say nothing about time by themselves.`);
  const lostR = S.ix.page.lost, x12 = fitX[0], xL1 = dsRows(mX, 'study_l1')[0], xPast = dsRows(mX, 'bridge').find((r) => r.working_set_bytes > mX.l1d_kib * 1024);
  $('ds-scope').replaceChildren(el('b', null, 'Scope of the headline range. '),
    `The range in section 1, ${lostR.min.toFixed(1)}× to ${lostR.max.toFixed(1)}×, is for the study’s sizes. This sweep shows that for matrix multiply on ${mX.cpu_short} the cost depends on the row length: as compiled ${fx(x12.as_compiled.ratio)}× at d = ${x12.d}, ${fx(xL1.as_compiled.ratio)}× at the study’s d = ${xL1.d}${xPast ? ` and ${fx(xPast.as_compiled.ratio)}× at d = ${xPast.d} (${num(xPast.working_set_bytes)} bytes, past the ${mX.l1d_kib} KiB L1 data cache)` : ''}, so ${lostR.min.toFixed(1)}× is not a floor for row lengths the study did not time.`);
  // Table 15
  const head = ['Model and row length', 'Role', 'As compiled: ratio (95% interval)', 'As compiled: extra ns per inner call', 'Aligned: ratio (95% interval)', 'Aligned: extra ns per inner call', 'Extra instructions per inner call', 'Compiled ÷ aligned'];
  const iv = (c) => `${lr(c.ratio)}× (${lr(c.ci95[0])} to ${lr(c.ci95[1])})`;
  $('ds-t-wrap').replaceChildren(el('table', { class: 'tbl dense arm-tbl', id: 'ds-t', 'aria-describedby': 'ds-t-cap' },
    el('thead', null, el('tr', null, ...head.map((h, j) => el('th', { scope: 'col', class: j >= 2 && j !== 7 ? 'num' : null }, h)))),
    el('tbody', null, ...ms.flatMap((m) => m.rows.map((r) => el('tr', null,
      el('th', { scope: 'row' }, `${m.cpu_short}, d = ${r.d}`), el('td', null, r.roles.map((q) => DS_ROLE[q]).join(', ')),
      el('td', { class: 'num' }, iv(r.as_compiled)), el('td', { class: 'num' }, ns2(r.as_compiled.excess_ns_per_inner)),
      el('td', { class: 'num' }, iv(r.aligned)), el('td', { class: 'num' }, ns2(r.aligned.excess_ns_per_inner)),
      el('td', { class: 'num' }, String(Math.round(r.extra_instr_per_inner))), el('td', null, `${d3(r.placement_d)}${r.placement_sensitive ? ' ‡' : ''}`)))))));
  const maxHw = Math.max(...mA.rows.flatMap((r) => ['as_compiled', 'aligned'].map((c) => ((dsCol(r, c).ci95[1] - dsCol(r, c).ci95[0]) / 2 / dsCol(r, c).ratio) * 100)));
  setV('dsCap', `Every row length timed: the pooled ratio of checked ÷ unchecked with its 95% interval and the extra time per inner call, as compiled and aligned; Cachegrind’s extra instructions per inner call (counted, not timed); compiled ÷ aligned, with ‡ where the written placement test calls the length placement-sensitive (fitted nowhere, as on the main study; the placement fields were defined for x86-64 fetch windows). ${D.jobs} jobs; ${mA.cpu_short} is one run of ${mA.jobs} jobs.`);
  $('ds-limits').replaceChildren(el('b', null, 'Limits. '),
    `The ${mA.cpu_short} result is ${numWord(mA.runs)} run of ${numWord(mA.jobs)} jobs on one core type, so its intervals (at most ±${pctS(maxHw)}) cannot show run-to-run or host-to-host spread. The aligned column uses a loop-alignment flag, and the placement controls are not verified on this core (the Limits paragraph of this section), so it is not a pure placement control; this is why both columns are reported. The sweep reads no hardware counters, so it cannot say where the cycles go. One kernel, one compiler (clang 18, FAST mode) and one flag set; nothing here is said about other cores. ${joinAnd(D.too_few_jobs.map((m) => m.cpu_short))} drew too few jobs for a word. No further runs will be made for this question.`);
}
function dsNiceStep(max, n) { const raw = max / n, p = 10 ** Math.floor(Math.log10(raw)), f = raw / p; return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p; }
const SVGNS = 'http://www.w3.org/2000/svg';
function sv(tag, attrs, ...kids) {
  const n = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v);
  for (const k of kids.flat()) if (k != null) n.append(k.nodeType ? k : document.createTextNode(String(k)));
  return n;
}
function dsPanel(m, met, W) {
  const H = 210, L = 44, Rt = 20, T = 10, B = 34, pw = W - L - Rt, ph = H - T - B;
  const cols = met === 'ns' ? ['as_compiled', 'aligned'] : ['as_compiled'];
  const val = (r, c) => (met === 'ns' ? dsNs(r, c) : r.extra_instr_per_inner);
  const xmax = Math.max(...m.rows.map((r) => r.d)), ymax0 = Math.max(...m.rows.flatMap((r) => cols.map((c) => val(r, c))));
  const xs = dsNiceStep(xmax, 4), xm = Math.ceil(xmax / xs) * xs, ys = dsNiceStep(ymax0, 4), ym = Math.ceil(ymax0 / ys) * ys;
  const X = (d) => L + (d / xm) * pw, Y = (v) => T + ph - (v / ym) * ph;
  const svg = sv('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'ds-svg', role: 'group', tabindex: '0', 'data-slug': m.slug,
    'aria-label': `${m.cpu_short}, ${met === 'ns' ? 'extra time' : 'extra instructions'} per inner call against the row length d. Use the left and right arrow keys to move between row lengths; the numbers are in the line below the figure and in Table 15.` });
  for (let v = 0; v <= ym + 1e-9; v += ys) svg.append(sv('line', { x1: L, x2: W - Rt, y1: Y(v), y2: Y(v), class: 'ds-grid' }), sv('text', { x: L - 6, y: Y(v) + 4, class: 'ds-tick', 'text-anchor': 'end' }, String(+v.toFixed(2))));
  for (let d = 0; d <= xm + 1e-9; d += xs) svg.append(sv('text', { x: X(d), y: T + ph + 16, class: 'ds-tick', 'text-anchor': 'middle' }, String(d)));
  svg.append(sv('text', { x: L + pw / 2, y: H - 4, class: 'ds-tick', 'text-anchor': 'middle' }, 'd, the row length'));
  const fit = dsRows(m, 'fit');
  svg.append(sv('rect', { x: X(fit[0].d), y: T, width: Math.max(1, X(fit[fit.length - 1].d) - X(fit[0].d)), height: ph, class: 'ds-band' }));
  const line = (c) => sv('polyline', { points: fit.map((r) => `${X(r.d).toFixed(1)},${Y(val(r, c)).toFixed(1)}`).join(' '), class: `ds-line ds-${c}` });
  for (const c of cols) svg.append(line(c));
  svg.append(sv('line', { x1: X(0), x2: X(0), y1: T, y2: T + ph, class: 'ds-cursor' }));
  for (const r of m.rows) for (const c of cols) {
    const fitted = r.roles.includes('fit') || r.roles.includes('study_l1'), big = fitted || r.roles.includes('study_l2');
    svg.append(sv('circle', { cx: X(r.d), cy: Y(val(r, c)), r: big ? 4.5 : 3, class: `ds-pt ds-${c}${fitted ? ' fitted' : ''}`, 'data-d': r.d }));
  }
  svg._x = X;
  const pick = (d) => dsPick(m.slug, d);
  svg.addEventListener('click', (e) => {
    const q = svg.getBoundingClientRect(), px = ((e.clientX - q.left) / q.width) * W;
    pick(m.rows.reduce((b, r) => (Math.abs(X(r.d) - px) < Math.abs(X(b.d) - px) ? r : b), m.rows[0]).d);
  });
  svg.addEventListener('keydown', (e) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return;
    e.preventDefault();
    const ds = m.rows.map((r) => r.d).sort((a, b) => a - b);
    let i = S.dsSel && S.dsSel.slug === m.slug ? ds.indexOf(S.dsSel.d) : -1;
    if (e.key === 'ArrowRight') i = Math.min(ds.length - 1, i + 1);
    if (e.key === 'ArrowLeft') i = Math.max(0, i < 0 ? 0 : i - 1);
    if (e.key === 'Home') i = 0;
    if (e.key === 'End') i = ds.length - 1;
    pick(ds[i]);
  });
  return svg;
}
function dsPick(slug, d) { S.dsSel = { slug, d }; dsMark(); dsRead(); dsStepState(); }
function dsSteps() { // the row lengths of the chosen panel, shortest first
  const m = S.ds.models.find((x) => x.slug === S.dsSel.slug);
  return m.rows.map((r) => r.d).sort((a, b) => a - b);
}
function dsStepState() {
  const ds = dsSteps(), i = ds.indexOf(S.dsSel.d);
  $('ds-prev').disabled = i <= 0;
  $('ds-next').disabled = i < 0 || i >= ds.length - 1;
}
function dsMark() {
  for (const svg of $('ds-panels').querySelectorAll('svg')) {
    const on = S.dsSel && S.dsSel.slug === svg.dataset.slug;
    const cur = svg.querySelector('.ds-cursor');
    cur.style.display = on ? '' : 'none';
    if (on) { const x = svg._x(S.dsSel.d); cur.setAttribute('x1', x); cur.setAttribute('x2', x); }
    for (const p of svg.querySelectorAll('.ds-pt')) p.classList.toggle('sel', !!on && Number(p.dataset.d) === S.dsSel.d);
  }
}
function dsRead() {
  const box = $('ds-read'), m = S.ds.models.find((x) => x.slug === S.dsSel.slug), r = m && m.rows.find((x) => x.d === S.dsSel.d);
  if (!r) { box.replaceChildren(); return; }
  const col = (c, n) => `${n} ${lr(dsCol(r, c).ratio)}× (${lr(dsCol(r, c).ci95[0])} to ${lr(dsCol(r, c).ci95[1])}), ${ns2(dsNs(r, c))} ns extra per inner call`;
  box.replaceChildren(el('p', { class: 'rp-head' }, el('b', null, `${m.cpu_short}, d = ${r.d}`), ` (${r.roles.map((q) => DS_ROLE[q]).join(', ')}, remainder ${r.d_mod_8}): ${col('as_compiled', 'as compiled')}; ${col('aligned', 'aligned')}. ${Math.round(r.extra_instr_per_inner)} extra instructions per inner call (counted, not timed). Compiled ÷ aligned ${d3(r.placement_d)}${r.placement_sensitive ? ', placement-sensitive' : ''}.`));
}
function dsPanelWidth(box) { // the width the grid really gives one panel: the stylesheet decides one or two columns, so read the first track, which keeps the drawing at scale 1
  const tracks = getComputedStyle(box).gridTemplateColumns.split(' ').map(parseFloat).filter((v) => v > 0);
  return Math.max(240, Math.floor(tracks.length ? tracks[0] : box.clientWidth));
}
function dsDraw() {
  const box = $('ds-panels'), ms = S.ds.models.filter(dsWord);
  const W = dsPanelWidth(box);
  S.dsBoxW = box.clientWidth;
  const had = document.activeElement && document.activeElement.closest && document.activeElement.closest('#ds-panels svg');
  const slug = had && had.dataset.slug;
  $('ds-title').textContent = `The extra ${S.dsMet === 'ns' ? 'time' : 'instructions'} per inner call against the row length d, on ${joinAnd(ms.map((m) => m.cpu_short))}`;
  box.replaceChildren(...ms.map((m) => el('div', { class: 'ds-panel' },
    el('p', { class: 'ds-ptitle' }, el('b', null, m.cpu_short), ` ${m.word}${m.columns_agree ? '' : ' (columns disagree)'}, ${repJobs(m.jobs)}`), dsPanel(m, S.dsMet, W))));
  dsMark();
  if (slug) { const n = box.querySelector(`svg[data-slug="${slug}"]`); if (n) n.focus(); }
}
function dsFigure() {
  if (!has('ds-panels') || !S.ds) return;
  const ms = S.ds.models.filter(dsWord), A = ms.find((m) => m.arch === 'aarch64');
  S.dsMet = S.dsMet || 'ns';
  S.dsSel = S.dsSel || { slug: A.slug, d: A.ladder.study_l1_d };
  const seg = $('ds-met-seg');
  for (const b of seg.querySelectorAll('button')) { b.setAttribute('aria-checked', b.dataset.met === S.dsMet ? 'true' : 'false'); b.onclick = () => { S.dsMet = b.dataset.met; for (const x of seg.querySelectorAll('button')) x.setAttribute('aria-checked', x.dataset.met === S.dsMet ? 'true' : 'false'); dsDraw(); dsCaption(); }; }
  if (!seg.dataset.keys) { seg.dataset.keys = '1'; radioKeys(seg, 'met', (v) => { S.dsMet = v; for (const x of seg.querySelectorAll('button')) x.setAttribute('aria-checked', x.dataset.met === v ? 'true' : 'false'); dsDraw(); dsCaption(); }); }
  const step = (dir) => () => { const ds = dsSteps(), i = ds.indexOf(S.dsSel.d); dsPick(S.dsSel.slug, ds[Math.max(0, Math.min(ds.length - 1, i + dir))]); };
  $('ds-prev').onclick = step(-1);
  $('ds-next').onclick = step(1);
  dsDraw();
  dsRead();
  dsStepState();
  dsCaption();
  if (!S.dsResize) { // redraw when the box changes width (a window resize, a fold opening, a text-size change), not when its height changes
    S.dsResize = true;
    let t = 0;
    const again = () => { clearTimeout(t); t = setTimeout(() => { if (S.ds && Math.abs($('ds-panels').clientWidth - S.dsBoxW) > 1) dsDraw(); }, 120); };
    if (window.ResizeObserver) new ResizeObserver(again).observe($('ds-panels')); else addEventListener('resize', again);
  }
}
function dsCaption() {
  const ms = S.ds.models.filter(dsWord), key = (c) => el('span', { class: `key ds-key ds-${c}`, 'aria-hidden': 'true' });
  const fits = ms.map((m) => { const f = dsRows(m, 'fit'); return `d = ${f[0].d} to ${f[f.length - 1].d} on ${m.cpu_short}`; });
  $('ds-cap').replaceChildren(el('b', null, 'Figure 9.'),
    ...(S.dsMet === 'ns'
      ? [' The time the checks add to one inner call (checked minus unchecked, ns), against the row length d, as compiled (', key('as_compiled'), ' filled) and aligned (', key('aligned'), ' hollow). ']
      : [' The instructions the checks add to one inner call (Cachegrind: counted, not timed), against the row length d. ']),
    `The shaded band is the ladder the rule fits (${joinAnd(fits)}), joined by a line; grey points are the remainder scan, the bridge and the study L2 size, fitted nowhere. The two panels have their own scales. Select a panel, or use its arrow keys, to read a row length; all are in `, el('a', { href: '#ds-t-cap' }, 'Table 15'), '.');
}
function renderDsweep() {
  if (!S.ds || !S.ds.models) return;
  armMmFill();
  armMatmul();
  dsDetails();
  dsFigure();
  updateScrollHints();
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
  const ceN = ceVersionCount(C), ceWho = `${ceN} compiler versions (${C.counts.compilers} Compiler Explorer compiler ids)`; // 28 ids = 14 versions, each as an x86 and an AArch64 id
  setV('ceCompilers', ceWho);
  const gccR = `GCC ${ceRanges(C.summary.majors.filter((m) => C.rows.some((r) => r.family === 'gcc' && r.major === m)))}`;
  setV('ceFind', `Compiled only, not timed, on ${ceWho}: ${f.short}`);
  setV('ceCap', `Compile-only: this says which loops lose vectorization, not what they cost. Each clang is paired with the libc++ Compiler Explorer provides (assumed to match). sten: stencil, strd: stride-2, gath: gather, mm: matrix multiply.`);
  setV('ceNote', `Every row of the compile-only sweep: ${C.counts.rows} rows (${ceN} compiler versions, ${f.clangRange} with libc++ and ${gccR} with assertions, offered as ${C.counts.compilers} separate x86-64 and AArch64 compiler ids on Compiler Explorer, on three targets at -O2 and -O3), ${C.counts.cells} loop cells from ${C.counts.builds} builds. No timing: a cell says whether the loop is vectorized with the checks off and with them on. ${f.text}`);
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
  setV('rwStatus', `${capFirst(numWord(prog.length))} workloads (${numWord(projectsOf(prog))} projects: LightGBM three ways, Draco, tiny-dnn, Spectra) that contain lost loops and two controls that do not, each timed whole with the checks off (NONE) and on (FAST): ${T.jobs} jobs in ${R.runs.length} runs on GitHub’s shared machines. ${main.jobs} jobs drew an AMD ${main.cpu_short}, the model with the most jobs, so Table 9 is that model; the other ${restJobs} jobs (AMD ${joinAnd(rest.map((g) => g.cpu_short))}) are summarised below and on the details page.`);
  setV('rwTCap', `FAST ÷ NONE, whole program, AMD ${main.cpu_short}, ${main.jobs} jobs, 95% interval beneath. Aligned: both builds with every hot loop aligned to 64 bytes. A/A floor: the unchecked program against a copy of itself. A reading needs both columns above the floor.`);
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
  setV('rwShare', `Cachegrind counts instructions, not time: the lost loops’ lines hold ${rwPct(lo, false)} to ${rwPct(hi, false)} of executed instructions (their functions up to ${pctS(fmax)}). For ${joinAnd(small.map((r) => RW_NAMES[r.row]))} it is under 1%, yet FAST costs them ${pc(Math.min(...small.flatMap((r) => [main.rows[r.row].fast.ratio, main.rows[r.row].aligned.ratio])))}% to ${pc(Math.max(...small.flatMap((r) => [main.rows[r.row].fast.ratio, main.rows[r.row].aligned.ratio])))}% across the two columns: consistent with most of the cost being checks elsewhere (loops that kept SIMD, other code). Which checks account for this was not isolated, so no mechanism is claimed (LightGBM linear, at ${pctS(lin.lines_none)}, cannot be separated).`);
  const ex = T.expect, held = ex.filter((e) => e.held), miss = ex.filter((e) => !e.held);
  const why = (e) => `${RW_NAMES[e.row].replace(' (control)', '')}: expected ${e.low.toFixed(2)} to ${e.high.toFixed(2)}${e.call === 'probably not' || e.call === 'no' ? ' and undetectable' : ''}, got ${rwR3(e.fast)} and ${rwR3(e.aligned)}${e.reading === 'detectably slower' ? ', detectable' : ''}`;
  setV('rwExpect', `Of the ${ex.length} expectations committed before any run (in the author’s unpublished development history), ${held.length} held (range and detectable-or-not call, both columns; Table 11 on the details page). Missed: ${miss.map(why).join('; ')}.`);
  setV('rwLimits', `Limits: no profile-guided optimization in this timing (section 7c’s PGO column did not make the cost vanish in most rows), shared virtual machines, one toolchain (clang 18, libc++ 18, -O2, x86-64 baseline), three AMD CPU models only, and programs picked because they contain lost loops, so not a sample of Google’s services. This neither confirms nor contradicts Google’s 0.30%.`);
  setV('rwOtherCap', `The other CPU models: ${rest.map((g) => `AMD ${g.cpu_short}, ${g.jobs} jobs in ${g.runs} runs`).join('; ')} (the second in Table 10c). Readings are summarised in section 7; with so few jobs the spread between machines is only sampled${rest.every((g) => g.max_in_a_run < R.minimum_jobs) ? `, and no run holds ${R.minimum_jobs} or more jobs of any of them to test it` : ''}. FAST ÷ NONE, interval beneath; Layout A/A: the unchecked binary aligned ÷ as compiled.`);
  setV('rwOther2Cap', rest[1] ? `AMD ${rest[1].cpu_short}, ${rest[1].jobs} jobs in ${rest[1].runs} runs. Same columns as Table 10.` : '');
  setV('rwAllCap', `All ${T.all.jobs} jobs pooled across CPU models. Descriptive only, since it mixes CPU models.`);
  for (const [id, g] of [['rw-other-table', rest[0]], ['rw-other2-table', rest[1]], ['rw-all-table', T.all]]) {
    if (!g) continue;
    $(id).querySelector('tbody').replaceChildren(...Object.keys(RW_NAMES).map((n) => rwTimeRow(n, g.rows[n], 'layout')));
  }
  setV('rwExpectCap', `Expectations written before any build or run, in the author’s unpublished development history (realworld/PLAN.md), checked against AMD ${main.cpu_short}. “Held” needs the as-compiled and aligned ratios inside the expected range and the detectable-or-not call to match.`);
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
    seg.append(el('button', { type: 'button', role: 'radio', 'data-cpu': c.slug, 'aria-checked': c.slug === S.cpu ? 'true' : 'false', tabindex: c.slug === S.cpu ? '0' : '-1', title: `${c.cpu_model}: ${c.jobs} job${c.jobs > 1 ? 's' : ''} pooled${c.form === 'inconclusive' ? '; no verdict (inconclusive)' : ''}`, onclick: () => selectCpu(c.slug) }, c.cpu_short));
  }
  renderVerdictNote();
  const pc = pooledOf(currentCpu().cpu_model);
  const hasAligned = !!(pc && pc.cells.some((c) => c.aligned));
  for (const b of $('col-seg').querySelectorAll('button')) {
    b.setAttribute('aria-checked', b.dataset.col === S.col ? 'true' : 'false');
    b.tabIndex = b.dataset.col === S.col ? 0 : -1;
    b.disabled = b.dataset.col === 'aligned' && !hasAligned;
  }
}
function renderVerdictNote() { // Figure 1 draws the measured bars for every model with enough jobs; a model the written rules left inconclusive, or passed by a narrow margin, says so beside the switcher
  const n = document.getElementById('cpu-verdict');
  if (!n) return;
  const c = currentCpu();
  if (!S.fixture && c.form === 'map' && closeCalls(c).length) { n.textContent = `${c.cpu_short}: ${closeWords(c)}${undecidedWords(c, true) ? ` ${capFirst(undecidedWords(c, true))}` : ''} More in Table 1 and the details.`; return; }
  if (S.fixture || c.form !== 'inconclusive') { n.textContent = ''; return; }
  const ms = missWords(c);
  n.textContent = `No verdict for ${c.cpu_short}: inconclusive under the written rules${ms ? `, because the ${limitWords(c)} rule is missed by ${ms}` : ''}. The bars are measured values; Table 1 has the reason.`;
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
  // the sample notices exist only while the test fixture is shown: the served HTML carries no such text
  const notice = (id, text) => { const n = document.getElementById(id); if (!n) return; n.textContent = sample ? text : ''; n.hidden = !sample; };
  notice('sample-band', 'SAMPLE DATA: the figures below show results/fixture.json, a made-up file for testing the page, not a measurement.');
  notice('sample-mark', 'SAMPLE DATA');
  return true;
}
// A link such as details.html#arm-full jumps to its target before this page has filled in the sections above it, and
// the browser does not always follow the target as they grow (Chromium on Linux stays where the first jump left it).
// Each time a section lands, a reader who has not scrolled yet is brought back to the target.
let readerMoved = false;
for (const ev of ['wheel', 'touchstart', 'keydown', 'mousedown']) addEventListener(ev, () => { readerMoved = true; }, { passive: true, once: true });
function landOnHash() {
  if (readerMoved) return;
  let id = '';
  try { id = decodeURIComponent(location.hash.slice(1)); } catch (err) { return; }
  // On the main page only the reference links point at things this script builds (#ref-queue, #cite-queue): the script that
  // opens collapsed sections and follows the hash runs before the reference list and the related-work table exist.
  if (PAGE !== 'details' && !/^(ref|cite)-[a-z0-9-]+$/.test(id)) return;
  const target = id && !id.includes('=') ? document.getElementById(id) : null;
  if (!target) return;
  const body = target.closest('.sec-body');
  if (body && body.hidden) { const more = document.querySelector(`.sec-more[aria-controls="${body.id}"]`); if (more) more.click(); } // the section the target sits in is collapsed
  const top = target.getBoundingClientRect().top;
  const pad = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0; // the room the sticky bar needs
  if (top < pad - 6 || top > pad + 64) target.scrollIntoView({ behavior: 'instant', block: 'start' });
}
async function loadSection(path, key, render, boxId) {
  try {
    S[key] = await getJSON(path);
    render();
    landOnHash();
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
      S.ix.sections.arm64 ? loadSection(S.ix.sections.arm64, 'arm', renderArm, has('arm') ? 'arm' : 'arm-full') : null,
      S.ix.sections.replication ? loadSection(S.ix.sections.replication, 'rep', renderReplication, has('fig-rep') ? 'fig-rep' : 'replication-full') : null,
      S.ix.sections.dsweep ? loadSection(S.ix.sections.dsweep, 'ds', renderDsweep, has('arm') ? 'arm' : 'dsweep-full') : null,
    ]);
    renderMatmulVersions();
    renderRuleList();
    renderProgSum();
    updateScrollHints();
    landOnHash();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(landOnHash);
    setTimeout(landOnHash, 600);
    if (typeof ResizeObserver === 'function' && location.hash.length > 1) { // whatever else grows above the target in the next few seconds
      const ro = new ResizeObserver(() => landOnHash());
      ro.observe(document.body);
      setTimeout(() => ro.disconnect(), 4000);
    }
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
    // the heading is named by its own words; the permalink inside it keeps its own name, so a screen reader does not read "Result Link to Result"
    const title = (no ? h.textContent.slice(no.textContent.length) : h.textContent).trim();
    h.setAttribute('aria-label', `${no ? `${no.textContent} ` : ''}${title}`);
    h.append(el('a', { class: 'pil', href: `#${sec.id}`, 'aria-label': `Link to section: ${title}` }, '¶'));
    const more = sec.querySelector(':scope > .sec-more');
    if (more) { // "Details" and "Hide details" say which section they open or close, whatever the button's text is at the moment
      const label = () => more.setAttribute('aria-label', `${more.textContent.trim()}: ${title}`);
      label();
      new MutationObserver(label).observe(more, { childList: true, characterData: true, subtree: true });
    }
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
  const gpct = S.ix && S.ix.claim ? `${S.ix.claim.google_pct.toFixed(2)}\\% ` : ''; // a bare % starts a comment in LaTeX, so it is escaped in the title
  $('cmd-cite').textContent = `@misc{jacobopacheco2026thirdofapercent,
  author = {JacoboPacheco},
  title  = {Third of a Percent: bounds checks in C++'s standard library, measured loop by loop next to Google's ${gpct}average},
  year   = {2026},
  note   = {Work in progress, October 2026. Code written by AI coding agents directed by the author},
  url    = {${base}}
}`;
}
/* The machine-code slide-over (built in hero.js) is a modal dialog. Tell assistive technology so, and keep Tab inside it: the
   panel's own handler skips <summary> elements, so with one of them last in the panel, Tab left the dialog for the page behind. */
function hardenDialog() {
  const mark = () => { const p = document.getElementById('asm-panel'); if (p) p.setAttribute('aria-modal', 'true'); return !!p; };
  if (!mark()) { const mo = new MutationObserver(() => { if (mark()) mo.disconnect(); }); mo.observe(document.body, { childList: true }); setTimeout(() => mo.disconnect(), 20000); }
  document.addEventListener('keydown', (e) => {
    const p = document.getElementById('asm-panel');
    if (e.key !== 'Tab' || !p || p.hidden || e.ctrlKey || e.altKey || e.metaKey) return;
    const f = [...p.querySelectorAll('button, a[href], summary, input, select, textarea, [tabindex]')].filter((n) => n.tabIndex >= 0 && !n.disabled);
    if (!f.length) return;
    const step = e.shiftKey ? -1 : 1;
    let i = f.indexOf(document.activeElement);
    e.preventDefault();
    e.stopImmediatePropagation();
    // the next control that takes focus: links and buttons inside a closed <details> are skipped because focus() refuses them
    for (let k = 0; k < f.length; k++) {
      i = i === -1 ? (step > 0 ? 0 : f.length - 1) : (i + step + f.length) % f.length;
      f[i].focus();
      if (document.activeElement === f[i]) return;
    }
  }, true);
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
  hardenDialog();
  await start();
  buildChrome();
}
init();
