"""Score for reel 38 (heritage, geometric-pattern motion graphics): qanun-style tremolo plucks in Nahawand
over a darbuka maqsum rhythm, chest creak + sparkle, wind-chime shimmer on lattice wipes, soft wood knocks.

usage: python3 sfx_reel38.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle
from sfx_reel10 import creak
from sfx_reel16 import wood
from sfx_reel17 import pluck

NAH = [293.7, 329.6, 349.2, 392.0, 440.0, 466.2, 554.4, 587.3]   # D nahawand (harmonic minor colour)
MEL = [0, 2, 3, 4, 3, 2, 1, 0, 4, 5, 6, 7, 6, 4, 3, 2]


def qanun(f, d=0.5):
    return mix(*[(i * 0.045, (0.6 - i * 0.12) * pluck(f, 0.6, 0.993)) for i in range(4)])[:int(d * SR)]


def darbuka(kind):
    t = np.arange(int(0.25 * SR)) / SR
    if kind == 'D':
        return np.sin(2 * np.pi * 85 * t * (1 + 0.5 * np.exp(-t * 30))) * np.exp(-t * 12)
    return lowpass(rng.standard_normal(len(t)), 6000) * np.exp(-t * 45) * 0.6 + np.sin(2 * np.pi * 650 * t) * np.exp(-t * 50) * 0.4


def maqsum(d, bpm=100):
    s8 = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2); pat = ['D', 'T', None, 'T', 'D', None, 'T', None]
    for i in range(int(d / s8) + 1):
        s = int(i * s8 * SR); parts = []
        k = pat[i % 8]
        if k: parts.append((0.55 if k == 'D' else 0.35) * darbuka(k))
        if i % 2 == 0: parts.append(0.3 * qanun(NAH[MEL[(i // 2) % 16]]))
        for x in parts:
            out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


def windchime(d=1.0):
    return mix(*[(i * 0.06, 0.25 * np.sin(2 * np.pi * f * np.arange(int(0.8 * SR)) / SR) * np.exp(-np.arange(int(0.8 * SR)) / SR * 5)) for i, f in enumerate([2093, 2349, 2637, 3136, 2794, 2349, 3520])])


D = dict(h1=0.2, h1b=1.0, a0=2.6, a1=4.6, a2=6.6, title=8.4, t2=9.4, u0=11.0, u1=12.3, u2=13.6, print=15.2, brand=17.6, store=18.8, store2=19.4, end_all=22.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.25 for k in ('a0', 'title', 'u0', 'print', 'brand')]
    parts = [(0, 0.45 * maqsum(dur)), (0.15, 0.6 * wood()), (1.0, 0.5 * creak(0.45)), (1.2, 0.6 * sparkle(1.0))]
    parts += [(c - 0.35, 0.45 * windchime()) for c in cuts]
    parts += [(T[k] - 0.15 + j * 0.12, 0.5 * wood()) for k in ('a0', 'a1', 'a2') for j in range(3)]
    parts += [(T['title'], 0.4 * sparkle(0.8))]
    parts += [(a + 0.3, 0.5 * wood()) for a in (cuts[2] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2)]
    parts += [(cuts[3] + 1.0, 0.3 * chime(0.6)), (cuts[4] + 0.3, 0.4 * sparkle(0.8)), (T['store2'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
