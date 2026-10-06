"""A tiny numpy synthesizer: instruments, drums, reverb and a jianpu sequencer."""
import math

import numpy as np

SR = 44100
RNG = np.random.default_rng(7)


def midi_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def env_adsr(n, a=0.005, d=0.1, s=0.7, r=0.1, sr=SR):
    a_n, d_n, r_n = int(a * sr), int(d * sr), int(r * sr)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([
        np.linspace(0, 1, max(a_n, 1), endpoint=False),
        np.linspace(1, s, max(d_n, 1), endpoint=False),
        np.full(s_n, s),
        np.linspace(s, 0, max(r_n, 1)),
    ])
    if len(e) < n:
        e = np.concatenate([e, np.zeros(n - len(e))])
    return e[:n]


def fft_filter(x, lo=None, hi=None, sr=SR):
    """Brick-ish (smoothed) band filter in the frequency domain."""
    n = len(x)
    if n == 0:
        return x
    size = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, size)
    f = np.fft.rfftfreq(size, 1.0 / sr)
    g = np.ones_like(f)
    if hi:
        g *= 1.0 / (1.0 + (f / hi) ** 4)
    if lo:
        g *= 1.0 / (1.0 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * g, size)[:n]


# ---------------------------------------------------------------------------
# instruments: fn(freq, dur_seconds, vel) -> mono np.array
# ---------------------------------------------------------------------------

def piano(f, dur, vel=0.8, bright=1.0):
    length = dur + 1.6
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h in range(1, 10):
        fh = f * h * (1 + 0.0004 * h * h)
        if fh > 16000:
            break
        amp = (1.0 / h ** 1.25) * (bright if h > 3 else 1)
        decay = 1.2 + 0.9 * h * (f / 440) ** 0.5
        out += amp * np.sin(2 * np.pi * fh * t + h) * np.exp(-t * decay)
    # hammer
    k = int(0.012 * SR)
    out[:k] += RNG.normal(0, 0.15, k) * np.linspace(1, 0, k)
    # damper release after note-off
    off = int(dur * SR)
    rel = np.ones(n)
    rel[off:] = np.exp(-np.arange(n - off) / (0.12 * SR))
    out *= rel
    out[:64] *= np.linspace(0, 1, 64)
    return out * vel * 0.35


def musicbox(f, dur, vel=0.8):
    n = int((dur + 2.0) * SR)
    t = np.arange(n) / SR
    out = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
           + 0.35 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 6)
           + 0.18 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)
           + 0.08 * np.sin(2 * np.pi * f * 8.9 * t) * np.exp(-t * 18))
    out[:32] *= np.linspace(0, 1, 32)
    return out * vel * 0.35


def bell(f, dur, vel=0.8):
    n = int((dur + 2.5) * SR)
    t = np.arange(n) / SR
    idx = 3.0 * np.exp(-t * 3)
    out = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t * 1.6)
    out[:32] *= np.linspace(0, 1, 32)
    return out * vel * 0.25


def epiano(f, dur, vel=0.8):
    """FM 'Rhodes'"""
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    idx = 1.8 * np.exp(-t * 4) * vel + 0.2
    out = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    out += 0.15 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t * 30)  # tine
    e = np.exp(-t * 1.4)
    off = int(dur * SR)
    e[off:] *= np.exp(-np.arange(n - off) / (0.15 * SR))
    out *= e
    out[:64] *= np.linspace(0, 1, 64)
    return out * vel * 0.3


def pluck(f, dur, vel=0.8, damp=0.996, bright=0.5):
    """Karplus-Strong string, vectorised per period."""
    total = int((dur + 1.0) * SR)
    N = max(2, int(round(SR / f - 0.5)))
    buf = RNG.uniform(-1, 1, N)
    # soften the excitation
    for _ in range(int((1 - bright) * 4)):
        buf = 0.5 * (buf + np.roll(buf, 1))
    out = np.zeros(total + N)
    out[:N] = buf
    start = N
    while start < total:
        prev = out[start - N:start]
        before = out[start - N - 1] if start - N - 1 >= 0 else 0.0
        shifted = np.concatenate(([before], prev[:-1]))
        seg = damp * 0.5 * (prev + shifted)
        out[start:start + N] = seg
        start += N
    out = out[:total]
    off = int(dur * SR)
    if off < total:
        out[off:] *= np.exp(-np.arange(total - off) / (0.08 * SR))
    return out * vel * 0.45


def guitar(f, dur, vel=0.8):
    return pluck(f, dur, vel, damp=0.997, bright=0.4)


def nylon(f, dur, vel=0.8):
    return pluck(f, dur, vel, damp=0.995, bright=0.1) * 1.1


def harmonica(f, dur, vel=0.8, vibrato=True):
    n = int((dur + 0.15) * SR)
    t = np.arange(n) / SR
    vib = 1 + (0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t * 2 - 0.3, 0, 1) if vibrato else 0)
    phase = 2 * np.pi * f * np.cumsum(vib) / SR
    out = np.zeros(n)
    for h in range(1, 14):
        if f * h > 12000:
            break
        # reed: strong odd+even, formant around 1.2-2.5 kHz
        form = 1.0 + 0.7 * math.exp(-((f * h - 1800) / 900) ** 2)
        weight = 1.8 if h == 1 else (1.0 / h ** 1.05)
        out += weight * form * np.sin(h * phase)
    out += RNG.normal(0, 0.05, n) * 0.6   # breath
    e = env_adsr(n, a=0.04, d=0.08, s=0.85, r=0.12)
    out = out * e
    out = fft_filter(out, lo=180, hi=5000)
    return out * vel * 0.12


def recorder(f, dur, vel=0.8):
    n = int((dur + 0.1) * SR)
    t = np.arange(n) / SR
    out = np.sin(2 * np.pi * f * t) + 0.12 * np.sin(4 * np.pi * f * t) + 0.05 * np.sin(6 * np.pi * f * t)
    out += fft_filter(RNG.normal(0, 0.08, n), lo=1500, hi=6000)
    out *= env_adsr(n, a=0.03, d=0.05, s=0.85, r=0.08)
    return out * vel * 0.3


def pad(f, dur, vel=0.6):
    n = int((dur + 1.0) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-0.006, 0.0, 0.007):
        ph = 2 * np.pi * f * (1 + det) * t
        # band-limited saw approximation (8 partials)
        for h in range(1, 9):
            out += np.sin(h * ph) / h * (0.6 if det else 1)
    out = fft_filter(out, hi=1400 + f)
    out *= env_adsr(n, a=0.6, d=0.3, s=0.8, r=0.9)
    return out * vel * 0.05


def strings(f, dur, vel=0.6):
    n = int((dur + 0.8) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.5 * t + RNG.uniform(0, 6))
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    out = np.zeros(n)
    for h in range(1, 12):
        if f * h > 9000:
            break
        out += np.sin(h * ph) / h
    out = fft_filter(out, hi=2600)
    out *= env_adsr(n, a=0.25, d=0.2, s=0.85, r=0.6)
    return out * vel * 0.09


def bass(f, dur, vel=0.8):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    out = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    out *= env_adsr(n, a=0.008, d=0.25, s=0.6, r=0.12)
    return out * vel * 0.32


def marimba(f, dur, vel=0.8):
    n = int((dur + 0.8) * SR)
    t = np.arange(n) / SR
    out = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)
    out[:48] *= np.linspace(0, 1, 48)
    return out * vel * 0.4


def epiano_lofi(f, dur, vel=0.8):
    x = epiano(f, dur, vel)
    return fft_filter(x, hi=2500)


INSTRUMENTS = {
    'piano': piano, 'musicbox': musicbox, 'bell': bell, 'epiano': epiano, 'guitar': guitar,
    'nylon': nylon, 'harmonica': harmonica, 'recorder': recorder, 'pad': pad, 'strings': strings,
    'bass': bass, 'marimba': marimba, 'lofi': epiano_lofi,
}


# ---------------------------------------------------------------------------
# drums
# ---------------------------------------------------------------------------

def kick(vel=0.9):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * vel * 0.8


def snare(vel=0.8, brush=False):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = RNG.normal(0, 1, n)
    noise = fft_filter(noise, lo=1200 if not brush else 2500, hi=9000)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    out = (noise * np.exp(-t * (18 if not brush else 10)) * (0.5 if not brush else 0.25)) + tone * (0.4 if not brush else 0.1)
    return out * vel * 0.6


def hat(vel=0.5, open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    noise = fft_filter(RNG.normal(0, 1, n), lo=7000, hi=15000)
    return noise * np.exp(-t * (12 if open_ else 60)) * vel * 0.35


def shaker(vel=0.4):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    noise = fft_filter(RNG.normal(0, 1, n), lo=4500, hi=11000)
    e = np.minimum(t * 60, 1) * np.exp(-t * 35)
    return noise * e * vel * 0.4


def clap(vel=0.7):
    n = int(0.25 * SR)
    out = np.zeros(n)
    for k, off in enumerate((0, 0.008, 0.017, 0.028)):
        s = int(off * SR)
        m = n - s
        tt = np.arange(m) / SR
        out[s:] += RNG.normal(0, 1, m) * np.exp(-tt * (60 if k < 3 else 14))
    return fft_filter(out, lo=800, hi=6000) * vel * 0.4


DRUMS = {'K': kick, 'S': snare, 'B': lambda v=0.8: snare(v, True), 'H': hat, 'O': lambda v=0.5: hat(v, True),
         'Z': shaker, 'C': clap}


# ---------------------------------------------------------------------------
# reverb & mixing
# ---------------------------------------------------------------------------

def make_ir(seconds=2.2, decay=3.2, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    irs = []
    for ch in range(2):
        noise = r.normal(0, 1, n) * np.exp(-t * decay)
        noise = fft_filter(noise, hi=6000)
        noise[:int(0.01 * SR)] = 0
        irs.append(noise / np.sqrt(np.sum(noise ** 2)))
    return irs


def convolve(x, ir):
    n = len(x) + len(ir) - 1
    size = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)
    return y[:n]


class Mix:
    def __init__(self, seconds):
        self.n = int(seconds * SR)
        self.dry = np.zeros((2, self.n))
        self.send = np.zeros(self.n)

    def add(self, sig, t0, pan=0.0, gain=1.0, rev=0.25):
        s = int(t0 * SR)
        if s >= self.n:
            return
        e = min(self.n, s + len(sig))
        seg = sig[:e - s] * gain
        l = math.cos((pan + 1) * math.pi / 4)
        r = math.sin((pan + 1) * math.pi / 4)
        self.dry[0, s:e] += seg * l
        self.dry[1, s:e] += seg * r
        self.send[s:e] += seg * rev

    def render(self, reverb_seconds=2.2, wet=1.0, loop_len=None, master=0.89):
        irs = make_ir(reverb_seconds)
        out = self.dry.copy()
        for ch in range(2):
            w = convolve(self.send, irs[ch])[:self.n] * wet
            out[ch] += w
        if loop_len is not None:
            # take the second pass of a doubled render so the loop point is seamless
            L = int(loop_len * SR)
            out = out[:, L:2 * L]
        peak = np.max(np.abs(out)) + 1e-9
        out = out / peak * master
        out = np.tanh(out * 1.1) / np.tanh(1.1)
        return out


# ---------------------------------------------------------------------------
# jianpu sequencer
# ---------------------------------------------------------------------------
# A melody string looks like:  "3:1.5 5:.5 6 5 | 3 2 1:2"
#   degree 1-7 (0 = rest), suffix ' = up an octave, , = down, # / b prefix,
#   ':dur' in beats (default 1).  '|' is ignored (bar marker for readability).
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def parse(melody, key_midi=60):
    notes = []
    beat = 0.0
    for tok in melody.split():
        if tok == '|':
            continue
        dur = 1.0
        if ':' in tok:
            tok, d = tok.split(':')
            dur = float(d)
        acc = 0
        while tok and tok[0] in '#b':
            acc += 1 if tok[0] == '#' else -1
            tok = tok[1:]
        octv = tok.count("'") - tok.count(',')
        deg = int(tok.strip("',"))
        if deg > 0:
            m = key_midi + MAJOR[deg - 1] + acc + 12 * octv
            notes.append((beat, dur, m))
        beat += dur
    return notes, beat


CHORDS = {
    'C': [0, 4, 7], 'Dm': [2, 5, 9], 'Em': [4, 7, 11], 'F': [5, 9, 12], 'G': [7, 11, 14],
    'Am': [9, 12, 16], 'Bb': [10, 14, 17], 'E': [4, 8, 11], 'D': [2, 6, 9], 'A': [9, 13, 16],
    'Fm': [5, 8, 12], 'G7': [7, 11, 14, 17], 'Cmaj7': [0, 4, 7, 11], 'Fmaj7': [5, 9, 12, 16],
    'Am7': [9, 12, 16, 19], 'Dm7': [2, 5, 9, 12], 'Em7': [4, 7, 11, 14], 'Gsus': [7, 12, 14],
}


def chord_notes(name, key_midi=60, octave=-1):
    return [key_midi + 12 * octave + i for i in CHORDS[name]]
