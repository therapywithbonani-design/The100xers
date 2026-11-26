#!/bin/bash
# $1=look
cd /tmp/claude-0/-home-user-The100xers/3dc716bb-8387-5a31-912b-63c195d92910/scratchpad/reel3d
ffmpeg -y -v error -framerate 30 -i frames/flip_$1/f_%04d.png -i in/vo.mp3 -i in/music.mp3 -i out/flip_sfx.wav \
 -filter_complex "[1:a]atrim=3.0:8.0,asetpts=PTS-STARTPTS,volume=1.6[v];[2:a]atrim=3.0:8.0,asetpts=PTS-STARTPTS,volume=0.10[m];[3:a]volume=0.9[s];[v][m][s]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]" \
 -map 0:v -map "[a]" -vf "scale=in_range=full:out_range=tv:out_color_matrix=bt709:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p" \
 -c:v libx264 -preset slow -crf 17 -profile:v high -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest out/flip_test_$1.mp4
