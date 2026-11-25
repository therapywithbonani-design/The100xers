import numpy as np, subprocess
CLIPS="/tmp/claude-0/-home-user-The100xers/3dc716bb-8387-5a31-912b-63c195d92910/scratchpad/clips"
W,H=1080,1920
# per-clip: wb gains (r,g,b), exposure stops, shadow lift, sat, pre-filter (rotation/crop) applied on 4K source
P={
 "IMG_4905":dict(wb=(0.985,1.0,1.02),ev=-0.15,lift=0.02,sat=1.04,pre=""),
 "IMG_4902":dict(wb=(1.03,1.0,1.0),ev=0.10,lift=0.03,sat=1.02,pre=""),
 "IMG_4903":dict(wb=(0.945,1.0,1.07),ev=0.45,lift=0.05,sat=1.05,pre=""),
 "IMG_4901":dict(wb=(0.97,1.0,1.05),ev=0.45,lift=0.05,sat=1.05,pre=""),
 "IMG_4904":dict(wb=(0.985,1.0,1.03),ev=-0.05,lift=0.02,sat=1.04,pre=""),
 "IMG_4896":dict(wb=(0.98,1.0,1.03),ev=0.45,lift=0.05,sat=1.03,pre=""),
 "IMG_4890":dict(wb=(0.96,1.0,1.06),ev=0.05,lift=0.03,sat=0.96,pre="rotate=-3.8*PI/180:ow=iw:oh=ih,crop=iw/1.17:ih/1.17"),
 "IMG_4891":dict(wb=(0.965,1.02,1.03),ev=-0.05,lift=0.02,sat=0.94,pre=""),
 "IMG_4895":dict(wb=(0.97,1.0,1.04),ev=0.15,lift=0.03,sat=1.0,pre=""),
 "IMG_4893":dict(wb=(1,1,1),ev=0,lift=0.02,sat=1.0,pre=""),
}
def vf(name, extra=""):
    p=P[name]["pre"]
    chain=[c for c in [p, "scale=1080:1920:flags=lanczos", "unsharp=5:5:0.45:5:5:0", extra] if c]
    return ",".join(chain)
def frame(name,t,graded=True):
    v=vf(name) if graded else "scale=1080:1920:flags=lanczos"
    raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",f"{CLIPS}/{name}.mov","-frames:v","1","-vf",v,"-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    a=np.frombuffer(raw,np.uint8).reshape(H,W,3)
    return grade(a,name) if graded else a
def s2l(x): return np.where(x<=0.04045,x/12.92,((x+0.055)/1.055)**2.4)
def l2s(x): return np.where(x<=0.0031308,x*12.92,1.055*np.power(np.maximum(x,0),1/2.4)-0.055)
def grade(a,name):
    p=P[name]; x=a.astype(np.float32)/255.0
    lin=s2l(x)
    lin=lin*np.array(p["wb"],np.float32)*(2**p["ev"])
    # soft-knee highlight roll-off in linear (recovers ring/panel gradient instead of flat white)
    k=0.42; c=2.6; Lmax=max(p["wb"])*(2**p["ev"])
    u=np.clip((lin-k)/(Lmax-k),0,1)
    lin=np.where(lin>k, k+(0.955-k)*(1-np.exp(-c*u))/(1-np.exp(-c)), lin)
    lin=np.minimum(lin,0.985)
    s=l2s(lin)
    # shadow lift (toe) + gentle global S
    s=s+p["lift"]*(1-s)**3
    s=s+0.06*np.sin((s-0.5)*np.pi)*0.5*(1-np.abs(2*s-1))  # mild midtone contrast
    # saturation (luma preserving), global look: very slight clean warmth in mids, neutral highs
    Y=(0.2126*s[...,0]+0.7152*s[...,1]+0.0722*s[...,2])[...,None]
    s=Y+(s-Y)*p["sat"]*1.03
    mids=4*Y*(1-Y)
    s=s+mids*np.array([0.006,0.0,-0.006],np.float32)
    s=np.clip(s,0,1)
    return (s*255+np.random.uniform(-0.5,0.5,s.shape)).clip(0,255).astype(np.uint8)
