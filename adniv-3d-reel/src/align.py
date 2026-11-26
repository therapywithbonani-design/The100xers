import json,subprocess,numpy as np
from faster_whisper import WhisperModel
raw=subprocess.run(["ffmpeg","-v","error","-i","in/vo.mp3","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
a=np.frombuffer(raw,np.float32).copy()
m=WhisperModel("small",device="cpu",compute_type="int8")
out={}
for lang in ("hi","en"):
    segs,info=m.transcribe(a,language=lang,word_timestamps=True,vad_filter=False,beam_size=5)
    words=[]
    for s in segs:
        for w in s.words: words.append(dict(w=w.word.strip(),s=round(w.start,3),e=round(w.end,3),p=round(w.probability,2)))
    out[lang]=words; print(lang,len(words),flush=True)
json.dump(out,open("ref/whisper_words.json","w"),ensure_ascii=False,indent=0)
