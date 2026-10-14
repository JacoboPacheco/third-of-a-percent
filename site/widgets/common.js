// Shared helpers for the three widgets. No globals are added; everything is exported.
// Style rule: every selector lives under a widget's own class (w3-<name>), injected as a <style> inside the widget.

export function h(tag, attrs, ...kids) {
  const n = document.createElement(tag);
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else n.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat()) if (k !== null && k !== undefined && k !== false) n.append(k.nodeType ? k : document.createTextNode(String(k)));
  return n;
}

export const fx = (v, d = 2) => Number(v).toFixed(d);
export const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
export const reducedQuery = () => (window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false, addEventListener() {}, removeEventListener() {} });

let uidN = 0;
export const uid = (p) => `w3-${p}-${++uidN}`;

// Fetch JSON relative to ctx.base; the error message is one plain line for the widget to show.
export async function loadJSON(base, name) {
  let r;
  try { r = await fetch(base + name); } catch (e) { throw new Error(`could not load ${name} (network)`); }
  if (!r.ok) throw new Error(`could not load ${name} (HTTP ${r.status})`);
  try { return await r.json(); } catch (e) { throw new Error(`${name} is not valid JSON`); }
}

// The custom properties the page defines, re-exposed under short local names with the agreed fallbacks.
export const BASE_CSS = `
.w3 { --i: var(--ink,#1b1b1b); --i2: var(--ink-2,#4a4a4a); --i3: var(--ink-3,#727272); --r: var(--rule,#d6d6d1); --r2: var(--rule-2,#ebebe7);
  --hv: var(--hover,#f6f6f2); --sl: var(--sel,#f0f0ea); --lo: var(--lost,#c2461e); --ke: var(--kept,#1f5aa6); --no: var(--none,#8d8d88);
  --st: var(--simd-tint,#e8eff9); --ck: var(--check-hl,#fcefb4); --pp: var(--paper,#fff); --sf: var(--serif,"Source Serif 4",Georgia,serif);
  --mo: var(--mono,"IBM Plex Mono",ui-monospace,Consolas,monospace); --ac: var(--accent,#1f5aa6); --rd: var(--radius,6px);
  font-family: var(--sf); color: var(--i); line-height: 1.45; font-size: 16px; container-type: inline-size; position: relative; }
.w3 *, .w3 *::before, .w3 *::after { box-sizing: border-box; }
.w3 .w-title { font-weight: 600; font-size: 1.06rem; line-height: 1.3; margin: 0 0 .15rem; }
.w3 .w-lede { color: var(--i2); font-size: .92rem; margin: 0 0 .9rem; max-width: 40em; }
.w3 .w-controls { display: flex; flex-wrap: wrap; gap: .55rem 1.1rem; margin: 0 0 .9rem; }
.w3 .w-field { display: flex; flex-direction: column; gap: .2rem; min-width: 0; }
.w3 .w-flabel { font-size: .75rem; color: var(--i3); line-height: 1.2; }
.w3 .w-seg { display: inline-flex; flex-wrap: wrap; border: 1px solid var(--r); border-radius: var(--rd); overflow: hidden; background: var(--pp); max-width: 100%; }
.w3 .w-seg-b { font: inherit; font-family: var(--mo); font-size: .76rem; line-height: 1.15; color: var(--i2); background: transparent; border: 0; border-right: 1px solid var(--r);
  padding: .5rem .7rem; min-height: 44px; cursor: pointer; text-align: left; transition: background-color .12s, color .12s; }
.w3 .w-seg-b:last-child { border-right: 0; }
.w3 .w-seg-b:hover { background: var(--hv); color: var(--i); }
.w3 .w-seg-b[aria-checked="true"] { background: var(--i); color: var(--pp); }
.w3 .w-seg-b:focus-visible { outline: 2px solid var(--ac); outline-offset: -2px; position: relative; z-index: 1; }
.w3 .w-seg-sub { display: block; font-size: .75rem; opacity: .75; margin-top: .1rem; }
.w3 .w-note { font-size: .84rem; color: var(--i2); margin: .6rem 0 0; }
.w3 .w-foot { font-size: .8rem; color: var(--i3); margin: .9rem 0 0; padding-top: .55rem; border-top: 1px solid var(--r2); line-height: 1.5; }
.w3 .w-err { font-size: .9rem; color: var(--lo); border-left: 3px solid var(--lo); padding: .3rem .7rem; margin: 0; }
.w3 .w-load { font-size: .9rem; color: var(--i3); margin: 0; }
.w3 .w-sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.w3 .w-chip { display: inline-block; font-family: var(--mo); font-size: .75rem; line-height: 1.2; padding: .14rem .42rem; border: 1px solid var(--r); border-radius: 99px; color: var(--i2); background: var(--pp); }
.w3 .w-chip.hl { background: var(--ck); border-color: transparent; color: var(--i); }
.w3 .w-btn { font: inherit; font-family: var(--mo); font-size: .75rem; color: var(--i2); background: var(--pp); border: 1px solid var(--r); border-radius: var(--rd); padding: .35rem .65rem; min-height: 44px; cursor: pointer; }
.w3 .w-btn:hover { background: var(--hv); color: var(--i); }
.w3 .w-btn:focus-visible { outline: 2px solid var(--ac); outline-offset: 2px; }
.w3 button:focus-visible, .w3 [tabindex]:focus-visible { outline: 2px solid var(--ac); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { .w3 *, .w3 *::before, .w3 *::after { transition: none !important; animation: none !important; } }
`;

export function injectCSS(el, css) {
  const s = document.createElement('style');
  s.textContent = BASE_CSS + css;
  el.append(s);
  return s;
}

export function liveRegion(root) {
  const n = h('div', { class: 'w-sr', role: 'status', 'aria-live': 'polite', 'aria-atomic': 'true' });
  root.append(n);
  let t = 0;
  return (msg) => { clearTimeout(t); t = setTimeout(() => { n.textContent = msg; }, 120); };
}

// Segmented control: a radiogroup with a roving tabindex; arrows, Home and End move and select.
export function segmented({ label, options, value, onChange }) {
  const root = h('div', { class: 'w-seg', role: 'radiogroup', 'aria-label': label });
  const btns = [];
  let cur = value;
  function paint() {
    btns.forEach(([o, b]) => {
      const on = o.value === cur;
      b.setAttribute('aria-checked', on ? 'true' : 'false');
      b.tabIndex = on ? 0 : -1;
    });
  }
  function pick(v, user) { if (v === cur) return; cur = v; paint(); if (user && onChange) onChange(v); }
  options.forEach((o) => {
    const b = h('button', { type: 'button', role: 'radio', class: 'w-seg-b', 'data-v': o.value, title: o.title }, o.label, o.sub ? h('span', { class: 'w-seg-sub' }, o.sub) : null);
    b.addEventListener('click', () => pick(o.value, true));
    b.addEventListener('keydown', (e) => {
      const i = btns.findIndex(([x]) => x.value === o.value);
      let j = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') j = (i + 1) % btns.length;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') j = (i - 1 + btns.length) % btns.length;
      else if (e.key === 'Home') j = 0;
      else if (e.key === 'End') j = btns.length - 1;
      if (j === null) return;
      e.preventDefault();
      btns[j][1].focus();
      pick(btns[j][0].value, true);
    });
    btns.push([o, b]);
    root.append(b);
  });
  paint();
  return { el: root, set: (v) => { cur = v; paint(); }, get: () => cur };
}

export function field(label, control) {
  return h('div', { class: 'w-field' }, h('span', { class: 'w-flabel' }, label), control);
}

// A log-scale position helper: returns a function mapping a value to 0..100 (percent).
export function logScale(lo, hi) {
  const a = Math.log(lo), b = Math.log(hi);
  return (v) => clamp(((Math.log(v) - a) / (b - a)) * 100, 0, 100);
}

export function median(xs) {
  const s = [...xs].sort((a, b) => a - b);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}
