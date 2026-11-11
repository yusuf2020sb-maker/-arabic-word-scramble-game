"""Reel 47 score: collector's-study jazz (brushed snare, upright bass, vibraphone), stamp thuds, glassine slides, magnifier swooshes and a postmark.

usage: python3 sfx_reel47.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel9 import stamp_thud
from sfx_reel16 import page
from sfx_reel17 import pluck
from sfx_reel42 import brush

# ii - V - I - vi in F, vibraphone comping
CH = [[196.0, 233.1, 293.7, 349.2], [261.6, 329.6, 392.0, 466.2], [174.6, 220.0, 261.6, 329.6], [146.8, 174.6, 220.0, 261.6]]
BASS = [[98.0, 110.0, 116.5, 123.5], [130.8, 123.5, 110.0, 98.0], [87.3, 98.0, 110.0, 130.8], [73.4, 87.3, 98.0, 110.0]]


def vib(f, d=1.2):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * (1 + 0.25 * np.sin(2 * np.pi * 5.5 * t)) * np.exp(-t * 2.4) * np.minimum(1, t / 0.004)


def study(d, bpm=104):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 4) % 4; s = int(i * b * SR)
        x = 0.45 * pluck(BASS[bar][i % 4], 0.6, 0.993); out[s:s + len(x)] += x[:len(out) - s]
        y = 0.8 * brush(); out[s:s + len(y)] += y[:len(out) - s]
        if i % 4 in (0, 2):
            z = mix(*[(0.02 * j, 0.07 * vib(f * 2, 1.0)) for j, f in enumerate(CH[bar])]); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.4)


def slide(d=0.25):
    # stamp slipping behind glassine
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 3000 + 3000 * t) * np.sin(np.pi * t) * 0.35


def swoosh(d=0.4):
    return 0.6 * lowpass(whoosh(d), 3000)


D = dict(h1=0.3, h2=1.4, c1=3.2, c2=4.6, c3=6.0, count=7.8, n2=9.2, u0=10.8, u1=12.0, u2=13.2, print=15.0, print2=16.1, brand=17.8, store=19.4, store2=20.1, end_all=23.0)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.45, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * study(dur))] + [(0.1 + i * 0.07 + 0.25, 0.4 * slide()) for i in range(16)]
    parts += [(T['h1'], 0.6 * stamp_thud()), (T['h2'], 0.7 * stamp_thud())]
    parts += [(c - 0.05, 0.6 * page()) for c in cut[1:]]
    parts += [(T[k] - 0.4, swoosh()) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.05, 0.4 * stamp_thud()) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1] + 0.1 + i * 0.025, 0.12 * stamp_thud()) for i in range(35)] + [(cut[1] + 0.15, 0.7 * stamp_thud()), (T['n2'], 0.5 * stamp_thud())]
    for a in (cut[2] + 0.05, T['u1'] - 0.3, T['u2'] - 0.3):
        parts += [(a + 0.2, 0.5 * stamp_thud()), (a + 0.55, 0.8 * stamp_thud())]
    parts += [(cut[3] + 0.1, 0.5 * slide(0.6)), (T['print2'], 0.4 * stamp_thud())]
    parts += [(cut[4] + 0.3, 0.6 * stamp_thud()), (cut[4] + 0.9, 0.9 * stamp_thud()), (T['store2'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
