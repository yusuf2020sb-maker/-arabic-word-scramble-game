"""Reel 60 score: ASMR sticker peels (sticky tear + paper flutter), tape rips, soft pops, over a dreamy lo-fi journal beat.

usage: python3 sfx_reel60.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng
from sfx_reel20 import hat, kick
from sfx_reel22 import pad, piano

CH = [[174.6, 220.0, 261.6, 329.6], [146.8, 220.0, 261.6, 349.2], [116.5, 174.6, 220.0, 293.7], [130.8, 196.0, 246.9, 329.6]]


def lofi(d, bpm=80):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b * 2) + 1):
        s = int(i * b / 2 * SR); bar = (i // 8) % 4
        if i % 8 == 0:
            z = mix(*[(0.03 * j, 0.08 * lowpass(piano(f, 2.5), 1600)) for j, f in enumerate(CH[bar])], (0, 0.04 * lowpass(pad(CH[bar], 4 * b), 800))); out[s:s + len(z)] += z[:len(out) - s]
        if i % 4 == 0:
            k = 0.3 * kick(); out[s:s + len(k)] += k[:len(out) - s]
        if i % 2 == 1:
            h = 0.08 * hat(0.05); out[s:s + len(h)] += h[:len(out) - s]
    out = lowpass(out[:int(d * SR)], 5000); tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.4) * np.minimum(1, (d - tt) / 1.4)


def peel(d=0.6):
    # sticky crackle (dense tiny clicks) rising, then a paper whoosh as it comes free
    n = int(d * SR); t = np.arange(n) / SR
    clicks = (rng.random(n) < (0.02 + 0.08 * t / d)) * rng.standard_normal(n)
    crack = lowpass(clicks, 7000) * np.minimum(1, (d - t) / 0.08) * 0.9
    fl = lowpass(rng.standard_normal(n), 2500) * np.sin(np.pi * t / d) ** 2 * 0.35
    return crack + fl


def rip(d=0.25):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 5000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 60 * t))) * np.exp(-t * 8) * 0.6


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    peels = [(T['h2'] + 0.25, 0.75), (T['c1'] - 0.5, 0.45), (T['c2'] - 0.45, 0.45), (T['c3'] - 0.45, 0.45), (T['count'] - 0.45, 0.45), (T['u0'] - 0.45, 0.5), (T['u1'] - 0.4, 0.4), (T['u2'] - 0.4, 0.4), (T['print'] - 0.45, 0.45), (T['brand'] - 0.45, 0.5)]
    parts = [(T['h2'] + 1.0, 0.5 * lofi(dur - T['h2'] - 1.0))]
    parts += [(a, peel(d + 0.1)) for a, d in peels] + [(a + d * 0.6 + j * 0.06, 0.25 * pop(0.08)) for a, d in peels[1:9] for j in range(3)]
    parts += [(T['h2'] + 1.1 + j * 0.06, 0.25 * pop(0.08)) for j in range(6)] + [(T['n2'], 0.4 * rip())]
    parts += [(T['store2'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
