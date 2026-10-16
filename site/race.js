/* Third of a Percent: the hero. One finding (what the bounds check costs each loop shape, per CPU model),
   four presentations of it, selectable with #hero=1 to #hero=4 (a small selector in the top bar appears
   only when the hash has "hero" or the reader presses H).
     4  The whole map in one race (default): all eight loops at once, each a pair of bars (check off, check on)
        whose length is the measured pooled ratio; the lanes that lose SIMD visibly lag, the forward ones tie.
     1  Race track: two lanes (check off / check on) on a light stage, isometric tiles, a finish line.
     2  Poster: the measured ratio as one huge number; the loop's access pattern drawn as arcs over array cells.
     3  Inspector: a lens over the array on a graphite stage, the real machine code beside it, a gauge.
   Every printed number is the measured pooled ratio from data/ (via app.js's S and helpers). Every animation is
   an illustration scaled to that ratio, labelled so; it runs once and rests on its final frame (reduced motion:
   the final frame at once). No audio, no external scripts. Loaded after app.js, before hero.js. */
(function () {
'use strict';
const $ = (id) => document.getElementById(id);
const RM = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const DEFAULT_HV = 4;
const LANES = 4, T0 = 0.3, RMIN = 0.5, RMAX = 4;
let N = 24;

/* ---------- the glyphs: each loop's access pattern, drawn ---------- */
const cx = (i) => 3.2 + i * 7.6;
function cells(y, hi, n) {
  let s = '';
  for (let i = 0; i < (n || 8); i++) s += `<rect class="g-c${(hi || []).includes(i) ? ' hi' : ''}" x="${cx(i)}" y="${y}" width="6" height="7" rx="1.3"/>`;
  return s;
}
const path = (d) => `<path class="g-a" d="${d}"/>`;
const GLYPH = {
  k01_sum_fwd: cells(24) + path('M4 13H58M54 9l4 4-4 4'),
  k02_add_fwd: cells(4) + cells(27) + path('M4 20H58M54 16l4 4-4 4'),
  k03_stencil: cells(24, [3, 4, 5]) + path(`M${cx(3)} 20v-5h${cx(5) + 6 - cx(3)}v5M${cx(4) + 3} 15V8`),
  k04_rev: cells(24) + path('M60 13H6M10 9l-4 4 4 4'),
  k05_stride2: cells(24, [0, 2, 4, 6]) + path(`M${cx(0) + 3} 22q3.8-11 7.6 0M${cx(2) + 3} 22q3.8-11 7.6 0M${cx(4) + 3} 22q3.8-11 7.6 0M${cx(6) + 3} 22q3.8-11 7.6 0`),
  k06_gather: cells(26, [1, 3, 5, 6]) + path(`M${cx(3) + 3} 24Q${cx(4.5) + 3} 2 ${cx(6) + 3} 24M${cx(6) + 3} 24Q${cx(3.5) + 3} 6 ${cx(1) + 3} 24M${cx(1) + 3} 24Q${cx(3) + 3} 12 ${cx(5) + 3} 24`),
  k07_hist: cells(3) + '<rect class="g-c hi" x="6" y="22" width="9" height="11" rx="1.3"/><rect class="g-c hi" x="19" y="14" width="9" height="19" rx="1.3"/><rect class="g-c hi" x="32" y="26" width="9" height="7" rx="1.3"/><rect class="g-c hi" x="45" y="18" width="9" height="15" rx="1.3"/>' + path('M22 12v-1M25 12v-1'),
  k08_matmul: (() => { let s = ''; for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) s += `<rect class="g-c${r === 1 || c === 2 ? ' hi' : ''}" x="${16 + c * 8.4}" y="${2 + r * 8.4}" width="6.6" height="6.6" rx="1.2"/>`; return s; })(),
};

/* ---------- the drawing helpers ---------- */
function perm() { const a = [...Array(N).keys()]; let s = 12345; for (let i = N - 1; i > 0; i--) { s = (s * 1103515245 + 12345) & 0x7fffffff; const j = s % (i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; }
let PERM = perm();
function setN() { const n = innerWidth < 641 ? 16 : 24; if (n !== N) { N = n; PERM = perm(); } }
function order(k) {
  let a = [...Array(N).keys()];
  if (k === 'k04_rev') a.reverse();
  else if (k === 'k05_stride2') a = a.filter((i) => i % 2 === 0);
  else if (k === 'k06_gather') a = PERM.slice();
  else if (k === 'k07_hist') { let q = 777; a = a.map(() => { q = (q * 1103515245 + 12345) & 0x7fffffff; return 6 + (q >> 8) % 9; }); } // the counters: few cells, hit again and again
  else if (k === 'k08_matmul') a = a.map((i) => 4 + (i % 8)); // the inner loop walks the same row of c once for every k
  return a;
}
function plan(k, on, cls) {
  const A = order(k), n = A.length, steps = [];
  const simdOk = cls === 'lost' || cls === 'kept';
  if (!on) {
    if (simdOk) for (let i = 0; i < n; i += LANES) steps.push({ el: A.slice(i, i + LANES), simd: true, chk: false });
    else for (const e of A) steps.push({ el: [e], simd: false, chk: false });
  } else if (cls === 'lost' || !simdOk) {
    for (const e of A) steps.push({ el: [e], simd: false, chk: true });
  } else {
    const tail = k === 'k01_sum_fwd' ? 0 : LANES, body = n - tail; // the forward sum: the compiler removes the check
    for (let i = 0; i < body; i += LANES) steps.push({ el: A.slice(i, i + LANES), simd: true, chk: false });
    for (const e of A.slice(body)) steps.push({ el: [e], simd: false, chk: true });
  }
  return steps;
}
function shade(hex, f) { // darken (f<1) or lighten (f>1) a #rrggbb colour
  const m = /^#([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) return hex;
  const n = parseInt(m[1], 16), c = [n >> 16, (n >> 8) & 255, n & 255].map((v) => clamp(Math.round(f < 1 ? v * f : v + (255 - v) * (f - 1)), 0, 255));
  return `rgb(${c.join(',')})`;
}
function palette(host) {
  const s = getComputedStyle(host);
  const g = (n, d) => s.getPropertyValue(n).trim() || d;
  return { lost: g('--cv-lost', '#c2461e'), kept: g('--cv-kept', '#1f5aa6'), chk: g('--cv-chk', '#fcefb4'), chkEdge: g('--cv-chk-edge', '#8a6d00'),
    slate: g('--cv-slate', '#5b6676'), empty: g('--cv-empty', '#e3e7ef'), emptyEdge: g('--cv-empty-edge', '#c5ccd8'), plate: g('--cv-plate', '#eceff5'),
    ink: g('--cv-ink', '#16202f'), ink2: g('--cv-ink2', '#44505f'), ink3: g('--cv-ink3', '#5b6676') };
}
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h); }
function progress(steps, prog) {
  const n = steps.length, pos = clamp(prog, 0, 1) * n, ci = Math.min(n - 1, Math.floor(pos));
  const frac = prog >= 1 ? 1 : pos - ci, m = new Map();
  for (let i = 0; i < n; i++) if (i < ci || (i === ci && frac > 0.55) || prog >= 1) for (const e of steps[i].el) m.set(e, steps[i]);
  return { m, ci, frac, cur: steps[ci], fin: prog >= 1 };
}
function fillOf(P, stp, on, cls) {
  if (stp.simd) return P.kept;
  if (on && cls === 'lost') return P.lost;
  if (on && cls === 'kept') return P.kept;
  return P.slate;
}

/* variant 1: two lanes on a light track, tiles with a visible thickness, a finish line */
function drawLanes(ctx, W, H) {
  const P = R.pal, on = R.on, cls = R.info.cls, phone = W < 520;
  ctx.clearRect(0, 0, W, H);
  const padL = phone ? 34 : 78, padR = phone ? 36 : 44, sh = -0.26, gap = 3;
  const aw = W - padL - padR - 30 - 6;
  const s = Math.min(27, (aw - (N - 1) * gap) / N), th = s * 0.62, dp = 5;
  if (!(s >= 3)) return;
  const pOff = RM() ? 1 : clamp(R.t / R.dOff, 0, 1), pOn = !on ? 0 : (RM() ? 1 : clamp(R.t / R.dOn, 0, 1));
  const laneY = [H * 0.27, H * 0.73];
  const lane = (li, steps, prog, active, label) => {
    const y0 = laneY[li] - th / 2;
    const g = progress(steps, prog);
    const tw = N * (s + gap) - gap;
    ctx.save();
    ctx.globalAlpha = active ? 1 : 0.5;
    ctx.translate(padL + 8, y0);
    ctx.transform(1, 0, sh, 1, 0, 0);
    ctx.fillStyle = shade(P.plate, 0.9); rr(ctx, -8, -9 + 5, tw + 36, th + dp + 18, 7); ctx.fill();
    ctx.fillStyle = P.plate; rr(ctx, -8, -9, tw + 36, th + dp + 18, 7); ctx.fill();
    for (let e = 0; e < N; e++) {
      const d = g.m.get(e), live = steps.some((q) => q.el.includes(e));
      const isCur = !g.fin && active && g.cur.el.includes(e) && !d;
      const lift = isCur ? -3 : 0, x = e * (s + gap);
      let top, side, edge = null;
      if (d) { top = fillOf(P, d, on && li === 1, cls); side = shade(top, 0.72); }
      else { top = P.empty; side = P.emptyEdge; if (live && active) edge = P.emptyEdge; }
      ctx.fillStyle = side; rr(ctx, x, y0 * 0 + dp + lift, s, th, 3); ctx.fill();
      ctx.fillStyle = top; rr(ctx, x, lift, s, th, 3); ctx.fill();
      if (edge) { ctx.strokeStyle = edge; ctx.lineWidth = 1; rr(ctx, x + .5, lift + .5, s - 1, th - 1, 3); ctx.stroke(); }
      if (d && d.chk && li === 1) { ctx.fillStyle = P.chk; ctx.strokeStyle = P.chkEdge; ctx.lineWidth = 1; rr(ctx, x + s / 2 - 3, th + 0.5, 6, 3.5, 1); ctx.fill(); ctx.stroke(); }
    }
    if (active && !g.fin && g.cur) { // the cursor: a beam over the SIMD group, or one raised tile with a gate
      const xs = g.cur.el.map((e) => e * (s + gap)), l = Math.min(...xs) - 2, r = Math.max(...xs) + s + 2;
      if (g.cur.simd) {
        ctx.fillStyle = 'rgba(31,90,166,.16)'; ctx.strokeStyle = P.kept; ctx.lineWidth = 1.5;
        rr(ctx, l, -13, r - l, th + 13 + 6, 5); ctx.fill(); ctx.stroke();
      } else {
        ctx.strokeStyle = li === 1 && on && cls === 'lost' ? P.lost : P.ink; ctx.lineWidth = 1.6;
        rr(ctx, l, -7, r - l, th + 7 + 4, 4); ctx.stroke();
        if (g.cur.chk && g.frac < 0.55) { // the gate the element must pass first
          const gx = (l + r) / 2;
          ctx.fillStyle = P.chk; ctx.strokeStyle = P.chkEdge; ctx.lineWidth = 1.4;
          rr(ctx, gx - 9, -20, 18, 7, 2); ctx.fill(); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(gx - 7, -13); ctx.lineTo(gx - 7, -7); ctx.moveTo(gx + 7, -13); ctx.lineTo(gx + 7, -7); ctx.stroke();
        }
      }
    }
    const fx0 = tw + 14, rows = 6, ch = (th + dp + 14) / rows; // finish line: a checkered strip
    for (let q = 0; q < rows; q++) for (let c = 0; c < 2; c++) { ctx.fillStyle = (q + c) % 2 ? P.ink : '#ffffff'; ctx.fillRect(fx0 + c * 5, -7 + q * ch, 5, ch); }
    ctx.strokeStyle = P.ink; ctx.lineWidth = 1; ctx.strokeRect(fx0 + .5, -6.5, 9, rows * ch - 1);
    ctx.restore();
    ctx.fillStyle = P.ink2; ctx.font = '13px "Source Serif 4", Georgia, serif'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
    ctx.fillText(label, 6, laneY[li] + 1);
    if (g.fin && active) { // arrived: the time it took, as a multiple of the unchecked run
      ctx.font = '600 13px "IBM Plex Mono", monospace'; ctx.textAlign = 'right'; ctx.fillStyle = li === 1 && cls === 'lost' ? P.lost : P.ink;
      ctx.fillText(li === 0 ? '1×' : (R.info.ratio == null ? '' : `${fx(R.info.ratio)}×`), W - 4, laneY[li] + 1);
    }
  };
  lane(0, R.stepsOff, pOff, true, phone ? 'off' : 'check off');
  lane(1, R.stepsOn, pOn, on, phone ? 'on' : 'check on');
}

/* variant 2: the access pattern as arcs between visited cells, on paper */
function drawArcs(ctx, W, H) {
  const P = R.pal, on = R.on, cls = R.info.cls;
  ctx.clearRect(0, 0, W, H);
  const pad = 6, gap = 3;
  const s = Math.min(30, (W - 2 * pad - (N - 1) * gap) / N);
  if (!(s >= 3)) return;
  const x0 = (W - (N * s + (N - 1) * gap)) / 2, X = (i) => x0 + i * (s + gap) + s / 2;
  const yRow = H - s - 6, maxH = yRow - 22;
  ctx.fillStyle = P.ink3; ctx.font = '12px "Source Serif 4", Georgia, serif'; ctx.textBaseline = 'top'; ctx.textAlign = 'left';
  const chk = R.on && R.info.cls !== 'none';
  const labels = [`order the loop reaches the elements, check ${R.on ? 'on' : 'off'}${chk ? ' (yellow: a check)' : ''}`, `order of visits, check ${R.on ? 'on' : 'off'}${chk ? ' (yellow: a check)' : ''}`, `order of visits, check ${R.on ? 'on' : 'off'}`, 'order of visits'];
  ctx.fillText(labels.find((t) => ctx.measureText(t).width <= W - 4) || labels[labels.length - 1], 2, 0); // never clipped by the canvas edge
  const steps = R.steps, prog = RM() ? 1 : clamp(R.t / R.D, 0, 1);
  const g = progress(steps, prog);
  const node = (q) => q.el.reduce((a, e) => a + X(e), 0) / q.el.length;
  const col = on && cls === 'lost' ? P.lost : P.kept;
  ctx.lineWidth = 1.5;
  const upto = g.fin ? steps.length - 1 : g.ci;
  for (let i = 1; i <= upto; i++) {
    const a = node(steps[i - 1]), b = node(steps[i]), dx = Math.abs(b - a), h = Math.min(maxH, 7 + dx * 0.34);
    ctx.strokeStyle = col; ctx.globalAlpha = 0.62;
    ctx.beginPath(); ctx.moveTo(a, yRow - 1); ctx.quadraticCurveTo((a + b) / 2, yRow - 1 - h * 2, b, yRow - 1); ctx.stroke();
    ctx.globalAlpha = 1;
    if (steps[i].chk) { const ay = yRow - 1 - h; ctx.fillStyle = P.chk; ctx.strokeStyle = P.chkEdge; ctx.lineWidth = 1.2; rr(ctx, (a + b) / 2 - 4, ay - 3, 8, 6, 1.5); ctx.fill(); ctx.stroke(); ctx.lineWidth = 1.5; }
  }
  for (let e = 0; e < N; e++) {
    const d = g.m.get(e), live = steps.some((q) => q.el.includes(e));
    rr(ctx, X(e) - s / 2, yRow, s, s * 0.78, Math.min(4, s / 4));
    if (d) { ctx.fillStyle = fillOf(P, d, on, cls); ctx.fill(); }
    else { ctx.fillStyle = live ? P.empty : '#f4f6fa'; ctx.fill(); ctx.strokeStyle = P.emptyEdge; ctx.lineWidth = 1; ctx.stroke(); }
  }
  if (!g.fin && g.cur) { const cxn = node(g.cur); ctx.fillStyle = P.ink; ctx.beginPath(); ctx.arc(cxn, yRow - 5, 4, 0, 7); ctx.fill(); }
}

/* variant 3: the lens over the array on graphite (the earlier drawing, kept: a CPU box and the elements) */
function drawLens(ctx, W, H) {
  const P = R.pal, on = R.on, cls = R.info.cls;
  ctx.clearRect(0, 0, W, H);
  const steps = R.steps, prog = RM() ? 1 : clamp(R.t / R.D, 0, 1);
  const pad = 10, gap = 3, s = Math.min(34, (W - 2 * pad - (N - 1) * gap) / N);
  if (!(s >= 3)) return;
  const x0 = (W - (N * s + (N - 1) * gap)) / 2, X = (i) => x0 + i * (s + gap);
  const g = progress(steps, prog), yRow = H - s - 14, up = H < 84 ? 28 : 40;
  for (let e = 0; e < N; e++) {
    const d = g.m.get(e), live = steps.some((q) => q.el.includes(e));
    rr(ctx, X(e), yRow, s, s, Math.min(4, s / 4));
    if (d) { ctx.fillStyle = fillOf(P, d, on, cls) === P.slate ? 'rgba(255,255,255,.8)' : fillOf(P, d, on, cls); ctx.fill(); }
    else { ctx.fillStyle = live ? 'rgba(255,255,255,.10)' : 'rgba(255,255,255,.03)'; ctx.fill(); ctx.strokeStyle = live ? 'rgba(255,255,255,.34)' : 'rgba(255,255,255,.12)'; ctx.lineWidth = 1; ctx.stroke(); }
    if (d && d.chk) { ctx.fillStyle = P.chk; ctx.fillRect(X(e) + s / 2 - 2.5, yRow + s + 4, 5, 3); }
  }
  const cur = g.cur, xs = cur.el.map(X), l = Math.min(...xs) - 4, r = Math.max(...xs) + s + 4, w = r - l;
  const ly = yRow - up, lh = s + up - 2;
  ctx.globalAlpha = g.fin ? 0.55 : 1;
  ctx.fillStyle = 'rgba(255,255,255,.07)'; ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 2;
  rr(ctx, l, ly, w, lh, 9); ctx.fill(); ctx.stroke();
  ctx.fillStyle = 'rgba(255,255,255,.55)'; rr(ctx, (l + r) / 2 - 3, ly + lh, 6, 8, 2); ctx.fill();
  ctx.globalAlpha = 1;
  if (!g.fin && cur.chk && g.frac < 0.55) { const ex = (l + r) / 2; ctx.fillStyle = P.chk; rr(ctx, ex - 10, ly - 12, 20, 14, 3); ctx.fill(); ctx.strokeStyle = '#3a3000'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(ex - 5, ly - 5); ctx.lineTo(ex - 1, ly - 1); ctx.lineTo(ex + 6, ly - 10); ctx.stroke(); }
  const slot = (w - 12) / cur.el.length;
  for (let q = 0; q < cur.el.length; q++) {
    ctx.fillStyle = g.fin ? 'rgba(255,255,255,.25)' : (g.frac > 0.55 ? (cur.simd ? P.kept : (on && cls === 'lost' ? P.lost : '#fff')) : 'rgba(255,255,255,.3)');
    rr(ctx, l + 6 + q * slot + 2, ly + 8, slot - 4, lh - 16 - 6, 4); ctx.fill();
  }
}

/* ---------- state ---------- */
const R = { k: null, pv: null, anims: [], on: true, t: 0, vis: true, raf: 0, last: 0, v: DEFAULT_HV, W: 0, H: 120, info: null, pal: null, codeTok: 0, asm: new Map(), ctx: null };
function infoFor(k) {
  const pc = pooledOf(currentCpu().cpu_model);
  const cell = cellOf(pc, `${k}.L1`);
  const col = column(cell) || (cell && cell.as_compiled) || null;
  const limPct = (pc && pc.verdict && pc.verdict.forward_limit_pct) || 2;
  const ps = !!(cell && pc && pc.verdict && (pc.verdict.placement_sensitive || []).some((p) => p.cell_id === cell.cell_id));
  // a forward loop the written rule leaves out because code placement moves it, and that sits above the limit: its number needs saying so
  return { cell, col, cls: cell ? role(cell) : 'none', ratio: col ? col.ratio : null, jobs: col ? col.jobs : null, limPct, left: ps && !!col && col.ratio > 1 + limPct / 100 };
}
function plansFor() {
  const i = R.info, rc = i.ratio == null ? 1 : clamp(i.ratio, RMIN, RMAX);
  R.stepsOff = plan(R.k, false, i.cls);
  R.stepsOn = plan(R.k, true, i.cls);
  R.steps = R.on ? R.stepsOn : R.stepsOff;
  R.dOff = T0; R.dOn = T0 * rc;
  R.D = R.on ? (R.v === 1 ? Math.max(R.dOff, R.dOn) : R.dOn) : R.dOff;
}
function frame() {
  if (R.v === 4) return; // the lanes are drawn in the page (layout4, run4), not on the canvas
  const cv = $('race-cv'), ctx = cv.getContext('2d'), dpr = cv.width / (R.W || 1);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  if (R.v === 1) drawLanes(ctx, R.W, R.H);
  else if (R.v === 2) drawArcs(ctx, R.W, R.H);
  else drawLens(ctx, R.W, R.H);
}
function loop(now) {
  R.raf = 0;
  if (!R.vis || document.hidden || RM()) return;
  const dt = Math.min(0.05, (now - R.last) / 1000 || 0);
  R.last = now;
  R.t = Math.min(R.D, R.t + dt);
  frame();
  if (R.t < R.D) R.raf = requestAnimationFrame(loop); // one run, then it rests on the final frame
}
function kick() { if (R.raf || RM() || !R.vis || document.hidden || R.t >= R.D) return; R.last = performance.now(); R.raf = requestAnimationFrame(loop); }
function sizeCanvas() {
  const cv = $('race-cv'), w = Math.floor(cv.parentElement.clientWidth);
  if (w < 120) return;
  const dpr = Math.min(2, devicePixelRatio || 1), phone = innerWidth < 641;
  setN();
  R.W = w; R.H = R.v === 1 ? (phone ? 112 : 150) : R.v === 2 ? (phone ? 78 : 112) : (phone ? 80 : 108);
  cv.width = Math.round(w * dpr); cv.height = Math.round(R.H * dpr);
  cv.style.height = `${R.H}px`;
  R.pal = palette($('race'));
  if (R.steps) frame();
}

/* ---------- the readout (the same words and numbers in every variant) ---------- */
const WHAT = { // the generic wording per outcome, used when a loop has no sentence of its own
  lost: 'The loop loses SIMD: it steps one element at a time, with a check before each.',
  kept: 'The loop keeps SIMD; the check only rides on the leftover tail.',
  none: 'No SIMD in either build; the check adds work to every element.',
};
/* One sentence per loop, in the wording of the data (the compiler's own remarks, Figure 2's reading). Each loop
   has its own: the reverse-loop story is told only for the reverse loop. */
const CAP = {
  k01_sum_fwd: { kept: 'Both builds are vectorized and, with the check on, the compiler removes the check altogether: nothing is left to pay for.' },
  k02_add_fwd: { kept: 'Both builds are vectorized; the check runs only on the leftover elements.', keptBelow: ' Below 1×: the checked loop happens to run faster (cause inferred; section 3).' },
  k03_stencil: { kept: 'Both builds are vectorized; the compiler tests the sizes once before the SIMD loop, so the check runs only on the leftover elements.' },
  k04_rev: { lost: 'Clang 18 could not vectorize it with the check inside.', novec: true },
  k05_stride2: { lost: 'Clang 18 gives the same remark as the reverse loop.', novec: true },
  k06_gather: { none: 'Not vectorized in either build, so there is no SIMD to lose; the check adds a compare and a jump to every pass over the index list.' },
  k07_hist: { none: 'Not vectorized in either build, so there is no SIMD to lose; the check adds a compare and a jump to every pass over the input.' },
  k08_matmul: { lost: 'On clang 18 the remark says vectorizing is not beneficial. Clang 19 to 21 keep SIMD yet cost 1.6× at L1 (EPYC 7763, timed); 23.1 and trunk lose it (compile-only).' },
};
function capFor(k, i, plain) { // plain: the sentence without the no-vectorize clause (the mechanism demo's caption stays short; the hero and the drawer carry the clause)
  const c = CAP[k] || {};
  const t = c[i.cls] || WHAT[i.cls] || WHAT.none;
  return t + (!plain && i.cls === 'lost' && c.novec ? novecClause(k, pooledOf(currentCpu().cpu_model), true) : '') + (c.keptBelow && i.cls === 'kept' && i.ratio != null && i.ratio < 0.95 ? c.keptBelow : '')
    + (!plain && i.cls === 'kept' && i.left ? ` Left out of the ${+i.limPct.toFixed(1)}% rule (‡).` : '');
}
function gaugeSvg() {
  const pos = (v) => (Math.log(clamp(v, 0.5, 10)) - Math.log(0.5)) / (Math.log(10) - Math.log(0.5));
  const pt = (p, r) => { const a = Math.PI * (1 - p); return [100 + r * Math.cos(a), 100 - r * Math.sin(a)]; };
  let ticks = '';
  for (const v of [1, 2, 4, 8]) { const [x1, y1] = pt(pos(v), 66), [x2, y2] = pt(pos(v), 76), [tx, ty] = pt(pos(v), 90); ticks += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="gt"/><text x="${tx}" y="${ty + 3}" text-anchor="middle" class="gl-t">${v}×</text>`; }
  const [ax, ay] = pt(0, 70), [bx, by] = pt(1, 70);
  return `<svg class="gauge" viewBox="0 0 200 116" aria-hidden="true" focusable="false"><path class="g-track" d="M${ax} ${ay}A70 70 0 0 1 ${bx} ${by}"/><path class="g-fill" id="g-fill" d=""/>${ticks}<g id="g-needle" class="g-needle"><line x1="100" y1="100" x2="34" y2="100"/><circle cx="100" cy="100" r="5"/></g></svg>`;
}
function setGauge(ratio, cls) {
  const f = $('g-fill'), n = $('g-needle');
  if (!f || !n) return;
  const pos = (v) => (Math.log(clamp(v, 0.5, 10)) - Math.log(0.5)) / (Math.log(10) - Math.log(0.5));
  const pt = (p, r) => { const a = Math.PI * (1 - p); return [100 + r * Math.cos(a), 100 - r * Math.sin(a)]; };
  const v = ratio == null || !R.on ? 1 : ratio, p1 = pos(1), p2 = pos(v);
  const [ax, ay] = pt(Math.min(p1, p2), 70), [bx, by] = pt(Math.max(p1, p2), 70);
  f.setAttribute('d', Math.abs(p2 - p1) < 0.004 ? '' : `M${ax} ${ay}A70 70 0 0 1 ${bx} ${by}`);
  f.setAttribute('class', `g-fill ${cls === 'lost' ? 'lost' : 'kept'}`);
  n.style.transform = `rotate(${(180 * p2).toFixed(1)}deg)`;
}
async function renderCode() {
  const box = $('hv-code');
  if (!box || R.v !== 3) return;
  const my = ++R.codeTok, cpu = currentCpu(), f = cpu.asm;
  const head = `<div class="hc-h"><span>${R.on ? 'Checks on' : 'Checks off'}</span><code>${R.on ? '_LIBCPP_HARDENING_MODE_FAST' : '_LIBCPP_HARDENING_MODE_NONE'}</code></div>`;
  if (!f) { box.innerHTML = `${head}<p class="hc-n">No machine code for this data.</p>`; return; }
  const cell = cellOf(pooledOf(cpu.cpu_model), `${R.k}.L1`);
  const sfx = S.col === 'aligned' && cell && cell.aligned ? '_a64' : '';
  const url = `${f.dir}${R.k}.${R.on ? 'fast' : 'none'}${sfx}.s`;
  let an = R.asm.get(url);
  if (!an) {
    try { an = analyse(parseListing(await getText(url))); R.asm.set(url, an); }
    catch (err) { if (my === R.codeTok) box.innerHTML = `${head}<p class="hc-n">The machine code did not load.</p>`; return; }
  }
  if (my !== R.codeTok) return;
  const keep = excerpt(an), chk = new Set(an.checks.flat());
  const shown = an.lines.filter((x) => keep.has(x.addr) && !x.pad);
  const MAXL = innerWidth < 641 ? 3 : 10;
  const part = shown.slice(0, MAXL), more = shown.length - part.length;
  const esc = (t) => t.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  box.innerHTML = head + '<pre class="hc-pre" tabindex="0" aria-label="The hot loop, as clang compiled it">' + part.map((x) => {
    const c = x.trap ? 'trap' : chk.has(x.addr) ? 'chk' : x.simd ? 'simd' : '';
    return `<span class="ln ${c}">${esc(x.mnem.padEnd(7))} ${esc(x.ops)}</span>`;
  }).join('') + (more > 0 ? `<span class="ln gap">⋯ ${more} more in the full view</span>` : '') + '</pre>';
}
function setFavicon(cls) { // the tab icon shows the selected loop's verdict: orange = loses SIMD, blue = keeps it, grey = baseline
  const link = document.querySelector('link[rel="icon"]');
  if (!link) return;
  const col = { lost: '%23c2461e', kept: '%231f5aa6' }[cls] || '%23727272';
  link.href = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='4' fill='%23fff' stroke='%231b1b1b' stroke-width='2'/%3E%3Cpath d='M7 22h4l3-12 4 14 3-9h4' fill='none' stroke='${col}' stroke-width='2.4' stroke-linejoin='round'/%3E%3C/svg%3E`;
}
function paintText(k) { // the name, the big ratio and the sentence for loop k: the selected loop, or the one under the pointer
  const i = k === R.k && R.info ? R.info : infoFor(k), cpu = currentCpu(), name = KERNEL_NAMES[k];
  const src = S.ix.kernel_source && S.ix.kernel_source[k];
  $('race-name').textContent = `${name}: read the machine code`;
  $('race-name').setAttribute('aria-label', `${name}: open the machine code, checks off and on`);
  $('race-src').textContent = src ? srcLine(src.text) : '';
  const big = $('race-ratio'), sub = $('race-sub');
  const mk = (cls, text) => Object.assign(document.createElement('span'), { className: cls, textContent: text });
  const head = (meta) => { const h = mk('rr-head', ''); h.append(Object.assign(document.createElement('b'), { className: 'rr-nm', textContent: `${SHORT_NAMES[k].replace(/^./, (c) => c.toUpperCase())}: ` }), mk('rr-meta', meta)); return h; };
  if (i.ratio == null) { big.textContent = 'n/a'; sub.replaceChildren(head('not measured on this CPU model.')); }
  else if (!R.on) { big.textContent = 'Baseline'; sub.replaceChildren(head('the check is off. Switch it on to see what it costs.')); }
  else {
    big.textContent = `${fx(i.ratio)}×`;
    const what = mk('rr-what', capFor(k, i));
    if (i.left) what.title = '‡ placement-sensitive: moving the loop’s code changes its ratio by more than noise, so the forward test leaves it out (section 3). It can still sit above 1× when aligned.';
    sub.replaceChildren(head(`${fx(i.ratio)}× as long as with the check off, ${cpu.cpu_short}, ${i.jobs} jobs. `), what);
  }
  if (R.shown !== big.textContent && R.shown != null && !RM() && big.animate) big.animate([{ opacity: 0.35 }, { opacity: 1 }], { duration: 160, easing: 'cubic-bezier(.25,1,.5,1)' }); // a swap, never a count-up
  R.shown = big.textContent;
  big.classList.toggle('lost', R.on && i.cls === 'lost');
  big.classList.toggle('base', !R.on || i.ratio == null);
  big.classList.toggle('kept', R.on && i.cls !== 'lost');
}

/* variant 4: the whole map in one race. Eight lanes, two bars each (check off, check on); a bar is as long as the
   measured pooled ratio (time), on one shared axis, so the unchecked finish is a single vertical line. */
const AX_TICKS = (max) => (max < 3 ? [0.5, 1, 1.5, 2, 2.5] : max < 6 ? [1, 2, 3, 4, 5] : [1, 2, 4, 8]).filter((v) => v <= max * 0.995);
function layout4(infos) {
  const ks = Object.keys(infos), rs = ks.map((k) => infos[k].ratio).filter((v) => v != null);
  const max = Math.max(1.3, ...rs) * 1.04, pct = (v) => (100 * v) / max;
  R.axisMax = max;
  const ticks = AX_TICKS(max);
  for (const b of $('race-loops').children) {
    const k = b.dataset.k, i = infos[k], tracks = b.querySelector('.ln-tracks');
    const simdOff = i.cls === 'lost' || i.cls === 'kept';
    const offT = tracks.querySelector('.ln-t.off'), onT = tracks.querySelector('.ln-t.on');
    offT.dataset.m = simdOff ? 'simd' : 'one';
    onT.dataset.m = i.cls === 'kept' ? 'simd' : 'one chk';
    const clip = (v) => `inset(0 ${(100 - Math.min(100, pct(v))).toFixed(2)}% 0 0 round 3px)`;
    b.style.setProperty('--w-off', `${pct(1).toFixed(2)}`);
    offT.firstChild.style.clipPath = clip(1);
    onT.hidden = i.ratio == null;
    if (i.ratio != null) {
      b.style.setProperty('--w-on', `${pct(i.ratio).toFixed(2)}`);
      onT.firstChild.style.clipPath = clip(i.ratio);
      const cap = onT.querySelector('.ln-cap');
      cap.hidden = !(i.cls === 'kept' && k !== 'k01_sum_fwd');
      cap.style.left = `calc(${pct(i.ratio).toFixed(2)}% - 7px)`;
    }
    for (const l of tracks.querySelectorAll('.ln-lbl')) l.hidden = true;
    const grid = tracks.querySelector('.ln-grid');
    grid.replaceChildren(...ticks.map((v) => Object.assign(document.createElement('i'), { className: v === 1 ? 'one' : '', style: `left:${pct(v).toFixed(2)}%` })));
  }
  // direct labels on the bars themselves (wide screens): the first lane names the unchecked bar, and one lane per outcome names the checked bar, where the track is empty
  let col = pct(1); // the labels share one left edge: right of the longest of the labelled bars, so they never sit on a bar or the 1x line
  const lbl = (k, kind, text, len) => { const l = $('race-loops').querySelector(`button[data-k="${k}"] .ln-t.${kind} .ln-lbl`); if (!l || len > 62) return; l.textContent = text; l.dataset.len = String(Math.max(len, pct(1))); col = Math.max(col, len); l.hidden = false; };
  const shortest = (cls) => ks.filter((k) => infos[k].cls === cls && infos[k].ratio != null).sort((a, b) => infos[a].ratio - infos[b].ratio)[0];
  lbl(ks[0], 'off', 'check off', pct(1));
  for (const [cls, text] of [['kept', 'check on, keeps SIMD'], ['lost', 'check on, loses SIMD'], ['none', 'check on, no SIMD to lose']]) { const k = shortest(cls); if (k) lbl(k, 'on', text, pct(infos[k].ratio)); }
  for (const l of $('race-loops').querySelectorAll('.ln-lbl:not([hidden])')) l.style.left = `calc(${col.toFixed(2)}% + 12px)`;
  const ax = $('race-axis');
  ax.replaceChildren(...ticks.map((v) => Object.assign(document.createElement('span'), { className: v === 1 ? 'one' : '', style: `left:${pct(v).toFixed(2)}%`, textContent: `${v}×` })));
}
function run4() { // the one run: every bar grows from the start; short ones finish first, the long ones lag
  for (const a of R.anims || []) a.cancel();
  R.anims = [];
  const loops = [...$('race-loops').children];
  if (RM()) { // no movement: a short fade of the bars shows that the click was received
    for (const t of $('race-loops').querySelectorAll('.ln-t')) {
      if (t.hidden || !t.firstChild) continue;
      const a = t.firstChild.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 450, easing: 'ease-out', fill: 'backwards' });
      a.onfinish = () => { R.anims = R.anims.filter((x) => x !== a); };
      R.anims.push(a);
    }
    return;
  }
  const maxLen = Math.max(...loops.map((b) => parseFloat(b.style.getPropertyValue('--w-on')) || 0), 1);
  const done = (a) => { a.onfinish = () => { R.anims = R.anims.filter((x) => x !== a); }; R.anims.push(a); };
  for (const b of loops) {
    for (const kind of ['off', 'on']) {
      if (kind === 'on' && !R.on) continue;
      const t = b.querySelector(`.ln-t.${kind}`);
      const len = parseFloat(b.style.getPropertyValue(`--w-${kind}`));
      if (!len || t.hidden) continue;
      const to = t.firstChild.style.clipPath, dur = 260 + 940 * (len / maxLen);
      done(t.firstChild.animate([{ clipPath: 'inset(0 100% 0 0 round 3px)' }, { clipPath: to }], { duration: dur, easing: 'cubic-bezier(.25,.6,.35,1)', fill: 'backwards' }));
      if (kind === 'on') done(b.querySelector('.tr').animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160, delay: Math.max(0, dur - 120), fill: 'backwards' }));
    }
  }
}
function preview(k) { // the pointer or focus on a lane: highlight it and show its sentence in the fixed caption area
  if (R.v !== 4) k = null;
  const pv = k && k !== R.k ? k : null;
  for (const b of $('race-loops').children) b.classList.toggle('hl', !!k && b.dataset.k === k);
  if (pv === (R.pv || null)) return;
  R.pv = pv;
  document.querySelector('#race .race-read').setAttribute('aria-live', pv ? 'off' : 'polite'); // a pointer preview is not announced; a real selection is
  paintText(R.pv || R.k);
}

function readout() {
  const i = R.info = infoFor(R.k), name = KERNEL_NAMES[R.k];
  if (R.v !== 4) R.pv = null;
  paintText(R.pv || R.k);
  setFavicon(R.on && i.ratio != null ? i.cls : 'none');
  $('race-cv').setAttribute('aria-label', `Illustration: ${name} processed with the check ${R.on ? 'on' : 'off'}, drawn to the measured ratio`);
  const c = $('race-cap'), build = S.col === 'aligned' ? 'aligned build' : 'as-compiled build';
  const sample = S.pooled && S.pooled.sample ? ' SAMPLE DATA: made up, not a measurement.' : '';
  const kb = Object.assign(document.createElement('span'), { className: 'kbd-hint', textContent: ' Keys: 1 to 8 pick a loop, C flips the check.' });
  if (R.v === 4) {
    c.replaceChildren('Illustration: each bar is as long as the measured pooled ratio', Object.assign(document.createElement('span'), { className: 'more', textContent: ` (${build}, smallest size)` }),
      ' on one shared axis, which rescales to the longest bar of each CPU model; only the speed of the run is for show. The number is the measurement.' + sample, kb);
  } else {
    c.replaceChildren('Illustration scaled to the measured pooled ratio', Object.assign(document.createElement('span'), { className: 'more', textContent: ` (${build}, smallest size)` }),
      (i.ratio != null && (i.ratio > RMAX || i.ratio < RMIN) ? ', clamped to stay watchable' : '') + '; the number is the measurement.' + sample, kb);
  }
  const infos = {};
  for (const b of $('race-loops').children) { // tiles and lanes: the loop's own measured ratio, tinted by what the check does to it
    const on = b.dataset.k === R.k, ii = infos[b.dataset.k] = infoFor(b.dataset.k);
    b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1;
    b.dataset.role = ii.cls;
    b.querySelector('.tr').textContent = ii.ratio == null ? 'n/a' : (R.on ? `${fx(ii.ratio)}×` : '1.00×'); // check off = the unchecked run, the baseline
    b.setAttribute('aria-label', `${SHORT_NAMES[b.dataset.k]}: ${ii.ratio == null ? 'not measured on this CPU model' : `${fx(ii.ratio)} times as long with the check on`}`);
  }
  for (const b of $('race-cpu').children) { const on = b.dataset.cpu === S.cpu; b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1; }
  const sw = $('race-sw'); sw.setAttribute('aria-checked', R.on); $('race-sw-w').textContent = R.on ? 'on' : 'off';
  $('race').classList.toggle('is-on', R.on);
  $('race').dataset.role = i.cls;
  setGauge(i.ratio, i.cls);
  layout4(infos);
  plansFor();
  renderCode();
}
function show() { cancelAnimationFrame(R.raf); R.raf = 0; for (const a of R.anims || []) a.cancel(); R.anims = []; readout(); R.t = R.D; frame(); }
function play() { cancelAnimationFrame(R.raf); R.raf = 0; readout(); R.t = 0; frame(); kick(); if (R.v === 4) run4(); }

/* ---------- variant switching ---------- */
function hashVariant() { const m = /(?:^|[#&])hero=([1234])(?:&|$)/.exec(location.hash); return m ? +m[1] : null; }
function applyVariant(n, quiet) {
  R.v = n;
  const box = $('race');
  box.dataset.hv = String(n);
  document.documentElement.dataset.hv = String(n);
  for (const b of document.querySelectorAll('.hv-switch button')) b.setAttribute('aria-pressed', String(+b.dataset.v === n));
  if (R.k) { sizeCanvas(); quiet ? show() : play(); }
}
function setVariantHash(n) {
  const h = new URLSearchParams(location.hash.slice(1));
  h.set('hero', String(n));
  history.replaceState(null, '', `${location.pathname}${location.search}#${h}`);
}
function buildSwitcher() {
  const el = document.createElement('div');
  el.className = 'hv-switch'; el.setAttribute('role', 'group'); el.setAttribute('aria-label', 'Hero variant');
  el.hidden = !/hero/.test(location.hash);
  el.innerHTML = '<span>Hero:</span>';
  for (const n of [1, 2, 3, 4]) {
    const b = document.createElement('button');
    b.type = 'button'; b.dataset.v = n; b.textContent = String(n); b.setAttribute('aria-label', `Hero variant ${n}`);
    b.addEventListener('click', () => { setVariantHash(n); applyVariant(n); });
    el.append(b);
  }
  const bar = $('bar'); // the switcher lives in the top bar, where it can never cover text
  bar.insertBefore(el, bar.querySelector('.bar-details') || null);
  document.addEventListener('keydown', (e) => {
    if ((e.key === 'h' || e.key === 'H') && !e.ctrlKey && !e.metaKey && !e.altKey && !/^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || ''))) el.hidden = !el.hidden;
  });
  document.addEventListener('keydown', (e) => { // 1 to 8 pick a loop, C flips the check; never while typing, never with a modifier
    if (e.ctrlKey || e.metaKey || e.altKey || /^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || '')) || document.querySelector('.slideover.open')) return;
    const ks = Object.keys(S.ix.criteria.kernels);
    if (/^[1-8]$/.test(e.key) && ks[+e.key - 1]) { select(ks[+e.key - 1], false, true); }
    else if (e.key === 'c' || e.key === 'C') { R.on = !R.on; show(); }
  });
  /* print: a static, light poster whatever the screen variant is (the bars are CSS backgrounds, which printers drop; the poster is drawn) */
  const pm = matchMedia('print'); let before = null;
  const toPrint = () => { if (before == null) { before = R.v; R.on = true; applyVariant(2, true); } };
  const fromPrint = () => { if (before != null) { const v = before; before = null; applyVariant(v, true); } };
  addEventListener('beforeprint', toPrint); addEventListener('afterprint', fromPrint);
  pm.addEventListener('change', (e) => (e.matches ? toPrint() : fromPrint()));
  addEventListener('hashchange', () => { const v = hashVariant(); if (v && v !== R.v) applyVariant(v); if (/hero/.test(location.hash)) el.hidden = false; });
}

/* ---------- the Reproduce button: the one-command box ---------- */
function buildRepro() {
  const btn = $('repro-btn'), box = $('repro-box');
  if (!btn || !box) return;
  const set = (on) => {
    box.hidden = !on; btn.setAttribute('aria-expanded', String(on));
    if (on) { const src = document.getElementById('cmd-check'); $('repro-cmd').textContent = src ? src.textContent : 'python scripts/check.py'; }
  };
  btn.addEventListener('click', () => set(box.hidden));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !box.hidden) { set(false); btn.focus(); } });
  document.addEventListener('click', (e) => { if (!box.hidden && !box.contains(e.target) && !btn.contains(e.target)) set(false); });
}

/* ---------- build ---------- */
function build(api) {
  const loops = $('race-loops'), cpus = $('race-cpu'), cap = (t) => t.replace(/^./, (c) => c.toUpperCase());
  loops.replaceChildren();
  for (const k of Object.keys(S.ix.criteria.kernels)) {
    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.k = k;
    b.innerHTML = `<span class="ln-tile"><svg class="gl" viewBox="0 0 64 36" aria-hidden="true" focusable="false">${GLYPH[k] || ''}</svg></span><span class="tl"></span><span class="tr" aria-hidden="true"></span>`
      + '<span class="ln-tracks" aria-hidden="true"><span class="ln-grid"></span><span class="ln-t off"><i></i><em class="ln-lbl" hidden></em></span><span class="ln-t on"><i></i><b class="ln-cap"></b><em class="ln-lbl" hidden></em></span></span>';
    b.querySelector('.tl').textContent = cap(SHORT_NAMES[k]);
    b.addEventListener('click', () => { // a lane opens the real machine code; on a touch screen the first tap shows the loop's sentence, the second opens it
      const touchFirst = R.v === 4 && matchMedia('(pointer: coarse)').matches && k !== R.k;
      select(k, false, true);
      if (R.v === 4 && !touchFirst) api.openAsm(k, b);
    });
    b.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'touch') preview(k); });
    b.addEventListener('pointerleave', () => preview(null));
    b.addEventListener('focus', () => preview(k));
    b.addEventListener('blur', () => preview(null));
    loops.append(b);
  }
  radioKeys(loops, 'k', (k) => select(k, false, true));
  cpus.replaceChildren();
  for (const c of cpuList()) {
    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.cpu = c.slug; b.textContent = c.cpu_short;
    b.title = `${c.cpu_model}: ${c.jobs} jobs pooled`;
    b.addEventListener('click', () => selectCpu(c.slug));
    cpus.append(b);
  }
  radioKeys(cpus, 'cpu', (s) => selectCpu(s));
  $('race-sw').addEventListener('click', () => { R.on = !R.on; show(); document.dispatchEvent(new Event('race-used')); });
  $('race-replay').addEventListener('click', () => play());
  $('race-name').addEventListener('click', (e) => api.openAsm(R.k, e.currentTarget));
  const rd = document.querySelector('#race .race-read');
  rd.insertAdjacentHTML('afterbegin', `<div class="hv-gauge" aria-hidden="true">${gaugeSvg()}</div>`);
  const ex = document.createElement('div'); ex.id = 'hv-code'; ex.className = 'hv-code'; ex.setAttribute('aria-live', 'off');
  $('race-cv').parentElement.after(ex);
  new ResizeObserver(() => sizeCanvas()).observe($('race-cv').parentElement);
  new IntersectionObserver((es) => { R.vis = es[0].isIntersecting; if (R.vis) kick(); }, { threshold: 0.05 }).observe($('race'));
  document.addEventListener('visibilitychange', kick);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (R.steps) frame(); }); // the lane labels are canvas text: redraw once the fonts are in
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', () => show());
  R.k = S.sel;
  buildSwitcher();
  buildRepro();
  R.v = hashVariant() || DEFAULT_HV;
  applyVariant(R.v, true);
  sizeCanvas();
  show();
  play(); // the first look: one short run
}
function sync(onlyIfChanged) { if (!R.k) return; if (onlyIfChanged && R.k === S.sel) return; R.k = S.sel; R.pv = null; show(); }
window.HeroRace = { build, sync, glyph: (k) => GLYPH[k] || '', words: (k) => capFor(k, infoFor(k), true), unhint: () => document.dispatchEvent(new Event('race-used')) };
})();
