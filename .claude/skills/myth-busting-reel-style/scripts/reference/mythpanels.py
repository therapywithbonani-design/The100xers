import numpy as np, cv2, math
from PIL import Image, ImageDraw
from mythlib import *
PH_FULL=820
_bg=None
def panel_bg():
    global _bg
    if _bg is None:
        yy,xx=np.mgrid[0:PH_FULL,0:W].astype(np.float32)
        g=np.zeros((PH_FULL,W,3),np.float32); t=(yy/PH_FULL)[...,None]
        c0=np.array([14,78,56],np.float32); c1=np.array([8,44,32],np.float32); g=c0*(1-t)+c1*t
        dots=((xx%54<3)&(yy%54<3)).astype(np.float32)[...,None]*14; g=g+dots
        r=np.hypot((xx-W/2)/(W/2),(yy-PH_FULL*0.4)/(PH_FULL/1.1)); g=g*(1-0.18*np.clip(r-0.4,0,1))[...,None]
        _bg=g
    return _bg.copy()
def pil_layer(): 
    im=Image.new('RGBA',(W,PH_FULL),(0,0,0,0)); return im,ImageDraw.Draw(im)
def over(base,im):
    a=np.asarray(im,np.float32); al=a[...,3:4]/255.; return base*(1-al)+a[...,:3]*al
def shadow_over(base,im,blur=16,dy=10,k=0.3):
    al=np.asarray(im,np.float32)[...,3]/255.; sh=np.roll(cv2.GaussianBlur(al,(0,0),blur),dy,axis=0)*k; return base*(1-sh[...,None])
def header(d,txt,y=62,col=(176,226,200)):
    f=F(800,34); 
    # letter-spaced caps
    sp=3; w=sum(f.getlength(c)+sp for c in txt)-sp; x=W/2-w/2
    for c in txt: d.text((x,y),c,font=f,fill=col+(255,),anchor='ls'); x+=f.getlength(c)+sp
def rrect(d,box,r,fill): d.rounded_rectangle(box,r,fill=fill)
def ico(d,kind,cx,cy,r): icon(d,kind,cx,cy,r)
def cardrow(d,y,label,ic,t,t_in,t_check,sub=None):
    p=smooth((t-t_in)/0.38)
    if p<=0: return
    off=int((1-back((t-t_in)/0.38,1.4))*-200)
    x0,x1=80+off,1000+off; a=int(255*smooth((t-t_in)/0.2))
    rrect(d,[x0,y,x1,y+150],38,(255,255,255,a))
    ico(d,ic,x0+84,y+75,48)
    d.text((x0+160,y+(66 if sub else 78)),label,font=F(800,50),fill=INK+(a,),anchor='lm')
    if sub: d.text((x0+160,y+112),sub,font=F(600,32),fill=(80,110,98,a),anchor='lm')
    if t>=t_check:
        q=back((t-t_check)/0.3,2.2)
        if q>0.02: 
            r=int(40*q); ico(d,'check',x1-70,y+75,max(2,r))
def panel_A(t):   # t = seconds since panel start
    base=panel_bg(); im,d=pil_layer(); header(d,"WHAT UNIVERSITIES LOOK AT")
    cardrow(d,185,"Very good internship",'brief',t,0.55,1.45)
    cardrow(d,375,"Bachelor's degree",'cap',t,1.55,2.25)
    cardrow(d,565,"= Strong profile",'star',t,2.45,99,None)
    base=shadow_over(base,im); return over(base,im)
def bar(d,x,y,w,h,val,col,track=(255,255,255,60)):
    rrect(d,[x,y,x+w,y+h],h//2,track)
    if val>0: rrect(d,[x,y,x+max(h,int(w*val)),y+h],h//2,col+(255,))
def card_pct(d,x0,x1,t,t_in,t_cnt,val,col,label,ic,t_lab,lab_col):
    p=back((t-t_in)/0.45,1.5)
    if p<=0.02: return
    y0=int(190+(1-clip01(p))*60); a=int(255*smooth((t-t_in)/0.25))
    rrect(d,[x0,y0,x1,y0+470],46,(255,255,255,a))
    cnt=smooth((t-t_cnt)/0.9); v=val*cnt
    d.text(((x0+x1)/2,y0+130),f"{int(round(v*100))}%",font=F(900,150),fill=INK+(a,),anchor='mm')
    bar(d,x0+40,y0+235,x1-x0-80,34,v,col,track=(16,38,29,28))
    if t>=t_lab:
        q=back((t-t_lab)/0.32,1.8)
        if q>0.02:
            w=x1-x0-60; h=int(110*min(1,q)); cy=y0+370
            rrect(d,[x0+30,cy-h//2,x0+30+w,cy+h//2],h//2,lab_col+(255,))
            ico2=ico
            d.text(((x0+x1)/2+22,cy+2),label,font=F(800,36),fill=WHITE+(255,),anchor='mm')
            cx=x0+30+h//2+2; 
            d.ellipse([cx-24,cy-24,cx+24,cy+24],fill=WHITE+(255,)); 
            if ic=='check': checkmark(d,cx,cy,50,lab_col)
            else:
                w_=7; d.line([cx-11,cy-11,cx+11,cy+11],fill=lab_col+(255,),width=w_); d.line([cx+11,cy-11,cx-11,cy+11],fill=lab_col+(255,),width=w_)
def panel_B(t):
    base=panel_bg(); im,d=pil_layer(); header(d,"MARKS ALONE DON'T GUARANTEE A SEAT",y=88)
    card_pct(d,50,522,t,0.15,0.55,0.75,GREEN,"Good university",'check',2.60,GREEN)
    card_pct(d,558,1030,t,3.40,4.00,0.92,RED,"Not admitted",'x',5.15,RED)
    base=shadow_over(base,im); return over(base,im)
def shield(d,cx,cy,s,col_border=GOLD,fill=(255,255,255,255)):
    pts=[(cx-s*.5,cy-s*.55),(cx+s*.5,cy-s*.55),(cx+s*.5,cy+s*.05),(cx,cy+s*.6),(cx-s*.5,cy+s*.05)]
    d.polygon(pts,fill=GOLD+(255,)); 
    inner=[(cx-s*.4,cy-s*.45),(cx+s*.4,cy-s*.45),(cx+s*.4,cy+.0*s),(cx,cy+s*.46),(cx-s*.4,cy+.0*s)]
    d.polygon(inner,fill=(14,78,56,255))
def badge_c(d,cx,t,t_in,name,sub):
    p=back((t-t_in)/0.45,1.6)
    if p<=0.02: return
    a=int(255*smooth((t-t_in)/0.25)); y=int(215+(1-clip01(p))*50)
    rrect(d,[cx-215,y,cx+215,y+260],42,(255,255,255,a))
    shield(d,cx,y+88,110)
    d.text((cx,y+190),name,font=F(900,40),fill=INK+(a,),anchor='mm'); d.text((cx,y+228),sub,font=F(700,28),fill=(80,110,98,a),anchor='mm')
def panel_C(t):
    base=panel_bg(); im,d=pil_layer(); header(d,"WHAT THEY ALL LOOK AT")
    badge_c(d,285,t,0.40,"IVY LEAGUE","USA"); badge_c(d,795,t,1.20,"RUSSELL GROUP","UK")
    # profile pill
    p=back((t-2.45)/0.45,1.6)
    if p>0.02:
        a=int(255*smooth((t-2.45)/0.25)); w=int(520*min(1,p)); cy=610
        rrect(d,[W/2-w/2,cy-70,W/2+w/2,cy+70],70,GREEN+(a,))
        d.text((W/2-20,cy+2),"PROFILE",font=F(900,68),fill=WHITE+(a,),anchor='mm')
        if p>0.8: d.ellipse([W/2+w/2-120,cy-36,W/2+w/2-48,cy+36],fill=WHITE+(a,)); checkmark(d,W/2+w/2-84,cy,76,GREEN)
    p2=back((t-3.65)/0.4,1.4)
    if p2>0.02:
        a=int(235*smooth((t-3.65)/0.25)); cy=740
        txt="academics only"; f=F(700,46); tw=f.getlength(txt); d.text((W/2,cy),txt,font=f,fill=(255,255,255,a),anchor='mm')
        L=tw*min(1,smooth((t-3.9)/0.25)); d.line([W/2-tw/2-8,cy+2,W/2-tw/2-8+L+16,cy+2],fill=RED+(255,),width=7)
    base=shadow_over(base,im); return over(base,im)
PANELS={'A':(11.40,14.90,panel_A),'B':(19.45,25.05,panel_B),'C':(26.35,31.00,panel_C)}
TIN=0.42; TOUT=0.40
def split_state(t):
    for k,(a,b,fn) in PANELS.items():
        if a-0.0<=t<=b:
            p=smooth((t-a)/TIN)*smooth((b-t)/TOUT); return k,p,t-a,fn
    return None,0.0,0.0,None
