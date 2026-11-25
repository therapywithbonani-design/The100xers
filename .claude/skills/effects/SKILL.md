---
name: effects
description: Quick command for the agency reel kit. Use when the user types /effects followed by style keywords (e.g. "/effects luxe", "/effects podcast text:giant fx:zoomcut", "/effects niche:jewellery", "/effects list"), or asks to apply a named style/effect/text/look/scene to a reel. Routes each keyword to the right saved skill and starts the edit or plan.
---

# /effects — quick command

Usage: `/effects <style> [text:<name>] [fx:<name>] [look:<name>] [scene:<name> style:<engine-style>] [niche:<niche>]`
- `/effects list` → print the keyword table below (short) + the guide book link: https://claude.ai/artifact/GC3aWAoCxqer5rZmN6j3no
- No style given but a niche → use the niche default.
- Keywords are case-insensitive; `-` and spaces are ignored (`glass-widgets` = `glass`).

## Routing
1. Read the args. Map each to a skill using the table; load that skill (Skill tool) and follow it.
2. If brand details are missing (audience, offer + price, platform, CTA), ask once, briefly, before editing.
3. Footage attached → edit/render. No footage → deliver a shot-by-shot edit plan in that style.
4. Always end with CTA + KPI.

| Keyword(s) | Skill to load |
|---|---|
| `pinteresty` | pinteresty-style |
| `lookbook` | editorial-lookbook |
| `darksplit` | dark-split-explainer |
| `countdown` | starfield-countdown |
| `podcast` | podcast-premium-edit (part A) |
| `noedit`, `beforeafter` | podcast-premium-edit (part B) |
| `luxe` | luxe-editorial-motion |
| `grid4` | luxe-editorial-motion (2×2 showcase) |
| `fxlist` | video-effects-kit (showcase format) |
| `slashdemo` | slash-demo-reel |
| `checklist`, `documentary`, `glass`/`glasswidgets`, `orbit`, `pixelreveal`, `splitchart`/`kallawaysplit`, `spotlight`, `timeline`, `travlink` | built-in: reel-checklist, reel-documentary, reel-glass-widgets, reel-orbit, reel-pixel-reveal, reel-split-chart, reel-spotlight, reel-timeline-ui, travlink-reference-edit |
| `text:<name>` (glass, behindhead, smoke, wallink, arc, bounce, neon, giant, explode, typer, outline, stack, counter, notes, follow, commentcta) | caption-animation-kit |
| `fx:<name>` (orbit, couchwall, uiworld, framebreak, digitalzoom, phone, checklist, headlinewall, zoomcut, chart, pullback, greenscreen, papercut, doodle, vertigo, cover, glasstype, lineup, shortcutrain, redcollage, commentbox, rabbithole, profilewall, noise, phonefan, bill, splitheadline, pastelword, tierlist, autoedit) | video-effects-kit |
| `look:<name>` (cyberpunk, paper, hologram, popart, thermal, anime, sunset, ukiyoe, claymation, swap) | animation-style-kit |
| `scene:<name>` + `style:<18 engine styles>` | animated-scene-engine |
| `prompts:pack1|pack2` | animation-style-kit |
| `niche:<clothing|jewellery|food|sports|talking|interview|sitevisit|gaming|info|travel|agency>` | reel-editing-kit (table D) |

Unknown keyword → show the 3 closest matches and ask.
