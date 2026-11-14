"""Reel 59 score: bouncy cartoon funk (slap bass, brass stabs, snare), comic slams, boings, record scratch and a slide-whistle.

usage: python3 sfx_reel59.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng
from sfx_reel5 import boing, thump
from sfx_reel8 import scratch
from sfx_reel20 import hat, kick

BASS = [98.0, 98.0, 116.5, 130.8, 98.0, 87.3, 98.0, 146.8]


def snare(d=0.18):
    n = int(d * SR); t = np.arange(n) / SR
    return (lowpass(rng.standard_normal(n), 6000) * 0.6 + 0.4 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 22)


def brass(fs, d=0.22):
    t = np.arange(int(d * SR)) / SR
    y = sum(np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * 2 * t) * 0.15 for f in fs)
    return lowpass(y, 2500) * np.minimum(1, t / 0.01) * np.exp(-t * 6)


def funk(d, bpm=104):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR)
    for i in range(int(d / e) + 1):
        s = int(i * e * SR)
        t = np.arange(int(e * 0.9 * SR)) / SR; b = 0.3 * np.sin(2 * np.pi * BASS[i % 8] * t) * np.exp(-t * 7); out[s:s + len(b)] += b[:len(out) - s]
        if i % 4 == 0:
            k = 0.4 * kick(); out[s:s + len(k)] += k[:len(out) - s]
        if i % 4 == 2:
            n = 0.35 * snare(); out[s:s + len(n)] += n[:len(out) - s]
        h = 0.08 * hat(0.04); out[s:s + len(h)] += h[:len(out) - s]
        if i % 16 in (3, 11):
            z = 0.25 * brass([392.0, 493.9, 587.3]); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.2) * np.minimum(1, (d - tt) / 1.2)


def slam():
    return mix((0, 0.9 * thump()), (0, 0.4 * snare(0.12)))


def whistle(d=0.5, up=True):
    t = np.arange(int(d * SR)) / SR; f = (700 + 900 * t / d) if up else (1600 - 900 * t / d)
    return 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.45 * funk(dur)), (T['h1'] - 0.2, slam()), (T['h1'] + 0.3, 0.4 * whistle(0.6, False)), (T['h2'] - 0.2, slam()), (T['h2'] + 0.15, 0.5 * boing())]
    parts += [(c - 0.05, 0.6 * scratch(0.3)) for c in cut]
    parts += [(T[k] - 0.25, slam()) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.1, 0.3 * pop()) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1] + 0.05, slam())] + [(cut[1] + 0.35 + i * 0.06, 0.3 * thump()) for i in range(8)] + [(T['n2'], 0.4 * boing())]
    parts += [(a, slam()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)] + [(a + 0.3 + j * 0.1, 0.25 * pop()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3) for j in range(3)]
    parts += [(cut[3] + 0.1, slam()), (T['print2'], 0.4 * whistle(0.4)), (cut[4] + 0.25, slam()), (cut[4] + 0.6, 0.4 * boing()), (T['store2'], 0.4 * brass([523.3, 659.3, 784.0], 0.6)), (T['store2'] + 0.05, 0.5 * chime(1.2))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
