"""Three editing directions for the spec'd-product scenes."""
from overlay import *

X0 = 72  # left text margin (inside 64)


def flow_chips(canvas, chips, x, y, t, start, maxw=862, gap=10, kind="navy", stagger=0.09, pop=True, fs=28):
    cx, cy = x, y
    for i, c in enumerate(chips):
        f = F("Inter-SemiBold", fs)
        if kind == "navy":
            im = chip(c, f, padx=20, h=58, r=29)
        elif kind == "white":
            im = chip(c, f, bg=(255, 255, 255, 245), fg=NAVY, dot=ORANGE, padx=20, h=58, r=29)
        else:  # glass-inner
            im = chip(c, f, bg=(255, 255, 255, 34), fg=WHITE, dot=ORANGE, outline=(255, 255, 255, 90), padx=18, h=54, r=27)
        if cx + im.width > x + maxw:
            cx = x
            cy += im.height + gap
        p = prog(t, start + i * stagger, 0.38)
        if p > 0:
            s = out_back(p) if pop else out_cubic(p)
            sc = 0.6 + 0.4 * s
            place(canvas, im, cx + im.width / 2, cy + im.height / 2 + (1 - out_cubic(p)) * 18,
                  opacity=clamp(p * 2.2), scale=sc, anchor="cm",
                  depth_kw=dict(soft=(0, 6, 14, 0.45), tight=(0, 2, 2, 0.35)))
        cx += im.width + gap
    return cy + 64


# ---------------- A: GALLERY LABEL ----------------
def style_A(canvas, bg, t, d, y=1118):
    """Editorial / museum-label minimalism: mask-rise type, growing hairline, solid navy chips."""
    num = text_img(d["num"], F("InterDisplay-SemiBold", 40), ORANGE, tracking=2)
    pn = prog(t, 0.0, 0.45)
    place(canvas, num, X0, y + (1 - out_cubic(pn)) * 14, opacity=pn)
    # hairline grows
    pl = prog(t, 0.1, 0.6)
    if pl > 0:
        ln = Image.new("RGBA", (max(1, int(150 * out_quint(pl))), 3), WHITE + (235,))
        place(canvas, ln, X0 + num.width + 18, y + 26, depth_kw=dict(soft=(0, 2, 4, 0.5), tight=(0, 1, 1, .3)))
    # title words mask-rise, staggered
    title = text_img(d["title"], F("InterDisplay-Medium", 92), WHITE, tracking=-1)
    pt = prog(t, 0.18, 0.75)
    place(canvas, mask_rise(title, pt), X0 - 4, y + 52)
    sub = text_img(d["sub"], F("Inter-Regular", 34), (255, 255, 255, 235), tracking=0.5)
    ps = prog(t, 0.42, 0.6)
    place(canvas, mask_rise(sub, ps), X0, y + 160, opacity=ps)
    flow_chips(canvas, d["chips"], X0, y + 220, t, 0.62, kind="navy", pop=False)


# ---------------- B: GLASS SPEC CARD ----------------
def style_B(canvas, bg, t, d, y=1095):
    """iOS 'liquid glass' card: frosted panel pops in (back-ease), big size counts up, glass chips."""
    p = prog(t, 0.0, 0.5)
    if p <= 0:
        return
    box_w, box_h = 868, 336
    s = 0.9 + 0.1 * out_back(p, 1.3)
    gx, gy = 66, y
    card = glass(bg, (gx, gy, gx + box_w, gy + box_h))
    place(canvas, card, gx + box_w / 2, gy + box_h / 2, opacity=clamp(p * 1.8), scale=s, anchor="cm",
          depth_kw=dict(soft=(0, 18, 34, 0.55), tight=(0, 3, 4, 0.3)))
    if p < 0.6:
        return
    ix = gx + 36
    badge = chip(d["num"], F("InterDisplay-Bold", 30), bg=ORANGE + (255,), fg=WHITE, dot=None, padx=18, h=52, r=14)
    pb = prog(t, 0.3, 0.3)
    place(canvas, badge, ix, gy + 34, opacity=pb, depth=False)
    cap = text_img(d["title"].upper(), F("Inter-SemiBold", 30), WHITE, tracking=5)
    place(canvas, wipe_lr(cap, prog(t, 0.36, 0.45)), ix + badge.width + 20, gy + 42, depth=False)
    # count-up hero number
    pc = out_cubic(prog(t, 0.4, 0.9))
    val = int(round(d["big_val"] * pc))
    big = text_img(f"{val}", F("InterDisplay-Bold", 120), WHITE, tracking=-2)
    unit = text_img(d["big_unit"], F("InterDisplay-Medium", 48), (255, 255, 255, 230))
    po = prog(t, 0.4, 0.3)
    place(canvas, big, ix - 4, gy + 92, opacity=po, depth=False)
    place(canvas, unit, ix + big.width + 8, gy + 152, opacity=po, depth=False)
    flow_chips(canvas, d["chips_b"], ix, gy + 252, t, 0.7, maxw=box_w - 64, kind="glass", gap=8, fs=26)


# ---------------- C: LIGHT-ON KINETIC ----------------
def style_C(canvas, bg, t, d, y=1150, anchor_pt=(430, 1092)):
    """Oversized extruded headline, letters drop in with a light-on flicker; leader-line callout to the fixture."""
    word = d["word"]
    f = F("InterDisplay-Black", 184)
    # leader line from fixture to label
    pl = prog(t, 0.0, 0.5)
    if pl > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        ax, ay = anchor_pt
        e = out_cubic(pl)
        # elbow: down from fixture, then left to the text margin
        p1 = (ax, ay + 44)
        seg1 = min(1, e * 2); seg2 = max(0, e * 2 - 1)
        dr.line((ax, ay, ax, ay + 44 * seg1), fill=WHITE + (235,), width=3)
        if seg2 > 0:
            dr.line((ax, p1[1], ax + (X0 + 4 - ax) * seg2, p1[1]), fill=WHITE + (235,), width=3)
        r = 9
        dr.ellipse((ax - r, ay - r, ax + r, ay + r), fill=ORANGE + (255,), outline=WHITE + (255,), width=3)
        sh = lay.split()[3].filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * .5))
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); shadow.putalpha(sh)
        canvas.alpha_composite(shadow, (0, 3)); canvas.alpha_composite(lay)
    # extruded letters
    x = X0 - 6
    for i, ch in enumerate(word):
        p = prog(t, 0.22 + i * 0.07, 0.45)
        cw = f.getlength(ch)
        if p > 0:
            face = text_img(ch, f, WHITE)
            ext = Image.new("RGBA", (face.width + 14, face.height + 14), (0, 0, 0, 0))
            for k in range(10, 0, -1):  # navy extrusion = 3D depth
                shade = tuple(int(c * (0.55 + 0.045 * (10 - k))) for c in NAVY)
                ext.alpha_composite(face.copy().point(lambda v: v) if False else _tint(face, shade), (k, k))
            # light-on flicker: face brightens 60%->100% with a blip
            fl = 1.0 if p > 0.7 else (0.55 + 0.45 * p / 0.7) * (0.75 if 0.3 < p < 0.4 else 1.0)
            ext.alpha_composite(_tint(face, tuple(int(255 * fl) for _ in range(3))), (0, 0))
            dy = (1 - out_back(p, 1.2)) * -70
            place(canvas, ext, x, y + dy, opacity=clamp(p * 2.5),
                  depth_kw=dict(soft=(0, 16, 26, 0.55), tight=(0, 3, 3, 0.35)))
        x += cw - 6
    spec = text_img(d["spec"], F("Inter-SemiBold", 30), WHITE, tracking=3)
    ps = prog(t, 0.65, 0.5)
    place(canvas, wipe_lr(spec, ps), X0, y + 206)
    flow_chips(canvas, d["chips_c"], X0, y + 258, t, 0.85, kind="white")


def _tint(face, rgb):
    im = Image.new("RGBA", face.size, rgb + (255,))
    im.putalpha(face.split()[3])
    return im


DONUT = dict(
    num="01", title="Donut Pendant", sub="600 mm Donut  ·  Black finish  ·  50 × 70 mm",
    chips=["36 W & 40 W", "4000K Natural White", "Canopy + 1.5 m kit"],
    big_val=600, big_unit="mm Donut",
    chips_b=["36 W & 40 W", "4000K Natural White", "Black finish"],
    word="DONUT", spec="01  ·  PENDANT  ·  600 mm  ·  BLACK",
    chips_c=["36 W & 40 W", "4000K Natural White"],
)
