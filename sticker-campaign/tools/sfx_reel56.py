"""Reel 56 score: gallery-lounge strings and harp, turntable whirs, spotlight 'shing' glints, soft chimes.

usage: python3 sfx_reel56.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel17 import pluck
from sfx_reel22 import pad

CH = [[146.8, 220.0, 293.7, 349.2], [116.5, 233.1, 293.7, 349.2], [130.8, 196.0, 261.6, 329.6], [110.0, 220.0, 277.2, 329.6]]


def lounge(d, bpm=76):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 4) % 4; s = int(i * b * SR)
        if i % 4 == 0:
            z = 0.08 * lowpass(pad(CH[bar], 4 * b + 0.5), 1400); out[s:s + len(z)] += z[:len(out) - s]
        for j, f in enumerate(CH[bar][1:]):
            x = 0.12 * pluck(f * 2, 0.9, 0.996); q = s + int(j * 0.09 * SR); out[q:q + len(x)] += x[:len(out) - q]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 1.4)


def whir(d=1.0):
    n = int(d * SR); x = np.linspace(0, 1, n)
    return 0.5 * lowpass(whoosh(d), 1800) + 0.15 * np.sin(2 * np.pi * (90 + 60 * x) * np.arange(n) / SR) * np.sin(np.pi * x)


def shing():
    return mix((0, 0.5 * sparkle(0.5)), (0.02, 0.4 * chime(0.7)))


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * lounge(dur)), (0, whir(1.6)), (T['h2'], 0.4 * shing())]
    parts += [(T[k] - 0.45, 0.7 * whir(0.4)) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.1, shing()) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1], whir(1.4)), (T['n2'], 0.4 * shing())]
    parts += [(a, 0.5 * lowpass(whoosh(0.45), 3000)) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)] + [(a + 0.35, 0.4 * shing()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)]
    parts += [(cut[3] + 0.1, 0.4 * shing()), (cut[4] + 0.25, shing()), (T['store2'], 0.6 * chime(1.6))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
