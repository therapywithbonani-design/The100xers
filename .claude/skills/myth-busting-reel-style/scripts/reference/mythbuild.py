import sys, subprocess, numpy as np, cv2, math, wave
from mythlib import *
import mythlib as M, mythpanels as P
init=M.init_grade(); 
CAPS=[("I think *guaranteed* toh nahi hai,",4.92,6.60),("aisa bilkul *nahi* *hota,*",6.56,7.85),("depends on your *overall* *profile.*",8.00,10.28),
 ("If you have done a very good *internship*",10.46,12.46),("during your *bachelors,*",12.46,14.30),("so probably *university*",14.40,16.62),("they try to match your *ECTS* *points.*",16.62,18.75),
 ("So even at *75%*",19.02,20.95),("you might get a good *university*",21.02,22.72),("and even at *92%*",22.72,24.25),("you might *not* get.",24.25,25.30),
 ("Be it *Ivy* *League*",26.22,27.40),("or *Russell* *Group,*",27.40,28.35),("they all look at your *profile*",28.44,29.80),("not only at your *academics.*",29.80,31.50),
 ("So we remember,",32.16,32.95),("work on your *profile*",33.06,33.96),("along with your *academics,*",33.96,35.30),("not just focus on your high *CGPA.*",35.68,38.30)]
STK=[("High CGPA =","Guaranteed admission?",'q','MYTH',1.30,3.75),("Not guaranteed",None,'x',None,5.45,7.30),("Overall profile",None,'person',None,8.45,10.30),
 ("University match",None,'cap',None,15.50,18.70),("Profile + Academics",None,'plus',None,33.00,35.30),("Only high CGPA",None,'x',None,36.00,38.70)]
CAP_TOP=1330; STK_CY=300
SCR=(np.clip((np.arange(H)-1120)/(H-1120.0),0,1)**1.4*0.40)[:,None,None].astype(np.float32)
def split_frame(src,p,t_rel,fn):
    PH=int(round(P.PH_FULL*p)); 
    if PH<=2: return None
    Hv=H-PH; r0=int(460*p); reg=src[r0:r0+Hv]
    vid=grade(reg.copy(),M.VIG[r0:r0+Hv]); out=np.zeros((H,W,3),np.float32); out[PH:]=vid
    pan=fn(t_rel); out[:PH]=pan[P.PH_FULL-PH:]
    # divider
    out[max(0,PH-4):PH+2]=np.array(GOLD,np.float32); sh=np.linspace(0.28,0,26)[:,None,None]; out[PH+2:PH+28]*= (1-sh)
    return out
def read_frames():
    p=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-vf',f'fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    i=0
    while True:
        buf=p.stdout.read(W*H*3)
        if len(buf)<W*H*3: break
        yield i,np.frombuffer(buf,np.uint8).reshape(H,W,3).astype(np.float32); i+=1
    p.stdout.close(); p.wait()
QWORDS=[("Sir,",0.55,False),("high",1.26,False),("CGPA",1.46,True),("hai,",2.00,False),("admission",2.28,True),("guaranteed",2.56,True),("hai",2.94,False),("kya?",3.20,False)]
Q_IN,Q_OUT=0.20,3.80
def mic(d,cx,cy,r,col):
    d.rounded_rectangle([cx-r*.28,cy-r*.62,cx+r*.28,cy+r*.1],r*.28,fill=col); d.arc([cx-r*.5,cy-r*.3,cx+r*.5,cy+r*.5],0,180,fill=col,width=int(r*.12))
    d.line([cx,cy+r*.5,cx,cy+r*.72],fill=col,width=int(r*.12)); d.line([cx-r*.26,cy+r*.74,cx+r*.26,cy+r*.74],fill=col,width=int(r*.12))
def make_qcard():
    f=F(800,56); sp=f.getlength(' '); maxw=800
    total=sum(f.getlength(t) for t,_,_ in QWORDS)+sp*(len(QWORDS)-1)
    best=None
    for i in range(1,len(QWORDS)):
        a=sum(f.getlength(t) for t,_,_ in QWORDS[:i])+sp*(i-1); b_=sum(f.getlength(t) for t,_,_ in QWORDS[i:])+sp*(len(QWORDS)-i-1)
        if best is None or max(a,b_)<best[0]: best=(max(a,b_),i)
    lines=[QWORDS[:best[1]],QWORDS[best[1]:]]
    cw,ch=960,355; x0=60; lh=88
    bg=Image.new('RGBA',(W,ch),(0,0,0,0)); d=ImageDraw.Draw(bg)
    d.rounded_rectangle([x0,20,x0+cw,ch-30],44,fill=(255,255,255,255))
    d.ellipse([x0+36,48,x0+36+64,48+64],fill=GREEN+(255,)); mic(d,x0+68,82,34,(255,255,255,255))
    lab=F(900,30); xx=x0+118; 
    for c in "QUESTION": d.text((xx,92),c,font=lab,fill=GREEN+(255,),anchor='ls'); xx+=lab.getlength(c)+4
    words=[]; y=190
    for ln in lines:
        tw=sum(f.getlength(t) for t,_,_ in ln)+sp*(len(ln)-1); x=W/2-tw/2
        for t,ts,k in ln:
            lay=Image.new('RGBA',(W,ch),(0,0,0,0)); ld=ImageDraw.Draw(lay); w_=f.getlength(t)
            if k: ld.rounded_rectangle([x-12,y-56,x+w_+12,y+20],18,fill=(206,238,221,255))
            ld.text((x,y),t,font=f,fill=((10,96,62,255) if k else INK+(255,)),anchor='ls')
            words.append((np.asarray(lay,np.float32),ts)); x+=w_+sp
        y+=lh
    a=np.asarray(bg,np.float32); al=a[...,3]/255.; sh=np.roll(cv2.GaussianBlur(al,(0,0),16),14,axis=0)*0.35
    return dict(rgb=a[...,:3],a=al,sh=sh,words=words,h=ch)
def draw_qcard(f,Q,t,top=1290):
    if not (Q_IN<=t<=Q_OUT+0.2): return
    pin=back((t-Q_IN)/0.35,1.5); pout=smooth((Q_OUT+0.2-t)/0.2); op=clip01((t-Q_IN)/0.15)*pout
    dy=int((1-clip01(pin))*60); h=Q['h']; y0=top+dy; ya,yb=max(0,y0),min(H,y0+h); sl=slice(ya-y0,yb-y0)
    reg=f[ya:yb]; sh=Q['sh'][sl]*op; al=Q['a'][sl]*op
    reg*=(1-sh)[...,None]; reg[:]=reg*(1-al)[...,None]+Q['rgb'][sl]*al[...,None]
    for lay,ts in Q['words']:
        wa=smooth((t-ts)/0.12)*op
        if wa<=0.01: continue
        la=lay[sl][...,3]/255.*wa; reg[:]=reg*(1-la)[...,None]+lay[sl][...,:3]*la[...,None]
def main(mode,want=()):
    caps=[(make_caption(t),s,e) for t,s,e in CAPS]
    Q=make_qcard()
    stk=[(sticker(a,b,c,d_,l2size=(54 if (d_=='MYTH') else 36),l2w=(800 if d_=='MYTH' else 600),l2col=((14,110,72,255) if d_=='MYTH' else (80,110,98,255))),s,e) for a,b,c,d_,s,e in STK]
    prog=None; shots=[]
    if mode=='render':
        prog=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','build/myth_audio.wav','-map','0:v','-map','1:a',
          '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart','/home/user/The100xers/myth/myth-busting-ep1.mp4'],stdin=subprocess.PIPE)
    n=0
    for i,src in read_frames():
        t=i/FPS; n+=1
        if mode=='preview' and not any(abs(t-w)<0.5/FPS for w in want): continue
        k,p,trel,fn=P.split_state(t)
        f=None
        if k is not None and p>0.01: f=split_frame(src,p,trel,fn)
        if f is None: f=grade(src.copy())
        f*= (1-SCR)
        for L,s,e in caps:
            if s<=t<e+0.2:
                draw_caption(f,L,CAP_TOP,(t-s)/0.16,(t-e)/0.14 if t>=e else 0)
        if k is None: draw_qcard(f,Q,t)
        if k is None or p<0.02:
            for S,s,e in stk: draw_sticker(f,S,W/2,STK_CY+(10 if S['h']>200 else 0)+(25 if S['h']>260 else 0),t,s,e)
        if prog: prog.stdin.write(np.clip(f,0,255).astype(np.uint8).tobytes())
        else: shots.append((t,np.clip(f,0,255).astype(np.uint8)))
    if prog: prog.stdin.close(); prog.wait()
    return n,shots
if __name__=='__main__':
    import os; os.makedirs('/home/user/The100xers/myth',exist_ok=True)
    if sys.argv[1]=='preview':
        want=[float(x) for x in sys.argv[2:]]; n,sh=main('preview',want); sh.sort(key=lambda x:x[0])
        tiles=[cv2.resize(f,(324,576)) for _,f in sh]; rows=[np.hstack(tiles[i:i+5]+[np.zeros_like(tiles[0])]*(5-len(tiles[i:i+5]))) for i in range(0,len(tiles),5)]
        cv2.imwrite('myth/preview.png',cv2.cvtColor(np.vstack(rows),cv2.COLOR_RGB2BGR)); print('frames',n,[w for w,_ in sh])
    else: print('rendered frames',main('render')[0])
