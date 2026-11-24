import cv2, numpy as np
def fix(t, leaf_xmax, clips=(), d='ep3', redx=0.60, open_k=5):
    im=cv2.imread(f'{d}/fr_{t}.png'); c=cv2.imread(f'{d}/cut_{t}.png',cv2.IMREAD_UNCHANGED)
    hv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); hh,ss,vv=hv[...,0],hv[...,1],hv[...,2]; H,W=hh.shape; yy,xx=np.mgrid[0:H,0:W]
    yellow=(hh>=19)&(hh<=36)&(ss>55)&(vv>110)
    redtxt=((hh<=5)|(hh>=168))&(ss>140)&(vv>90)
    leaf=(((hh>=158)|(hh<=4))&(ss>95))|((hh>=36)&(hh<=90)&(ss>60))
    bad=((yellow&(yy<0.47*H)&(xx>0.40*W))|(redtxt&(yy<0.47*H)&(xx>redx*W)))|(leaf&(xx<leaf_xmax*W)&(yy<0.46*H))
    bad=cv2.dilate(bad.astype(np.uint8),np.ones((13,13),np.uint8))>0
    a=c[...,3].astype(np.float32)/255; a[bad]=0
    for (xa,xb,ya,yb) in clips: a[int(ya*H):int(yb*H),int(xa*W):int(xb*W)]=0
    m=(a>0.5).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((open_k,open_k),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m); big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); a=a*(lab==big)
    m=(a>0.5).astype(np.uint8); ff=(1-m).copy(); mask=np.zeros((H+2,W+2),np.uint8); cv2.floodFill(ff,mask,(0,0),2)
    holes=(ff==1); a=np.where(holes,1.0,a)
    a=cv2.GaussianBlur(a,(0,0),3.5); a=np.clip((a-0.5)*3+0.5,0,1)
    c[...,3]=(a*255).astype(np.uint8); cv2.imwrite(f'{d}/cut_{t}.png',c)
    al=c[...,3:4]/255.; comp=(c[...,:3]*al+np.array([60,170,255])*(1-al)).astype(np.uint8); return comp
