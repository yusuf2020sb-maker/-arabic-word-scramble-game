"""Score for reel 29 (autumn motion graphics): punchy 120 bpm beat with bass, slams, pops, zips and swooshes.

usage: python3 sfx_reel29.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, sparkle, whoosh
from sfx_reel5 import boing
from sfx_reel9 import zip_sweep
from sfx_reel10 import boom
from sfx_reel20 import hat, kick


def snare():
    t = np.arange(int(0.18 * SR)) / SR
    return 0.6 * lowpass(rng.standard_normal(len(t)), 6000) * np.exp(-t * 22) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)


def bass(f, d):
    t = np.arange(int(d * SR)) / SR
    return lowpass(np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * t), 500) * np.exp(-t * 3) * np.minimum(1, t * 300)


def beat(d, bpm=120):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR); BL = [55.0, 55.0, 65.4, 49.0]
    for i in range(int(d / b * 2) + 1):
        s = int(i * b / 2 * SR)
        parts = []
        if i % 4 == 0: parts.append(0.8 * kick(0.3))
        if i % 4 == 2: parts.append(0.5 * snare())
        parts.append(0.18 * hat(0.04))
        if i % 2 == 0: parts.append(0.35 * bass(BL[(i // 8) % 4], b * 0.9))
        for x in parts:
            out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.2) * np.minimum(1, (d - tt) / 1.0)


def slam():
    return mix((0, 0.9 * boom(0.5)), (0, 0.5 * snare()))


D = dict(h1=0.15, h2=1.0, j1=2.7, j2=3.8, count=5.2, k0=8.2, k1=9.2, k2=10.2, s0=11.4, s1=12.2, s2=13.0, u0=14.4, u1=15.6, u2=16.8, brand=18.2, store=19.6, end_all=22.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.2 for k in ('j1', 'count', 'k0', 's0', 'u0', 'brand')]
    parts = [(0, 0.45 * beat(dur)), (T['h1'], slam()), (T['h2'], 0.6 * boing(0.4)), (T['h2'] + 0.05, 0.5 * sparkle(0.6))]
    parts += [(c - 0.1, 0.6 * whoosh(0.45)) for c in cuts]
    parts += [(T['j1'], 0.4 * whoosh(0.3)), (cuts[0] + 0.15, 0.5 * pop(0.12)), (cuts[0] + 0.8, 0.5 * boing(0.35)), (T['j2'] - 0.05, slam())]
    parts += [(cuts[1] + 0.2, 0.6 * zip_sweep(0.5)), (cuts[1] + 0.7, 0.6 * zip_sweep(0.45)), (cuts[1] + 0.7, slam())]
    parts += [(cuts[1] + 1.1 + i * 0.06, 0.3 * pop(0.1)) for i in range(12)]
    parts += [(a - 0.15, 0.5 * whoosh(0.35)) for a in (T['k0'], T['k1'], T['k2'])] + [(a + 0.25, 0.5 * pop(0.14)) for a in (T['k0'], T['k1'], T['k2'])]
    parts += [(a - 0.1, 0.6 * boing(0.35)) for a in (T['s0'], T['s1'], T['s2'])]
    parts += [(a + 0.1, 0.4 * slam()) for a in (cuts[4] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2)]
    parts += [(a + 0.35 + j * 0.18, 0.35 * pop(0.1)) for a in (cuts[4] + 0.1, T['u1'] - 0.2, T['u2'] - 0.2) for j in range(3)]
    parts += [(cuts[5] + 0.15, slam()), (cuts[5] + 0.5, 0.5 * sparkle(0.8)), (T['store'], 0.7 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
