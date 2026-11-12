"""Reel 53 score: autumn folk on fingerpicked guitar, wind gusts, leaf rustles and wooden peg clicks.

usage: python3 sfx_reel53.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng
from sfx_reel10 import rustle
from sfx_reel16 import wood
from sfx_reel17 import pluck
from sfx_reel22 import pad

# Em - C - G - D travis-style picking
CH = [[82.4, 164.8, 196.0, 246.9], [65.4, 164.8, 196.0, 261.6], [98.0, 146.8, 196.0, 246.9], [73.4, 146.8, 185.0, 220.0]]
PAT = [0, 2, 1, 3, 0, 2, 1, 2]


def folk(d, bpm=92):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2)
    for i in range(int(d / e) + 1):
        bar = (i // 8) % 4; s = int(i * e * SR); f = CH[bar][PAT[i % 8]]
        x = (0.32 if PAT[i % 8] == 0 else 0.2) * pluck(f * (2 if PAT[i % 8] else 1), 1.0, 0.996); out[s:s + len(x)] += x[:len(out) - s]
        if i % 8 == 0:
            z = 0.04 * lowpass(pad(CH[bar][1:], 8 * e + 0.2), 900); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


def wind(d=1.0):
    n = int(d * SR); x = np.linspace(0, 1, n)
    cut = 300 + 1800 * np.sin(np.pi * x) ** 2
    return lowpass(rng.standard_normal(n), cut) * np.sin(np.pi * x) ** 1.5 * 0.9


def peg():
    return mix((0, 0.5 * wood(0.05)), (0.03, 0.3 * wood(0.04)))


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * folk(dur)), (0, 0.5 * wind(1.0))] + [(a + 0.5, peg()) for a in (0.15, 0.3, 0.45)] + [(T['h1'] - 0.2, peg()), (T['h2'] - 0.2, peg())]
    parts += [(c - 0.55, wind(1.1)) for c in cut] + [(c - 0.4, 0.5 * rustle(0.8)) for c in cut]
    parts += [(T[k] - 0.3, 0.5 * wind(0.6)) for k in ('c2', 'c3')] + [(T[k] - 0.1, peg()) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1] + 0.1 + i * 0.06, 0.4 * wood(0.04)) for i in range(15)] + [(T['n2'] - 0.2, peg())]
    parts += [(a + 0.1, peg()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)] + [(a - 0.3, 0.4 * wind(0.6)) for a in (T['u1'], T['u2'])]
    parts += [(cut[3] + 0.4, peg()), (T['print'] - 0.2, peg()), (T['print2'] - 0.2, peg())]
    parts += [(cut[4] + 0.55, peg()), (T['brand'] - 0.2, peg()), (T['store'] - 0.2, peg()), (T['store2'] - 0.2, peg()), (T['store2'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
