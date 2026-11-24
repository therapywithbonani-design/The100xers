# Myth Busting - style spec (from the shipped episode)

Canvas 1080x1920, 30 fps, H.264 crf 22 (~17 MB for 39 s), AAC 44.1 kHz. No retiming: output frame i = source frame i.

## Palette
green (18,138,92) pills/icons; dark green panel (14,78,56)->(8,44,32) with faint dot grid; gold (242,182,50) divider/highlights;
red (226,58,64) crosses/tags; ink (16,38,29) text on white cards; white captions. Covers use the same greens + gold + red.

## Fonts (assets/fonts): Inter 600/700/800/900 (SIL OFL). Captions 700, stickers/panels 800-900.
Note: Inter latin subset has no "not-equal" glyph - reword instead of using symbols.

## Captions (`mythlib.make_caption` / `draw_caption`)
- 62 px Inter Bold, sentence case, max width 940, two balanced lines, line height 94, layer top y = 1330.
- Keyword markup `*word*`; consecutive keywords merge into one green rounded pill (radius 22, padding 18 px).
- Fade-in 0.16 s with 20 px rise, fade-out 0.14 s; shadow alpha 0.55 (blur 9).
- Scrim: black gradient from y = 1120 to the bottom, alpha 0 -> 0.40 (power 1.4) - needed for white text on a white desk.
- Phrase timing straight from word timestamps (start = first word start, end = last word end).

## Grade (`mythlib.grade`)
vibrance 1.05 + 0.20 x (1 - saturation/0.45); shadows +0.012; contrast x1.045 around 0.47; roll off values above 0.80 by 45 %;
R x1.012, B x0.99; vignette 7 %. Goal: richer but "not too bright, not too high contrast".

## Stickers (`mythlib.sticker`)
White rounded card (radius 40), icon circle (check green, x red, person/cap/brief green, ? gold, plus green, star gold),
Inter 800 54 px ink text, optional 2nd line (36 px grey, or 54 px green bold for the myth card), optional red tag (MYTH).
Centre x 540, y ~300 (+10 if tag, +25 if two-line myth card). Pop 0.34 s (back-ease 1.8), out 0.16 s. Hidden during split screens.

## Interviewer question card (`mythbuild.make_qcard`)
White card 960 px wide at y 1290, mic icon in a green circle + "QUESTION" (Inter 900 30 px, letter-spaced), text Inter 800 56 px
in two balanced lines; each word fades in at its spoken start time (`QWORDS`), key words on a light-green pill (206,238,221) with
green text; card pops in at 0.20 s (back-ease) and fades out ~0.2 s after the question ends. Replaces captions for the question.

## Split screens (`mythpanels.py`)
- Panel 1080x820, animates height 0 -> 820 over 0.42 s (smooth), content slides in from the top; video region
  `Hv = 1920 - PH`, crop start row `r0 = int(460 * p)` so the speaker stays framed (face ~ 300 px below the divider).
  Gold divider line (6 px) + soft shadow under it. Out over 0.40 s.
- Panels used: A) "WHAT UNIVERSITIES LOOK AT" - rows (briefcase "Very good internship", cap "Bachelor's degree", star "= Strong profile")
  slide in and get ticks; B) "MARKS ALONE DON'T GUARANTEE A SEAT" - two white cards, big counting % (75 / 92), progress bars,
  chips "Good university" (green, tick) and "Not admitted" (red, x); C) "WHAT THEY ALL LOOK AT" - two shield badges
  (IVY LEAGUE / RUSSELL GROUP), green "PROFILE" pill with tick, struck-through "academics only".
- Each panel is timed to the words (rows appear as the item is named; chips appear on the word "good"/"not").
- `PANELS = {'A': (start, end, fn), ...}` in source seconds; keep total split time <= ~14 s of a 39 s clip.

## Voice enhancement (before effects)
```
ffmpeg -i clip.mp4 -vn -af "highpass=f=85,afftdn=nr=14:nf=-38:tn=1,equalizer=f=220:t=q:w=1.0:g=-2.5,\
equalizer=f=3200:t=q:w=1.1:g=3.2,equalizer=f=7500:t=h:w=0.7:g=1.5,\
acompressor=threshold=0.07:ratio=3:attack=12:release=160:makeup=3,\
dynaudnorm=f=250:g=11:p=0.92:m=8,alimiter=limit=0.9" -ar 44100 -ac 2 voice_enh.wav
```
Measured: off-camera question -29.9 dB vs answer -18.5 dB RMS -> after: -17.4 vs -17.5. The chain adds ~30 ms delay:
drop the first 0.030 s of the filtered voice (`mythaudio.py` does this) and re-verify sync.
Effects (`sfx2_synth.py` functions): whoosh at split in/out, pop per sticker, 2-note tick per tick/check, low buzz on x; gains 0.26-0.32,
ducked 50 % under the voice. Final: `loudnorm I=-15 TP=-1.5` + `aresample=44100`.

## Cover (`mythcover.py`)
- Background: Voronoi "shattered glass" (about 57 seeds in rings around an impact point at 46 % height), cell tone jitter,
  light green crack lines fading outward, impact glow, vignette. Green family, clearly different from the sunburst.
- Person: RMBG mask limited to the upper body (rows above 70 %), largest component, white outline (31 px), width 1090, bottom flush.
- Title (tilted +3 deg, 3D extrude): "MYTH" Inter 900 288 px white; "BUSTING" Inter 900 170 px gold, letter-spaced.
- Question card (tilted -3 deg, white, radius 52, 890x300) with red "MYTH" tag; line 1 "High CGPA =" 92 px ink; line 2
  "Guaranteed" on a gold marker + "admission?" in green, 64 px. Two lines so nothing leaves the frame.
- "BUSTED" stamp (red double border, white 92 % fill, rotated 8 deg, 430x140) beside the head, not on the card text or face.
- Cover frame: eyes open, mouth closed, looking at camera, upper-body only (table/laptop masked out).

## Adaptation points
`mythlib.py`: `SRC`. `mythbuild.py`: `CAPS`, `STK`, `QWORDS`, `Q_IN/Q_OUT`, `CAP_TOP`, output path. `mythpanels.py`: `PANELS` times
and the panel functions (new topics need new panel designs: keep the same card/pill/bar vocabulary). `mythaudio.py`: sticker and tick
times (must mirror STK and PANELS) and the enhanced-voice path. `mythcover.py`: frame/mask paths, texts.
