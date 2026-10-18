/* Third of a Percent: the interactive layer on top of app.js (slide-over,
   rewrite toggle, real-programs chart, widget loader, progress bar and rail). It reads the same data
   through app.js's own state (S) and helpers; every number it prints comes from data/, and every
   animation is an illustration of a measured ratio, labelled as one. No audio, no external scripts. */
(function () {
'use strict';
const $ = (id) => document.getElementById(id);
const RM = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function whenReady(test, ms = 15000) {
  const t0 = performance.now();
  while (performance.now() - t0 < ms) { try { if (test()) return true; } catch (e) { /* app.js still starting */ } await sleep(60); }
  return false;
}

/* ---------- chrome: current section, rail ---------- */
function chrome() {
  const cur = $('bar-sec'), rail = $('rail'), bar = $('bar');
  const secs = [...document.querySelectorAll('.body section[id]')].filter((s) => s.querySelector('h2'));
  const links = new Map();
  for (const s of secs) {
    const h = s.querySelector('h2');
    const no = h.querySelector('.secno');
    const name = (no ? h.textContent.slice(no.textContent.length) : h.textContent).replace('¶', '').trim();
    const a = document.createElement('a');
    a.href = `#${s.id}`;
    a.tabIndex = -1; // the Contents menu in the top bar is the keyboard route to a section; the rail is a pointer shortcut
    a.innerHTML = '<i></i><span></span>';
    a.lastChild.textContent = name;
    a.title = name;
    rail.append(a);
    links.set(s, [a, name]);
  }
  let tick = false;
  const upd = () => {
    tick = false;
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.classList.toggle('on', scrollY > innerHeight * 0.6);
    document.documentElement.classList.toggle('scrolled', scrollY > 120); // the section dots appear once the reader has scrolled
    let on = null;
    // the section under the sticky bar (46 px) plus a small margin; a Contents jump lands a section's top at about 70 px
    for (const s of secs) if (s.getBoundingClientRect().top <= 100) on = s;
    if (max > 0 && scrollY >= max - 2) on = secs[secs.length - 1]; // the last, short section can never reach the line
    for (const [s, [a]] of links) a.classList.toggle('on', s === on);
    cur.textContent = on ? links.get(on)[1] : '';
  };
  addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive: true });
  addEventListener('resize', upd);
  upd();
}

/* ---------- slide-over with the real machine code (the existing Figure 2, moved in while open) ---------- */
let asmOpener = null, asmPushed = false, asmIgnorePop = false;
function openAsm(k, opener) {
  const panel = $('asm-panel');
  asmOpener = opener || document.activeElement;
  if (S.sel !== k) select(k, false, true);
  const f2 = $('fig2');
  f2.classList.add('open');
  $('asm-slot').append(f2);
  panel.hidden = false;
  if (!asmPushed) { history.pushState({ asm: 1 }, '', location.href); asmPushed = true; } // Back closes the panel, not the site
  document.body.classList.add('panel-open');
  requestAnimationFrame(() => { panel.classList.add('open'); $('asm-close').focus(); });
}
function closeAsm() {
  const panel = $('asm-panel');
  if (panel.hidden) return;
  if (asmPushed) { asmPushed = false; asmIgnorePop = true; history.back(); }
  panel.classList.remove('open');
  $('figures').append($('fig2'));
  document.body.classList.remove('panel-open');
  setTimeout(() => { panel.hidden = true; }, RM() ? 0 : 220);
  if (asmOpener && asmOpener.focus) asmOpener.focus({ preventScroll: true });
}
function buildPanel() {
  const p = document.createElement('aside');
  p.id = 'asm-panel'; p.className = 'slideover'; p.hidden = true;
  p.setAttribute('role', 'dialog'); p.setAttribute('aria-label', 'Machine code, checks off and on');
  p.innerHTML = '<div class="so-head"><span>Machine code</span><button type="button" id="asm-close" class="so-close" aria-label="Close the machine code panel">Close</button></div><div id="asm-slot" class="so-body"></div>';
  const veil = document.createElement('div');
  veil.id = 'asm-veil'; veil.className = 'veil'; veil.hidden = true;
  document.body.append(veil, p);
  p.querySelector('#asm-close').addEventListener('click', closeAsm);
  veil.addEventListener('click', closeAsm);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !p.hidden) closeAsm(); });
  addEventListener('popstate', () => { if (asmIgnorePop) { asmIgnorePop = false; return; } if (!p.hidden) { asmPushed = false; closeAsm(); } });
  new MutationObserver(() => { veil.hidden = p.hidden; }).observe(p, { attributes: true, attributeFilter: ['hidden'] });
  p.addEventListener('keydown', (e) => { // keep Tab inside the open panel
    if (e.key !== 'Tab') return;
    const f = [...p.querySelectorAll('button, a[href], [tabindex="0"]')].filter((n) => n.offsetParent !== null);
    if (!f.length) return;
    const a = f[0], z = f[f.length - 1];
    if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
    else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
  });
}

/* ---------- section 5: before and after the rewrite ---------- */
function buildRewrite() {
  const M = S.mit;
  if (!M || !$('mit-toggle-box')) return;
  const box = $('mit-toggle-box');
  const shapes = M.shapes;
  const st = { i: Math.max(0, shapes.findIndex((s) => s.kernel === 'm04_rev')), after: false };
  box.replaceChildren();
  const seg = document.createElement('div'); seg.className = 'seg'; seg.setAttribute('role', 'radiogroup'); seg.setAttribute('aria-label', 'Loop shape');
  shapes.forEach((s, i) => { const b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.i = i; b.textContent = SHAPE_NAMES[s.kernel] || s.shape; seg.append(b); });
  const sw = document.createElement('button'); sw.type = 'button'; sw.className = 'sw'; sw.setAttribute('role', 'switch');
  sw.innerHTML = '<span class="sw-l">Rewrite</span><span class="sw-t" aria-hidden="true"><i></i></span><b>before</b>';
  const bar = document.createElement('div'); bar.className = 'rw-bar';
  bar.innerHTML = '<div class="rw-track"><span class="rw-one"></span><span class="rw-fill"></span></div><div class="rw-val"></div>';
  const note = document.createElement('p'); note.className = 'rw-note small';
  const ctl = document.createElement('div'); ctl.className = 'controls'; ctl.append(seg, sw);
  box.append(ctl, bar, note);
  const dom = [0.5, 10], pp = (v) => (Math.log(clamp(v, dom[0], dom[1])) - Math.log(dom[0])) / (Math.log(dom[1]) - Math.log(dom[0]));
  const upd = () => {
    const s = shapes[st.i];
    const orig = s.variants.find((v) => v.variant === 'orig'), rec = s.variants.find((v) => v.variant === s.recommended);
    const v = st.after ? rec : orig;
    for (const b of seg.children) { const on = +b.dataset.i === st.i; b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1; }
    sw.setAttribute('aria-checked', st.after); sw.querySelector('b').textContent = st.after ? 'after' : 'before';
    const lo = pp(v.range.min), hi = pp(v.range.max);
    const f = bar.querySelector('.rw-fill');
    f.style.left = `${lo * 100}%`; f.style.width = `${Math.max(0.8, (hi - lo) * 100)}%`;
    f.classList.toggle('good', st.after);
    bar.querySelector('.rw-one').style.left = `${pp(1) * 100}%`;
    bar.querySelector('.rw-val').textContent = `${rangeX(v.range.min, v.range.max)} as long as the original without checks`;
    note.textContent = st.after ? `Rewrite: ${variantLabel(rec) || rec.variant}. Checks still on (aligned, range over every job and both sizes).` : 'Original loop, checks on (aligned, range over every job and both sizes).';
  };
  seg.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { st.i = +b.dataset.i; upd(); } });
  radioKeys(seg, 'i', (i) => { st.i = +i; upd(); });
  sw.addEventListener('click', () => { st.after = !st.after; upd(); });
  upd();
}

/* ---------- section 7: real programs, bars with intervals, CPU switch, PGO overlay ---------- */
function buildPrograms() {
  const R7 = S.rw, box = $('rw-chart');
  if (!R7 || !box) return;
  const T = R7.timing, st = { cpu: T.main_cpu, pgo: false };
  box.replaceChildren();
  const groups = T.groups.filter((g) => g.enough);
  const seg = document.createElement('div'); seg.className = 'seg'; seg.setAttribute('role', 'radiogroup'); seg.setAttribute('aria-label', 'CPU model');
  groups.forEach((g) => { const b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.cpu = g.cpu_model; b.textContent = g.cpu_short; b.title = `${g.jobs} jobs`; seg.append(b); });
  const sw = document.createElement('button'); sw.type = 'button'; sw.className = 'sw'; sw.setAttribute('role', 'switch');
  sw.innerHTML = '<span class="sw-l">With PGO</span><span class="sw-t" aria-hidden="true"><i></i></span><b>off</b>';
  const ctl = document.createElement('div'); ctl.className = 'controls'; ctl.append(seg, sw);
  const chart = document.createElement('div'); chart.className = 'pc';
  const cap = document.createElement('p'); cap.className = 'small';
  box.append(ctl, chart, cap);
  const MAXP = 12; // percent at the right edge (clipped with an arrow)
  const upd = () => {
    for (const b of seg.children) { const on = b.dataset.cpu === st.cpu; b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1; }
    sw.setAttribute('aria-checked', st.pgo); sw.querySelector('b').textContent = st.pgo ? 'on' : 'off';
    const g = groups.find((q) => q.cpu_model === st.cpu);
    const pg = S.pgo && S.pgo.cpus.find((c) => c.cpu_model === st.cpu);
    chart.replaceChildren();
    const x = (pc) => clamp(pc / MAXP, 0, 1) * 100;
    for (const [key, m] of Object.entries(g.rows)) {
      const f = m.fast, name = RW_NAMES[key] || key;
      const lo = (f.lo - 1) * 100, hi = (f.hi - 1) * 100, mid = (f.ratio - 1) * 100;
      const row = document.createElement('div'); row.className = 'pc-row';
      row.tabIndex = 0;
      row.setAttribute('aria-label', `${name}: ${rwPctOver(f.ratio)} slower with checks on, interval ${rwPctOver(f.lo)} to ${rwPctOver(f.hi)}, ${m.reading}`);
      const zero = x(0), l = x(Math.max(0, lo)), r = x(Math.max(0, hi)), mm = x(Math.max(0, mid));
      let pgoMark = '';
      if (st.pgo && pg) {
        const pr = pg.rows.find((q) => q.name === name);
        if (pr && pr.pgo && pr.pgo.fast) pgoMark = `<span class="pc-pgo" style="left:${x((pr.pgo.fast.ratio - 1) * 100)}%" title="With PGO: ${rwPctOver(pr.pgo.fast.ratio)}"></span>`;
      }
      row.innerHTML = `<span class="pc-name"></span><span class="pc-track"><span class="pc-zero" style="left:${zero}%"></span><span class="pc-ci" style="left:${l}%;width:${Math.max(0.6, r - l)}%"></span><span class="pc-dot ${m.reading === 'detectably slower' ? 'slow' : ''}" style="left:${mm}%"></span>${pgoMark}</span><span class="pc-val"></span>`;
      row.querySelector('.pc-name').textContent = name;
      row.querySelector('.pc-val').textContent = `${rwPctOver(f.ratio)} ${m.reading === 'detectably slower' ? '' : (m.reading === 'detectably faster' ? '(faster)' : '(not detectable)')}`.trim();
      chart.append(row);
    }
    cap.textContent = `FAST ÷ NONE, whole program, ${g.cpu_short}, ${g.jobs} jobs; dot is the pooled ratio as a percent over 1, bar its 95% interval${st.pgo ? '; open ring: the same program built with profile-guided optimization' : ''}. Not a verdict on Google's services. Table 9 above has both columns and the noise floor.`;
  };
  seg.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { st.cpu = b.dataset.cpu; upd(); } });
  radioKeys(seg, 'cpu', (c) => { st.cpu = c; upd(); });
  sw.addEventListener('click', () => { st.pgo = !st.pgo; upd(); });
  if (S.pgo) { sw.disabled = false; } else sw.disabled = true;
  upd();
}

/* ---------- widgets (the interactive modules); a one-line fallback stays if one is missing ---------- */
async function mountWidgets() {
  const ctx = { base: 'data/', tokens: getComputedStyle(document.documentElement) };
  const phone = matchMedia('(max-width: 640px)').matches;
  for (const name of ['placement', 'mitigation', 'programs']) {
    const el = $(`w-${name}`), wd = $(`wd-${name}`);
    if (!el) continue;
    const keep = [...el.childNodes];
    let m;
    try { m = await import(`./widgets/${name}.js`); } catch (err) { continue; } // missing: the one-line fallback stays
    if (name === 'programs' && $('rw-chart')) $('rw-chart').hidden = true;
    const mount = async () => {
      if (el.__widget) return;
      try {
        el.replaceChildren();
        el.__widget = await m.mount(el, ctx);
        el.classList.add('mounted');
      } catch (err) { el.replaceChildren(...keep); el.classList.remove('mounted'); el.__widget = null; }
    };
    const folded = el.closest('.sec-body');
    if (folded && folded.hidden) { const sec = folded.parentElement; const once = () => { sec.removeEventListener('secopen', once); mount(); }; sec.addEventListener('secopen', once); continue; }
    if (wd && phone && name === 'programs') { // phones: this one is folded, mounted on first open, so the page stays short
      wd.open = false;
      wd.addEventListener('toggle', () => { if (wd.open) mount(); });
    } else await mount();
  }
}

/* ---------- sections: a glance first, the full text one click away ---------- */
const GLANCE = { placement: ['#wd-placement'], mitigate: ['#mit-toggle-box'] }; // census, compiler grid and the real programs: a one-line verdict, the figure behind Details
function openSec(sec, on) {
  const body = sec.querySelector(':scope > .sec-body'), btn = sec.querySelector(':scope > .sec-more');
  if (!body) return;
  body.hidden = !on;
  btn.setAttribute('aria-expanded', on ? 'true' : 'false');
  btn.textContent = on ? 'Hide details' : 'Details';
  sec.classList.toggle('sec-open', on);
  if (on && typeof updateScrollHints === 'function') updateScrollHints();
  if (on) sec.dispatchEvent(new Event('secopen'));
}
function openFor(target) {
  const sec = target && target.closest && target.closest('section.sec');
  if (sec && sec.querySelector(':scope > .sec-body').hidden) openSec(sec, true);
}
function collapsibles() {
  const open = window.__OPEN_ALL__ === true;
  for (const sec of document.querySelectorAll('.body section[id]')) {
    const h2 = sec.querySelector(':scope > h2');
    if (!h2 || sec.id === 'references') continue;
    const gist = sec.querySelector(':scope > .gist');
    const keep = new Set((GLANCE[sec.id] || []).map((q) => sec.querySelector(q)).filter(Boolean));
    const body = document.createElement('div');
    body.className = 'sec-body'; body.id = `sb-${sec.id}`;
    const glance = [];
    for (const n of [...sec.children]) {
      if (n === h2 || n === gist) continue;
      if (keep.has(n)) { glance.push(n); continue; }
      body.append(n);
    }
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'sec-more'; btn.setAttribute('aria-controls', body.id);
    btn.addEventListener('click', () => openSec(sec, body.hidden));
    sec.classList.add('sec');
    sec.append(...glance, btn, body);
    openSec(sec, open);
  }
  const go = () => { const t = location.hash.length > 1 ? document.getElementById(decodeURIComponent(location.hash.slice(1))) : null; if (t) { openFor(t); t.scrollIntoView(); } };
  addEventListener('hashchange', go);
  document.addEventListener('click', (e) => { const a = e.target.closest('a[href^="#"]'); if (a && a.getAttribute('href').length > 1) openFor(document.getElementById(a.getAttribute('href').slice(1))); });
  document.body.classList.add('sec-js');
  go();
}

/* ---------- word chips: tap one, its one-line definition shows ---------- */
function buildWords() {
  const box = $('words'); if (!box) return;
  const out = $('w-def'); let cur = null;
  for (const b of box.querySelectorAll('.w-chip')) b.addEventListener('click', () => {
    const on = cur !== b;
    for (const x of box.querySelectorAll('.w-chip')) x.setAttribute('aria-expanded', x === b && on ? 'true' : 'false');
    cur = on ? b : null;
    out.hidden = !on;
    if (on) { out.textContent = ''; const s = document.createElement('b'); s.textContent = b.textContent + ': '; out.append(s, b.dataset.def); }
  });
}

/* ---------- boot ---------- */
async function boot() {
  buildPanel();
  buildWords();
  collapsibles();
  chrome();
  if (!(await whenReady(() => S.ix && S.pooled && S.rows && S.cpu && S.sel))) return;
  // follow Figure 1: a new loop or CPU model there moves the race
  const _select = select, _show = showCpu;
  select = function (k, f, p) { const r = _select(k, f, p); HeroRace.sync(true); return r; };
  showCpu = function () { const r = _show(); HeroRace.sync(false); return r; };
  HeroRace.build({ openAsm });
  await whenReady(() => S.mit && S.rw && S.pgo !== undefined, 8000);
  buildRewrite();
  buildPrograms();
  mountWidgets();
}
boot();
})();
