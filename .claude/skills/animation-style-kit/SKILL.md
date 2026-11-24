---
name: animation-style-kit
description: Library of 10 visual animation/illustration looks (Cyberpunk Neon, Paper Cutout, Hologram, Isometric, Pop Art, Thermal Cam, Anime Cel, Sunset Silhouette, Ukiyo-e, Claymation) to apply to reels — as full-reel looks, b-roll treatments, hook/style-swap transitions or AI-generated cutaways. Includes a ready ffmpeg filter script (looks.sh) to apply 9 of them to real footage, AI generation prompts for all 10, and which look suits which niche. Use when the user asks for a stylised/animated look, cartoon/anime/neon/thermal/pop-art effect, style-switch transition, or "animation styles" in any reel.
---

# Animation Style Kit — 10 Looks

Picked from a "10 animation styles" countdown reel (same scene of a man walking a dog in 10 styles).
Two ways to use every look:
- **A. Filter on real footage** → `looks.sh` (fast, works on talking heads, b-roll, product shots). An approximation of the style.
- **B. AI-generated** → `prompts.md` (true illustrated look; generate image/video, or restyle a frame/clip with image-to-image / video-to-video).

```bash
# apply to a clip or a still (png/jpg output = single frame)
.claude/skills/animation-style-kit/looks.sh <style> input.mp4 output.mp4
# styles: cyberpunk paper hologram popart thermal anime sunset ukiyoe claymation
```

---

## The 10 looks

| # | Look | Visual signature | Palette | Filter (A) | Best niches / use |
|---|---|---|---|---|---|
| 1 | **Cyberpunk Neon** | Night city, magenta/violet neon glow, neon signage, wet reflective ground, scanlines | #1A0B2E bg · #FF3CAC magenta · #7B5CFF violet · #2EE6FF cyan | ✅ `cyberpunk` (grade + glow + scanlines) | Gaming, nightlife, cafés at night, tech launches, sports hype |
| 2 | **Paper Cutout** | Layered paper shapes, soft shadows between layers, paper grain, stop-motion | beige #EADBC0 · leaf green #7DAA4F · brick red #C8473A | ✅ `paper` (posterise + soft edges + grain) | Kids/edu, food recipes, D2C storytelling, explainers |
| 3 | **Hologram** | Cyan wireframe lines, translucent figure, scanlines, flicker, HUD labels | navy #04121F · cyan #3FD8FF · white | ✅ `hologram` (edge lines + glow + scanlines + flicker) | Tech/SaaS, AI, futuristic product reveal, real-estate "plans" |
| 4 | **Isometric** | 3/4 top-down diorama, pastel tiles, low-poly props, floating UI tags | mint #BFE8C8 · sand #F1D9B5 · coral accents | ❌ AI only (needs re-drawing the scene) | Site visits/real estate, process explainers, apps, maps |
| 5 | **Pop Art** | Comic halftone dots, thick black outlines, flat primaries, "WOOF!" bursts, caption box | yellow #FFD400 · red #E23B2E · blue #2F7BE5 · black | ✅ `popart` (posterise + halftone + ink lines) | Sales/discount reels, food, fashion drops, fun brands |
| 6 | **Thermal Cam** | Heat-map figures (orange/yellow/white) on cold purple, scale bar, crosshair HUD | inferno map: #120A3C → #B5367A → #FCA50A → #FCFFA4 | ✅ `thermal` (inferno map + HUD bar) | Sports/fitness ("burn"), spicy food, gaming, "hot drop" sales |
| 7 | **Anime Cel** | Flat cel shading, crisp ink lines, bright sky, Ghibli daylight | sky #6EC6FF · grass #5DBB4A · skin warm flats | ✅ `anime` (smooth + posterise + ink lines) | Travel, fashion, cafés, lifestyle creators, Gen-Z brands |
| 8 | **Sunset Silhouette** | Pure black shapes on orange→purple gradient sky, big sun | #2B1650 → #FF8A3D | ⚠️ `sunset` (works best on **backlit** shots or with a person cutout) | Travel, emotional brand stories, endings/outros, jewellery glints |
| 9 | **Ukiyo-e** | Japanese woodblock: washi texture, muted indigo/ochre, Fuji, red sun, calligraphy cartouche + red seal | indigo #2D3E66 · ochre #C9A15B · paper #EFE3C8 · seal red #C0392B | ✅ `ukiyoe` (muted posterise + ink + paper grain + cartouche) | Ethnicwear, tea/Asian food, artisanal & heritage brands |
| 10 | **Claymation** | Plasticine texture, fingerprints, warm studio light, blurred bg, 12fps stop-motion | warm saturated pastels | ⚠️ `claymation` (12fps + smoothing — feel only; true clay texture needs AI) | Kids, food, D2C fun, explainer intros, mascots |

Filter quality notes (tested on a talking-head frame): strong = Pop Art, Hologram, Thermal, Anime, Paper, Cyberpunk; medium = Ukiyo-e, Claymation; Sunset needs a backlit shot or a cutout.

---

## How to use them in reels

1. **Style-swap hook (first 2–3s):** same shot flips through 3–5 looks on the beat (0.3–0.5s each) → "which one is you?" Instantly stops the scroll.
2. **Style-swap transition:** between two scenes, flash 2–3 looks for 2–4 frames each instead of a whoosh.
3. **Section looks:** give each part of a reel its own look — e.g. *Thermal* for the "problem / burn" part, *Anime* for the dream outcome.
4. **B-roll treatment:** keep the talking head natural; stylise only the b-roll cutaways (Hologram for product tech, Pop Art for price drops).
5. **Countdown showcase:** "10 looks of one product/outfit" in the `starfield-countdown` layout.
6. **Outro:** Sunset Silhouette or Ukiyo-e freeze-frame behind the CTA.

Pair with text: Cyberpunk/Hologram → Neon Sign or Retro Typer; Pop Art → Explosive Breakup / Kinetic Bounce; Anime/Paper → Kinetic Bounce; Ukiyo-e/Sunset → Hierarchy Stack (see `caption-animation-kit`).

## Niche picks
| Niche | Looks |
|---|---|
| Clothing | Anime Cel, Pop Art (drops), Ukiyo-e (ethnicwear) |
| Jewellery | Sunset Silhouette, Ukiyo-e, Cyberpunk (festive/night) |
| Food / café | Pop Art, Paper Cutout, Claymation, Thermal (spicy) |
| Sports | Thermal Cam, Cyberpunk, Pop Art |
| Talking reel | Style-swap hook + Anime/Pop Art b-roll |
| Interviews | Sunset outro, Hologram for stats |
| Site visits | Isometric (AI), Hologram (plans) |
| Gaming | Cyberpunk, Hologram, Thermal, Pop Art |
| Informational | Paper Cutout, Isometric, Hologram |
| Travel | Anime Cel, Ukiyo-e, Sunset Silhouette |

## Conversion layer
- Style-swap hooks drive rewatches and shares ("tag someone who's the Pop Art one").
- Offer the looks as a lead magnet: "Comment LOOKS and I'll send you the prompts / presets".
- KPIs: 3s hold rate, replays/avg watch %, shares per 1k reach, keyword comments → DM leads (CPL).
