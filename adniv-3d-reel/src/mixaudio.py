import sys, subprocess, wave, json, numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-The100xers/3dc716bb-8387-5a31-912b-63c195d92910/scratchpad')
import sfx
SR=48000; TOTAL=53.6; N=int(TOTAL*SR)
def load(p, ch=2):
    raw=subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def lufs(x):
    # integrated loudness via ffmpeg ebur128 (BS.1770) on a temp wav
    import tempfile, os, re
    f=tempfile.mktemp(suffix=".wav"); pcm=(np.clip(x,-1,1)*32767).astype("<i2")
    with wave.open(f,"wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    r=subprocess.run(["ffmpeg","-nostats","-i",f,"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr
    os.remove(f); m=re.findall(r"I:\s+(-?[\d.]+) LUFS",r); p=re.findall(r"Peak:\s+(-?[\d.]+) dBFS",r)
    return float(m[-1]), float(p[-1]) if p else None
def g(db): return 10**(db/20)

vo=load("in/vo.mp3"); mu=load("in/music.mp3")
# --- voiceover -> -14.5 LUFS (speech only: gate on silence by ebur128 relative gate)
l,_=lufs(vo); vo*=g(-14.5-l)
VOUT=np.zeros((N,2),np.float32); VOUT[:min(len(vo),N)]=vo[:N]
# --- music: trimmed to 53.6 s, normalised so that it sits 19 dB under the VO, rising 4 dB on the CTA, fade out
mu=mu[:N]; 
if len(mu)<N: mu=np.pad(mu,((0,N-len(mu)),(0,0)))
lm,_=lufs(mu); mu*=g(-14.5-lm)
t=np.arange(N)/SR
env=np.full(N,-16.2)
env+=3.0*np.clip((t-44.0)/1.5,0,1)                        # rises on the CTA
env-= 2.0*np.clip((t-0.0)/1.0,0,1)*0                       # (placeholder)
fade=np.clip((TOTAL-t)/2.6,0,1); fade_db=20*np.log10(np.maximum(fade,1e-4))
fin=np.clip(t/0.8,0,1)                                      # fade in
# duck extra 3 dB under speech: smooth gate from word timings
W=json.load(open("in/words.json"))["words"]; duck=np.zeros(N)
for w in W:
    a,b=int((w["s"]-0.05)*SR),int((w["e"]+0.15)*SR); duck[max(a,0):min(b,N)]=1
k=int(0.12*SR); duck=np.convolve(duck,np.ones(k)/k,"same")
mdb=env-3.0*duck+fade_db+20*np.log10(np.maximum(fin,1e-4))
MUS=mu*(10**(mdb/20))[:,None]
# --- SFX
S=np.zeros((N,2),np.float32)
def put(sig,at,gain_db=0,pan=.5,pre=0.0):
    i=int((at-pre)*SR)
    if i<0 or i>=N: return
    e=min(i+len(sig),N); a=sig[:e-i]*g(gain_db)
    S[i:e,0]+=a*(1-pan)*1.4; S[i:e,1]+=a*pan*1.4
ev=[]
# street flip on "safed" 4.69: flash shimmer + a click per lamp pair running down the road
put(sfx.flash(),4.69,-3,.5,0.02); put(sfx.whoosh(),4.69,-8,.5,0.15)
for k in range(13): put(sfx.click(),4.73+k*0.155,-6 if k else -3,0.3+0.4*(k%2))
# 2015 sweep: switch click + a rolling set of fast ticks as the white wave crosses the city
put(sfx.click(),15.40,-2,.5); put(sfx.air(),15.30,-8,.5)
for k in range(8): put(sfx.click(),15.50+k*0.11,-10,0.25+0.5*(k%2))
# scene transitions
for tt,kind,gdb in [(7.4,'whoosh',-7),(14.2,'swell',-9),(24.0,'whoosh',-8),(27.65,'air',-8),(30.35,'swell',-8),(41.35,'whoosh',-7)]:
    put(getattr(sfx,kind)(),tt,gdb,.5,0.18)
put(sfx.flash(),44.85,-2,.5,0.02); put(sfx.whoosh(),44.85,-6,.5,0.15)
# reassemble + light on at "Adniv"
put(sfx.whoosh(True),35.45,-7,.5,0.0); put(sfx.click(),36.38,-1,.5); put(sfx.flash(),36.38,-5,.5,0.02)
# labels, count-ups, pills, CTA buttons: small UI ticks
for tt in (33.44,34.56): put(sfx.click(),tt,-8,.5)
for tt in (20.1,24.55,27.8): put(sfx.click(),tt,-9,.5)
for tt in (37.69,38.82,39.95,43.68): put(sfx.click(),tt,-9,.5)
for tt in (46.6,46.8): put(sfx.click(),tt,-8,.5)
SFXR=S*g(-4.5)
mix=VOUT+MUS+SFXR
# --- limiter: soft clip above -1.5 dBFS
pk=np.abs(mix).max(); ceil=g(-1.5)
mix=ceil*np.tanh(mix/ceil) if pk>ceil*0.9 else mix
li,lp=lufs(mix); lv,_=lufs(VOUT[:int(52.2*SR)]); lmus,_=lufs(MUS[int(1*SR):int(44*SR)]); 
print(f"final mix: {li:.1f} LUFS integrated, sample peak {20*np.log10(np.abs(mix).max()):.2f} dBFS, true-peak {lp} | VO alone {lv:.1f} LUFS | music (1-44 s) {lmus:.1f} LUFS -> {lv-lmus:.1f} dB under VO")
pcm=(np.clip(mix,-1,1)*32767).astype("<i2")
with wave.open("out/audio_mix.wav","wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
for name,sig in (("sfx",SFXR),("vo",VOUT),("music",MUS)):
    p=(np.clip(sig,-1,1)*32767).astype("<i2")
    with wave.open(f"out/stem_{name}.wav","wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(p.tobytes())
print("stems written")
