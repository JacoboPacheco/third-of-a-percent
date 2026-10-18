// Widget 2: one up-front size check. Reads data/mitigate.json.
import { h, fx, clamp, injectCSS, loadJSON, liveRegion, segmented, field, logScale, reducedQuery, median, uid } from './common.js';

const CSS = `
.w3-mitigation .mi-main { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: 1.2rem 1.6rem; align-items: start; }
.w3-mitigation .mi-h { font-size: .78rem; color: var(--i3); margin: 0 0 .35rem; display: flex; justify-content: space-between; gap: .6rem; align-items: baseline; flex-wrap: wrap; }
.w3-mitigation .mi-tog { display: inline-flex; max-width: 100%; border: 1px solid var(--r); border-radius: 99px; padding: 3px; background: var(--hv); margin-bottom: .55rem; }
.w3-mitigation .mi-tog .w-seg { border: 0; background: transparent; border-radius: 99px; flex-wrap: nowrap; }
.w3-mitigation .mi-tog .w-seg-b { border: 0; border-radius: 99px; padding: .45rem .85rem; font-family: var(--sf); font-size: .86rem; white-space: normal; text-align: center; line-height: 1.2; }
.w3-mitigation .mi-tog .w-seg-b[aria-checked="true"] { background: var(--i); color: var(--pp); }
.w3-mitigation .mi-code { margin: 0; padding: .7rem 0; background: var(--hv); border: 1px solid var(--r2); border-radius: var(--rd); overflow-x: auto; font-family: var(--mo); font-size: .76rem; line-height: 1.55; tab-size: 2; }
.w3-mitigation .mi-line { display: block; padding: 0 .8rem; white-space: pre; border-left: 3px solid transparent; transition: background-color .2s, border-color .2s; }
.w3-mitigation .mi-line.add { background: var(--ck); border-left-color: var(--i); }
.w3-mitigation .mi-chips { display: flex; flex-wrap: wrap; gap: .3rem .4rem; margin: .55rem 0 0; }
.w3-mitigation .mi-what { font-size: .84rem; color: var(--i2); margin: .5rem 0 0; }
.w3-mitigation .mi-lane { margin: 0 0 .75rem; }
.w3-mitigation .mi-lanelabel { font-size: .8rem; color: var(--i2); margin: 0 0 .3rem; line-height: 1.3; }
.w3-mitigation .mi-lanelabel b { font-weight: 600; color: var(--i); }
.w3-mitigation .mi-belt { display: grid; grid-template-columns: repeat(16, 1fr); gap: 3px; }
.w3-mitigation .mi-cell { height: 22px; border-radius: 3px; background: var(--r2); border: 1px solid var(--r); position: relative; }
.w3-mitigation .mi-cell.on { background: var(--no); border-color: var(--no); }
.w3-mitigation .mi-cell.on.kept { background: var(--ke); border-color: var(--ke); }
.w3-mitigation .mi-cell.on.lost { background: var(--lo); border-color: var(--lo); }
.w3-mitigation .mi-cell.head { box-shadow: 0 0 0 2px var(--pp), 0 0 0 3.5px var(--i); z-index: 1; }
.w3-mitigation .mi-checks { display: grid; grid-template-columns: repeat(16, 1fr); gap: 3px; margin-top: 3px; height: 7px; }
.w3-mitigation .mi-chk { background: var(--ck); border-radius: 2px; border: 1px solid #e3d27a; }
.w3-mitigation .mi-chk.one { grid-column: 1 / 2; }
.w3-mitigation .mi-time { font-family: var(--mo); font-size: .75rem; color: var(--i3); margin-top: .25rem; }
.w3-mitigation .mi-playrow { display: flex; gap: .6rem; align-items: center; flex-wrap: wrap; }
.w3-mitigation .mi-bars { margin-top: 1.3rem; border-top: 1px solid var(--r2); padding-top: .8rem; }
.w3-mitigation .mi-brow { display: grid; grid-template-columns: 8.5rem minmax(0, 1fr) 6.6rem; gap: .5rem .8rem; align-items: center; padding: .35rem 0; }
/* the rows that are not selected are quieter, but their words keep a colour that passes 4.5:1: only the bars are faded */
.w3-mitigation .mi-btrack { transition: opacity .2s; }
.w3-mitigation .mi-brow:not(.act) .mi-btrack { opacity: .55; }
.w3-mitigation .mi-brow:not(.act) .mi-bname b, .w3-mitigation .mi-brow:not(.act) .mi-bval { color: var(--i2); }
.w3-mitigation .mi-bname { font-size: .82rem; line-height: 1.25; }
.w3-mitigation .mi-bname b { display: block; font-weight: 600; }
.w3-mitigation .mi-bname span { color: var(--i3); font-size: .75rem; }
.w3-mitigation .mi-btrack { position: relative; height: 30px; }
.w3-mitigation .mi-baxis { position: absolute; left: 0; right: 0; top: 14px; height: 2px; background: var(--r2); }
.w3-mitigation .mi-bone { position: absolute; top: 0; bottom: 0; width: 0; border-left: 1px dashed var(--i3); }
.w3-mitigation .mi-brange { position: absolute; top: 9px; height: 12px; border-radius: 3px; min-width: 4px; background: var(--no); transition: left .2s, width .2s; }
.w3-mitigation .mi-brange.kept { background: var(--ke); }
.w3-mitigation .mi-brange.lost { background: var(--lo); }
.w3-mitigation .mi-bmed { position: absolute; top: 5px; height: 20px; width: 2px; margin-left: -1px; background: var(--i); transition: left .2s; }
.w3-mitigation .mi-bdot { position: absolute; top: 12px; width: 6px; height: 6px; margin-left: -3px; border-radius: 50%; background: var(--pp); border: 1px solid var(--i); transition: left .2s; }
.w3-mitigation .mi-bval { font-family: var(--mo); font-size: .9rem; font-variant-numeric: tabular-nums; text-align: right; line-height: 1.15; }
.w3-mitigation .mi-bval small { display: block; font-size: .75rem; color: var(--i3); }
.w3-mitigation .mi-baxrow { display: grid; grid-template-columns: 8.5rem minmax(0, 1fr) 6.6rem; gap: .5rem .8rem; }
.w3-mitigation .mi-baxl { position: relative; height: 1.1rem; }
.w3-mitigation .mi-baxl span { position: absolute; transform: translateX(-50%); font-family: var(--mo); font-size: .75rem; color: var(--i3); }
.w3-mitigation select { font: inherit; font-family: var(--mo); font-size: .76rem; color: var(--i); background: var(--pp); border: 1px solid var(--r); border-radius: var(--rd); padding: .5rem .5rem; min-height: 44px; max-width: 100%; }
.w3-mitigation select:focus-visible { outline: 2px solid var(--ac); outline-offset: 2px; }
.w3-mitigation .mi-rules { font-size: .8rem; color: var(--i2); }
.w3-mitigation .mi-rules p { margin: .3rem 0; }
@container (max-width: 640px) {
  .w3-mitigation .mi-main { grid-template-columns: minmax(0, 1fr); }
  .w3-mitigation .mi-brow { grid-template-columns: minmax(0, 1fr) 6.2rem; }
  .w3-mitigation .mi-brow .mi-btrack { grid-column: 1 / -1; grid-row: 2; }
  .w3-mitigation .mi-baxrow { grid-template-columns: minmax(0, 1fr); }
  .w3-mitigation .mi-baxrow > span { display: none; }
}
`;

const T0 = 1.3;        // seconds the unchecked loop takes in the illustration
const HOLD = 1.4;
const CELLS = 16;
const LMIN = 0.5, LMAX = 10;

export function mount(el, ctx) {
  const base = (ctx && ctx.base) || 'data/';
  let dead = false, raf = 0, io = null;
  const mq = reducedQuery();
  const root = h('div', { class: 'w3 w3-mitigation' });
  el.append(root);
  injectCSS(root, CSS);
  const body = h('div');
  root.append(body);
  body.append(h('p', { class: 'w-load' }, 'Loading rewrite data'));
  const announce = liveRegion(root);
  const cleanups = [];

  loadJSON(base, 'mitigate.json').then((d) => {
    if (dead) return;
    try { build(d); } catch (e) { fail('could not draw the rewrite widget (' + e.message + ')'); }
  }, (e) => fail(e.message));

  function fail(msg) { if (!dead) body.replaceChildren(h('p', { class: 'w-err', role: 'alert' }, msg)); }

  function build(d) {
    const shapes = d.shapes || [];
    if (!shapes.length) { fail('mitigate.json has no loop shapes'); return; }
    const cpus = d.cpus || [];
    const addedLater = new Set((d.added_after_first_run || '').match(/m\d\d_\w+\.\w+/g) || []);
    const st = { shape: 0, variant: shapes[0].recommended, cpu: 'all', mode: 'after', playing: true };

    const shapeOf = () => shapes[st.shape];
    const varOf = (key) => shapeOf().variants.find((v) => v.variant === key);
    const jobsOf = (v, cpu) => (cpu === 'all' ? Object.values(v.per_cpu_range).reduce((a, x) => a + x.jobs, 0) : (v.per_cpu_range[cpu] || {}).jobs || 0);
    const rangeOf = (v, cpu) => (cpu === 'all' ? v.range : (v.per_cpu_range[cpu] ? v.per_cpu_range[cpu].both : null));
    const pointsOf = (v, cpu) => {
      const out = [];
      for (const [c, szs] of Object.entries(v.per_cpu)) { if (cpu !== 'all' && c !== cpu) continue; for (const arr of Object.values(szs)) for (const p of arr) out.push(p.ratio); }
      return out;
    };
    const showRange = (r) => { const a = fx(r.min, 2), b = fx(r.max, 2); return (a === b ? a : `${a}–${b}`) + '×'; };

    const title = h('p', { class: 'w-title' }, 'One up-front size check');
    const lede = h('p', { class: 'w-lede' }, 'With checks on, a loop that indexes every element can lose its vectorization. Checking the size once before the loop can bring the speed back. Pick a loop shape and a rewrite and compare.');

    const shapeSeg = segmented({ label: 'Loop shape', value: '0', options: shapes.map((s, i) => ({ value: String(i), label: s.shape })), onChange: (v) => { st.shape = +v; st.variant = shapeOf().recommended; update(); } });
    const cpuOpts = [{ value: 'all', label: 'all models' }, ...cpus.map((c) => ({ value: c, label: c }))];
    const cpuSeg = segmented({ label: 'CPU model', value: 'all', options: cpuOpts, onChange: (v) => { st.cpu = v; update(); } });
    const selId = uid('variant');
    const select = h('select', { id: selId });
    select.addEventListener('change', () => { st.variant = select.value; st.mode = 'after'; update(); });
    const selField = h('div', { class: 'w-field' }, h('label', { class: 'w-flabel', for: selId }, 'Rewrite'), select);
    const controls = h('div', { class: 'w-controls' }, field('Loop shape', shapeSeg.el), field('CPU model', cpuSeg.el), selField);

    const modeSeg = segmented({ label: 'Show the loop', value: 'after', options: [{ value: 'before', label: 'Checks on every element' }, { value: 'after', label: 'One size check before the loop' }], onChange: (v) => { st.mode = v; update(); } });
    const codeEl = h('pre', { class: 'mi-code', tabindex: '0', 'aria-label': 'Source code of the loop' });
    const chips = h('div', { class: 'mi-chips' });
    const what = h('p', { class: 'mi-what' });
    const left = h('div', null, h('p', { class: 'mi-h' }, h('span', null, 'The loop, as written')), h('div', { class: 'mi-tog' }, modeSeg.el), codeEl, chips, what);

    // belt
    const mkBelt = () => { const cells = Array.from({ length: CELLS }, () => h('span', { class: 'mi-cell' })); return { cells, el: h('div', { class: 'mi-belt', 'aria-hidden': 'true' }, cells) }; };
    const b0 = mkBelt(), b1 = mkBelt();
    const lbl0 = h('p', { class: 'mi-lanelabel' });
    const lbl1 = h('p', { class: 'mi-lanelabel' });
    const checks1 = h('div', { class: 'mi-checks', 'aria-hidden': 'true' });
    const time1 = h('p', { class: 'mi-time' });
    const pauseBtn = h('button', { type: 'button', class: 'w-btn', 'aria-pressed': 'false' }, 'Replay');
    const beltNote = h('p', { class: 'w-note', style: 'margin-top:.3rem' });
    const right = h('div', null,
      h('p', { class: 'mi-h' }, h('span', null, 'Sixteen elements, one pass')),
      h('div', { class: 'mi-lane' }, lbl0, b0.el),
      h('div', { class: 'mi-lane' }, lbl1, b1.el, checks1, time1),
      h('div', { class: 'mi-playrow' }, pauseBtn),
      beltNote);

    // bars
    const bars = h('div', { class: 'mi-bars' });
    const rules = h('div', { class: 'mi-rules w-foot' });
    body.replaceChildren(title, lede, controls, h('div', { class: 'mi-main' }, left, right), bars, rules);

    const pos = logScale(LMIN, LMAX);
    let beltState = null;

    function paintBelt(frac0, frac1) {
      const bs = beltState; if (!bs) return;
      const n0 = Math.floor(frac0 * CELLS + 1e-9);
      for (let i = 0; i < CELLS; i++) b0.cells[i].classList.toggle('on', i < n0);
      const n1 = Math.min(CELLS, Math.floor((frac1 * CELLS) / bs.g + 1e-9) * bs.g);
      for (let i = 0; i < CELLS; i++) {
        const c = b1.cells[i];
        c.classList.toggle('on', i < n1);
        c.classList.toggle('head', !bs.static && n1 < CELLS && i >= n1 && i < n1 + bs.g);
      }
    }

    function frame(ts) {
      raf = 0;
      if (dead || !beltState) return;
      const bs = beltState;
      if (!bs.t0) bs.t0 = ts;
      const tt = (ts - bs.t0) / 1000;
      const total = T0 * Math.max(1, bs.ratio);
      if (tt >= total) { paintStatic(); return; } // one run, then it rests on the final frame
      paintBelt(Math.min(1, tt / T0), Math.min(1, tt / (T0 * bs.ratio)));
      raf = requestAnimationFrame(frame);
    }
    function startAnim() {
      cancelAnimationFrame(raf); raf = 0;
      if (!beltState) return;
      if (mq.matches || !st.playing || !visible) { paintStatic(); return; }
      beltState.static = false;
      beltState.t0 = 0;
      raf = requestAnimationFrame(frame);
    }
    function paintStatic() {
      if (!beltState) return;
      beltState.static = true;
      paintBelt(1, Math.min(1, 1 / beltState.ratio));
    }
    let visible = true;
    if ('IntersectionObserver' in window) {
      io = new IntersectionObserver((es) => { visible = es[es.length - 1].isIntersecting; startAnim(); });
      io.observe(root);
    }
    const onMq = () => { pauseBtn.hidden = mq.matches; startAnim(); };
    mq.addEventListener && mq.addEventListener('change', onMq);
    cleanups.push(() => mq.removeEventListener && mq.removeEventListener('change', onMq));
    pauseBtn.hidden = mq.matches;
    pauseBtn.addEventListener('click', () => {
      st.playing = true;
      startAnim();
    });

    let firstPaint = true;
    function update() {
      const sh = shapeOf();
      const orig = varOf('orig');
      let v = varOf(st.variant) || varOf(sh.recommended);
      st.variant = v.variant;
      shapeSeg.set(String(st.shape)); cpuSeg.set(st.cpu); modeSeg.set(st.mode);
      select.replaceChildren(...sh.variants.filter((x) => x.variant !== 'orig').map((x) => h('option', { value: x.variant }, `${x.variant}: ${x.what}${x.variant === sh.recommended ? ' (recommended)' : ''}`)));
      select.value = v.variant;
      select.disabled = false;
      const showV = st.mode === 'before' ? orig : v;

      // code with the lines that differ from the original marked
      const origLines = new Set(orig.code.map((l) => l.trim()));
      codeEl.replaceChildren(...showV.code.map((l) => h('span', { class: 'mi-line' + (showV !== orig && !origLines.has(l.trim()) ? ' add' : '') }, l || ' ')));
      const ch = [];
      const trapped = (showV.short_fast || []).join(', ');
      ch.push(h('span', { class: 'w-chip' }, showV.keeps_safety ? 'keeps safety: the too-short input trapped under FAST' : `does not keep safety: the too-short input ${trapped || 'did not trap'}`));
      if (showV.readability_cost && showV !== orig) ch.push(h('span', { class: 'w-chip' }, showV.readability_cost));
      const key = `${sh.kernel}.${showV.variant}`;
      ch.push(h('span', { class: 'w-chip' + (addedLater.has(key) ? ' hl' : '') }, addedLater.has(key) ? 'added after the first timed run' : showV === orig ? 'the original' : 'in the first timed run'));
      if (showV !== orig && showV.variant === sh.recommended) ch.push(h('span', { class: 'w-chip' }, 'the rewrite shown first on the page'));
      chips.replaceChildren(...ch);
      what.textContent = st.mode === 'before' ? `${orig.what}. With FAST every index is checked as the loop runs.` : `${v.what}. Highlighted: lines that are not in the original.`;

      // belt
      const r = rangeOf(showV, st.cpu);
      const pts = pointsOf(showV, st.cpu);
      const ratio = pts.length ? median(pts) : (r ? (r.min + r.max) / 2 : 1);
      const vec = showV.vectorized_fast;
      const g = vec === true ? 4 : 1;
      const oneCheck = showV !== orig && showV.code.some((l) => /REQUIRE/.test(l));
      lbl0.innerHTML = '';
      lbl0.append(h('b', null, 'Checks off'), ' (the unchecked original)');
      lbl1.innerHTML = '';
      lbl1.append(h('b', null, st.mode === 'before' ? 'Checks on, original loop' : `Checks on, rewrite “${v.variant}”`), vec === true ? ': four elements at a time (vectorized under FAST)' : vec === false ? ': one element at a time (not vectorized under FAST)' : ': vectorization under FAST not recorded here');
      b1.cells.forEach((c) => { c.classList.remove('kept', 'lost'); c.classList.add(vec === true ? 'kept' : vec === false ? 'lost' : 'none'); });
      checks1.replaceChildren(...(oneCheck ? [h('span', { class: 'mi-chk one', title: 'one up-front check' })] : Array.from({ length: CELLS }, () => h('span', { class: 'mi-chk', title: 'a check' }))));
      time1.textContent = `unchecked: 1.0 time units · this loop: ${fx(ratio, 2)} (median of the measured ratios${st.cpu === 'all' ? ', all CPU models' : ', ' + st.cpu})`;
      beltNote.textContent = (mq.matches ? 'Static frame: where each loop is when the unchecked one finishes. ' : '') + 'Illustration scaled to the measured median; the yellow marks are the bounds checks (one per element, or one up front).';
      beltState = { ratio: Math.max(ratio, 0.05), g, t0: 0, static: true };
      if (firstPaint) { firstPaint = false; startAnim(); } else { cancelAnimationFrame(raf); raf = 0; paintStatic(); }

      // bars
      const mk = (vv, label, sub, active) => {
        const rr = rangeOf(vv, st.cpu);
        const kind = vv.vectorized_fast === true ? 'kept' : vv.vectorized_fast === false ? 'lost' : '';
        if (!rr) return h('div', { class: 'mi-brow' + (active ? ' act' : '') }, h('div', { class: 'mi-bname' }, h('b', null, label), h('span', null, sub)), h('div', { class: 'mi-btrack' }), h('div', { class: 'mi-bval' }, 'no jobs'));
        const pp = pointsOf(vv, st.cpu);
        const track = h('div', { class: 'mi-btrack', role: 'img', 'aria-label': `${label}: ${showRange(rr)} over ${jobsOf(vv, st.cpu)} jobs` },
          h('div', { class: 'mi-baxis' }), h('div', { class: 'mi-bone', style: `left:${pos(1)}%` }),
          h('div', { class: `mi-brange ${kind}`, style: `left:${pos(rr.min)}%;width:${Math.max(0.5, pos(rr.max) - pos(rr.min))}%` }),
          ...pp.map((x) => h('span', { class: 'mi-bdot', style: `left:${pos(x)}%` })),
          pp.length ? h('div', { class: 'mi-bmed', style: `left:${pos(median(pp))}%` }) : null);
        return h('div', { class: 'mi-brow' + (active ? ' act' : '') }, h('div', { class: 'mi-bname' }, h('b', null, label), h('span', null, sub)), track,
          h('div', { class: 'mi-bval' }, h('span', { 'data-range': '1' }, showRange(rr)), h('small', null, `${jobsOf(vv, st.cpu)} job${jobsOf(vv, st.cpu) === 1 ? '' : 's'}`)));
      };
      const axl = h('div', { class: 'mi-baxrow' }, h('span'), h('div', { class: 'mi-baxl' }, [0.5, 1, 2, 5, 10].map((t) => h('span', { style: `left:${pos(t)}%` + (t === 10 ? ';transform:translateX(-100%)' : t === 0.5 ? ';transform:none' : '') }, String(t)))), h('span'));
      bars.replaceChildren(
        h('p', { class: 'mi-h' }, h('span', null, 'FAST build against the unchecked original, time ratio (1.0 = no cost)'), h('span', null, 'bar = range, line = median, dots = jobs')),
        mk(orig, 'Original', 'checks on every element', st.mode === 'before'),
        mk(v, `Rewrite “${v.variant}”`, v.what, st.mode === 'after'),
        axl);

      // rules from the data
      const usable = d.usable_jobs, total = d.job_count;
      const later = [...addedLater];
      rules.replaceChildren(
        h('p', null, `Only ${usable} of ${total} jobs had a clean enough noise floor to count (A/A at most ${d.aa_max_pct}%), all on ${(d.usable_cpus || []).join(', ') || 'no CPU model'}. The ranges above include every job.`),
        h('p', null, `The rule for the word “better”: ${d.headline_rule}`),
        later.length ? h('p', null, `Added after the first timed run, judged by the same rules: ${later.join(', ')}.`) : null);
      announce(`${sh.shape}, ${st.mode === 'before' ? 'original loop' : 'rewrite ' + v.variant}, ${st.cpu === 'all' ? 'all CPU models' : st.cpu}: ${rangeOf(showV, st.cpu) ? showRange(rangeOf(showV, st.cpu)) : 'no jobs'} against the unchecked original.`);
    }
    update();
  }

  return { destroy() { dead = true; cancelAnimationFrame(raf); if (io) io.disconnect(); cleanups.forEach((f) => f()); root.remove(); } };
}
