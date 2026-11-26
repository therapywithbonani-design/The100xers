# Adniv x CRUSH Salon reel: QA report

Cut: Style C "Light-On Kinetic", Cover 3 "Your salon, lit like this?"
File: `adniv_crush_reel.mp4`, H.264 High, 1080x1920, 30 fps, 16 Mbps, bt709, 30.7 s (9 scenes + 4.5 s end card). Silent. SFX stem separate.

| Check | Result |
|---|---|
| Frame at every scene and every transition | `qa/frames_every_scene.jpg`, `qa/frames_every_transition.jpg` (viewed) |
| Safe area x64-1016 / y230-1500, all frames | Overlay bounds of every frame (text, chips, plates, leader lines) tested, 0 violations. Logo box x736-1016, y244-358. End card content x69-834, y288-1461 |
| Icon column (x>940, y1000-1500) clear | Yes. Widest element ends at x=932 (sizes row, scene 5) |
| Safe-zone proof images | `qa/safezone_overlay_check.jpg`, `cover_safezone_check.jpg` |
| Logo top-right on every scene, none on end card | Yes. End card has only the centred main logo. Reversed (white) version on dark footage, original (black) on bright scene 5 |
| Spec spelling | Every on-screen string audited against the brief. No "concealed panel" label remains on any product (scenes 4 and 7 were corrected by the client) |
| No text over the lights | Text pixels over light-source pixels (luma>225): 0.0-1.0% (leader dot touches the fixture edge by design). Navy plates (scenes 1, 7, 9) sit over wall/floor areas, not fixtures. Scene 7 plate covers part of the wall glow, which is unavoidable in that busy frame |
| No colour wash over footage | Highlights rolled off in the grade only. No tint/gradient layers. Light-leak (scene 5 to 6) and white flash (2 to 3, 9 to end) are 0.3 s transitions |
| Faces | No prominent faces. Scene 1 has two staff walking at distance, seen from behind/profile. A receptionist is partly visible over the counter in scenes 1 and 5, small. The reclining guest (face visible from ~3.3 s of IMG_4905) is cut out |
| Clipped highlights | 0% on all rings/panels after grade (was 0.2-1.15%) |

Known compromises
- IMG_4893 (spa chandelier) was not supplied, so the planned mood scene is not in the reel.
- IMG_4902: the clip pans across the sign, so "C" touches the left edge at the very end. Window trimmed to the best 1.9 s.
- Scene 7 (IMG_4890) was straightened ~3.8 degrees with a 1.17x crop from the 4K frame.
- The reversed logo is derived from the supplied PNG (neutral parts inverted, blue mark and orange dot untouched), not an official Adniv asset.
- Hook chip "Lighting by Adniv" is an addition to the "CRUSH Salon, Gurgaon" line in your brief.

Update: website corrected to www.adniv.in on the end card, in the caption and in the review page (the brief originally listed www.adnivtech.com). The reel was re-encoded; nothing else changed. The end-card layout is unchanged (content x69-834, y288-1461).

Update 2: scene 8 ("Softer light. Longer stays.") changed from navy type on the beige chair to the navy plate with white type and orange extrusion, for legibility. Overlay bounds x64-788, y1186-1432 (inside the safe area, clear of the icon column).

Update 3 (client spec corrections)
- Scene 3 donut: now 800 mm Donut, 60 W (was 600 mm, 36 W & 40 W). Other specs unchanged: black finish, 4000K Neutral White, 50 x 70 mm, canopy + 1.5 m suspension kit.
- Scene 7 (IMG_4890) is a strip light with aluminium profile, not a concealed panel. It runs 4.8 s in two text phases on one navy plate: (1) Strip Light, 10 x 10 mm aluminium profile, 240 LED 24 V, 3000K Warm White, with power supply; (2) range: profile 10x10 / 12x12 / 16x16 / 25x25 mm & more, 3.6 m length; strip 120 LED 12 V and 240 LED 24 V with power supply, 5 m roll; 3000K / 4000K / 6500K / tri-colour 3-in-1.
- IMG_4890 is a locked-off shot, so it was slowed to 0.59x (frame-blended) to give the extra text time to be read. Slow motion is not noticeable on this shot.
- Reel is now 31.8 s (was 28.6 s). Safe-zone test re-run on all frames: 0 violations (scene 7 plate x64-898, y1110-1496).
- Caption updated to match; the concealed panel in the caption is the Round Concealed Panel from scene 4 (15 W, 4000K).

Update 4: scene 7 range screen now says what is available. Labels: "PROFILE SIZES AVAILABLE (mm) / 3.6 m LENGTH" with 10x10, 12x12, 16x16, 25x25 and "mm & more"; "STRIP AVAILABLE / 5 m ROLL" with 120 LED 12 V, 240 LED 24 V, with power supply; "STRIP COLOURS AVAILABLE" with 3000K, 4000K, 6500K, Tri-colour (3-in-1). Scene is 5.2 s (clip slowed to 0.54x, locked-off shot). Reel 31.1 s. Safe-zone re-run on all frames: 0 violations (scene 7 plate x64-928, y1084-1500). Caption updated to say "available".

Update 5: scene 5 replaced with the client photo (assets/photo_donut_sizes.jpg, 722x952 source). The reception clip IMG_4904 is no longer used.
- Layout: photo in a rounded card (x64-1016, y380-1118) on solid Adniv navy, logo top-right above it. Cropped to y160-720 of the photo so the staff at the bottom (faces) are out of frame.
- Animation: 0.5 s card slide-in, slow push-in (1.0 to 1.10), and a light-on effect on the fixtures only (rings and downlights are masked by brightness: dim, flicker, switch on with a soft bloom; the rest of the photo is untouched).
- Text: "Concealed Panel / Round Donut", "ALSO MADE TO YOUR OWN PREFERENCE", chips 450 / 500 / 600 / 800 / 900 / 1000 / mm & more. Text bounds x70-932, y1144-1464, inside the safe area. Safe-zone re-run on all frames: 0 violations.
- Source photo is low resolution (722 px wide), shown about 1.3x enlarged with light sharpening. A higher-resolution original would look crisper.

Update 6: scene 4 (IMG_4901) relabelled from "Round Concealed Panel, 15 W, 4000K" to a donut, per client. On screen: "DONUT", "02 ROUND DONUT / CUSTOM-MADE". The leader line to the small disc was removed. The 15 W and 4000K chips were dropped because they were attached to the panel label; the donut's own size and wattage are still needed from the client. Caption updated (concealed panel bullet and keyword removed). Safe-zone re-run on all frames: 0 violations (text x71-739, y1267-1466).
