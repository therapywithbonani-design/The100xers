---
name: reel-editing-kit
description: Master index of the agency's saved reel editing styles and add-on kits — Pinteresty, Editorial Lookbook, Dark Split Explainer, Starfield Countdown, Podcast Premium Edit, Luxe Editorial Motion, Caption Animation Kit, Animation Style Kit, Animated Scene Engine, plus built-in reel-* styles. Use first whenever the user asks to edit/plan a reel, asks "which style", lists the kit, or names a niche (clothing, jewellery, food, sports, talking reel, interview, site visit, gaming, informational, travel) — then load the chosen style's skill.
---

# Reel Editing Kit — Master Index

## A. Full editing styles (pick ONE per reel)
| Style | Skill | Format | Signature | Best for |
|---|---|---|---|---|
| **Pinteresty** | `pinteresty-style` | Creator talking + b-roll, haul | B&W red-text hook, script lead-in + serif keyword, typed price tracker, doodle callouts, B&W asides, photo-strip | Hauls, cafés, lifestyle, D2C product, creator content |
| **Editorial Lookbook** | `editorial-lookbook` | No-talk, music-led | B&W still + colour photo cards popping into a grid, flash-cut burst, look→detail rhythm, wordmark fade | Clothing, ethnicwear, jewellery, launches, catalogue-to-reel |
| **Dark Split Explainer** | `dark-split-explainer` | Talking head, split screen | Black top panel with UI motion graphics, sans + italic-serif titles, stamps (NOW., SAME DAY), full-screen punchlines | Services, B2B, SaaS, courses, webinars, site visits |
| **Starfield Countdown** | `starfield-countdown` | Faceless/voice-over listicle | Numbered list revealing names, wiping showcase card, drifting grid CTA "Comment KEYWORD" | "10 looks/flavours/ways", product ranges, lead magnets |
| **Podcast Premium Edit** | `podcast-premium-edit` | Podcast / seated interview | Stacked mixed-size captions, orange script + highlighter accents, face-track bracket hook, cross-mask collage, scrapbook wide shot; NO EDIT vs FINAL ad | Podcasts, founders, coaches, interviews, agency lead-gen |
| **Luxe Editorial Motion** | `luxe-editorial-motion` | Model / talking, luxury | Glass phone card behind subject, one-giant-word captions, magazine serif beside model, script + polaroids, chrome-orb & stat interludes; 2×2 showcase | Luxury fashion, jewellery, beauty, premium brands, AI/SaaS promos |

## B. Add-on kits (layer onto any style)
| Kit | Skill | What it adds |
|---|---|---|
| **Caption Animation Kit** | `caption-animation-kit` | 12 text animations (Glass Widget, Behind-Head Depth, Smoke Exit, Wall Ink, Arc Orbit, Kinetic Bounce, Neon Sign, Giant Behind, Explosive Breakup, Retro Typer, Outline Run, Hierarchy Stack) + listicle overlays + sample reel |
| **Animation Style Kit** | `animation-style-kit` | 10 looks as filters on real footage (`looks.sh`) + AI prompt packs 1 & 2 (consistent character) |
| **Animated Scene Engine** | `animated-scene-engine` | Code-built animated scenes (dog walk, shopping, café, film set) in 18 styles; add scenes/props/mascots |

## C. Built-in styles (Anthropic skills)
`reel-checklist`, `reel-documentary`, `reel-glass-widgets`, `reel-orbit`, `reel-pixel-reveal`, `reel-split-chart`, `reel-spotlight`, `reel-timeline-ui`, `travlink-reference-edit`.

## D. Niche picker
| Niche | Main style | Add-ons |
|---|---|---|
| Clothing brand | Editorial Lookbook (launch/ads) · Pinteresty (hauls) | Hierarchy Stack, Outline Run; Anime/Pop Art looks |
| Jewellery brand | Luxe Editorial Motion · Editorial Lookbook (macro) | Arc Orbit, Hierarchy Stack; Sunset/Storybook looks |
| Food brand / café | Pinteresty · Starfield Countdown (menu) | Wall Ink, Kinetic Bounce; Claymation/Pop Art scenes |
| Sports | Dark Split Explainer (stats) · built-in glass widgets | Giant Behind, Explosive Breakup; Thermal/Cyberpunk looks |
| Talking reel | Dark Split Explainer · Podcast Premium | Behind-Head Depth, Smoke Exit; scene-engine cutaways |
| Interviews / podcasts | Podcast Premium Edit · built-in documentary | Hierarchy Stack, Glass Widget |
| Site visits / real estate | Dark Split Explainer · Luxe Editorial (luxury homes) | Wall Ink, Glass Widget; Isometric/Hologram |
| Gaming | Starfield Countdown · built-in timeline-ui | Explosive Breakup, Neon Sign; Pixel/Low-Poly/Cyberpunk |
| Informational | Dark Split Explainer · built-in checklist | Retro Typer, Glass Widget; Flat Vector/Paper scenes |
| Travel | Pinteresty · TravLink | Wall Ink, Hierarchy Stack; Anime/Ukiyo-e looks |
| Agency self-promo | Podcast Premium (NO EDIT vs FINAL) · Luxe 2×2 showcase | Comment-keyword CTA |

## E. Rules
1. One main style per reel + max 2 add-ons.
2. Every reel ends on a CTA mapped to a KPI (DM/comment keyword → CPL; link → CTR/ROAS; booking → cost per booking).
3. Keep text out of the bottom 20% and the right UI rail.
4. New reference reel → analyse → save as a new style skill → add a row here.

## F. Keyword map (team guide book: https://claude.ai/artifact/GC3aWAoCxqer5rZmN6j3no)
Requests use `STYLE:` + up to two add-ons; not case-sensitive; `+` joins.
- STYLE: PINTERESTY→pinteresty-style · LOOKBOOK→editorial-lookbook · DARKSPLIT→dark-split-explainer · COUNTDOWN→starfield-countdown · PODCAST→podcast-premium-edit (A) · NOEDIT→podcast-premium-edit (B, before/after ad) · LUXE→luxe-editorial-motion · GRID4→luxe-editorial-motion (2×2 showcase)
- STYLE (built-in): CHECKLIST→reel-checklist · DOCUMENTARY→reel-documentary · GLASS→reel-glass-widgets · ORBIT→reel-orbit · PIXELREVEAL→reel-pixel-reveal · SPLITCHART→reel-split-chart · SPOTLIGHT→reel-spotlight · TIMELINE→reel-timeline-ui · TRAVLINK→travlink-reference-edit
- TEXT: (caption-animation-kit) GLASS=Glass Widget · BEHINDHEAD=Behind-Head Depth · SMOKE=Smoke Exit · WALLINK=Wall Ink · ARC=Arc Orbit · BOUNCE=Kinetic Bounce · NEON=Neon Sign · GIANT=Giant Behind · EXPLODE=Explosive Breakup · TYPER=Retro Typer · OUTLINE=Outline Run · STACK=Hierarchy Stack · overlays COUNTER/NOTES/FOLLOW/COMMENTCTA
- LOOK: (animation-style-kit/looks.sh) CYBERPUNK PAPER HOLOGRAM POPART THERMAL ANIME SUNSET UKIYOE CLAYMATION · SWAP = style-swap hook/transition · `ON: hook|broll|transition|full`
- SCENE: (animated-scene-engine) DOGWALK SHOPPING CAFE FILMSET or `NEW — <description>` + STYLE: one of 18 engine styles; `CHARACTER:` locks a mascot via `colors`
- PROMPTS: PACK1 → animation-style-kit/prompts.md · PACK2 → prompts-pack-2.md
- NICHE: CLOTHING JEWELLERY FOOD SPORTS TALKING INTERVIEW SITEVISIT GAMING INFO TRAVEL AGENCY → use table D defaults
When a new style is saved, add its keyword here AND in the guide book doc.
