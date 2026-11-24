---
name: myth-busting-reel-style
description: Edit a talking-head video in the "Myth Busting" series style - hook left untouched, clean Inter sans-serif sentence-case captions with green highlight pills, off-camera interviewer question card, natural colour enhancement, flat white icon stickers, animated split-screen explainer panels (checklist, 75% vs 92% bar comparison, badge panels), cleaned and levelled voice, soft sound design, and a green shattered-glass cover with a two-line tilted question card and BUSTED stamp. Use whenever the user asks for "Myth Busting", "myth buster reel", "different editing style, not the Ask The Founder style", split screen with explainer visuals, or sends a founder clip that debunks a study-abroad myth (e.g. "high CGPA = guaranteed admission").
---

# Myth Busting - editing style

Vertical 1080x1920 / 30 fps reel for a study-abroad consultancy where a founder debunks a common myth. It is
deliberately calmer and cleaner than the Ask The Co-Founder series (see the `ask-cofounder-reel-style` skill):
no freeze title card, no smoke captions, no 3D text. The persuasion is in the structure: the myth is stated in the
first second, the answer is proven visually with split-screen panels, and the key claim is repeated at the end.
Business outcome: saves/shares, follows, consultation enquiries. Suggest KPIs: 3-second retention (hook),
average watch time (split screens), saves + shares (the myth/answer line).

Read `references/style-spec.md` (exact numbers) and `references/pitfalls.md` before building.

## Inputs to collect (ask briefly, then proceed with defaults and flag them)
- The clip. Who asks the question (often an off-camera interviewer: the question must be shown on screen).
- The myth sentence for the cover chip (two lines max) and the sticker.
- Brand assets only if the user wants them on screen (never fabricate logos; use text badges meanwhile).

## Workflow
1. **Analyse**: ffprobe, contact sheet, transcript: `python3 scripts/transcribe.py clip.mp4 work "domain words"`.
   Hinglish: caption Hindi words in Latin letters; fix mis-hearings (CGPS -> CGPA) and flag uncertain terms.
   Measure voice levels: the off-camera questioner is usually ~10 dB quieter than the founder.
2. **Plan** (source seconds; the video is NOT re-timed - the hook and all pauses stay as shot):
   - caption phrases (1-2 lines, from word timings), keyword highlights;
   - 2-3 split-screen moments (3.5-5.6 s each, about a third of the video max), each tied to a concrete thing
     he says (checklist of what universities look at, numbers compared, institutions named);
   - flat stickers for the myth, "not guaranteed", "overall profile", etc., outside split screens;
   - the interviewer question card words with start times.
3. **Build** with `scripts/reference/` (copy to a work dir; `mkdir -p fonts/ttf && cp assets/fonts/*.ttf fonts/ttf/`):
   `mythlib.py` (grade, captions, stickers) + `mythpanels.py` (panel designs + `PANELS` times) + `mythbuild.py`
   (captions/stickers/question card lists, render loop) + `mythaudio.py` + `mythcover.py`.
   Preview ~16 frames (`python3 mythbuild.py preview t1 t2 ...`), look at them, then `python3 mythbuild.py render`.
4. **Voice**: enhance first (chain in `references/style-spec.md`), compensate the ~30 ms filter delay, then add the
   soft effects and loudness-normalise (`mythaudio.py`, then `scripts/finalize_video.sh`).
5. **Cover**: cut out the person from a pause frame (eyes open, mouth closed) with `cutout.py` -> `mythcover.py`.
6. **Verify**: `scripts/verify_sync.py SOURCE EXPORT 1:1 6:6 12:12 ...` (identity mapping: the video is not retimed) must
   show 0 +-35 ms and high corr; check size (< 30 MB), sample rate 44100, duration; view preview frames.
7. **Deliver**: video + cover, commit/push if the repo workflow is in use. Say what was measured vs not watched/heard;
   list items to confirm (question wording, uncertain terms such as ECTS, badge artwork, cover frame/gesture).

## The style in one screen
- **Hook**: untouched. Question card (mic icon + "QUESTION") types in word by word as the interviewer speaks,
  top sticker "MYTH: High CGPA = Guaranteed admission?" in two lines.
- **Captions**: Inter Bold 62 px, sentence case, white, soft shadow, bottom-third; keywords sit on a green rounded pill;
  fade + 20 px rise; soft dark gradient under the captions keeps white text readable on white desks.
- **Colour**: natural enhancement - slightly richer muted colours (vibrance), gentle contrast, bright whites rolled off,
  tiny warmth, light vignette. Not bright, not punchy.
- **Stickers**: flat white rounded cards, green / red / gold icon circle, dark-green ink text, optional red tag.
- **Split screens**: dark-green dotted panel slides down from the top (0.42 s), video re-frames underneath with a gold divider;
  animated content timed to words (rows slide in and tick, bars grow, chips appear), slides back out (0.40 s).
- **Sound**: voice cleaned and levelled; very quiet whoosh/pop/tick/buzz under the voice.
- **Cover**: green shattered-glass background (different from the sunburst), "MYTH" white 3D over "BUSTING" gold 3D, tilted,
  a tilted two-line question card with red MYTH tag and gold marker on the key word, BUSTED stamp beside the head.

## Rules that matter
- "Keep the hook as it is": no cuts, no retime, no intro card in the first seconds; overlays only.
- Do not retime audio vs video; never export audio at 96 kHz (see pitfalls).
- Do not state facts the founder did not say; flag uncertain words instead of guessing silently.
- Text must fit the 1080 px frame with margins; long lines go to two balanced lines.
- A different series needs its own style skill; do not reuse Ask The Co-Founder elements here (sunburst, smoke captions, 3D lower text).
