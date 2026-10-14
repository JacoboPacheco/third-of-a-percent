# Design notes for the main page

Design rules: click-first, no sliders, short. The reader is often a recruiter or interviewer: the finding must be clear in seconds and every control must act at once.

1. First ten seconds: the first view (1440x900 and 390x844) holds the whole finding: the finding drawn one of four ways (see HERO VARIANTS below; the old dark navy race was dropped; the default, variant 4, draws all eight loops at once as eight lanes of two bars, so the contrast between loops that tie and loops that lag is one image), eight glyph tiles that draw each loop's access pattern, a bounds-check switch (on at the start, so the measured ratio is already printed), the CPU chips, the one-line scope sentence (clang, libc++ FAST, -O2, no PGO), a Reproduce button and a Full details link in the sticky bar. On a phone variant 4 shows all eight lanes with their ratios in the first view and its caption area after a short scroll. One scroll later: Figure 1, the clickable heatmap (rows open the machine code; tooltips on hover).
2. Click-first: no scrollytelling, no pinned or scroll-driven figures, no drag sliders. Every state change is instant; the hero's illustration runs once, briefly, on load and on Replay, then rests on its final frame. Under 250 ms for any transition, never needed to read a result; reduced motion shows the final frame. The placement widget is four tap targets (arrow keys stay as an extra); the machine code opens in a slide-over.
3. Short by default: every section after the figures is collapsed to a one-line gist plus one glanceable, click-driven figure where it has one (census chart, compiler matrix, rewrite before/after toggle, placement and programs widgets); one button opens the full text, and a link or hash into a collapsed section opens it. Phone: the collapsed main page is about 7,200 px (every section open: about 14,700; depth lives on details.html). Without JavaScript every section is open and the key numbers are in the HTML.
4. Article layer kept, compact: Source Serif 4 text column, numbered figures and tables, sidenotes on wide screens, references, cite box, print stylesheet (figures print as their static state). Identity: white paper plus the hero stage (light, paper or graphite, per variant); --lost orange-red and --kept blue are the only data colours, the yellow highlighter (--check-hl) always means "the check". Type hierarchy by size and weight (4.1rem title, 3.7rem measured ratio). Two voices only: Source Serif 4 for text and labels, IBM Plex Mono for code and numbers; no italic captions; nothing under 12 px; captions at least 4.5:1.
5. Honesty of the animation: an illustration scaled to the measured pooled ratio (aligned, smallest size; clamped, and the caption says so); the printed number is the data's. Nothing numeric is typed into the page: everything comes from site/data/*.json, and the first view's key numbers are baked into the HTML by scripts/build_site_data.py. Widgets in site/widgets/ mount into #w-placement, #w-mitigation, #w-programs (folded on phones, mounted on first open, a one-line fallback if a module is missing) and read only: --paper --ink --ink-2 --ink-3 --rule --rule-2 --hover --sel --lost --kept --none --simd-tint --check-hl --serif --mono --accent --radius.

## HERO VARIANTS

Four contrasting presentations of the same finding, all built from the same data (the measured pooled ratio per loop and CPU model), the same controls and the same checks. Code: `site/race.js` (drawing, tiles, readout, switcher), `site/hero.css` (the three looks).

- **1 Race track.** A light, elevated stage. Two isometric lanes, check off and check on, with a finish line: a wide SIMD beam steps four tiles at a time in one lane, a single cursor with a yellow gate in the other; each lane ends with its time as a multiple of the unchecked run.
- **2 Poster** (the earlier default). White paper, a heavy rule, one huge extruded number (the ratio) and, small beside it, the loop's access pattern drawn as arcs over array cells (forward, backward, every second, scattered) with a yellow mark where a check sits.
- **3 Inspector.** A graphite stage: a lens moves over the array, the real machine code of the hot loop sits under it with the check lines highlighted (read live from `data/asm`, checks on or off), and a gauge needle shows the ratio on a log scale.

- **4 The whole map in one race** (the default). A full-width white stage. Eight lanes in a tray (glyph tile, loop name, two thin bars, the measured ratio at the lane end). A bar is as long as the pooled ratio on one linear axis, so the unchecked finish is a single heavy vertical line at 1x: forward lanes end on it, reverse, stride-2 and matrix multiply run far past it. Bar texture says what the compiler did: wide blocks are SIMD (four numbers per step), thin cells with a yellow notch are one element per step with a check on each; a yellow cap marks the check riding on the leftover tail. Direct labels sit on the bars in the empty track space ("check off", one lane per outcome: "check on, keeps SIMD / loses SIMD / no SIMD to lose"); on a phone a four-swatch key replaces them. One click on a lane opens the real machine code (on a touch screen the first tap shows the loop's sentence, the second opens it). Hovering or focusing a lane highlights it and shows its own sentence in a fixed-height caption area (every loop has its own wording, taken from the compiler's remarks and Figure 2's reading). The run happens once on load (bars grow from the start; short bars finish first, 260 to 1,200 ms) and rests with every finish position visible; a switch off hides the checked bars (baseline), Replay runs it again. Lengths are exact (the data's ratios, no clamping); only the speed is for show, and the caption says so.

Shared: eight glyph tiles (SVG of the access pattern, text label, the loop's own measured ratio, tinted orange-red when the check makes it lose SIMD), a Bounds check switch, CPU model buttons, Replay, a Reproduce button (opens the one-command box), the slide-over with the full machine code. Motion: one run of 1.2 s at most, then it rests; reduced motion draws the final frame; hover and press 100 to 120 ms; nothing else moves. Depth: the three elevation tokens, tiles and lanes with a drawn thickness; no tilt, nothing spins.

How to switch: add `#hero=1` to `#hero=4` to the URL (the choice survives clicking loops and CPUs). A small "Hero: 1 2 3 4" switcher appears inside the sticky top bar (it can never cover text; on a phone it takes its own row of the bar) only when the hash contains "hero", or after pressing the key H (H again hides it). A visitor with no hash sees the default and no switcher. The default is the `DEFAULT_HV` constant at the top of `site/race.js`.

Scores (the first scoring, three variants; research checklist, section 6 of DESIGN-RESEARCH.md, 0 to 2 each; superseded by SCORE ROUND 2):

| # | Item | V1 | V2 | V3 |
|---|---|---|---|---|
| 1 | first view holds the finding | 2 | 2 | 2 |
| 2 | ratio on first paint and in HTML without JS (HTML has the range only, the ratio is printed by JS) | 1 | 1 | 1 |
| 3 | every control acts at once | 2 | 2 | 2 |
| 4 | at most one ambient motion, none loops | 2 | 2 | 2 |
| 5 | reduced motion shows the final frame | 2 | 2 | 2 |
| 6 | transitions match the table | 2 | 2 | 2 |
| 7 | shadows use the elevation tokens | 2 | 2 | 1 |
| 8 | no scroll-driven, sliding or drag elements | 2 | 2 | 2 |
| 9 | every number traces to data | 2 | 2 | 2 |
| 10 | caveat within one screen | 2 | 2 | 2 |
| 11 | colours: one meaning each | 2 | 2 | 1 |
| 12 | contrast 4.5:1 | 2 | 2 | 2 |
| 13 | touch targets 44 px (tiles yes; CPU buttons 34 to 36 px on phones) | 1 | 1 | 1 |
| 14 | keyboard | 2 | 2 | 2 |
| 15 | text alternative | 2 | 2 | 2 |
| 16 | hover info also on tap and focus | 2 | 2 | 2 |
| 17 | direct labels (V2's arcs got a one-line label after the first scoring) | 2 | 2 | 2 |
| 18 | gist plus one figure | 2 | 2 | 2 |
| 19 | phone page length (9,248 / 9,246 / 9,328 px, cap 10,500) | 2 | 2 | 2 |
| 20 | print shows the static state (V3's white-on-dark canvas does not print) | 2 | 2 | 1 |
| | total of 40 | 38 | 38 | 35 |

Default: variant 4 (see SCORE ROUND 2 below for the scoring and for why it is the default although the original 20 items rank variant 2 one point higher).

## SCORE ROUND 1 (default hero V2 at the time; checklist of DESIGN-RESEARCH.md section 6, 0 to 2)

Scored from playwright screenshots at 1440x900 and 390x844, a phone touch audit (`elementFromPoint` 22 px above and below each control), print emulation, grep of the CSS, and `check_site.py`. Before = the page as found; after = this round.

| # | Item | Before | Evidence before | After | What changed |
|---|---|---|---|---|---|
| 1 | first view holds the finding | 1 | the canvas label above the arcs was cut off at the canvas edge on both sizes ("... (yellow: a che") | 2 | the label is measured and shortened to fit (race.js) |
| 2 | ratio on first paint and without JS | 1 | HTML held "...", JS printed the ratio | 2 | `scripts/build_site_data.py` bakes the default cell (reverse, EPYC 7763, aligned, L1) as `heroRatio`, `heroCpu`, `heroJobs`, `heroWhat`; check_site reads it from the raw HTML |
| 3 | every control acts at once | 2 | clicks swap at once | 2 | |
| 4 | at most one ambient motion | 2 | the hero run, once, rests | 2 | |
| 5 | reduced motion = final frame | 2 | | 2 | |
| 6 | transitions match the table | 1 | global 180 ms, a 350 ms `left` transition | 2 | global 120 ms with the table easing; the dot slide is 200 ms |
| 7 | shadows use the elevation tokens | 1 | slide-over had a 60 px blur, the contents list an ad hoc one | 2 | both use `--e2` and `--e1` (small ring shadows on dots stay as marks, not elevation) |
| 8 | nothing scroll-driven | 1 | a reading-progress bar scaled with scroll | 2 | removed (bar, JS, CSS; check_site asserts it is gone). The rail dots and the bar's section name still follow the scroll position as passive state, nothing slides |
| 9 | every number traces to data | 2 | check_site walks the numbers | 2 | the new baked hero spans come from the same build |
| 10 | caveat within one screen | 2 | scope line under the title | 2 | |
| 11 | one colour, one meaning | 2 | | 2 | the new favicon state reuses orange (loses SIMD) and blue (keeps it) |
| 12 | contrast | 2 | earlier measurement, every text pair at least 4.8:1 | 2 | new text uses `--ink-3` and `--t-ink3` (5.9:1 on white); not re-measured with a tool |
| 13 | touch targets 44 px | 1 | CPU, aligned/as-compiled, word chips, bar buttons, widget segments 31 to 36 px | 2 | pseudo-element hit areas (no layout growth) for the hero, bar and Figure 1 buttons; real 44 px height for the word chips and the widget segments, selects and copy buttons (the main page with everything open grew about 1.5%, check cap 17,000 to 18,000). One open item: the first "Copy" button fails the audit at its top and bottom edge (50x44, covered by a neighbour), not found why |
| 14 | keyboard | 2 | roving rows, Esc | 2 | plus keys 1 to 8 pick a loop and C flips the check (hero), hint shown only with a mouse on wide screens |
| 15 | text alternative | 2 | row labels, live ratio | 2 | |
| 16 | hover info also on tap and focus | 1 | the dot tooltip (pooled ratio and 95% interval) was mouse only | 2 | the drawer's per-size line now prints "Pooled N x (95% interval a to b)", reachable by tap and keyboard |
| 17 | direct labels | 2 | range printed at each row's end, 1x tick labelled | 2 | |
| 18 | gist plus one figure | 2 | | 2 | |
| 19 | phone page length | 2 | 9,329 px, cap 10,500 | 2 | 9,469 px after the hit areas (collapsed default) |
| 20 | print shows the static state | 1 | the screen variant printed as drawn; V3 is white on dark | 2 | before print the hero switches to variant 2 (light, static) and back afterwards; verified with print emulation for V3 and V2; the keys hint is hidden in print |
| | total of 40 | 32 | | 40 | one known open item under 13 |

Also done from the list: the live side panel for Figure 1 on wide screens (hovering a row previews its machine code in the panel, with "Preview. Click the row to pin it."; a click pins; leaving the rows returns to the pinned one); five details that delight: keys 1 to 8 and C, a favicon that turns orange, blue or grey with the selected loop, a 160 ms cross-fade (never a count-up) when the ratio changes, "Copied" announced politely for 1.2 s, per-size pooled interval in the drawer. Fonts: the Google Fonts stylesheet no longer blocks first paint (print-media swap with a noscript fallback; `display=swap` was already set); a failed data fetch already prints a one-line error with the fix.

Not fitted, with the reason:
- On phones the machine-code panel appears below Figure 1 after a tap (scrolls to it, with a "Back to the eight loops" button), not directly under the tapped row: the rows are one listbox, and splitting it would break its keyboard model; a larger rewrite than this round allowed.
- A "last updated" line from the data: the data holds no per-run dates (only run ids), and stamping the build time would make `build_site_data.py --check` non-deterministic.
- Per-row mini graphs were already there (dots with intervals, per-job ticks, the 1x line and the A/A band).

Things that tire, audited: no replay on scroll (the hero run is gated by a one-shot clock), no count-up numbers, no drag controls, no looping gradient or video, one fixed section rail (dots) that only highlights. Nothing found to remove besides the progress bar.

## Review of the first view and hero variant 4

Findings of an independent first-view review, and the change made for each:

| Finding | Change |
|---|---|
| The page never shows "some loops tie, some lose 3 to 8x" in one glance; the animation was tiny beside a huge number | Hero variant 4, the default: all eight loops as lanes of two bars on one axis (above). |
| After picking Matrix multiply the caption still told the reverse-loop story and the strip did not change | Each loop has its own caption (`CAP` in `site/race.js`, wording from the compiler remarks and Figure 2's reading) and the strip has its own visiting order for the histogram (a few counters hit again and again) and matrix multiply (the same row of c walked once per k); the baked first-paint sentence comes from `scripts/build_site_data.py` (`heroWhat`). |
| The hero switcher pill overlapped text | The switcher lives in the sticky top bar (own row on a phone). |
| "di-rected" hyphen split in the byline | `hyphens: none` on the title block. |
| Word pills clipped at the right edge on a phone | They wrap (the widget chips too: the 12 px floor made them wider). |
| Dead space under the loop code in hero 2 | Hero 2 is no longer the first thing; its head and the Reproduce button now fill the left column (looked at, not measured). |
| Jargon pill row placed before any plain sentence | One plain sentence above "Words used here". |
| Abstract and Figure 1 caption were walls | Abstract: 58 visible words, the scope, the four findings and the closing paragraph behind "Scope, census, rewrites, other compilers"; Figure 1 caption: at most 60 visible words, the reading of the marks behind "How to read the marks"; the limits box runs under the abstract in two columns (no tall empty gap). |
| Section list narrower than, and centred under, the full-width figure | At 1041 px and wider the section column starts on the figures' left edge. |
| Three type voices, 11 to 13 px low-contrast captions | Two voices (serif, mono for code and numbers), no italic captions, a 12 px floor on every text (CSS floor in `site/hero.css`, widget sizes raised in `site/widgets/*.js`), `--ink-3` darker (#666), captions at `--ink-2`; `check_site.py` measures all of it. |
| No visible way to reproduce | "Reproduce in one command" button in the hero head: a small box with the check command, a Copy button and a link to section 10. |

Cost of the 12 px floor: the machine-code listings and a few widget labels are about 25 % larger, so the slide-over listing wraps more; it is still readable and every number is unchanged.

Decision: the default hero is variant 4 although the original 20 items rank variant 2 first (below). Reason: the design rule is that the finding must be clear in seconds, and the one-glance test is the thing none of the other three passes. To make variant 2 or 1 the default, change `DEFAULT_HV` in `site/race.js` and the static `data-hv` on `<html>` and `#race` in `site/index.html`.
Decision (one click opens the machine code): on a touch screen the first tap on a lane selects it and shows its sentence, the second opens the machine code, because a phone has no hover and an immediate panel would hide the caption. A mouse or keyboard click opens at once.

## SCORE ROUND 2 (four variants, the research checklist of DESIGN-RESEARCH.md section 6, 0 to 2, scored harshly from playwright shots and measurements)

Measured with a playwright script (1440x900 and 390x844) and `scripts/check_site.py`. Ratio size: V1 62 px desktop / 38 px phone, V2 154 / 74, V3 51 / 35, V4 59 / 38 (3.6rem = 57.6 px). Phone page length with everything collapsed: 9,142 / 9,140 / 9,196 / 9,551 px (cap 10,500). Print emulation: every variant switches to the light, drawn V2 poster (V4's bars are CSS backgrounds, which printers drop). Phone touch audit: no control under 44 px in any variant.

| # | Item | V1 | V2 | V3 | V4 | Evidence |
|---|---|---|---|---|---|---|
| 1 | first view holds the finding (ratio >= 3.6rem, switch, chips, scope, no scroll) | 1 | 2 | 1 | 1 | Only V2 meets the 57.6 px ratio on both sizes; V1 and V4 meet it on desktop only; V3 misses on both. V4 on a phone: all eight lanes with their ratios and the long bars are in the first view, the big readout is one short scroll down. |
| 2 | ratio on first paint and in HTML without JS | 2 | 2 | 2 | 2 | `heroRatio`, `heroCpu`, `heroJobs`, `heroWhat` baked in index.html; without JS the lanes are empty in every variant (the noscript line gives the range). |
| 3 | every control acts at once | 2 | 2 | 2 | 2 | check_site clicks every loop, CPU and switch and reads the printed ratio at once. |
| 4 | one ambient motion, no loop, none on scroll | 2 | 2 | 2 | 2 | after Replay `document.getAnimations()` is empty (V4) / the canvas is identical after 2.6 s (V1 to V3). |
| 5 | reduced motion shows the final frame | 2 | 2 | 2 | 2 | check_site with `reduced_motion="reduce"` for each variant. |
| 6 | transitions match the table | 2 | 2 | 2 | 2 | V4: 120 ms hover, 200 ms bar clip (the table's "lane bar width"), clip-path is paint-only. |
| 7 | shadows use the elevation tokens | 2 | 2 | 1 | 2 | V3 adds ad hoc `0 6px 14px` and `0 6px 16px` shadows on the graphite stage. |
| 8 | nothing scroll-driven, sliding, draggable | 2 | 2 | 2 | 2 | no scroll or range handlers in the hero code. |
| 9 | every number traces to data | 2 | 2 | 2 | 2 | check_site number walk; the V4 axis ticks (1x, 2x, 4x, 8x) are the scale. |
| 10 | caveat within one screen | 2 | 2 | 2 | 2 | the scope sentence is in the first view in all four (check_site). |
| 11 | one colour, one meaning | 2 | 2 | 1 | 2 | V3 re-tints orange and blue for the dark stage and uses white for the selection. V4: orange loses SIMD, blue keeps it, graphite no SIMD to lose, yellow the check, slate the unchecked bar. |
| 12 | contrast 4.5:1 and text size | 2 | 2 | 1 | 2 | check_site computes caption and label contrast; V3's gauge tick labels are 9 px SVG text. |
| 13 | 44 px touch targets on a phone | 2 | 2 | 2 | 2 | audit in check_site (hit areas by pseudo-element); V4 lanes are 54 px. |
| 14 | keyboard | 2 | 2 | 2 | 2 | roving radios, arrows, 1 to 8, C, Enter or Space opens the code, Esc closes the box and the panel. |
| 15 | text alternative | 2 | 2 | 2 | 2 | aria-labels with the ratio on every lane or tile; V4's caption region is silenced while a pointer previews another loop, so only a real selection is announced. |
| 16 | hover info also on tap and focus | 2 | 2 | 2 | 2 | V4: focus previews like hover; on touch the first tap shows the sentence. |
| 17 | direct labels, no legend | 2 | 2 | 2 | 1 | V4 labels the bars directly on wide screens, but a four-swatch key replaces that on a phone (the bars are 6 px there). |
| 18 | gist plus one figure | 2 | 2 | 2 | 2 | the hero is one figure with one sentence. |
| 19 | phone page length | 2 | 2 | 2 | 2 | measured above. |
| 20 | print shows the static state | 2 | 2 | 2 | 2 | print emulation: all four become the V2 poster with the measured number. |
| | total of 40 | 39 | 40 | 36 | 38 | |
| 21 | Added after the first-view review (not in the research checklist): the contrast between loops that cost nothing and loops that cost 3 to 8x is visible in one image with no click | 0 | 0 | 0 | 2 | V1 to V3 show one loop at a time; V4 shows all eight. |
| | total of 42 | 39 | 40 | 36 | 40 | |

Reading: on the original 20 items variant 2 leads variant 4 by two points, entirely from items 1 and 17; with the added item 21 (disclosed: it was added after the review named the gap, so it is a judgement, not a neutral test) they tie at 40 and V4 is the default, with the decision above. Items still open on V4: the phone first view (item 1) and the phone legend (item 17). The scores are the project's own, not an independent judgement.

## The modules under the hero

A second independent review found: the hero is distinctive and lands in about 10 s, but below it the page turns back into a preprint, there is no hands-on mechanism, no single big contrast statement, and a list of small flaws. What was done (code: `site/story.js`, `site/modules.css`):

| Finding | Change |
|---|---|
| No single big contrast | The contrast band under the hero: Google's reported average (0.30%) beside this study's worst loop at the selected CPU (8.0x on EPYC 7763; follows the chip), "one loop, same check", and the neutral sentence (this neither confirms nor contradicts Google's average). The default is baked into the HTML by `build_site_data.py` (`bandWorst`, `bandName`). |
| No hands-on mechanism, SIMD never glossed | "Why does the check slow it down?": eight array cells, the glyph tiles as loop chooser, Check off / Check on and Step (no dragging, no timers). Off: one Step lights four cells ("one instruction"). On: one cell per Step past a yellow gate, with the data's own reason (HeroRace.words); forward loops: the sizes are tested once up front and four at a time stay. The access orders for gather, histogram and matrix multiply are illustrations; the note says the mechanism is inferred and steps are not time. A "What is SIMD?" chip in the hero says it in one line. |
| Below the hero it is a preprint | Sections are modules (white card, e1 elevation, the same tray and chip language): a small section label, a bold one-line takeaway in large type, the figure if it has one, "Details" behind a button. Census chart, compiler grid and real-programs widget are behind Details (a one-line verdict is what shows). The placement module shows its sentence and the four taps only; the ruler and controls are one click away. The rewrite module shows only the before/after toggle. Abstract, "What this cannot tell you" and the word chips are folds; "Limits" is a link in the top bar that opens the box. |
| Small flaws | In-bar labels 13 px on a white chip, all on one left edge, clear of bars and the 1x line; ratios stay legible with the check off; "Replay the race"; a one-time "flip the check" hint after the first run (ends on the first use of the switch or after 9 s); the caption says the axis rescales to the longest bar of each CPU model; the section dots are darker with their label on hover; every link, chip and button has a 44 px hit area on a phone (pseudo-element, checked by script); Figure 1 on a phone is an accordion: the machine code opens directly under the tapped row (rows become buttons with aria-expanded, a second tap folds it, arrows still move between rows; on wide screens it stays a listbox with the panel beside it). |

Decision (sections collapsed to a gist plus one figure): the figure of the census, compiler and real-programs sections is no longer shown by default; the takeaway sentence is. Reason: the review named these three as the places the page reads as a paper. One click on Details shows the figure (mounted on first open).
Check changes (disclosed): Figure 1 is now "within three screens" instead of 1.7 (the band and the demo come first); the all-sections-open phone cap is 19,500 px (was 18,000; the cards add padding); the abstract and limits checks read the folds open; the phone Figure 2 checks now test the accordion.
Phone default height after this round: about 6,400 px (was 9,551; cap 10,500).
Not fitted: the mechanism demo has no animation of its own (by design); the hero's V1 to V3 variants do not get the SIMD chip on a phone.

- Cap change (Oct 14, after a failing check): the phone all-sections-open cap rises 19,500 to 20,000 px because the new section "How can 0.30% be true?" adds about 250 px; the default collapsed-page cap (10,500) is unchanged.
