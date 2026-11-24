import numpy as np, cv2, sys
def cutout(img_path, mask_path, out_path, clips=(), colorfix=False):
    im=cv2.imread(img_path); m=cv2.imread(mask_path,0)
    S=2; sm=cv2.resize(im,(im.shape[1]//S,im.shape[0]//S)); mm=cv2.resize(m,(sm.shape[1],sm.shape[0]))
    h,w=sm.shape[:2]
    gc=np.full((h,w),cv2.GC_BGD,np.uint8)
    y0,y1,x0,x1=int(h*0.285),int(h*0.712),int(w*0.04),int(w*0.97)   # ROI around founder
    roi=np.zeros((h,w),bool); roi[y0:y1,x0:x1]=True
    gc[roi]=cv2.GC_PR_BGD
    gc[roi&(mm>100)]=cv2.GC_PR_FGD
    core=cv2.erode((mm>230).astype(np.uint8),np.ones((25,25),np.uint8))>0
    gc[roi&core]=cv2.GC_FGD
    # banner/shelf area right of head is background (yellow/red banner): sure BG by colour in HSV
    hsv=cv2.cvtColor(sm,cv2.COLOR_BGR2HSV)
    ban=(((hsv[...,0]>=19)&(hsv[...,0]<=35))|(hsv[...,0]<=5)|(hsv[...,0]>=170))&(hsv[...,1]>175)&(hsv[...,2]>120)
    ban[int(h*0.48):,:]=False
    gc[ban&roi]=cv2.GC_BGD
    # table (bright, low saturation) below desk line is bg
    gc[:, :][ (np.arange(h)[:,None]>int(h*0.70)) & (hsv[...,1]<40) & (hsv[...,2]>170)]=cv2.GC_BGD
    bg=np.zeros((1,65)); fg=np.zeros((1,65))
    cv2.grabCut(sm,gc,None,bg,fg,6,cv2.GC_INIT_WITH_MASK)
    fgm=((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD)).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(fgm)
    big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); fgm=(lab==big).astype(np.uint8)
    fgm=cv2.morphologyEx(fgm,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    fgm=cv2.morphologyEx(fgm,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    a=cv2.resize(fgm.astype(np.float32),(im.shape[1],im.shape[0]),interpolation=cv2.INTER_LINEAR)
    a=cv2.GaussianBlur(a,(0,0),2.2); a=np.clip((a-0.35)/0.4,0,1)
    H,W=a.shape
    if colorfix:
        hv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); hh,ss,vv=hv[...,0],hv[...,1],hv[...,2]
        yy,xx=np.mgrid[0:H,0:W]
        leaf=(((hh>=158)|(hh<=4))&(ss>95))|((hh>=36)&(hh<=90)&(ss>60))
        bad=(leaf&(xx<0.47*W)&(yy<0.46*H))|(((hh>=21)&(hh<=36))&(ss>70)&(yy<0.42*H)&(xx>0.46*W))
        bad=cv2.dilate(bad.astype(np.uint8),np.ones((9,9),np.uint8))>0
        a=a*(~bad)
        keep=((vv<118)|((hh>=2)&(hh<=19)&(ss>=35)&(ss<=200)&(vv>=70))).astype(np.uint8)
        keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
        keep=cv2.morphologyEx(keep,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
        a=np.where(yy<0.47*H,a*keep,a)
        m8=(a>0.5).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(m8)
        big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); a=a*(lab==big)
    for (xa,xb,ya,yb) in clips: a[int(ya*H):int(yb*H),int(xa*W):int(xb*W)]=0
    rgba=np.dstack([im,(a*255).astype(np.uint8)])
    cv2.imwrite(out_path,rgba)
if __name__=='__main__':
    CL={'1.45':[(0.515,1,0,0.47)],'18.0':[(0,0.432,0,0.45),(0.69,1,0,0.45)]}
    for t in ['1.45','18.0']:
        cutout(f'build/fr_{t}.png',f'build/mask2_{t}.png',f'build/cut_{t}.png',CL[t])
    a=[]
    for t in ['1.45','18.0']:
        c=cv2.imread(f'build/cut_{t}.png',cv2.IMREAD_UNCHANGED); al=c[...,3:4]/255.
        comp=(c[...,:3]*al+np.array([60,170,255])*(1-al)).astype(np.uint8)
        a.append(cv2.resize(comp,(360,640)))
    cv2.imwrite('build/prev3.png',np.hstack(a))
