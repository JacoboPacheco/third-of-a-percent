// Widget 1: does where the loop lands change the cost?
// Reads data/layout.json (ratios per kernel, size and CPU model) and, for the four measured placements,
// widgets/placements.json (same analysis files, one ratio per placement). Without the sidecar it shows the range only.
import { h, fx, clamp, injectCSS, loadJSON, liveRegion, segmented, field, logScale, reducedQuery } from './common.js';

const CSS = `
.w3-placement .pl-ruler { position: relative; margin: .2rem 0 .3rem; padding: 0 22px; user-select: none; }
.w3-placement .pl-rows { position: relative; }
.w3-placement .pl-row { position: relative; height: 54px; }
.w3-placement .pl-rowlabel { font-size: .78rem; color: var(--i2); margin: 0 0 .25rem; display: flex; flex-wrap: wrap; gap: .1rem .6rem; align-items: baseline; }
.w3-placement .pl-rowlabel b { font-family: var(--mo); font-weight: 500; font-size: .75rem; color: var(--i); }
.w3-placement .pl-lane { position: absolute; left: 0; right: 0; top: 14px; height: 28px; }
.w3-placement .pl-cells { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.w3-placement .pl-line { position: absolute; left: 0; top: 0; bottom: 0; background: var(--hv); border: 1px solid var(--r); border-radius: 3px; }
.w3-placement .pl-ghost { position: absolute; top: 0; bottom: 0; right: 0; border: 1px dashed var(--r); border-left: 0; border-radius: 0 3px 3px 0; background: repeating-linear-gradient(135deg, transparent 0 5px, var(--r2) 5px 6px); }
.w3-placement .pl-bar { touch-action: none; position: absolute; top: 3px; bottom: 3px; border-radius: 3px; display: flex; transition: left .22s cubic-bezier(.3,.7,.3,1); }
.w3-placement .pl-in { background: var(--i); height: 100%; border-radius: 3px 0 0 3px; min-width: 2px; }
.w3-placement .pl-in.full { border-radius: 3px; }
.w3-placement .pl-out { height: 100%; background: var(--lo); border-radius: 0 3px 3px 0; opacity: 0; transition: opacity .2s; }
.w3-placement .pl-bar.cross .pl-out { opacity: 1; }
.w3-placement .pl-bar.none-bar .pl-in { background: var(--no); }
.w3-placement .pl-bar.drag {  }
.w3-placement .pl-bar.drag:active {  }
.w3-placement .pl-bar.drag:hover .pl-in { background: #000; }
.w3-placement .pl-bar:focus-visible { outline: 2px solid var(--ac); outline-offset: 3px; }
.w3-placement .pl-grip { position: absolute; left: 3px; top: 50%; width: 3px; height: 12px; margin-top: -6px; border-left: 1px solid rgba(255,255,255,.7); border-right: 1px solid rgba(255,255,255,.7); pointer-events: none; }
.w3-placement .pl-bound { position: absolute; top: -5px; bottom: -5px; width: 0; border-left: 2px solid var(--i); pointer-events: none; z-index: 2; }
.w3-placement .pl-boundlabel { position: absolute; top: -1.2rem; transform: translateX(-50%); font-family: var(--mo); font-size: .75rem; color: var(--i); white-space: nowrap; }
.w3-placement .pl-ticks { position: relative; height: 1.1rem; margin-top: -2px; }
.w3-placement .pl-tick { position: absolute; transform: translateX(-50%); font-family: var(--mo); font-size: .75rem; color: var(--i3); }
.w3-placement .pl-stops { position: relative; height: 50px; margin-top: .15rem; }
.w3-placement .pl-stop { position: absolute; top: 0; transform: translateX(-50%); min-width: 46px; min-height: 46px; font-family: var(--mo); font-size: .75rem; color: var(--i2); background: var(--pp); border: 1px solid var(--r); border-radius: var(--rd); cursor: pointer; padding: .2rem .35rem; line-height: 1.1; transition: background-color .12s, color .12s; }
.w3-placement .pl-stop.cost small { color: var(--lo); opacity: 1; font-weight: 600; }
.w3-placement .pl-stop.cost[aria-pressed="true"] small { color: #ffb59c; }
.w3-placement .pl-stop:hover { background: var(--hv); color: var(--i); }
.w3-placement .pl-stop[aria-pressed="true"] { background: var(--i); color: var(--pp); border-color: var(--i); }
.w3-placement .pl-stop small { display: block; font-size: .75rem; opacity: .8; margin-top: .1rem; }
.w3-placement .pl-schem { font-size: .75rem; color: var(--i3); font-style: normal; }
.w3-placement .pl-flags { display: flex; flex-wrap: wrap; gap: .3rem .5rem; margin: .25rem 0 .1rem; }
.w3-placement .pl-gauge { margin: 1.1rem 0 0; border-top: 1px solid var(--r2); padding-top: .8rem; }
.w3-placement .pl-read { display: flex; flex-wrap: wrap; align-items: baseline; gap: .1rem 1rem; margin-bottom: .6rem; }
.w3-placement .pl-num { font-family: var(--mo); font-size: 2.1rem; line-height: 1.1; font-weight: 500; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }
.w3-placement .pl-num.lost { color: var(--lo); }
.w3-placement .pl-readsub { font-size: .84rem; color: var(--i2); }
.w3-placement .pl-track { position: relative; height: 66px; margin: 0 10px; }
.w3-placement .pl-axis { position: absolute; left: 0; right: 0; top: 17px; height: 2px; background: var(--r); }
.w3-placement .pl-one { position: absolute; top: 2px; height: 32px; width: 0; border-left: 1px dashed var(--i3); }
.w3-placement .pl-swing { position: absolute; top: 16px; height: 4px; background: var(--i3); opacity: .35; border-radius: 2px; }
.w3-placement .pl-dot { position: absolute; top: 18px; width: 10px; height: 10px; margin: -5px 0 0 -5px; border: 1.5px solid var(--i2); background: var(--pp); border-radius: 50%; }
.w3-placement .pl-dot.sel { width: 16px; height: 16px; margin: -8px 0 0 -8px; background: var(--i); border-color: var(--i); transition: left .22s cubic-bezier(.3,.7,.3,1); z-index: 2; }
.w3-placement .pl-dot.sel.lost { background: var(--lo); border-color: var(--lo); }
.w3-placement .pl-ci { position: absolute; top: 17px; height: 2px; background: var(--i); z-index: 1; }
.w3-placement .pl-ref { position: absolute; top: 31px; width: 8px; height: 8px; margin-left: -4px; transform: rotate(45deg); border: 1.5px solid var(--ke); background: var(--pp); }
.w3-placement .pl-gt { position: absolute; top: 46px; transform: translateX(-50%); font-family: var(--mo); font-size: .75rem; color: var(--i3); }
.w3-placement .pl-legend { display: flex; flex-wrap: wrap; gap: .25rem 1rem; font-size: .76rem; color: var(--i2); margin-top: .1rem; }
.w3-placement .pl-legend i { display: inline-block; vertical-align: -1px; margin-right: .3rem; }
.w3-placement .pl-lg-dot { width: 9px; height: 9px; border: 1.5px solid var(--i2); border-radius: 50%; }
.w3-placement .pl-lg-sel { width: 11px; height: 11px; background: var(--i); border-radius: 50%; }
.w3-placement .pl-lg-ref { width: 7px; height: 7px; border: 1.5px solid var(--ke); transform: rotate(45deg); }
.w3-placement .pl-caption { font-size: .82rem; color: var(--i2); margin: .7rem 0 0; max-width: 42em; }
.w3-placement .pl-fallback { font-size: .86rem; color: var(--i2); margin: 0 0 .8rem; border-left: 3px solid var(--r); padding: .2rem .7rem; }
.w3-placement .pl-dim { opacity: .55; }
@container (max-width: 520px) {
  .w3-placement .pl-num { font-size: 1.7rem; }
  .w3-placement .pl-stop { min-width: 40px; font-size: .75rem; }
}
`;

const SPAN = 112;   // bytes drawn: the 64-byte line plus 48 bytes of the next one
const LINE = 64;
const LOGMIN = 0.7, LOGMAX = 10;

// Choose a schematic loop length that agrees with the measured "extra window" flags of the four placements.
function schematicLength(plac, whichStart, whichFlag) {
  let lower = 0, upper = LINE;
  for (const p of plac) {
    const room = LINE - p[whichStart];
    if (p[whichFlag] === true) lower = Math.max(lower, room);
    else if (p[whichFlag] === false) upper = Math.min(upper, room);
  }
  if (lower < upper) return clamp(Math.round((lower + Math.min(upper, lower + 30)) / 2 + (lower === 0 ? 14 : 0)), 8, 60);
  return 28;
}

export function mount(el, ctx) {
  const base = (ctx && ctx.base) || 'data/';
  let dead = false;
  const mq = reducedQuery();
  const root = h('div', { class: 'w3 w3-placement' });
  el.append(root);
  injectCSS(root, CSS);
  const body = h('div');
  root.append(body);
  body.append(h('p', { class: 'w-load' }, 'Loading placement data'));
  const announce = liveRegion(root);

  (async () => {
    let layout, side = null;
    try { layout = await loadJSON(base, 'layout.json'); } catch (e) { fail(e.message); return; }
    try { const r = await fetch(new URL('./placements.json', import.meta.url)); if (r.ok) side = await r.json(); } catch (e) { side = null; }
    if (dead) return;
    try { build(layout, side); } catch (e) { fail('could not draw the placement widget (' + e.message + ')'); }
  })();

  function fail(msg) { if (dead) return; body.replaceChildren(h('p', { class: 'w-err', role: 'alert' }, msg)); }

  function build(layout, side) {
    // One entry per CPU model: the one with the most jobs (the pooled analysis), then the page's order.
    const best = new Map();
    for (const c of layout.cpus || []) {
      const o = best.get(c.cpu_model);
      if (!o || c.jobs > o.jobs) best.set(c.cpu_model, c);
    }
    const cpus = [...best.values()];
    if (!cpus.length) { fail('layout.json has no CPU models'); return; }
    const need = (layout.rules && layout.rules.min_jobs) || 3;
    const kernels = [];
    for (const r of cpus[0].rows) if (!kernels.find((k) => k.id === r.kernel)) kernels.push({ id: r.kernel, name: r.name });
    const sizes = [...new Set(cpus[0].rows.map((r) => r.size))];
    const rowOf = (cpu, k, s) => cpu.rows.find((r) => r.kernel === k && r.size === s);
    const placOf = (cpu, k, s) => {
      const cell = side && side.cells && side.cells[`${cpu.cpu_model}|${cpu.jobs}|${k}|${s}`];
      if (!cell) return null;
      return Object.entries(cell).map(([id, v]) => ({ id, ...v })).sort((a, b) => a.fast_start_mod64 - b.fast_start_mod64);
    };

    const st = { cpu: 0, kernel: kernels.find((k) => k.id === 'k02_add_fwd') ? 'k02_add_fwd' : kernels[0].id, size: sizes[0], slot: 0 };
    const firstEnough = cpus.findIndex((c) => c.enough);
    st.cpu = firstEnough >= 0 ? firstEnough : 0;

    const title = h('p', { class: 'w-title' }, 'Does where the loop lands change the cost?');
    const lede = h('p', { class: 'w-lede' }, 'Pick one of the four measured positions of the loop within a 64-byte line. For each, the gauge shows the run time of the build with checks (FAST) relative to the build without (NONE): above 1 is slower, below 1 is faster.');

    const cpuSeg = segmented({ label: 'CPU model', value: String(st.cpu), options: cpus.map((c, i) => ({ value: String(i), label: c.cpu_short, sub: `${c.jobs} job${c.jobs === 1 ? '' : 's'}${c.jobs < need ? ', too few' : ''}` })), onChange: (v) => { st.cpu = +v; update(true); } });
    const kSeg = segmented({ label: 'Loop', value: st.kernel, options: kernels.map((k) => ({ value: k.id, label: k.name })), onChange: (v) => { st.kernel = v; update(true); } });
    const sSeg = segmented({ label: 'Working-set size', value: st.size, options: sizes.map((s) => ({ value: s, label: s })), onChange: (v) => { st.size = v; update(true); } });
    const controls = h('div', { class: 'w-controls' }, field('CPU model', cpuSeg.el), field('Loop', kSeg.el), field('Size', sSeg.el));

    const tooFew = h('p', { class: 'w-note' });
    const fallback = h('p', { class: 'pl-fallback' }, 'The per-placement values are not in this build of the data, so only the range over the four placements is drawn.');

    // ruler
    const mkRow = (cls, drag) => {
      drag = false;
      const inn = h('div', { class: 'pl-in' });
      const out = h('div', { class: 'pl-out' });
      const bar = h('div', { class: `pl-bar ${cls}` + (drag ? ' drag' : '') }, inn, out, drag ? h('span', { class: 'pl-grip' }) : null);
      return { inn, out, bar };
    };
    const fastRow = mkRow('fast-bar', true);
    const noneRow = mkRow('none-bar', false);
    const lane = (r) => h('div', { class: 'pl-lane' },
      h('div', { class: 'pl-line', style: `width:${(LINE / SPAN) * 100}%` }),
      h('div', { class: 'pl-bound', style: `left:${(LINE / SPAN) * 100}%` }),
      h('div', { class: 'pl-ghost', style: `left:${(LINE / SPAN) * 100}%` }),
      r.bar);
    const fastLabel = h('span', null, 'FAST build, loop start ');
    const fastPos = h('b', null, '');
    const noneLabel = h('span', null, 'NONE build for comparison, loop start ');
    const nonePos = h('b', null, '');
    const schem = h('span', { class: 'pl-schem' }, 'schematic: bar length is drawn, not measured');
    const rowA = h('div', null, h('p', { class: 'pl-rowlabel' }, fastLabel, fastPos, schem), h('div', { class: 'pl-row' }, lane(fastRow)));
    const rowB = h('div', null, h('p', { class: 'pl-rowlabel' }, noneLabel, nonePos), h('div', { class: 'pl-row' }, lane(noneRow)));
    
    const ticks = h('div', { class: 'pl-ticks' }, [0, 16, 32, 48, 64].map((b) => h('span', { class: 'pl-tick', style: `left:${(b / SPAN) * 100}%` + (b === 64 ? ';color:var(--i);font-weight:600' : '') }, b === 64 ? '64 (boundary)' : String(b))), h('span', { class: 'pl-tick', style: `left:${(88 / SPAN) * 100}%` }, 'next line'));
    const stops = h('div', { class: 'pl-stops', role: 'group', 'aria-label': 'Measured placements of the FAST loop start' });
    const flags = h('div', { class: 'pl-flags' });
    const ruler = h('div', { class: 'pl-ruler' }, h('div', { class: 'pl-rows' }, rowA, rowB), ticks, stops, flags);

    // gauge
    const num = h('span', { class: 'pl-num' }, '');
    const readsub = h('span', { class: 'pl-readsub' });
    const read = h('div', { class: 'pl-read' }, num, readsub);
    const track = h('div', { class: 'pl-track' });
    const legend = h('div', { class: 'pl-legend' },
      h('span', null, h('i', { class: 'pl-lg-sel' }), 'this placement'),
      h('span', null, 'dashed line: 1.0, no cost'),
      h('span', null, h('i', { class: 'pl-lg-dot' }), 'the other measured placements'),
      h('span', null, h('i', { class: 'pl-lg-ref' }), 'as compiled and aligned (no placement control)'));
    const verdict = h('p', { class: 'w-note' });
    const gauge = h('div', { class: 'pl-gauge' }, read, track, legend, verdict);

    const caption = h('p', { class: 'pl-caption' }, 'Measured at four placements the compiler can produce; the in-between positions on the ruler are NOT measured (the bar snaps to the nearest measured stop). The mechanism is inferred, not shown: the window-crossing drawing is schematic.');

    body.replaceChildren(title, lede, controls, tooFew, fallback, ruler, gauge, caption);

    // log scale
    const pos = logScale(LOGMIN, LOGMAX);
    let plac = null, row = null;
    let lenFast = 28, lenNone = 28;

    function setBar(r, start, len) {
      len = Math.min(len, SPAN - start);
      r.bar.style.left = (start / SPAN) * 100 + '%';
      r.bar.style.width = (len / SPAN) * 100 + '%';
      const inside = Math.min(len, LINE - start), outside = Math.max(0, start + len - LINE);
      r.inn.style.width = (inside / len) * 100 + '%';
      r.inn.classList.toggle('full', outside === 0);
      r.out.style.width = (outside / len) * 100 + '%';
      r.bar.classList.toggle('cross', outside > 0);
    }

    function gaugeTrack(cur) {
      const kids = [h('div', { class: 'pl-axis' })];
      kids.push(h('div', { class: 'pl-one', style: `left:${pos(1)}%` }));
      for (const t of [2, 5, 10]) kids.push(h('span', { class: 'pl-gt', style: `left:${pos(t)}%` }, String(t)));
      kids.push(h('span', { class: 'pl-gt', style: `left:${pos(1)}%` }, '1.0'));
      if (plac) {
        const lo = Math.min(...plac.map((p) => p.ratio)), hi = Math.max(...plac.map((p) => p.ratio));
        kids.push(h('div', { class: 'pl-swing', style: `left:${pos(lo)}%;width:${Math.max(0.6, pos(hi) - pos(lo))}%` }));
        plac.forEach((p, i) => { if (i !== cur) kids.push(h('span', { class: 'pl-dot', style: `left:${pos(p.ratio)}%`, title: `FAST starts at byte ${p.fast_start_mod64}: ${fx(p.ratio, 3)}` })); });
        const c = plac[cur];
        kids.push(h('div', { class: 'pl-ci', style: `left:${pos(c.ci95[0])}%;width:${Math.max(0.3, pos(c.ci95[1]) - pos(c.ci95[0]))}%` }));
        selDot = h('span', { class: 'pl-dot sel' + (row.class === 'lost' ? ' lost' : ''), style: `left:${pos(c.ratio)}%` });
        kids.push(selDot);
      } else {
        kids.push(h('div', { class: 'pl-swing', style: `left:${pos(row.min)}%;width:${Math.max(0.6, pos(row.max) - pos(row.min))}%;opacity:.7;height:8px;top:17px` }));
        kids.push(h('span', { class: 'pl-dot sel' + (row.class === 'lost' ? ' lost' : ''), style: `left:${pos(row.median)}%` }));
      }
      for (const [v, name] of [[row.as_compiled, 'as compiled'], [row.aligned, 'aligned']]) {
        if (v) kids.push(h('span', { class: 'pl-ref', style: `left:${pos(v)}%`, title: `${name}: ${fx(v, 3)}` }));
      }
      track.replaceChildren(...kids);
    }
    let selDot = null;

    function update(fromUser) {
      const cpu = cpus[st.cpu];
      row = rowOf(cpu, st.kernel, st.size);
      if (!row) { fail('no data for this selection'); return; }
      plac = placOf(cpu, st.kernel, st.size);
      cpuSeg.set(String(st.cpu)); kSeg.set(st.kernel); sSeg.set(st.size);
      tooFew.hidden = cpu.jobs >= need;
      tooFew.textContent = cpu.jobs >= need ? '' : `Too few jobs on ${cpu.cpu_short}: ${cpu.jobs} of the ${need} needed for a reading. The numbers are shown, but the data gives this model no verdict.`;
      root.classList.toggle('w3-dimmed', cpu.jobs < need);
      fallback.hidden = !!plac;
      ruler.hidden = !plac;
      if (plac) {
        st.slot = clamp(st.slot, 0, plac.length - 1);
        lenFast = schematicLength(plac, 'fast_start_mod64', 'fast_extra_window');
        lenNone = schematicLength(plac, 'none_start_mod64', 'none_extra_window');
        const p = plac[st.slot];
        setBar(fastRow, p.fast_start_mod64, lenFast);
        setBar(noneRow, p.none_start_mod64, lenNone);
        fastPos.textContent = `byte ${p.fast_start_mod64} of 64`;
        nonePos.textContent = `byte ${p.none_start_mod64} of 64`;
        fastRow.bar.setAttribute('role', 'slider');
        fastRow.bar.tabIndex = 0;
        fastRow.bar.setAttribute('aria-label', 'FAST loop start: use the four buttons below, or the arrow keys');
        fastRow.bar.setAttribute('aria-valuemin', '1');
        fastRow.bar.setAttribute('aria-valuemax', String(plac.length));
        fastRow.bar.setAttribute('aria-valuenow', String(st.slot + 1));
        fastRow.bar.setAttribute('aria-valuetext', `stop ${st.slot + 1} of ${plac.length}: FAST loop starts at byte ${p.fast_start_mod64}, ratio ${fx(p.ratio, 3)}`);
        stops.replaceChildren(...plac.map((q, i) => {
          const b = h('button', { type: 'button', class: 'pl-stop' + (q.ratio >= 1.02 ? ' cost' : ''), style: `left:${((q.fast_start_mod64 + 0) / SPAN) * 100 + 0}%`, 'aria-pressed': i === st.slot ? 'true' : 'false', 'aria-label': `FAST loop starts at byte ${q.fast_start_mod64}, ratio ${fx(q.ratio, 3)}` }, String(q.fast_start_mod64), h('small', null, fx(q.ratio, 2) + '×'));
          b.style.left = `calc(${(q.fast_start_mod64 / SPAN) * 100}% + 0px)`;
          b.addEventListener('click', () => { st.slot = i; update(true); const nb = stops.children[i]; if (nb) nb.focus(); });
          return b;
        }));
        const fe = p.fast_extra_window, ne = p.none_extra_window;
        const yn = (v) => (v === true ? 'yes' : v === false ? 'no' : 'unknown');
        flags.replaceChildren(h('span', { class: 'w-chip' + (fe ? ' hl' : '') }, `data: FAST loop spans an extra 64-byte window: ${yn(fe)}`), h('span', { class: 'w-chip' }, `NONE loop: ${yn(ne)}`));
      }
      // gauge
      gaugeTrack(plac ? st.slot : 0);
      const shown = plac ? plac[st.slot].ratio : row.median;
      num.textContent = fx(shown, 3) + '×';
      num.classList.toggle('lost', row.class === 'lost');
      const where = plac ? `at this placement` : `median over the four placements`;
      const ci = plac ? ` (95% interval ${fx(plac[st.slot].ci95[0], 3)} to ${fx(plac[st.slot].ci95[1], 3)})` : '';
      readsub.textContent = `FAST ÷ NONE ${where}${ci}`;
      const range = `Over all four placements: ${fx(row.min, 3)} to ${fx(row.max, 3)}. As compiled: ${row.as_compiled == null ? 'n/a' : fx(row.as_compiled, 3)}. Aligned: ${row.aligned == null ? 'n/a' : fx(row.aligned, 3)}. `;
      verdict.textContent = `${range}The data's reading for this cell: ${row.verdict} (${row.n_pass} of ${row.n_placements} placements pass the forward rule${row.class === 'lost' ? '; for a loop that loses SIMD the question is whether the cost holds' : ''}).`;
      announce(`${cpu.cpu_short}, ${row.name}, ${st.size}${plac ? `, FAST loop at byte ${plac[st.slot].fast_start_mod64}` : ''}: FAST over NONE ${fx(shown, 3)}. Reading: ${row.verdict}.`);
    }

    // the four stops are tap targets; the arrow keys on the bar are an extra (no dragging)
    fastRow.bar.addEventListener('keydown', (e) => {
      if (!plac) return;
      let i = st.slot;
      if (e.key === 'ArrowRight' || e.key === 'ArrowUp') i++;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') i--;
      else if (e.key === 'Home') i = 0;
      else if (e.key === 'End') i = plac.length - 1;
      else return;
      e.preventDefault();
      i = clamp(i, 0, plac.length - 1);
      if (i !== st.slot) { st.slot = i; update(true); fastRow.bar.focus(); }
    });
    update(false);
    void mq;
  }

  return { destroy() { dead = true; root.remove(); } };
}
