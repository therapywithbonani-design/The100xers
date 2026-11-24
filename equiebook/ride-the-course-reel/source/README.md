# Rebuild the reel
npm install && node render.js 1080 1920 frames all && python3 audio.py frames/meta.json audio.wav
ffmpeg -framerate 30 -i frames/f%05d.jpg -i audio.wav -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -shortest out.mp4
Course, prompts and copy are in scene.js (segs / prompts / endCard). Needs Chromium + Playwright.
