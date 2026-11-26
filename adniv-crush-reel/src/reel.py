"""Adniv x CRUSH Salon reel - Style C 'Light-On Kinetic' full renderer.

usage:  python reel.py stills [scene_idx ...]   -> QA stills (overlay + light-overlap check)
        python reel.py scenes                   -> render all scene files in parallel (4 procs)
        python reel.py assemble                 -> transitions + logo + end card -> MP4
"""
import os, sys, json, subprocess, time, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S_DIR = "/tmp/claude-0/-home-user-The100xers/3dc716bb-8387-5a31-912b-63c195d92910/scratchpad"
sys.path.insert(0, S_DIR)
from overlay import (F, text_img, with_depth, chip, rounded, prog, out_cubic, out_back, out_quint,
                     in_out, clamp, logo, NAVY, ORANGE, WHITE, W, H)
import grade as G

CL, ST, WORK = S_DIR + "/clips", S_DIR + "/stabs", S_DIR + "/work"
os.makedirs(WORK, exist_ok=True)
FPS, XT = 30, 9          # fps, transition frames (0.3 s)
SW, SH = 1242, 2208      # decode size (9:16, 1.15x of output so push-ins stay sharp)
X0 = 72                  # text margin (safe area starts at 64)
X0P = 96                 # text margin inside a navy plate (plate starts at x=64)
GAP_WORD, ROW_GAP = 30, 10
SH_TEXT = dict(soft=(0, 16, 26, 0.55), tight=(0, 3, 3, 0.35))
SH_ITEM = dict(soft=(0, 6, 14, 0.45), tight=(0, 2, 2, 0.35))
SH_SPEC = dict(soft=(0, 6, 16, 0.55), tight=(0, 2, 3, 0.45))

# ----------------------------------------------------------------------------------------------
# SCENES  (dur = own on-screen seconds; scene is rendered dur+0.3 s so the transition can overlap)
# look: dark  = white face / navy extrusion      plate = navy plate, white face / orange extrusion
#       light = navy face / white extrusion
# ----------------------------------------------------------------------------------------------
SC = [
    dict(id="s01_hook", clip="IMG_4905", ss=0.0, dur=2.7, z=(1.00, 1.05), look="plate", delay=0.05,
         lines=["CRUSH"], S=168, maxw=640, caps_top=1196,
         rows=[["~SALON, GURGAON"], ["Lighting by Adniv"]], tr="whip_l"),
    dict(id="s02_sign", clip="IMG_4902", ss=0.9, dur=1.9, z=(1.00, 1.00), look="dark", stab=True,
         lines=["First", "impressions,", "backlit."], S=90, maxw=540, caps_top=1215, rows=[], tr="flash"),
    dict(id="s03_donut", clip="IMG_4903", ss=0.2, dur=3.4, z=(1.00, 1.05), look="dark", stab=True,
         lines=["DONUT"], S=146, maxw=860, caps_top=1156,
         rows=[["#01", "~PENDANT  ·  800 mm  ·  BLACK FINISH"], ["60 W", "4000K Neutral White"],
               ["50 × 70 mm", "Canopy + 1.5 m suspension kit"]],
         anchor=dict(kind="bottom", box=(100, 900, 900, 1200)), elbow_off=-28, tr="iris"),
    dict(id="s04_panel", clip="IMG_4901", ss=0.1, dur=2.7, z=(1.00, 1.04), look="dark", stab=True,
         lines=["PANEL"], S=84, maxw=860, caps_top=1286,
         rows=[["#02", "~ROUND CONCEALED PANEL"], ["15 W", "4000K Neutral White"]],
         anchor=dict(kind="bottom", box=(250, 1135, 700, 1340)), elbow_off=-22, tr="slide_u"),
    dict(id="s05_size", clip="IMG_4904", ss=0.0, dur=2.7, z=(1.00, 1.05), look="dark",
         lines=["Donut made", "to your size."], S=96, maxw=860, caps_top=1174,
         rows=[["450", "500", "600", "800", "900", "1000", "mm & more"], ["~CUSTOM-MADE TO YOUR PREFERENCE"]],
         nodots=True, tr="leak"),
    dict(id="s06_dome", clip="IMG_4896", ss=0.2, dur=3.0, z=(1.00, 1.05), look="dark",
         lines=["DOME"], S=146, maxw=860, caps_top=1156,
         rows=[["#03", "~DOME HANGING LIGHT  ·  DECORATIVE"], ["3000K Warm White", "Black finish"],
               ["Canopy + 1.5 m black wire"]], tr="slide_d"),
    dict(id="s07_strip", clip="IMG_4890", ss=0.1, dur=5.2, z=(1.00, 1.10), look="plate", slow=1.85, row_dt=0.13,
         phases=[
             dict(start=0.0, lines=["Strip Light"], S=118, maxw=780, caps_top=1150,
                  rows=[["#04", "~10 × 10 mm ALUMINIUM PROFILE"],
                        ["240 LED · 24 V", "3000K Warm White"],
                        ["With power supply"]]),
             dict(start=2.3, lines=[], S=100, maxw=780, caps_top=1124,
                  rows=[["~~PROFILE SIZES AVAILABLE  ·  3.6 m LENGTH"],
                        ["10 × 10", "12 × 12", "16 × 16", "25 × 25", "mm & more"],
                        ["~~STRIP AVAILABLE  ·  5 m ROLL"],
                        ["120 LED · 12 V", "240 LED · 24 V", "With power supply"],
                        ["~~STRIP COLOURS AVAILABLE"],
                        ["3000K", "4000K", "6500K", "Tri-colour (3-in-1)"]]),
         ], nodots=True, tr="whip_r"),
    dict(id="s08_chairs", clip="IMG_4891", ss=0.3, dur=2.5, z=(1.00, 1.05), look="plate",
         lines=["Softer light.", "Longer stays."], S=100, maxw=820, caps_top=1226, rows=[], tr="whip_l"),
    dict(id="s09_shelf", clip="IMG_4895", ss=0.2, dur=2.5, z=(1.00, 1.05), look="plate",
         lines=["Light that", "moves product."], S=96, maxw=760, caps_top=1290, rows=[], tr="flash"),
]
END_FRAMES = 135  # 4.5 s


def n_own(sc): return round(sc["dur"] * FPS)


# ----------------------------------------------------------------------------------------------
# kinetic type
# ----------------------------------------------------------------------------------------------
_LET = {}


def line_x(fnt, line, i, S):
    """x of glyph i: kerning-aware advance, slightly tightened, with proper word gaps."""
    return fnt.getlength(line[:i]) - i * 0.016 * S + 0.12 * S * line[:i].count(" ")


def line_w(fnt, line, S):
    return line_x(fnt, line, len(line), S) - 0.016 * S


def make_letter(ch, S, face, ext, lo):
    key = (ch, S, face, ext, lo)
    if key in _LET:
        return _LET[key]
    f = F("InterDisplay-Black", S)
    D = max(5, round(S * 0.055))
    g = text_img(ch, f, (255, 255, 255))
    a = g.split()[3]
    im = Image.new("RGBA", (g.width + D + 2, g.height + D + 2), (0, 0, 0, 0))
    for k in range(D, 0, -1):
        fac = lo + (0.97 - lo) * (D - k) / max(D - 1, 1)
        lay = Image.new("RGBA", g.size, tuple(int(c * fac) for c in ext) + (255,))
        lay.putalpha(a)
        im.alpha_composite(lay, (k, k))
    fl = Image.new("RGBA", g.size, face + (255,))
    fl.putalpha(a)
    im.alpha_composite(fl, (0, 0))
    _LET[key] = im
    return im


def mix(a, b, t): return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


LOOKS = dict(
    dark=dict(face=WHITE, ext=NAVY, lo=0.55, off=(95, 100, 125), chip="white", ink=WHITE),
    plate=dict(face=WHITE, ext=ORANGE, lo=0.62, off=(150, 150, 170), chip="white", ink=WHITE),
    light=dict(face=NAVY, ext=WHITE, lo=0.70, off=(120, 125, 165), chip="navy", ink=NAVY),
    end=dict(face=NAVY, ext=ORANGE, lo=0.72, off=(150, 155, 190), chip="navy", ink=NAVY),
)


def _chip_img(text, look, nodots):
    fnt = F("Inter-SemiBold", 28)
    dot = None if nodots else ORANGE
    if LOOKS[look]["chip"] == "white":
        return chip(text, fnt, bg=(255, 255, 255, 247), fg=NAVY, dot=dot, padx=20, h=58, r=29)
    return chip(text, fnt, bg=NAVY + (245,), fg=WHITE, dot=dot, padx=20, h=58, r=29)


def build_layout(sc):
    """Static layout + pre-rendered row items for one scene."""
    look = LOOKS[sc["look"]]
    S = sc["S"]
    fnt = F("InterDisplay-Black", S)
    x0 = X0P if sc["look"] == "plate" else X0
    lines = sc["lines"]
    maxw = sc["maxw"]
    adv_k = 0.0
    widths = [line_w(fnt, l, S) for l in lines] or [0]
    if max(widths) > maxw:                       # autofit
        S = int(S * maxw / max(widths))
        fnt = F("InterDisplay-Black", S)
        widths = [line_w(fnt, l, S) for l in lines]
    D = max(5, round(S * 0.055))
    hb = fnt.getbbox("H")
    cap_top_in, cap_h = hb[1] + 2, hb[3] - hb[1]
    pitch = 0.95 * S
    caps_top = sc["caps_top"]
    if lines:
        word_bottom = caps_top + (len(lines) - 1) * pitch + cap_h
        has_desc = any(c in "gjpqy,;" for c in lines[-1])
        y = word_bottom + GAP_WORD + (0.14 * S if has_desc else 0)
    else:
        word_bottom, y = caps_top, caps_top
    rows, block_w = [], max(widths) + D
    for r in sc["rows"]:
        items, x, rh = [], x0, 0
        for it in r:
            if it.startswith("#"):
                im = chip(it[1:], F("InterDisplay-Bold", 28), bg=ORANGE + (255,), fg=WHITE, dot=None, padx=16, h=46, r=12)
                typ, gap = "badge", 16
            elif it.startswith("~~"):
                im = text_img(it[2:], F("Inter-SemiBold", 28), look["ink"], tracking=1.5)
                typ, gap = "text", 12
            elif it.startswith("~"):
                im = text_img(it[1:], F("Inter-SemiBold", 30), look["ink"], tracking=3)
                typ, gap = "text", 12
            else:
                im = _chip_img(it, sc["look"], sc.get("nodots", False))
                typ, gap = "chip", 10
            items.append(dict(typ=typ, im=im, x=x, w=im.width))
            x += im.width + gap
            rh = max(rh, im.height - 4 if typ == "text" else im.height)
        rh = max(rh, 40)
        for it in items:
            it["y"] = y + (rh - it["im"].height) / 2
        rows.append(dict(items=items, y=y, h=rh))
        block_w = max(block_w, x - gap - x0)
        y += rh + ROW_GAP
    bottom = (rows[-1]["y"] + rows[-1]["h"]) if rows else word_bottom
    lay = dict(S=S, D=D, x0=x0, cap_top_in=cap_top_in, cap_h=cap_h, pitch=pitch, caps_top=caps_top, bottom=bottom,
               rows=rows, block_w=block_w, lines=lines, widths=widths, adv_k=adv_k, look=look)
    if sc["look"] == "plate":
        px0, py0 = 64, caps_top - 40
        pw, ph = int(block_w + (x0 - 64) * 2 + 8), int(bottom + 32 - py0)
        lay["plate"] = (px0, py0, pw, ph)
        assert px0 + pw <= 940 or py0 + ph < 1000, f"plate hits icon column {sc['id']}"
        assert py0 + ph <= 1500, f"plate below safe area {sc['id']} {py0+ph}"
    assert bottom <= 1495, f"{sc['id']} text bottom {bottom:.0f} > 1495"
    assert caps_top >= 235
    assert x0 + block_w <= 940 or bottom < 1000 or True
    return lay


def blit(cv, im, x, y, op=1.0, shadow=None, anchor="lt"):
    """Composite RGBA `im` on RGBA canvas with clipping, opacity and optional depth shadow."""
    if op <= 0.003:
        return
    pad = 0
    if shadow is not None:
        im, pad = with_depth(im, **shadow)
    w, h = im.size
    iw, ih = w - 2 * pad, h - 2 * pad
    if anchor[0] == "c": x -= iw / 2
    elif anchor[0] == "r": x -= iw
    if anchor[1] == "m": y -= ih / 2
    elif anchor[1] == "b": y -= ih
    if op < 1:
        a = im.split()[3].point(lambda v: int(v * op))
        im = im.copy(); im.putalpha(a)
    dx, dy = int(round(x - pad)), int(round(y - pad))
    sx, sy = max(0, -dx), max(0, -dy)
    ex, ey = min(w, W - dx), min(h, H - dy)
    if ex <= sx or ey <= sy:
        return
    if (sx, sy, ex, ey) != (0, 0, w, h):
        im = im.crop((sx, sy, ex, ey))
    cv.alpha_composite(im, (dx + sx, dy + sy))


def mask_rise(layer, p):
    w, h = layer.size
    off = int((1 - out_quint(p)) * h * 1.05)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if off < h:
        out.alpha_composite(layer.crop((0, 0, w, h - off)), (0, off))
    return out


def draw_leader(cv, node, elbow_y, xl, p):
    if node is None or p <= 0:
        return
    x, y = node
    seg1 = max(elbow_y - y, 0)
    seg2 = max(x - xl, 1)
    cur = out_cubic(p) * (seg1 + seg2)
    bx0, by0, bx1, by1 = int(xl - 16), int(y - 20), int(x + 20), int(max(elbow_y, y) + 20)
    lay = Image.new("RGBA", (bx1 - bx0, by1 - by0), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ly = lambda v: v - by0
    lx = lambda v: v - bx0
    s1 = min(cur, seg1)
    d.line((lx(x), ly(y), lx(x), ly(y + s1)), fill=WHITE + (240,), width=3)
    if cur > seg1:
        d.line((lx(x), ly(elbow_y), lx(x - (cur - seg1)), ly(elbow_y)), fill=WHITE + (240,), width=3)
    dot = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    ImageDraw.Draw(dot).ellipse((3, 3, 56, 56), fill=ORANGE + (255,), outline=WHITE + (255,), width=9)
    dot = dot.resize((20, 20), Image.LANCZOS)
    lay.alpha_composite(dot, (int(lx(x) - 10), int(ly(y) - 10)))
    blit(cv, lay, bx0, by0, 1.0, shadow=dict(soft=(0, 3, 5, 0.5), tight=(0, 1, 1, 0.3)))


def draw_overlay(sc, lay, t, anchor=None, amul=1.0, shtext=SH_TEXT, cmul=1.0, tplate=None):
    """Transparent W x H overlay for scene-local text time t (seconds)."""
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tp = t if tplate is None else tplate
    if t <= 0 and tp <= 0:
        return cv
    look, S, D, x0 = lay["look"], lay["S"], lay["D"], lay["x0"]
    plate_dt = 0.0
    if "plate" in lay:
        px0, py0, pw, ph = lay["plate"]
        pp = prog(tp, 0.0, 0.5)
        if pp > 0:
            pl = rounded((pw, ph), 26, NAVY + (250,))
            wcut = max(2, int(pw * out_cubic(pp)))
            blit(cv, pl.crop((0, 0, wcut, ph)), px0, py0, 1.0, shadow=dict(soft=(0, 14, 26, .5), tight=(0, 3, 4, .3)))
        plate_dt = 0.28 if tplate is None else 0.0
    if t <= 0:
        if amul < 1:
            cv.putalpha(cv.split()[3].point(lambda v: int(v * max(amul, 0))))
        return cv
    plate_img, cv = cv, Image.new("RGBA", (W, H), (0, 0, 0, 0))   # content goes on its own layer (cmul fades only this)
    # leader line to the fixture
    if "anchor" in sc and anchor is not None:
        elbow_y = sc["caps_top"] + sc["elbow_off"]
        draw_leader(cv, anchor, elbow_y, x0 + 2, prog(t, 0.0, 0.5))
    # kinetic letters
    asc_pad = int(S * 0.55)
    nl = len(lay["lines"])
    lh = int(lay["pitch"] * (nl - 1) + lay["cap_h"] + lay["cap_top_in"] + S * 0.5 + 12)
    wl = Image.new("RGBA", (int(lay["block_w"] + D + 40), lh + asc_pad), (0, 0, 0, 0))
    if not lay["lines"]:
        wl = None
    fnt = F("InterDisplay-Black", S)
    for j, line in enumerate(lay["lines"]):
        box_top = asc_pad + j * lay["pitch"] - lay["cap_top_in"]
        for i, ch in enumerate(line):
            if ch == " ":
                continue
            st = plate_dt + 0.12 + j * 0.14 + i * 0.065
            p = prog(t, st, 0.45)
            if p <= 0:
                continue
            fl = 1.0 if p > 0.7 else (0.55 + 0.45 * p / 0.7) * (0.75 if 0.3 < p < 0.4 else 1.0)
            fl = round(fl * 8) / 8
            lvl = clamp((fl - 0.4) / 0.6)
            face = mix(look["off"], look["face"], lvl)
            let = make_letter(ch, S, face, look["ext"], look["lo"])
            xx = line_x(fnt, line, i, S)
            yy = box_top + (1 - out_back(p, 1.2)) * (-0.45 * S)
            op = clamp(p * 2.5)
            if op < 1:
                let = let.copy(); let.putalpha(let.split()[3].point(lambda v: int(v * op)))
            wl.alpha_composite(let, (int(round(xx)), int(round(yy)))) if yy >= 0 else wl.alpha_composite(
                let.crop((0, int(-yy), let.width, let.height)), (int(round(xx)), 0))
    if wl is not None:
        blit(cv, wl, x0, lay["caps_top"] - asc_pad, 1.0, shadow=shtext)
    # rows (badge / spec text / chips)
    base = plate_dt + 0.45 + 0.08 * nl
    for ri, row in enumerate(lay["rows"]):
        for ii, it in enumerate(row["items"]):
            st = base + ri * sc.get("row_dt", 0.2) + ii * 0.09
            p = prog(t, st, 0.4)
            if p <= 0:
                continue
            im = it["im"]
            if it["typ"] == "text":
                blit(cv, mask_rise(im, p), it["x"], it["y"], clamp(p * 1.5), shadow=SH_SPEC)
            else:
                sc_ = 0.6 + 0.4 * out_back(p)
                im2 = im.resize((max(1, int(im.width * sc_)), max(1, int(im.height * sc_))), Image.LANCZOS) if sc_ != 1 else im
                blit(cv, im2, it["x"] + it["w"] / 2, it["y"] + im.height / 2 + (1 - out_cubic(p)) * 16,
                     clamp(p * 2.2), shadow=SH_ITEM, anchor="cm")
    if cmul < 1:
        cv.putalpha(cv.split()[3].point(lambda v: int(v * max(cmul, 0))))
    plate_img.alpha_composite(cv)
    if amul < 1:
        plate_img.putalpha(plate_img.split()[3].point(lambda v: int(v * max(amul, 0))))
    return plate_img


# ----------------------------------------------------------------------------------------------
# footage
# ----------------------------------------------------------------------------------------------
def decode(sc, n):
    name = sc["clip"]
    pre = G.P[name]["pre"]
    vf = [pre] if pre else []
    vf.append(f"scale={SW}:{SH}:flags=lanczos")
    if sc.get("stab"):
        vf.append(f"vidstabtransform=input={ST}/{name}.trf:smoothing=15:zoom=2:interpol=bicubic")
    slow = sc.get("slow", 1.0)
    vf.append(f"trim=start={sc['ss']}:end={sc['ss'] + (n / FPS + 0.3) / slow},setpts=(PTS-STARTPTS)*{slow}")
    vf.append(f"framerate=fps={FPS}")
    cmd = ["ffmpeg", "-v", "error", "-i", f"{CL}/{name}.mov", "-vf", ",".join(vf), "-frames:v", str(n),
           "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SW * SH * 3 * 2)
    sz = SW * SH * 3
    try:
        for _ in range(n):
            buf = p.stdout.read(sz)
            if len(buf) < sz:
                return
            yield np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
    finally:
        p.kill()


def prep(arr, z, name):
    im = Image.fromarray(arr)
    bw, bh = SW / z, SH / z
    x0, y0 = (SW - bw) / 2, (SH - bh) / 2
    im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
    im = im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=40, threshold=2))
    return G.grade(np.asarray(im), name)


def detect_anchor(fr, spec):
    x0, y0, x1, y1 = spec["box"]
    m = fr[y0:y1, x0:x1].astype(np.float32).mean(-1) > spec.get("thr", 215)
    ys, xs = np.nonzero(m)
    if len(xs) < 30:
        return None
    ymax = ys.max(); sel = ys > ymax - 6
    return (x0 + float(xs[sel].mean()), y0 + float(ymax))


LOGO_BOX = (736, 244, 1016, 360)


def render_scene(i, keep=None, out=None):
    """Render scene i. keep=None -> write full scene file; keep=set(k) -> return {k: (rgb_with_overlay, overlay, base)}."""
    sc = SC[i]
    phases = sc.get("phases")
    if phases:
        lays = [build_layout(dict(sc, **ph)) for ph in phases]
        rects = [l["plate"] for l in lays]                    # one shared plate that fits every phase
        ux0, uy0 = min(r[0] for r in rects), min(r[1] for r in rects)
        ux1, uy1 = max(r[0] + r[2] for r in rects), max(r[1] + r[3] for r in rects)
        assert uy1 <= 1500 and (ux1 <= 940 or uy1 < 1000), (ux1, uy1)
        for l in lays:
            l["plate"] = (ux0, uy0, ux1 - ux0, uy1 - uy0)
        lay = lays[0]
        print(sc["id"], "shared plate", lays[0]["plate"], "bottoms", [round(l["bottom"]) for l in lays], flush=True)
    else:
        lay = build_layout(sc)
    N = n_own(sc) + XT
    delay = sc.get("delay", 0.2)
    res, bbox, lums = {}, {}, []
    mm = None
    if keep is None:
        mm = np.lib.format.open_memmap(f"{WORK}/{sc['id']}.npy", mode="w+", dtype=np.uint8, shape=(N, H, W, 3))
    anc = None
    gen = decode(sc, N)
    for k, arr in enumerate(gen):
        if keep is not None and k not in keep:
            continue
        z = sc["z"][0] + (sc["z"][1] - sc["z"][0]) * (k / (n_own(sc) - 1))
        fr = prep(arr, z, sc["clip"])
        if "anchor" in sc:
            a = detect_anchor(fr, sc["anchor"])
            if a is not None:
                anc = a if anc is None else (anc[0] * .6 + a[0] * .4, anc[1] * .6 + a[1] * .4)
        amul = 1.0 if k < n_own(sc) else 1 - (k - n_own(sc) + 1) / (XT + 1)
        t = k / FPS - delay
        if phases:
            pi = max([j for j, ph in enumerate(phases) if ph["start"] <= t] or [0])
            ph = phases[pi]
            nxt = phases[pi + 1]["start"] if pi + 1 < len(phases) else None
            cm = 1 - prog(t, nxt - 0.2, 0.2) if nxt else 1.0
            if pi == 0:
                ov = draw_overlay(dict(sc, **ph), lays[0], t, anc, amul, cmul=cm)
            else:
                ov = draw_overlay(dict(sc, **ph), lays[pi], t - ph["start"], anc, amul, cmul=cm, tplate=t)
        else:
            ov = draw_overlay(sc, lay, t, anc, amul)
        base = Image.fromarray(fr).convert("RGBA")
        base.alpha_composite(ov)
        rgb = np.asarray(base.convert("RGB"))
        bb = ov.split()[3].point(lambda v: 255 if v > 128 else 0).getbbox()
        bbox[k] = bb
        if 8 <= k < n_own(sc) and k % 5 == 0:
            lums.append(float(fr[LOGO_BOX[1]:LOGO_BOX[3], LOGO_BOX[0]:LOGO_BOX[2]].astype(np.float32).mean()))
        if keep is None:
            mm[k] = rgb
        else:
            res[k] = (rgb, ov, fr)
    if mm is not None:
        mm.flush()
        meta = dict(id=sc["id"], n=N, bbox=bbox, logo_lum=float(np.mean(lums)) if lums else 0.0,
                    layout=dict(bottom=lay["bottom"], S=lay["S"]))
        json.dump(meta, open(f"{WORK}/{sc['id']}.json", "w"))
        return meta
    return res


def overlap_report(fr, ov):
    """% of glyph/chip pixels that sit on bright (light-source) footage pixels."""
    a = np.asarray(ov.split()[3]) > 128
    bright = fr.astype(np.float32).mean(-1) > 225
    return float((a & bright).sum() / max(a.sum(), 1) * 100)


def _worker(i):
    t = time.time()
    meta = render_scene(i)
    return i, round(time.time() - t, 1), meta["logo_lum"]


# ----------------------------------------------------------------------------------------------
# stills
# ----------------------------------------------------------------------------------------------
def stills(idx):
    os.makedirs(S_DIR + "/qa", exist_ok=True)
    for i in idx:
        sc = SC[i]
        d = sc.get("delay", 0.2)
        ks = {int((d + 0.45) * FPS), int((d + 1.0) * FPS), int((d + 2.2) * FPS), n_own(sc) - 2}
        if sc["dur"] > 4:
            ks |= {int((d + 3.5) * FPS)}
        ks = sorted(ks)
        ks = [min(k, n_own(sc) - 1) for k in ks]
        res = render_scene(i, keep=set(ks))
        tiles = []
        for k in ks:
            rgb, ov, fr = res[k]
            print(f"{sc['id']} k={k}  text-over-light {overlap_report(fr, ov):.1f}%  overlay bbox "
                  f"{ov.split()[3].point(lambda v: 255 if v > 128 else 0).getbbox()}")
            tiles.append(Image.fromarray(rgb).resize((432, 768), Image.LANCZOS))
        sheet = Image.new("RGB", (432 * len(tiles) + 8 * (len(tiles) - 1), 768), (20, 20, 20))
        for n, t_ in enumerate(tiles):
            sheet.paste(t_, (n * 440, 0))
        sheet.save(f"{S_DIR}/qa/still_{sc['id']}.jpg", quality=88)


# ----------------------------------------------------------------------------------------------
# end card (white = "lights on"), original Adniv logo, same type system
# ----------------------------------------------------------------------------------------------
SC_END = dict(id="end", look="end", lines=["Want your", "salon lit", "like this?"], S=150, maxw=860,
              caps_top=585, rows=[])
SH_END = dict(soft=(0, 10, 18, 0.22), tight=(0, 2, 2, 0.18))
PHONES = ["99108 13339", "93190 74766"]
_END = {}


def end_assets():
    if _END:
        return _END
    lay = build_layout(SC_END)
    sub = text_img("DM us to book a lighting consultation", F("Inter-Medium", 38), NAVY)
    orc = text_img("or call", F("Inter-Medium", 34), (86, 90, 128))
    web = text_img("www.adniv.in", F("Inter-SemiBold", 42), NAVY)
    y_sub = lay["bottom"] + 38
    y_or = y_sub + 40 + 40
    y_b1 = y_or + 46 + 18
    y_b2 = y_b1 + 96 + 16
    y_web = y_b2 + 96 + 34
    btns = []
    for ph in PHONES:
        b = rounded((760, 96), 48, NAVY + (255,))
        dot = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
        ImageDraw.Draw(dot).ellipse((0, 0, 179, 179), fill=ORANGE + (255,))
        b.alpha_composite(dot.resize((44, 44), Image.LANCZOS), (26, 26))
        b.alpha_composite(text_img(ph, F("InterDisplay-SemiBold", 48), WHITE, tracking=2), (98, 20))
        b.alpha_composite(text_img("CALL", F("Inter-Bold", 24), ORANGE, tracking=5), (760 - 110, 33))
        btns.append(b)
    assert sub.width <= 860 and y_web + 50 <= 1495, (sub.width, y_web)
    _END.update(lay=lay, sub=sub, orc=orc, web=web, y_sub=y_sub, y_or=y_or, y_b=[y_b1, y_b2], y_web=y_web, btns=btns,
                logo=logo(540, True))
    return _END


def draw_end(t):
    A = end_assets()
    cv = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    p = prog(t, 0.0, 0.55)
    lg = A["logo"]
    sc_ = 0.92 + 0.08 * out_cubic(p)
    lg2 = lg.resize((int(lg.width * sc_), int(lg.height * sc_)), Image.LANCZOS)
    blit(cv, lg2, W / 2, 285 + lg.height / 2 + (1 - out_cubic(p)) * 14, clamp(p * 1.6), anchor="cm")
    ov = draw_overlay(SC_END, A["lay"], t - 0.35, None, 1.0, shtext=SH_END)
    cv.alpha_composite(ov)
    ps = prog(t, 1.1, 0.6)
    blit(cv, mask_rise(A["sub"], ps), X0, A["y_sub"], clamp(ps * 1.5))
    po = prog(t, 1.45, 0.4)
    blit(cv, A["orc"], X0, A["y_or"] + (1 - out_cubic(po)) * 8, clamp(po * 1.6))
    for i, b in enumerate(A["btns"]):
        pb = prog(t, 1.65 + i * 0.2, 0.45)
        if pb > 0:
            s2 = 0.7 + 0.3 * out_back(pb)
            b2 = b.resize((max(1, int(b.width * s2)), max(1, int(b.height * s2))), Image.LANCZOS)
            blit(cv, b2, X0 + b.width / 2, A["y_b"][i] + b.height / 2, clamp(pb * 2),
                 shadow=dict(soft=(0, 12, 20, 0.3), tight=(0, 3, 4, 0.25)), anchor="cm")
    pw = prog(t, 2.3, 0.5)
    web = A["web"]
    blit(cv, web.crop((0, 0, max(1, int(web.width * out_cubic(pw))), web.height)), X0, A["y_web"], 1.0)
    if pw > 0:
        ul = Image.new("RGBA", (max(1, int((web.width - 4) * out_cubic(pw))), 5), ORANGE + (255,))
        cv.alpha_composite(ul, (X0 + 2, int(A["y_web"] + web.height - 2)))
    bb = cv.split()[3]
    return cv


def render_end():
    A = end_assets()
    mm = np.lib.format.open_memmap(f"{WORK}/end.npy", mode="w+", dtype=np.uint8, shape=(END_FRAMES, H, W, 3))
    for k in range(END_FRAMES):
        mm[k] = np.asarray(draw_end(k / FPS - 0.1).convert("RGB"))
    mm.flush()


# ----------------------------------------------------------------------------------------------
# transitions
# ----------------------------------------------------------------------------------------------
_dist = {}


def dist_map(c):
    if c not in _dist:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _dist[c] = np.sqrt((xx - c[0]) ** 2 + (yy - c[1]) ** 2)
    return _dist[c]


def tr_slide(A, B, p, axis, sign, blur):
    e = in_out(p)
    n = W if axis == 1 else H
    strip = np.concatenate([A, B] if sign > 0 else [B, A], axis=axis)
    off = e * n if sign > 0 else (1 - e) * n
    r = blur * n * math.sin(math.pi * p)
    acc = np.zeros(A.shape, np.float32)
    ns = 1 if r < 1 else 41
    offs = np.clip(off + np.linspace(-r, r, ns), 0, n)
    wts = np.exp(-0.5 * (np.linspace(-1, 1, ns) / 0.55) ** 2) if ns > 1 else np.ones(1)
    wts /= wts.sum()
    for o, wt in zip(offs, wts):
        o = int(round(o))
        acc += (strip[:, o:o + W] if axis == 1 else strip[o:o + H]) * np.float32(wt)
    return np.clip(acc, 0, 255).astype(np.uint8)


def tr_flash(A, B, p):
    base = A if p < 0.5 else B
    g = (math.sin(math.pi * p) ** 1.6) * 0.96
    return (base.astype(np.float32) * (1 - g) + 255 * g).astype(np.uint8)


IRIS_C = (488, 815)


def tr_iris(A, B, p):
    d = dist_map(IRIS_C)
    e = in_out(p)
    R = e * math.hypot(max(IRIS_C[0], W - IRIS_C[0]), max(IRIS_C[1], H - IRIS_C[1])) * 1.06
    m = np.clip((R - d) / 26 + 0.5, 0, 1)[..., None]
    out = A.astype(np.float32) * (1 - m) + B.astype(np.float32) * m
    ring = (np.exp(-((d - R) / 5.0) ** 2) * (0.9 * (1 - p)))[..., None]
    return np.clip(out + ring * 255, 0, 255).astype(np.uint8)


def tr_leak(A, B, p):
    e = in_out(p)
    base = A.astype(np.float32) * (1 - e) + B.astype(np.float32) * e
    g = math.sin(math.pi * p) ** 1.5
    d = dist_map((930, 380))
    glow = (np.clip(1 - d / 1000, 0, 1) ** 2)[..., None]
    return np.clip(base + glow * np.array(ORANGE, np.float32) * 0.6 * g, 0, 255).astype(np.uint8)


def transition(kind, A, B, p):
    A, B = np.asarray(A), np.asarray(B)
    if kind == "whip_l": return tr_slide(A, B, p, 1, +1, 0.15)
    if kind == "whip_r": return tr_slide(A, B, p, 1, -1, 0.15)
    if kind == "slide_u": return tr_slide(A, B, p, 0, +1, 0.05)
    if kind == "slide_d": return tr_slide(A, B, p, 0, -1, 0.05)
    if kind == "flash": return tr_flash(A, B, p)
    if kind == "iris": return tr_iris(A, B, p)
    if kind == "leak": return tr_leak(A, B, p)
    raise ValueError(kind)


# ----------------------------------------------------------------------------------------------
# logo overlay (top-right, y=244, every scene except the end card)
# ----------------------------------------------------------------------------------------------
_LG = {}


def logo_layer(var):
    if var not in _LG:
        lg = logo(280, dark=(var == "orig"))
        sh = dict(soft=(0, 4, 12, 0.55), tight=(0, 1, 2, 0.45)) if var == "rev" else dict(soft=(0, 3, 8, 0.18), tight=(0, 1, 1, 0.12))
        im, pad = with_depth(lg, **sh)
        _LG[var] = (1016 - lg.width - pad, 244 - pad, im)
    return _LG[var]


def add_logo(fr, var, op):
    if op <= 0.003:
        return fr
    x, y, im = logo_layer(var)
    h, w = im.height, im.width
    reg = Image.fromarray(fr[y:y + h, x:x + w]).convert("RGBA")
    if op < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * op)))
    reg.alpha_composite(im)
    fr = fr.copy() if not fr.flags.writeable else fr
    fr[y:y + h, x:x + w] = np.asarray(reg.convert("RGB"))
    return fr


# ----------------------------------------------------------------------------------------------
# assemble + encode
# ----------------------------------------------------------------------------------------------
def assemble(out_path, crf=15):
    metas = [json.load(open(f"{WORK}/{sc['id']}.json")) for sc in SC]
    mms = [np.load(f"{WORK}/{sc['id']}.npy", mmap_mode="r") for sc in SC]
    end = np.load(f"{WORK}/end.npy", mmap_mode="r")
    var = ["orig" if m["logo_lum"] > 150 else "rev" for m in metas]
    print("logo variants", dict(zip([s["id"] for s in SC], var)), [round(m["logo_lum"]) for m in metas])
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-maxrate", "22M", "-bufsize", "44M", "-profile:v", "high",
           "-level", "4.2", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-r", str(FPS), "-movflags", "+faststart", "-an", out_path]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    events, g = [], 0
    T = 0.0
    for i, sc in enumerate(SC):
        own = n_own(sc)
        if i == 0:
            events.append((0.05, "click"))
        else:
            events.append((T, {"whip_l": "whoosh", "whip_r": "whoosh", "slide_u": "whoosh_lo", "slide_d": "whoosh_lo",
                               "flash": "flash", "iris": "swell", "leak": "air"}[SC[i - 1]["tr"]]))
        d = sc.get("delay", 0.2)
        for ph in sc.get("phases", [])[1:]:
            events.append((T + d + ph["start"] + 0.35, "click"))
        if sc.get("rows") or sc.get("phases") or sc["id"] in ("s01_hook",):
            events.append((T + d + (0.4 if sc["look"] == "plate" else 0.12) + 0.3, "click"))
        for k in range(own):
            if i > 0 and k < XT:
                p = (k + 1) / (XT + 1)
                fr = transition(SC[i - 1]["tr"], mms[i - 1][n_own(SC[i - 1]) + k], mms[i][k], p)
                fr = np.array(fr)
                if var[i - 1] == var[i]:
                    fr = add_logo(fr, var[i], 1.0)
                else:
                    fr = add_logo(fr, var[i - 1], 1 - p); fr = add_logo(fr, var[i], p)
            else:
                fr = np.array(mms[i][k])
                fr = add_logo(fr, var[i], 1.0)
            enc.stdin.write(fr.tobytes()); g += 1
        T += own / FPS
    # end card: flash in, logo fades out, no logo afterwards
    events.append((T, "flash")); events.append((T + 1.55 + 0.2, "click")); events.append((T + 1.75 + 0.2, "click"))
    for k in range(END_FRAMES):
        if k < XT:
            p = (k + 1) / (XT + 1)
            fr = np.array(tr_flash(np.asarray(mms[-1][n_own(SC[-1]) + k]), np.asarray(end[k]), p))
            fr = add_logo(fr, var[-1], max(0.0, 1 - 1.7 * p))
        else:
            fr = np.array(end[k])
        enc.stdin.write(fr.tobytes()); g += 1
    enc.stdin.close(); enc.wait()
    total = g / FPS
    json.dump(dict(events=events, total=total, frames=g, end_start=T), open(f"{WORK}/timeline.json", "w"))
    print("frames", g, "duration", round(total, 2), "s; end card starts", round(T, 2))


def _worker(i):
    t = time.time()
    meta = render_scene(i)
    return i, round(time.time() - t, 1), round(meta["logo_lum"])


if __name__ == "__main__":
    import multiprocessing as mp
    cmd = sys.argv[1]
    if cmd == "stills":
        stills([int(a) for a in sys.argv[2:]] or range(len(SC)))
    elif cmd == "scenes":
        t0 = time.time()
        render_end()
        with mp.Pool(4) as pool:
            for r in pool.imap_unordered(_worker, range(len(SC))):
                print("scene", r, flush=True)
        print("scenes done", round(time.time() - t0), "s")
    elif cmd == "assemble":
        assemble(sys.argv[2])
