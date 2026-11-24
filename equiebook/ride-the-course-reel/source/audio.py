import json, sys, wave, numpy as np
meta = json.load(open(sys.argv[1])); out = sys.argv[2]
SR = 48000; DUR = meta['DUR']; N = int(SR * (DUR + 4))
L = np.zeros(N); Rch = np.zeros(N)
rs = np.random.default_rng(5)
t_all = np.arange(N) / SR

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[:j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414 / 1.414 * (1 - max(0, pan) * 0.5)
    Rch[i:j] += s * (1 - max(0, -pan) * 0.5)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = ((f >= lo) & (f <= hi)).astype(float)
    # soft edges
    m = np.convolve(m, np.hanning(41) / np.hanning(41).sum(), 'same')
    return np.fft.irfft(X * m, len(x))

def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)

# ---------- hoofbeat ----------
def hoof(strength=1.0):
    n = int(0.18 * SR); t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (70 + 40 * np.exp(-t * 40)) * t) * env(n, 0.002, 0.05)
    grit = band(rs.standard_normal(n), 900, 4500) * env(n, 0.001, 0.025) * 0.9
    return (thud * 0.9 + grit * 0.6) * strength

V = meta['strides']
for s in V:
    if s['v'] < 0.15: continue
    T = 1 / (1.2 + 0.55 * min(1, s['v']))
    for k, off in enumerate([0.0, 0.16, 0.3]):
        if s['air'] > 0.25: continue
        add(hoof(0.55 + 0.45 * s['v']) * (1.15 if k == 2 else 0.85), s['t'] + off * T + rs.uniform(-0.004, 0.004), 0.55, pan=[-0.2, 0.2, 0][k])

# ---------- jumps ----------
for f in meta['fences']:
    d = f['tLD'] - f['tTO']; n = int((d + 0.3) * SR); t = np.arange(n) / SR
    w = band(rs.standard_normal(n), 300, 2500) * np.sin(np.pi * np.clip(t / (d + 0.3), 0, 1)) ** 2
    add(w, f['tTO'] - 0.1, 0.18)
    add(hoof(1.6), f['tTO'] - 0.05, 0.6)                       # take-off push
    add(hoof(2.0), f['tLD'], 0.75); add(hoof(1.6), f['tLD'] + 0.09, 0.6)   # landing
    # leather creak / breath
    nb = int(0.35 * SR); add(band(rs.standard_normal(nb), 200, 900) * env(nb, 0.05, 0.12), f['tTO'] - 0.12, 0.25)

# ---------- UI sounds ----------
def tone(freq, dur, dec, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)) * env(n, 0.003, dec) * amp
for p in meta['prompts']:
    if p['text'] in ('CLEAR ROUND!',): continue
    add(tone(880, 0.25, 0.06) + tone(1320, 0.25, 0.05, 0.5), p['t0'], 0.16)
    if p.get('press'): add(tone(220, 0.2, 0.05), p['press'], 0.25)
for f in meta['fences']:
    add(tone(1318.5, 0.5, 0.15), f['tLD'] + 0.02, 0.1); add(tone(1975.5, 0.6, 0.2), f['tLD'] + 0.1, 0.08)

# ---------- snort in intro ----------
n = int(0.6 * SR); t = np.arange(n) / SR
sn = band(rs.standard_normal(n), 250, 1400) * (np.sin(np.pi * t / 0.6) ** 0.6) * (1 + 0.5 * np.sin(2 * np.pi * 18 * t))
add(sn, 1.4, 0.35)

# ---------- crowd ambience + cheer ----------
amb = band(rs.standard_normal(N), 250, 2200)
amb /= np.abs(amb).max()
tc = meta['tClear']; te = meta['tEnd']
lvl = 0.05 + 0.25 * np.clip((t_all - tc + 0.2) / 0.4, 0, 1) * np.exp(-np.clip(t_all - tc, 0, None) / 2.6)
lvl *= np.where(t_all > te + 0.6, np.exp(-(t_all - te - 0.6) / 0.6), 1)
L += amb * lvl; Rch += np.roll(amb, 3000) * lvl
for k in range(260):  # claps
    tt = tc + rs.uniform(0.1, 3.0) ** 1.3; nn = int(0.03 * SR)
    add(band(rs.standard_normal(nn), 800, 5000) * env(nn, 0.001, 0.008), tt, 0.12 * rs.uniform(0.3, 1), pan=rs.uniform(-0.8, 0.8))

# ---------- music bed (D major, 120bpm) ----------
bpm = 120; beat = 60 / bpm
def note(m): return 440 * 2 ** ((m - 69) / 12)
prog = [[62, 66, 69, 74], [59, 62, 66, 71], [55, 59, 62, 67], [57, 61, 64, 69]]  # D Bm G A
music = np.zeros(N)
bar = 4 * beat
nbars = int(DUR / bar) + 1
for b in range(nbars):
    ch = prog[b % 4]; t0 = b * bar
    n = int(bar * SR) + int(0.4 * SR); t = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * note(m) * t) + 0.5 * np.sin(2 * np.pi * note(m) * 1.003 * t) for m in ch) / 6
    pad *= np.minimum(1, t / 0.25) * np.minimum(1, np.maximum(0, (bar + 0.4 - t) / 0.4))
    i = int(t0 * SR); j = min(N, i + n); music[i:j] += pad[:j - i] * 0.35
    # bass pulse eighths
    for e in range(8):
        tb = t0 + e * beat / 2; nn = int(beat / 2 * SR); tt = np.arange(nn) / SR
        bs = np.sin(2 * np.pi * note(ch[0] - 24) * tt) * env(nn, 0.005, 0.12)
        i = int(tb * SR); j = min(N, i + nn)
        if tb > meta['T0'] - 0.1: music[i:j] += bs[:j - i] * 0.55
    # pluck arpeggio after start
    if t0 > meta['T0'] - 0.1:
        for e in range(8):
            m = ch[[0, 1, 2, 3, 2, 1, 2, 3][e]] + 12; tb = t0 + e * beat / 2; nn = int(0.4 * SR); tt = np.arange(nn) / SR
            pl = (np.sin(2 * np.pi * note(m) * tt) + 0.25 * np.sin(2 * np.pi * note(m) * 3 * tt)) * env(nn, 0.002, 0.12)
            i = int(tb * SR); j = min(N, i + nn); music[i:j] += pl[:j - i] * 0.18
# kick on beats during ride
for k in range(int(DUR / beat)):
    tb = k * beat
    if meta['T0'] - 0.05 < tb < meta['tClear']:
        nn = int(0.25 * SR); tt = np.arange(nn) / SR
        kk = np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * env(nn, 0.001, 0.09)
        i = int(tb * SR); j = min(N, i + nn); music[i:j] += kk[:j - i] * 0.5
# clear-round swell + final chord
nn = int(1.2 * SR); tt = np.arange(nn) / SR
sw = band(rs.standard_normal(nn), 3000, 12000) * (tt / 1.2) ** 3
add(sw, tc - 1.2, 0.12)
nn = int(4.5 * SR); tt = np.arange(nn) / SR
fin = sum(np.sin(2 * np.pi * note(m) * tt) for m in [50, 62, 66, 69, 74, 78]) / 6 * np.minimum(1, tt / 0.05) * np.exp(-tt / 2.2)
music[int(tc * SR):int(tc * SR) + nn] += fin[:max(0, min(nn, N - int(tc * SR)))] * 0.9
music *= np.clip(1.2 - 0.0 * t_all, 0, 1)
fade = np.clip((DUR - t_all) / 1.2, 0, 1)
L += music * 0.32; Rch += music * 0.32
L *= fade; Rch *= fade
pk = max(np.abs(L).max(), np.abs(Rch).max()); L /= pk / 0.89; Rch /= pk / 0.89
L = np.tanh(L * 1.2) / np.tanh(1.2); Rch = np.tanh(Rch * 1.2) / np.tanh(1.2)
n = int(DUR * SR)
st = np.stack([L[:n], Rch[:n]], 1)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', DUR)
