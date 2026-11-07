"""Score for reel 24 (colour vases): kalimba bossa bed, colour swooshes, tile flips, spotlight, snips.

usage: python3 sfx_reel24.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel8 import clunk
from sfx_reel17 import pluck
from sfx_reel20 import kick, hat

PENTA = [392.0, 440.0, 523.3, 587.3, 659.3, 784.0, 880.0]


def kalimba(f, d=0.9):
    t = np.arange(int(d * SR)) / SR
    y = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 30)
    return y * np.exp(-t * 5) * np.minimum(1, t * 600)


def swoosh_col(up=True, d=0.45):
    t = np.arange(int(d * SR)) / SR
    f = (300 + 1500 * (t / d)) if up else (1800 - 1500 * (t / d))
    tone = 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)
    return tone + 0.6 * whoosh(d)[:len(t)]


def flip():
    t = np.arange(int(0.07 * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 4000) * np.exp(-t * 80) * 0.6 + np.sin(2 * np.pi * 1400 * t) * np.exp(-t * 90) * 0.3


def snip():
    t = np.arange(int(0.09 * SR)) / SR
    return (rng.standard_normal(len(t)) * np.exp(-t * 70)) * 0.5 + np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 120) * 0.4


def bossa(d, bpm=104):
    beat = 60 / bpm; n = int(d / beat * 2); out = np.zeros(int(d * SR) + SR)
    mel = [0, 2, 4, 2, 5, 4, 2, 1, 0, 2, 4, 6, 5, 4, 2, 0]
    for i in range(n):
        s = int(i * beat / 2 * SR)
        if i % 4 in (0, 3):
            x = 0.5 * kick(0.25); out[s:s + len(x)] += x[:len(out) - s]
        if i % 2 == 1:
            x = 0.25 * hat(0.05); out[s:s + len(x)] += x[:len(out) - s]
        if i % 2 == 0:
            x = 0.4 * kalimba(PENTA[mel[(i // 2) % 16]]); out[s:s + len(x)] += x[:len(out) - s]
        if i % 8 == 0:
            x = 0.35 * pluck(PENTA[0] / 4 * (1 if (i // 8) % 2 == 0 else 1.335), 1.5); out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.2)


D = dict(h1=0.2, h2=1.0, c0=3.2, c1=4.9, c2=6.6, count=8.6, art=12.6, u0=15.6, u1=17.1, u2=18.6, print=20.2, brand=23.2, store=24.6, end_all=27.5)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.2 for k in ('c0', 'count', 'art', 'u0', 'print', 'brand')]
    parts = [(0, 0.45 * bossa(dur))]
    parts += [(T['h1'], 0.6 * kalimba(784)), (T['h2'], 0.6 * kalimba(880))]
    parts += [(c - 0.45, 0.8 * swoosh_col(i % 2 == 0)) for i, c in enumerate(cuts)]
    parts += [(a + 0.3, 0.5 * kalimba(f)) for a, f in ((cuts[0], 523.3), (T['c1'] - 0.25, 659.3), (T['c2'] - 0.25, 784.0))]
    parts += [(cuts[1] + 0.15 + (i % 4 + i // 4) * 0.09 + 0.3, 0.5 * flip()) for i in range(16)]
    parts += [(cuts[1] + 1.25, 0.6 * sparkle(0.6))]
    parts += [(cuts[2] + 0.25, 1.0 * clunk())]
    parts += [(a + 0.7, 0.6 * kick(0.2)) for a in (cuts[3] + 0.1, T['u1'] - 0.25, T['u2'] - 0.25)]
    parts += [(cuts[4] + 1.2 + i * 0.25, 0.6 * snip()) for i in range(5)]
    parts += [(cuts[5] + 0.2 + i * 0.05, 0.3 * kalimba(PENTA[i % 7] * 2, 0.4)) for i in range(11)]
    parts += [(T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
