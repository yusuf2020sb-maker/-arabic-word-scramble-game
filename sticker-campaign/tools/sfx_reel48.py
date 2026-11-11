"""Reel 48 score: slow tea-house lo-fi on kanun-like plucks, liquid pours, bubbles, spoon clinks and a tea-tag bell.

usage: python3 sfx_reel48.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle
from sfx_reel14 import pour
from sfx_reel17 import clink, pluck
from sfx_reel20 import hat, kick
from sfx_reel22 import pad

CH = [[110.0, 164.8, 220.0, 261.6], [87.3, 174.6, 220.0, 261.6], [98.0, 196.0, 246.9, 293.7], [82.4, 164.8, 207.7, 246.9]]
MEL = [440.0, 523.3, 493.9, 440.0, 392.0, 440.0, 329.6, 349.2]


def lofi(d, bpm=78):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b * 2) + 1):
        s = int(i * b / 2 * SR); bar = (i // 8) % 4
        if i % 8 == 0:
            z = 0.07 * lowpass(pad(CH[bar], 4 * b + 0.3), 900); out[s:s + len(z)] += z[:len(out) - s]
        if i % 4 == 0:
            k = 0.3 * kick(); out[s:s + len(k)] += k[:len(out) - s]
        if i % 2 == 1:
            h = 0.08 * hat(); out[s:s + len(h)] += h[:len(out) - s]
        if i % 2 == 0:
            x = 0.16 * pluck(MEL[(i // 2) % 8] * (1 if bar % 2 == 0 else 0.89), 0.7, 0.994); out[s:s + len(x)] += x[:len(out) - s]
    out = lowpass(out[:int(d * SR)], 5000); tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.4)


def bubble(f=600):
    t = np.arange(int(0.09 * SR)) / SR
    return np.sin(2 * np.pi * (f + 900 * t / 0.09) * t) * np.exp(-t * 40) * 0.5


def slosh(d=0.8):
    # liquid wave: low filtered noise swell
    n = int(d * SR); x = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 500 + 900 * np.sin(np.pi * x)) * np.sin(np.pi * x) ** 1.5 * 1.2


D = dict(h1=0.3, h2=1.4, c1=3.2, c2=4.5, c3=5.8, count=7.6, n2=9.0, u0=10.6, u1=11.8, u2=13.0, print=14.8, print2=15.9, brand=17.6, store=19.1, store2=19.8, end_all=22.8)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * lofi(dur)), (0.05, 0.6 * pour(0.8)), (T['h2'], 0.5 * clink())]
    parts += [(c - 0.4, 0.7 * slosh(0.85)) for c in cut]
    parts += [(T[k] - 0.3, 0.4 * sparkle(0.35)) for k in ('c1', 'c2', 'c3')] + [(T[k] + 0.05 + j * 0.05, bubble(500 + 150 * j)) for k in ('c1', 'c2', 'c3') for j in range(3)]
    parts += [(cut[1] + 0.2 + i * 0.13, 0.6 * bubble(400 + 60 * (i % 7))) for i in range(18)]
    parts += [(a + 0.4, 0.4 * clink()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)]
    parts += [(cut[3] + 0.2, 0.4 * sparkle()), (cut[4] + 0.75, 0.5 * clink()), (T['store2'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
