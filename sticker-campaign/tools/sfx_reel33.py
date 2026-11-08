"""Score for reel 33 (cozy home, draw-on motion graphics): warm lo-fi waltz on felt piano + brushes,
pencil scratches when lines draw, soft wooden plops when items land, a kettle whistle and a paper feed.

usage: python3 sfx_reel33.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel5 import printer
from sfx_reel16 import wood
from sfx_reel18 import pen
from sfx_reel22 import piano

CH = [[130.8, 196.0, 261.6, 329.6], [110.0, 196.0, 261.6, 329.6], [87.3, 174.6, 261.6, 349.2], [98.0, 196.0, 246.9, 293.7]]


def brush(d=0.25):
    t = np.arange(int(d * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 5000) * np.sin(np.pi * t / d) * 0.25


def felt(d, bpm=88):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3); i = 0
    while i * b < d:
        ch = CH[(i // 3) % 4]; s = int(i * b * SR)
        notes = [ch[0]] if i % 3 == 0 else [ch[2], ch[3]]
        for f in notes:
            x = (0.4 if i % 3 == 0 else 0.18) * lowpass(piano(f, 1.6), 1800); out[s:s + len(x)] += x[:len(out) - s]
        x = brush(); out[s:s + len(x)] += x[:len(out) - s]
        i += 1
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.4)


def whistle(d=0.7):
    t = np.arange(int(d * SR)) / SR
    return 0.3 * np.sin(2 * np.pi * (1800 + 120 * np.sin(2 * np.pi * 6 * t)) * t) * np.sin(np.pi * t / d) + 0.1 * lowpass(rng.standard_normal(len(t)), 4000) * np.sin(np.pi * t / d)


D = dict(h1=0.2, h2=1.3, k0=3.4, k1=4.3, k2=5.2, k3=6.1, count=7.4, n2=8.6, u0=10.4, u1=11.8, u2=13.2, print=14.8, brand=17.6, store=19.0, end_all=21.8)


def main(out_path):
    T = D; dur = T['end_all']; Z = [0, T['k0'] - 0.2, T['count'] - 0.2, T['u0'] - 0.2, T['print'] - 0.2, T['brand'] - 0.2]
    parts = [(0, 0.45 * felt(dur)), (0.0, 0.4 * pen(0.8))]
    parts += [(a, 0.5 * wood()) for a in (0.75, 0.95, 1.15)]
    parts += [(z - 0.35, 0.35 * whoosh(0.7)) for z in Z[1:]]
    parts += [(Z[1] - 0.2, 0.3 * pen(0.6))]
    parts += [(T[k] + 0.15 + j * 0.1, 0.6 * wood()) for k in ('k0', 'k1', 'k2', 'k3') for j in range(2)]
    parts += [(T['k1'] - 0.2, 0.35 * whistle())]
    parts += [(T['count'] - 0.1, 0.4 * pen(1.0))] + [(T['count'] + 0.9 + i * 0.07, 0.3 * pop(0.1)) for i in range(12)]
    parts += [(a - 0.1, 0.35 * pen(0.6)) for a in (T['u0'] - 0.1, T['u1'] - 0.15, T['u2'] - 0.15)]
    parts += [(a + 0.6 + j * 0.2, 0.5 * wood()) for a in (T['u0'] - 0.1, T['u1'] - 0.15, T['u2'] - 0.15) for j in range(2)]
    parts += [(Z[4] - 0.1, 0.3 * pen(0.7)), (Z[4] + 0.6, 0.5 * printer(1.4))]
    parts += [(Z[5] - 0.1, 0.3 * pen(0.7)), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
