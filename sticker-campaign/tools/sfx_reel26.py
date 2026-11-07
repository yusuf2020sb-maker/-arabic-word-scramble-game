"""Score for reel 26 (vintage ephemera): romantic piano in D minor, wax crack, paper burst, drawer slides, flipbook riffle, seal thud.

usage: python3 sfx_reel26.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel9 import stamp_thud
from sfx_reel10 import rustle
from sfx_reel18 import crack, slide
from sfx_reel22 import pad, piano

DM = [[146.8, 293.7, 349.2, 440.0], [116.5, 293.7, 349.2, 466.2], [130.8, 261.6, 329.6, 392.0], [110.0, 277.2, 329.6, 440.0]]


def romance(d, bpm=72):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 3); i = 0
    while i * e < d:
        ch = DM[(i // 8) % 4]; f = ch[[0, 2, 3, 1, 2, 3, 1, 2][i % 8]]
        x = (0.5 if i % 8 == 0 else 0.25) * piano(f, 1.8); s = int(i * e * SR); out[s:s + len(x)] += x[:len(out) - s]
        if i % 8 == 0:
            y = 0.12 * pad(ch, 8 * e + 0.5); out[s:s + len(y)] += y[:len(out) - s]
        i += 1
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 1.5)


def flap(n=6, gap=0.05):
    return mix(*[(i * gap, 0.4 * lowpass(rng.standard_normal(int(0.03 * SR)), 2500) * np.exp(-np.arange(int(0.03 * SR)) / SR * 120)) for i in range(n)])


def riffle(d):
    n = int(d / 0.04)
    return mix(*[(i * 0.04, 0.35 * lowpass(rng.standard_normal(int(0.025 * SR)), 5000) * np.exp(-np.arange(int(0.025 * SR)) / SR * 150)) for i in range(n)])


def drawer(d=0.45):
    t = np.arange(int(d * SR)) / SR
    x = lowpass(rng.standard_normal(len(t)), 700) * np.sin(np.pi * t / d) * 0.8
    return x + 0.3 * np.sin(2 * np.pi * 90 * t) * np.exp(-(d - t) * 30)


D = dict(h1=0.2, h2=1.0, open=2.4, h3=2.6, h4=3.4, title=4.8, t2=5.6, k0=7.6, k1=8.5, k2=9.4, k3=10.3, colors=11.6, c0=12.6, c1=13.4, c2=14.2, c3=15.0,
         count=16.4, u0=19.0, u1=20.4, u2=21.8, print=23.4, brand=26.0, store=27.4, end_all=30.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.25 for k in ('title', 'k0', 'colors', 'count', 'u0', 'print', 'brand')]
    parts = [(0, 0.42 * romance(dur)), (0.1, 0.4 * slide(0.6))]
    parts += [(T['open'], 0.9 * crack(0.3)), (T['open'] + 0.3, 0.5 * slide(0.6)), (T['h4'] - 0.1, 0.8 * rustle(0.6)), (T['h4'], 0.5 * sparkle(0.8))]
    parts += [(c - 0.6, 0.5 * flap(10, 0.06)) for c in cuts]
    parts += [(cuts[0] + 0.1, 0.4 * whoosh(0.6))]
    parts += [(a - 0.1, 0.5 * whoosh(0.35)) for a in (T['k0'], T['k1'], T['k2'], T['k3'])]
    parts += [(a - 0.2, 0.8 * drawer()) for a in (T['c0'], T['c1'], T['c2'], T['c3'])]
    parts += [(cuts[3] + 0.1, riffle(max(1.2, cuts[4] - cuts[3] - 0.5)))]
    parts += [(a, 0.6 * whoosh(0.45)) for a in (cuts[4] + 0.1, T['u1'] - 0.25, T['u2'] - 0.25)]
    parts += [(cuts[5] + 0.1, 0.6 * slide(0.7)), (cuts[5] + 1.0, 0.4 * chime(0.6))]
    parts += [(cuts[6] + 0.9 + 0.22, 1.0 * stamp_thud()), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
