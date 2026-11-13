"""Reel 57 score: antique clockwork waltz (harpsichord-like plucks + cello pad), clock ticks, gear ratchets, wind-up and an hour bell.

usage: python3 sfx_reel57.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng
from sfx_reel8 import tick
from sfx_reel17 import pluck
from sfx_reel22 import pad

CH = [[110.0, 220.0, 261.6, 329.6], [98.0, 196.0, 246.9, 293.7], [87.3, 174.6, 220.0, 261.6], [82.4, 164.8, 207.7, 246.9]]
MEL = [659.3, 587.3, 523.3, 587.3, 523.3, 493.9, 523.3, 440.0, 415.3, 440.0, 493.9, 523.3]


def harpsi(f, d=0.6):
    return mix((0, pluck(f, d, 0.992)), (0, 0.4 * pluck(f * 2, d * 0.6, 0.99)))


def clockwork(d, bpm=108):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 2)
    for i in range(int(d / b) + 1):
        bar = (i // 3) % 4; s = int(i * b * SR)
        x = 0.2 * harpsi(CH[bar][0] if i % 3 == 0 else CH[bar][1 + i % 3]); out[s:s + len(x)] += x[:len(out) - s]
        m = 0.12 * harpsi(MEL[i % 12]); out[s:s + len(m)] += m[:len(out) - s]
        if i % 3 == 0:
            z = 0.06 * lowpass(pad([CH[bar][0], CH[bar][2]], 3 * b + 0.2), 700); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.4)


def ticks(d, rate=2.0):
    return mix(*[(i / rate, (0.35 if i % 2 else 0.25) * tick(0.03)) for i in range(int(d * rate))])


def ratchet(n=6, gap=0.05):
    def c():
        m = int(0.025 * SR); t = np.arange(m) / SR
        return lowpass(rng.standard_normal(m), 4000) * np.exp(-t * 250) * 0.5 + 0.3 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 300)
    return mix(*[(i * gap, c()) for i in range(n)])


def bell(f=440.0, d=2.0):
    t = np.arange(int(d * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * dk) for r, a, dk in [(1, 0.6, 1.2), (2.0, 0.3, 1.8), (2.4, 0.25, 2.2), (3.0, 0.15, 3.0), (4.2, 0.1, 4.0)])


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.45 * clockwork(dur)), (0, ticks(cut[0])), (T['h2'], 0.4 * bell(523.3, 1.5))]
    parts += [(T[k] - 0.45, ratchet(8, 0.05)) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.05, 0.3 * bell(659.3, 0.9)) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1], ratchet(14, 0.04))] + [(cut[1] + 0.2 + i * 0.07, 0.3 * tick(0.03)) for i in range(12)] + [(T['n2'], 0.3 * bell(587.3, 0.9))]
    parts += [(a, ratchet(4)) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)]
    parts += [(cut[3] + 0.1, ratchet(5)), (T['print2'], 0.3 * bell(659.3, 0.9))]
    parts += [(cut[4] + 0.2, ratchet(6)), (T['store2'], 0.6 * bell(440.0, 2.0)), (T['store2'] + 0.05, 0.4 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
