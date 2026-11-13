"""Reel 55 score: chic boutique lo-fi (rhodes chords, soft kick, shaker), fan-deck ratchet clicks, colour-wash swooshes and paper pops.

usage: python3 sfx_reel55.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel20 import hat, kick

CH = [[220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 349.2], [164.8, 207.7, 246.9, 293.7]]


def rhodes(f, d=1.4):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t * 3))) * np.exp(-t * 2.2) * np.minimum(1, t / 0.005)


def boutique(d, bpm=86):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 2)
    for i in range(int(d / b * 2) + 1):
        s = int(i * b / 2 * SR); bar = (i // 8) % 4
        if i % 4 == 0:
            z = mix(*[(0.02 * j, 0.09 * rhodes(f, 2.0)) for j, f in enumerate(CH[bar])]); out[s:s + len(z)] += z[:len(out) - s]
            k = 0.3 * kick(); out[s:s + len(k)] += k[:len(out) - s]
        if i % 2 == 1:
            h = 0.1 * hat(0.06); out[s:s + len(h)] += h[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return lowpass(out, 6000) * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


def ratchet(n=5, gap=0.07):
    def click():
        m = int(0.02 * SR); t = np.arange(m) / SR
        return lowpass(rng.standard_normal(m), 5000) * np.exp(-t * 300) * 0.6
    return mix(*[(i * gap, click()) for i in range(n)])


def wash(d=0.5):
    return 0.6 * lowpass(whoosh(d), 3500)


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * boutique(dur)), (0.3, ratchet(6, 0.12)), (T['h1'], 0.4 * pop()), (T['h2'], 0.5 * pop())]
    parts += [(T[k] - 0.45, wash()) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.1 + j * 0.07, 0.25 * pop(0.08)) for k in ('c1', 'c2', 'c3') for j in range(6)]
    parts += [(cut[1], ratchet(5)), (cut[1] + 0.3, wash(0.6))] + [(cut[1] + 0.3 + i * 0.03, 0.12 * pop(0.06)) for i in range(24)] + [(T['n2'], 0.4 * pop())]
    parts += [(a, wash(0.4)) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)] + [(a + 0.3 + j * 0.1, 0.25 * pop(0.08)) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3) for j in range(3)]
    parts += [(cut[3], wash(0.6)), (T['print2'], 0.4 * pop()), (cut[4] + 0.2, wash(0.5)), (cut[4] + 0.3, 0.5 * pop()), (T['store2'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
