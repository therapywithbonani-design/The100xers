import numpy as np, cv2, math, re, subprocess
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
SRC="/root/.claude/uploads/75a718db-0e97-535e-9ec5-e09fe2bf5112/52a9e4b1-F83B2EE0-0785-4AC7-8410-D2718968B2B1.mp4"
FD='fonts/ttf/'
GREEN=(18,138,92); DGREEN=(10,52,38); GOLD=(242,182,50); RED=(226,58,64); WHITE=(255,255,255); INK=(16,38,29)
def F(w,s): return ImageFont.truetype(f'{FD}Inter-{w}.ttf',int(s))
def clip01(x): return max(0.,min(1.,x))
def smooth(x): x=clip01(x); return x*x*(3-2*x)
def back(x,k=1.7):
    x=clip01(x); return 1+(k+1)*(x-1)**3+k*(x-1)**2
def comp(base,rgb,a,top,left=0):
    h,w=a.shape; y0,x0=max(0,top),max(0,left); y1,x1=min(base.shape[0],top+h),min(base.shape[1],left+w)
    if y1<=y0 or x1<=x0: return
    sa=a[y0-top:y1-top,x0-left:x1-left,None]; sr=rgb[y0-top:y1-top,x0-left:x1-left]
    base[y0:y1,x0:x1]=base[y0:y1,x0:x1]*(1-sa)+sr*sa
# ---------------- grade: natural, slightly richer, soft highlights, gentle contrast
VIG=None
def init_grade():
    global VIG
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.hypot((xx-W/2)/(W/2),(yy-H*0.45)/(H/2)); VIG=(1-0.07*np.clip(r-0.5,0,1)**1.3)[...,None]
def grade(f,vig=None):
    x=f/255.0
    L=(x@np.array([.299,.587,.114],np.float32))[...,None]
    ch=x-L; sat=np.abs(ch).max(axis=2,keepdims=True)
    boost=1.05+0.20*np.clip(1-sat/0.45,0,1)           # vibrance: lift muted colours more than vivid ones
    x=L+ch*boost
    x=x+0.012                                          # lift deep shadows a touch
    x=0.47+(x-0.47)*1.045                              # very gentle contrast
    hi=np.clip(x-0.80,0,None); x=x-hi*0.45              # roll off bright whites (walls, table)
    x[...,0]*=1.012; x[...,2]*=0.99                    # tiny warmth
    return np.clip(x,0,1)*255.0*(VIG if vig is None else vig)
# ---------------- captions
CAP_SIZE=62; CAP_LH=94; CAP_W=940
def make_caption(markup):
    toks=[]
    for t in markup.split(' '):
        if t=='': continue
        m=re.match(r'^\*(.+)\*(\W*)$',t)
        toks.append((m.group(1)+m.group(2),True) if m else (t,False))
    f=F(700,CAP_SIZE); sp=f.getlength(' ')
    total=sum(f.getlength(t) for t,_ in toks)+sp*(len(toks)-1)
    if total<=CAP_W or len(toks)<2: lines=[toks]
    else:
        best=None
        for i in range(1,len(toks)):
            a=sum(f.getlength(t) for t,_ in toks[:i])+sp*(i-1); b=sum(f.getlength(t) for t,_ in toks[i:])+sp*(len(toks)-i-1)
            m=max(a,b)
            if best is None or m<best[0]: best=(m,i)
        lines=[toks[:best[1]],toks[best[1]:]]
    h=len(lines)*CAP_LH+60; img=Image.new('RGBA',(W,h),(0,0,0,0)); d=ImageDraw.Draw(img); pill=Image.new('RGBA',(W,h),(0,0,0,0)); pd=ImageDraw.Draw(pill)
    y=30+CAP_LH*0.74
    for ln in lines:
        tw=sum(f.getlength(t) for t,_ in ln)+sp*(len(ln)-1); x=W/2-tw/2; xs=[]
        for t,k in ln: xs.append((x,x+f.getlength(t),t,k)); x+=f.getlength(t)+sp
        i=0
        while i<len(xs):
            if xs[i][3]:
                j=i
                while j+1<len(xs) and xs[j+1][3]: j+=1
                x0,x1=xs[i][0]-18,xs[j][1]+18
                pd.rounded_rectangle([x0,y-CAP_SIZE*0.86,x1,y+CAP_SIZE*0.30],22,fill=GREEN+(255,)); i=j+1
            else: i+=1
        for x0,x1,t,k in xs: d.text((x0,y),t,font=f,fill=WHITE+(255,),anchor='ls')
        y+=CAP_LH
    t_=np.asarray(img,np.float32); p_=np.asarray(pill,np.float32)
    ta=t_[...,3]/255.; pa=p_[...,3]/255.
    sh=np.roll(cv2.GaussianBlur(np.maximum(ta,pa),(0,0),9),5,axis=0)*0.55
    return dict(h=h,ta=ta,pa=pa,sh=sh,prgb=np.array(GREEN,np.float32))
def draw_caption(base,L,top,pin,pout):
    a=smooth(pin)*(1-smooth(pout)); 
    if a<=0.01: return
    dy=int((1-smooth(pin))*20+smooth(pout)*(-10)); h=L['h']
    sh=L['sh']*a; pa=L['pa']*a; ta=L['ta']*a
    y0=top+dy; ya,yb=max(0,y0),min(H,y0+h); sl=slice(ya-y0,yb-y0)
    reg=base[ya:yb,:]; reg*=(1-sh[sl])[...,None]
    reg[:]=reg*(1-pa[sl])[...,None]+L['prgb']*pa[sl][...,None]
    reg[:]=reg*(1-ta[sl])[...,None]+255*ta[sl][...,None]
# ---------------- stickers (flat white cards)
def sup(w,h,fn,ss=2):
    im=Image.new('RGBA',(w*ss,h*ss),(0,0,0,0)); d=ImageDraw.Draw(im); fn(d,w*ss,h*ss,ss); return im.resize((w,h),Image.LANCZOS)
def checkmark(d,cx,cy,s,col=WHITE):
    pts=[(cx-s*.22,cy+s*.02),(cx-s*.05,cy+s*.2),(cx+s*.24,cy-s*.18)]; wd=int(s*.13); d.line(pts,fill=col,width=wd,joint='curve')
    for p in (pts[0],pts[-1]): d.ellipse([p[0]-wd/2,p[1]-wd/2,p[0]+wd/2,p[1]+wd/2],fill=col)
def icon(d,kind,cx,cy,r):
    col={'check':GREEN,'x':RED,'person':GREEN,'cap':GREEN,'q':GOLD,'plus':GREEN,'star':GOLD,'brief':GREEN}[kind]
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
    if kind=='check': checkmark(d,cx,cy,r*2*0.95)
    elif kind=='x':
        w_=int(r*.26); d.line([cx-r*.36,cy-r*.36,cx+r*.36,cy+r*.36],fill=WHITE,width=w_); d.line([cx+r*.36,cy-r*.36,cx-r*.36,cy+r*.36],fill=WHITE,width=w_)
        for p in [(cx-r*.36,cy-r*.36),(cx+r*.36,cy+r*.36),(cx+r*.36,cy-r*.36),(cx-r*.36,cy+r*.36)]: d.ellipse([p[0]-w_/2,p[1]-w_/2,p[0]+w_/2,p[1]+w_/2],fill=WHITE)
    elif kind=='person':
        d.ellipse([cx-r*.2,cy-r*.5,cx+r*.2,cy-r*.1],fill=WHITE); d.pieslice([cx-r*.46,cy,cx+r*.46,cy+r*.9],180,360,fill=WHITE)
    elif kind=='cap':
        s=r*1.6; d.polygon([(cx,cy-s*.28),(cx+s*.5,cy-s*.04),(cx,cy+s*.18),(cx-s*.5,cy-s*.04)],fill=WHITE)
        d.polygon([(cx-s*.29,cy+s*.07),(cx-s*.29,cy+s*.3),(cx,cy+s*.44),(cx+s*.29,cy+s*.3),(cx+s*.29,cy+s*.07),(cx,cy+s*.21)],fill=WHITE)
    elif kind=='q': d.text((cx,cy+r*.06),"?",font=F(900,int(r*1.4)),fill=INK,anchor='mm')
    elif kind=='plus':
        w_=int(r*.26); d.line([cx-r*.45,cy,cx+r*.45,cy],fill=WHITE,width=w_); d.line([cx,cy-r*.45,cx,cy+r*.45],fill=WHITE,width=w_)
    elif kind=='star':
        pts=[]
        for i in range(10):
            rr=r*.62 if i%2==0 else r*.26; a=-math.pi/2+i*math.pi/5; pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
        d.polygon(pts,fill=INK)
    elif kind=='brief':
        d.rounded_rectangle([cx-r*.5,cy-r*.3,cx+r*.5,cy+r*.42],r*.1,fill=WHITE); d.rounded_rectangle([cx-r*.2,cy-r*.52,cx+r*.2,cy-r*.28],r*.08,outline=WHITE,width=int(r*.12))
        d.rectangle([cx-r*.5,cy+r*.02,cx+r*.5,cy+r*.1],fill=col)
def sticker(l1,l2=None,ic='check',tag=None,minw=0,l2size=36,l2w=600,l2col=(80,110,98,255)):
    f1=F(800,54); f2=F(l2w,l2size); tw=max(f1.getlength(l1),f2.getlength(l2) if l2 else 0)
    w=int(max(minw,tw+235)); h=(190 if not tag else 215)+(52 if l2size>40 else 0); pad=40
    def fn(d,W_,H_,ss):
        top=0 if not tag else 22*ss
        d.rounded_rectangle([pad*ss,pad*ss+top//2,(w-pad)*ss if False else W_-pad*ss,H_-pad*ss],40*ss,fill=(255,255,255,255))
        icon(d,ic,(pad+66)*ss,H_/2+ (top//4),44*ss)
        x=(pad+130)*ss; cy=H_/2+(top//4)
        if l2: d.text((x,cy-14*ss),l1,font=F(800,50*ss),fill=INK+(255,),anchor='ls'); d.text((x,cy+(34 if l2size<=40 else 52)*ss),l2,font=F(l2w,(34 if l2size<=40 else l2size)*ss),fill=l2col,anchor='ls')
        else: d.text((x,cy+2*ss),l1,font=F(800,52*ss),fill=INK+(255,),anchor='lm')
        if tag:
            tf=F(900,24*ss); tw_=tf.getlength(tag)+36*ss; tx=(pad+30)*ss; ty=pad*ss-4*ss
            d.rounded_rectangle([tx,ty,tx+tw_,ty+42*ss],21*ss,fill=RED+(255,)); d.text((tx+tw_/2,ty+21*ss),tag,font=tf,fill=WHITE+(255,),anchor='mm')
    img=sup(w+2*0,h,fn)
    a=np.asarray(img,np.float32); al=a[...,3]/255.
    sh=np.roll(cv2.GaussianBlur(al,(0,0),14),14,axis=0)*0.35
    return dict(rgb=a[...,:3]*al[...,None],a=al,sh=sh,w=w,h=h)
def draw_sticker(base,S,cx,cy,t,s,e):
    if not (s<=t<=e): return
    pin=(t-s)/0.34; pout=(e-t)/0.16; sc=back(pin,1.8)*smooth(pout)
    if sc<=0.03: return
    w,h=S['w'],S['h']; nw,nh=max(2,int(w*sc)),max(2,int(h*sc))
    pr=cv2.resize(S['rgb'],(nw,nh),interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_LINEAR); al=cv2.resize(S['a'],(nw,nh)); sh=cv2.resize(S['sh'],(nw,nh))
    y0=int(cy-nh/2); x0=int(cx-nw/2)
    ya,yb,xa,xb=max(0,y0),min(H,y0+nh),max(0,x0),min(W,x0+nw)
    if yb<=ya or xb<=xa: return
    sl=(slice(ya-y0,yb-y0),slice(xa-x0,xb-x0)); reg=base[ya:yb,xa:xb]
    reg*= (1-sh[sl][...,None]); reg[:]=reg*(1-al[sl][...,None])+pr[sl]
