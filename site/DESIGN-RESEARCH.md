# Design research: what "perfect" looks like for this page

Date: Tue Oct 13 2026. Scope: rules for the main page (`site/index.html`), on top of `site/DESIGN.md` and its design rules (1 intuitive, creative, interactive; 2 reads like an article; skimmable in seconds; click-first; no sliding, no scroll-driven steps, no drag sliders; moving elements over a table of contents; depth welcome, over-animation bad; dense little graphs per row wanted).

## 0. Method and honest limits

- 12 exemplars read (WebFetch text extraction) and 4 of them also measured in the built-in browser pane with computed styles (Linear, Ciechanowski, Comeau, Stripe). Numbers marked MEASURED below were read from the live page on Oct 13 2026; numbers marked REPORTED come from a text summary or a search snippet and should be re-checked before being quoted.
- Not loaded: Reuters Graphics (fetch refused), WebPageTest (HTTP 403), NYT and FT (not attempted: paywalled, text extraction would show nothing of the design). Setosa returned only the text skeleton, so nothing about its drag behaviour is claimed here beyond what is common knowledge of the site.
- Screenshots: the pane returned small, mostly unrendered first frames (Linear and Compiler Explorer showed an empty dark page at 400x472 before their JS drew). No 1440x900 or 390x844 files were saved; a reviewer who wants them has to capture them. Nothing below depends on a screenshot.
- Search sources are secondary (blogs, checklists). Where a rule is a judgement, it says so.

## 1. Ten principles, ranked

1. **Show the result before the explanation.** The hero is the finding, already running. Proof: Distill's momentum article opens with the widget before any theory ([distill.pub/2017/momentum](https://distill.pub/2017/momentum/)); Brendan Gregg's flame-graph page opens with a real flame graph, then a two-line definition ([brendangregg.com/flamegraphs.html](https://www.brendangregg.com/flamegraphs.html)); Ciechanowski puts the first demo within the first screen ([ciechanow.ski/bicycle](https://ciechanow.ski/bicycle/)). Here: the loop race with the printed ratio, already on.
2. **Every control acts at once, and says what it does in words on the control.** Proof: Comeau's flexbox guide has labelled options that re-lay-out the demo immediately with a live readout beside it ("Reduced by: 0%") ([joshwcomeau.com](https://www.joshwcomeau.com/css/interactive-guide-to-flexbox/)); Ciechanowski names each control in the sentence that introduces it. Here: a toggle reads "Bounds check: on / off", never an icon.
3. **One sentence, one figure, one takeaway.** Short beats alternating with a bolded conclusion. Proof: Parable of the Polygons, one to three lines per beat and a bold takeaway after each experiment ([ncase.me/polygons](https://ncase.me/polygons/)); Apple's one claim + one image per section ([apple.com/macbook-air](https://www.apple.com/macbook-air/)); Linear pairs one claim with one dense, real screenshot ([linear.app](https://linear.app/)).
4. **Density lives in small repeated shapes, not in prose.** Small multiples and sparklines give overview and detail at once (Tufte, via [this summary](https://websites.umich.edu/~mmmc/516/notes/TuftePrinciples.pdf), secondary source). The per-row code + dot plot + side panel pattern is already used on the page. Proof for the pattern at scale: Linear's mockups carry the complexity so the copy can stay sparse; uops.info keeps one table and switches the metric ([uops.info/table.html](https://uops.info/table.html)).
5. **Colour carries one meaning each, everywhere.** Proof: Ciechanowski reuses red/blue/green for forces across every widget so the code is learned once ([ciechanow.ski/bicycle](https://ciechanow.ski/bicycle/)). Here: orange-red = lost SIMD, blue = kept, yellow highlighter = "the check", nothing else is data colour (already in DESIGN.md).
6. **Print the caveat where the number is.** Proof: Benchmarks Game opens with "micro benchmarks ... far from realistic" and names exact implementation versions in labels ([benchmarksgame-team.pages.debian.net](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html)); Apple's heavy footnotes show the cost of the opposite extreme (long, test-config footnotes bury the claim). Here: scope line under the ratio, "n = jobs, CI" on the dot plot, a "what this cannot tell you" box, and no footnote wall.
7. **Direct labels beat legends; labels name the thing, not the code.** "Reverse loop" not "k04". Proof: Benchmarks Game's ambiguous short labels are the cautionary case (labels that look like languages but name implementations); Tufte-style guidance "labels next to the data they describe" ([source](https://websites.umich.edu/~mmmc/516/notes/TuftePrinciples.pdf), secondary).
8. **Multiple entry points, one dominant action.** One primary action in the hero; chips to jump to a loop or a CPU. Proof: Seeing Theory's single "Start" plus per-subsection tiles; its weakness (inconsistent CTA wording "Start" vs "Go to") is the thing to avoid ([seeing-theory.brown.edu](https://seeing-theory.brown.edu/)).
9. **Say what a control will do before it does something irreversible, and escape is always visible.** Proof: Comeau announces that the code editor traps focus until Escape; Ciechanowski warns when Reset restarts a simulation. Here: the slide-over closes with Esc, Back and a visible X.
10. **Skip, don't gate.** Never make the reader sit through an animation. Proof: The Pudding's pockets story offers a jump-to-final-state notice for its scroll animation ([pudding.cool/2018/08/pockets](https://pudding.cool/2018/08/pockets/)); that story's weakness is relying on scroll animation at all, which is the thing the page's rules exclude. Here: the race runs once, <1.5 s, rests on its final frame; Replay is a button.

## 2. Motion budget

**Ambient motion: at most one.** The belt/race on load and on Replay (it then rests). Nothing else loops, ever: no pulsing badges, no marquee, no auto-rotating cards, no animated gradient background.

Calibration (MEASURED unless noted):

| Site | UI transitions found |
|---|---|
| Linear | 100 ms color/background, 160 ms for border/background/box-shadow/opacity/transform, all `cubic-bezier(0.25,0.46,0.45,0.94)`; one 700 ms `cubic-bezier(0.32,0.72,0,1)` transform for large moves |
| Stripe | 240 ms `cubic-bezier(0.45,0.05,0.55,0.95)` for color/opacity, 300 ms `cubic-bezier(0.25,1,0.5,1)` for color/transform |
| Comeau | 200 ms ease for box-shadow/opacity, 400 to 700 ms only for reveal/transform, 350 ms theme colour change |
| Material (REPORTED, [m1.material.io](https://m1.material.io/motion/duration-easing.html)) | mobile baseline 300 ms, enter about 225 ms, exit about 195 ms, avoid over 400 ms; exits about 75% of enter |

Transition table for this page:

| What | Animates | Duration | Easing | Never |
|---|---|---|---|---|
| Hover/focus on chip, cell, row, button | background, border-color, box-shadow (via opacity of a pseudo-element when possible) | 120 ms | `cubic-bezier(0.25,0.46,0.45,0.94)` | scale above 1.03, bounce |
| Press (active) | transform translateY(1px), shadow shrinks | 80 ms | ease-out | delay before result |
| Bounds-check switch | thumb translate, ratio number swap, lane bar width to new value | 200 ms | `cubic-bezier(0.25,1,0.5,1)` | counting up digit by digit; result must be correct at frame 0 of the next paint |
| Select a loop chip / CPU chip | race lanes and ratio swap | 200 ms crossfade/width | same | re-running the whole intro |
| Heatmap cell select | ring + panel content swap | 160 ms | same | moving the layout under the pointer |
| Row expand / section open | height via `grid-template-rows: 0fr to 1fr` | 240 ms | `cubic-bezier(0.25,1,0.5,1)` | animating `height: auto` with JS; content jumping |
| Slide-over (machine code) | translateX(100% to 0) + backdrop opacity | 240 in, 180 out | enter `cubic-bezier(0.2,0,0,1)`, exit `cubic-bezier(0.4,0,1,1)` | blocking input during the transition |
| Rewrite before/after toggle | highlighted lines crossfade | 160 ms | same | typewriter effect |
| Intro race (the one ambient) | lane bars sweep once | 1,200 ms total | linear for the belt, ease-out for the settle | repeat, loop, run on scroll |
| Tooltip | opacity | 100 ms in, 0 ms out | ease-out | delay over 100 ms |

Rules: animate `transform` and `opacity` only; no layout-affecting animation except the 0fr/1fr grid trick. Total motion on screen at one time: one element. `prefers-reduced-motion: reduce` sets all durations to 0 ms and shows the final frame of the race; the information must be the same ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion): reduce means swap movement for something gentler such as a dissolve; scaling and panning large objects is the vestibular trigger). A second rule from a secondary source: if removing an animation breaks understanding, the animation was carrying information and needs a static equivalent ([blakecrosley.com](https://blakecrosley.com/blog/motion-grammar-when-animation-earns-its-frames), unverified secondary).

## 3. Depth recipe (CSS only; no WebGL needed)

Why not WebGL: the page's value is a number you can trust and read; WebGL adds load, a fallback path and an accessibility gap for no extra information. If a 3D hero is ever wanted, it must render the same lanes as the 2D version and fall back to them on `prefers-reduced-motion`, no WebGL, or `(hover: none)`.

The one rule of depth (from [Comeau on shadows](https://www.joshwcomeau.com/css/designing-shadows), summarised in search results): every shadow comes from the same light, so use the same offset ratio, and bigger shadow = higher element. Measured examples: Stripe cards `0 15px 35px rgba(23,23,23,.08)` + `0 3px 6px rgba(23,23,23,.06)` and `0 16px 32px rgba(50,50,93,.12)`; Comeau layered `0 .4px .8px rgba(0,0,0,.027), 0 1.3px 2.7px rgba(0,0,0,.043), 0 6px 12px rgba(0,0,0,.07)`; Linear uses 1px inset rings (`inset 0 0 0 1px rgba(255,255,255,.05)`) on dark surfaces instead of drop shadows.

Tokens (light paper surface; light from top-left, y-offset about 2x blur/3):

```css
:root {
  --e0: 0 0 0 1px rgb(0 0 0 / .06);                         /* resting card: ring only */
  --e1: 0 1px 1px rgb(15 23 42 / .06),
        0 2px 4px rgb(15 23 42 / .06),
        0 6px 12px rgb(15 23 42 / .05);                      /* hovered/selected cell */
  --e2: 0 2px 2px rgb(15 23 42 / .05),
        0 8px 16px rgb(15 23 42 / .08),
        0 24px 48px rgb(15 23 42 / .10);                     /* slide-over, hero stage */
  --e-dark: inset 0 0 0 1px rgb(255 255 255 / .06),
            0 24px 48px rgb(0 0 0 / .35);                    /* on the navy stage */
}
```

- **Stage (hero):** navy panel, `box-shadow: var(--e-dark)`; inside, a subtle top-down gradient `linear-gradient(180deg, rgb(255 255 255 / .04), transparent 40%)` on the lane tracks to suggest a surface. Lanes are 14 px tall bars with `border-radius: 3px` and a 2 px lighter top edge (`box-shadow: inset 0 2px 0 rgb(255 255 255 / .25)`): this is the isometric-bar feel without a transform.
- **Layered cards (Figure 1 side panel):** the selected row's panel sits at `--e1`, the page at `--e0`; selection changes elevation by one step, not colour alone.
- **Tilt (optional, hover-only, one element class):** from the tilt guidance in [this search](https://www.w3schools.com/htmlcss/htmlcss_transforms.asp): perspective about 700 to 1000 px, angles about 5 to 8 degrees, 200 to 300 ms ease. Use it only on the hero stage, not on cells:

```css
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .stage { transform: perspective(1000px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
           transition: transform 200ms cubic-bezier(.25,.46,.45,.94); }
}
/* JS: pointermove sets --rx/--ry = clamp(-4deg, offset*4deg, 4deg); pointerleave resets. No tilt on touch. */
```
  Max 4 degrees (the generic tutorials say 5 to 10; this page's text sits on the stage, so stay under 5). `will-change: transform` only while hovered.
- **Isometric bars (dot-plot rows, optional):** a bar with a 6 px darker "side" made of `box-shadow: 4px 4px 0 var(--bar-side)` (no blur, same direction as the soft shadows). Keep it to the row's value bar; never skew text.
- **Parallax-free:** nothing moves with scroll. Depth comes from elevation, ring borders and the dark stage only.

## 4. Proposal for this page, section by section

Conventions: desktop = 1440x900, phone = 390x844. Everything is visible without JS (static values baked in), the interactive layer enhances.

### 4.1 Hero (first screen holds the whole finding)

```
DESKTOP 1440x900
+--------------------------------------------------------------------------------+
| Third of a Percent                           [Full details]  [Cite]  [GitHub]   |  sticky bar, 48px
+--------------------------------------------------------------------------------+
|  Does turning on libc++ bounds checks really cost 0.3%?      (H1, 4.4rem)       |
|  It depends on the loop. Measured: forward 1.0x, reverse 5.5x.  (1 sentence)    |
|  +---------------- navy stage -----------------------------------------------+  |
|  | Loop: [fwd][2-array][stencil][reverse][stride2][gather][hist][matmul]      |  |
|  | check OFF  ====================>                         1.00x             |  |
|  | check ON   ====================>  (+check)               5.5x  (3.6rem)    |  |
|  | [ Bounds check  (ON) ]   CPU: [EPYC 7763][9V74][9V45][Xeon]   [Replay]     |  |
|  +----------------------------------------------------------------------------+  |
|  clang 18, libc++ FAST, -O2, no PGO. Measured, not modelled. Scroll: Figure 1  |
+--------------------------------------------------------------------------------+
PHONE 390x844: title (2 lines) / sentence / stage with lanes full width / chips in ONE scrolling row / switch (48px high) / ratio. Replay and CPU chips below the fold line but visible by 844 px.
```
Rules: the ratio is the largest number on screen; the switch is the only large control; the race animates once. Chip row scrolls horizontally with a fade on the edge, each chip at least 44 px tall.

### 4.2 Figure 1 workbench (always-visible side panel, per-row mini graphs)

```
DESKTOP
+----------------------------------------------------+---------------------------+
| loop             code        cost per CPU (dot plot)| SELECTED: reverse         |
| forward          for(i..)    o--o-o--o  1.0-1.1x    | 5.5x on EPYC 7763         |
| two-array        a[i]=b[i]   o-o--oo    1.0x        | [asm diff: 2 added lines] |
| stencil          ...         o-o-o-o    1.1x        | NONE: vector  FAST: scalar |
| >reverse<        a[n-1-i]    ......o--o--o  5.5x    | check = highlighted       |
| stride-2         ...         ........o--o  2.8-5.1x | [Open machine code]       |
| ...                                                 | [Copy command]            |
+----------------------------------------------------+---------------------------+
 axis (log scale, 1x line labelled "no cost", 1.02x band "A/A noise") shared by all rows
PHONE: rows stack; each row = name + inline 1-line code + dot plot; tapping a row expands the panel directly beneath it (same content), no separate screen. Selected row stays highlighted.
```
Rules:
- One shared log axis, drawn once at the top and bottom, not per row (range-frame idea, [Tufte summary](https://websites.umich.edu/~mmmc/516/notes/TuftePrinciples.pdf)). Dots are 10 px, hit area 44 px, direct label on the maximum dot only.
- Row height 56 px desktop, 64 px phone. Hover on desktop previews in the side panel (no click needed); click pins it. On touch, tap pins.
- Selected state = elevation `--e1` + 3 px left bar in the data colour + panel update in 160 ms.
- The panel never moves position; it is sticky on desktop (`position: sticky; top: 64px`).
- Keyboard: rows are a roving-tabindex list (Up/Down move, Enter opens machine code, Esc closes); screen reader gets a real `<table>` with the numbers (see checklist) ([Deque](https://www.deque.com/blog/how-to-make-interactive-charts-accessible/): interactive controls must be keyboard operable; a data table alone is an acceptable alternative only for simple charts, per the Highcharts discussion in [this search](https://www.washington.edu/accesstech/events/webinars/data-viz), so also give a one-sentence text summary).

### 4.3 Machine-code slide-over

Right-hand sheet, 560 px desktop, full width on phone, `--e2`. Two columns NONE | FAST with the added instructions highlighted in the yellow "check" colour and the lost `padd`/`mulps` lines in orange-red; a one-line reading above it ("FAST adds `cmp`+`jae`; the loop is no longer vectorised"). Esc, Back, X and backdrop tap all close it.

### 4.4 Compiler matrix

A grid of 28 compiler rows by 6 loops, one small square per cell (12 px desktop, 20 px phone), orange = lost, blue = kept, grey = n/a; direct row labels on the left (`clang 18`, `gcc 13`), hover/tap shows the cell's answer in a fixed strip under the grid (not a floating tooltip on phone). Gist line above: "Reverse and stride-2 lost SIMD in all 54 clang rows." One button opens the full table.

### 4.5 Census

One horizontal 100% bar pair: "19 libraries: 1 of 593" vs "25 numeric projects: 444 of 4,968", each segment clickable to list the projects. Label counts as counts ("counted, not timed"). Nothing animates.

### 4.6 Rewrite before/after

A single toggle "Original loop | With one size check up front" swapping two code blocks and the ratio (5.5x to 1.0x). Same position, same size, 160 ms crossfade, the changed lines highlighted. Default state = the slow one, so the toggle shows the improvement.

### 4.7 Real programs

Two horizontal bars per program (nlohmann/json, fmt) with CI whiskers and the label "timed on 3 CPU models"; below, the instruction-share chip "lost loops hold 0 to 6% of executed instructions". A sentence says what the bar means and what it does not.

### 4.8 Placement

Four tap targets (alignment 0/16/32/48) switch the same two-bar result; the numbers swap in place. Caption: "same code, moved by N bytes, 1.6x vs 1.0x".

### 4.9 Limits

A bordered box, always visible (not collapsed), 5 bullets max, each starting with a bolded noun: "libc++ 18 only", "shared VMs", "no PGO", "programs picked for containing lost loops", "9V45 fragile". Honest-first is the trust move ([Benchmarks Game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html) puts its caveat first).

Section navigation: no table of contents. A slim sticky bar shows the current section title only if it can be done without scroll-driven animation; otherwise use the chip row in the hero that anchors to Figure 1, compilers, census, rewrite, programs, limits.

## 5. Details that delight (10) and things that tire (10)

Delight:
1. The ratio number is correct on first paint and also in the HTML without JS.
2. Hovering a row previews it in the side panel; clicking pins it (no mode to learn).
3. The yellow highlighter on the exact added instruction is the same yellow as the "check" lane segment in the hero.
4. A copy-command button that changes to "Copied" for 1,200 ms and returns focus.
5. The URL hash records the selected loop and CPU, so a shared link opens on the same cell (Ciechanowski-style presets: [ciechanow.ski](https://ciechanow.ski/bicycle/) uses inline links as state presets).
6. A tiny "A/A noise" band drawn on the axis so the reader sees what "1.02x" is worth.
7. Dot plot dots are keyboard-focusable with a visible 2 px ring and 3:1 contrast.
8. Counterfactual rows ("what if we change nothing": a null result is labelled as the lesson, as in [Parable of the Polygons](https://ncase.me/polygons/)).
9. Empty/unavailable cells say why ("no 9V45 run for this loop") instead of staying blank (The Pudding's empty state explains missing results: [pudding.cool](https://pudding.cool/2018/08/pockets/)).
10. Reduced-motion and print show the final frame with the same numbers.

Tire:
1. Any animation that replays when the section scrolls into view.
2. Counting-up numbers (the reader waits for the answer).
3. Tooltips that cover the thing being pointed at, or that never appear on touch.
4. Drag-only or slider-only controls.
5. Legends that make the eye travel; Greek-letter-only controls (Distill's widgets are a known example, [distill.pub](https://distill.pub/2017/momentum/)).
6. Repeating the same CTA with different words (Seeing Theory) or several competing CTAs (Linear).
7. Footnote walls under every claim (Apple's performance charts).
8. Full-width auto-playing background video or looping gradients.
9. A table of contents drawn as a pinned side rail that competes with the side panel.
10. Hover-only information; jargon with no inline gloss (uops.info's "Uops", "Port Usage" example).

## 6. Scoring checklist (0 = missing, 1 = partly, 2 = done). Pass: 32 of 40 and no 0 on items 1, 2, 3, 9.

| # | Item | How to check | Score |
|---|---|---|---|
| 1 | First view (1440x900 and 390x844) shows the finding: ratio >= 3.6rem, switch, loop chips, scope line | screenshot both sizes, no scroll | |
| 2 | Ratio correct on first paint and in HTML with JS off | view-source / disable JS | |
| 3 | Every control changes the figure in under 250 ms, no loading state | click each, time it | |
| 4 | At most one ambient motion; none loops; none runs on scroll | DevTools, scroll the page | |
| 5 | `prefers-reduced-motion: reduce` shows final frames, same information | emulate in DevTools | |
| 6 | Transitions match section 2 table (duration and easing) | grep `transition`/`animation` | |
| 7 | Shadows use the three elevation tokens, one light direction; no blur over 48 px | grep `box-shadow` | |
| 8 | No scroll-driven, sliding, or drag-slider elements | grep `scroll`/`range` | |
| 9 | Every number on the page traces to `site/data/*.json` or a baked HTML value | run the build script, diff | |
| 10 | Caveat sits within one screen of every headline number | read in sequence | |
| 11 | Colours: orange-red, blue, yellow-check only for data; one meaning each | audit CSS vars | |
| 12 | Text/UI contrast: body 4.5:1 or better, dot/ring/focus 3:1 or better | axe / contrast tool | |
| 13 | Touch targets: all controls and dot hit areas at least 44x44 CSS px on phone (WCAG 2.2 AA floor is 24x24, [source](https://allaccessible.org/blog/wcag-258-target-size-minimum-implementation-guide), secondary) | measure in DevTools phone mode | |
| 14 | Keyboard: Tab reaches switch, chips, rows; arrows move rows; Enter opens; Esc closes slide-over; visible focus ring | tab through | |
| 15 | Charts have a real `<table>` or text summary alternative, and `aria-label`/`aria-live` on the ratio | screen reader or a11y tree | |
| 16 | Hover info also available on tap and focus | emulate touch | |
| 17 | Direct labels on dot plots; no legend needed | read the figure cold | |
| 18 | Each section: one gist line + one figure + one button for details; no prose over 4 lines before a figure | read through | |
| 19 | Phone main page within the page's length cap (7,195 px default, 13,228 cap); no horizontal scroll | measure scrollHeight | |
| 20 | Print stylesheet shows the static state with all numbers | print preview | |

Reviewer's note: score from screenshots and DevTools, not from memory; list each 0 or 1 with the fix.

## 7. Sources (all fetched or searched Oct 13 2026)

Exemplars: [ciechanow.ski/bicycle](https://ciechanow.ski/bicycle/) (MEASURED: title 38.4 px/600 Inter, body 19.2 px/30.72 line IBM Plex Sans, text column 446 px inside 704 px, background #f8f8f8, 118 canvases), [ncase.me/polygons](https://ncase.me/polygons/), [seeing-theory.brown.edu](https://seeing-theory.brown.edu/), [setosa.io](https://setosa.io/ev/ordinary-least-squares-regression/) (thin), [joshwcomeau.com flexbox](https://www.joshwcomeau.com/css/interactive-guide-to-flexbox/) (MEASURED: h1 36 px/500, body 18 px/27 line), [distill.pub momentum](https://distill.pub/2017/momentum/), [uops.info](https://uops.info/table.html), [pudding.cool pockets](https://pudding.cool/2018/08/pockets/), [Benchmarks Game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/index.html), [web.dev rendering performance](https://web.dev/articles/rendering-performance) (steal: standfirst + a numbered diagram per variant, bold lead-ins, concrete numeric targets), [linear.app](https://linear.app/) (MEASURED: h1 38 px/510, line 41.8, tracking -0.836 px, body 16 px, background #08090a), [vercel.com](https://vercel.com/) (steal: one claim + one proof, one repeated primary action; visual style not verifiable from text), [stripe.com](https://stripe.com/) (MEASURED: h1 34 px/300, tracking -0.34 px), [apple.com/macbook-air](https://www.apple.com/macbook-air/), [brendangregg.com/flamegraphs.html](https://www.brendangregg.com/flamegraphs.html) (hover details in a status bar, click to zoom, search highlighting; opens with a real example; weakness: stale update list and typos), Compiler Explorer ([godbolt.org](https://godbolt.org/), only an unrendered first frame was captured).

Technique sources: [Material duration and easing](https://m1.material.io/motion/duration-easing.html), [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion), [Comeau designing shadows](https://www.joshwcomeau.com/css/designing-shadows), [Deque accessible interactive charts](https://www.deque.com/blog/how-to-make-interactive-charts-accessible/), [WCAG target size summaries](https://allaccessible.org/blog/wcag-258-target-size-minimum-implementation-guide), [Tufte principles summary](https://websites.umich.edu/~mmmc/516/notes/TuftePrinciples.pdf), [CSS tilt guidance](https://www.w3schools.com/htmlcss/htmlcss_transforms.asp).

Unchecked (no source read): Observable notebooks, NYT, FT, Reuters Graphics, WebPageTest, Phoronix, Framer showcases, Apple's measured CSS. Do not cite them as researched.
