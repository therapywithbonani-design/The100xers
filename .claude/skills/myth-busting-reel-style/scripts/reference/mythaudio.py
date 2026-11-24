import numpy as np, wave, subprocess, math
t=open('sfx2_synth.py').read(); head=t[:t.index("# ---- timeline")].replace("import build as B\n","")
exec(head)
import mythpanels as P
SRC=__import__('mythlib').SRC
A0=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','build/voice_enh.wav','-ac','2','-ar','44100','-f','s16le','-'],capture_output=True).stdout,np.int16).reshape(-1,2).astype(np.float32)/32768
SH=int(round(0.030*44100)); A=np.concatenate([A0[SH:],np.zeros((SH,2),np.float32)])   # remove the 30 ms filter delay
n=len(A); fx=[]
def add(tt,sig,g=1.0,pan=0.0): fx.append((tt,sig,g,pan))
for k,(a,b,fn) in P.PANELS.items():
    add(a-0.06,whoosh(0.45,True,350,7000,0.7),0.30); add(b-0.40,whoosh(0.40,False,350,6000,0.6),0.26)
stk=[1.30,5.45,8.45,15.50,33.00,36.00]
for tt in stk: add(tt,pop(560,0.5),0.30)
add(5.45+0.03,error(0.4),0.30)
add(36.00+0.03,error(0.4),0.28)
tick=lambda: seq([784,1047],0.08,0.7,0.5)
add(11.40+1.45,tick(),0.30); add(11.40+2.25,tick(),0.30); add(11.40+2.45,pop(520,0.5),0.28)
add(19.45+0.15,pop(480,0.5),0.28); add(19.45+2.60,tick(),0.30); add(19.45+3.40,pop(430,0.5),0.28); add(19.45+5.15,error(0.45),0.30)
add(26.35+0.40,pop(480,0.5),0.28); add(26.35+1.20,pop(430,0.5),0.28); add(26.35+2.45,tick(),0.32); add(26.35+3.90,swish(0.2,0.5),0.30)
add(33.00+0.03,tick(),0.28)
mono=np.abs(A.mean(axis=1)); k=int(0.06*44100); env=np.convolve(np.convolve(mono,np.ones(k)/k,'same'),np.ones(2*k)/(2*k),'same'); envn=np.clip(env/(np.percentile(env,95)+1e-9),0,1); duck=1-0.5*envn
fxl=np.zeros(n+44100*2); fxr=np.zeros(n+44100*2)
for tt,sig,g,pan in fx:
    i=max(0,int(tt*44100)); m=min(len(sig),len(fxl)-i); s=sig[:m]*g
    if i+m<=len(duck): s=s*duck[i:i+m]
    fxl[i:i+m]+=s; fxr[i:i+m]+=s
mix=A.copy(); mix[:,0]+=fxl[:n]; mix[:,1]+=fxr[:n]
w=wave.open('build/myth_raw.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg','-v','error','-y','-i','build/myth_raw.wav','-af','loudnorm=I=-15:TP=-1.5:LRA=11,aresample=44100','-ar','44100','build/myth_audio.wav'],check=True)
print('audio ok',n/44100)
