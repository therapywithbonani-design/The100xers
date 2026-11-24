# Pitfalls and lessons (read before building)

## Audio / sync - the costly ones
1. **Wrong audio file.** Episode 4 shipped with Episode 3's voice because a find/replace renamed the *write* of the
   raw audio cache but not the *read*. Result: mouth never matched. Always derive cache names from one variable and
   run `scripts/verify_sync.py` (it reports low `corr` when the wrong voice is in the file) before delivering.
2. **loudnorm outputs 96 kHz.** Phones/gallery players play 96 kHz AAC late or drifting. Always end with
   `aresample=44100` and `-ar 44100` (`finalize_video.sh` does this).
3. **Filter latency.** Heavy voice filters (afftdn, dynaudnorm) delay audio ~30 ms. Measure with `verify_sync.py` and trim
   that many samples from the start of the filtered voice.
4. Build audio and video from the same segment list (live / title / question / outro). Title and question cards are
   silent for voice; count their lengths in frames (`round(sec*30)/30`) for both.
5. Do not pipe a script that writes the output file into `head`: the broken pipe kills it before it writes.
6. Re-mux audio with `-c:v copy` when only sound changes; no need to re-render the picture.
7. Delivery: keep < 30 MB (user's upload limit). `crf 22` gives ~17-25 MB for 30-40 s.

## Transcript
- Extract wav with ffmpeg first; faster-whisper's decoder can crash (PyAV version).
- Model downloads need huggingface.co, cdn-lfs.huggingface.co, cas-bridge.xethub.hf.co, cdn-lfs-us-1.hf.co,
  us.aws.cdn.hf.co, transfer.xethub.hf.co, cas-server.xethub.hf.co allowed in the environment's network settings
  (use the environment update tool; the user approves a card).
- Use an `initial_prompt` with domain words (universities, exams, brand names). Re-transcribe skipped stretches with
  gain x3. Hinglish: write Hindi words in Latin letters, fix obvious mis-hearings (CGPS -> CGPA) and flag them.
- Brand: **Successcribe** is one word.

## Person cut-out (title card + cover)
- `cutout.py`: RMBG-1.4 (full `onnx/model.onnx`, not the quantized one) gives a rough mask that grabs banners and the
  desk; GrabCut inside an ROI around the person fixes most of it.
- Remaining specks come from the yellow/red university banner and the pink plant behind the head: remove by colour
  (`fixcut.py`: yellow/red in the upper-right, leaf colours in the upper-left) and with small rectangular clips,
  then fill holes and keep the largest component. **Always open the result and look near the ear/hair.**
- Pick a freeze pose where the banner is not behind the head if possible.

## Frames
- Freeze frame: a natural pause after the first sentence, face visible, hand gesture is fine.
- Cover frame: eyes open, mouth closed, looking at camera. Contact-sheet 16 candidates from the silent windows.

## Layout
- Hook cover text must never cover the face: raise the person and put the pill on the chest.
- Captions: auto-shrink lines over ~980 px; stickers must not leave the 1080 px frame (check long text badges).
- Highlight markup must keep trailing punctuation inside the highlight (`*Kong,*`) or asterisks leak into the picture.
- A cross sticker must not sit on top of badge text; put it on a corner.

## Honesty with the user
State what was verified by measurement (sync offsets, duration, levels) and what was not watched/listened to.
List: question wording, names (students, brand), uncertain transcript words (ECTS/ACTS style), hand-drawn flags/badges
(real logos need user assets), cut-out edge quality.
