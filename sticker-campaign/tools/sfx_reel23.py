"""Score for reel 23 (vintage botanical): harp waltz bed, drips, peel, bloom pops, page turns, presses.

usage: python3 sfx_reel23.py <out.wav>            (silent cut, default timeline)
       import: drip, harp_gliss, bloom, press, inkswell, waltz
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel16 import page
from sfx_reel17 import pluck
from sfx_reel20 import peel

C = [261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 493.9]
CHORDS = [[130.8, 261.6, 329.6, 392.0], [174.6, 261.6, 349.2, 440.0], [110.0, 261.6, 329.6, 440.0], [98.0, 246.9, 293.7, 392.0]]


def drip(f=900):
    t = np.arange(int(0.25 * SR)) / SR
    sweep = f * (1 + 1.6 * np.exp(-t * 30))
    return np.sin(2 * np.pi * np.cumsum(sweep) / SR) * np.exp(-t * 22)


def harp_gliss(up=True, n=12, step=0.045):
    notes = [f * o for o in (1, 2) for f in C][:n]
    notes = notes if up else notes[::-1]
    return mix(*[(i * step, 0.5 * pluck(f, 1.4)) for i, f in enumerate(notes)])


def bloom(i):
    t = np.arange(int(0.18 * SR)) / SR
    f = 500 * 2 ** (i / 12)
    return np.sin(2 * np.pi * f * t * (1 + 0.3 * np.exp(-t * 40))) * np.exp(-t * 28) * np.minimum(1, t * 400)


def press():
    t = np.arange(int(0.16 * SR)) / SR
    thud = np.sin(2 * np.pi * 120 * t) * np.exp(-t * 35)
    tick = lowpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 90) * 0.5
    return thud + tick


def inkswell(d=0.7):
    t = np.arange(int(d * SR)) / SR
    x = lowpass(rng.standard_normal(len(t)), 1800) * (t / d) ** 2
    return x * np.minimum(1, (d - t) * 40)


def waltz(d, bpm=96):
    beat = 60 / bpm; out = np.zeros(int(d * SR) + SR * 2); b = 0
    while b * beat < d:
        ch = CHORDS[(b // 6) % 4]
        f = ch[0] if b % 3 == 0 else ch[1 + (b % 3)]
        x = (0.55 if b % 3 == 0 else 0.3) * pluck(f, 1.6, 0.997)
        s = int(b * beat * SR); out[s:s + len(x)] += x[:len(out) - s]
        if b % 6 == 3:
            y = 0.18 * pluck(ch[3] * 2, 1.2); out[s:s + len(y)] += y[:len(out) - s]
        b += 1
    out = out[:int(d * SR)]
    return out * np.minimum(1, np.arange(len(out)) / SR / 1.0) * np.minimum(1, (d - np.arange(len(out)) / SR) / 1.5)


# default (silent) timeline, mirrors D in reel23.html
D = dict(h1=0.25, h2=1.0, h3=2.2, rev=3.6, count=6.4, kinds=10.4, k2=12.3, k3=13.3, k4=14.3, u0=15.6, u1=17.1, u2=18.6, print=20.2, brand=23.0, store=24.4, end_all=27.0)


def main(out_path):
    T = D; dur = T['end_all']
    cuts = [T[k] - 0.15 for k in ('count', 'kinds', 'u0', 'print', 'brand')]
    parts = [(0, 0.35 * waltz(dur)), (0.05, 0.5 * harp_gliss())]
    parts += [(T['h2'] + 0.6 + i * 0.28, 0.35 * drip(800 + i * 90)) for i in range(5)]
    parts += [(T['rev'] - 0.1, 1.2 * peel(0.5)), (T['rev'] + 0.3, 0.8 * sparkle(0.9)), (T['rev'] + 0.35, 0.4 * press())]
    parts += [(c - 0.5, 0.45 * whoosh(0.8)) for c in cuts]
    parts += [(cuts[0] + 0.15 + i * 0.045, 0.22 * bloom(i % 24)) for i in range(34)]
    parts += [(a, 0.9 * page(0.5)) for a in (T['kinds'] + 0.05, T['k2'] - 0.25, T['k3'] - 0.25, T['k4'] - 0.25)]
    for a in (T['u1'] - 0.2, T['u2'] - 0.2):
        parts.append((a - 0.3, 0.5 * inkswell()))
    for a in (cuts[2], T['u1'] - 0.2, T['u2'] - 0.2):
        parts += [(a + 0.5 + j * 0.3 + 0.3, 0.7 * press()) for j in range(3)]
    parts += [(cuts[3] + 0.1, 0.7 * page(0.7)), (cuts[3] + 1.2, 0.4 * chime(0.8))]
    parts += [(cuts[4] + 0.1 + i * 0.07, 0.18 * bloom(12 + i % 12)) for i in range(16)]
    parts += [(cuts[4] + 0.9, 0.5 * harp_gliss(False)), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
