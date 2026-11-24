import build3 as B, numpy as np, cv2
from PIL import Image
B.OUT='/home/user/The100xers/ep3/'
B.SUN=None; B.sunburst()
B.T1=B.text3d(B.SERIES1,112,extr=14); B.T2=B.text3d(B.SERIES2,112,extr=14); B.T3=B.text3d(B.EPNUM,150,extr=18)
P='ep3/cut_24.3.png'
# plain cover (unchanged layout, fixed person scale)
cut=B.prep_cut(P,scale=1.30); B.PSHIFT=0; B.TSHIFT=0
f=B.title_frame_rgb(2.9,cut); Image.fromarray(np.clip(f,0,255).astype(np.uint8)).save(B.OUT+'cover-ep3.png')
# hook cover: person raised ~95px (taller cut-out keeps bottom flush), title nudged up, pill moved lower
cut2=B.prep_cut(P,scale=1.415); B.TSHIFT=55; B.PILLY=1370
g=B.title_frame_rgb(2.9,cut2); B.hook_pill(g,"MBBS IN GERMANY?")
Image.fromarray(np.clip(g,0,255).astype(np.uint8)).save(B.OUT+'cover-ep3-with-hook.png')
