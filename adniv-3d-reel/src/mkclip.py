import sys,subprocess,wave,numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-The100xers/3dc716bb-8387-5a31-912b-63c195d92910/scratchpad')
import sfx
SR=48000
def build(flipT0, dur, out):
    n=int(dur*SR); L=np.zeros(n); R=np.zeros(n)
    def put(s,t,pan=.5,g=1.0):
        i=int(t*SR); e=min(i+len(s),n)
        if i<0 or i>=n: return
        L[i:e]+=s[:e-i]*(1-pan)*g*1.3; R[i:e]+=s[:e-i]*pan*g*1.3
    put(sfx.flash(),flipT0-0.02,.5,0.5)
    for k in range(12):                              # light-switch clicks run down the road with the wave
        put(sfx.click(),flipT0+0.03+k*0.17,0.35+0.3*(k%2),0.55)
    put(sfx.whoosh(),flipT0-0.15,.5,0.5)
    pk=max(abs(L).max(),abs(R).max()); g=10**(-6/20)/pk
    pcm=(np.clip(np.stack([L,R],1)*g,-1,1)*32767).astype('<i2')
    with wave.open(out,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
if __name__=="__main__":
    build(1.69,5.0,"out/flip_sfx.wav"); print("sfx ok")
