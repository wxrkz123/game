"""Compose and render all music & sound for 《余音》.

    python3 tools/audio/build_audio.py            # everything
    python3 tools/audio/build_audio.py bgm se     # only some groups

The heart of the soundtrack is one leitmotif — 《余音》 — in four phrases,
one for each stage of 林音's life.  Each chapter re-arranges it.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from synth import (SR, INSTRUMENTS, DRUMS, Mix, parse, chord_notes, midi_freq, fft_filter,
                   make_ir, convolve, musicbox, bell, marimba, piano, harmonica, nylon, recorder,
                   pluck, kick, snare, clap, RNG)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'YuYin', 'audio'))

# ---------------------------------------------------------------------------
# The leitmotif (jianpu, 1 = C)
# ---------------------------------------------------------------------------
P1 = "3:1.5 5:.5 6 5 | 3 2 1:2"            # 蝉鸣  childhood
P2 = "2:1.5 3:.5 5 6 | 5 3 2:2"            # 逆风  youth
P3 = "6:1.5 1':.5 6 5 | 3 5 6:2"           # 霓虹  young adult
P4 = "5:1.5 3:.5 2 1 | 2 3 1:2"            # 心跳  middle age
CODA = "1':1.5 6:.5 5 3 | 5:4 | 2:1.5 3:.5 2 1 | 1:4"   # 余音  the ending
THEME = ' '.join([P1, P2, P3, P4])
THEME_CHORDS = ['C', 'Am', 'F', 'G', 'Am', 'F', 'G', 'C']
CODA_CHORDS = ['F', 'C', 'G', 'C']

# the short phrases the player learns in the echo mini-game (1..8 = C4..C5)
GAME_PHRASES = {
    'warmup': [1, 2, 3],
    'p1': [3, 5, 6, 5, 3, 2, 1],
    'p2': [2, 3, 5, 6, 5, 3, 2],
    'p3': [6, 8, 6, 5, 3, 5, 6],
    'p4': [5, 3, 2, 1, 2, 3, 1],
}


class Song:
    def __init__(self, bpm, beats_per_bar=4):
        self.bpm = bpm
        self.bpb = beats_per_bar
        self.ev = []      # (beat, dur, midi, inst, vel, pan, gain, rev)
        self.hits = []    # (beat, drum, vel, pan, gain, rev)

    def sec(self, beat):
        return beat * 60.0 / self.bpm

    def melody(self, inst, text, start_bar=0, key=60, octave=0, vel=0.8, pan=0.0, gain=1.0, rev=0.3,
               legato=1.0):
        notes, length = parse(text, key + 12 * octave)
        b0 = start_bar * self.bpb
        for (b, d, m) in notes:
            self.ev.append((b0 + b, d * legato, m, inst, vel, pan, gain, rev))
        return length / self.bpb

    def chords(self, inst, names, start_bar=0, key=60, octave=-1, vel=0.5, pan=0.0, gain=1.0, rev=0.4,
               beats=None):
        for i, c in enumerate(names):
            if c is None:
                continue
            for m in chord_notes(c, key, octave):
                self.ev.append(((start_bar + i) * self.bpb, beats or self.bpb, m, inst, vel, pan, gain, rev))

    def arp(self, inst, names, pattern, start_bar=0, key=60, octave=-1, step=0.5, vel=0.55, pan=0.0,
            gain=1.0, rev=0.35, hold=1.0):
        """pattern: list of chord-tone indexes (0,1,2,3=root+octave...) per step; None = rest."""
        steps = int(self.bpb / step)
        for i, c in enumerate(names):
            if c is None:
                continue
            tones = chord_notes(c, key, octave)
            tones = tones + [t + 12 for t in tones]
            for s in range(steps):
                idx = pattern[s % len(pattern)]
                if idx is None:
                    continue
                m = tones[idx % len(tones)]
                b = (start_bar + i) * self.bpb + s * step
                self.ev.append((b, step * hold, m, inst, vel * (1.0 if s % 2 == 0 else 0.85), pan, gain, rev))

    def bassline(self, names, pattern, start_bar=0, key=60, vel=0.8, gain=1.0, rev=0.1, inst='bass'):
        """pattern: list of (beat, dur, offset) where offset 0 = root, 7 = fifth, 12 = octave"""
        for i, c in enumerate(names):
            if c is None:
                continue
            root = chord_notes(c, key, -2)[0]
            for (b, d, off) in pattern:
                self.ev.append(((start_bar + i) * self.bpb + b, d, root + off, inst, vel, 0.0, gain, rev))

    def drums(self, pattern, bars, start_bar=0, step=0.5, vel=0.8, gain=1.0, rev=0.12):
        """pattern: string per bar, one char per step; '.' rest, letters see synth.DRUMS.
        Several voices can be stacked with '+', e.g. 'K+H'."""
        tokens = pattern.split()
        for bar in range(bars):
            for s, tok in enumerate(tokens):
                if tok == '.':
                    continue
                for ch in tok.split('+'):
                    b = (start_bar + bar) * self.bpb + s * step
                    v = vel * (0.7 if ch in 'HZ' and s % 2 else 1.0)
                    pan = {'H': 0.3, 'O': 0.3, 'Z': -0.3}.get(ch, 0.0)
                    self.hits.append((b, ch, v, pan, gain, rev))

    def render(self, total_bars, loop=True, tail=3.0, reverb=2.2, wet=1.0):
        L = self.sec(total_bars * self.bpb)
        passes = 2 if loop else 1
        mix = Mix(L * passes + tail)
        cache = {}
        for p in range(passes):
            off = p * total_bars * self.bpb
            for (b, d, m, inst, vel, pan, gain, rev) in self.ev:
                key_ = (inst, round(self.sec(d), 3), m, round(vel, 2))
                if key_ not in cache:
                    cache[key_] = INSTRUMENTS[inst](midi_freq(m), self.sec(d), vel)
                mix.add(cache[key_], self.sec(b + off), pan, gain, rev)
            for (b, ch, v, pan, gain, rev) in self.hits:
                mix.add(DRUMS[ch](v), self.sec(b + off), pan, gain, rev)
        return mix.render(reverb, wet, loop_len=L if loop else None)


# ---------------------------------------------------------------------------
# BGM
# ---------------------------------------------------------------------------

def bgm_title():
    s = Song(70)
    s.melody('musicbox', THEME, 0, octave=1, vel=0.7, gain=1.0, rev=0.5)
    s.melody('musicbox', CODA, 8, octave=1, vel=0.7, rev=0.5)
    ch = THEME_CHORDS + CODA_CHORDS
    s.arp('piano', ch, [0, 2, 1, 2, 3, 2, 1, 2], octave=-1, vel=0.35, gain=0.8, rev=0.5)
    s.chords('pad', ch, octave=-1, vel=0.5, gain=0.9, rev=0.6)
    return s.render(12)


def bgm_summer():
    s = Song(100)
    mel = ("3:.5 5:.5 6 5 3:.5 2:.5 | 1 2 3:2 | 2:.5 3:.5 5 6 5:.5 3:.5 | 2 3 2:2 | "
           "6:.5 1':.5 6 5 3:.5 5:.5 | 6 5 3:2 | 5:.5 3:.5 2 1 2:.5 3:.5 | 1:4")
    s.melody('marimba', mel, 0, octave=1, vel=0.75, pan=-0.1, rev=0.25)
    s.melody('marimba', mel, 8, octave=1, vel=0.75, pan=-0.1, rev=0.25)
    s.melody('recorder', "0:4 | 0:4 | 0:4 | 0:4 | 3:2 5:2 | 6:4 | 5:2 2:2 | 1:4", 8, octave=1, vel=0.5,
             pan=0.3, gain=0.8, rev=0.35)
    ch = ['C', 'Am', 'F', 'G', 'Am', 'F', 'G', 'C'] * 2
    s.arp('nylon', ch, [0, 2, 1, 2, 3, 2, 1, 2], octave=-1, vel=0.55, pan=0.25, rev=0.25)
    s.bassline(ch, [(0, 1.5, 0), (1.5, .5, 7), (2, 2, 12)], vel=0.6, gain=0.8)
    s.drums("Z Z Z Z Z Z Z Z", 16, vel=0.5, gain=0.7)
    s.drums("K . . . K . . .", 16, vel=0.6, gain=0.6)
    return s.render(16)


def bgm_harmonica():
    s = Song(72)
    s.melody('harmonica', THEME, 0, vel=0.85, rev=0.4, legato=0.97)
    s.arp('nylon', THEME_CHORDS, [0, 2, 3, 2], step=1.0, octave=-1, vel=0.5, pan=0.2, rev=0.35)
    return s.render(8)


def bgm_home():
    s = Song(84)
    mel = (P2 + ' | ' + P3 + ' | ' + "5:1.5 3:.5 2 1 | 6,:1 1:1 2:2 | " + P1 + ' | ' + P4)
    s.melody('piano', mel, 0, octave=1, vel=0.6, rev=0.35)
    ch = ['F', 'G', 'Am', 'F', 'Dm', 'G', 'C', 'Am', 'F', 'G', 'C', 'C']
    s.arp('piano', ch, [0, 1, 2, 1, 3, 1, 2, 1], octave=-1, vel=0.32, gain=0.85, rev=0.4)
    s.bassline(ch, [(0, 4, 0)], vel=0.4, gain=0.6, inst='piano')
    return s.render(12)


def bgm_band():
    s = Song(112)
    ch = ['C', 'G', 'Am', 'F'] + THEME_CHORDS + CODA_CHORDS
    # intro riff then theme sung by a bright lead guitar
    s.melody('guitar', "5:.5 5:.5 6 5:.5 3:.5 2 | 5:.5 5:.5 6 1':2 | 6:.5 6:.5 5 3:.5 2:.5 1 | 2 3 5:2", 0,
             octave=0, vel=0.7, pan=-0.2)
    s.melody('guitar', THEME, 4, octave=1, vel=0.9, pan=-0.15, gain=1.1, rev=0.25)
    s.melody('guitar', CODA, 12, octave=1, vel=0.9, pan=-0.15, gain=1.1, rev=0.3)
    s.arp('guitar', ch, [0, 1, 2, 1], step=0.5, octave=-1, vel=0.55, pan=0.35, gain=0.8, rev=0.2)
    s.chords('pad', ch, octave=0, vel=0.4, gain=0.7)
    s.bassline(ch, [(0, .5, 0), (.5, .5, 0), (1, .5, 12), (1.5, .5, 0), (2, .5, 0), (2.5, .5, 7),
                    (3, .5, 12), (3.5, .5, 7)], vel=0.75)
    s.drums("K+H H S+H H K+H K+H S+H H", 16, vel=0.75, gain=0.9)
    s.drums(". . . . . . . O", 16, start_bar=0, vel=0.4, gain=0.6)
    return s.render(16)


def bgm_neon():
    s = Song(76)
    mel = ("0:1 3:.5 2:.5 3 5 | 6:1.5 5:.5 3:2 | 0:1 2:.5 1:.5 2 3 | 5:1.5 3:.5 2:2 | "
           "0:1 3:.5 2:.5 1 6, | 1:1.5 2:.5 3:2 | 2:1 1:.5 6,:.5 6,:1 5,:1 | 6,:4")
    s.melody('lofi', mel, 0, octave=1, vel=0.65, pan=-0.1, rev=0.4)
    s.melody('lofi', mel, 8, octave=1, vel=0.65, pan=-0.1, rev=0.4)
    ch = ['Am7', 'Fmaj7', 'Cmaj7', 'G', 'Am7', 'Fmaj7', 'Dm7', 'Em7'] * 2
    s.chords('lofi', ch, octave=-1, vel=0.4, gain=0.7, rev=0.4, beats=3.5)
    s.bassline(ch, [(0, 1.5, 0), (2.5, 1.5, 7)], vel=0.55, gain=0.8)
    s.drums("K . B . . K B .", 16, vel=0.6, gain=0.75)
    s.drums("H H H H H H H H", 16, vel=0.3, gain=0.5)
    out = s.render(16)
    # vinyl crackle
    n = out.shape[1]
    crack = np.zeros(n)
    idx = RNG.integers(0, n, n // 3000)
    crack[idx] = RNG.uniform(-0.3, 0.3, len(idx))
    crack = fft_filter(crack, lo=800, hi=6000)
    out += crack * 0.25
    return out


def bgm_tension():
    s = Song(60)
    s.melody('piano', "0:2 3:1 2:1 | 1:4 | 0:2 6,:1 7,:1 | #5,:4 | 0:2 3:1 2:1 | 1:2 7,:2 | 6,:4 | 0:4", 0,
             vel=0.55, rev=0.5)
    ch = ['Am', 'F', 'Dm', 'E', 'Am', 'F', 'E', 'Am']
    s.chords('piano', ch, octave=-2, vel=0.4, gain=0.9, rev=0.55)
    s.chords('strings', ch, octave=-1, vel=0.5, gain=0.8, rev=0.6)
    return s.render(8)


def bgm_silence():
    s = Song(56)
    s.melody('piano', "6,:4 | 0:4 | 3:4 | 0:4 | 2:4 | 0:4 | 1:2 7,:2 | 6,:4", 0, vel=0.45, rev=0.7)
    s.chords('pad', ['Am', 'Am', 'F', 'F', 'Dm', 'Dm', 'E', 'Am'], octave=-2, vel=0.6, gain=1.0, rev=0.7)
    out = s.render(8, reverb=3.0)
    # everything muffled, as if heard through water
    for ch in range(2):
        out[ch] = fft_filter(out[ch], hi=700)
    out /= np.max(np.abs(out)) + 1e-9
    return out * 0.8


def bgm_spring():
    s = Song(80)
    s.melody('harmonica', P4 + ' | ' + P1 + ' | ' + P2 + ' | ' + P3, 0, vel=0.85, rev=0.35)
    s.melody('harmonica', CODA, 8, vel=0.85, rev=0.4)
    s.melody('recorder', "0:4 | 0:4 | 1':2 7:2 | 6:4 | 0:4 | 0:4 | 3':2 2':2 | 1':4 | 3':4 | 3':4 | 2':4 | 1':4",
             0, vel=0.45, pan=0.35, gain=0.7, rev=0.4)
    ch = ['G', 'C', 'C', 'Am', 'F', 'G', 'Am', 'F'] + CODA_CHORDS
    s.arp('piano', ch, [0, 2, 1, 2, 3, 2, 1, 2], octave=-1, vel=0.35, pan=-0.2, rev=0.4)
    s.bassline(ch, [(0, 2, 0), (2, 2, 7)], vel=0.4, gain=0.6, inst='nylon')
    return s.render(12)


def bgm_twilight():
    s = Song(66)
    s.melody('piano', THEME, 0, octave=1, vel=0.55, rev=0.45)
    s.arp('piano', THEME_CHORDS, [0, 2, 3, 2], step=1.0, octave=-1, vel=0.3, gain=0.8, rev=0.5)
    s.chords('strings', THEME_CHORDS, octave=-1, vel=0.45, gain=0.7, rev=0.6)
    return s.render(8)


def bgm_finale():
    s = Song(76)
    # A: old 林音 alone at the piano
    s.melody('piano', THEME, 0, octave=1, vel=0.6, rev=0.45)
    s.arp('piano', THEME_CHORDS, [0, 2, 3, 2], step=1.0, octave=-1, vel=0.32, gain=0.85, rev=0.45)
    # B: grandpa's harmonica joins, with guitar and strings (her whole life joining in)
    s.melody('harmonica', THEME, 8, vel=0.9, rev=0.35, legato=0.97)
    s.arp('nylon', THEME_CHORDS, [0, 2, 1, 2, 3, 2, 1, 2], start_bar=8, octave=-1, vel=0.5, pan=0.25)
    s.chords('strings', THEME_CHORDS, start_bar=8, octave=-1, vel=0.45, gain=0.8, rev=0.55)
    s.bassline(THEME_CHORDS, [(0, 2, 0), (2, 2, 7)], start_bar=8, vel=0.5, gain=0.7)
    # C: lift to D major, everyone plays
    key = 62
    s.melody('strings', THEME, 16, key=key, octave=1, vel=0.8, gain=1.6, rev=0.5)
    s.melody('piano', THEME, 16, key=key, octave=1, vel=0.6, rev=0.4)
    s.melody('harmonica', THEME, 16, key=key, vel=0.6, gain=0.7, rev=0.35)
    s.arp('nylon', THEME_CHORDS, [0, 2, 1, 2, 3, 2, 1, 2], start_bar=16, key=key, octave=-1, vel=0.5,
          pan=0.25)
    s.chords('strings', THEME_CHORDS, start_bar=16, key=key, octave=-1, vel=0.5, gain=0.9, rev=0.55)
    s.bassline(THEME_CHORDS, [(0, 1.5, 0), (1.5, .5, 7), (2, 2, 12)], start_bar=16, key=key, vel=0.6)
    s.drums("K . Z . B . Z .", 8, start_bar=16, vel=0.5, gain=0.6)
    # coda and the last long chord
    s.melody('piano', CODA, 24, key=key, octave=1, vel=0.65, rev=0.5)
    s.melody('harmonica', CODA, 24, key=key, vel=0.7, gain=0.8, rev=0.45)
    s.chords('strings', CODA_CHORDS + ['C'], start_bar=24, key=key, octave=-1, vel=0.5, gain=0.9, rev=0.6)
    s.arp('piano', CODA_CHORDS, [0, 2, 3, 2], step=1.0, start_bar=24, key=key, octave=-1, vel=0.3, rev=0.5)
    s.chords('piano', ['C'], start_bar=28, key=key, octave=0, vel=0.5, rev=0.6)
    return s.render(30, loop=False, tail=4.0, reverb=2.8)


BGM = {
    'YY_Title': bgm_title, 'YY_Summer': bgm_summer, 'YY_Harmonica': bgm_harmonica, 'YY_Home': bgm_home,
    'YY_Band': bgm_band, 'YY_Neon': bgm_neon, 'YY_Tension': bgm_tension, 'YY_Silence': bgm_silence,
    'YY_Spring': bgm_spring, 'YY_Twilight': bgm_twilight, 'YY_Finale': bgm_finale,
}


# ---------------------------------------------------------------------------
# ME (short jingles)
# ---------------------------------------------------------------------------

def me_fragment():
    s = Song(120)
    s.melody('musicbox', "1:.5 3:.5 5:.5 1':.5 3':2", 0, octave=1, vel=0.8, rev=0.6)
    s.melody('bell', "0:2 1':2", 0, octave=1, vel=0.4, gain=0.6, rev=0.7)
    s.chords('pad', ['C'], octave=0, vel=0.5, beats=3)
    return s.render(1, loop=False, tail=2.5)


def me_chapter():
    s = Song(76)
    s.melody('harmonica', "3:1.5 5:.5 6:2", 0, vel=0.85, rev=0.5)
    s.arp('nylon', ['F'], [0, 1, 2, 3], step=1.0, octave=-1, vel=0.45)
    return s.render(1, loop=False, tail=2.5)


def me_memory():
    s = Song(90)
    s.melody('bell', "1'':.5 5':.5 3':.5 1':2.5", 0, vel=0.6, rev=0.8)
    s.chords('pad', ['Fmaj7'], octave=0, vel=0.5, beats=4)
    return s.render(1, loop=False, tail=3.0, reverb=3.0)


def me_end():
    s = Song(66)
    s.melody('musicbox', "5:1 3:1 2:1 1:4", 0, octave=1, vel=0.7, rev=0.6)
    s.chords('strings', ['C', 'C'], octave=-1, vel=0.4, beats=4)
    return s.render(2, loop=False, tail=3.0)


ME = {'YY_Fragment': me_fragment, 'YY_Chapter': me_chapter, 'YY_Memory': me_memory, 'YY_End': me_end}


# ---------------------------------------------------------------------------
# SE
# ---------------------------------------------------------------------------

def _mono(x, seconds=None):
    if seconds:
        n = int(seconds * SR)
        x = np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n]
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.85
    fade = min(len(x), 2000)
    x[-fade:] *= np.linspace(1, 0, fade)
    return np.vstack([x, x])


def _seq(parts, total):
    out = np.zeros(int(total * SR))
    for (t, sig, g) in parts:
        s = int(t * SR)
        e = min(len(out), s + len(sig))
        out[s:e] += sig[:e - s] * g
    return out


def _small_reverb(x, amount=0.25, seconds=1.0):
    ir = make_ir(seconds, 5.0)[0]
    y = convolve(x, ir)[:len(x)]
    return x + y * amount


def se_note(inst, deg):
    m = 60 + [0, 2, 4, 5, 7, 9, 11, 12][deg - 1]
    fn = {'Harm': harmonica, 'Gtr': nylon, 'Pno': piano, 'Box': musicbox, 'Rec': recorder}[inst]
    dur = {'Harm': 0.55, 'Gtr': 0.6, 'Pno': 0.6, 'Box': 0.4, 'Rec': 0.5}[inst]
    x = fn(midi_freq(m), dur, 0.85)
    x = _small_reverb(np.concatenate([x, np.zeros(int(0.4 * SR))]), 0.2)
    out = _mono(x, 1.4)
    # equal loudness across instruments: RMS of the first 0.5 s -> -15 dBFS
    head = out[0, :int(0.5 * SR)]
    gain = 10 ** (-15 / 20) / (np.sqrt(np.mean(head ** 2)) + 1e-9)
    out = out * gain
    return out / max(1.0, np.max(np.abs(out)) / 0.95)


def se_cursor():
    return _mono(marimba(midi_freq(84), 0.05, 0.6), 0.25)


def se_decision():
    return _mono(_seq([(0, bell(midi_freq(79), 0.1, 0.6), 1), (0.07, bell(midi_freq(84), 0.2, 0.6), 1)], 0.8))


def se_cancel():
    return _mono(_seq([(0, marimba(midi_freq(76), 0.1, 0.6), 1), (0.08, marimba(midi_freq(72), 0.2, 0.6), 1)], 0.6))


def se_buzzer():
    return _mono(_seq([(0, marimba(midi_freq(52), 0.1, 0.7), 1), (0.1, marimba(midi_freq(51), 0.2, 0.7), 1)], 0.6))


def se_save():
    p = [(i * 0.07, musicbox(midi_freq(m), 0.2, 0.7), 1) for i, m in enumerate((72, 76, 79, 84))]
    return _mono(_small_reverb(_seq(p, 1.6), 0.3))


def se_load():
    p = [(i * 0.07, musicbox(midi_freq(m), 0.2, 0.7), 1) for i, m in enumerate((84, 79, 76, 72))]
    return _mono(_small_reverb(_seq(p, 1.6), 0.3))


def se_item():
    p = [(0, bell(midi_freq(84), 0.2, 0.6), 1), (0.09, bell(midi_freq(88), 0.4, 0.6), 1)]
    return _mono(_small_reverb(_seq(p, 1.8), 0.3))


def se_sparkle():
    p = [(i * 0.05, musicbox(midi_freq(m), 0.15, 0.6), 1) for i, m in enumerate((79, 84, 88, 91, 96))]
    return _mono(_small_reverb(_seq(p, 1.8), 0.4))


def se_door():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 18)
    creak = fft_filter(RNG.normal(0, 1, n), lo=500, hi=1800) * np.exp(-((t - 0.25) / 0.12) ** 2) * 0.25
    return _mono(thud + creak, 0.7)


def se_knock():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    k = (np.sin(2 * np.pi * 180 * t) + fft_filter(RNG.normal(0, 0.6, n), lo=300, hi=2000)) * np.exp(-t * 40)
    return _mono(_seq([(0, k, 1), (0.18, k, 0.9), (0.36, k, 0.8)], 0.7))


def se_paper():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = fft_filter(RNG.normal(0, 1, n), lo=1500, hi=8000)
    x *= (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t)) * np.exp(-((t - 0.2) / 0.15) ** 2)
    return _mono(x, 0.5)


def se_phone():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    parts = []
    for burst in range(2):
        for k in range(12):
            f = 1000 if k % 2 == 0 else 1250
            tone = np.sin(2 * np.pi * f * t) * 0.6
            parts.append((burst * 1.2 + k * 0.05, tone, 1))
    return _mono(_seq(parts, 2.2))


def se_applause():
    parts = []
    for _ in range(260):
        t0 = RNG.uniform(0, 3.2)
        g = min(1.0, t0 * 2) * (1 if t0 < 2.4 else max(0.0, 1 - (t0 - 2.4) / 0.8))
        parts.append((t0, clap(RNG.uniform(0.4, 0.9)), g))
    x = _seq(parts, 3.6)
    return _mono(_small_reverb(x, 0.4))


def se_heartbeat():
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    b = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 22)
    return _mono(_seq([(0, b, 1), (0.22, b, 0.7)], 0.9))


def se_windchime():
    parts = []
    for i in range(7):
        m = RNG.choice([84, 86, 88, 91, 93, 96])
        parts.append((RNG.uniform(0, 1.0), bell(midi_freq(m), 0.3, 0.5), 1))
    return _mono(_small_reverb(_seq(parts, 2.6), 0.3))


def se_bicycle_bell():
    parts = []
    for i in range(3):
        parts.append((i * 0.14, bell(midi_freq(93), 0.1, 0.6), 1))
    return _mono(_seq(parts, 1.4))


def se_cicada():
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    noise = fft_filter(RNG.normal(0, 1, n), lo=3800, hi=7000)
    am = (0.5 + 0.5 * np.sin(2 * np.pi * 42 * t)) ** 3
    swell = np.minimum(t / 0.4, 1) * np.minimum((2.5 - t) / 0.6, 1)
    return _mono(noise * am * swell, 2.5)


def se_stream():
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    x = fft_filter(RNG.normal(0, 1, n), lo=200, hi=2500) * 0.6
    for _ in range(25):
        t0 = RNG.uniform(0, 2.3)
        f0 = RNG.uniform(500, 1400)
        m = int(0.06 * SR)
        tt = np.arange(m) / SR
        blip = np.sin(2 * np.pi * (f0 + 3000 * tt) * tt) * np.exp(-tt * 50)
        s = int(t0 * SR)
        x[s:s + m] += blip[:len(x[s:s + m])] * 0.6
    x *= np.minimum(t / 0.3, 1) * np.minimum((2.5 - t) / 0.5, 1)
    return _mono(x, 2.5)


def se_step():
    n = int(0.1 * SR)
    t = np.arange(n) / SR
    x = fft_filter(RNG.normal(0, 1, n), lo=100, hi=900) * np.exp(-t * 50)
    return _mono(x, 0.15) * 0.6


def se_coin():
    return _mono(_seq([(0, bell(midi_freq(96), 0.08, 0.5), 1), (0.06, bell(midi_freq(100), 0.2, 0.5), 1)], 1.0))


def se_splash():
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    x = fft_filter(RNG.normal(0, 1, n), lo=400, hi=5000) * np.exp(-t * 7)
    return _mono(x, 0.8)


def se_whoosh():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = fft_filter(RNG.normal(0, 1, n), lo=300, hi=3000) * np.sin(np.pi * t / 0.9) ** 2
    return _mono(x, 0.9)


def se_tinnitus():
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 5200 * t) * 0.15 + fft_filter(RNG.normal(0, 1, n), hi=200) * 0.4
    x *= np.minimum(t / 0.8, 1) * np.minimum((3 - t) / 0.8, 1)
    return _mono(x, 3.0) * 0.5


def se_strum():
    parts = [(i * 0.025, nylon(midi_freq(m), 1.2, 0.7), 1) for i, m in enumerate((48, 55, 60, 64, 67, 72))]
    return _mono(_seq(parts, 2.2))


SE = {
    'YY_Cursor': se_cursor, 'YY_Decision': se_decision, 'YY_Cancel': se_cancel, 'YY_Buzzer': se_buzzer,
    'YY_Save': se_save, 'YY_Load': se_load, 'YY_Item': se_item, 'YY_Sparkle': se_sparkle,
    'YY_Door': se_door, 'YY_Knock': se_knock, 'YY_Paper': se_paper, 'YY_Phone': se_phone,
    'YY_Applause': se_applause, 'YY_Heartbeat': se_heartbeat, 'YY_WindChime': se_windchime,
    'YY_Bell': se_bicycle_bell, 'YY_Cicada': se_cicada, 'YY_Stream': se_stream, 'YY_Step': se_step,
    'YY_Coin': se_coin, 'YY_Splash': se_splash, 'YY_Whoosh': se_whoosh, 'YY_Tinnitus': se_tinnitus,
    'YY_Strum': se_strum,
}
for _inst in ('Harm', 'Gtr', 'Pno', 'Box', 'Rec'):
    for _d in range(1, 9):
        SE['YY_%s_%d' % (_inst, _d)] = (lambda i=_inst, d=_d: se_note(i, d))


# ---------------------------------------------------------------------------
# BGS (ambient loops)
# ---------------------------------------------------------------------------

def _loop_xfade(x, xf=2.0):
    """make a mono signal loop seamlessly by crossfading its tail into its head."""
    n = int(xf * SR)
    head, body, tail = x[:n], x[n:-n] if len(x) > 2 * n else x[n:], x[-n:]
    ramp = np.linspace(0, 1, n)
    blended = tail * (1 - ramp) + head * ramp
    return np.concatenate([blended, body])


def _stereo_loop(make, seconds, xf=2.0):
    chans = []
    for c in range(2):
        chans.append(_loop_xfade(make(seconds + xf, c), xf))
    out = np.vstack(chans)
    return out / (np.max(np.abs(out)) + 1e-9) * 0.7


def bgs_cicada(seconds, c):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(6):
        f = RNG.uniform(3800, 6200)
        noise = fft_filter(RNG.normal(0, 1, n), lo=f - 700, hi=f + 700)
        rate = RNG.uniform(30, 55)
        am = (0.5 + 0.5 * np.sin(2 * np.pi * rate * t + RNG.uniform(0, 6))) ** 3
        swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / RNG.uniform(5, 11) + RNG.uniform(0, 6))
        x += noise * am * swell ** 2
    return x


def bgs_stream(seconds, c):
    n = int(seconds * SR)
    x = fft_filter(RNG.normal(0, 1, n), lo=150, hi=2200) * 0.5
    for _ in range(int(seconds * 9)):
        t0 = RNG.uniform(0, seconds - 0.1)
        f0 = RNG.uniform(400, 1300)
        m = int(0.05 * SR)
        tt = np.arange(m) / SR
        blip = np.sin(2 * np.pi * (f0 + 2500 * tt) * tt) * np.exp(-tt * 60)
        s = int(t0 * SR)
        x[s:s + m] += blip[:len(x[s:s + m])] * 0.35
    return x


def bgs_city(seconds, c):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = fft_filter(RNG.normal(0, 1, n), hi=350) * 1.2
    for _ in range(int(seconds / 4)):
        t0 = RNG.uniform(0, seconds)
        w = RNG.uniform(1.5, 3.0)
        car = fft_filter(RNG.normal(0, 1, n), lo=200, hi=1500) * np.exp(-((t - t0) / w) ** 2)
        x += car * (0.5 if c == 0 else 0.35)
    return x


def bgs_wind(seconds, c):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for (lo, hi) in ((80, 300), (300, 800), (800, 1600)):
        band = fft_filter(RNG.normal(0, 1, n), lo=lo, hi=hi)
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * t / RNG.uniform(4, 9) + RNG.uniform(0, 6))
        x += band * lfo ** 2
    return x


def bgs_crowd(seconds, c):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(10):
        f = RNG.uniform(300, 900)
        band = fft_filter(RNG.normal(0, 1, n), lo=f * 0.7, hi=f * 1.6)
        am = np.clip(np.sin(2 * np.pi * RNG.uniform(2.5, 5) * t + RNG.uniform(0, 6)), 0, 1)
        slow = 0.5 + 0.5 * np.sin(2 * np.pi * t / RNG.uniform(3, 8) + RNG.uniform(0, 6))
        x += band * am * slow
    return x


def bgs_night(seconds, c):
    n = int(seconds * SR)
    x = fft_filter(RNG.normal(0, 1, n), hi=300) * 0.15
    for _ in range(int(seconds * 1.5)):
        t0 = RNG.uniform(0, seconds - 0.5)
        f = RNG.uniform(4200, 4800)
        for k in range(RNG.integers(2, 5)):
            m = int(0.03 * SR)
            tt = np.arange(m) / SR
            chirp = np.sin(2 * np.pi * f * tt) * np.sin(np.pi * tt / 0.03)
            s = int((t0 + k * 0.06) * SR)
            x[s:s + m] += chirp[:len(x[s:s + m])] * 0.3
    return x


def bgs_tinnitus(seconds, c):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 5200 * t) * 0.05 + fft_filter(RNG.normal(0, 1, n), hi=160) * 0.8


BGS = {'YY_Cicadas': (bgs_cicada, 20), 'YY_River': (bgs_stream, 16), 'YY_CityNight': (bgs_city, 24),
       'YY_Wind': (bgs_wind, 20), 'YY_Crowd': (bgs_crowd, 16), 'YY_Night': (bgs_night, 16),
       'YY_Muffled': (bgs_tinnitus, 12)}


# ---------------------------------------------------------------------------
# encoding
# ---------------------------------------------------------------------------

def write(folder, name, stereo, q=4):
    os.makedirs(os.path.join(ROOT, folder), exist_ok=True)
    data = np.clip(stereo.T, -1, 1)
    pcm = (data * 32767).astype('<i2')
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
        wav_path = tf.name
    with wave.open(wav_path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    base = os.path.join(ROOT, folder, name)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav_path, '-c:a', 'libvorbis', '-q:a', str(q),
                    base + '.ogg'], check=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav_path, '-c:a', 'aac', '-b:a',
                    '128k' if folder in ('bgm', 'bgs') else '96k', base + '.m4a'], check=True)
    os.unlink(wav_path)


def main(groups):
    if 'bgm' in groups:
        for name, fn in BGM.items():
            write('bgm', name, fn(), q=4)
            print('bgm', name)
    if 'me' in groups:
        for name, fn in ME.items():
            write('me', name, fn())
            print('me', name)
    if 'se' in groups:
        for name, fn in SE.items():
            write('se', name, fn(), q=3)
        print('se', len(SE))
    if 'bgs' in groups:
        for name, (fn, secs) in BGS.items():
            write('bgs', name, _stereo_loop(fn, secs), q=3)
            print('bgs', name)


if __name__ == '__main__':
    main(sys.argv[1:] or ['bgm', 'me', 'se', 'bgs'])
