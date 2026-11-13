"""Reel 58 score: winter-night music box over a soft felt piano, door creak, light-switch clicks with a warm hum, snow wind and a door bell.

usage: python3 sfx_reel58.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng
from sfx_reel10 import creak
from sfx_reel16 import crackle
from sfx_reel22 import pad, piano

CH = [[146.8, 185.0, 220.0, 293.7], [123.5, 146.8, 185.0, 246.9], [98.0, 146.8, 196.0, 246.9], [110.0, 138.6, 164.8, 220.0]]
MEL = [880.0, 740.0, 659.3, 740.0, 587.3, 659.3, 740.0, 880.0, 987.8, 880.0, 740.0, 659.3]


def mbox(f, d=1.0):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 8)) * np.exp(-t * 3.5) * np.minimum(1, t / 0.003)


def night(d, bpm=84):
    b = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 8) % 4; s = int(i * b * SR)
        m = 0.18 * mbox(MEL[i % 12]); out[s:s + len(m)] += m[:len(out) - s]
        if i % 8 == 0:
            z = mix(*[(0.03 * j, 0.07 * lowpass(piano(f, 2.5), 1400)) for j, f in enumerate(CH[bar])], (0, 0.05 * lowpass(pad(CH[bar], 8 * b + 0.3), 700))); out[s:s + len(z)] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 1.4)


def switch():
    n = int(0.03 * SR); t = np.arange(n) / SR
    c = lowpass(rng.standard_normal(n), 5000) * np.exp(-t * 250) * 0.6
    h = np.arange(int(0.5 * SR)) / SR; hum = 0.12 * np.sin(2 * np.pi * 120 * h) * np.exp(-h * 4)
    return mix((0, c), (0.02, hum))


def wind(d=2.0):
    n = int(d * SR); x = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 400 + 500 * np.sin(np.pi * x) ** 2) * np.sin(np.pi * x) * 0.6


def doorbell():
    return mix((0, 0.5 * mbox(1318.5, 0.8)), (0.18, 0.5 * mbox(1046.5, 1.0)))


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * night(dur)), (0, wind(2.5)), (T['h2'] + 0.6, 0.6 * creak()), ]
    parts += [(T[k] - 0.1, switch()) for k in ('c1', 'c2', 'c3')] + [(T['c1'] + 0.1, 0.25 * crackle(1.2))] + [(T[k] - 0.05 + j * 0.1, 0.25 * pop(0.08)) for k in ('c1', 'c2', 'c3') for j in range(4)]
    parts += [(cut[1] + 0.4 + i * 0.15 + j * 0.08, 0.2 * pop(0.08)) for i in range(3) for j in range(3)] + [(T['n2'], 0.3 * mbox(1318.5, 0.6))]
    parts += [(a + 0.3, 0.3 * pop()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)]
    parts += [(cut[3] + 0.2, 0.3 * mbox(1174.7, 0.6)), (cut[4], 0.5 * creak()), (cut[4] + 0.5, 0.4 * pop()), (T['store2'], doorbell()), (T['store2'] + 0.1, 0.4 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
