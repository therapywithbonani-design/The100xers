# Adniv × CRUSH Salon — project reel

Status: steps 1–4 done (inspection, shot list, grade, 3 styles, 3 covers). Client logo applied. Waiting on style + cover pick and IMG_4893.

- `review/index.html` – review page (contact sheets, shot list, grade before/after, style samples, covers, safe-zone + grid checks)
- `src/grade.py` – per-clip colour correction + shared grade (WB from neutrals, linear exposure, bounded highlight roll-off, shadow lift)
- `src/overlay.py` – text/chip/logo/glass/depth engine, Reels safe-area constants, safe-zone overlay
- `src/styles.py` – the three directions (A Gallery Label, B Glass Spec Card, C Light-On Kinetic)
- `src/covers.py` – cover options + 4:5 / 3:4 grid checks
- `src/analyze.py`, `src/jitter.py` – exposure/cast/clipping and shake measurement

Raw clips are not committed (client footage, ~180 MB). Logo: `assets/adniv_logo_reversed.png` (white wordmark, brand blue + orange kept) on footage; `assets/adniv_logo_original.png` on light backgrounds.
