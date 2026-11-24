#!/usr/bin/env python3
"""Word-level transcript + silence map for a talking-head clip.

usage: python3 transcribe.py VIDEO OUT_DIR "domain prompt, brand names, jargon"

Why this exists: faster-whisper's own decoder crashes on some phone files (PyAV
version mismatch), so audio is extracted with ffmpeg first. The initial prompt
(brand names, universities, exams) fixes most mis-hearings. Stretches the model
skipped (long gaps between words that are NOT silent) are re-run with boosted gain.
Writes OUT_DIR/words.json  [[start,end,word],...]  and prints segments + silent windows.
Needs huggingface.co (+ the cdn/xethub hosts) allowed in the environment network settings.
"""
import sys, json, subprocess, os, numpy as np
video, out = sys.argv[1], sys.argv[2]; prompt = sys.argv[3] if len(sys.argv) > 3 else ""
os.makedirs(out, exist_ok=True); wav = f"{out}/audio.wav"
subprocess.run(["ffmpeg","-v","error","-y","-i",video,"-ac","1","-ar","16000",wav],check=True)
raw = subprocess.run(["ffmpeg","-v","error","-i",wav,"-f","s16le","-"],capture_output=True).stdout
a = np.frombuffer(raw,np.int16).astype(np.float32)/32768
from faster_whisper import WhisperModel
m = WhisperModel("medium", compute_type="int8")
segs,_ = m.transcribe(a, word_timestamps=True, beam_size=5, initial_prompt=prompt, vad_filter=False)
words = []
for s in segs:
    print(f"--{s.start:6.2f}-{s.end:6.2f} {s.text}")
    words += [[x.start,x.end,x.word] for x in s.words]
# silence map (0.1 s windows below RMS 400/32768)
k = 1600; rms = [np.sqrt((a[i:i+k]**2).mean())*32768 for i in range(0,len(a),k)]
silent = [round(i*0.1,1) for i,x in enumerate(rms) if x < 400]
# gaps > 0.9 s between words that contain speech energy -> re-transcribe boosted
for (s0,e0,_),(s1,e1,_) in zip(words, words[1:]):
    if s1-e0 > 0.9:
        seg = a[int(e0*16000):int(s1*16000)]
        if len(seg) and np.sqrt((seg**2).mean())*32768 > 600:
            ss,_ = m.transcribe(np.clip(seg*3,-1,1), word_timestamps=True, beam_size=5, vad_filter=False,
                                condition_on_previous_text=False, no_speech_threshold=0.95, log_prob_threshold=-3.0)
            for q in ss:
                for x in q.words: words.append([x.start+e0, x.end+e0, x.word])
            print(f"re-transcribed missed speech {e0:.2f}-{s1:.2f}")
words.sort(key=lambda w: w[0]); json.dump(words, open(f"{out}/words.json","w"))
print("silent windows (0.1 s):", silent)
