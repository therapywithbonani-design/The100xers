"""Cinematic 'golden heritage' grade for the City Palace reel.

Pipeline (all on 8-bit BGR in, float32 BGR 0..1 out):
 1. Per-source levels: fixed black/white points measured once per source (no flicker),
    so the flat HLG->SDR video matches the punchier iPhone photos.
 2. Clarity / dehaze: CLAHE on L (LAB) blended in, lifts the hazy city and carved stone.
 3. Filmic tone curve: soft toe with a slight black lift (matte), gentle S, soft highlight shoulder.
 4. Colour: vibrance, warm-tone boost (sandstone, gold, saffron), sky pushed slightly teal and deeper,
    greens muted toward olive, split-tone (teal shadows / amber highlights).
 5. Halation: soft warm glow from highlights.
"""
import numpy as np, cv2

def _levels_lut(black, white, gamma=1.0):
    x = np.arange(256, dtype=np.float32)
    y = np.clip((x - black) / max(1.0, white - black), 0, 1) ** gamma
    return (y * 255 + 0.5).astype(np.uint8)

def measure(samples):
    """samples: list of uint8 BGR images from one source -> (black, white) on luma."""
    lo, hi = [], []
    for s in samples:
        y = cv2.cvtColor(cv2.resize(s, (270, 480)), cv2.COLOR_BGR2GRAY)
        lo.append(np.percentile(y, 0.4)); hi.append(np.percentile(y, 99.6))
    return float(np.median(lo)), float(np.median(hi))

# filmic curve LUT (0..1 -> 0..1)
_t = np.linspace(0, 1, 1024, dtype=np.float32)
def _filmic(x):
    s = x * x * (3 - 2 * x)                       # S
    y = 0.55 * x + 0.45 * s
    y = 0.028 + (1 - 0.028 - 0.02) * y            # matte black lift, highlight roll-off below pure white
    sh = np.clip((y - 0.82) / 0.18, 0, 1)         # soft shoulder
    return y - 0.035 * sh * sh
FILMIC = _filmic(_t).astype(np.float32)

_clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(6, 10))

def grade(u8, levels=None, clarity=0.32, strength=1.0):
    img = u8
    if levels is not None:
        b, w = levels
        img = cv2.LUT(img, _levels_lut(b - 2, w + 4, 0.96))
    # clarity / dehaze on L
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L = lab[..., 0]
    Lc = _clahe.apply(L)
    lab[..., 0] = cv2.addWeighted(L, 1 - clarity, Lc, clarity, 0)
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    f = img.astype(np.float32) / 255.0
    # filmic tone curve applied on luma, ratio-preserving (keeps hue)
    Y = f[..., 0] * 0.114 + f[..., 1] * 0.587 + f[..., 2] * 0.299
    Yt = np.interp(Y, _t, FILMIC).astype(np.float32)
    f = f * ((Yt + 1e-4) / (Y + 1e-4))[..., None]
    f = np.clip(f, 0, 1)

    # selective colour in HSV (OpenCV float HSV: H 0..360, S/V 0..1)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    H, Sat, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    def band(c, wdt):  # smooth hue window
        d = np.abs(((H - c + 180) % 360) - 180)
        return np.clip(1 - d / wdt, 0, 1)
    warm = band(32, 28)      # oranges, sandstone, gold
    red = band(5, 16)        # reds / saffron
    sky = band(212, 30)      # blues
    green = band(105, 40)    # foliage
    teal = band(175, 22)     # painted turquoise walls
    vib = 1 + 0.30 * (1 - Sat) * strength                       # vibrance
    Sat = Sat * vib * (1 + 0.14 * warm + 0.10 * red + 0.18 * sky + 0.12 * teal - 0.25 * green)
    H = H - 6 * sky - 6 * green                                  # sky toward cyan-teal, foliage toward olive
    V = V * (1 - 0.10 * sky * np.clip(V - 0.45, 0, 1) / 0.55)   # deeper sky
    V = V * (1 + 0.03 * warm)                                    # warm glow on stone
    hsv = np.stack([H % 360, np.clip(Sat, 0, 1), np.clip(V, 0, 1)], -1)
    f = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # split toning: teal shadows, amber highlights (BGR)
    Y = f[..., 0] * 0.114 + f[..., 1] * 0.587 + f[..., 2] * 0.299
    sh = np.clip(1 - Y / 0.45, 0, 1)[..., None] ** 1.5
    hi = np.clip((Y - 0.55) / 0.45, 0, 1)[..., None]
    f = f + sh * np.array([0.030, 0.012, -0.022], np.float32) * strength \
          + hi * np.array([-0.035, 0.004, 0.030], np.float32) * strength

    # halation: warm glow from highlights
    small = cv2.resize(f, (f.shape[1] // 4, f.shape[0] // 4), interpolation=cv2.INTER_AREA)
    hl = np.clip((small - 0.72) / 0.28, 0, 1)
    glow = cv2.GaussianBlur(hl, (0, 0), 10) * np.array([0.55, 0.85, 1.0], np.float32)
    glow = cv2.resize(glow, (f.shape[1], f.shape[0]), interpolation=cv2.INTER_LINEAR)
    f = 1 - (1 - f) * (1 - 0.22 * glow)
    return np.clip(f, 0, 1)
