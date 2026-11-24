---
name: caption-animation-kit
description: Library of 12 animated caption/text styles (Glass Widget, Behind-Head Depth, Smoke Exit, Wall Ink, Arc Orbit, Kinetic Bounce, Neon Sign, Giant Behind, Explosive Breakup, Retro Typer, Outline Run, Hierarchy Stack) plus supporting overlays (series counter, prompt bar, checklist notes panel, browser card, follow-button gag, comment-keyword CTA). Use when the user asks for animated captions, kinetic text, text animation styles, or wants to add any of these to a talking reel, tutorial, listicle, product or brand reel — alone or layered on another style (pinteresty-style, editorial-lookbook, reel-*).
---

# Caption Animation Kit — 12 Text Styles

Reverse-engineered from a 38s, 9:16 talking-head listicle ("12 animated caption styles").
Speaker on a sofa, warm lamp-lit room, one take with jump cuts. Every 2–3s a new caption style.

## 0. Base layer used under every style
- **Running caption:** 1–3 words at a time, white bold sans (**Inter/Poppins Bold**), small, centred mid-chest (~65% height). **Keyword in yellow #FFD21F.**
- Big animated style sits in the **upper third** (head/wall area) so both coexist.
- Shared palette: white, warm yellow #FFD21F, peach #F7B28C, neon pink #FF4FD8, deep red-brown #8E2A2A (ink).
- Shared font pair: **clean geometric sans** for connectors + **italic display serif** (**Playfair Display Italic / DM Serif Display Italic**) for the keyword. Rule: *small sans words lead, big serif keyword lands.*

---

## 1. The 12 styles

| # | Name | Look | Motion (in → hold → out) | Best for |
|---|---|---|---|---|
| 1 | **Glass Widget** | Frosted pill (background blur 20px, white 15–20% fill, 1px white stroke, 24px radius) with an icon on the left (toggle switch / play button / emoji tile). White sans; keyword in gold italic serif | Pill slides up 20px + fades in (6f); toggle flips grey→yellow on the keyword; pill grows width as words type in; fade out | Tech, SaaS, apps, sports stats, real-estate specs |
| 2 | **Behind-Head Depth** | Words stacked vertically above/around the head; lead words small white sans, keyword HUGE gold italic serif with soft glow; text sits **behind the subject** (person mask) | Each word fades up 15px one by one, previous words dim to 40%; keyword scales 110→100% | Talking reels, coaches, founders, interviews |
| 3 | **Smoke Exit** | White bold sans, keyword yellow | New words appear clean; previous line **dissolves into smoke** — blur 0→20, turbulent displace, drift up 30px, opacity →0 over 12f | Storytelling, transitions between points, mystery hooks |
| 4 | **Wall Ink** | Text "painted" on the wall: corner-pinned/tracked to the wall plane, rotated with perspective, Multiply blend, dark red-brown; sans lead + script/serif italic keyword | Write-on / brush wipe reveal per word, stays stuck to wall while camera moves | Home décor, cafés, interiors, site visits, lifestyle |
| 5 | **Arc Orbit** | Words placed on a curved path around head/shoulders; keyword yellow | Text scrolls along the arc (path offset animation) as words are spoken | Personal brand, jewellery (around neck/face), beauty |
| 6 | **Kinetic Bounce** | Alternating: white CAPS sans / big yellow italic serif | Each word drops from −80px with spring overshoot (110%→95%→100%, ~10f), squash on landing | Kids, food, D2C fun brands, energetic promos |
| 7 | **Neon Sign** | Rounded sans (**Comfortaa/Quicksand Bold/Poppins**), magenta #FF4FD8 core + white inner + 2-layer outer glow; tiny lowercase connector in blue neon | Flicker on: 0→100→20→100→60→100 opacity over 10f, slight glow pulse while held | Nightlife, cafés, bars, events, gaming, beauty |
| 8 | **Giant Behind** | Massive condensed CAPS (**Anton/Bebas Neue**) in yellow, full frame width, **behind the subject**; small italic serif connectors in front ("that", "behind me", "down.") | Letters **rise** from below with stagger (2f per letter) or **fall** off bottom with stagger + motion blur; old word exits as new enters | Hooks, sports, gym, sale announcements, product names |
| 9 | **Explosive Breakup** | Bold CAPS yellow with orange bevel/outline + glow, "EXPLODES!" | Pops in 120→100%; on beat letters **scatter** outward with rotation + blur + sparkle particles, fade over 15f | Big reveals, discounts, launches, gaming, sports highlights |
| 10 | **Retro Typer** | Monospace (**Courier Prime/Space Mono**), light grey-white, keyword yellow, solid block cursor █ | Character-by-character type-on (1 char / 1–2f), cursor blinks at 2Hz, optional key-click SFX | Tutorials, informational, tech, B2B, "how it works" |
| 11 | **Outline Run** | Glowing white stroke (4px + glow) traced around the **subject's silhouette**; caption runs along that outline path (white sans, keyword yellow) | Stroke draws on around the body, then text slides along the path | Fashion (outline the outfit), fitness (body), product hero |
| 12 | **Hierarchy Stack** | Clean centred 2-tier: small white/grey sans title + giant peach italic serif keyword underneath with soft glow | Title fades in; keyword fades up 20px + blur 10→0 | Elegant brands, ethnicwear, jewellery, title cards, CTAs |

---

## 2. Supporting overlays (series / listicle kit)

- **Title card:** giant yellow number with dark outline ("12") + white CAPS on a black highlight strip (rough torn edges) + italic serif glow line beneath. Pops in letter by letter in first 1s.
- **Series counter (top-left):** small orange pill "01/12" + style name in white small sans. Updates each segment.
- **Prompt bar (top-centre):** frosted rounded pill with monospace typed command and an orange send-arrow button — "typing a prompt" effect before each style. Swap for a search bar / order field for brands.
- **Checklist notes panel (bottom-right):** white iOS-Notes-style card, title + list of all items; current item bold with yellow tick, completed items ticked. Persistent progress = retention.
- **Browser / app card:** rounded window card (traffic-light dots) slides down from top showing a website/product page; add a yellow **"FREE" starburst** badge and a small "live · hands-on" pill.
- **Handwritten aside:** white script note with emoji ("just drag to tweak :P"), slight rotation.
- **Follow-button gag:** profile card drops in, cursor clicks **Follow** (blue) → turns to **Following ✓** (purple) with a click SFX.
- **Comment CTA card:** Instagram comments sheet slides up, keyword ("CAPTIONS") types into the comment field + big glowing yellow keyword over the speaker.
- **Outro:** "I'll see you in the next one." — word-by-word, one keyword yellow, last word held.

---

## 3. How to build (by tool)
- **Person mask (styles 2, 8, 11):** CapCut "Remove background" on a duplicate layer above the text; Resolve Magic Mask; AE Roto Brush. Text track sits between the plate and the cutout.
- **Wall tracking (4):** CapCut "Tracking" or Resolve planar tracker / AE Mocha corner pin; blend mode Multiply.
- **Smoke / explode (3, 9):** CapCut text animations "Dissolve"/"Shatter" + particle overlay; AE Turbulent Displace + Shatter/CC Particle World.
- **Glow (7, 12, 2):** duplicate text, Gaussian blur 15–30, Screen/Add blend, 60% opacity.
- **Typer (10):** CapCut "Typewriter" in-animation; Resolve Text+ "Write On".
- **Path text (5, 11):** AE text-on-path; CapCut "Curve" text + keyframed rotation as a workaround.
- I can also render any of these directly (ffmpeg + HTML/canvas overlays) on uploaded footage.

## 4. Picking styles by niche

| Niche | Primary | Accents |
|---|---|---|
| Clothing | Hierarchy Stack, Outline Run | Behind-Head Depth |
| Jewellery | Arc Orbit, Hierarchy Stack | Neon Sign (festive) |
| Food / café | Wall Ink, Kinetic Bounce | Neon Sign |
| Sports | Giant Behind, Explosive Breakup | Glass Widget (stats) |
| Talking reel | Behind-Head Depth, Smoke Exit | Giant Behind (hook) |
| Interviews | Hierarchy Stack (name/quote), Smoke Exit | Glass Widget (credentials) |
| Site visits | Wall Ink (on walls), Glass Widget (specs) | Arc Orbit |
| Gaming | Explosive Breakup, Neon Sign | Retro Typer |
| Informational | Retro Typer, Glass Widget | Checklist panel + series counter |
| Travel | Wall Ink (on landmarks/buildings), Hierarchy Stack | Kinetic Bounce |

Rules: max **2 big styles + base caption** per reel unless it's a listicle; one keyword per line; keep upper-third text clear of face, and all text out of the bottom 20% and right UI rail.

## 5. Conversion layer (what this reel does well — reuse it)
- **Listicle hook:** number + promise in frame 1 ("12 …"), counter top-left keeps people to the end.
- **Comment-keyword lead magnet:** "Comment CAPTIONS and I'll send you the link" + comment-card overlay → DM automation (ManyChat). Swap reward per brand: price list, menu, size guide, discount code, brochure.
- **Follow gag** mid-reel, not at the end.
- **"FREE" badge** on the offer card.
- KPIs: comments-per-1k-reach (keyword comments), DM→lead conversion, CPL; 3s hold >60%, avg watch time >50%, saves.

## 6. Sample reel
`samples/caption-styles-sample.mp4` shows all 12 styles labelled. Re-render: `node .claude/skills/caption-animation-kit/demo/render.js <abs path to demo dir> out.mp4` (canvas renderer in demo/index.html — reuse its draw functions for real footage overlays).
