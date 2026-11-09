"""Score for reel 36 (stamps factory motion graphics): quirky marimba + woodblock factory groove,
conveyor hum, printer, perforation punches, postmark thud, bells and pops.

usage: python3 sfx_reel36.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel5 import printer
from sfx_reel8 import clunk
from sfx_reel9 import stamp_thud
from sfx_reel18 import bell
from sfx_reel25 import punch

SC = [261.6, 293.7, 329.6, 392.0, 440.0, 523.3]
MEL = [0, 2, 4, 2, 3, 1, 0, 5, 4, 2, 3, 4, 2, 1, 0, 0]


def marimba(f, d=0.35):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 40)) * np.exp(-t * 9) * np.minimum(1, t * 800)


def block(f=900):
    t = np.arange(int(0.06 * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 70)


def hum(d):
    t = np.arange(int(d * SR)) / SR
    return 0.12 * lowpass(np.sign(np.sin(2 * np.pi * 50 * t)), 300) * (0.8 + 0.2 * np.sin(2 * np.pi * 4 * t))


def factory(d, bpm=120):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR)
    for i in range(int(d / e) + 1):
        s = int(i * e * SR); parts = [0.25 * block(1200 if i % 2 else 800)]
        if i % 2 == 0: parts.append(0.3 * marimba(SC[MEL[(i // 2) % 16]]))
        if i % 4 == 0: parts.append(0.35 * marimba(SC[MEL[(i // 2) % 16]] / 2, 0.5))
        for x in parts:
            out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 1.2)


D = dict(h1=0.2, h1b=0.9, k0=3.4, k1=4.9, k2=6.4, count=8.2, n2=9.0, q0=10.8, q1=11.6, q2=12.4, u0=14.0, u1=15.3, u2=16.6, print=18.2, brand=20.6, store=21.8, store2=22.4, end_all=25.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T['k0'] - 0.6] + [T[k] - 0.25 for k in ('count', 'q0', 'u0', 'print', 'brand')]
    parts = [(0, 0.42 * factory(dur)), (cuts[0], hum(cuts[1] - cuts[0])), (T['h1'], 0.5 * clunk()), (T['h1b'], 0.6 * clunk())]
    parts += [(c - 0.3, 0.5 * whoosh(0.6)) for c in cuts]
    parts += [(T['k0'] - 0.1, 0.6 * printer(0.7)), (T['k0'] - 0.2, 0.3 * bell())]
    parts += [(T['k1'] - 0.05 + i * 0.07, 0.5 * punch()) for i in range(4)]
    parts += [(T['k2'], 1.0 * stamp_thud()), (T['k2'] + 0.3, 0.4 * clunk())]
    parts += [(cuts[1] + 0.2 + i * 0.07, 0.3 * pop(0.1)) for i in range(14)]
    parts += [(T[k] - 0.15, 0.5 * whoosh(0.35)) for k in ('q0', 'q1', 'q2')]
    parts += [(a + 0.55, 0.8 * stamp_thud()) for a in (cuts[3] + 0.1, T['u1'] - 0.25, T['u2'] - 0.25)]
    parts += [(cuts[4] + 0.1, 0.5 * printer(0.8)), (cuts[5] + 0.3, 0.6 * stamp_thud()), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
