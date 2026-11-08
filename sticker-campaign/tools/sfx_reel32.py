"""Score for reel 32 (vases, Swiss motion graphics): minimal 124 bpm house with a synth pluck arp,
camera-shutter clicks at cuts, ticks on flash cuts, soft thuds on bento pops, pen-draw on dimension lines.

usage: python3 sfx_reel32.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel8 import tick
from sfx_reel18 import pen
from sfx_reel20 import hat, kick


def shutter():
    t = np.arange(int(0.12 * SR)) / SR
    c = lambda d: lowpass(rng.standard_normal(len(t)), 6000) * np.exp(-np.maximum(0, t - d) * 120) * (t >= d)
    return 0.6 * c(0) + 0.5 * c(0.05)


def synpluck(f, d=0.3):
    t = np.arange(int(d * SR)) / SR
    y = (2 * ((f * t) % 1) - 1) + 0.5 * (2 * ((f * 1.005 * t) % 1) - 1)
    return lowpass(y, 2200) * np.exp(-t * 14) * np.minimum(1, t * 500)


ARP = [261.6, 329.6, 392.0, 523.3, 392.0, 329.6, 293.7, 392.0]


def house(d, bpm=124):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR)
    for i in range(int(d / b * 4) + 1):
        s = int(i * b / 4 * SR); parts = []
        if i % 4 == 0: parts.append(0.7 * kick(0.25))
        if i % 4 == 2: parts.append(0.25 * hat(0.06))
        if i % 2 == 1: parts.append(0.1 * hat(0.03))
        if i % 2 == 0: parts.append(0.18 * synpluck(ARP[(i // 2) % 8] * (1 if (i // 32) % 2 == 0 else 0.89)))
        for x in parts:
            out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 1.2)


def thud():
    t = np.arange(int(0.15 * SR)) / SR
    return np.sin(2 * np.pi * 140 * t * (1 - 0.3 * t)) * np.exp(-t * 28)


D = dict(h1=0.2, h2=1.2, c1=2.8, c2=3.6, k0=5.0, k1=5.8, k2=6.6, k3=7.4, print=8.8, p2=9.8, u0=11.4, u1=12.6, u2=13.8, brand=15.4, store=16.8, end_all=19.5)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.2 for k in ('c1', 'k0', 'print', 'u0', 'brand')]
    parts = [(0, 0.45 * house(dur)), (0.05, 0.5 * whoosh(0.5)), (T['h1'], 0.6 * thud()), (T['h2'], 0.5 * thud())]
    parts += [(c - 0.12, shutter()) for c in cuts]
    parts += [(T['c2'] - 0.1 + i * 0.28, 0.5 * tick(0.02)) for i in range(int((cuts[1] - T['c2']) / 0.28))]
    parts += [(T[k] - 0.15, 0.7 * thud()) for k in ('k0', 'k1', 'k2', 'k3')] + [(T[k] - 0.03, 0.5 * thud()) for k in ('k1', 'k2')]
    parts += [(cuts[2] + 0.1, 0.4 * whoosh(0.6)), (T['p2'] - 0.1, 0.4 * pen(0.6)), (T['p2'] + 0.1, 0.4 * pen(0.6)), (T['p2'] + 0.4, 0.4 * pop(0.1)), (T['p2'] + 0.6, 0.4 * pop(0.1))]
    parts += [(a, 0.5 * whoosh(0.4)) for a in (cuts[3] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2)] + [(a + 0.5, 0.6 * thud()) for a in (cuts[3] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2)]
    parts += [(cuts[4] + 0.2, 0.6 * thud()), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
