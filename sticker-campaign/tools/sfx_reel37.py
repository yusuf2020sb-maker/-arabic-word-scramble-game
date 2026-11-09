"""Score for reel 37 (vintage roses, luxury ink-bloom motion graphics): dark string pad in C minor,
slow celesta arpeggios, ink-bloom swells (reversed noise), gold shimmer chimes and soft low booms.

usage: python3 sfx_reel37.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle
from sfx_reel10 import boom
from sfx_reel22 import pad

CM = [[130.8, 155.6, 196.0, 261.6], [103.8, 155.6, 207.7, 261.6], [116.5, 146.8, 174.6, 233.1], [98.0, 146.8, 196.0, 246.9]]


def celesta(f, d=1.2):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)) * np.exp(-t * 3.5) * np.minimum(1, t * 600)


def swell(d=0.9):
    t = np.arange(int(d * SR)) / SR
    x = lowpass(rng.standard_normal(len(t)), 2500) * (t / d) ** 2.2
    return x * np.minimum(1, (d - t) * 30)


def score(d, bpm=70):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3); i = 0
    while i * b * 4 < d:
        ch = CM[i % 4]; s = int(i * b * 4 * SR)
        x = 0.35 * pad(ch, b * 4 + 0.8); out[s:s + len(x)] += x[:len(out) - s]
        for j, f in enumerate([ch[3] * 2, ch[2] * 2, ch[1] * 4, ch[3] * 2]):
            y = 0.12 * celesta(f); ss = s + int(j * b * SR); out[ss:ss + len(y)] += y[:len(out) - ss]
        i += 1
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 1.0) * np.minimum(1, (d - tt) / 1.8)


D = dict(h1=0.2, h2=1.2, c0=3.0, c1=3.9, c2=4.8, count=6.4, n2=7.4, u0=9.0, u1=10.3, u2=11.6, print=13.2, brand=15.8, store=17.0, store2=17.6, end_all=20.5)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.25 for k in ('c0', 'count', 'u0', 'print', 'brand')]
    parts = [(0, 0.5 * score(dur)), (0, 0.4 * swell(0.6)), (0.4, 0.4 * boom(0.8)), (T['h1'] + 0.2, 0.35 * sparkle(0.8)), (T['h2'] + 0.2, 0.3 * sparkle(0.8))]
    blooms = [cuts[0] + 0.05, T['c1'] - 0.2, T['c2'] - 0.2, cuts[2] + 0.05, T['u1'] - 0.25, T['u2'] - 0.25, cuts[4]]
    parts += [(a - 0.5, 0.45 * swell(0.6)) for a in blooms] + [(a + 0.1, 0.25 * boom(0.6)) for a in blooms]
    parts += [(cuts[1] + 0.2, 0.4 * chime(1.0)), (T['n2'], 0.3 * sparkle(0.8))]
    parts += [(cuts[3] + 0.1, 0.4 * swell(0.5)), (cuts[3] + 1.0, 0.3 * chime(0.6))]
    parts += [(T['store2'], 0.6 * chime(1.6)), (T['store2'] + 0.1, 0.35 * sparkle(1.0))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
