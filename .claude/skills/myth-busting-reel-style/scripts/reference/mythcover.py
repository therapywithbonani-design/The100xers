import numpy as np, cv2, math
from PIL import Image, ImageDraw
from mythlib import F, W, H, GREEN, GOLD, RED, WHITE, INK, sup, icon
rng=np.random.RandomState(21)
def shards_bg():
    S=4; h,w=H//S,W//S; yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    cx,cy=w*0.5,h*0.46
    pts=[(cx,cy)]
    for ring,(r,n) in enumerate([(0.10,6),(0.22,9),(0.38,12),(0.58,14),(0.85,16)]):
        for k in range(n):
            a=(k/n)*2*math.pi+rng.uniform(-0.25,0.25)+ring*0.3; rr=r*h*rng.uniform(0.85,1.15); pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    pts=np.array(pts,np.float32); d=((xx[...,None]-pts[:,0])**2+(yy[...,None]-pts[:,1])**2); ids=d.argmin(axis=2)
    tone=rng.uniform(-1,1,len(pts)).astype(np.float32)
    base0=np.array([12,92,64],np.float32); base1=np.array([6,40,29],np.float32)
    r=np.hypot((xx-cx)/(w/2),(yy-cy)/(h/1.6)); r=np.clip(r,0,1.3)
    g=(base0*(1-np.clip(r,0,1))[...,None]+base1*np.clip(r,0,1)[...,None])
    g=g*(1+0.13*tone[ids])[...,None]
    # cracks: cell boundaries
    e=np.zeros((h,w),np.float32); e[:,1:]+= (ids[:,1:]!=ids[:,:-1]); e[1:,:]+= (ids[1:,:]!=ids[:-1,:]); e=np.clip(e,0,1)
    e=cv2.GaussianBlur(e,(0,0),0.8); fade=np.clip(1.25-r,0,1)
    g=g+ (e*fade*95)[...,None]*np.array([0.85,1.0,0.9],np.float32)
    big=cv2.resize(g,(W,H),interpolation=cv2.INTER_CUBIC)
    # impact glow
    yy2,xx2=np.mgrid[0:H,0:W].astype(np.float32); rr=np.hypot(xx2-W*0.5,yy2-H*0.46)/(W*0.55); glow=np.exp(-rr**2*2.2)[...,None]*np.array([40,70,55],np.float32)
    big=big+glow; vig=(1-0.35*np.clip(np.hypot((xx2-W/2)/(W/2),(yy2-H/2)/(H/2))-0.45,0,1)**1.4)[...,None]
    return np.clip(big*vig,0,255)
def person_layer(frame_png,mask_png,ymax=0.70,xclip=0.05,width=1090):
    im=cv2.imread(frame_png); m=cv2.imread(mask_png,0).astype(np.float32)/255
    h,w=m.shape; m[int(ymax*h):]=0; m[:,:int(xclip*w)]=0
    m=(m>0.5).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m); big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(lab==big).astype(np.uint8)
    ff=(1-m).copy(); mk=np.zeros((h+2,w+2),np.uint8); cv2.floodFill(ff,mk,(0,0),2); m=np.where(ff==1,1,m).astype(np.uint8)
    a=cv2.GaussianBlur(m.astype(np.float32),(0,0),2.5); a=np.clip((a-0.5)*3+0.5,0,1)
    ys,xs=np.where(a>0.1); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    rgb=im[y0:y1,x0:x1,::-1].astype(np.float32); al=a[y0:y1,x0:x1]
    sc=width/rgb.shape[1]; rgb=cv2.resize(rgb,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA); al=cv2.resize(al,(rgb.shape[1],rgb.shape[0]))
    pad=44; R=np.zeros((rgb.shape[0]+2*pad,rgb.shape[1]+2*pad,3),np.float32); A=np.zeros(R.shape[:2],np.float32); R[pad:-pad,pad:-pad]=rgb; A[pad:-pad,pad:-pad]=al
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31,31)); dil=cv2.GaussianBlur(cv2.dilate((A*255).astype(np.uint8),k).astype(np.float32)/255,(0,0),1.4)
    sh=np.roll(cv2.GaussianBlur(cv2.dilate((A*255).astype(np.uint8),k).astype(np.float32)/255,(0,0),18),18,axis=0)*0.5
    return R,A,dil,sh
def paste(base,R,A,dil,sh,x,y):
    h,w=A.shape; ya,yb,xa,xb=max(0,y),min(H,y+h),max(0,x),min(W,x+w); sl=(slice(ya-y,yb-y),slice(xa-x,xb-x)); reg=base[ya:yb,xa:xb]
    reg*= (1-sh[sl])[...,None]; reg[:]=reg*(1-dil[sl])[...,None]+255*dil[sl][...,None]; reg[:]=reg*(1-A[sl])[...,None]+R[sl]*A[sl][...,None]
def text_layer(draw_fn):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); draw_fn(d); a=np.asarray(im,np.float32); return a[...,:3],a[...,3]/255.
def over(base,rgb,al,shadow=0.0):
    if shadow>0:
        sh=np.roll(cv2.GaussianBlur(al,(0,0),14),12,axis=0)*shadow; base*= (1-sh)[...,None]
    base[:]=base*(1-al)[...,None]+rgb*al[...,None]
def spaced(d,x,y,txt,font,fill,sp=0,anchor='ls'):
    for c in txt: d.text((x,y),c,font=font,fill=fill,anchor=anchor); x+=font.getlength(c)+sp
    return x
def extrude(d,x,y,txt,font,fill,depth,col,anchor='ms',sp=0):
    for i in range(depth,0,-1): d.text((x+i*0.9,y+i),txt,font=font,fill=col,anchor=anchor)
    d.text((x,y),txt,font=font,fill=fill,anchor=anchor)
def rot_layer(rgb,al,ang,center):
    M=cv2.getRotationMatrix2D(center,ang,1.0); a4=np.dstack([rgb*al[...,None],al]); r=cv2.warpAffine(a4,M,(W,H),flags=cv2.INTER_LINEAR)
    a=r[...,3]; return np.where(a[...,None]>1e-4,r[...,:3]/np.maximum(a[...,None],1e-4),0),a
def build(out):
    base=shards_bg()
    R,A,dil,sh=person_layer('myth/fr_13.1.png','myth/mask_13.1.png')
    ph,pw=A.shape; px=(W-pw)//2+10; py=H-ph+60
    DK=(5,34,24,255)
    # ---- title: tilted, 3D extruded, MYTH over BUSTING
    def t1(d):
        extrude(d,W/2,405,"MYTH",F(900,288),WHITE+(255,),20,DK)
        f2=F(900,170); sp=14; tw2=sum(f2.getlength(c)+sp for c in "BUSTING")-sp; x=W/2-tw2/2
        for c in "BUSTING":
            extrude(d,x+f2.getlength(c)/2,585,c,f2,GOLD+(255,),14,(120,78,10,255)); x+=f2.getlength(c)+sp
    rgb,al=text_layer(t1); rgb,al=rot_layer(rgb,al,3.0,(W/2,420))
    # ---- question card: two lines, tilted, MYTH tag, gold marker on "Guaranteed"
    def t2(d):
        x0,y0,w,h=95,700,890,300
        d.rounded_rectangle([x0,y0,x0+w,y0+h],52,fill=WHITE+(255,))
        d.rounded_rectangle([x0+34,y0-34,x0+34+196,y0+34],34,fill=RED+(255,)); d.text((x0+34+98,y0+1),"MYTH",font=F(900,44),fill=WHITE+(255,),anchor='mm')
        d.text((x0+52,y0+138),"High CGPA =",font=F(900,92),fill=INK+(255,),anchor='ls')
        f=F(900,64); g="Guaranteed"; gw=f.getlength(g); xx=x0+52; yy=y0+248
        d.rounded_rectangle([xx-12,yy-60,xx+gw+12,yy+16],16,fill=GOLD+(255,)); d.text((xx,yy),g,font=f,fill=INK+(255,),anchor='ls')
        d.text((xx+gw+18,yy),"admission?",font=f,fill=(14,110,72,255),anchor='ls')
    rgb2,al2=text_layer(t2); rgb2,al2=rot_layer(rgb2,al2,-3.0,(W/2,850))
    paste(base,R,A,dil,sh,px,py)
    over(base,rgb,al,0.5); over(base,rgb2,al2,0.45)
    # ---- BUSTED stamp overlapping the card corner
    st=Image.new('RGBA',(520,170),(0,0,0,0)); d=ImageDraw.Draw(st)
    d.rounded_rectangle([6,6,514,164],20,fill=(255,255,255,235),outline=RED+(255,),width=10); d.rounded_rectangle([22,22,498,148],10,outline=RED+(255,),width=3)
    d.text((260,92),"BUSTED",font=F(900,112),fill=RED+(255,),anchor='mm')
    st=st.resize((430,140),Image.LANCZOS).rotate(8,expand=True,resample=Image.BICUBIC); sa=np.asarray(st,np.float32)
    cv=np.zeros((H,W,3),np.float32); ca=np.zeros((H,W),np.float32); sx,sy=40,1060
    cv[sy:sy+sa.shape[0],sx:sx+sa.shape[1]]=sa[...,:3]; ca[sy:sy+sa.shape[0],sx:sx+sa.shape[1]]=sa[...,3]/255.
    over(base,cv,ca,0.4)
    Image.fromarray(np.clip(base,0,255).astype(np.uint8)).save(out)
if __name__=='__main__':
    build('/home/user/The100xers/myth/cover-myth-busting.png')
    im=cv2.imread('/home/user/The100xers/myth/cover-myth-busting.png'); cv2.imwrite('myth/cover_prev.png',cv2.resize(im,(540,960)))
