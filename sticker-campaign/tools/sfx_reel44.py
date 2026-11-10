"""Reel 44 score: retro-computer chiptune, error bonks, mouse clicks, window blips, printer buzz and a success jingle.

usage: python3 sfx_reel44.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, lowpass, mix, norm, rng


def sq(f, d, duty=0.5, dec=6.0):
    t = np.arange(int(d * SR)) / SR
    return np.where((f * t) % 1 < duty, 1.0, -1.0) * np.exp(-t * dec) * np.minimum(1, t / 0.004)


def tri(f, d):
    t = np.arange(int(d * SR)) / SR
    return (2 * np.abs(2 * ((f * t) % 1) - 1) - 1) * np.minimum(1, (d - t) / 0.02)


# i - VI - III - VII in A minor, 8-bit style
BASS = [110.0, 87.3, 130.8, 98.0]
ARP = [[440.0, 523.3, 659.3], [349.2, 440.0, 523.3], [523.3, 659.3, 784.0], [392.0, 493.9, 587.3]]


def chip(d, bpm=112):
    s16 = 60 / bpm / 4; out = np.zeros(int(d * SR) + SR)
    for i in range(int(d / s16) + 1):
        bar = (i // 16) % 4; s = int(i * s16 * SR)
        a = 0.10 * sq(ARP[bar][i % 3], s16 * 0.9, 0.25, 9); out[s:s + len(a)] += a[:len(out) - s]
        if i % 4 == 0:
            b = 0.22 * tri(BASS[bar], s16 * 3.5); out[s:s + len(b)] += b[:len(out) - s]
        if i % 8 == 4:
            n = int(0.05 * SR); z = 0.12 * rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 60); out[s:s + n] += z[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return lowpass(out, 7000) * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 1.0)


def bonk():
    # error buzzer: two low square notes
    return mix((0, 0.6 * sq(196, 0.18, 0.5, 4)), (0.17, 0.6 * sq(147, 0.3, 0.5, 4)))


def click():
    n = int(0.03 * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 4000) * np.exp(-t * 300) + 0.4 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 200)


def blip(f=880):
    return 0.5 * mix((0, sq(f, 0.06, 0.5, 30)), (0.05, sq(f * 1.5, 0.08, 0.5, 30)))


def steps(n=8, d=0.45, f=1200):
    # stepped type-in: tiny ticks, one per step
    return mix(*[(i * d / n, 0.25 * sq(f + i * 30, 0.02, 0.5, 120)) for i in range(n)])


def buzz(d=1.0):
    t = np.arange(int(d * SR)) / SR
    return 0.3 * np.where((90 * t) % 1 < 0.5, 1.0, -1.0) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 6 * t))) * np.minimum(1, (d - t) / 0.05)


def tada():
    return mix(*[(i * 0.11, 0.5 * sq(f, 0.5 if i == 3 else 0.12, 0.5, 5)) for i, f in enumerate([523.3, 659.3, 784.0, 1046.5])])


D = dict(h1=0.3, h2=1.3, q=3.0, a=3.8, c1=5.6, c2=7.0, c3=8.6, count=10.4, n2=11.6, u0=13.2, u1=14.2, u2=15.2, print=16.8, print2=17.8, brand=19.4, store=20.8, store2=21.5, end_all=24.2)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['q'] - 0.35, T['c1'] - 0.35, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.55 * chip(dur)), (0.05, bonk()), (T['h1'], steps()), (T['h2'], steps()), (T['h2'] + 0.7, click())]
    parts += [(T['h2'] + 0.6 + i * 0.12, 0.6 * bonk()[:int(0.12 * SR)]) for i in range(7)]
    parts += [(cut[0], blip(700)), (T['q'] - 0.05, steps(6, 0.35)), (T['a'] - 0.05, click()), (T['a'] - 0.2, blip(900)), (T['a'], steps(8, 0.6))]
    parts += [(T['a'] + 0.2 + i * 0.1, 0.3 * sq(1500, 0.02, 0.5, 120)) for i in range(int((cut[1] - 0.25 - T['a'] - 0.2) / 0.1))]
    parts += [(T[k] - 0.25, click()) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.25, blip(800 + 120 * i)) for i, k in enumerate(('c1', 'c2', 'c3'))]
    parts += [(cut[2], blip(700))] + [(cut[2] + 0.25 + i * 0.04, 0.2 * sq(2000 + i * 40, 0.015, 0.5, 150)) for i in range(20)] + [(cut[2] + 0.35, blip(1000)), (T['n2'], steps())]
    parts += [(T[k] - 0.25, click()) for k in ('u0', 'u1', 'u2')] + [(T[k] - 0.25, blip(900 + 100 * i)) for i, k in enumerate(('u0', 'u1', 'u2'))]
    parts += [(T['print'] - 0.2, click()), (cut[4], blip(700)), (T['print'] + 0.2, buzz(T['print2'] + 0.4 - T['print']))]
    parts += [(cut[5], blip(1000)), (T['brand'], steps(8, 0.55)), (T['store2'] - 0.05, click()), (T['store2'], tada())]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
