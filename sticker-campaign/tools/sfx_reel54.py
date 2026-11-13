"""Reel 54 score: spring garden waltz on glockenspiel and plucked strings, sprout 'bloop' rises, soil thuds, bird chirps and leaf rustles.

usage: python3 sfx_reel54.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle
from sfx_reel10 import rustle
from sfx_reel17 import pluck
from sfx_reel22 import pad

CH = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
MEL = [784.0, 659.3, 784.0, 880.0, 784.0, 659.3, 587.3, 659.3, 523.3, 587.3, 659.3, 587.3]


def glock(f, d=0.9):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 12)) * np.exp(-t * 4) * np.minimum(1, t / 0.002)


def spring(d, bpm=120):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 2)
    for i in range(int(d / b) + 1):
        bar = (i // 3) % 4; s = int(i * b * SR)
        x = 0.28 * pluck(CH[bar][0] / 2 if i % 3 == 0 else CH[bar][i % 3], 0.8, 0.995); out[s:s + len(x)] += x[:len(out) - s]
        g = 0.12 * glock(MEL[i % 12]); out[s:s + len(g)] += g[:len(out) - s]
        if i % 3 == 0:
            z = 0.04 * lowpass(pad(CH[bar], 3 * b + 0.2), 1200); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


def sprout(d=0.35, f0=300, f1=900):
    t = np.arange(int(d * SR)) / SR; f = f0 + (f1 - f0) * (t / d) ** 0.6
    return 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)


def bloom():
    return mix((0, 0.5 * glock(1318.5, 0.6)), (0.05, 0.3 * sparkle(0.4)))


def thud(d=0.25):
    t = np.arange(int(d * SR)) / SR
    return 0.7 * np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 16) + 0.3 * lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 20)


def chirp(f=3200):
    d = 0.09; t = np.arange(int(d * SR)) / SR
    one = np.sin(2 * np.pi * (f + 1200 * np.sin(np.pi * t / d)) * t) * np.sin(np.pi * t / d) * 0.25
    return mix((0, one), (0.12, one), (0.3, 0.8 * one))


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * spring(dur)), (0.6, thud()), (0.2, 0.3 * chirp())] + [(T['h2'] - 0.6 + i * 0.15, sprout()) for i in range(3)] + [(T['h2'] - 0.2 + i * 0.15, bloom()) for i in range(3)]
    parts += [(c - 0.1, 0.5 * rustle(0.6)) for c in cut]
    parts += [(T[k] - 0.5, sprout(0.45, 250, 800)) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.1, bloom()) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1] + 0.1 + i * 0.05, 0.25 * sprout(0.2, 400 + 30 * i, 1100)) for i in range(20)] + [(T['n2'], 0.3 * chirp(3600))]
    for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3):
        parts += [(a + 0.05, 0.6 * thud()), (a + 0.25, sprout()), (a + 0.6, bloom())]
    parts += [(cut[3] + 0.3, 0.5 * thud()), (cut[3] + 0.6, sprout()), (T['print2'], 0.3 * chirp())]
    parts += [(cut[4] + 0.3, 0.6 * thud()), (cut[4] + 0.6, sprout()), (cut[4] + 1.0, bloom()), (T['store2'], 0.5 * chime(1.4)), (T['store2'] + 0.4, 0.3 * chirp(3400))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
