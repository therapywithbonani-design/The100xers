import re,sys,numpy as np
for f in sys.argv[1:]:
    xs=[];ys=[];rs=[]
    for line in open(f):
        if line.startswith("Frame"):
            ms=re.findall(r"LM (\-?\d+) (\-?\d+) \d+ \d+ \d+ ([\d.]+) ([\d.]+)",line)
            ms=[m for m in ms if float(m[3])<0.3] or ms
            if ms:
                v=np.array([[float(a),float(b)] for a,b,_,_ in ms]); xs.append(np.median(v[:,0])); ys.append(np.median(v[:,1]))
            else: xs.append(0);ys.append(0)
    x=np.cumsum(xs);y=np.cumsum(ys)
    k=9
    def hf(p):
        s=np.convolve(np.pad(p,k//2,mode='edge'),np.ones(k)/k,'valid'); return np.abs(p-s).mean()
    print(f.split('/')[-1], f"path dx={x[-1]:.0f} dy={y[-1]:.0f}px@540w  jitter x={hf(x):.2f} y={hf(y):.2f}px")
