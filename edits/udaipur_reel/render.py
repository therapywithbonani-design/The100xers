"""TravLink - City Palace Udaipur reel (no text). Built from the Travlink Reel Editing Playbook.

Usage: python3 render.py <frames_dir> <photos_dir> <assets_dir> <out.mp4>
frames_dir holds IMG_0642/ IMG_0672/ IMG_0712/ IMG_0714/ JPEG sequences (SDR, 1080x1920, 24 fps).
"""
import sys, math, subprocess, functools
from multiprocessing import Pool
import numpy as np, cv2
from PIL import Image, ImageOps

FR_DIR, PH_DIR, AS_DIR, OUT = sys.argv[1:5]
W, H, FPS, DUR = 1080, 1920, 30, 33.0
BG = np.array([0.055, 0.063, 0.071], np.float32)  # warm near-black, BGR

# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(u): u = clamp(u); return 1 - (1 - u) ** 3
def ease_in(u): u = clamp(u); return u ** 3
def ease_io(u): u = clamp(u); return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2
def back_out(u, s=1.7): u = clamp(u) - 1; return 1 + (s + 1) * u ** 3 + s * u ** 2
def lerp(a, b, u): return a + (b - a) * u

# ---------------- grade ----------------
_x = np.arange(256) / 255.0
def _curve(x, gain, lift):
    x = np.clip(x * gain + lift, 0, 1)
    s = x * x * (3 - 2 * x)
    return np.clip(0.62 * x + 0.38 * s, 0, 1)
LUT = np.stack([_curve(_x, 0.95, 0.0), _curve(_x, 1.0, 0.004), _curve(_x, 1.05, 0.012)], 1)  # B,G,R warm
LUT = (LUT * 255).astype(np.uint8).reshape(256, 1, 3)

def grade(u8):
    img = cv2.LUT(u8, LUT).astype(np.float32) / 255.0
    g = img.mean(2, keepdims=True)
    return np.clip(g + (img - g) * 1.10, 0, 1)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGNETTE = (1 - 0.38 * np.clip(r - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 0.014, (H, W, 1)).astype(np.float32) for _ in range(6)]

# ---------------- sources ----------------
VIDEO_FPS = {'IMG_0642': 24.0, 'IMG_0672': 24.0, 'IMG_0712': 23.976, 'IMG_0714': 23.976}
VIDEO_LEN = {}
import os
for n in VIDEO_FPS: VIDEO_LEN[n] = len(os.listdir(f'{FR_DIR}/{n}'))

@functools.lru_cache(maxsize=48)
def vframe(name, idx):
    idx = int(clamp(idx, 0, VIDEO_LEN[name] - 1))
    return grade(cv2.imread(f'{FR_DIR}/{name}/{idx + 1:04d}.jpg'))

def video(name, t):
    return vframe(name, round(t * VIDEO_FPS[name]))

PHOTO_FILES = {
    'pano': '138eb100-image.jpg', 'horse': 'd0da4d1a-image.jpg', 'armour': '731f7dea-image.jpg',
    'wall': '2e438ac7-image.jpg', 'daggers': '75b64950-image.jpg', 'pratap': 'bb9b4374-image.jpg',
    'vani': '33f9b7a2-image.jpg', 'garden': '3491b826-image.jpg', 'facade': '40d400c3-image.jpg'}
# crop regions (x0, y0, x1, y1) in photo pixels: keep visitors out of frame
PHOTO_CROP = {
    'horse': (120, 0, 1180, 1128), 'armour': (300, 80, 1060, 1160), 'daggers': (120, 150, 1420, 1999),
    'wall': (480, 200, 1500, 1285), 'pratap': (150, 60, 1350, 1767), 'facade': (470, 620, 1000, 1374),
    'garden': (0, 250, 1500, 1577)}

@functools.lru_cache(maxsize=16)
def photo(key):
    im = ImageOps.exif_transpose(Image.open(f'{PH_DIR}/{PHOTO_FILES[key]}')).convert('RGB')
    if key in PHOTO_CROP: im = im.crop(PHOTO_CROP[key])
    return grade(cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR))

# ---------------- reframe ----------------
def reframe(img, w, h, zoom=1.0, cx=0.5, cy=0.5):
    ih, iw = img.shape[:2]
    ar = w / h
    if iw / ih > ar: ch, cw = ih, ih * ar
    else: cw, ch = iw, iw / ar
    cw, ch = cw / zoom, ch / zoom
    x0 = clamp(cx * iw - cw / 2, 0, iw - cw); y0 = clamp(cy * ih - ch / 2, 0, ih - ch)
    s = w / cw
    if s < 0.7:  # pre-shrink to avoid aliasing
        f = s / 0.7
        img = cv2.resize(img, (max(1, int(iw * f)), max(1, int(ih * f))), interpolation=cv2.INTER_AREA)
        x0, y0, cw, s = x0 * f, y0 * f, cw * f, w / (cw * f)
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------------- shot builders ----------------
def settle_push(u, dur):
    return (1 + 0.05 * (1 - ease_out(u / 0.35))) * (1 + 0.025 * u / dur)

def vshot(name, s0, s1, zoom=1.0, cx=.5, cy=.5, settle=True, punch=None):
    def f(t, dur, w=W, h=H):
        st = s0 + (s1 - s0) * (t / dur)
        z = zoom * (settle_push(t, dur) if settle else 1.0)
        if punch is not None and t >= punch: z *= 1 + 0.14 * ease_out((t - punch) / 0.25)
        return reframe(video(name, st), w, h, z, cx, cy)
    return f

def ramp_shot(name, s0, s1):
    n = 400
    sp = np.array([2.6 - 1.9 * math.sin(math.pi * clamp((i / n - 0.15) / 0.7)) for i in range(n)])
    cum = np.concatenate([[0], np.cumsum(sp)]); cum /= cum[-1]
    def f(t, dur, w=W, h=H):
        u = t / dur
        st = s0 + (s1 - s0) * np.interp(clamp(u), np.linspace(0, 1, n + 1), cum) if 0 <= u <= 1 else s0 + (s1 - s0) * u
        return reframe(video(name, st), w, h, settle_push(t, dur))
    return f

def kb(key, z0, z1, c0, c1):
    def f(t, dur, w=W, h=H):
        u = ease_io(t / dur)
        return reframe(photo(key), w, h, lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u))
    return f

MASKS = {}
def rmask(w, h, rad=30):
    if (w, h) not in MASKS:
        m = np.zeros((h * 2, w * 2), np.uint8)
        cv2.rectangle(m, (rad * 2, 0), (w * 2 - rad * 2, h * 2), 255, -1)
        cv2.rectangle(m, (0, rad * 2), (w * 2, h * 2 - rad * 2), 255, -1)
        for cx_, cy_ in [(rad * 2, rad * 2), (w * 2 - rad * 2, rad * 2), (rad * 2, h * 2 - rad * 2), (w * 2 - rad * 2, h * 2 - rad * 2)]:
            cv2.circle(m, (cx_, cy_), rad * 2, 255, -1, cv2.LINE_AA)
        MASKS[(w, h)] = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)[..., None].astype(np.float32) / 255
    return MASKS[(w, h)]

def paste(canvas, img, x, y):
    h, w = img.shape[:2]; m = rmask(w, h)
    x, y = int(round(x)), int(round(y))
    X0, Y0, X1, Y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if X1 <= X0 or Y1 <= Y0: return
    sub, mm = img[Y0 - y:Y1 - y, X0 - x:X1 - x], m[Y0 - y:Y1 - y, X0 - x:X1 - x]
    canvas[Y0:Y1, X0:X1] = sub * mm + canvas[Y0:Y1, X0:X1] * (1 - mm)

def layout_shot(panels, stagger=0.12, slide=0.42):
    """panels: list of (x,y,w,h, [(t_from, source_fn), ...], from_dir)"""
    def f(t, dur, w=W, h=H):
        srcs0 = panels[0][4]; s0 = [s for s in srcs0 if t >= s[0]] or srcs0[:1]
        small = s0[-1][1](max(0, t - s0[-1][0]), dur - s0[-1][0], 270, 480)
        cv = cv2.resize(cv2.GaussianBlur(small, (0, 0), 9), (W, H)) * 0.38 + BG * 0.3
        for i, (x, y, pw, ph, srcs, d) in enumerate(panels):
            src = [s for s in srcs if t >= s[0] - 1e-6]
            t0, fn = src[-1] if src else srcs[0]
            img = fn(t - t0 if src else 0, dur - t0, pw, ph)
            if len(srcs) > 1 and src and t0 > 0 and t - t0 < 0.07:  # 2-frame flash on panel swap
                img = np.clip(img + 0.55, 0, 1)
            u = ease_out((t - i * stagger) / slide)
            ox = (1 - u) * (W + 40) * d[0]; oy = (1 - u) * (H + 40) * d[1]
            paste(cv, img, x + ox, y + oy)
        return cv
    return f

def split_open(top_fn, bot_fn):
    def f(t, dur, w=W, h=H):
        u = ease_out((t - 0.5) / 0.38)
        th = int(round(lerp(H, 956, u)))
        cv = np.empty((H, W, 3), np.float32); cv[:] = BG
        top = top_fn(t, dur, W, th)
        if u < 1e-3: cv[:] = top
        else: paste(cv, top, 0, 0)
        if u > 0: paste(cv, bot_fn(t, dur, W, 956), 0, lerp(H + 20, 964, u))
        return cv
    return f

# ---------------- timeline ----------------
G = 'IMG_0642'; J = 'IMG_0672'; C = 'IMG_0712'; Y = 'IMG_0714'
HERO, BL, BR = (0, 0, 1080, 1150), (0, 1158, 536, 762), (544, 1158, 536, 762)
SHOTS = [
    (0.0, 2.0, vshot(J, 1.5, 4.5, 1.04)),
    (2.0, 4.0, kb('pano', 1.08, 1.16, (0.30, 0.55), (0.62, 0.55))),
    (4.0, 6.5, vshot(Y, 0.3, 2.8, 1.02)),
    (6.5, 8.5, vshot(G, 0.0, 2.0, 1.04, cy=0.45)),
    (8.5, 12.0, layout_shot([
        (*HERO, [(0, kb('horse', 1.0, 1.08, (.45, .4), (.4, .35))), (1.75, kb('wall', 1.0, 1.1, (.5, .5), (.5, .45)))], (0, -1)),
        (*BL, [(0, kb('armour', 1.0, 1.1, (.5, .4), (.5, .35))), (1.87, kb('pratap', 1.0, 1.06, (.5, .45), (.5, .4)))], (-1, 0)),
        (*BR, [(0, kb('daggers', 1.0, 1.1, (.5, .5), (.45, .45))), (1.99, kb('facade', 1.0, 1.08, (.5, .5), (.5, .45)))], (1, 0))])),
    (12.0, 15.5, ramp_shot(C, 1.0, 8.4)),
    (15.5, 17.5, kb('vani', 1.0, 1.14, (0.5, 0.5), (0.5, 0.52))),
    (17.5, 20.5, split_open(vshot(J, 6.5, 9.5, 1.0), kb('garden', 1.0, 1.1, (.5, .5), (.5, .55)))),
    (20.5, 23.5, layout_shot([
        (0, 0, 536, 956, [(0, vshot(C, 1.0, 4.0, settle=False))], (-1, 0)),
        (544, 0, 536, 956, [(0, vshot(J, 5.0, 8.0, settle=False))], (1, 0)),
        (0, 964, 536, 956, [(0, vshot(Y, 0.3, 3.3, settle=False))], (-1, 0)),
        (544, 964, 536, 956, [(0, vshot(G, 0.0, 2.0, cy=0.45, settle=False))], (1, 0))])),
    (23.5, 27.0, vshot(Y, 3.5, 7.0, 1.0, punch=1.5)),
    (27.0, 30.5, kb('pano', 1.05, 1.22, (0.28, 0.5), (0.22, 0.5))),
]
END = (30.5, DUR)
# transitions at shot boundaries: (time, kind, length)
TRANS = [(2.0, 'zoom', 0.30), (4.0, 'whip', 0.24), (6.5, 'whipv', 0.24), (8.5, 'cut', 0), (12.0, 'zoom', 0.30),
         (15.5, 'leak', 0.6), (17.5, 'whip', 0.24), (20.5, 'cut', 0), (23.5, 'zoom', 0.30), (27.0, 'leak', 0.6),
         (30.5, 'end', 0.4)]

def render_shot(i, t):
    a, b, fn = SHOTS[i]
    return fn(t - a, b - a)

def blur(img, k):
    k = int(k) | 1
    return img if k < 3 else cv2.GaussianBlur(img, (k, k), 0)

def zoom_img(img, z):
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def end_bg(t):
    last = SHOTS[-1]
    img = last[2](min(t - last[0], last[1] - last[0] + 1.0), last[1] - last[0])
    return img

def transition(kind, A, B, w):
    if kind == 'zoom':
        if w < 0.5:
            u = ease_in(w * 2); return blur(zoom_img(A, 1 + 1.3 * u), 2 + 60 * u)
        u = ease_out((w - 0.5) * 2); return blur(zoom_img(B, 1.6 - 0.6 * u), 2 + 60 * (1 - u))
    if kind in ('whip', 'whipv'):
        u = ease_io(w)
        if kind == 'whip':
            strip = np.concatenate([A, B], 1); off = int(u * W)
            fr = strip[:, off:off + W]
            k = int(2 + 140 * math.sin(math.pi * w)) | 1
            return cv2.blur(fr, (k, 1))
        strip = np.concatenate([A, B], 0); off = int(u * H)
        fr = strip[off:off + H]
        k = int(2 + 160 * math.sin(math.pi * w)) | 1
        return cv2.blur(fr, (1, k))
    if kind == 'leak':
        mix = A * (1 - ease_io(w)) + B * ease_io(w)
        cx = lerp(-0.25 * W, 1.25 * W, w)
        leak = np.exp(-(((xx - cx) / 520) ** 2 + ((yy - 0.35 * H) / 900) ** 2))[..., None]
        col = np.array([0.25, 0.62, 1.0], np.float32)  # warm amber, BGR
        L = leak * col * (0.85 * math.sin(math.pi * w))
        return 1 - (1 - mix) * (1 - L)
    if kind == 'blur':
        u = ease_io(w); k = 2 + 50 * math.sin(math.pi * w)
        return blur(A * (1 - u) + B * u, k)
    return B if w >= 0.5 else A

# ---------------- logo ----------------
def load_logo(path, width):
    im = Image.open(path).convert('RGBA'); h = int(im.height * width / im.width)
    a = np.array(im.resize((width, h), Image.LANCZOS)).astype(np.float32) / 255
    return a[..., [2, 1, 0]], a[..., 3:4]
BUG_RGB, BUG_A = load_logo(f'{AS_DIR}/travlink_logo_white.png', 118)
END_RGB, END_A = load_logo(f'{AS_DIR}/travlink_logo_white.png', 470)

def over(cv, rgb, a, x, y, op=1.0):
    h, w = a.shape[:2]; x, y = int(x), int(y)
    X0, Y0, X1, Y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if X1 <= X0 or Y1 <= Y0: return
    aa = a[Y0 - y:Y1 - y, X0 - x:X1 - x] * op
    cv[Y0:Y1, X0:X1] = rgb[Y0 - y:Y1 - y, X0 - x:X1 - x] * aa + cv[Y0:Y1, X0:X1] * (1 - aa)

def bug(cv, t):
    if t >= END[0]: return
    u = ease_out(t / 0.5); op = 0.88 * (1 - ease_io((t - (END[0] - 0.3)) / 0.3))
    x = W - 56 - 118 + (1 - u) * 260; y = 118
    sh = cv2.GaussianBlur(np.pad(BUG_A, ((12, 12), (12, 12), (0, 0)))[..., 0], (0, 0), 6)[..., None]
    over(cv, np.zeros_like(np.pad(BUG_RGB, ((12, 12), (12, 12), (0, 0)))), sh, x - 12 + 3, y - 12 + 4, op * 0.55)
    over(cv, BUG_RGB, BUG_A, x, y, op)

GLOW = None
def end_card(cv, t):
    global GLOW
    u = (t - END[0])
    if GLOW is None:
        g = cv2.GaussianBlur(np.pad(END_A, ((120, 120), (120, 120), (0, 0)))[..., 0], (0, 0), 48)[..., None]
        GLOW = (g / g.max(), np.ones_like(g) * np.array([0.94, 0.31, 0.0], np.float32))  # brand blue (0,80,239)
    s = 0.6 + 0.4 * back_out((u - 0.15) / 0.55)
    op = ease_out((u - 0.15) / 0.35)
    if op <= 0: return
    a = cv2.resize(END_A, None, fx=s, fy=s)[..., None]; rgb = cv2.resize(END_RGB, None, fx=s, fy=s)
    ga = cv2.resize(GLOW[0], None, fx=s, fy=s)[..., None]
    gx, gy = W / 2 - ga.shape[1] / 2, H * 0.46 - ga.shape[0] / 2
    gl = np.ones(ga.shape[:2] + (3,), np.float32) * np.array([0.94, 0.31, 0.0], np.float32)
    over(cv, gl, np.clip(ga * 1.1, 0, 1), gx, gy, op * 0.75)
    over(cv, rgb, a, W / 2 - a.shape[1] / 2, H * 0.46 - a.shape[0] / 2, op)

# ---------------- frame ----------------
def frame(n):
    t = n / FPS
    if t >= END[0] - TRANS[-1][2] / 2:
        bg = end_bg(t)
        w = clamp((t - (END[0] - 0.2)) / 0.4)
        dark = blur(bg, 1 + 70 * ease_io(w)) * (1 - 0.5 * ease_io(w))
        img = dark
    else:
        img = None
        for (tb, kind, L) in TRANS[:-1]:
            if L and tb - L / 2 <= t < tb + L / 2:
                i = [k for k, s in enumerate(SHOTS) if abs(s[0] - tb) < 1e-6][0]
                img = transition(kind, render_shot(i - 1, t), render_shot(i, t), (t - (tb - L / 2)) / L)
                break
        if img is None:
            i = max(k for k, s in enumerate(SHOTS) if s[0] <= t + 1e-9)
            img = render_shot(i, t)
    img = img * VIGNETTE + GRAIN[n % 6]
    img = np.clip(img, 0, 1)
    bug(img, t)
    if t >= END[0]: end_card(img, t)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()

if __name__ == '__main__':
    N = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', OUT], stdin=subprocess.PIPE)
    only = os.environ.get('FRAMES')
    frames = [int(x) for x in only.split(',')] if only else range(N)
    with Pool(4) as p:
        for k, buf in enumerate(p.imap(frame, frames, chunksize=4)):
            ff.stdin.write(buf)
            if k % 60 == 0: print(f'{k}/{len(frames)}', flush=True)
    ff.stdin.close(); ff.wait()
