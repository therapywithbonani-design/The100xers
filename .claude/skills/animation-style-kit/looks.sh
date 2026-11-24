#!/usr/bin/env bash
# Apply an Animation Style Kit look to real footage (approximation filters).
# Usage: looks.sh <style> <input> <output>
# styles: cyberpunk paper hologram popart thermal anime sunset ukiyoe claymation
set -euo pipefail
S="$1"; IN="$2"; OUT="$3"
EDGES="format=gray,edgedetect=low=0.06:high=0.18,negate,format=rgb24"
case "$S" in
 cyberpunk) FC="[0:v]format=rgb24,eq=contrast=1.5:brightness=-0.2:saturation=1.8,colorbalance=rs=0.10:bs=0.40:rm=0.30:gm=-0.15:bm=0.35:rh=0.30:gh=-0.10:bh=0.25,split[a][b];[b]gblur=sigma=14[g];[a][g]blend=all_mode=screen:all_opacity=0.55,drawgrid=w=iw:h=3:t=1:c=black@0.18[v]";;
 paper)     FC="[0:v]format=rgb24,bilateral=sigmaS=12:sigmaR=0.12,eq=saturation=1.15:brightness=0.04,lutrgb=r='trunc(val/40)*40+20':g='trunc(val/40)*40+20':b='trunc(val/40)*40+20',colorbalance=rm=0.06:bm=-0.06,split[a][b];[b]$EDGES,gblur=sigma=1.5[e];[a][e]blend=all_mode=multiply:all_opacity=0.55,noise=alls=7:allf=t[v]";;
 hologram)  FC="[0:v]format=gray,eq=contrast=1.5:brightness=-0.1,split[l][m];[m]edgedetect=low=0.05:high=0.15,format=gbrp,colorchannelmixer=rr=0.35:gg=0.95:bb=1,split[e1][e2];[e2]gblur=sigma=6[eg];[l]format=gbrp,colorchannelmixer=rr=0.05:gg=0.35:bb=0.6[base];[base][e1]blend=all_mode=addition[x];[x][eg]blend=all_mode=screen:all_opacity=0.8,drawgrid=w=iw:h=4:t=1:c=black@0.45,eq=brightness='0.03*sin(t*37)':eval=frame[v]";;
 popart)    FC="[0:v]format=rgb24,bilateral=sigmaS=8:sigmaR=0.15,eq=contrast=1.35:saturation=2.2,lutrgb=r='if(gt(val,128),255,if(gt(val,60),150,0))':g='if(gt(val,128),220,if(gt(val,60),110,0))':b='if(gt(val,140),230,if(gt(val,70),90,0))',split=3[a][b][c];[b]format=gray,geq=lum='if(lt(hypot(mod(X,7)-3.5,mod(Y,7)-3.5),3.6*(1-lum(X,Y)/255)+0.6),70,255)',format=rgb24[h];[c]format=gray,edgedetect=low=0.1:high=0.25,negate,format=rgb24,lutrgb=r='if(lt(val,200),0,255)':g='if(lt(val,200),0,255)':b='if(lt(val,200),0,255)'[e];[a][h]blend=all_mode=multiply:all_opacity=0.6[x];[x][e]blend=all_mode=multiply[v]";;
 thermal)   FC="[0:v]format=gray,gblur=sigma=2,eq=contrast=1.4:brightness=0.02,format=yuv420p,pseudocolor=preset=inferno,drawbox=x=iw-28:y=ih*0.2:w=10:h=ih*0.5:c=white@0.6:t=1,drawgrid=w=iw:h=ih/2:t=1:c=white@0.15[v]";;
 anime)     FC="[0:v]format=rgb24,bilateral=sigmaS=16:sigmaR=0.18,bilateral=sigmaS=10:sigmaR=0.12,eq=saturation=1.45:brightness=0.06:contrast=1.1,lutrgb=r='trunc(val/28)*28+14':g='trunc(val/28)*28+14':b='trunc(val/28)*28+14',split[a][b];[b]$EDGES,lutrgb=r='if(lt(val,180),30,255)':g='if(lt(val,180),30,255)':b='if(lt(val,180),40,255)'[e];[a][e]blend=all_mode=multiply[v]";;
 sunset)    FC="[0:v]format=gray,gblur=sigma=1.5,lutyuv=y='if(lt(val,150),0,255)',format=gbrp[m];gradients=s=WxH:c0=0x2B1650:c1=0xFF8A3D:x0=0:y0=0:x1=0:y1=HH:speed=0.00001,format=gbrp[g];[g][m]blend=all_mode=multiply:shortest=1,drawbox=x=0:y=ih*0.86:w=iw:h=ih*0.14:c=black:t=fill[v]";;
 ukiyoe)    FC="[0:v]format=rgb24,bilateral=sigmaS=12:sigmaR=0.15,eq=saturation=0.65:contrast=1.1,colorbalance=rs=-0.1:bs=0.15:rh=0.12:gh=0.06:bh=-0.12,lutrgb=r='trunc(val/36)*36+30':g='trunc(val/36)*36+26':b='trunc(val/36)*36+18',split[a][b];[b]$EDGES[e];[a][e]blend=all_mode=multiply:all_opacity=0.8,noise=alls=10:allf=u,vignette=PI/5,drawbox=x=iw-70:y=40:w=40:h=170:c=0xEFE3C8:t=fill,drawbox=x=iw-62:y=180:w=24:h=24:c=0xC0392B:t=fill[v]";;
 claymation)FC="[0:v]fps=12,format=rgb24,bilateral=sigmaS=14:sigmaR=0.2,eq=saturation=1.25:contrast=0.95:brightness=0.03,lutrgb=r='trunc(val/24)*24+12':g='trunc(val/24)*24+12':b='trunc(val/24)*24+12',unsharp=7:7:1.2,noise=alls=4:allf=t,vignette=PI/5[v]";;
 *) echo "unknown style $S"; exit 1;;
esac
# sunset needs WxH substituted
FC="${FC//WxH/$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$IN")}"
FC="${FC//y1=HH/y1=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$IN")}"
if [[ "$OUT" =~ \.(png|jpg)$ ]]; then FC="${FC//fps=12,/}"; ffmpeg -v warning -y -i "$IN" -filter_complex "$FC" -map "[v]" -frames:v 1 "$OUT"
else ffmpeg -v error -y -i "$IN" -filter_complex "$FC" -map "[v]" -map 0:a? -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy -shortest "$OUT"; fi
