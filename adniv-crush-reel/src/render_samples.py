import sys; sys.path.insert(0,'.')
from grade import frame
from styles import *
import numpy as np
bgcache={}
def bg(t):
    k=round(t,2)
    if k not in bgcache: bgcache[k]=Image.fromarray(frame("IMG_4903",k))
    return bgcache[k]
def comp(style,t,src0=0.4):
    b=bg(src0+t); c=b.convert("RGBA")
    {"A":style_A,"B":style_B,"C":style_C}[style](c,b,t,DONUT)
    place_logo(c)
    return c.convert("RGB")
for s in sys.argv[1:]:
    hero=comp(s,2.2); hero.save(f"samples/style{s}_hero.png")
    safe_overlay(hero).convert("RGB").save(f"samples/style{s}_hero_safezone.jpg",quality=88)
    ts=[0.15,0.45,0.8,1.8]; fr=[]
    for t in ts:
        im=comp(s,t).resize((540,960),Image.LANCZOS); dd=ImageDraw.Draw(im)
        dd.text((14,12),f"t = {t:.2f}s",font=F("Inter-Bold",26),fill="white",stroke_width=3,stroke_fill="black"); fr.append(im)
    strip=Image.new("RGB",(540*4+30,960),(20,20,20))
    for i,im in enumerate(fr): strip.paste(im,(i*550,0))
    strip.save(f"samples/style{s}_strip.jpg",quality=88)
    print("done",s)
