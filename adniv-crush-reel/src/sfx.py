"""Subtle premium SFX stem: whooshes, light-switch clicks, flash shimmer. Synthesised (no samples), 48 kHz stereo."""
import json, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def env(n, a, r, curve=2.0):
    t = np.arange(n) / n
    e = np.minimum(t / max(a, 1e-4), 1.0) ** curve * np.minimum((1 - t) / max(r, 1e-4), 1.0) ** curve
    return e


def swept_noise(dur, f0, f1, q=0.22, a=0.45, r=0.55):
    """Band-limited noise whose centre frequency sweeps f0 -> f1 (STFT filtering)."""
    n = int(dur * SR)
    x = rng.standard_normal(n + 2048)
    blk, hop = 1024, 512
    win = np.hanning(blk)
    out = np.zeros(n + 2048)
    nb = (n + 1024) // hop
    fr = np.fft.rfftfreq(blk, 1 / SR)
    for b in range(nb):
        i = b * hop
        if i + blk > len(x):
            break
        c = f0 * (f1 / f0) ** (i / max(n, 1))
        g = np.exp(-0.5 * (np.log2((fr + 1) / c) / q) ** 2)
        seg = np.fft.irfft(np.fft.rfft(x[i:i + blk] * win) * g, blk)
        out[i:i + blk] += seg * win
    out = out[:n]
    out /= np.abs(out).max() + 1e-9
    return out * env(n, a, r)


def whoosh(lo=False):
    d = 0.5 if not lo else 0.55
    a = swept_noise(d, 500, 4200, 0.45) if not lo else swept_noise(d, 220, 1800, 0.5)
    return a * (0.55 if not lo else 0.5)


def click():
    n = int(0.12 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 55) * 0.55
    tick = np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 520) * 0.5
    nz = rng.standard_normal(n) * np.exp(-t * 900) * 0.35
    return thump + tick + nz


def flash():
    n = int(0.55 * SR); t = np.arange(n) / SR
    sh = sum(np.sin(2 * np.pi * f * t + p) * a for f, a, p in
             [(1318, .22, 0), (1976, .16, 1), (2637, .12, 2), (3951, .08, 3)]) * np.exp(-t * 7.5)
    sh *= np.minimum(t / 0.012, 1)
    return sh * 0.6 + swept_noise(0.35, 1200, 6500, 0.55, 0.3, 0.6)[:n].mean() * 0 + np.pad(
        swept_noise(0.35, 1200, 6500, 0.55, 0.3, 0.6) * 0.35, (0, n - int(0.35 * SR)))


def swell():
    return swept_noise(0.55, 160, 2400, 0.5, 0.7, 0.3) * 0.6


def air():
    return swept_noise(0.55, 900, 2600, 0.8, 0.5, 0.5) * 0.35


BANK = dict(whoosh=whoosh, whoosh_lo=lambda: whoosh(True), click=click, flash=flash, swell=swell, air=air)


def build(timeline, out):
    tl = json.load(open(timeline))
    n = int((tl["total"] + 0.8) * SR)
    L = np.zeros(n); R = np.zeros(n)
    for t, kind in tl["events"]:
        s = BANK[kind]()
        pre = 0.18 if kind in ("whoosh", "whoosh_lo", "swell", "air") else 0.0   # whoosh peaks into the cut
        i = max(int((t - pre) * SR), 0)
        pan = 0.5 + 0.18 * np.sin(t * 3.1)
        e = min(i + len(s), n)
        L[i:e] += s[:e - i] * (1 - pan) * 1.2
        R[i:e] += s[:e - i] * pan * 1.2
    peak = max(np.abs(L).max(), np.abs(R).max())
    g = 10 ** (-4 / 20) / peak
    st = np.stack([L, R], 1) * g
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print("sfx", out, round(n / SR, 2), "s", len(tl["events"]), "cues")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
