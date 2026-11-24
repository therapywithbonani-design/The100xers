import numpy as np, wave, subprocess, math
import build3 as B
SR=44100; FPS=30
rs=np.random.RandomState(11)
def T(d): return np.arange(int(d*SR))/SR
def env_exp(n,k): return np.exp(-np.arange(n)/SR*k)
def lowpass_sweep(x,f0,f1):
    y=np.zeros_like(x); s=0.; n=len(x)
    for i in range(n):
        fc=f0*(f1/f0)**(i/n); a=1-math.exp(-2*math.pi*fc/SR); s+=a*(x[i]-s); y[i]=s
    return y
def hp(x,fc=2000):
    a=math.exp(-2*math.pi*fc/SR); y=np.zeros_like(x); p=0.;q=0.
    for i in range(len(x)): y[i]=a*(y[i-1]+x[i]-q) if i else x[0]; q=x[i]
    return y
def norm(x,pk=1.0): m=np.abs(x).max(); return x/m*pk if m>0 else x
def reverb(x,dec=0.9,mix=0.3,seed=5):
    r=np.random.RandomState(seed); n=int(dec*SR*1.5); t=np.arange(n)/SR
    ir=r.randn(n)*np.exp(-t*(6.9/dec)); ir[:int(0.012*SR)]*=np.linspace(0,1,int(0.012*SR))
    N=1<<int(np.ceil(np.log2(len(x)+n))); y=np.fft.irfft(np.fft.rfft(x,N)*np.fft.rfft(ir,N),N)[:len(x)+n]
    y=y/np.abs(y).max()*np.abs(x).max()
    out=np.zeros(len(x)+n); out[:len(x)]+=x*(1-mix); out+=y*mix*1.4; return out
def whoosh(dur=0.5,rise=True,f0=250,f1=7000,pk=0.8):
    x=rs.randn(int(dur*SR)); y=lowpass_sweep(x,f0,f1) if rise else lowpass_sweep(x,f1,f0)
    n=len(y); p=np.linspace(0,1,n); e=np.sin(np.pi*p)**(1.6 if rise else 1.6)
    e=(p**1.8) if rise else ((1-p)**1.8); e=e*np.sin(np.pi*np.clip(p,0,1))**0.4
    return norm(y*e,pk)
def swish(dur=0.2,pk=0.5): 
    y=whoosh(dur,True,600,9000,pk); return y
def riser(dur=0.9,pk=0.8):
    t=T(dur); n=len(t); p=t/dur
    f=180*(7**p); ph=2*np.pi*np.cumsum(f)/SR
    tone=np.sin(ph)*0.5+np.sin(ph*2.01)*0.25
    nz=lowpass_sweep(rs.randn(n),300,9000)*0.9
    return norm((tone+nz)*(p**2.2),pk)
def impact(dur=1.4,pk=0.95):
    t=T(dur); n=len(t)
    f=48+110*np.exp(-t*22); body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.2)
    sub=np.sin(2*np.pi*38*t)*np.exp(-t*2.2)*0.5
    crack=hp(rs.randn(n),1500)*np.exp(-t*45)*0.7
    boom=lowpass_sweep(rs.randn(n),1800,120)*np.exp(-t*4.0)*0.6
    y=reverb(norm(body+sub+crack+boom,1),1.3,0.28); return norm(y,pk)
def zap(pk=0.5):   # white-flash "shing"
    t=T(0.35); y=hp(rs.randn(len(t)),3500)*np.exp(-t*14)
    y+=np.sin(2*np.pi*(2400+3500*np.exp(-t*30))*t)*np.exp(-t*20)*0.4; return norm(y,pk)
def pop(f0=520,pk=0.6,dur=0.16):
    t=T(dur); f=f0*(1+1.4*(1-np.exp(-t*60))); y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*28)
    y+=hp(rs.randn(len(t)),4000)*np.exp(-t*220)*0.3; return norm(y,pk)
def bell(f,dur=1.0,pk=0.5,idx=1.6,ratio=3.5,dec=4.5):
    t=T(dur); y=np.sin(2*np.pi*f*t+idx*np.exp(-t*3)*np.sin(2*np.pi*f*ratio*t))*np.exp(-t*dec)
    y+=0.25*np.sin(2*np.pi*f*2*t)*np.exp(-t*dec*1.4); return norm(y,pk)
def seq(notes,gap,dur=0.9,pk=0.5,dec=5.0,rev=0.25):
    L=int((gap*(len(notes)-1)+dur)*SR)+1; out=np.zeros(L)
    for i,f in enumerate(notes):
        b=bell(f,dur,pk,dec=dec); s=int(i*gap*SR); out[s:s+len(b)]+=b[:L-s]
    return norm(reverb(out,0.8,rev),pk)
def sparkle(pk=0.4,n=5):
    out=np.zeros(int(0.9*SR)); 
    for i in range(n):
        f=rs.choice([2093,2349,2637,3136,3520,3951]); b=bell(f,0.5,0.6,idx=0.8,dec=9); s=int(i*0.045*SR); out[s:s+len(b)]+=b[:len(out)-s]
    return norm(reverb(out,0.6,0.25),pk)
def error(pk=0.6):
    t=T(0.34); f=185*(0.55+0.45*np.exp(-t*7)); ph=2*np.pi*np.cumsum(f)/SR
    y=(np.sign(np.sin(ph))*0.5+np.sin(ph))*np.exp(-t*8.5)
    y=lowpass_sweep(y,2500,500)+np.sin(2*np.pi*70*t)*np.exp(-t*12)*0.8; return norm(y,pk)
def stamp(pk=0.8):
    t=T(0.5); y=np.sin(2*np.pi*(70+120*np.exp(-t*40))*t)*np.exp(-t*9)+hp(rs.randn(len(t)),900)*np.exp(-t*70)*0.5
    return norm(reverb(y,0.5,0.15),pk)
def knock(pk=0.8):
    t=T(0.35); y=np.sin(2*np.pi*(190*np.exp(-t*8))*t)*np.exp(-t*22)+lowpass_sweep(rs.randn(len(t)),4000,900)*np.exp(-t*60)*0.9
    y+=np.sin(2*np.pi*620*t)*np.exp(-t*45)*0.25; return norm(reverb(y,0.45,0.2),pk)
def click(pk=0.3):
    t=T(0.02); return norm(hp(rs.randn(len(t)),5000)*np.exp(-t*400),pk)
def drone(dur=2.6,pk=0.35):
    t=T(dur); y=np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*82.4*t)+0.3*np.sin(2*np.pi*110*t)
    e=np.minimum(1,t/0.6)*np.exp(-np.maximum(0,t-0.6)*1.1); return norm(y*e,pk)
# ---- timeline (Episode 2)
def o(s_):
    t0=0.
    for k,a,b in B.segments():
        if k=='live':
            n=int(round((b-a)*FPS))
            if a-1e-6<=s_<a+n/FPS: return t0+(s_-a)
            t0+=n/FPS
        elif k=='title': t0+=int(round(B.TITLE*FPS))/FPS
        elif k=='question': t0+=int(round(B.QLEN*FPS))/FPS
        else: t0+=int(round(B.OUTRO*FPS))/FPS
    return t0
QL=B.QLEN
TITLE0=int(round(B.FRZ*FPS))/FPS; Q0=TITLE0+B.TITLE
TOT=sum((int(round((b-a)*FPS))/FPS if k=='live' else int(round({'title':B.TITLE,'question':B.QLEN,'outro':B.OUTRO}[k]*FPS))/FPS) for k,a,b in B.segments())
OUT_OUTRO=TOT-int(round(B.OUTRO*FPS))/FPS
print('title0',TITLE0,'q0',Q0,'outro',OUT_OUTRO,'total',TOT)
fx=[]
def add(t,sig,g=1.0,pan=0.0,duck=True): fx.append((t,sig,g,pan,duck))
for i in range(13): add(0.25+i*0.043,click(0.22+0.1*rs.rand()),1,-0.5,False)
add(0.15,pop(900,0.35,0.1),0.7,-0.5,False)
add(TITLE0-1.0,riser(1.0,0.85),0.45,0,True)
add(TITLE0,impact(),1.0,0,False); add(TITLE0-0.02,zap(0.5),0.8,0,False)
add(TITLE0,whoosh(0.55,True,300,6000,0.7),0.55,0,False)
for d,f in ((0.10,380),(0.20,440),(0.34,330)): add(TITLE0+d+0.02,stamp(0.7),0.75,0,False); add(TITLE0+d+0.02,pop(f,0.5),0.6,0,False)
add(TITLE0+0.62,sparkle(0.5),0.85,0.2,False); add(TITLE0+2.0,drone(1.0,0.2),0.4,0,False)
add(TITLE0+3.0-0.42,whoosh(0.42,True,500,9000,0.7)[::-1].copy(),0.6,0,False); add(TITLE0+3.0-0.1,zap(0.4),0.6,0,False)
add(Q0-0.04,whoosh(0.4,True,400,8000,0.7),0.5,0,False)
add(Q0+0.05,pop(650,0.5),0.6,0,False); add(Q0+0.38,pop(560,0.4),0.35,0,False)
add(Q0+0.55,seq([1319,1760],0.07,0.7,0.5),0.8,0,False)
for i in range(int(1.9/0.052)): add(Q0+0.66+i*0.052,click(0.16+0.1*rs.rand()),1,0.2,False)
add(Q0+QL-0.42,whoosh(0.42,True,500,9000,0.7)[::-1].copy(),0.6,0,False)
for s_ in (4.85,7.15,13.3,18.75,26.25): add(o(s_)-0.06,swish(0.2,0.5),0.5,0.3,True)
good=lambda: seq([784,1047],0.09,0.8,0.55)
add(o(7.90),pop(430,0.6),0.85,0,True)
add(o(9.72),pop(560,0.6),0.8,0,True); add(o(9.72)+0.03,sparkle(0.35,4),0.7,0,True)
add(o(10.64),pop(430,0.6),0.85,0,True); add(o(11.0)+0.02,error(0.55),0.8,0.3,True)
add(o(12.30),pop(520,0.6),0.8,0,True); add(o(12.30)+0.04,bell(1319,0.9,0.3),0.6,0,True)
add(o(16.22),pop(520,0.6),0.8,0,True)
add(o(17.95),pop(500,0.6),0.8,0,True); add(o(18.4),good(),0.8,0.2,True)
add(o(19.62),pop(520,0.6),0.8,0,True); add(o(21.0),good(),0.8,0.2,True)
add(o(21.62),pop(430,0.6),0.85,-0.5,True); add(o(22.26),pop(380,0.6),0.85,0,True); add(o(22.94),pop(340,0.6),0.85,0.5,True)
add(o(26.58),stamp(0.9),0.9,0,True); add(o(26.58)+0.02,pop(480,0.5),0.6,0,True)
add(o(27.0),error(0.6),0.9,0.3,True); add(o(27.0)+0.02,stamp(0.6),0.5,0,True)
add(OUT_OUTRO-0.45,riser(0.45,0.6),0.5,0,True)
add(OUT_OUTRO,impact(1.8,0.9),0.85,0,False); add(OUT_OUTRO,drone(2.8,0.35),0.5,0,False)
add(OUT_OUTRO+0.2,whoosh(0.5,False,300,5000,0.5),0.4,0,False)
add(OUT_OUTRO+0.75,pop(600,0.7),0.9,0,False); add(OUT_OUTRO+0.77,seq([1047,1568,2093],0.07,1.2,0.5),0.8,0,False)
def build_voice():
    A=B.load_audio(); segs=B.segments(); parts=[]
    for k,a,b in segs:
        if k=='live': n=int(round((b-a)*FPS)); parts.append(A[int(a*SR):int(a*SR)+int(n/FPS*SR)])
        elif k=='question': parts.append(np.zeros((int(B.QLEN*FPS)*SR//FPS,2),np.float32))
        elif k=='title': parts.append(np.zeros((int(B.TITLE*FPS)*SR//FPS,2),np.float32))
        else: parts.append(np.zeros((int(B.OUTRO*FPS)*SR//FPS,2),np.float32))
    return np.concatenate(parts)
v=build_voice(); total=len(v)/SR; print('voice dur',total)
n=len(v)+SR*2
# voice envelope for ducking
mono=np.abs(v.mean(axis=1)); k=int(0.06*SR); envv=np.convolve(mono,np.ones(k)/k,'same'); envv=np.convolve(envv,np.ones(k*2)/(k*2),'same')
envn=np.clip(envv/ (np.percentile(envv,95)+1e-9),0,1); duck=1-0.55*envn
fxL=np.zeros(n); fxR=np.zeros(n); bigL=np.zeros(n); bigR=np.zeros(n)
for t,sig,g,pan,dk in fx:
    i=max(0,int(t*SR)); m=min(len(sig),n-i); s=sig[:m]*g
    gl=math.cos((pan+1)*math.pi/4); gr=math.sin((pan+1)*math.pi/4)
    if dk: s=s*duck[i:i+m] if i+m<=len(duck) else s
    (fxL if True else bigL)[i:i+m]+=s*gl*1.41; (fxR)[i:i+m]+=s*gr*1.41
mix=np.zeros((n,2),np.float32); mix[:len(v)]+=v*1.0
mix[:,0]+=fxL*0.42; mix[:,1]+=fxR*0.42
mix=mix[:int(total*SR)]
w=wave.open('build/audio_ep3.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes()); w.close(); print('peak',np.abs(mix).max())
