"""TravLink Edit Guide: every transition, split-screen layout and panel animation from the playbook,
labelled on screen. Reuses the reel's sources, grade and transition code (render.py).
Usage: python3 glossary.py <graded_frames_dir> <photos_dir> <assets_dir> <out.mp4> <sfx_out.wav>"""
import sys, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FR, PH, AS, OUT, SFX_OUT = sys.argv[1:6]
sys.argv = [sys.argv[0], FR, PH, AS, OUT]
import render as R
from render import W, H, ease_out, ease_io, ease_in, back_out, clamp, lerp, reframe, video, photo, blur, zoom_img, paste

FPS = 24
import functools
R.vframe = functools.lru_cache(maxsize=10)(R.vframe.__wrapped__)  # keep worker memory low
FONT_BIG = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
FONT_MID = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
FONT_KICK = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
BLUE = (0, 80, 239)

# ---------------- sources (real-time clips + photo moves) ----------------
def clip(name, s0, zoom=1.02, cy=0.5):
    return lambda t, dur=0, w=W, h=H: reframe(video(name, s0 + t), w, h, zoom * (1 + 0.012 * t), 0.5, cy)

def still(key, z0=1.0, z1=1.12, c0=(.5, .5), c1=(.5, .5), D=3.0):
    def f(t, dur=0, w=W, h=H):
        u = ease_io(t / D)
        return reframe(photo(key), w, h, lerp(z0, z1, u), lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u))
    return f

J, Y, G, C = 'IMG_0672', 'IMG_0714', 'IMG_0642', 'IMG_0712'
SRC = {
    'jali': clip(J, 3.3), 'jali2': clip(J, 6.6), 'court': clip(Y, 0.4), 'court2': clip(Y, 3.6),
    'yard': clip(G, 0.0, cy=0.45), 'corr': clip(C, 1.2), 'corr2': clip(C, 4.5),
    'pano': still('pano', 1.08, 1.16, (.35, .55), (.55, .55)), 'pano2': still('pano', 1.05, 1.2, (.25, .5), (.22, .5)),
    'vani': still('vani', 1.0, 1.12), 'garden': still('garden', 1.0, 1.1), 'horse': still('horse', 1.0, 1.08, (.45, .4), (.4, .35)),
    'armour': still('armour'), 'daggers': still('daggers'), 'wall': still('wall'), 'pratap': still('pratap', 1, 1.06),
    'facade': still('facade'),
}

# ---------------- extra transitions ----------------
def t_glitch(A, B, w):
    base = A if w < 0.5 else B
    rng = np.random.default_rng(int(w * 1000))
    out = base.copy()
    sh = int(18 + 40 * math.sin(math.pi * w))
    out[..., 2] = np.roll(base[..., 2], sh, 1); out[..., 0] = np.roll(base[..., 0], -sh, 1)
    for _ in range(7):  # displaced slices
        y0 = rng.integers(0, H - 120); hgt = rng.integers(20, 120); dx = int(rng.integers(-120, 120))
        out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], dx, 1)
    return out

def t_circle(A, B, w):
    r = ease_io(w) * math.hypot(W, H) / 2 * 1.05
    m = np.zeros((H, W), np.float32); cv2.circle(m, (W // 2, H // 2), int(r), 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 3)[..., None]
    out = A * (1 - m) + B * m
    ring = np.zeros((H, W), np.float32); cv2.circle(ring, (W // 2, H // 2), int(r), 1.0, 6, cv2.LINE_AA)
    return np.clip(out + cv2.GaussianBlur(ring, (0, 0), 4)[..., None] * 0.6, 0, 1)

def t_mask(A, B, w):
    # a dark foreground 'pillar' sweeps across; shots swap behind it
    u = ease_io(w); x = lerp(-420, W + 420, u)
    edge = np.clip((xx_ - x) / 40, -1, 1)
    out = np.where((xx_ < x)[..., None], B, A)
    pillar = np.clip(1 - np.abs(xx_ - x) / 210, 0, 1) ** 0.6
    shade = (pillar * 0.92)[..., None]
    col = np.array([0.05, 0.07, 0.09], np.float32)
    return out * (1 - shade) + col * shade

def t_smash(A, B, w):
    return np.clip(B + 0.9, 0, 1) if w < 0.25 else (np.clip(B + 0.4, 0, 1) if w < 0.5 else B)

def t_dissolve(A, B, w):
    return R.transition('blur', A, B, w)

xx_ = np.tile(np.arange(W, dtype=np.float32), (H, 1))

def T(kind):
    if kind == 'cut': return lambda A, B, w: A if w < 0.5 else B
    if kind == 'smash': return t_smash
    if kind == 'glitch': return t_glitch
    if kind == 'circle': return t_circle
    if kind == 'mask': return t_mask
    if kind == 'dissolve': return t_dissolve
    return lambda A, B, w: R.transition(kind, A, B, w)

# ---------------- segments ----------------
SEG = []  # dicts: dur, fn(t)->frame, label, badge, sfx
def add(dur, fn, label=None, badge=None, sfx=()):
    SEG.append(dict(dur=dur, fn=fn, label=label, badge=badge, sfx=sfx))

def card_bg(src, dim=0.45):
    return lambda t: blur(src(t), 61) * dim

# title
add(2.6, card_bg(SRC['pano2'], 0.5), label=('TRAVLINK', 'Edit Guide', 'Transitions · Layouts · Panel animations', 'title'), sfx=(('chime', 0.2),))

TRANS = [
    ('Hard cut', 'cut', 0.084, 'Instant switch · cut on the beat', 'jali', 'pano'),
    ('Smash cut', 'smash', 0.084, 'Hard cut + 2-frame white flash · impact, contrast', 'court', 'vani'),
    ('Blur dissolve', 'dissolve', 0.30, '0.24–0.3 s · into cutaways and the end card', 'corr', 'garden'),
    ('Whip pan', 'whip', 0.25, '0.20–0.25 s · location to location', 'yard', 'court2'),
    ('Vertical whip', 'whipv', 0.25, '0.25 s · tilts, top-to-bottom energy', 'pano', 'corr2'),
    ('Zoom-through', 'zoom', 0.32, '0.3 s · hook into the first destination', 'jali2', 'court'),
    ('RGB glitch', 'glitch', 0.21, '4–6 frames · pattern interrupts, reveals', 'vani', 'yard'),
    ('Shape wipe', 'circle', 0.40, '0.35–0.4 s · reveal a new scene or offer', 'horse', 'jali'),
    ('Light leak', 'leak', 0.60, '0.4–0.7 s · emotional beats, before the CTA', 'court2', 'pano2'),
    ('Mask wipe', 'mask', 0.40, '0.3–0.4 s · through a pillar or doorway', 'corr', 'court'),
]
add(1.6, card_bg(SRC['court'], 0.42), label=('PART 1', 'Transitions', f'{len(TRANS)} ways to move between shots', 'section'), sfx=(('whoosh', 0.0),))
for k, (name, kind, L, desc, a, b) in enumerate(TRANS):
    A, B = SRC[a], SRC[b]; fn = T(kind); tb = 1.2
    def real(t, A=A, B=B, fn=fn, L=L, tb=tb):
        if t < tb - L / 2: return A(t)
        if t >= tb + L / 2: return B(t - (tb - L / 2))
        return fn(A(t), B(t - (tb - L / 2)), (t - (tb - L / 2)) / L)
    lab = (f'TRANSITION {k + 1:02d}/{len(TRANS)}', name, desc, 'item')
    add(tb + 1.1, real, label=lab, sfx=(('whoosh' if kind not in ('cut', 'smash') else 'impact', tb),))
    win = max(0.5, L / 2 + 0.35)
    add(win * 4, lambda t, real=real, tb=tb, win=win: real(tb - win + t * 0.5),
        label=lab, badge='SLOW-MO REPLAY  ·  0.5×')

# ---------------- layouts ----------------
def panels_frame(t, panels, bg_src=None):
    cv = np.empty((H, W, 3), np.float32); cv[:] = R.BG
    if bg_src is not None:
        cv[:] = cv2.resize(cv2.GaussianBlur(bg_src(t, 0, 270, 480), (0, 0), 9), (W, H)) * 0.35 + R.BG * 0.3
    for (x, y, w, h, src, op, sc) in panels:
        img = src(t, 0, w, h) * op
        if sc != 1.0:
            w2, h2 = int(w * sc), int(h * sc); img = cv2.resize(img, (w2, h2)); x, y = x - (w2 - w) / 2, y - (h2 - h) / 2
        paste(cv, img, x, y)
    return cv

LAY = [
    ('2-up stack', 'Before/after · expectation vs reality', [(0, 0, 1080, 956, 'jali2'), (0, 964, 1080, 956, 'pano')]),
    ('Side by side', 'This vs that · two places at once', [(0, 0, 536, 1920, 'corr'), (544, 0, 536, 1920, 'court')]),
    ('Triple stack', 'One trip, three vibes', [(0, 0, 1080, 634, 'pano2'), (0, 643, 1080, 634, 'vani'), (0, 1286, 1080, 634, 'yard')]),
    ('Hero + two', 'Destination hero + room & activity', [(0, 0, 1080, 1150, 'court'), (0, 1158, 536, 762, 'armour'), (544, 1158, 536, 762, 'daggers')]),
    ('Picture-in-picture', 'Host or reaction over footage', [(0, 0, 1080, 1920, 'corr2'), (680, 150, 360, 640, 'jali')]),
    ('2×2 grid', 'Day 1–4 itinerary · recap collage', [(0, 0, 536, 956, 'corr'), (544, 0, 536, 956, 'jali2'), (0, 964, 536, 956, 'court'), (544, 964, 536, 956, 'yard')]),
]
add(1.6, card_bg(SRC['vani'], 0.42), label=('PART 2', 'Split-screen layouts', 'Several shots on one 9:16 screen', 'section'), sfx=(('whoosh', 0.0),))
for k, (name, desc, ps) in enumerate(LAY):
    def lf(t, ps=ps):
        return panels_frame(t, [(x, y, w, h, SRC[s], 1.0, 1.0) for (x, y, w, h, s) in ps])
    add(3.0, lf, label=(f'LAYOUT {k + 1}/{len(LAY)}', name, desc, 'item'), sfx=(('pop', 0.0),))

# ---------------- panel animations ----------------
G4 = [(0, 0, 536, 956), (544, 0, 536, 956), (0, 964, 536, 956), (544, 964, 536, 956)]
def anim_stagger(t):
    srcs = ['court', 'jali2', 'corr', 'pano']; ps = []
    for i, (x, y, w, h) in enumerate(G4):
        u = ease_out((t - 0.5 - i * 0.12) / 0.4); d = -1 if i % 2 == 0 else 1
        ps.append((x + (1 - u) * (W + 40) * d, y, w, h, SRC[srcs[i]], 1.0, 1.0))
    return panels_frame(t, ps, SRC['court'])

def anim_split(t):
    return R.split_open(SRC['jali2'], SRC['pano'])(t - 0.4, 3.5)

def anim_merge(t):
    u = ease_io((t - 1.4) / 0.4)
    th = int(round(lerp(956, H, u)))
    cv = np.empty((H, W, 3), np.float32); cv[:] = R.BG
    paste(cv, SRC['court'](t, 0, W, 956), 0, lerp(964, H + 40, u))
    top = SRC['jali'](t, 0, W, th)
    if u >= 0.999: cv[:] = top
    else: paste(cv, top, 0, 0)
    return cv

def anim_active(t):
    rects = [(0, 0, 1080, 634), (0, 643, 1080, 634), (0, 1286, 1080, 634)]; srcs = ['pano2', 'corr', 'vani']
    act = int(t / 1.1) % 3; ps = []
    for i, (x, y, w, h) in enumerate(rects):
        on = i == act
        ps.append((x, y, w, h, SRC[srcs[i]], 1.0 if on else 0.55, 1.03 if on else 1.0))
    ps.sort(key=lambda p: p[6])  # active drawn last
    return panels_frame(t, ps)

def anim_swap(t):
    pool = [['court', 'horse', 'pratap'], ['jali2', 'daggers', 'vani'], ['corr', 'wall', 'garden'], ['yard', 'facade', 'pano']]
    step = int(t / 0.5); ps = []
    for i, (x, y, w, h) in enumerate(G4):
        n = max(0, (step - i + 3) // 4); key = pool[i][n % 3]
        img_src = SRC[key]
        flash = 1.0
        if step >= 1 and (step - 1) % 4 == i and (t % 0.5) < 0.084 and n > 0: flash = 1.6
        ps.append((x, y, w, h, img_src, flash, 1.0))
    return np.clip(panels_frame(t, ps), 0, 1)

ANIM = [
    ('Staggered slide-in', 'Panels arrive 0.12 s apart, ease-out', anim_stagger, (('whoosh', 0.5), ('whoosh', 0.62), ('whoosh', 0.74), ('whoosh', 0.86))),
    ('Split open', 'Full screen splits into panels on the beat', anim_split, (('whoosh', 0.85),)),
    ('Merge back', 'The winning shot fills the screen · use on the CTA', anim_merge, (('whoosh', 1.4),)),
    ('Active panel', 'Focus one panel, dim the rest to 55%', anim_active, (('pop', 0.0), ('pop', 1.1), ('pop', 2.2))),
    ('Panel swap', 'Layout stays, one panel changes per beat', anim_swap, tuple(('pop', 0.5 * s) for s in range(1, 7))),
]
add(1.6, card_bg(SRC['corr'], 0.42), label=('PART 3', 'Panel animations', 'How split screens move', 'section'), sfx=(('whoosh', 0.0),))
for k, (name, desc, fn, sfx) in enumerate(ANIM):
    add(3.4, fn, label=(f'PANEL ANIMATION {k + 1}/{len(ANIM)}', name, desc, 'item'), sfx=sfx)
add(2.4, card_bg(SRC['pano2'], 0.5), label=('TRAVLINK', 'Edit Guide', 'Pick by name when you brief the edit', 'end'), sfx=(('chime', 0.15),))

STARTS = np.cumsum([0] + [s['dur'] for s in SEG]); DUR = float(STARTS[-1])

# ---------------- labels (pre-rendered RGBA) ----------------
def text_w(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0], b[3] - b[1]

def make_label(kick, name, desc, kind):
    big = kind in ('title', 'end')
    img = Image.new('RGBA', (W, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fk = ImageFont.truetype(FONT_KICK, 30); fn = ImageFont.truetype(FONT_BIG, 118 if big or kind == 'section' else 96)
    fd = ImageFont.truetype(FONT_MID, 46)
    # fit name
    while text_w(d, name, fn)[0] > 960: fn = ImageFont.truetype(FONT_BIG, fn.size - 4)
    kw, kh = text_w(d, kick, fk); nw, nh = text_w(d, name, fn); dw, dh = text_w(d, desc, fd)
    while dw > 900: fd = ImageFont.truetype(FONT_MID, fd.size - 2); dw, dh = text_w(d, desc, fd)
    y = 60
    pill = (W // 2 - kw // 2 - 26, y, W // 2 + kw // 2 + 26, y + kh + 30)
    d.rounded_rectangle(pill, radius=(kh + 30) // 2, fill=BLUE + (255,))
    d.text((W // 2 - kw // 2, y + 15 - d.textbbox((0, 0), kick, font=fk)[1]), kick, font=fk, fill=(255, 255, 255, 255))
    y = pill[3] + 26
    ny = y - d.textbbox((0, 0), name, font=fn)[1]
    # translucent dark card behind name + description for readability on any footage
    cw = max(nw, dw) + 90; dy0 = y + nh + 28
    card = Image.new('RGBA', img.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((W // 2 - cw // 2, y - 26, W // 2 + cw // 2, dy0 + dh + 34), radius=34, fill=(10, 12, 16, 150))
    card.alpha_composite(img); img = card; d = ImageDraw.Draw(img)
    d.rounded_rectangle(pill, radius=(kh + 30) // 2, fill=BLUE + (255,))
    d.text((W // 2 - kw // 2, pill[1] + 15 - d.textbbox((0, 0), kick, font=fk)[1]), kick, font=fk, fill=(255, 255, 255, 255))
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.text((W // 2 - nw // 2, ny + 4), name, font=fn, fill=(0, 0, 0, 200))
    dy = y + nh + 28; sd.text((W // 2 - dw // 2, dy - d.textbbox((0, 0), desc, font=fd)[1] + 3), desc, font=fd, fill=(0, 0, 0, 220))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    sh.alpha_composite(img); img = sh; d = ImageDraw.Draw(img)
    d.text((W // 2 - nw // 2, ny), name, font=fn, fill=(255, 255, 255, 255))
    d.text((W // 2 - dw // 2, dy - d.textbbox((0, 0), desc, font=fd)[1]), desc, font=fd, fill=(255, 236, 205, 255))
    a = np.array(img).astype(np.float32) / 255
    bbox = img.getbbox()
    return a[..., [2, 1, 0]], a[..., 3:4], bbox[3] if bbox else 700

def make_badge(text):
    f = ImageFont.truetype(FONT_KICK, 30)
    tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10))); tw, th = text_w(tmp, text, f)
    img = Image.new('RGBA', (tw + 56, th + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=img.height // 2, fill=(255, 255, 255, 235))
    d.text((28, 15 - d.textbbox((0, 0), text, font=f)[1]), text, font=f, fill=BLUE + (255,))
    a = np.array(img).astype(np.float32) / 255
    return a[..., [2, 1, 0]], a[..., 3:4]

LABELS = {}
def label_for(lab):
    if lab not in LABELS: LABELS[lab] = make_label(*lab)
    return LABELS[lab]
BADGE = {}

# top scrim so labels read over any footage
gy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
SCRIM_TOP = np.clip(1 - gy / 0.36, 0, 1) ** 1.6 * 0.62
SCRIM_CENTRE = np.exp(-((gy - 0.47) / 0.16) ** 2) * 0.35

LOGO_RGB, LOGO_A = R.load_logo(f'{AS}/travlink_logo_white.png', 300)

def frame(n):
    t = n / FPS
    i = int(np.searchsorted(STARTS, t, side='right') - 1); i = min(i, len(SEG) - 1)
    s = SEG[i]; lt = t - STARTS[i]
    img = s['fn'](lt)
    img = img * R.VIGNETTE + R.GRAIN[n % 6]
    img = np.clip(img, 0, 1)
    lab = s['label']
    if lab:
        kind = lab[3]
        rgb, a, bottom = label_for(lab)
        same_as_prev = i > 0 and SEG[i - 1]['label'] == lab
        u = 1.0 if same_as_prev else ease_out(lt / 0.35)
        if kind in ('title', 'section', 'end'):
            img = img * (1 - SCRIM_CENTRE)
            y = int(H * 0.47 - bottom / 2 + (1 - u) * 40)
            if kind in ('title', 'end'):
                ls = 0.85 + 0.15 * back_out(lt / 0.5); la = cv2.resize(LOGO_A, None, fx=ls, fy=ls)[..., None]
                lr = cv2.resize(LOGO_RGB, None, fx=ls, fy=ls)
                R.over(img, lr, la, W / 2 - la.shape[1] / 2, y - la.shape[0] - 10, ease_out(lt / 0.4))
                y += 40
        else:
            img = img * (1 - SCRIM_TOP)
            y = int(118 + (1 - u) * -30)
        R.over(img, rgb, a, 0, y, u)
        if s['badge']:
            if s['badge'] not in BADGE: BADGE[s['badge']] = make_badge(s['badge'])
            brgb, ba = BADGE[s['badge']]
            R.over(img, brgb, ba, W / 2 - ba.shape[1] / 2, y + bottom + 24, ease_out(lt / 0.25))
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()

# ---------------- sfx ----------------
def build_sfx():
    import soundfile as sf
    sys.argv = ['sfx', '/dev/null']
    import importlib.util
    spec = importlib.util.spec_from_file_location('sfxlib', __file__.replace('glossary.py', 'sfx.py'))
    src = open(spec.origin).read().split('# transitions (centred on the cut)')[0]
    ns = {}; exec(src.replace('48000, 33.0', f'48000, {DUR + 0.5}'), ns)
    mix = ns['mix']; place = ns['place']
    for k, s in enumerate(SEG):
        for kind, at in s['sfx']:
            t = STARTS[k] + at
            if kind == 'whoosh': place(ns['whoosh'](0.45), t - 0.22, 0.28)
            elif kind == 'impact': place(ns['impact'](), t, 0.3)
            elif kind == 'pop': place(ns['pop'](900), t, 0.22)
            elif kind == 'chime': place(ns['chime'](), t, 0.26)
    mix *= 10 ** (-3 / 20) / max(1e-6, np.abs(mix).max())
    sf.write(SFX_OUT, mix[:int(48000 * DUR)], 48000)

if __name__ == '__main__':
    from multiprocessing import Pool
    import os
    build_sfx()
    N = int(DUR * FPS); print('duration', round(DUR, 2), 's,', N, 'frames', flush=True)
    only = os.environ.get('FRAMES')
    frames = [int(x) for x in only.split(',')] if only else range(N)
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', OUT], stdin=subprocess.PIPE)
    frames = list(frames); B = 48  # bounded batches: the encoder is slower than the renderers,
    with Pool(4, maxtasksperchild=40) as p:  # so unbounded imap would queue frames in RAM
        for b0 in range(0, len(frames), B):
            for buf in p.imap(frame, frames[b0:b0 + B], chunksize=4):
                ff.stdin.write(buf)
            if b0 % 240 == 0: print(f'{b0}/{len(frames)}', flush=True)
    ff.stdin.close(); ff.wait()
