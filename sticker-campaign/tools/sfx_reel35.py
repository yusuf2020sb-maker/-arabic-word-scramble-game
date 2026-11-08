"""Score for reel 35 (coffee, retro groovy motion graphics): funky 100 bpm groove (wah-ish bass, clavinet stabs, claps),
battery drain beeps, a power-up on the charge, boings on squash-pops, wave swooshes at cuts.

usage: python3 sfx_reel35.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel5 import boing
from sfx_reel14 import pour, powerup
from sfx_reel20 import hat, kick
from sfx_reel28 import clap


def clav(f, d=0.18):
    t = np.arange(int(d * SR)) / SR
    y = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * 2 * f * t) * 0.3
    return lowpass(y, 3000) * np.exp(-t * 18)


def wbass(f, d):
    t = np.arange(int(d * SR)) / SR
    y = 2 * ((f * t) % 1) - 1
    cut = 300 + 900 * np.exp(-t * 8)
    return lowpass(y, 700) * np.exp(-t * 2) * np.minimum(1, t * 300) * (0.6 + 0.4 * (cut / 1200))


def funk(d, bpm=100):
    s16 = 60 / bpm / 4; out = np.zeros(int(d * SR) + SR); BL = [82.4, 82.4, 98.0, 110.0]
    for i in range(int(d / s16) + 1):
        s = int(i * s16 * SR); parts = []
        if i % 16 in (0, 10): parts.append(0.7 * kick(0.25))
        if i % 8 == 4: parts.append(0.45 * clap())
        if i % 2 == 0: parts.append(0.12 * hat(0.04))
        if i % 16 in (0, 3, 6, 10, 12): parts.append(0.3 * wbass(BL[(i // 16) % 4], s16 * 2.5))
        if i % 16 in (2, 7, 11, 14): parts.append(0.14 * clav(BL[(i // 16) % 4] * 4))
        for x in parts:
            out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 1.2)


def beep(f=1200, d=0.08):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.minimum(1, (d - t) * 200) * 0.6


D = dict(h1=0.2, h2=2.0, title=3.6, t2=4.6, b0=6.4, b1=7.8, b2=9.2, u0=11.0, u1=12.4, u2=13.8, print=15.4, brand=18.0, store=19.4, end_all=22.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.25 for k in ('title', 'b0', 'u0', 'print', 'brand')]
    parts = [(T['h2'] + 0.2, 0.45 * funk(dur - T['h2'] - 0.2))]
    parts += [(0.2 + i * 0.3, 0.4 * beep(1400 - i * 120)) for i in range(5)] + [(1.6, 0.5 * beep(600, 0.4))]
    parts += [(T['h2'] - 0.1, 0.6 * boing(0.4)), (T['h2'] + 0.2, 0.7 * powerup(0.85)), (T['h2'] + 0.15, 0.4 * pour(0.8))]
    parts += [(c - 0.35, 0.6 * whoosh(0.7)) for c in cuts]
    parts += [(cuts[0] + 0.1 + i * 0.05, 0.25 * pop(0.1)) for i in range(12)]
    parts += [(T[k] - 0.15, 0.6 * boing(0.4)) for k in ('b0', 'b1', 'b2')]
    parts += [(a + 0.35 + j * 0.15, 0.4 * pop(0.12)) for a in (cuts[2] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2) for j in range(2)]
    parts += [(cuts[3] + 1.0, 0.4 * boing(0.3)), (cuts[3] + 1.2, 0.4 * boing(0.3))]
    parts += [(cuts[4] + 0.3, 0.5 * boing(0.4)), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
