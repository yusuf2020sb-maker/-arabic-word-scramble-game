"""Score for reel 40 (classic vintage, old-cinema motion graphics): silent-film stride piano, projector rattle,
countdown beeps, colour-flood shimmer, film-gate clicks on each frame and a projector switch clunk.

usage: python3 sfx_reel40.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import rattle
from sfx_reel8 import clunk, tick
from sfx_reel22 import piano
from sfx_reel35 import beep

CH = [[130.8, 261.6, 329.6, 392.0], [174.6, 261.6, 349.2, 440.0], [98.0, 246.9, 293.7, 392.0], [130.8, 261.6, 329.6, 392.0]]
MEL = [523.3, 587.3, 659.3, 523.3, 784.0, 659.3, 587.3, 523.3, 440.0, 523.3, 587.3, 659.3, 587.3, 523.3, 493.9, 523.3]


def honky(f, d=0.5, a=0.3):
    return a * (piano(f, d) + 0.6 * piano(f * 1.006, d))


def stride(d, bpm=132):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 2)
    for i in range(int(d / b) + 1):
        ch = CH[(i // 4) % 4]; s = int(i * b * SR)
        x = honky(ch[0] if i % 2 == 0 else ch[0] * 2, 0.4, 0.35) if i % 2 == 0 else mix(*[(0, honky(f, 0.3, 0.16)) for f in ch[1:]])
        out[s:s + len(x)] += x[:len(out) - s]
        y = honky(MEL[i % 16], 0.35, 0.18); out[s:s + len(y)] += y[:len(out) - s]
    out = lowpass(out[:int(d * SR)], 3500); tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 1.2)


def whir(d):
    t = np.arange(int(d * SR)) / SR
    return 0.08 * lowpass(rng.standard_normal(len(t)), 1200) * (0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 24 * t)))


D = dict(h1=0.9, h2=2.2, k0=3.6, k1=4.4, k2=5.2, k3=6.4, k4=7.2, k5=8.0, count=9.6, n2=10.6, u0=12.2, u1=13.5, u2=14.8, print=16.4, brand=18.8, store=20.0, store2=20.6, end_all=23.2)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T['k0'] - 0.3] + [T[k] - 0.25 for k in ('count', 'u0', 'print', 'brand')]
    parts = [(0.8, 0.45 * stride(dur - 0.8)), (0, whir(dur)), (0, 0.5 * beep(1000, 0.12)), (0.27, 0.5 * beep(1000, 0.12)), (0.53, 0.5 * beep(1000, 0.12))]
    parts += [(T['h2'] - 0.1, 0.4 * whoosh(0.6)), (T['h2'] + 0.1, 0.5 * sparkle(0.9))]
    parts += [(cuts[0], 0.5 * rattle(0.6))] + [(T[k] - 0.1, 0.6 * tick(0.03)) for k in ('k0', 'k1', 'k2', 'k3', 'k4', 'k5')]
    parts += [(cuts[1] + 0.05, 0.8 * clunk()), (cuts[1] + 0.3, 0.4 * rattle(0.8))]
    parts += [(a, 0.5 * tick(0.03)) for a in (cuts[2] + 0.05, T['u1'] - 0.2, T['u2'] - 0.2)]
    parts += [(cuts[3] + 0.1, 0.4 * whoosh(0.5)), (cuts[4] + 0.1, 0.6 * clunk()), (T['store2'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
