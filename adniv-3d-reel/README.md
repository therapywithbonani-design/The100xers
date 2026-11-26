# Adniv "Peeli Light Kahan Gayi?" 3D reel

Status: full reel rendered and QA passed (B + C hybrid). See `final/`.

- `review/index.html` - review page (reference analysis, word timings, beat sheet, style frames, flip clips, safe-zone proof)
- `assets/words.json` - 127 voiceover words with start/end times (aligned to vo.mp3)
- `src/` - Three.js scenes (`engine.js`), DOM typography/captions/CTA (`hud.js`), shot programs (`shots.js`), headless renderer (`render.js`), word alignment (`words.py`, `align.py`), clip audio + mux (`mkclip.py`, `mux_flip.sh`)

Render: `npm i three@0.160.0 playwright`, serve the `three/` folder (`node serve.js`), then `node render.js <A|B|C> <shot> <t0> <t1> 30 <outDir>`. WebGL runs on software GL (about 1 s per 1080x1920 frame).
Inputs (reference.mov, vo.mp3, music.mp3) are not committed.
