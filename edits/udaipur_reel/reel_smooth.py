"""City Palace reel, re-edited with smooth transitions only.
LABELS=1 renders the learning version (each transition named on screen); LABELS=0 the clean posting version.
Usage: LABELS=1 python3 reel_smooth.py <graded_frames_dir> <photos_dir> <assets_dir> <out.mp4> <sfx_out.wav>"""
import sys, os, math, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FR, PH, AS, OUT, SFX_OUT = sys.argv[1:6]
sys.argv = [sys.argv[0], FR, PH, AS, OUT]
import render as R
from render import (W, H, ease_out, ease_in, ease_io, back_out, clamp, lerp, reframe, video, photo, blur,
                    zoom_img, paste, vshot, ramp_shot, kb, split_open)
R.vframe = functools.lru_cache(maxsize=12)(R.vframe.__wrapped__)
FPS, DUR = 24, 33.0
R.END = (30.85, DUR)  # logo drops after the logo wipe completes
LABELS = os.environ.get('LABELS', '1') == '1'
J, Y, G, C = 'IMG_0672', 'IMG_0714', 'IMG_0642', 'IMG_0712'
xx = np.tile(np.arange(W, dtype=np.float32), (H, 1)); yy = np.tile(np.arange(H, dtype=np.float32)[:, None], (1, W))

# ---------------- shots ----------------
def layout(panels):
    """static panels; each panel: (x,y,w,h,[(t_from, fn), ...]) with 0.5 s crossfades between its sources"""
    def f(t, dur, w=W, h=H):
        fn0 = panels[0][4][0][1]
        small = fn0(max(t, 0), dur, 270, 480)
        cv = cv2.resize(cv2.GaussianBlur(small, (0, 0), 9), (W, H)) * 0.38 + R.BG * 0.3
        for (x, y, pw, ph, srcs) in panels:
            cur = [k for k, s in enumerate(srcs) if t >= s[0]] or [0]; k = cur[-1]
            t0, fn = srcs[k]; img = fn(t - t0 if t >= t0 else 0, dur - t0, pw, ph)
            if k > 0 and t - t0 < 0.5:
                pt0, pfn = srcs[k - 1]; u = ease_io((t - t0) / 0.5)
                img = pfn(t - pt0, dur - pt0, pw, ph) * (1 - u) + img * u
            paste(cv, img, x, y)
        return cv
    return f

def vshot_smooth_punch(name, s0, s1, at):
    def f(t, dur, w=W, h=H):
        z = (1 + 0.03 * t / dur) * (1 + 0.12 * ease_io((t - at) / 0.8))
        return reframe(video(name, s0 + (s1 - s0) * t / dur), w, h, z)
    return f

HERO, BL, BR = (0, 0, 1080, 1150), (0, 1158, 536, 762), (544, 1158, 536, 762)
SHOTS = [
    (0.0, 2.0, vshot(J, 3.25, 5.25, 1.02)),
    (2.0, 4.0, kb('pano', 1.08, 1.16, (0.30, 0.55), (0.62, 0.55))),
    (4.0, 6.5, vshot(Y, 0.3, 2.8, 1.02)),
    (6.5, 8.5, vshot(G, 0.0, 2.0, 1.04, cy=0.45)),
    (8.5, 12.0, layout([
        (*HERO, [(0, kb('horse', 1.0, 1.08, (.45, .4), (.4, .35))), (1.75, kb('wall', 1.0, 1.1, (.5, .5), (.5, .45)))]),
        (*BL, [(0, kb('armour', 1.0, 1.1, (.5, .4), (.5, .35))), (1.95, kb('pratap', 1.0, 1.06, (.5, .45), (.5, .4)))]),
        (*BR, [(0, kb('daggers', 1.0, 1.1, (.5, .5), (.45, .45))), (2.15, kb('facade', 1.0, 1.08, (.5, .5), (.5, .45)))])])),
    (12.0, 15.5, ramp_shot(C, 1.0, 8.4)),
    (15.5, 17.5, kb('vani', 1.0, 1.14, (0.5, 0.5), (0.5, 0.52))),
    (17.5, 20.5, split_open(vshot(J, 6.5, 9.5, 1.0), kb('garden', 1.0, 1.1, (.5, .5), (.5, .55)))),
    (20.5, 23.5, layout([
        (0, 0, 536, 956, [(0, vshot(C, 1.0, 4.0, settle=False))]),
        (544, 0, 536, 956, [(0, vshot(J, 5.0, 8.0, settle=False))]),
        (0, 964, 536, 956, [(0, vshot(Y, 0.3, 3.3, settle=False))]),
        (544, 964, 536, 956, [(0, vshot(G, 0.0, 2.0, cy=0.45, settle=False))])])),
    (23.5, 27.0, vshot_smooth_punch(Y, 3.5, 7.0, 1.3)),
    (27.0, 30.5, kb('pano', 1.05, 1.22, (0.28, 0.5), (0.22, 0.5))),
]
END0 = 30.5

def end_bg(t):
    a, b, fn = SHOTS[-1]
    img = fn(min(t - a, b - a + 1.0), b - a)
    return blur(img, 71) * 0.5

# ---------------- smooth transitions ----------------
def lum(f): return f[..., 0] * 0.114 + f[..., 1] * 0.587 + f[..., 2] * 0.299

def tr_zoom(A, B, w):
    u = ease_io(w)
    a = zoom_img(A, 1 + 0.35 * ease_in(w)); b = zoom_img(B, 1.25 - 0.25 * ease_out(w))
    m = ease_io((w - 0.3) / 0.4)
    return blur(a * (1 - m) + b * m, 1 + 28 * math.sin(math.pi * w))

def tr_luma(A, B, w):
    th = 1.15 - 1.4 * ease_io(w)
    m = np.clip((lum(B) - th) / 0.25, 0, 1)[..., None]
    return A * (1 - m) + B * m

def tr_cross(A, B, w):
    u = ease_io(w); return A * (1 - u) + B * u

def tr_blur(A, B, w): return R.transition('blur', A, B, w)
def tr_leak(A, B, w): return R.transition('leak', A, B, w)

ARCH = None
def arch_mask(scale):
    # Rajasthani arch: tall rectangle with a pointed (ogee-like) top, centred
    aw, ah = 420 * scale, 760 * scale
    cx, base = W / 2, H / 2 + ah / 2
    top = base - ah; spring = top + aw * 0.55
    m = np.zeros((H, W), np.uint8)
    pts = []
    for k in range(41):
        a = k / 40
        x = cx - aw / 2 + aw * a
        # pointed arch: two arcs meeting at a point
        d = abs(a - 0.5) * 2
        y = spring - (aw * 0.55) * (1 - d ** 1.6) ** 0.8 - (aw * 0.08) * (1 - d) ** 6
        pts.append((x, y))
    poly = [(cx - aw / 2, base), *pts, (cx + aw / 2, base)]
    cv2.fillPoly(m, [np.int32(np.round(poly))], 255, cv2.LINE_AA)
    return m.astype(np.float32) / 255

def tr_arch(A, B, w):
    s = lerp(0.05, 4.6, ease_in(clamp(w * 1.05)))
    m = cv2.GaussianBlur(arch_mask(s), (0, 0), 3)[..., None]
    edge = np.clip(cv2.GaussianBlur(m[..., 0], (0, 0), 9) - m[..., 0] * 0.0, 0, 1)
    ring = np.clip(np.abs(cv2.Laplacian(m[..., 0], cv2.CV_32F, ksize=5)) * 3, 0, 1)
    ring = cv2.GaussianBlur(ring, (0, 0), 4)[..., None] * np.array([0.35, 0.75, 1.0], np.float32) * 0.8 * (1 - w)
    return np.clip(A * (1 - m) + B * m + ring, 0, 1)

def tr_tilt(A, B, w):
    u = ease_io(w); strip = np.concatenate([A, B], 0); off = int(u * H)
    k = int(1 + 70 * math.sin(math.pi * w)) | 1
    return cv2.blur(strip[off:off + H], (1, k))

def tr_push(A, B, w):
    u = ease_io(w); strip = np.concatenate([A, B], 1); off = int(u * W)
    k = int(1 + 50 * math.sin(math.pi * w)) | 1
    return cv2.blur(strip[:, off:off + W], (k, 1))

def tr_mask(A, B, w):
    u = ease_io(w); x = lerp(-460, W + 460, u)
    out = np.where((xx < x)[..., None], B, A)
    pillar = np.clip(1 - np.abs(xx - x) / 230, 0, 1) ** 0.6
    shade = (pillar * 0.94)[..., None]
    return out * (1 - shade) + np.array([0.05, 0.07, 0.09], np.float32) * shade

def tr_dip_white(A, B, w):
    if w < 0.5: u = ease_in(w * 2); return A * (1 - u) + 0.97 * u
    u = ease_out((w - 0.5) * 2); return 0.97 * (1 - u) + B * u

LOGO_A_BIG = None
def tr_logo(A, B, w):
    global LOGO_A_BIG
    if LOGO_A_BIG is None:
        im = Image.open(f'{AS}/travlink_logo_white.png').convert('RGBA')
        LOGO_A_BIG = np.array(im)[..., 3].astype(np.float32) / 255
        ys, xs = np.nonzero(LOGO_A_BIG > 0.5)
        LOGO_A_BIG = LOGO_A_BIG[:int(ys.max() * 0.78)]  # icon only (drop wordmark)
    s = lerp(0.12, 9.0, ease_in(w)) * 400 / LOGO_A_BIG.shape[1]
    M = np.float32([[s, 0, W / 2 - LOGO_A_BIG.shape[1] * s / 2], [0, s, H * 0.46 - LOGO_A_BIG.shape[0] * s / 2]])
    m = cv2.warpAffine(LOGO_A_BIG, M, (W, H), flags=cv2.INTER_LINEAR)
    m = np.maximum(m, ease_in(clamp((w - 0.75) / 0.25)))[..., None]
    return A * (1 - m) + B * m

TRANS = [  # time, fn, length, name, when-to-use
    (2.0, tr_zoom, 0.50, 'Smooth zoom', 'Carry the camera push into the next place'),
    (4.0, tr_luma, 0.70, 'Luma fade', 'Light flows into the next scene · golden-hour moments'),
    (6.5, tr_cross, 0.25, 'Match cut', 'Same pattern in both shots · here, chequered floors'),
    (8.5, tr_blur, 0.50, 'Blur dissolve', 'Soft entry into a split screen or cutaway'),
    (12.0, tr_arch, 0.70, 'Arch wipe', 'Reveal through a heritage arch · palaces, forts, temples'),
    (15.5, tr_leak, 0.70, 'Light leak', 'Warm emotional beat · before a highlight or CTA'),
    (17.5, tr_tilt, 0.60, 'Tilt transition', 'Feels like one continuous camera move'),
    (20.5, tr_push, 0.55, 'Smooth push', 'Next chapter without breaking the rhythm'),
    (23.5, tr_mask, 0.65, 'Mask wipe', 'Pass behind a pillar or wall into the next scene'),
    (27.0, tr_dip_white, 0.70, 'Dip to white', 'Time or place change · airy, dreamy feel'),
    (30.5, tr_logo, 0.80, 'Logo wipe', 'Branded close into the end card · once per reel'),
]

def shot_at(t):
    i = max(k for k, s in enumerate(SHOTS) if s[0] <= t + 1e-9) if t < END0 else None
    return i

def render_shot(i, t):
    if i is None: return end_bg(t)
    a, b, fn = SHOTS[i]; return fn(t - a, b - a)

def base_frame(t):
    for (tb, fn, L, *_r) in TRANS:
        if tb - L / 2 <= t < tb + L / 2:
            ia = shot_at(tb - 1e-3); ib = shot_at(tb + 1e-3)
            return fn(render_shot(ia, t), render_shot(ib, t), (t - (tb - L / 2)) / L)
    return render_shot(shot_at(t), t)

# ---------------- labels ----------------
FONT_BIG = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
FONT_MID = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
FONT_KICK = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
BLUE = (0, 80, 239)
def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0], b[3] - b[1], b[1]

@functools.lru_cache(maxsize=16)
def label_img(k):
    tb, fn, L, name, desc = TRANS[k]
    kick = f'SMOOTH TRANSITION {k + 1:02d}/{len(TRANS)}'
    img = Image.new('RGBA', (W, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fk, fn_, fd = ImageFont.truetype(FONT_KICK, 28), ImageFont.truetype(FONT_BIG, 84), ImageFont.truetype(FONT_MID, 40)
    kw, kh, ko = tw(d, kick, fk); nw, nh, no = tw(d, name, fn_); dw, dh, do = tw(d, desc, fd)
    while dw > 900: fd = ImageFont.truetype(FONT_MID, fd.size - 2); dw, dh, do = tw(d, desc, fd)
    pill_h = kh + 28; y_name = pill_h + 30; y_desc = y_name + nh + 24
    cw = max(nw, dw) + 90
    d.rounded_rectangle((W // 2 - cw // 2, pill_h // 2 + 6, W // 2 + cw // 2, y_desc + dh + 34), radius=34, fill=(10, 12, 16, 160))
    d.rounded_rectangle((W // 2 - kw // 2 - 24, 0, W // 2 + kw // 2 + 24, pill_h), radius=pill_h // 2, fill=BLUE + (255,))
    d.text((W // 2 - kw // 2, 14 - ko), kick, font=fk, fill=(255, 255, 255, 255))
    d.text((W // 2 - nw // 2, y_name - no), name, font=fn_, fill=(255, 255, 255, 255))
    d.text((W // 2 - dw // 2, y_desc - do), desc, font=fd, fill=(255, 236, 205, 255))
    a = np.array(img).astype(np.float32) / 255
    return a[..., [2, 1, 0]], a[..., 3:4]

def draw_label(img, t):
    for k, (tb, fn, L, name, desc) in enumerate(TRANS):
        t_in, t_out = tb - L / 2 - 0.25, min(tb + L / 2 + 1.1, TRANS[k + 1][0] - TRANS[k + 1][2] / 2 - 0.3) if k + 1 < len(TRANS) else tb + L / 2 + 0.6
        if t_in <= t < t_out:
            op = min(ease_out((t - t_in) / 0.25), ease_out((t_out - t) / 0.25))
            rgb, a = label_img(k)
            R.over(img, rgb, a, 0, 1290 + (1 - op) * 24, op)

# ---------------- frame ----------------
def frame(n):
    t = n / FPS
    img = base_frame(t)
    img = np.clip(img * R.VIGNETTE + R.GRAIN[n % 6], 0, 1)
    R.bug(img, t)
    if t >= END0: R.end_card(img, t)
    if LABELS: draw_label(img, t)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()

# ---------------- sfx (soft, long whooshes) ----------------
def build_sfx():
    import soundfile as sf
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sfx.py')).read().split('# transitions (centred on the cut)')[0]
    ns = {}; exec(src, ns)
    place = ns['place']
    for (tb, fn, L, name, _d) in TRANS[:-1]:
        place(ns['whoosh'](max(0.7, L + 0.3), 180, 1600), tb - max(0.7, L + 0.3) / 2, 0.20)
    place(ns['whoosh'](1.0, 200, 2000), 30.5 - 0.5, 0.18)
    place(ns['chime'](), 30.95, 0.26)
    mix = ns['mix']; mix *= 10 ** (-3 / 20) / np.abs(mix).max()
    sf.write(SFX_OUT, mix, 48000)

if __name__ == '__main__':
    from multiprocessing import Pool
    build_sfx()
    N = int(DUR * FPS)
    only = os.environ.get('FRAMES')
    frames = [int(x) for x in only.split(',')] if only else list(range(N))
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', OUT], stdin=subprocess.PIPE)
    B = 48
    with Pool(4, maxtasksperchild=40) as p:
        for b0 in range(0, len(frames), B):
            for buf in p.imap(frame, frames[b0:b0 + B], chunksize=4):
                ff.stdin.write(buf)
            if b0 % 240 == 0: print(f'{b0}/{len(frames)}', flush=True)
    ff.stdin.close(); ff.wait()
