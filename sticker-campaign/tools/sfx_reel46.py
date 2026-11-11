"""Reel 46 score: florist-shop waltz on music box and strings, paper rustles, soft flower thuds, ribbon zips and a shop bell.

usage: python3 sfx_reel46.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle
from sfx_reel10 import rustle
from sfx_reel17 import pluck
from sfx_reel18 import bell
from sfx_reel22 import pad

# D - Bm - G - A waltz
CH = [[146.8, 220.0, 293.7, 370.0], [123.5, 185.0, 246.9, 293.7], [98.0, 196.0, 246.9, 293.7], [110.0, 220.0, 277.2, 329.6]]
MEL = [[740, 659, 587], [587, 554, 494], [494, 587, 740], [659, 554, 440]]


def mbox(f, d=1.0):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 8)) * np.exp(-t * 3.5) * np.minimum(1, t / 0.003)


def waltz(d, bpm=138):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 3) % 4; s = int(i * b * SR); beat = i % 3
        if beat == 0:
            x = 0.3 * pluck(CH[bar][0], 1.2, 0.996)
            z = 0.06 * lowpass(pad(CH[bar][1:], 3 * b + 0.2), 1500); out[s:s + len(z)] += z[:len(out) - s]
        else:
            x = 0.12 * mix(*[(0, pluck(f, 0.5, 0.993)) for f in CH[bar][1:3]])
        out[s:s + len(x)] += x[:len(out) - s]
        m = 0.22 * mbox(MEL[bar][beat]); out[s:s + len(m)] += m[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


def thud(d=0.25):
    # flower landing in paper: soft low thump plus crinkle
    t = np.arange(int(d * SR)) / SR
    return 0.7 * np.sin(2 * np.pi * (90 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 18) + 0.25 * lowpass(rng.standard_normal(len(t)), 5000) * np.exp(-t * 25)


def zipr(d=0.35):
    # ribbon pulled tight: rising filtered noise
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 800 + 5000 * t) * np.sin(np.pi * t) * 0.5


D = dict(h1=0.3, h2=1.3, c1=3.0, c2=4.2, c3=5.4, count=7.4, n2=8.8, u0=10.4, u1=11.6, u2=12.8, print=14.6, print2=15.7, brand=17.4, store=18.8, store2=19.5, end_all=22.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.55 * waltz(dur)), (0.0, 0.6 * rustle(0.6))] + [(0.35 + i * 0.12 + 0.3, 0.4 * thud()) for i in range(4)]
    parts += [(T['h2'] + 0.15, 0.6 * thud()), (T['h2'] + 0.2, 0.4 * sparkle())]
    parts += [(c - 0.1, 0.5 * rustle(0.45)) for c in cut]
    parts += [(T[k] - 0.05, 0.7 * thud()) for k in ('c1', 'c2', 'c3')] + [(T['c3'] + 0.6, zipr())]
    parts += [(cut[1] + 0.25 + i * 0.05, 0.2 * thud(0.15)) for i in range(14)] + [(T['n2'], 0.4 * sparkle())]
    parts += [(a + 0.05, 0.5 * rustle(0.4)) for a in (cut[2] + 0.05, T['u1'] - 0.3, T['u2'] - 0.3)] + [(a + 0.55, 0.6 * thud()) for a in (cut[2] + 0.05, T['u1'] - 0.3, T['u2'] - 0.3)]
    parts += [(cut[3] + 0.1, 0.6 * rustle(0.9)), (cut[3] + 1.3, 0.5 * thud())]
    parts += [(cut[4] + 0.2 + i * 0.12, 0.35 * thud()) for i in range(5)] + [(T['store'] - 0.4, 0.5 * zipr()), (T['store2'], 0.5 * bell()), (T['store2'] + 0.05, 0.4 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
