"""Adniv x CRUSH reel - overlay engine (text, chips, logo, depth, animation)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1920
NAVY = (27, 31, 84)
ORANGE = (247, 147, 30)
WHITE = (255, 255, 255)
SAFE = dict(x0=64, x1=1016, y0=230, y1=1500, icons_x=940, icons_y0=1000)
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}


def F(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + name + ".otf", size)
    return _fc[k]


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, start, dur):
    return clamp((t - start) / dur)


def out_cubic(x):
    return 1 - (1 - x) ** 3


def out_quint(x):
    return 1 - (1 - x) ** 5


def out_back(x, s=1.6):
    x = x - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def in_out(x):
    return 3 * x * x - 2 * x * x * x


# ---------- primitives ----------
def text_img(text, font, fill=WHITE, tracking=0):
    """Render text tightly into RGBA with optional letter tracking (px)."""
    asc, desc = font.getmetrics()
    if tracking == 0:
        w = int(font.getlength(text)) + 4
    else:
        w = int(sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)) + 4
    im = Image.new("RGBA", (max(w, 1), asc + desc + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking == 0:
        d.text((2, 2), text, font=font, fill=fill)
    else:
        x = 2
        for c in text:
            d.text((x, 2), c, font=font, fill=fill)
            x += font.getlength(c) + tracking
    return im


def with_depth(layer, soft=(0, 8, 22, 0.55), tight=(0, 2, 3, 0.45), pad=48):
    """Add a soft ambient shadow + tight contact shadow under a layer -> real depth, no frame darkening."""
    w, h = layer.size
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = layer.split()[3]
    for dx, dy, r, op in (soft, tight):
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        m = Image.new("L", out.size, 0)
        m.paste(a, (pad + dx, pad + dy))
        m = m.filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * op))
        sh.putalpha(m)
        out = Image.alpha_composite(out, sh)
    out.alpha_composite(layer, (pad, pad))
    return out, pad


def place(canvas, layer, x, y, opacity=1.0, scale=1.0, anchor="lt", depth=True, depth_kw=None):
    """Composite layer onto canvas at (x,y) (anchor lt / ct / rt / lb), with depth shadow, opacity and scale."""
    if layer is None or opacity <= 0.001:
        return
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.LANCZOS)
    pad = 0
    if depth:
        layer, pad = with_depth(layer, **(depth_kw or {}))
    w, h = layer.size
    iw, ih = w - 2 * pad, h - 2 * pad
    if anchor[0] == "c":
        x -= iw / 2
    elif anchor[0] == "r":
        x -= iw
    if anchor[1] == "b":
        y -= ih
    elif anchor[1] == "m":
        y -= ih / 2
    if opacity < 1:
        a = layer.split()[3].point(lambda v: int(v * opacity))
        layer.putalpha(a)
    canvas.alpha_composite(layer, (int(round(x - pad)), int(round(y - pad))))


def mask_rise(layer, p):
    """Mask-wipe reveal: text rises from behind an invisible baseline. p 0..1"""
    w, h = layer.size
    e = out_quint(p)
    off = int((1 - e) * h * 1.05)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(layer, (0, 0) if off == 0 else (0, 0))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if off < h:
        out.alpha_composite(layer.crop((0, 0, w, h - off)), (0, off))
    return out


def wipe_lr(layer, p):
    w, h = layer.size
    cut = int(w * out_cubic(p))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if cut > 0:
        out.alpha_composite(layer.crop((0, 0, cut, h)), (0, 0))
    return out


def rounded(size, r, fill, outline=None, ow=0):
    s = 3  # supersample for smooth edges
    im = Image.new("RGBA", (size[0] * s, size[1] * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] * s - 1, size[1] * s - 1), r * s, fill=fill,
                                         outline=outline, width=ow * s)
    return im.resize(size, Image.LANCZOS)


def chip(text, font=None, bg=NAVY + (240,), fg=WHITE, dot=ORANGE, padx=26, h=64, r=32, outline=None):
    font = font or F("Inter-SemiBold", 30)
    t = text_img(text, font, fg)
    dotw = 22 if dot else 0
    w = t.width + 2 * padx + dotw
    c = rounded((w, h), r, bg, outline=outline, ow=2 if outline else 0)
    if dot:
        d = Image.new("RGBA", (36, 36), (0, 0, 0, 0))
        ImageDraw.Draw(d).ellipse((0, 0, 35, 35), fill=dot + (255,))
        d = d.resize((12, 12), Image.LANCZOS)
        c.alpha_composite(d, (padx, h // 2 - 6))
    asc, desc = font.getmetrics()
    c.alpha_composite(t, (padx + dotw, int(h / 2 - (asc + desc) / 2 - 1)))
    return c


_logo_cache = {}


def logo(width=210, dark=False):
    """Typeset placeholder for the Adniv logo (swap for client PNG before final render)."""
    k = (width, dark)
    if k in _logo_cache:
        return _logo_cache[k]
    path = "/tmp/claude-0/-home-user-The100xers/3dc716bb-8387-5a31-912b-63c195d92910/scratchpad/assets/adniv_logo.png"
    import os
    if os.path.exists(path):
        im = Image.open(path).convert("RGBA")
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    else:
        col = NAVY if dark else WHITE
        word = text_img("ADNIV", F("InterDisplay-Bold", 64), col, tracking=10)
        tag = text_img("We light. We power. We build.", F("Inter-Medium", 17), col, tracking=0.5)
        sc = width / word.width
        word = word.resize((width, int(word.height * sc)), Image.LANCZOS)
        tag = tag.resize((width, int(tag.height * width / tag.width)), Image.LANCZOS)
        im = Image.new("RGBA", (width, word.height + tag.height + 6), (0, 0, 0, 0))
        im.alpha_composite(word, (0, 0))
        bar = Image.new("RGBA", (int(width * 0.18), 3), ORANGE + (255,))
        im.alpha_composite(tag, (0, word.height + 6))
    _logo_cache[k] = im
    return im


def place_logo(canvas, opacity=1.0, width=210):
    lg = logo(width)
    place(canvas, lg, SAFE["x1"], 244, opacity=opacity, anchor="rt",
          depth_kw=dict(soft=(0, 4, 12, 0.5), tight=(0, 1, 2, 0.4)))


def glass(bg_rgb, box, radius=36, blur=28, tint=(255, 255, 255, 26), border=(255, 255, 255, 80)):
    """Frosted-glass panel: blurs ONLY the footage under the card (small element), hairline border, top sheen."""
    x0, y0, x1, y1 = box
    region = bg_rgb.crop(box).filter(ImageFilter.GaussianBlur(blur)).convert("RGBA")
    region.alpha_composite(Image.new("RGBA", region.size, tint))
    sheen = Image.new("L", region.size, 0)
    sd = ImageDraw.Draw(sheen)
    for i in range(region.size[1] // 2):
        sd.line((0, i, region.size[0], i), fill=int(30 * (1 - i / (region.size[1] / 2))))
    region.alpha_composite(Image.merge("RGBA", (*[Image.new("L", region.size, 255)] * 3, sheen)))
    m = rounded(region.size, radius, (255, 255, 255, 255)).split()[3]
    region.putalpha(m)
    edge = rounded(region.size, radius, (0, 0, 0, 0), outline=border, ow=2)
    region.alpha_composite(edge)
    return region


def safe_overlay(img):
    """Draw Instagram Reels UI-forbidden zones for QA."""
    im = img.convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    red = (255, 40, 40, 90)
    d.rectangle((0, 0, W, 230), fill=red)
    d.rectangle((0, 1500, W, H), fill=red)
    d.rectangle((0, 230, 64, 1500), fill=red)
    d.rectangle((1016, 230, W, 1500), fill=red)
    d.rectangle((940, 1000, 1016, 1500), fill=(255, 140, 0, 110))
    d.rectangle((64, 230, 1016, 1500), outline=(0, 255, 120, 255), width=4)
    f = F("Inter-Bold", 26)
    d.text((80, 190), "TOP BAR (no graphics)", font=f, fill="white")
    d.text((80, 1520), "CAPTION / USERNAME / AUDIO (no graphics)", font=f, fill="white")
    d.text((700, 1460), "ICON COLUMN", font=f, fill=(255, 200, 120))
    d.text((80, 240), "SAFE AREA x64-1016, y230-1500", font=F("Inter-Bold", 22), fill=(0, 255, 120))
    return Image.alpha_composite(im, ov)
