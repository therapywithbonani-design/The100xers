import numpy as np, cv2, subprocess, math, sys, os, wave
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
PSHIFT=0; TSHIFT=0; PILLY=1290
SRC="/root/.claude/uploads/75a718db-0e97-535e-9ec5-e09fe2bf5112/a5d7b262-F88A535C-5A91-4E52-8A5B-6FD8B4763B13.mp4"
FD='fonts/ttf/'; OUT='/home/user/The100xers/ep1/'
YEL=(255,210,31); RED=(255,84,84); WHITE=(255,255,255); NAVY=(22,36,84)
SERIES1,SERIES2="ASK THE","CO-FOUNDER"; EPNUM="EPISODE 3"; TAG1="Ask The Co-Founder"; TAG2="EPISODE 3"
def font(w,s): return ImageFont.truetype(f'{FD}Montserrat-{w}.ttf',int(s))
def clip01(x): return max(0.,min(1.,x))
def smooth(x): x=clip01(x); return x*x*(3-2*x)
def back(x,k=1.9):
    x=clip01(x); return 1+(k+1)*(x-1)**3+k*(x-1)**2
def pil2np(im): return np.asarray(im,dtype=np.float32)
# ------------------------------------------------------------ stickers
def finish(im,border=12,pad=50):
    a=np.asarray(im)[...,3]; h,w=a.shape
    can=np.zeros((h+2*pad,w+2*pad,4),np.uint8); can[pad:pad+h,pad:pad+w]=np.asarray(im)
    al=can[...,3]
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*border+1,2*border+1))
    dil=cv2.GaussianBlur(cv2.dilate(al,k),(0,0),1.3)
    sh=cv2.GaussianBlur(cv2.dilate(al,k),(0,0),12); sh=np.roll(sh,14,axis=0)*0.5
    out=np.zeros(can.shape,np.float32)
    out[...,:3]=0; out[...,3]=sh
    # white outline
    A=dil/255.; out[...,:3]=out[...,:3]*(1-A[...,None])+255*A[...,None]; out[...,3]=out[...,3]*(1-A)+255*A
    B=al/255.; out[...,:3]=out[...,:3]*(1-B[...,None])+can[...,:3]*B[...,None]; out[...,3]=out[...,3]*(1-B)+255*B
    return out
def sup(w,h,fn,ss=2):
    im=Image.new('RGBA',(w*ss,h*ss),(0,0,0,0)); d=ImageDraw.Draw(im); fn(d,w*ss,h*ss,ss); return im.resize((w,h),Image.LANCZOS)
def rr_mask(w,h,r,ss=2):
    m=Image.new('L',(w*ss,h*ss),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w*ss-1,h*ss-1],r*ss,fill=255); return m.resize((w,h),Image.LANCZOS)
def flag(kind,w=420,h=280):
    ss=2
    im=Image.new('RGBA',(w*ss,h*ss),(255,255,255,255)); d=ImageDraw.Draw(im); W2,H2=w*ss,h*ss
    if kind=='it':
        for i,c in enumerate([(0,146,70),(255,255,255),(206,43,55)]): d.rectangle([i*W2//3,0,(i+1)*W2//3,H2],fill=c)
    elif kind=='de':
        for i,c in enumerate([(0,0,0),(221,0,0),(255,206,0)]): d.rectangle([0,i*H2//3,W2,(i+1)*H2//3],fill=c)
    elif kind=='in':
        for i,c in enumerate([(255,153,51),(255,255,255),(19,136,8)]): d.rectangle([0,i*H2//3,W2,(i+1)*H2//3],fill=c)
        cx,cy,r=W2//2,H2//2,int(H2*0.15); d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=(0,0,128),width=6)
        for k in range(24):
            a=k*math.pi/12; d.line([cx,cy,cx+r*math.cos(a),cy+r*math.sin(a)],fill=(0,0,128),width=3)
        d.ellipse([cx-8,cy-8,cx+8,cy+8],fill=(0,0,128))
    elif kind=='uk':
        d.rectangle([0,0,W2,H2],fill=(1,33,105))
        for p in [((0,0),(W2,H2)),((0,H2),(W2,0))]: d.line(p,fill=(255,255,255),width=int(H2*.2))
        for p in [((0,0),(W2,H2)),((0,H2),(W2,0))]: d.line(p,fill=(200,16,46),width=int(H2*.07))
        d.rectangle([0,H2*.5-H2*.17,W2,H2*.5+H2*.17],fill=(255,255,255)); d.rectangle([W2*.5-H2*.17,0,W2*.5+H2*.17,H2],fill=(255,255,255))
        d.rectangle([0,H2*.5-H2*.1,W2,H2*.5+H2*.1],fill=(200,16,46)); d.rectangle([W2*.5-H2*.1,0,W2*.5+H2*.1,H2],fill=(200,16,46))
    im=im.resize((w,h),Image.LANCZOS)
    # gloss
    g=Image.new('RGBA',(w,h),(0,0,0,0)); gd=ImageDraw.Draw(g); gd.polygon([(0,0),(w*.55,0),(w*.25,h),(0,h)],fill=(255,255,255,38))
    im=Image.alpha_composite(im,g); im.putalpha(rr_mask(w,h,26)); return im
def scales(d,cx,cy,s,col):
    d.rectangle([cx-s*.035,cy-s*.42,cx+s*.035,cy+s*.40],fill=col)
    d.rounded_rectangle([cx-s*.26,cy+s*.37,cx+s*.26,cy+s*.46],s*.03,fill=col)
    d.ellipse([cx-s*.07,cy-s*.5,cx+s*.07,cy-s*.36],fill=col)
    d.line([cx-s*.55,cy-s*.33,cx+s*.55,cy-s*.33],fill=col,width=max(2,int(s*.055)))
    for px in (cx-s*.55,cx+s*.55):
        d.line([px,cy-s*.33,px-s*.26,cy+s*.14],fill=col,width=max(2,int(s*.022)))
        d.line([px,cy-s*.33,px+s*.26,cy+s*.14],fill=col,width=max(2,int(s*.022)))
        d.pieslice([px-s*.27,cy,px+s*.27,cy+s*.28],0,180,fill=col)
def checkmark(d,cx,cy,s,col=(255,255,255)):
    pts=[(cx-s*.22,cy+s*.02),(cx-s*.05,cy+s*.2),(cx+s*.24,cy-s*.18)]; wd=int(s*.13)
    d.line(pts,fill=col,width=wd,joint='curve')
    for p in (pts[0],pts[-1]): d.ellipse([p[0]-wd/2,p[1]-wd/2,p[0]+wd/2,p[1]+wd/2],fill=col)
def circ_icon(kind,size=230):
    def f(d,w,h,ss):
        if kind=='x':
            d.ellipse([0,0,w-1,h-1],fill=(235,40,48)); s=w*.2; 
            d.line([w*.3,h*.3,w*.7,h*.7],fill=WHITE,width=int(w*.13)); d.line([w*.7,h*.3,w*.3,h*.7],fill=WHITE,width=int(w*.13))
            for p in [(w*.3,h*.3),(w*.7,h*.7),(w*.7,h*.3),(w*.3,h*.7)]: d.ellipse([p[0]-w*.065,p[1]-w*.065,p[0]+w*.065,p[1]+w*.065],fill=WHITE)
        elif kind=='check':
            d.ellipse([0,0,w-1,h-1],fill=(36,190,96)); checkmark(d,w/2,h/2,w*1.0)
        elif kind=='law':
            d.ellipse([0,0,w-1,h-1],fill=YEL); scales(d,w/2,h*.5,w*.62,NAVY)
    return sup(size,size,f)
def llb_sticker():
    def f(d,w,h,ss):
        d.rounded_rectangle([0,0,w-1,h-1],34*ss,fill=NAVY); d.rounded_rectangle([10*ss,10*ss,w-11*ss,h-11*ss],26*ss,outline=YEL,width=5*ss)
        scales(d,w*.2,h*.5,h*.62,YEL)
        d.text((w*.40,h*.46),"LLB",font=font(900,128*ss),fill=YEL,anchor='lm')
        d.text((w*.41,h*.80),"LAW DEGREE",font=font(700,32*ss),fill=WHITE,anchor='lm')
    return sup(600,250,f)
def council_sticker():
    def f(d,w,h,ss):
        bh=int(h*.80)
        d.rounded_rectangle([0,0,w-1,bh],34*ss,fill=NAVY); d.rounded_rectangle([10*ss,10*ss,w-11*ss,bh-10*ss],26*ss,outline=YEL,width=5*ss)
        scales(d,w*.15,bh*.5,bh*.62,YEL)
        d.text((w*.29,bh*.36),"BAR COUNCIL",font=font(900,70*ss),fill=WHITE,anchor='lm')
        d.text((w*.29,bh*.70),"OF INDIA",font=font(900,70*ss),fill=YEL,anchor='lm')
        pw,ph=w*.5,h*.26; px,py=w*.5-pw/2,h-ph
        d.rounded_rectangle([px,py,px+pw,py+ph],ph/2,fill=(36,190,96),outline=WHITE,width=4*ss)
        checkmark(d,px+ph*.62,py+ph*.52,ph*.95); d.text((px+ph*1.15,py+ph*.54),"RECOGNISED",font=font(800,36*ss),fill=WHITE,anchor='lm')
    return sup(780,350,f)

def star_pts(cx,cy,r,n=5,inner=0.382,rot=-math.pi/2):
    pts=[]
    for i in range(n*2):
        rr=r if i%2==0 else r*inner; a=rot+i*math.pi/n; pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    return pts
def flag2(kind,w=420,h=280):
    ss=2; im=Image.new('RGBA',(w*ss,h*ss),(255,255,255,255)); d=ImageDraw.Draw(im); W2,H2=w*ss,h*ss
    if kind=='eu':
        d.rectangle([0,0,W2,H2],fill=(0,51,153))
        for k in range(12):
            a=k*math.pi/6; cx=W2/2+H2*.32*math.cos(a); cy=H2/2+H2*.32*math.sin(a); d.polygon(star_pts(cx,cy,H2*.065),fill=(255,204,0))
    elif kind=='sg':
        d.rectangle([0,0,W2,H2//2],fill=(237,41,57)); d.rectangle([0,H2//2,W2,H2],fill=(255,255,255))
        cx,cy,r=W2*.2,H2*.25,H2*.17; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(255,255,255)); r2=r*.82; d.ellipse([cx-r2+r*.38,cy-r2,cx+r2+r*.38,cy+r2],fill=(237,41,57))
        sx,sy=W2*.335,H2*.25
        for k in range(5):
            a=-math.pi/2+k*2*math.pi/5; d.polygon(star_pts(sx+H2*.11*math.cos(a),sy+H2*.11*math.sin(a),H2*.04),fill=(255,255,255))
    elif kind=='hk':
        d.rectangle([0,0,W2,H2],fill=(222,41,16)); cx,cy=W2/2,H2/2
        for k in range(5):
            a=-math.pi/2+k*2*math.pi/5; px,py=cx+H2*.16*math.cos(a),cy+H2*.16*math.sin(a)
            pet=Image.new('RGBA',(W2,H2),(0,0,0,0)); pd=ImageDraw.Draw(pet); pd.ellipse([px-H2*.12,py-H2*.07,px+H2*.12,py+H2*.07],fill=(255,255,255,255))
            pet=pet.rotate(-math.degrees(a)-0,center=(px,py)); im=Image.alpha_composite(im,pet); d=ImageDraw.Draw(im)
            d.ellipse([cx+H2*.2*math.cos(a+.45)-4,cy+H2*.2*math.sin(a+.45)-4,cx+H2*.2*math.cos(a+.45)+4,cy+H2*.2*math.sin(a+.45)+4],fill=(222,41,16))
        d.ellipse([cx-H2*.03,cy-H2*.03,cx+H2*.03,cy+H2*.03],fill=(222,41,16))
    if kind=='fr':
        for i,c in enumerate([(0,35,149),(255,255,255),(237,41,57)]): d.rectangle([i*W2//3,0,(i+1)*W2//3,H2],fill=c)
    elif kind=='se':
        d.rectangle([0,0,W2,H2],fill=(0,106,167)); d.rectangle([W2*.30,0,W2*.30+H2*.2,H2],fill=(254,204,0)); d.rectangle([0,H2*.4,W2,H2*.6],fill=(254,204,0))
    elif kind=='de':
        for i,c in enumerate([(0,0,0),(221,0,0),(255,206,0)]): d.rectangle([0,i*H2//3,W2,(i+1)*H2//3],fill=c)
    im=im.resize((w,h),Image.LANCZOS); g=Image.new('RGBA',(w,h),(0,0,0,0)); gd=ImageDraw.Draw(g); gd.polygon([(0,0),(w*.55,0),(w*.25,h),(0,h)],fill=(255,255,255,38))
    im=Image.alpha_composite(im,g); im.putalpha(rr_mask(w,h,26)); return im
def bars(d,cx,cy,s,col):
    for i,hh in enumerate((.35,.6,.9)):
        x=cx-s*.42+i*s*.3; d.rounded_rectangle([x,cy+s*.45-s*hh,x+s*.22,cy+s*.45],s*.03,fill=col)
    d.line([cx-s*.5,cy+s*.05,cx-s*.1,cy-s*.2,cx+s*.1,cy-s*.05,cx+s*.5,cy-s*.5],fill=col,width=max(2,int(s*.05)),joint='curve')
    d.polygon([(cx+s*.52,cy-s*.58),(cx+s*.52,cy-s*.30),(cx+s*.28,cy-s*.5)],fill=col)
def coin(d,cx,cy,r,col=YEL,ink=NAVY,txt='$',ss=2):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col,outline=ink,width=max(2,int(r*.1))); d.text((cx,cy+r*.04),txt,font=font(900,int(r*1.25)),fill=ink,anchor='mm')
def cap(d,cx,cy,s,col):
    d.polygon([(cx,cy-s*.3),(cx+s*.55,cy-s*.05),(cx,cy+s*.2),(cx-s*.55,cy-s*.05)],fill=col)
    d.polygon([(cx-s*.32,cy+s*.08),(cx-s*.32,cy+s*.36),(cx,cy+s*.5),(cx+s*.32,cy+s*.36),(cx+s*.32,cy+s*.08),(cx,cy+s*.24)],fill=col)
    d.line([cx+s*.5,cy-s*.02,cx+s*.5,cy+s*.35],fill=col,width=max(2,int(s*.04)))
def calendar(d,cx,cy,s,col,ink):
    d.rounded_rectangle([cx-s*.45,cy-s*.4,cx+s*.45,cy+s*.5],s*.08,fill=col)
    d.rectangle([cx-s*.45,cy-s*.4,cx+s*.45,cy-s*.12],fill=ink)
    for x in (-.25,.25): d.rounded_rectangle([cx+x*s-s*.04,cy-s*.52,cx+x*s+s*.04,cy-s*.28],s*.03,fill=col)
    checkmark(d,cx,cy+s*.17,s*.55,ink)
def badge(w,h,draw_icon,lines,cols,sizes,tx=.3,ss=2):
    def f(d,W_,H_,ss):
        d.rounded_rectangle([0,0,W_-1,H_-1],34*ss,fill=NAVY); d.rounded_rectangle([10*ss,10*ss,W_-11*ss,H_-11*ss],26*ss,outline=YEL,width=5*ss)
        draw_icon(d,W_,H_,ss); n=len(lines)
        for i,(t,c,sz) in enumerate(zip(lines,cols,sizes)):
            d.text((W_*tx,H_*((i+1)/(n+1))),t,font=font(900,sz*ss),fill=c,anchor='lm')
    return sup(w,h,f)
def new_stickers():
    STICKERS['eu']=finish(flag2('eu')); STICKERS['sg']=finish(flag2('sg')); STICKERS['hk']=finish(flag2('hk'))
    STICKERS['econ']=finish(badge(640,250,lambda d,W_,H_,ss: bars(d,W_*.16,H_*.5,H_*.62,YEL),["ECONOMICS","HONOURS"],[WHITE,YEL],[64,64],tx=.31))
    STICKERS['lowbud']=finish(badge(700,230,lambda d,W_,H_,ss: coin(d,W_*.15,H_*.5,H_*.3),["LOW BUDGET"],[YEL],[66],tx=.28))
    STICKERS['boc']=finish(badge(760,260,lambda d,W_,H_,ss: cap(d,W_*.14,H_*.48,H_*.62,YEL),["BOCCONI","UNIVERSITY · ITALY"],[WHITE,YEL],[84,36],tx=.27))
    STICKERS['goodbud']=finish(badge(860,260,lambda d,W_,H_,ss: d.polygon(star_pts(W_*.12,H_*.5,H_*.34),fill=YEL),["GOOD BUDGET","+ STRONG PROFILE"],[WHITE,YEL],[64,50],tx=.24))
    def chart_icon(d,w,h,ss):
        d.ellipse([0,0,w-1,h-1],fill=YEL); bars(d,w/2,h/2,w*.5,NAVY)
    STICKERS['chart']=finish(sup(300,300,chart_icon),border=14)
    def consult_f(d,W_,H_,ss):
        d.rounded_rectangle([0,0,W_-1,H_-1],34*ss,fill=YEL); d.rounded_rectangle([10*ss,10*ss,W_-11*ss,H_-11*ss],26*ss,outline=NAVY,width=5*ss)
        calendar(d,W_*.15,H_*.5,H_*.6,NAVY,YEL)
        d.text((W_*.30,H_*.37),"BOOK A",font=font(900,70*ss),fill=NAVY,anchor='lm'); d.text((W_*.30,H_*.68),"CONSULTATION",font=font(900,64*ss),fill=NAVY,anchor='lm')
    STICKERS['consult']=finish(sup(840,260,consult_f))

def logo_sticker():
    im=Image.open('ep2/assets/logo.jpg').convert('RGB'); a=np.asarray(im).astype(np.int16)
    mask=(a.min(axis=2)<235); ys,xs=np.where(mask); im=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
    tw=600; th=int(im.height*tw/im.width); im=im.resize((tw,th),Image.LANCZOS)
    pad=34; w,h=tw+2*pad,th+2*pad
    card=Image.new('RGBA',(w,h),(255,255,255,255)); card.paste(im,(pad,pad)); card.putalpha(rr_mask(w,h,30)); return card

def medcross(d,cx,cy,r):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=WHITE); w_=r*.32; l=r*.62
    d.rounded_rectangle([cx-w_,cy-l,cx+w_,cy+l],r*.08,fill=(220,40,50)); d.rounded_rectangle([cx-l,cy-w_,cx+l,cy+w_],r*.08,fill=(220,40,50))
def speech(d,cx,cy,s,col,ink,txt='EN'):
    d.rounded_rectangle([cx-s*.5,cy-s*.4,cx+s*.5,cy+s*.3],s*.14,fill=col); d.polygon([(cx-s*.25,cy+s*.28),(cx-s*.05,cy+s*.28),(cx-s*.35,cy+s*.5)],fill=col)
    d.text((cx,cy-s*.05),txt,font=font(900,int(s*.42)),fill=ink,anchor='mm')
def new_stickers2():
    STICKERS['de_s']=finish(flag2('de',300,200),border=10,pad=40); STICKERS['fr_s']=finish(flag2('fr',300,200),border=10,pad=40); STICKERS['se_s']=finish(flag2('se',300,200),border=10,pad=40)
    STICKERS['de']=finish(flag2('de')); 
    STICKERS['mbbs']=finish(badge(640,250,lambda d,W_,H_,ss: medcross(d,W_*.16,H_*.5,H_*.33),["MBBS"],[YEL],[110],tx=.32))
    STICKERS['eng']=finish(badge(780,250,lambda d,W_,H_,ss: speech(d,W_*.14,H_*.5,H_*.62,YEL,NAVY),["ENGLISH","TAUGHT"],[WHITE,YEL],[64,64],tx=.27))

STICKERS={}
def build_stickers():
    STICKERS['llb']=finish(llb_sticker())
    STICKERS['it']=finish(flag('it')); STICKERS['de']=finish(flag('de'))
    STICKERS['in']=finish(flag('in')); STICKERS['uk']=finish(flag('uk'))
    STICKERS['council']=finish(council_sticker())
    STICKERS['check']=finish(circ_icon('check',250),border=14)
    STICKERS['law']=finish(circ_icon('law',300),border=14)
    STICKERS['x']=finish(circ_icon('x',170),border=10,pad=30)
    STICKERS['tick']=finish(circ_icon('check',170),border=10,pad=30)
    new_stickers(); new_stickers2(); STICKERS['logo']=finish(logo_sticker(),border=10)
# (key, start, end, centre(x,y), angle)  -- times in SOURCE seconds
POPS=[('de',7.90,9.05,(540,345),3),('mbbs',9.72,10.60,(540,335),-3),('de',10.64,12.26,(540,345),4),('x',11.0,12.26,(700,255),0),
 ('eng',12.30,13.15,(540,335),-3),('eu',16.22,17.35,(540,345),-3),('it',17.95,19.0,(540,345),4),('tick',18.4,19.0,(690,255),0),
 ('eng',19.62,21.40,(540,335),-3),('tick',21.0,21.40,(690,255),0),
 ('de_s',21.62,25.9,(215,345),-5),('fr_s',22.26,25.9,(540,345),3),('se_s',22.94,25.9,(865,345),-4),
 ('mbbs',26.58,29.20,(540,335),2),('x',27.0,29.20,(845,240),0)]
def draw_sticker(base,key,t,s,e,c,ang):
    if not (s<=t<=e): return
    sp=STICKERS[key]; h,w=sp.shape[:2]
    pin=(t-s)/0.40; pout=(e-t)/0.20
    sc=back(pin)*smooth(pout) if key not in('x','tick') else back(pin,2.6)*smooth(pout)
    if sc<=0.02: return
    a=math.radians(0)
    rot=ang+(1-clip01(pin))*(-14 if ang<=0 else 14)
    cy=c[1]+math.sin((t-s)*4.2)*6
    M=cv2.getRotationMatrix2D((w/2,h/2),rot,sc); M[0,2]+=c[0]-w/2; M[1,2]+=cy-h/2
    # warp only the local box for speed
    R=int(math.hypot(w,h)*sc*0.55)+4; x0,y0=int(c[0])-R,int(cy)-R
    M2=M.copy(); M2[0,2]-=x0; M2[1,2]-=y0
    prem=sp.copy(); prem[...,:3]*=prem[...,3:4]/255.
    wr=cv2.warpAffine(prem,M2,(2*R,2*R),flags=cv2.INTER_LINEAR,borderValue=(0,0,0,0))
    xa,ya=max(0,x0),max(0,y0); xb,yb=min(W,x0+2*R),min(H,y0+2*R)
    if xb<=xa or yb<=ya: return
    sub=wr[ya-y0:yb-y0,xa-x0:xb-x0]; al=sub[...,3:4]/255.
    base[ya:yb,xa:xb]=base[ya:yb,xa:xb]*(1-al)+sub[...,:3]
# ------------------------------------------------------------ captions
PHRASES=[("SO EK AUR|SAWAAL HAI NA,",0.00,2.20),("KISKA?",2.32,3.10),("I THINK",3.14,3.80),
 ("HE IS ASKING THAT,",5.00,5.90),("RELATED TO *GERMANY*|AGAIN,",7.42,9.05),("WANT TO DO|*MBBS* IN *GERMANY*,",9.10,10.60),
 ("NOT *POSSIBLE*",10.64,11.66),("WHEN YOU ARE|THINKING *ENGLISH*|*TAUGHT*",11.68,13.35),
 ("WHEN YOU ARE|THINKING *ENGLISH*|*TAUGHT*,",13.58,15.45),("PROBABLY IN *EUROPE*,",15.58,16.80),
 ("ONE COUNTRY YOU|CAN ALWAYS PICK",16.84,18.15),("THAT IS *ITALY*",18.18,18.84),("THEY HAVE PLENTY OF|*ENGLISH* *TAUGHT*|PROGRAMS,",18.84,21.45),
 ("BUT *GERMANY*,|*FRANCE*, *SWEDEN*,",21.50,23.32),("ALL THESE|COUNTRIES ARE|PROVIDING",23.36,24.96),("IN THEIR *LOCAL*|*LANGUAGE*",24.96,25.95),
 ("NO *MBBS* IN THESE|COUNTRIES",26.40,27.82),("IN *ENGLISH*|*LANGUAGE*",27.82,29.20)]
LH=122
def make_layer(text,size=84,kw=100,w=W,h=520,cy=260,col_kw=YEL):
    img=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(img)
    lines=text.split('|'); n=len(lines); y=cy-(n*LH)/2+LH*0.78
    for ln in lines:
        toks=[]
        for t in ln.split(' '):
            c=WHITE; sz=size
            import re as _re
            mm=_re.match(r'^([*!])(.+?)\1(\W*)$',t)
            if mm: c=col_kw if mm.group(1)=='*' else RED; sz=kw; t=mm.group(2)+mm.group(3)
            toks.append((t,c,font(800,sz)))
        sp=font(800,size).getlength(' ')
        tw=sum(f.getlength(t) for t,_,f in toks)+sp*(len(toks)-1)
        if tw>980:
            fct=980/tw; toks=[(t,c,font(800,f.size*fct)) for t,c,f in toks]; sp=sp*fct; tw=sum(f.getlength(t) for t,_,f in toks)+sp*(len(toks)-1)
        x=w/2-tw/2
        for t,c,f in toks:
            d.text((x,y),t,font=f,fill=c+(255,),anchor='ls'); x+=f.getlength(t)+sp
        y+=LH
    arr=np.asarray(img,np.float32); ta=arr[...,3]/255.; rgb=arr[...,:3]
    s1=np.roll(cv2.GaussianBlur(ta,(0,0),13),12,axis=0)*0.9; s2=np.roll(cv2.GaussianBlur(ta,(0,0),2.5),5,axis=0)*0.75
    sa=1-(1-np.clip(s1,0,1))*(1-s2)
    return dict(rgb=rgb,ta=ta,sa=sa,h=h,w=w)
rng=np.random.RandomState(7)
def make_noise(h,w):
    n=cv2.GaussianBlur(rng.rand(h//4,w//4).astype(np.float32),(0,0),5); n=cv2.resize(n,(w,h),interpolation=cv2.INTER_CUBIC)
    n=(n-n.min())/(n.max()-n.min()); return n
def draw_layer(base,L,top,noise,pin=1.,pout=0.):
    # smoke reveal: pin 0..1 in, pout 0..1 out
    ta,sa,rgb=L['ta'],L['sa'],L['rgb']; smoke=None
    if pin<1: q=pin; ex=(1-q)*30; blur=(1-q)**1.5*11
    elif pout>0: q=1-pout; ex=-pout*45; blur=pout*13
    else: q=1; ex=0; blur=0
    if q<1:
        mult=np.clip((q-noise*0.55)/0.45,0,1)
        sm=cv2.GaussianBlur(ta,(0,0),26)*noise*(1-q)*1.5; smoke=np.clip(sm,0,0.7)
        ta=ta*mult; sa=sa*mult
        if blur>0.5: ta=cv2.GaussianBlur(ta,(0,0),blur); sa=cv2.GaussianBlur(sa,(0,0),blur*0.6)
        if abs(ex)>0.5:
            M=np.float32([[1,0,0],[0,1,ex]]); h,w=ta.shape
            ta=cv2.warpAffine(ta,M,(w,h)); sa=cv2.warpAffine(sa,M,(w,h)); rgb=cv2.warpAffine(rgb,M,(w,h))
            if smoke is not None: smoke=cv2.warpAffine(smoke,M,(w,h))
    h,w=ta.shape; y0=top; ya=max(0,y0); yb=min(H,y0+h)
    reg=base[ya:yb,:w]; sl=slice(ya-y0,yb-y0)
    reg*= (1-sa[sl])[...,None]
    if smoke is not None: reg[:]=reg*(1-smoke[sl])[...,None]+np.array([215,215,222],np.float32)*smoke[sl][...,None]
    reg[:]=reg*(1-ta[sl])[...,None]+rgb[sl]*ta[sl][...,None]
# ------------------------------------------------------------ text 3D / title card
def text3d(txt,size,w=W,h=None,extr=14,wt=900):
    f=font(wt,size); tw=f.getlength(txt); h=h or int(size*1.5)
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im); x=w/2-tw/2; y=h/2
    for i in range(extr,0,-1):
        c=(94,40,140) if i>extr*0.5 else (230,57,70)
        d.text((x+i*.7,y+i),txt,font=f,fill=c+(255,),anchor='lm',stroke_width=4,stroke_fill=c+(255,))
    d.text((x,y),txt,font=f,fill=(40,16,70,255),anchor='lm',stroke_width=6,stroke_fill=(40,16,70,255))
    d.text((x,y),txt,font=f,fill=(255,255,255,255),anchor='lm')
    a=np.asarray(im,np.float32); al=a[...,3]/255.
    sh=np.roll(cv2.GaussianBlur(al,(0,0),14),22,axis=0)*0.4
    out=np.zeros_like(a); out[...,:3]=a[...,:3]*al[...,None]; out[...,3]=1-(1-al)*(1-sh)  # premult rgb, alpha incl shadow
    out[...,:3]=out[...,:3]  # shadow is black => premult 0
    return out
SUN=None
def sunburst():
    global SUN
    S=2900; yy,xx=np.mgrid[0:S,0:S].astype(np.float32); ang=np.arctan2(yy-S/2,xx-S/2)
    k=((ang/(2*math.pi)*28)%1.0)<0.5
    c1=np.array([18,96,60],np.float32); c2=np.array([7,56,36],np.float32)
    img=np.where(k[...,None],c1,c2); r=np.hypot(yy-S/2,xx-S/2)/(S/2)
    img=img*(1-0.22*np.clip(1-r*1.8,0,1))[...,None]+255*0.07*np.clip(1-r*2.2,0,1)[...,None]
    SUN=np.clip(img,0,255).astype(np.uint8)
def sun_frame(t):
    M=cv2.getRotationMatrix2D((SUN.shape[1]/2,SUN.shape[0]/2),t*5,1.0); M[0,2]+=W/2-SUN.shape[1]/2; M[1,2]+=H*0.42-SUN.shape[0]/2
    return cv2.warpAffine(SUN,M,(W,H),flags=cv2.INTER_LINEAR).astype(np.float32)
def prep_cut(path,width=1040,scale=None):
    c=cv2.imread(path,cv2.IMREAD_UNCHANGED); al=c[...,3]; ys,xs=np.where(al>20)
    c=c[ys.min():ys.max()+1,xs.min():xs.max()+1]
    if scale: width=int(c.shape[1]*scale)
    sc=width/c.shape[1]
    c=cv2.resize(c,(width,int(c.shape[0]*sc)),interpolation=cv2.INTER_AREA)
    pad=40; can=np.zeros((c.shape[0]+2*pad,c.shape[1]+2*pad,4),np.uint8); can[pad:-pad,pad:-pad]=c
    a=can[...,3]; k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(37,37)); dil=cv2.GaussianBlur(cv2.dilate(a,k),(0,0),1.5)
    sh=np.roll(cv2.GaussianBlur(cv2.dilate(a,k),(0,0),16),16,axis=0)*0.45
    out=np.zeros(can.shape,np.float32); rgb=np.zeros(can.shape[:2]+(3,),np.float32)
    A=dil/255.; B=a/255.
    rgb=255*A[...,None]; rgb=rgb*(1-B[...,None])+can[...,[2,1,0]]*B[...,None]
    alpha=np.clip(1-(1-sh/255.)*(1-A),0,1); alpha=1-(1-alpha)*(1-B)
    out[...,:3]=rgb*np.where(A+B>0,1,0)[...,None]*1.0; out[...,3]=alpha*255
    return out   # straight rgb, alpha 0..255 (shadow part has rgb=0)
def title_frame(t,cut,hook=None,final=False):
    base=sun_frame(t)
    # person
    th,tw=cut.shape[:2]; slide=0 if final else (1-back(t/0.55,1.5))*820
    zoom=1+0.015*min(t,3)/3 if not final else 1.0
    topy=int(H+30-th+slide-PSHIFT); x0=(W-tw)//2
    prem=cut.copy(); prem[...,:3]*=prem[...,3:4]/255.
    if zoom!=1.0:
        M=cv2.getRotationMatrix2D((tw/2,th),0,zoom); prem=cv2.warpAffine(prem,M,(tw,th))
    ya,yb=max(0,topy),min(H,topy+th)
    if yb>ya:
        sub=prem[ya-topy:yb-topy]; xa=max(0,x0); xb=min(W,x0+tw); sub=sub[:,xa-x0:xb-x0]; al=sub[...,3:4]/255.
        base[ya:yb,xa:xb]=base[ya:yb,xa:xb]*(1-al)+sub[...,:3]
    # titles
    for L,cy,delay in ((T1,430,0.10),(T2,560,0.20),(T3,760,0.34)):
        s=1.0 if final else back((t-delay)/0.45,2.2); al=1.0 if final else clip01((t-delay)/0.12)
        if s<=0.02 or al<=0: continue
        h,w=L.shape[:2]; M=cv2.getRotationMatrix2D((w/2,h/2),0,s); wr=cv2.warpAffine(L,M,(w,h))
        y0=int(cy-TSHIFT-h/2); ya,yb=max(0,y0),min(H,y0+h); sub=wr[ya-y0:yb-y0]*al; a=sub[...,3:4]
        base[ya:yb,:w]=base[ya:yb,:w]*(1-a)+sub[...,:3]
    if hook:
        pass
    return base
def hook_pill(base,text):
    f=font(900,50); tw=f.getlength(text); pw,ph=int(tw+110),104; x0=(W-pw)//2; y0=PILLY
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([x0,y0+10,x0+pw,y0+ph+10],ph//2,fill=(0,0,0,90))
    d.rounded_rectangle([x0,y0,x0+pw,y0+ph],ph//2,fill=YEL+(255,),outline=WHITE+(255,),width=6)
    d.text((W/2,y0+ph/2+2),text,font=f,fill=NAVY+(255,),anchor='mm')
    a=np.asarray(im,np.float32); al=a[...,3:4]/255.; base[:]=base*(1-al)+a[...,:3]*al

def q_layout(f_txt,maxw=760):
    words=QTEXT.split(' '); lines=[[]]; sp=f_txt.getlength(' ')
    for w in words:
        cur=lines[-1]; wd=sum(f_txt.getlength(x) for x in cur)+sp*len(cur)
        if cur and wd+f_txt.getlength(w)>maxw: lines.append([w])
        else: cur.append(w)
    return lines
def question_frame(t):
    base=sun_frame(t+1.0)*0.85
    ft=font(800,64); lines=q_layout(ft); LH2=92
    bh=len(lines)*LH2+110; bw=900; x0=90; y0=950
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # pill header
    pf=font(900,44); ptxt="QUESTION FROM A STUDENT"; pw=int(pf.getlength(ptxt)+100); px=(W-pw)//2; py=700
    d.rounded_rectangle([px,py+8,px+pw,py+100+8],50,fill=(0,0,0,90)); d.rounded_rectangle([px,py,px+pw,py+100],50,fill=YEL+(255,),outline=WHITE+(255,),width=5)
    d.text((W/2,py+52),ptxt,font=pf,fill=NAVY+(255,),anchor='mm')
    # avatar
    ax,ay=x0+60,y0+bh+110
    d.ellipse([ax-60,ay-60,ax+60,ay+60],fill=YEL+(255,),outline=WHITE+(255,),width=5)
    d.ellipse([ax-17,ay-34,ax+17,ay],fill=NAVY+(255,)); d.pieslice([ax-34,ay+6,ax+34,ay+66],180,360,fill=NAVY+(255,))
    d.text((ax+84,ay),"A student asked",font=font(700,38),fill=WHITE+(255,),anchor='lm')
    if t<0.55:
        # typing dots bubble
        d.rounded_rectangle([x0,y0,x0+300,y0+130],65,fill=WHITE+(255,)); 
        for i in range(3):
            yy=y0+65-abs(math.sin(t*9+i*0.7))*14; d.ellipse([x0+78+i*68-14,yy-14,x0+78+i*68+14,yy+14],fill=(120,130,150,255))
    else:
        d.rounded_rectangle([x0,y0,x0+bw,y0+bh],56,fill=WHITE+(255,)); d.polygon([(x0+50,y0+bh-6),(x0+120,y0+bh-6),(x0+62,y0+bh+52)],fill=WHITE+(255,))
        nchar=int(max(0,(t-0.65))/1.9*len(QTEXT)); shown=0; y=y0+55+LH2*0.72; sp=ft.getlength(' ')
        for ln in lines:
            x=x0+70
            for w in ln:
                part=w[:max(0,nchar-shown)]; col=(14,110,70) if w.strip('?.,').upper() in QHI else NAVY
                if part: d.text((x,y),part,font=ft,fill=col+(255,),anchor='ls')
                x+=ft.getlength(w)+sp; shown+=len(w)+1
            y+=LH2
        if nchar<len(QTEXT) and int(t*3)%2==0:
            pass
    a=np.asarray(im,np.float32); al=a[...,3]/255.
    sh=np.roll(cv2.GaussianBlur(al,(0,0),18),20,axis=0)*0.45
    pop=back((t-0.0)/0.40,2.0) if t<0.55 else (1.0 if t>0.95 else 1+0.0)
    if t>=0.55: pop=back((t-0.55)/0.35,2.2)
    s_=max(0.001,pop)
    if s_!=1.0:
        M=cv2.getRotationMatrix2D((x0+450,y0+bh/2),0,s_) if t>=0.55 else cv2.getRotationMatrix2D((W/2,1000),0,s_)
        a=cv2.warpAffine(a,M,(W,H)); al=a[...,3]/255.; sh=cv2.warpAffine(sh,M,(W,H))
    base*= (1-sh)[...,None]; base[:]=base*(1-al)[...,None]+a[...,:3]*al[...,None]
    return base

# ------------------------------------------------------------ series tag / grade
def make_tag():
    im=Image.new('RGBA',(820,200),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((34,70),TAG1,font=font(800,56),fill=WHITE+(255,),anchor='lm'); d.text((36,134),TAG2,font=font(700,34),fill=(235,235,235,255),anchor='lm')
    a=np.asarray(im,np.float32); al=a[...,3]/255.
    sh=np.roll(cv2.GaussianBlur(al,(0,0),6),4,axis=0)*0.8
    return a[...,:3],al,sh
VIG=None
def grade(f):
    f=(f-128)*1.05+128; g=f@np.array([.299,.587,.114],np.float32); f=g[...,None]+(f-g[...,None])*1.08
    return f*VIG
def draw_tag(base,t,TAGL):
    rgb,al,sh=TAGL; reveal=smooth((t-0.25)/0.55); bar=smooth((t-0.15)/0.3)
    # top scrim
    sc=np.clip(1-np.arange(380)/380.,0,1)**1.6*0.55*min(1,t/0.2+0.01); base[:380]*= (1-sc)[:,None,None]
    x0,y0=60,70
    bh=int(112*bar); 
    if bh>0:
        base[y0+10+(112-bh):y0+10+112,x0:x0+9]=np.array([228,36,52],np.float32)
    cols=int(al.shape[1]*reveal)
    if cols>0:
        a=al[:,:cols].copy(); s=sh[:,:cols]; r=rgb[:,:cols]
        edge=min(cols,40); a[:,cols-edge:]*=np.linspace(1,0,edge)[None]
        reg=base[y0:y0+200,x0+9:x0+9+cols]; reg*=(1-s)[...,None]; reg[:]=reg*(1-a)[...,None]+r*a[...,None]
# ------------------------------------------------------------ audio
SR=44100
def load_audio():
    subprocess.run(['ffmpeg','-v','error','-y','-i',SRC,'-ac','2','-ar',str(SR),'-f','s16le','build/a3.raw'],check=True)
    return np.frombuffer(open('build/a3.raw','rb').read(),np.int16).reshape(-1,2).astype(np.float32)/32768
def sfx_whoosh(dur=0.5,rise=True):
    n=int(dur*SR); x=np.random.RandomState(3).randn(n).astype(np.float32); y=np.zeros(n,np.float32); s=0.
    for i in range(n):
        p=i/n; a=(0.02+0.35*(p if rise else 1-p)**1.5); s+=a*(x[i]-s); y[i]=s
    env=np.sin(np.pi*np.linspace(0,1,n))**1.5; y*=env*3.2
    return y/np.abs(y).max()*0.5
def sfx_hit():
    n=int(0.5*SR); t=np.arange(n)/SR; y=np.sin(2*np.pi*(62+90*np.exp(-t*30))*t)*np.exp(-t*7)
    y+=np.random.RandomState(5).randn(n)*np.exp(-t*60)*0.4; return (y*0.8).astype(np.float32)
def sfx_pop(f0=520):
    n=int(0.14*SR); t=np.arange(n)/SR; y=np.sin(2*np.pi*(f0+700*t/0.14*0.7)*t)*np.exp(-t*30); return (y*0.35).astype(np.float32)
def sfx_riser(dur=1.0):
    return sfx_whoosh(dur,True)*0.8
# ------------------------------------------------------------ main
CUT_A=5.90; CUT_B=7.15; FRZ=4.35; RES=4.85; BWEND=1.8; END=29.2333; CUT_C=25.95; CUT_D=26.25; TITLE=3.0; OUTRO=2.8; QLEN=3.4
QTEXT='I want to do MBBS in Germany. Is it possible?'
QHI=('MBBS','GERMANY')
ZOOMS=[(0,4.35,1.00,1.04),(4.85,5.9,1.10,1.12),(7.15,13.3,1.00,1.05),(13.3,18.75,1.10,1.15),(18.75,25.95,1.00,1.05),(26.25,30,1.12,1.18)]
def zoom_at(ts):
    for a,b,z0,z1 in ZOOMS:
        if a<=ts<b+1e-6: return z0+(z1-z0)*(ts-a)/(b-a)
    return 1.0
def segments():
    return [('live',0.0,FRZ),('title',0,TITLE),('question',0,QLEN),('live',RES,CUT_A),('live',CUT_B,CUT_C),('live',CUT_D,END),('outro',0,OUTRO)]
def read_frames(a,b):
    n=int(round((b-a)*FPS)); p=subprocess.Popen(['ffmpeg','-v','error','-ss',f'{a:.4f}','-i',SRC,'-frames:v',str(n),'-vf',f'fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    for i in range(n):
        buf=p.stdout.read(W*H*3)
        if len(buf)<W*H*3: break
        yield i,np.frombuffer(buf,np.uint8).reshape(H,W,3).astype(np.float32)
    p.stdout.close(); p.wait()
def main(mode):
    global T1,T2,T3,VIG
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.hypot((xx-W/2)/(W/2),(yy-H/2)/(H/2)); VIG=(1-0.16*np.clip(r-0.55,0,1)**1.4)[...,None]
    build_stickers(); sunburst()
    T1=text3d(SERIES1,112,extr=14); T2=text3d(SERIES2,112,extr=14); T3=text3d(EPNUM,150,extr=18)
    cut=prep_cut('ep3/cut_4.35.png',1040); TAGL=make_tag()
    caps=[(make_layer(t),make_noise(520,W),s,e) for t,s,e in PHRASES]
    outroL=[(make_layer("TO BE|CONTINUED…",size=104,kw=104,h=460,cy=230),make_noise(460,W))]
    pillL=make_layer("FOLLOW FOR EPISODE 4",size=50,kw=50,h=200,cy=100)
    segs=segments(); events=[]  # (out_time, kind)
    prog=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','build/audio_mix3.wav',
        '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT+'ask-the-cofounder-ep3.mp4'],stdin=subprocess.PIPE) if mode=='render' else None
    prev_frames=[]; want=[float(x) for x in sys.argv[2:]] if mode=='preview' else []
    out_t0=0.0; last_live=None; aud=[]; A=load_audio(); sfx=[]
    def emit(fr,ot):
        fr8=np.clip(fr,0,255).astype(np.uint8)
        if prog: prog.stdin.write(fr8.tobytes())
        for w in want:
            if abs(ot-w)<0.5/FPS: prev_frames.append((w,fr8.copy()))
    def audio_chunk(a,b): aud.append(A[int(a*SR):int(b*SR)])
    for kind,a,b in segs:
        if kind=='live':
            n=int(round((b-a)*FPS)); audio_chunk(a,a+n/FPS)
            # pop sfx times
            for key,s,e,c,ang in POPS:
                if a<=s<b and key not in ('x','tick') or (a<=s<b): sfx.append((out_t0+(s-a),'pop'))
            for i,fr in read_frames(a,b):
                ts=a+i/FPS; ot=out_t0+i/FPS; last_live=fr
                if mode=='preview' and not any(abs(ot-w)<0.5/FPS for w in want): continue
                z=zoom_at(ts); M=np.float32([[z,0,W/2-W/2*z],[0,z,900-900*z]]); f=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
                f=grade(f)
                if a<0.5 and ts<FRZ+1e-6:
                    gray=1.0 if ts<BWEND else clip01(1-(ts-BWEND)/0.35); g=f@np.array([.299,.587,.114],np.float32); f=f*(1-gray)+g[...,None]*gray
                    draw_tag(f,ts,TAGL)
                for L,nz,s,e in caps:
                    if s<=ts<e+0.22:
                        pin=(ts-s)/0.30; pout=(ts-e)/0.20 if ts>=e else 0
                        draw_layer(f,L,1170,nz,pin=clip01(pin),pout=clip01(pout))
                for key,s,e,c,ang in POPS: draw_sticker(f,key,ts,s,e,c,ang)
                emit(f,ot)
            out_t0+=n/FPS
        elif kind=='title':
            n=int(round(TITLE*FPS)); audio_chunk(0,0); aud.append(np.zeros((n*SR//FPS,2),np.float32)); sfx.append((out_t0-0.15,'whoosh_in')); sfx.append((out_t0,'hit')); sfx.append((out_t0+TITLE-0.35,'whoosh_out'))
            for i in range(n):
                t=i/FPS; ot=out_t0+t
                if mode=='preview' and not any(abs(ot-w)<0.5/FPS for w in want): continue
                f=title_frame(t,cut) if False else title_frame_rgb(t,cut)
                fl=clip01(1-t/0.22); f=f*(1-fl)+255*fl
                if t>TITLE-0.12: q=(t-(TITLE-0.12))/0.12; f=f*(1-q)+255*q
                emit(f,ot)
            out_t0+=n/FPS
        elif kind=='question':
            n=int(round(QLEN*FPS)); aud.append(np.zeros((n*SR//FPS,2),np.float32))
            for i in range(n):
                t=i/FPS; ot=out_t0+t
                if mode=='preview' and not any(abs(ot-w)<0.5/FPS for w in want): continue
                f=question_frame(t)
                if t<0.1: q=1-t/0.1; f=f*(1-q)+255*q*0.0+0
                if t>QLEN-0.1: q=(t-(QLEN-0.1))/0.1; f=f*(1-q)+255*q
                emit(f,ot)
            out_t0+=n/FPS
        else:
            n=int(round(OUTRO*FPS)); aud.append(np.zeros((n*SR//FPS,2),np.float32)); sfx.append((out_t0,'hit')); sfx.append((out_t0+0.78,'pop'))
            for i in range(n):
                t=i/FPS; ot=out_t0+t
                if mode=='preview' and not any(abs(ot-w)<0.5/FPS for w in want): continue
                z=1.18+0.05*t/OUTRO; M=np.float32([[z,0,W/2-W/2*z],[0,z,900-900*z]]); f=cv2.warpAffine(last_live,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
                f=grade(f); g=f@np.array([.299,.587,.114],np.float32); f=np.repeat(g[...,None],3,axis=2)*0.62
                sc=np.clip(np.arange(H)/H,0,1)[:,None,None]; f=f*1.15
                L,nz=outroL[0]; draw_layer(f,L,1000,nz,pin=clip01((t-0.2)/0.5))
                # pill
                pin=back((t-0.75)/0.45,2.0); pulse=1+0.03*math.sin(t*7)
                pw,ph=820,150; im=Image.new('RGBA',(W,300),(0,0,0,0)); d=ImageDraw.Draw(im)
                d.rounded_rectangle([130,60,950,210],75,fill=(0,0,0,100)); d.rounded_rectangle([130,45,950,195],75,fill=YEL+(255,),outline=WHITE+(255,),width=7)
                d.text((540,122),"FOLLOW FOR EPISODE 4",font=font(900,46),fill=NAVY+(255,),anchor='mm')
                a_=np.asarray(im,np.float32); s_=max(0.001,pin*pulse); Mm=cv2.getRotationMatrix2D((540,150),0,s_); pr=a_.copy(); pr[...,:3]*=pr[...,3:4]/255.
                wr=cv2.warpAffine(pr,Mm,(W,300)); al=wr[...,3:4]/255.*clip01(pin*2); 
                f[1400:1700]=f[1400:1700]*(1-al)+wr[...,:3]*clip01(pin*2)
                draw_tag(f,2.0,TAGL) if False else None
                emit(f,ot)
            out_t0+=n/FPS
    total=out_t0
    if mode=='render':
        prog.stdin.close(); prog.wait()
    return total,prev_frames,aud,sfx
def title_frame_rgb(t,cut):
    # compose using straight-alpha sticker (cut) and premult titles
    base=sun_frame(t); th,tw=cut.shape[:2]; slide=(1-back(t/0.55,1.5))*820
    topy=int(H+30-th+slide-PSHIFT); x0=(W-tw)//2
    zoom=1+0.02*t/3
    st=cut.copy(); st[...,:3]*=st[...,3:4]/255.
    if zoom!=1: st=cv2.warpAffine(st,cv2.getRotationMatrix2D((tw/2,th),0,zoom),(tw,th))
    ya,yb=max(0,topy),min(H,topy+th)
    if yb>ya:
        sub=st[ya-topy:yb-topy]; xa,xb=max(0,x0),min(W,x0+tw); sub=sub[:,xa-x0:xb-x0]; al=sub[...,3:4]/255.
        base[ya:yb,xa:xb]=base[ya:yb,xa:xb]*(1-al)+sub[...,:3]
    for L,cy,delay in ((T1,430,0.10),(T2,560,0.20),(T3,760,0.34)):
        s=back((t-delay)/0.45,2.2); al=clip01((t-delay)/0.12)
        if s<=0.02: continue
        h,w=L.shape[:2]; wr=cv2.warpAffine(L,cv2.getRotationMatrix2D((w/2,h/2),0,s),(w,h))
        y0=int(cy-TSHIFT-h/2); ya,yb=max(0,y0),min(H,y0+h); sub=wr[ya-y0:yb-y0]*al; a=sub[...,3:4]
        base[ya:yb,:w]=base[ya:yb,:w]*(1-a)+sub[...,:3]
    return base
def mix_audio(aud,sfx,total):
    v=np.concatenate(aud); n=int(total*SR)+SR; mix=np.zeros((n,2),np.float32); mix[:len(v)]+=v[:n]
    for tt,k in sfx:
        s={'whoosh_in':sfx_whoosh(0.5,True),'whoosh_out':sfx_whoosh(0.4,False),'hit':sfx_hit(),'pop':sfx_pop()}[k]
        i=int(max(0,tt)*SR); m=min(len(s),n-i); mix[i:i+m,0]+=s[:m]*0.9; mix[i:i+m,1]+=s[:m]*0.9
    mix=mix[:int(total*SR)]
    w=wave.open('build/audio_mix3.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes()); w.close()
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='preview':
        total,pf,aud,sfx=main('preview'); print('total',total)
        pf.sort(key=lambda x:x[0]); tiles=[cv2.resize(f,(360,640)) for _,f in pf]
        rows=[np.hstack(tiles[i:i+5]+[np.zeros_like(tiles[0])]*(5-len(tiles[i:i+5]))) for i in range(0,len(tiles),5)]
        Image.fromarray(np.vstack(rows)).save('build/preview.png'); print([w for w,_ in pf])
    elif mode=='render':
        # pass 1: dry run for timings (audio), pass 2: render
        total,_,aud,sfx=main('preview'); mix_audio(aud,sfx,total); print('audio ok',total)
        main('render')
