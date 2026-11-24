#!/usr/bin/env python3
"""Check that audio in an EXPORT lines up with the SOURCE recording. Run before delivering.

usage: python3 verify_sync.py SOURCE EXPORT out_t:src_t [out_t:src_t ...]
Each pair says "at EXPORT time out_t the speech should be the source's speech at src_t".
Pick ~6 pairs spread across the video (inside live-footage segments, not title cards).
Prints the audio offset in ms; anything beyond +-35 ms (1 frame) is a bug.
corr ~0.9+ means the voice matches; low corr (<0.4) means the WRONG audio is in the file.
"""
import numpy as np, subprocess, sys
SR=16000
def pcm(path,t0=None,dur=None):
    cmd=['ffmpeg','-v','error']+(['-ss',str(t0),'-t',str(dur)] if t0 is not None else [])+['-i',path,'-ac','1','-ar',str(SR),'-f','s16le','-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.int16).astype(np.float32)
def hpf(x): return x-np.convolve(x,np.ones(32)/32,'same')
SRC,TEST=sys.argv[1],sys.argv[2]; pairs=[tuple(map(float,p.split(':'))) for p in sys.argv[3:]]
S=hpf(pcm(SRC))
for ot,st in pairs:
    seg=hpf(pcm(TEST,ot,1.0)); lo=int(max(0,st-0.8)*SR); hi=int(min(len(S)/SR,st+1.8)*SR); ref=S[lo:hi]
    N=1<<int(np.ceil(np.log2(len(ref)+len(seg)))); c=np.fft.irfft(np.fft.rfft(ref,N)*np.conj(np.fft.rfft(seg,N)),N)[:len(ref)-len(seg)]
    nn=np.sqrt(np.convolve(ref**2,np.ones(len(seg)),'valid')[:len(c)])*np.linalg.norm(seg)+1e-6; c=c/nn
    i=int(np.argmax(c)); f=(lo+i)/SR; print(f"out {ot:6.2f}s expected src {st:7.3f} -> found {f:7.3f}  offset {(f-st)*1000:+5.0f} ms  corr {c[i]:.2f}")
