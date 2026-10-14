// Widget 3: real programs, whole-program FAST / NONE. Reads data/realworld.json and data/pgo.json.
import { h, fx, clamp, injectCSS, loadJSON, liveRegion, segmented, field, uid } from './common.js';

const CSS = `
.w3-programs .pr-grid { display: grid; grid-template-columns: 9.2rem minmax(0, 1fr) 10rem; column-gap: .9rem; }
.w3-programs .pr-axis { position: relative; height: 1.3rem; margin-bottom: .1rem; }
.w3-programs .pr-axis span { position: absolute; transform: translateX(-50%); font-family: var(--mo); font-size: .75rem; color: var(--i3); }
.w3-programs .pr-list { list-style: none; margin: 0; padding: 0; }
.w3-programs .pr-row { display: grid; grid-template-columns: 9.2rem minmax(0, 1fr) 10rem; column-gap: .9rem; align-items: center; padding: .5rem .3rem .45rem; margin: 0; border-top: 1px solid var(--r2); border-radius: 4px; cursor: default; transition: background-color .12s; }
.w3-programs .pr-row:hover, .w3-programs .pr-row.on { background: var(--hv); }
.w3-programs .pr-row:focus-visible { outline: 2px solid var(--ac); outline-offset: 0; }
.w3-programs .pr-name { font-size: .88rem; line-height: 1.2; }
.w3-programs .pr-name small { display: block; font-size: .75rem; color: var(--i3); margin-top: .1rem; }
.w3-programs .pr-plot { position: relative; height: 38px; }
.w3-programs .pr-plot.two { height: 50px; }
.w3-programs .pr-one { position: absolute; top: 0; bottom: 0; width: 0; border-left: 1px dashed var(--i3); }
.w3-programs .pr-aa { position: absolute; top: 2px; bottom: 2px; background: var(--sl); border-left: 1px solid var(--r); border-right: 1px solid var(--r); min-width: 5px; margin-left: -2px; }
.w3-programs .pr-iv { position: absolute; height: 3px; margin-top: -1.5px; border-radius: 2px; background: var(--i2); min-width: 2px; }
.w3-programs .pr-iv.pgo { background: var(--ke); }
.w3-programs .pr-pt { position: absolute; width: 11px; height: 11px; margin: -5.5px 0 0 -5.5px; border-radius: 50%; background: var(--i2); border: 2px solid var(--pp); box-shadow: 0 0 0 1px var(--i2); transition: left .35s cubic-bezier(.3,.7,.3,1); }
.w3-programs .pr-pt.pgo { border-radius: 2px; transform: rotate(45deg); background: var(--ke); box-shadow: 0 0 0 1px var(--ke); width: 10px; height: 10px; margin: -5px 0 0 -5px; }
.w3-programs .pr-clip { position: absolute; font-size: .8rem; line-height: 1; margin-top: -7px; color: var(--i2); }
.w3-programs .pr-val { font-family: var(--mo); font-size: .84rem; font-variant-numeric: tabular-nums; text-align: right; line-height: 1.2; }
.w3-programs .pr-val small { display: block; font-variant-numeric: normal; font-family: var(--sf); font-size: .75rem; color: var(--i3); line-height: 1.2; }
.w3-programs .pr-val .pgo { color: var(--ke); }
.w3-programs .pr-val > span + small { margin-bottom: .2rem; }
.w3-programs .pr-val > span { display: block; }
.w3-programs .pr-share { grid-column: 1 / -1; display: flex; align-items: center; gap: .5rem; font-size: .75rem; color: var(--i3); margin-top: .2rem; }
.w3-programs .pr-mini { position: relative; width: 84px; height: 6px; background: var(--r2); border-radius: 3px; flex: none; overflow: hidden; }
.w3-programs .pr-mini i { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 3px; }
.w3-programs .pr-mini .f { background: var(--lo); opacity: .3; }
.w3-programs .pr-mini .l { background: var(--lo); }
.w3-programs .pr-legend { display: flex; flex-wrap: wrap; gap: .25rem 1.1rem; font-size: .76rem; color: var(--i2); margin: .2rem 0 .5rem; }
.w3-programs .pr-legend i { display: inline-block; vertical-align: -1px; margin-right: .35rem; }
.w3-programs .lg-np { width: 9px; height: 9px; border-radius: 50%; background: var(--i2); }
.w3-programs .lg-pg { width: 8px; height: 8px; background: var(--ke); transform: rotate(45deg); }
.w3-programs .lg-aa { width: 14px; height: 9px; background: var(--sl); border: 1px solid var(--r); }
.w3-programs .lg-lo { width: 14px; height: 5px; background: var(--lo); border-radius: 3px; }
.w3-programs .pr-tip { position: absolute; z-index: 5; width: min(22rem, calc(100% - 8px)); background: var(--pp); border: 1px solid var(--i); border-radius: var(--rd); padding: .6rem .75rem; font-size: .78rem; line-height: 1.4; box-shadow: 0 6px 18px rgba(0,0,0,.12); pointer-events: none; }
.w3-programs .pr-tip b { font-weight: 600; }
.w3-programs .pr-tip .t { font-family: var(--mo); font-size: .75rem; }
.w3-programs .pr-tip p { margin: .25rem 0 0; }
.w3-programs .pr-tip .h { font-size: .9rem; margin: 0 0 .1rem; }
.w3-programs .pr-msg { font-size: .9rem; color: var(--i2); border-left: 3px solid var(--r); padding: .3rem .75rem; margin: .4rem 0; }
.w3-programs select { font: inherit; font-family: var(--mo); font-size: .76rem; color: var(--i); background: var(--pp); border: 1px solid var(--r); border-radius: var(--rd); padding: .5rem .5rem; min-height: 44px; max-width: 100%; }
.w3-programs select:focus-visible { outline: 2px solid var(--ac); outline-offset: 2px; }
@container (max-width: 560px) {
  .w3-programs .pr-grid, .w3-programs .pr-row { grid-template-columns: minmax(0, 1fr) 6.6rem; }
  .w3-programs .pr-axis { grid-column: 1 / -1; }
  .w3-programs .pr-plot { grid-column: 1 / -1; grid-row: 2; }
  .w3-programs .pr-val { grid-column: 2; grid-row: 1; }
  .w3-programs .pr-share { grid-column: 1 / -1; grid-row: 3; }
}
`;

const NAMES = { lightgbm_default: 'LightGBM (default)', lightgbm_multiclass: 'LightGBM (multiclass)', lightgbm_linear: 'LightGBM (linear)', draco: 'Draco', tinydnn: 'tiny-dnn', spectra: 'Spectra', meshopt: 'meshoptimizer', fmt: '{fmt}' };

export function mount(el, ctx) {
  const base = (ctx && ctx.base) || 'data/';
  let dead = false;
  const root = h('div', { class: 'w3 w3-programs' });
  el.append(root);
  injectCSS(root, CSS);
  const body = h('div');
  root.append(body);
  body.append(h('p', { class: 'w-load' }, 'Loading program timings'));
  const announce = liveRegion(root);

  Promise.all([loadJSON(base, 'realworld.json'), loadJSON(base, 'pgo.json')]).then(([rw, pgo]) => {
    if (dead) return;
    try { build(rw, pgo); } catch (e) { fail('could not draw the programs widget (' + e.message + ')'); }
  }, (e) => fail(e.message));

  function fail(msg) { if (!dead) body.replaceChildren(h('p', { class: 'w-err', role: 'alert' }, msg)); }

  function build(rw, pgo) {
    const minJobs = (rw.minimum_jobs || 3);
    const groups = (rw.timing && rw.timing.groups) || [];
    const pcpus = pgo.cpus || [];
    const rowsMeta = rw.rows || [];
    // CPU models: those with non-PGO timings, then any that only the PGO file has.
    const models = [];
    for (const g of groups) models.push({ short: g.cpu_short, np: g, pg: pcpus.find((c) => c.cpu_short === g.cpu_short) || null });
    for (const c of pcpus) if (!models.find((m) => m.short === c.cpu_short)) models.push({ short: c.cpu_short, np: null, pg: c });
    if (!models.length) { fail('no timing data for any CPU model'); return; }
    const npOK = (m) => !!(m.np && m.np.enough && m.np.jobs >= minJobs);
    const pgOK = (m) => !!(m.pg && m.pg.enough && m.pg.jobs >= minJobs);
    const npJobs = (m) => (m.np ? m.np.jobs : 0);
    const pgJobs = (m) => (m.pg ? m.pg.jobs : 0);
    const meta = new Map(rowsMeta.map((r) => [r.row, r]));
    const ids = rowsMeta.map((r) => r.row);

    const st = { cpu: Math.max(0, models.findIndex(npOK)), col: 'fast', ser: 'np', sort: 'listed', hover: null };

    const title = h('p', { class: 'w-title' }, 'Real programs');
    const lede = h('p', { class: 'w-lede' }, 'Whole programs built with and without checks, timed on shared runners. Each dot is the pooled time ratio, FAST over NONE, for one program; the line is its 95% interval.');

    const cpuSeg = segmented({ label: 'CPU model', value: String(st.cpu), options: models.map((m, i) => ({ value: String(i), label: m.short, sub: `${npJobs(m)} jobs${npOK(m) ? '' : ', too few'}${m.pg ? ` · PGO ${pgJobs(m)}${pgOK(m) ? '' : ', too few'}` : ''}` })), onChange: (v) => { st.cpu = +v; render(); } });
    const colSeg = segmented({ label: 'Build', value: st.col, options: [{ value: 'fast', label: 'as compiled' }, { value: 'aligned', label: 'aligned' }], onChange: (v) => { st.col = v; render(); } });
    const serSeg = segmented({ label: 'Profile-guided optimization', value: st.ser, options: [{ value: 'np', label: 'non-PGO' }, { value: 'pgo', label: 'PGO' }, { value: 'both', label: 'both' }], onChange: (v) => { st.ser = v; render(); } });
    const sortId = uid('sort');
    const sortSel = h('select', { id: sortId }, h('option', { value: 'listed' }, 'as listed'), h('option', { value: 'ratio' }, 'cost, high to low'), h('option', { value: 'share' }, 'share of lost loops, high to low'));
    sortSel.addEventListener('change', () => { st.sort = sortSel.value; render(); });
    const controls = h('div', { class: 'w-controls' }, field('CPU model', cpuSeg.el), field('Build', colSeg.el), field('Profile-guided optimization', serSeg.el), h('div', { class: 'w-field' }, h('label', { class: 'w-flabel', for: sortId }, 'Sort'), sortSel));

    const legend = h('div', { class: 'pr-legend' });
    const msgs = h('div');
    const axis = h('div', { class: 'pr-grid' }, h('span'), h('div', { class: 'pr-axis' }), h('span'));
    const list = h('ol', { class: 'pr-list', 'aria-label': 'Programs' });
    const tip = h('div', { class: 'pr-tip', role: 'tooltip', id: uid('tip'), hidden: true });
    const foot = h('p', { class: 'w-foot' }, 'Caveats: the programs were chosen because they contain lost loops (the two controls contain none). For PGO, the training input is the timed input. Timed on shared runners; a model with fewer than ' + minJobs + ' jobs gets no reading.');
    body.replaceChildren(title, lede, controls, legend, msgs, axis, list, tip, foot);

    const colName = { fast: 'as compiled', aligned: 'aligned' };
    const f4 = (v) => fx(v, 4);

    // value of one series for one row: {ratio, lo, hi, aa, reading, text, atMost, compare}
    function val(m, id, ser) {
      if (ser === 'np') {
        if (!npOK(m)) return null;
        const r = m.np.rows[id]; if (!r) return null;
        const c = r[st.col];
        return { ratio: c.ratio, lo: c.lo, hi: c.hi, aa: r.aa.half_width_pct, reading: r.reading, text: r.text, atMost: r.at_most_pct, both: { fast: r.fast, aligned: r.aligned } };
      }
      if (!pgOK(m)) return null;
      const r = m.pg.rows.find((x) => x.row === id); if (!r) return null;
      const c = r.pgo[st.col];
      return { ratio: c.ratio, lo: c.lo, hi: c.hi, aa: r.pgo.aa_half_width_pct, reading: r.pgo.reading, atMost: r.pgo.at_most_pct, compare: r.compare, both: { fast: r.pgo.fast, aligned: r.pgo.aligned }, name: r.name };
    }

    function domain(m) {
      const pts = [];
      for (const id of ids) for (const ser of ['np', 'pgo']) { const v = val(m, id, ser); if (!v) continue; for (const col of ['fast', 'aligned']) pts.push(v.both[col].ratio); }
      let lo = Math.min(0.97, ...(pts.length ? pts : [1]) ) - 0.015, hi = Math.max(1.06, ...(pts.length ? pts : [1])) + 0.015;
      lo = clamp(lo, 0.8, 0.97); hi = clamp(hi, 1.06, 1.4);
      return [lo, hi];
    }

    function nice(lo, hi) {
      const span = hi - lo;
      const step = [0.01, 0.02, 0.05, 0.1].find((s) => span / s <= 7) || 0.1;
      const out = [];
      for (let t = Math.ceil(lo / step - 1e-9) * step; t <= hi + 1e-9; t += step) out.push(+t.toFixed(3));
      return out;
    }

    const showPct = (p, approx) => (p > 0 && p < 0.01 ? 'under 0.01%' : (approx ? '≈ ' : '') + fx(p, 2) + '%');

    function tipHTML(m, id) {
      const mt = meta.get(id);
      const wrap = h('div');
      wrap.append(h('p', { class: 'h' }, h('b', null, NAMES[id] || id), mt && mt.control ? ' (control, no lost loop)' : ''));
      for (const ser of ['np', 'pgo']) {
        if (st.ser !== 'both' && st.ser !== ser) continue;
        const v = val(m, id, ser);
        const lab = ser === 'np' ? `non-PGO, ${npJobs(m)} jobs` : `PGO, ${pgJobs(m)} jobs`;
        if (!v) { wrap.append(h('p', null, h('b', null, lab + ': '), 'too few jobs for a reading')); continue; }
        wrap.append(h('p', null, h('b', null, lab), h('br'),
          h('span', { class: 't' }, `as compiled ${f4(v.both.fast.ratio)} [${f4(v.both.fast.lo)}, ${f4(v.both.fast.hi)}]`), h('br'),
          h('span', { class: 't' }, `aligned ${f4(v.both.aligned.ratio)} [${f4(v.both.aligned.lo)}, ${f4(v.both.aligned.hi)}]`), h('br'),
          h('span', { class: 't' }, `A/A half-width ${fx(v.aa, 2)}%`), h('br'),
          ser === 'np' ? v.text : `${v.reading}${v.atMost != null ? `: at most ${fx(v.atMost, 2)}%` : ''}${v.compare ? `; against non-PGO: ${v.compare}` : ''}`));
      }
      if (mt && !mt.control) wrap.append(h('p', null, `Share of executed instructions (counted, not timed): lines of the lost loops ${showPct(mt.lines_none, mt.approximate)}, their functions ${showPct(mt.funcs_none, mt.approximate)}.`));
      return wrap;
    }

    function showTip(li, m, id) {
      tip.replaceChildren(tipHTML(m, id));
      tip.hidden = false;
      const host = root.getBoundingClientRect(), r = li.getBoundingClientRect();
      const w = tip.offsetWidth, hh = tip.offsetHeight;
      let top = r.bottom - host.top + 4;
      if (top + hh > host.height && r.top - host.top - hh - 4 > 0) top = r.top - host.top - hh - 4;
      tip.style.top = Math.max(0, top) + 'px';
      tip.style.left = clamp(r.left - host.left + 24, 0, Math.max(0, host.width - w)) + 'px';
      li.setAttribute('aria-describedby', tip.id);
    }
    function hideTip() { tip.hidden = true; list.querySelectorAll('[aria-describedby]').forEach((n) => n.removeAttribute('aria-describedby')); list.querySelectorAll('.on').forEach((n) => n.classList.remove('on')); }
    root.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideTip(); });

    function render() {
      hideTip();
      const m = models[st.cpu];
      cpuSeg.set(String(st.cpu)); colSeg.set(st.col); serSeg.set(st.ser); sortSel.value = st.sort;
      // legend
      const lg = [];
      if (st.ser !== 'pgo') lg.push(h('span', null, h('i', { class: 'lg-np' }), `non-PGO (${npJobs(m)} jobs)`));
      if (st.ser !== 'np') lg.push(h('span', null, h('i', { class: 'lg-pg' }), `PGO (${pgJobs(m)} jobs)`));
      lg.push(h('span', null, h('i', { class: 'lg-aa' }), 'shaded band: the noise floor (A/A) around 1.0'));
      lg.push(h('span', null, h('i', { class: 'lg-lo' }), 'red bar: lost-loop share of executed instructions'));
      legend.replaceChildren(...lg);

      const want = st.ser === 'both' ? ['np', 'pgo'] : [st.ser];
      const avail = want.filter((s) => (s === 'np' ? npOK(m) : pgOK(m)));
      const notes = [];
      for (const s of want) if (!avail.includes(s)) {
        if (s === 'np') notes.push(m.np ? `${m.short}: ${npJobs(m)} non-PGO job${npJobs(m) === 1 ? '' : 's'}, too few jobs (${minJobs} needed for a reading).` : `${m.short}: no non-PGO timing.`);
        else notes.push(m.pg ? `${m.short}: ${pgJobs(m)} PGO job${pgJobs(m) === 1 ? '' : 's'}, too few jobs (${minJobs} needed for a reading).` : `${m.short}: no PGO timing.`);
      }
      msgs.replaceChildren(...notes.map((n) => h('p', { class: 'pr-msg' }, n)));
      if (!avail.length) { axis.hidden = true; list.replaceChildren(); announce(notes.join(' ')); return; }
      axis.hidden = false;

      const [lo, hi] = domain(m);
      const X = (v) => ((v - lo) / (hi - lo)) * 100;
      const axEl = axis.children[1];
      axEl.replaceChildren(...nice(lo, hi).map((t) => h('span', { style: `left:${X(t)}%` + (X(t) > 94 ? ';transform:translateX(-100%)' : X(t) < 6 ? ';transform:none' : '') }, fx(t, 2))));

      let order = [...ids];
      const key = (id) => { const v = val(m, id, avail[0]); return v ? v.ratio : 0; };
      if (st.sort === 'ratio') order.sort((a, b) => key(b) - key(a));
      else if (st.sort === 'share') order.sort((a, b) => ((meta.get(b) || {}).lines_none || 0) - ((meta.get(a) || {}).lines_none || 0));
      const maxFunc = Math.max(1, ...rowsMeta.map((r) => r.funcs_none || 0));

      const items = order.map((id) => {
        const mt = meta.get(id) || {};
        const two = avail.length === 2;
        const aaw = Math.max(...avail.map((ser) => { const v = val(m, id, ser); return v ? v.aa : 0; }));
        const plot = h('div', { class: 'pr-plot' + (two ? ' two' : '') }, h('div', { class: 'pr-aa', style: `left:${X(1 - aaw / 100)}%;width:${X(1 + aaw / 100) - X(1 - aaw / 100)}%` }), h('div', { class: 'pr-one', style: `left:${X(1)}%` }));
        const vals = h('div', { class: 'pr-val' });
        const summary = [];
        avail.forEach((ser, i) => {
          const v = val(m, id, ser); if (!v) return;
          const y = two ? (i === 0 ? 17 : 36) : 19;
                    const l = clamp(v.lo, lo, hi), u = clamp(v.hi, lo, hi);
          plot.append(h('div', { class: 'pr-iv' + (ser === 'pgo' ? ' pgo' : ''), style: `left:${X(l)}%;width:${Math.max(0, X(u) - X(l))}%;top:${y}px` }));
          if (v.hi > hi) plot.append(h('span', { class: 'pr-clip', style: `left:calc(${X(hi)}% - 4px);top:${y}px`, title: `interval runs past ${fx(hi, 2)}` }, '›'));
          if (v.lo < lo) plot.append(h('span', { class: 'pr-clip', style: `left:${X(lo)}%;top:${y}px`, title: `interval runs below ${fx(lo, 2)}` }, '‹'));
          const pt = h('span', { class: 'pr-pt' + (ser === 'pgo' ? ' pgo' : ''), style: `left:${X(clamp(v.ratio, lo, hi))}%;top:${y}px` });
          plot.append(pt);
          const note = v.atMost != null ? `${v.reading}, at most ${fx(v.atMost, 2)}%` : v.reading;
          vals.append(h('span', { class: ser === 'pgo' ? 'pgo' : '' }, avail.length === 2 ? (ser === 'pgo' ? '◆ ' : '● ') : '', `${fx(v.ratio, 3)}×`), h('small', null, note));
          summary.push(`${ser === 'np' ? 'non-PGO' : 'PGO'} ${fx(v.ratio, 3)}, ${note}`);
        });
        const share = mt.control
          ? h('div', { class: 'pr-share' }, 'no lost loop in this program')
          : h('div', { class: 'pr-share' }, h('span', { class: 'pr-mini', 'aria-hidden': 'true' }, h('i', { class: 'f', style: `width:${Math.max(mt.funcs_none > 0 ? 3 : 0, (mt.funcs_none / maxFunc) * 100)}%` }), h('i', { class: 'l', style: `width:${Math.max(mt.lines_none > 0 ? 2 : 0, (mt.lines_none / maxFunc) * 100)}%` })),
            h('span', null, `lost-loop lines hold ${showPct(mt.lines_none, mt.approximate)} of executed instructions (functions ${showPct(mt.funcs_none, mt.approximate)}); counted, not timed`));
        const li = h('li', { class: 'pr-row', tabindex: '0', 'aria-label': `${NAMES[id] || id}, ${colName[st.col]}: ${summary.join('; ')}` },
          h('div', { class: 'pr-name' }, NAMES[id] || id, mt.control ? h('small', null, 'control') : h('small', null, mt.what || '')), plot, vals, share);
        li.addEventListener('mouseenter', () => { hideTip(); li.classList.add('on'); showTip(li, m, id); });
        li.addEventListener('mouseleave', hideTip);
        li.addEventListener('focus', () => { li.classList.add('on'); showTip(li, m, id); });
        li.addEventListener('blur', hideTip);
        return li;
      });
      list.replaceChildren(...items);

      const counts = {};
      for (const id of ids) { const v = val(m, id, avail[0]); if (v) counts[v.reading] = (counts[v.reading] || 0) + 1; }
      announce(`${m.short}, ${colName[st.col]}, ${st.ser === 'np' ? 'non-PGO' : st.ser === 'pgo' ? 'PGO' : 'non-PGO and PGO'}: ` + Object.entries(counts).map(([k, n]) => `${n} ${k}`).join(', ') + '.');
    }
    render();
  }

  return { destroy() { dead = true; root.remove(); } };
}
