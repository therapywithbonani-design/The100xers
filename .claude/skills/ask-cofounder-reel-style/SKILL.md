---
name: ask-cofounder-reel-style
description: Edit a talking-head video in the "Ask The Co-Founder" series style - black-and-white cold open with series tag, freeze-frame title card (dark green sunburst, white-outlined cut-out, 3D "EPISODE N"), typing "question from a student" card, Montserrat smoke-reveal captions with yellow highlighted keywords, pop-in flag/badge/icon stickers on keywords, tuned sound design, "To be continued" outro and matching covers. Use this whenever the user says "same style as episode 1/2/3/4", "Ask The Co-Founder", "edit this as episode N", "founder answering student questions", or sends a new founder Q&A clip for the series, even if they only say "edit this like the previous ones".
---

# Ask The Co-Founder - episode editing style

A vertical (1080x1920, 30 fps) founder-answers-student-question series for a study-abroad consultancy
(brand: Successcribe). The look is high-energy: every few seconds something changes (zoom, sticker, caption pop)
so viewers keep watching, and the end hook ("To be continued...") makes them follow for the next episode.
Business outcome: follows / returns per episode, DMs and consultation bookings. Suggest KPIs to the user
(3-second retention for the freeze title, follows per reach for the outro, saves/shares for the answer).

Read `references/style-spec.md` for exact numbers/colours/timings and `references/pitfalls.md` before building:
it lists the mistakes that cost us rounds of rework (wrong audio file loaded, 96 kHz audio, cut-out specks, ...).

## Inputs to collect (ask briefly, then proceed with defaults and flag them)
- The clip. Episode number (series name is fixed: **Ask The Co-Founder**).
- The student's question text. Founders often read it off a phone, so it is not always audible: write a short
  clean version from what is audible, and flag it for confirmation.
- Brand name/logo if the founder says it (Successcribe is ONE word; logo goes in a white rounded card).
- Key terms that deserve stickers (countries -> flags, universities -> badge, % / dates -> badge).
  Real logos/photos (universities, brands) must come from the user; draw generic badges meanwhile and say so.

## Workflow
1. **Analyse**: `ffprobe`, contact sheet (`fps=1/2,tile`), transcript with word timestamps:
   `python3 scripts/transcribe.py clip.mp4 work/epN "domain words, brand names"`. This needs
   huggingface.co + cdn hosts allowed in the environment network (see pitfalls). Read the silent windows list:
   those are where cuts and the freeze frame go.
2. **Plan the timeline** (source seconds): cold-open end / freeze point `FRZ` (a pause after the first sentence,
   face visible, not mid-word), resume point `RES`, dead-air cuts (pauses >= 0.5 s), zoom blocks that change at
   each cut, caption phrases (2-4 words, <= 2 lines, from word timings), sticker list (keyword -> start/end).
3. **Pick two frames**: freeze frame for the title card and a cover frame (eyes open, mouth closed, looking
   at camera, not speaking: look at pauses, view a contact sheet of face crops). Cut the person out with
   `scripts/reference/cutout.py` (RMBG-1.4 mask + GrabCut) and clean specks with `fixcut.py`; **view the result**.
4. **Build**: copy `scripts/reference/*.py` and `assets/fonts` into a work dir; the working pipeline is
   `build3.py` (video) + `sfx4.py` (audio) + `cover3.py` (covers). Edit only the config blocks listed in
   `references/style-spec.md` ("Adaptation points"). Render previews of ~15 frames first, look at them, fix, then render.
5. **Sound**: `sfx4.py` synthesises and mixes the effects from the same timeline; then
   `scripts/finalize_video.sh` (loudness, 44.1 kHz, <30 MB).
6. **Verify before sending**: `scripts/verify_sync.py SOURCE EXPORT out:src ...` at ~6 points inside live segments:
   offsets must be within +-35 ms and corr high. Check duration, resolution, sample rate, peak (< -1 dB).
7. **Deliver**: send the mp4 + both covers; commit/push if the repo workflow is in use. Report honestly what
   was measured vs. what was not watched/listened to, and list items needing confirmation (names, question
   wording, uncertain transcript words, cut-out edges, hand-drawn badges/flags).

## The style in one screen
- **Cold open (3-4.5 s)**: live footage in black & white; red-bar series tag top-left types in
  ("Ask The Co-Founder" / "EPISODE N"); colour fades in at ~1-1.8 s.
- **Freeze title card (3.0 s)**: white flash, dark-green rotating sunburst, founder cut-out with thick white
  outline sliding up, 3 stacked lines "ASK THE / CO-FOUNDER / EPISODE N" in Montserrat Black with red-purple
  3D extrude, pop-in with overshoot, impact hit sound.
- **Question card (3.4 s)**: yellow "QUESTION FROM A STUDENT" pill + white chat bubble: typing dots, then text
  types out, key words in green. Then straight back into the answer.
- **Body**: Montserrat ExtraBold captions with soft shadow and a smoke reveal; keywords bigger + yellow
  (negatives red); alternate zoom levels at every cut; stickers pop above the head on the keyword and leave
  when it is done; red x for "don't/no", green tick for "do/yes".
- **Outro (2.8 s)**: last frame in B&W, "TO BE CONTINUED..." + yellow "FOLLOW FOR EPISODE N+1" pill, riser + impact.
- **Covers**: (a) series name + episode number only, (b) same + a short question hook pill; person raised so the
  pill sits on the chest, never on the face.

## Rules that matter
- Never retime audio and video separately: build the audio from the SAME segment list as the video.
- Do not invent facts in captions (dates, percentages, names): use what is spoken, flag uncertain words.
- Keep to the series colours (dark green, white, yellow highlight, red/purple 3D) so episodes look like one series.
- A different series (e.g. Myth Busting) has its own style skill: do not mix them.
