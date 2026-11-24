#!/usr/bin/env bash
# usage: finalize_video.sh RAW_VIDEO MIX_WAV OUT.mp4 DURATION_SECONDS
# Muxes the finished picture with the mixed audio and avoids three bugs we hit:
#  - loudnorm silently upsamples to 96 kHz -> phones play it late (looks like bad lip-sync): force 44.1 kHz
#  - audio longer than video -> trim with -t
#  - keep files under the 30 MB upload limit (crf 22 is visually fine for 1080x1920 talking heads)
set -e
RAW="$1"; WAV="$2"; OUT="$3"; DUR="$4"
ffmpeg -v error -y -i "$RAW" -i "$WAV" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p \
  -af "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=44100" -ar 44100 -ac 2 -c:a aac -b:a 192k -t "$DUR" -movflags +faststart "$OUT"
ffprobe -v error -show_entries stream=codec_type,sample_rate,duration -of compact "$OUT"; ls -la "$OUT"
