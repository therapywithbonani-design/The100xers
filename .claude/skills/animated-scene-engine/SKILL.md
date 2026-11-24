---
name: animated-scene-engine
description: Recreate any simple scene as a looping 2D vector animation (side-scroller: characters walk in place while parallax props scroll past) and render it in any of 10 animation styles — Cyberpunk Neon, Paper Cutout, Hologram, Isometric, Pop Art, Thermal Cam, Anime Cel, Sunset Silhouette, Ukiyo-e, Claymation. Code-built (canvas + Playwright + ffmpeg), so scenes are reusable and restyleable in one line. Use when the user wants animated scenes/cutaways/explainers in reels, a "same scene in N styles" showcase, illustrated b-roll for a brand, or to recreate a scene in one of these animation styles.
---

# Animated Scene Engine

## How the reference animation is built (what we copied)
- **2D flat-vector side-scroller.** Characters stay near centre doing a **walk cycle**; the **world scrolls right→left** in layers (far skyline/hills slow, mid props normal, near bushes faster) → parallax depth from flat shapes.
- **One scene graph, many skins.** Every style uses the *same* shapes (tree = trunk + 3 circles, lamp post, bench, bush, skyline, person, dog, leash); only palette, line, texture, lighting and overlays change. That's why the 10 styles read as "the same moment".
- **Seamless loop:** props wrap around, so any length loops cleanly (ideal for the 1.3s cards in `starfield-countdown`).
- **Style signatures in code:** neon glow + wet-floor reflection + scanlines (Cyberpunk); offset paper shadows + grain (Paper); wireframe + grid + HUD labels + flicker (Hologram); tilted world + tiles + UI pill (Isometric); thick outlines + halftone + sunburst + speech burst + caption box (Pop Art); heat-gradient bodies + cold world + temp bar + target boxes (Thermal); cel shading + outlines + clouds (Anime); black shapes on gradient + giant sun (Sunset); Fuji + red sun + paper texture + calligraphy cartouche (Ukiyo-e); soft 3D shading + blurred background (depth of field) + 12fps stepping + vignette (Claymation).

## Files
- `engine.html` — renderer: props, characters (person with walk cycle; carry `leash|cup|bags`; dog with gait + tail wag), far layers, 10 style skins, overlays.
- `scenes.js` — scene library (`dogwalk`, `shopping`, `cafe`). Add scenes here.
- `render.js` — renders a plan to MP4 (or stills).
- Sample: `samples/animated-scenes-sample.mp4` (dog walk ×10 styles, shopping ×3, café ×3).

## Render
```bash
cd .claude/skills/animated-scene-engine
node render.js out.mp4 '[{"scene":"cafe","style":"anime","dur":3},{"scene":"cafe","style":"popart","dur":3}]'
# options per item: scene, style, dur (s), t0 (start time), label (true = style name pill)
# stills:  node render.js prefix '[{"scene":"dogwalk","style":"ukiyoe","t":0.5}]' stills
```
Styles: `cyberpunk paper hologram isometric popart thermal anime sunset ukiyoe claymation`

## Making a new scene (describe it → I add it to scenes.js)
```js
gym:{label:'Gym run', speed:180, burst:'BURN!', caption:'DAY 1...', kanji:'運動', tag:'5 km · 320 kcal',
  props:[{type:'store',x:150,label:'FITCLUB'},{type:'lamp',x:420},{type:'tree',x:700},{type:'bush',x:500,layer:'near'}],
  chars:[{type:'person',x:340}]}
```
- Props available: `tree, lamp, bench, bush, store(label), cafe(label), table, sign(label)`; `layer:'near'` = foreground parallax.
- Characters: `person` (`carry: leash|cup|bags`, `leash:true` links to dog), `dog`.
- Per-scene text hooks used by styles: `burst` (Pop Art word), `caption` (Pop Art box), `kanji` (Ukiyo-e cartouche), `tag` (Isometric pill).
- New props/characters (car, product bottle, phone, building, mascot…) = add a draw function in `P` (engine.html) once; it then works in all 10 styles automatically.

## Using it in reels
| Use | How |
|---|---|
| **Explainer cutaways** in talking-head reels | 2–3s animated scene per point (e.g. "your customer walks past 10 shops" → shopping scene) in one consistent style per brand |
| **Style showcase / countdown** | same scene ×10 styles at 1.3s in `starfield-countdown` layout (lead magnet: "Comment STYLES") |
| **Brand mascot loops** | brand colours as a custom skin (copy a style in `STY`, change hex) |
| **Animated backgrounds** | loop behind text/CTA (Hierarchy Stack, Neon Sign from `caption-animation-kit`) |
| **Top panel of Dark Split Explainer** | scene plays in the top card while the speaker talks below |

Niche starters: clothing → `shopping` (Anime/Pop Art); café/food → `cafe` (Claymation/Paper); jewellery → `shopping` w/ store label (Sunset/Ukiyo-e); sports → new `gym/run` scene (Thermal/Cyberpunk); travel → new street/landmark scene (Anime/Ukiyo-e); real estate → building scene (Isometric/Hologram); gaming → Cyberpunk/Hologram.

## Limits (be upfront with clients)
- Characters are simple flat-vector figures (faceless-friendly, like the reference) — not detailed illustration or lip-sync.
- Brand-specific detailed art (exact products, real people likeness) → generate with AI using `animation-style-kit/prompts.md`, or supply SVG assets to add as props.
- Rendering: ~1 min per 30s of video in this environment.

## Conversion layer
- Use scenes to *show the customer journey* (walks past → enters store → leaves with bags) — benefit-led storytelling without a shoot.
- End every scene sequence on an offer frame (product + price + CTA text) — KPIs: 3s hold, avg watch %, saves/shares, link CTR or keyword comments → CPL.
