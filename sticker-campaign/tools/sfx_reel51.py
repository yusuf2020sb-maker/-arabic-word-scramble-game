"""Reel 51 score: bubbly vending-machine pop (marimba + soft bass + snaps), button beeps, coil whirs, item thunks, neon buzz and a cha-ching.

usage: python3 sfx_reel51.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, sparkle
from sfx_reel20 import hat, kick

CH = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
BASS = [130.8, 110.0, 87.3, 98.0]


def marimba(f, d=0.5):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)) * np.exp(-t * 9) * np.minimum(1, t / 0.002)


def bop(d, bpm=112):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR)
    for i in range(int(d / e) + 1):
        bar = (i // 8) % 4; s = int(i * e * SR)
        m = 0.22 * marimba(CH[bar][[0, 1, 2, 1, 2, 0, 1, 2][i % 8]] * 2); out[s:s + len(m)] += m[:len(out) - s]
        if i % 4 == 0:
            k = 0.35 * kick(); out[s:s + len(k)] += k[:len(out) - s]
            t2 = np.arange(int(0.4 * SR)) / SR; b = 0.25 * np.sin(2 * np.pi * BASS[bar] * t2) * np.exp(-t2 * 5); out[s:s + len(b)] += b[:len(out) - s]
        if i % 4 == 2:
            h = 0.15 * hat(0.08); out[s:s + len(h)] += h[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 1.2)


def beep(f=1500, d=0.09):
    t = np.arange(int(d * SR)) / SR
    return 0.5 * np.sign(np.sin(2 * np.pi * f * t)) * np.minimum(1, (d - t) / 0.01) * 0.5


def whir(d=0.3):
    t = np.arange(int(d * SR)) / SR
    return 0.4 * np.sin(2 * np.pi * (120 + 40 * np.sin(2 * np.pi * 18 * t)) * t) * np.sin(np.pi * t / d) + 0.1 * lowpass(rng.standard_normal(len(t)), 1500)


def thunk(d=0.3):
    t = np.arange(int(d * SR)) / SR
    return 0.8 * np.sin(2 * np.pi * (80 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 16) + 0.3 * lowpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 40)


def buzz(d=0.25):
    t = np.arange(int(d * SR)) / SR
    return 0.2 * np.sign(np.sin(2 * np.pi * 120 * t)) * (rng.random(len(t)) > 0.3) * np.sin(np.pi * t / d)


def ching():
    return mix((0, 0.6 * chime(1.0)), (0.08, 0.5 * sparkle(0.5)), (0, 0.4 * thunk(0.15)))


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * bop(dur)), (T['h1'], buzz()), (T['h2'], buzz()), (0.6, 0.3 * beep(1200))]
    for k in ('c1', 'c2', 'c3'):
        parts += [(T[k] - 0.6, beep(1500)), (T[k] - 0.4, whir(0.25)), (T[k] + 0.2, thunk()), (T[k] + 0.25, 0.4 * pop())]
    parts += [(cut[1] + 0.2 + i * 0.12, 0.2 * pop(0.08)) for i in range(10)] + [(cut[1] + 0.1, buzz()), (T['n2'], 0.4 * beep(1800))]
    parts += [(cut[2] - 0.2, 0.5 * whir(0.5))] + [(a + 0.3, 0.4 * pop()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)] + [(cut[3] - 0.2, 0.5 * whir(0.5))]
    parts += [(cut[3] + 0.3, 0.6 * whir(0.9)), (T['print2'], 0.4 * beep(1800))]
    parts += [(cut[4], buzz()), (cut[4] + 0.3, 0.5 * pop()), (T['store'], 0.4 * beep(1500)), (T['store2'] - 0.1, buzz()), (T['store2'], ching())]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
