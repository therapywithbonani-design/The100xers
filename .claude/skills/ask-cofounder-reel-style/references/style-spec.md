# Ask The Co-Founder - style spec (numbers taken from the shipped episodes 1-4)

Canvas 1080x1920, 30 fps, H.264 yuv420p, AAC 44.1 kHz stereo. All coordinates below are for that canvas.

## Palette
| use | RGB |
|---|---|
| sunburst light / dark rays | (18,96,60) / (7,56,36) (darkened x0.85 on the question card) |
| caption highlight | yellow (255,210,31); negative words red (255,84,84) |
| badge fill / border | navy (22,36,84) / yellow |
| 3D title extrude | purple (94,40,140) outer half, red (230,57,70) inner half, dark outline (40,16,70) |
| series-tag bar | red (228,36,52) |
| tick / cross | green (36,190,96) / red (235,40,48) |

## Fonts (assets/fonts)
Montserrat 700 / 800 / 900 (SIL OFL). Captions 800; title 900; tag 800 + 700.

## Segment order (output)
`live(0 -> FRZ)` -> `title 3.0 s` -> `question 3.4 s` -> `live(RES -> ...cuts...)` -> `outro 2.8 s`

## Cold open
- Footage is grayscale until `BWEND` (1.0-2.3 s), then colour returns over 0.35 s.
- Series tag top-left at (60,70): red bar 9 px wide, "Ask The Co-Founder" Montserrat 800 56 px white, "EPISODE N" 700 34 px
  below; shadow; top scrim (380 px, alpha 0.55 -> 0). Reveals left-to-right 0.25 -> 0.8 s.
- Zoom 1.00 -> 1.04 slow push.
- If the clip starts with > 0.5 s silence trim the start (`START`) and anchor the tag animation to output time.

## Freeze title card (3.0 s)
- Background: 28-ray sunburst, rotating 5 deg/s, centred at y = 0.42 H, light radial highlight.
- Person: cut-out of the freeze frame, 1040 px wide, white outline (37 px dilation) + soft shadow, bottom flush to
  the frame bottom, slides up from +820 px with back-ease (0.55 s), tiny zoom 1.00 -> 1.02.
- Titles (Montserrat Black, white, 3D extrude): "ASK THE" 112 px at y 430, "CO-FOUNDER" 112 px at y 560,
  "EPISODE N" 150 px at y 760. Pop-in delays 0.10 / 0.20 / 0.34 s, back-ease overshoot 2.2.
- White flash in over 0.22 s, flash out over the last 0.12 s. Sound: impact + whoosh + stamp per word.

## Question card (3.4 s)
- Sunburst x0.85 brightness. Yellow pill "QUESTION FROM A STUDENT" (Montserrat 900 44 px, navy) at y 700.
- White rounded bubble (x 90, y 950, 900 wide, height from line count): typing dots 0 -> 0.55 s, then characters type
  over ~1.9 s (Montserrat 800 64 px, navy; highlight words green (14,110,70)). Avatar + "A student asked" under it.
- Sound: whoosh in, pop, "message" ding, typing ticks (one per ~52 ms), whoosh out.

## Captions
- Montserrat 800, 84 px (keywords 100 px yellow). 1-2 lines, 2-4 words per phrase, text centred, layer top y = 1170.
- Soft drop shadow (blur 13 + blur 2.5, offset down). Auto-shrink if a line is wider than ~980 px.
- Smoke reveal: in over 0.30 s (blur + rise 30 px + noise-mask dissolve with a grey smoke puff), out over 0.20 s
  (dissolve + rise 45 px). Phrases follow word timestamps; show next phrase exactly when the word starts.
- Markup used in code: `*word*` yellow, `!word!` red, `|` forced line break.
  Punctuation after a marked word is kept inside the highlight.

## Cuts, zoom, grade
- Remove pauses >= 0.5 s (trim ~0.8-1.2 s per episode in total) at silent windows; change zoom block at every cut so
  the jump looks intentional. Typical blocks: 1.00-1.05, 1.10-1.15, 1.12-1.18 (centre x, anchor y = 900).
- Grade: contrast x1.05, saturation x1.08, vignette -16 %.

## Stickers
- Pop 0.40 s with back-ease (overshoot), leave 0.20 s scale-down; white 12 px outline + soft shadow; slight rotation
  (-6..+5 deg) and gentle bob; centre (540, ~335-345) (above the head), side-by-side flags at x 290 / 790 or
  215 / 540 / 865 (small, 300x200) for lists.
- Tick/cross: small circle (170 px) at (690,255) or beside flags: green tick = recommended, red x = not allowed/no.
- Kinds drawn in code (`build3.py`): flags (IT DE IN UK EU SG HK FR SE), navy badges with icon + 1-2 text lines
  (scales, graduation cap, coin, bars/chart, calendar, speech bubble, medical cross, star), white logo card.
- Only stick what is said. Use generic badges for universities/brands unless the user supplies the logo.

## Outro (2.8 s)
- Last live frame, grayscale x0.62, zoom 1.18 -> 1.23. "TO BE|CONTINUED..." Montserrat 800 104 px with smoke reveal
  at y 1000; yellow pill "FOLLOW FOR EPISODE N+1" (Montserrat 900 46 px, navy, white outline) at y ~1400-1700,
  pulsing 3 %. Sound: riser into impact, drone, pop + rising chime on the pill.

## Sound design (all synthesised in `sfx4.py`, royalty free)
cold open: typewriter ticks for the tag + rising sweep -> freeze: impact, shimmer, stamp per title word, sparkle ->
return: reversed whoosh + flash -> zoom cuts: quiet swish -> stickers: pop (+ sparkle/chime); x: low error buzz;
tick: 2-3 note rising ding; badges: stamp thump -> outro: riser, impact, drone, pop, chime.
Effects are ducked under the voice (side-chain from the voice envelope); big hits sit in the silent cards.
Loudness: loudnorm I=-15 TP=-1.5, then `aresample=44100`.

## Covers (1080x1920 PNG)
- Plain: sunburst, 3-line 3D title (EPISODE N), person cut-out scale 1.30.
- Hook: person scale 1.415 (raised ~95 px, bottom still flush), title shifted up 55 px, white-outlined yellow pill with a
  short question (e.g. "MBBS IN GERMANY?") at y 1370 so it lies on the chest and the face stays clear.
- Cover frame: eyes open, mouth closed, looking at camera, not speaking.

## Adaptation points in `scripts/reference/build3.py` (everything else stays)
1. `SRC`, `OUT`, `SERIES1/2`, `EPNUM`, `TAG1/2`, output filename and audio mix filename.
2. The one-line segment config: `START/FRZ/RES/CUT_A..CUT_D/BWEND/END` (source seconds) and `segments()`.
3. `QTEXT` / `QHI` (question text + highlighted words).
4. `ZOOMS` list, `PHRASES` list (text markup, start, end), `POPS` list (sticker key, start, end, centre, angle).
5. Sticker constructors (`new_stickers*`, `flag2`, `badge`) if new keywords need new artwork.
6. Cut-out path in `main()` (`prep_cut('...')`) and outro text.
`sfx4.py` imports `build3` as `B` and rebuilds the audio timeline: update its event list to the same sticker/cut times
(use `o(source_time)` to convert source time -> output time) and its audio output filename.
`cover3.py`: change the module name, cut-out path and hook text.
