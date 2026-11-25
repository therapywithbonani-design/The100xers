import subprocess, numpy as np, sys
for n in sys.argv[1:]:
    w,h=270,480
    raw=subprocess.run(["ffmpeg","-v","error","-i",n,"-vf",f"scale={w}:{h},fps=10","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    a=np.frombuffer(raw,np.uint8).reshape(-1,h,w,3).astype(np.float32)
    y=0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
    m=a.reshape(-1,3).mean(0)
    # neutral-ish pixels (low saturation, mid luma) for cast
    mx=a.max(-1); mn=a.min(-1); sat=(mx-mn)/(mx+1)
    sel=(sat<0.25)&(y>40)&(y<220)
    nm=a[sel].mean(0) if sel.sum()>100 else m
    clip=(y>250).mean()*100
    # shake: mean abs diff of grayscale between consecutive frames after small blur
    d=np.abs(np.diff(y[:,::4,::4],axis=0)).mean(axis=(1,2))
    print(f"{n:14s} frames={len(a)} meanY={y.mean():5.1f} p5={np.percentile(y,5):5.1f} p99={np.percentile(y,99):5.1f} clip%={clip:4.2f} neutralRGB={nm.round(1)} R/G={nm[0]/nm[1]:.3f} B/G={nm[2]/nm[1]:.3f} motion={d.mean():.1f}±{d.std():.1f}")
