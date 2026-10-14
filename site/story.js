/* Third of a Percent: the modules under the hero.
   1. the contrast band: Google's reported average beside this study's worst loop (follows the CPU chip);
   2. the mechanism demo: click-driven, eight array cells, check off or on, Step;
   3. small parts: the SIMD chip, the one-time hint on the toggle, links that open a folded block.
   Reads app.js's state (S) and helpers and race.js's exports; every number comes from data/. Click-first: no
   dragging, no scroll-driven steps, no timers except the one-time hint. No audio, no external scripts. */
(function () {
'use strict';
const $ = (id) => document.getElementById(id);
const RM = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function whenReady(test, ms = 15000) {
  const t0 = performance.now();
  while (performance.now() - t0 < ms) { try { if (test()) return true; } catch (e) { /* app.js still starting */ } await sleep(60); }
  return false;
}
const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };

function cellInfo(k) { // the same cell the hero lanes read: this CPU model, the smallest size
  const pc = pooledOf(currentCpu().cpu_model), cell = cellOf(pc, `${k}.L1`);
  const col = column(cell) || (cell && cell.as_compiled) || null;
  return { cls: cell ? role(cell) : 'none', ratio: col ? col.ratio : null };
}

/* ---------- 1. the contrast band ---------- */
function paintBand() {
  const ks = Object.keys(S.ix.criteria.kernels);
  let best = null;
  for (const k of ks) { const i = cellInfo(k); if (i.ratio != null && (!best || i.ratio > best.ratio)) best = { k, ratio: i.ratio }; }
  const out = $('band-worst'), lab = $('band-wl');
  if (!best) { out.textContent = 'n/a'; lab.textContent = 'not measured on this CPU model'; return; }
  out.textContent = `${fx(best.ratio)}×`;
  lab.textContent = `The slowest of the eight loops in the main timing (${SHORT_NAMES[best.k]}, ${currentCpu().cpu_short}): one loop, a check of the same kind`;
}

/* ---------- 2. the mechanism demo ---------- */
const NC = 8, LANES = 4;
const ORDER = {
  k01_sum_fwd: [0, 1, 2, 3, 4, 5, 6, 7],
  k02_add_fwd: [0, 1, 2, 3, 4, 5, 6, 7],
  k03_stencil: [0, 1, 2, 3, 4, 5, 6, 7],
  k04_rev: [7, 6, 5, 4, 3, 2, 1, 0],
  k05_stride2: [0, 2, 4, 6],
  k06_gather: [3, 7, 1, 5, 0, 6, 2, 4],
  k07_hist: [5, 2, 6, 2, 5, 5, 6, 2],   // a few counters, hit again and again
  k08_matmul: [4, 5, 6, 7, 4, 5, 6, 7], // the same row walked once for every k
};
const M = { k: null, on: true, i: 0 };

function plan(k, on) {
  const A = ORDER[k] || ORDER.k01_sum_fwd, inf = cellInfo(k), simdOk = inf.cls === 'lost' || inf.cls === 'kept';
  const steps = [];
  if (!on) {
    if (simdOk) for (let i = 0; i < A.length; i += LANES) steps.push({ el: A.slice(i, i + LANES), simd: true, gate: null });
    else for (const e of A) steps.push({ el: [e], simd: false, gate: null });
  } else if (inf.cls === 'kept') { // the sizes are tested once before the loop; the check runs only on leftover elements (none with eight)
    for (let i = 0; i < A.length; i += LANES) steps.push({ el: A.slice(i, i + LANES), simd: true, gate: i === 0 && k !== 'k01_sum_fwd' ? 'once' : null });
  } else for (const e of A) steps.push({ el: [e], simd: false, gate: 'each' });
  return { A, steps, cls: inf.cls };
}

function explain(k, on, cls) {
  const words = HeroRace.words(k);
  if (!on) return cls === 'none' ? 'Check off, and this loop is not vectorized in either build: one element per step.' : 'Check off: one Step handles four elements at once. That is SIMD: one instruction, four elements.';
  if (cls === 'kept') return k === 'k01_sum_fwd' ? `Check on. ${words}` : 'Check on: the compiler tests the sizes once, before the loop, and keeps the four-at-a-time body; the check only runs on leftover elements, and eight divide evenly by four.';
  if (cls === 'lost') return `Check on: each element must pass the gate, which stops the program if the index is out of range. ${words}`;
  return `Check on: each element passes the gate. ${words}`;
}

function drawMech() {
  const row = $('mech-row'), P = plan(M.k, M.on), n = P.steps.length;
  if (M.i > n) M.i = 0;
  const visited = new Set(P.A), done = new Set(), now = new Set();
  for (let s = 0; s < Math.min(M.i, n); s++) for (const e of P.steps[s].el) (s === M.i - 1 ? now : done).add(e);
  const cur = M.i > 0 ? P.steps[M.i - 1] : null;
  row.replaceChildren();
  const role_ = P.cls === 'lost' ? 'lost' : P.cls === 'kept' ? 'kept' : 'none';
  $('mech-card').dataset.role = role_;
  for (let c = 0; c < NC; c++) {
    const d = el('i', 'mc');
    d.style.gridColumn = String(c + 1);
    d.append(el('span', 'mc-n', String(c)));
    if (!visited.has(c)) d.classList.add('skip');
    if (done.has(c)) d.classList.add('done');
    if (now.has(c)) d.classList.add('now');
    if (M.on && P.steps.some((s, si) => si < M.i && s.gate === 'each' && s.el.includes(c))) d.classList.add('chk');
    row.append(d);
  }
  if (cur) { // the bracket under the cells that move together, or the gate above the cell about to pass
    const lo = Math.min(...cur.el), hi = Math.max(...cur.el);
    if (cur.simd) { const b = el('i', 'mc-simd'); b.style.gridColumn = `${lo + 1} / ${hi + 2}`; b.append(el('span', null, 'one instruction')); row.append(b); }
    if (cur.gate === 'each') { const g = el('i', 'mc-gate'); g.style.gridColumn = String(cur.el[0] + 1); g.append(el('span', null, 'in range?')); row.append(g); }
    if (cur.gate === 'once') { const g = el('i', 'mc-gate once'); g.style.gridColumn = '1 / -1'; g.append(el('span', null, 'sizes tested once, before the loop')); row.append(g); }
  }
  const total = n, label = M.i >= n && n ? 'Start over' : 'Step';
  $('mech-step').textContent = label;
  $('mech-count').textContent = `Step ${Math.min(M.i, n)} of ${total}`;
  $('mech-step').setAttribute('aria-label', `${label}: ${M.i >= n ? 'back to the start' : `step ${M.i + 1} of ${total}`}`);
  const say = $('mech-say');
  const base = explain(M.k, M.on, P.cls);
  let prog = '';
  if (cur && cur.gate === 'each') prog = ` Element ${cur.el[0]}: in range, go on.`;
  else if (cur && cur.simd) prog = ` Elements ${[...cur.el].sort((a, b) => a - b).join(', ')} done together.`;
  else if (cur) prog = ` Element ${cur.el[0]} done.`;
  else prog = ' Press Step to begin.';
  say.replaceChildren(el('span', 'ms-why', base), el('span', 'ms-now', prog));
  for (const b of $('mech-chk').children) { const on = (b.dataset.on === '1') === M.on; b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1; }
  for (const b of $('mech-tiles').children) { const on = b.dataset.k === M.k; b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1; b.dataset.role = cellInfo(b.dataset.k).cls; }
}

function buildMech() {
  const tiles = $('mech-tiles'), card = $('mech-card');
  for (const k of Object.keys(S.ix.criteria.kernels)) {
    const b = el('button'); b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.k = k;
    b.innerHTML = `<svg class="gl" viewBox="0 0 64 36" aria-hidden="true" focusable="false">${HeroRace.glyph(k)}</svg><span class="mt-l"></span>`;
    b.querySelector('.mt-l').textContent = SHORT_NAMES[k].replace(/^./, (c) => c.toUpperCase());
    b.setAttribute('aria-label', SHORT_NAMES[k]);
    b.addEventListener('click', () => { select(k, false, true); M.k = k; M.i = 0; drawMech(); });
    tiles.append(b);
  }
  radioKeys(tiles, 'k', (k) => { select(k, false, true); M.k = k; M.i = 0; drawMech(); });
  const setOn = (v) => { M.on = v; M.i = 0; drawMech(); };
  $('mech-chk').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) setOn(b.dataset.on === '1'); });
  radioKeys($('mech-chk'), 'on', (v) => setOn(v === '1'));
  $('mech-step').addEventListener('click', () => { const n = plan(M.k, M.on).steps.length; M.i = M.i >= n ? 0 : M.i + 1; drawMech(); });
  card.hidden = false;
  M.k = S.sel;
  drawMech();
}

/* ---------- 3. small parts ---------- */
function simdChip() {
  const b = $('simd-chip'), d = $('simd-def');
  if (!b || !d) return;
  b.addEventListener('click', () => { const on = d.hidden; d.hidden = !on; b.setAttribute('aria-expanded', String(on)); });
}
function toggleHint() { // shown once, when the first run has finished; any use of the switch (or 9 s) ends it
  const h = $('sw-hint'); if (!h) return;
  let gone = false;
  const end = () => { if (gone) return; gone = true; h.classList.remove('show'); setTimeout(() => { h.hidden = true; }, 220); };
  document.addEventListener('race-used', end, { once: true });
  setTimeout(() => { if (gone) return; h.hidden = false; requestAnimationFrame(() => h.classList.add('show')); setTimeout(end, 9000); }, 1700);
}
function openFolds() { // a link into a folded block opens it first
  const open = (t) => { for (let n = t; n; n = n.parentElement) if (n.tagName === 'DETAILS' && !n.open) n.open = true; };
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]'); if (!a || a.getAttribute('href').length < 2) return;
    const t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
    if (t) { open(t); if (a.id === 'bar-limits') { e.preventDefault(); t.scrollIntoView({ behavior: RM() ? 'auto' : 'smooth', block: 'center' }); history.replaceState(null, '', '#cannot'); } }
  });
  if (location.hash.length > 1) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) open(t); }
}

function placementSimple() { // the placement module shows one sentence and the four taps; the ruler and controls are one click away
  const wd = $('wd-placement'), host = $('w-placement'); if (!wd || !host) return;
  wd.classList.add('pl-lite');
  const btn = el('button', 'pl-more', 'Show the ruler and controls'); btn.type = 'button'; btn.setAttribute('aria-expanded', 'false');
  btn.addEventListener('click', () => { const on = !wd.classList.contains('pl-full'); wd.classList.toggle('pl-full', on); btn.setAttribute('aria-expanded', String(on)); btn.textContent = on ? 'Hide the ruler and controls' : 'Show the ruler and controls'; });
  host.after(btn);
}

async function boot() {
  placementSimple();
  simdChip();
  openFolds();
  toggleHint();
  if (!(await whenReady(() => S.ix && S.pooled && S.rows && S.cpu && S.sel && window.HeroRace))) return;
  paintBand();
  buildMech();
  const _sync = HeroRace.sync; // a new loop or CPU model anywhere follows into the band and the demo
  HeroRace.sync = function (only) { const r = _sync.apply(this, arguments); paintBand(); if (M.k !== S.sel) { M.k = S.sel; M.i = 0; } drawMech(); return r; };
}
boot();
})();
