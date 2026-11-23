"""Self-made SFX bed for the reel (whooshes, pops, impact, end-card chime). No licensed music.
Usage: python3 sfx.py out.wav"""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 33.0
rng = np.random.default_rng(3)
mix = np.zeros((int(SR * DUR), 2), np.float32)

def place(sig, t, gain, pan=0.0):
    i = int(t * SR); n = min(len(sig), len(mix) - i)
    if n <= 0: return
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i:i + n, 0] += sig[:n] * gain * l * 1.41
    mix[i:i + n, 1] += sig[:n] * gain * r * 1.41

def whoosh(length=0.45, lo=300, hi=3500):
    n = int(SR * length); x = rng.normal(0, 1, n)
    out = np.zeros(n); seg = 512
    for k in range(0, n, seg):
        u = k / n; fc = lo + (hi - lo) * np.sin(np.pi * u) ** 2
        sos = butter(2, [max(80, fc * 0.6), min(SR / 2 - 100, fc * 1.6)], 'bandpass', fs=SR, output='sos')
        out[k:k + seg] = sosfilt(sos, x[max(0, k - 2048):k + seg])[-len(out[k:k + seg]):]
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    s = out * env; return s / np.abs(s).max()

def pop(f=900):
    n = int(SR * 0.09); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t * (1 - 0.4 * t / t[-1])) * np.exp(-t * 55); return s / np.abs(s).max()

def impact():
    n = int(SR * 0.6); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (55 + 60 * np.exp(-t * 18)) * t) * np.exp(-t * 7)
    s += 0.25 * sosfilt(butter(2, 900, 'low', fs=SR, output='sos'), rng.normal(0, 1, n)) * np.exp(-t * 30)
    return s / np.abs(s).max()

def chime():
    n = int(SR * 2.2); t = np.arange(n) / SR; s = np.zeros(n)
    for f, a, d in [(1318.5, 1, 2.2), (1975.5, .55, 2.8), (2637, .35, 3.4), (659.3, .4, 1.6)]:
        s += a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
    for k in range(10):  # sparkle
        st = int(SR * (0.03 + 0.045 * k)); f = 3000 + 600 * rng.random()
        tt = t[:n - st]; s[st:] += 0.12 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 25)
    s *= np.minimum(1, t / 0.004); return s / np.abs(s).max()

# transitions (centred on the cut)
for t, L, g, pan in [(2.0, .5, .30, 0), (4.0, .4, .30, .4), (6.5, .4, .30, -.4), (12.0, .5, .30, 0), (17.5, .4, .30, .4),
                     (23.5, .5, .30, 0)]:
    place(whoosh(L), t - L / 2, g, pan)
for t in (15.5, 27.0):  # light leaks: soft long airy swell
    place(whoosh(1.0, 200, 1800), t - 0.5, 0.18)
place(whoosh(.35, 250, 2500), 17.9, 0.2)          # split open
# panel slide-ins and swaps
for k, t in enumerate([8.5, 8.62, 8.74]): place(whoosh(.3, 400, 4000), t, .14, [0, -.5, .5][k])
for k, t in enumerate([8.92, 9.04, 9.16]): place(pop(800 + 120 * k), t, .2, [0, -.5, .5][k])
for k, t in enumerate([10.25, 10.37, 10.49]): place(pop(1000 + 150 * k), t, .2, [0, -.5, .5][k])
for k, t in enumerate([20.5, 20.62, 20.74, 20.86]): place(whoosh(.3, 400, 4000), t, .13, [-.5, .5, -.5, .5][k])
place(impact(), 8.5, .26); place(impact(), 20.5, .22); place(impact(), 25.0, .24)
place(chime(), 30.65, .28); place(impact(), 30.65, .18)

peak = np.abs(mix).max(); mix *= 10 ** (-3 / 20) / peak
sf.write(sys.argv[1], mix, SR)
