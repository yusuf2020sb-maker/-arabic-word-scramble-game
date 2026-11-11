"""Reel 45 score: night-sky celesta lullaby, star twinkles, harp glissandos and shooting-star whooshes.

usage: python3 sfx_reel45.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, sparkle, whoosh
from sfx_reel22 import pad

# Am - F - C - G, slow 6/8 lullaby
CH = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [261.6, 329.6, 392.0], [196.0, 246.9, 293.7]]


def celesta(f, d=1.2):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 9)) * np.exp(-t * 3.2) * np.minimum(1, t / 0.003)


def lullaby(d, bpm=72):
    e = 60 / bpm / 3; out = np.zeros(int(d * SR) + SR * 3)
    pat = [0, 1, 2, 1, 2, 1]
    for i in range(int(d / e) + 1):
        bar = (i // 12) % 4; s = int(i * e * SR); f = CH[bar][pat[i % 6]] * 2
        x = 0.22 * celesta(f); out[s:s + len(x)] += x[:len(out) - s]
        if i % 12 == 0:
            z = 0.08 * lowpass(pad([c / 2 for c in CH[bar]], 12 * e + 0.5), 700); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 1.5)


def twinkle(f=1760):
    return mix((0, 0.5 * celesta(f, 0.8)), (0.07, 0.35 * celesta(f * 1.5, 0.8)), (0.02, 0.3 * sparkle(0.4)))


def harp(up=True, n=9, gap=0.045):
    sc = [261.6, 293.7, 329.6, 392.0, 440.0, 523.3, 587.3, 659.3, 784.0, 880.0]
    seq = sc[:n] if up else sc[:n][::-1]
    return mix(*[(i * gap, 0.35 * celesta(f, 0.9)) for i, f in enumerate(seq)])


def shoot(d=0.6):
    return mix((0, 0.7 * lowpass(whoosh(d), 6000)), (d * 0.5, 0.4 * sparkle(0.5)))


D = dict(h1=0.4, h2=1.6, c1=3.4, c2=4.6, c3=5.8, count=7.6, n2=9.0, u0=10.6, u1=11.8, u2=13.0, print=14.8, print2=15.9, brand=17.6, store=19.0, store2=19.7, end_all=22.6)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.45, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.55 * lullaby(dur)), (0.1, 0.4 * harp()), (T['h2'] + 0.2, 0.5 * twinkle(2093))]
    parts += [(c - 0.35, shoot()) for c in cut]
    parts += [(T[k] - 0.4, twinkle(1568 + 200 * i)) for i, k in enumerate(('c1', 'c2', 'c3'))]
    parts += [(cut[1] + 0.3 + i * 0.07, 0.25 * celesta(1046.5 * (1 + (i % 5) * 0.125), 0.5)) for i in range(14)] + [(T['n2'], 0.4 * twinkle(2349))]
    parts += [(a, 0.5 * harp(i % 2 == 0, 6)) for i, a in enumerate((cut[2] + 0.05, T['u1'] - 0.3, T['u2'] - 0.3))]
    parts += [(cut[3] + 0.05, 0.4 * harp(False)), (T['print2'], 0.4 * twinkle(1760))]
    parts += [(cut[4] + 0.2 + i * 0.18, 0.35 * twinkle(1318.5 * 2 ** (i / 6))) for i in range(5)] + [(T['store2'], 0.6 * chime(1.6))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
