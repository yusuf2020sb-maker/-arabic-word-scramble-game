"""Score for reel 42 (coffee & sweets, chalkboard-menu motion graphics): café jazz trio (walking bass, brushes,
soft Rhodes), chalk scratches when text is written, cup clinks, espresso steam and eraser rubs at cuts.

usage: python3 sfx_reel42.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng
from sfx_reel14 import hiss
from sfx_reel17 import clink, pluck
from sfx_reel22 import piano

PROG = [[146.8, 174.6, 220.0, 261.6], [98.0, 174.6, 246.9, 293.7], [130.8, 164.8, 196.0, 246.9], [110.0, 164.8, 196.0, 261.6]]
WALK = [[73.4, 82.4, 87.3, 98.0], [98.0, 87.3, 82.4, 73.4], [65.4, 73.4, 82.4, 87.3], [55.0, 61.7, 65.4, 69.3]]


def brush(d=0.18):
    t = np.arange(int(d * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 6000) * np.sin(np.pi * t / d) * 0.25


def jazz(d, bpm=96):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 4) % 4; s = int(i * b * SR)
        x = 0.5 * pluck(WALK[bar][i % 4], 0.6, 0.994); out[s:s + len(x)] += x[:len(out) - s]
        y = brush(); out[s:s + len(y)] += y[:len(out) - s]
        if i % 4 in (1, 3):
            z = mix(*[(0, 0.12 * lowpass(piano(f * 2, 0.9), 1800)) for f in PROG[bar]]); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.4)


def chalk(d=0.4):
    t = np.arange(int(d * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 3500) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 9 * t))) * np.sin(np.pi * t / d) * 0.5


def rub(d=0.6):
    t = np.arange(int(d * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 1200) * np.abs(np.sin(2 * np.pi * 5 * t)) * np.sin(np.pi * t / d) * 0.6


D = dict(h1=0.2, h2=1.0, d0=2.6, d1=3.4, d2=4.2, s0=5.6, s1=6.4, s2=7.2, count=8.6, n2=9.8, u0=11.4, u1=12.8, u2=14.2, print=15.8, brand=18.2, store=19.6, store2=20.2, end_all=22.8)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T['d0'] - 0.4] + [T[k] - 0.3 for k in ('count', 'u0', 'print', 'brand')]
    parts = [(0, 0.45 * jazz(dur)), (T['h1'], chalk(0.5)), (T['h2'], chalk(0.5)), (T['h2'] - 0.1, 0.5 * clink()), (0.8, 0.3 * hiss(0.8))]
    parts += [(c - 0.35, rub()) for c in cuts]
    parts += [(T[k] - 0.1, 0.8 * chalk(0.45)) for k in ('d0', 'd1', 'd2', 's0', 's1', 's2')] + [(T[k] + 0.2, 0.3 * pop(0.1)) for k in ('d0', 'd1', 'd2', 's0', 's1', 's2')]
    parts += [(cuts[1] + 0.2, chalk(0.6))] + [(cuts[1] + 0.5 + i * 0.06, 0.2 * pop(0.1)) for i in range(14)]
    parts += [(a, chalk(0.5)) for a in (cuts[2] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2)] + [(a + 0.5, 0.4 * clink()) for a in (cuts[2] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2)]
    parts += [(cuts[3] + 0.1, chalk(0.5)), (cuts[4] + 0.1, chalk(0.6)), (T['store2'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
