"""Reel 43 score: cozy acoustic plucks, card swipes, 'like' dings, card deals and a match chime.

usage: python3 sfx_reel43.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, sparkle, whoosh
from sfx_reel8 import tick
from sfx_reel17 import pluck
from sfx_reel20 import kick
from sfx_reel22 import pad

# I - vi - IV - V in D, played as gentle finger-picked arpeggios
CH = [[146.8, 220.0, 293.7, 370.0], [123.5, 185.0, 246.9, 293.7], [98.0, 196.0, 246.9, 293.7], [110.0, 220.0, 277.2, 329.6]]


def cozy(d, bpm=88):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2)
    order = [0, 2, 1, 3, 2, 1, 3, 2]
    for i in range(int(d / e) + 1):
        bar = (i // 8) % 4; s = int(i * e * SR); f = CH[bar][order[i % 8]]
        x = 0.35 * pluck(f, 0.9, 0.995); out[s:s + len(x)] += x[:len(out) - s]
        if i % 8 == 0:
            z = 0.05 * lowpass(pad(CH[bar], 8 * e + 0.3), 900); out[s:s + len(z)] += z[:len(out) - s]
            k = 0.18 * kick(); out[s:s + len(k)] += k[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.2)


def swipe(d=0.35):
    # quick airy flick of a card
    return lowpass(whoosh(d), 5000) * 0.9


def like(f=1320):
    # two-note 'liked' ding
    t = np.arange(int(0.35 * SR)) / SR
    a = np.sin(2 * np.pi * f * t) * np.exp(-t * 14)
    return mix((0, 0.6 * a), (0.08, 0.6 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 14)))


def deal(d=0.07):
    # card snapping onto the table
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 3000) * np.exp(-t * 70) * 0.8


def flip(d=0.4):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 2500) * np.sin(np.pi * t) ** 2 * 0.5


D = dict(h1=0.3, h2=1.6, c1=3.2, c2=4.4, c3=5.6, c4=6.8, count=8.6, n2=9.9, u0=11.6, u1=12.8, u2=14.0, print=15.8, print2=16.8, brand=18.6, store=20.0, store2=20.7, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.45, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    outs = [T['c1'] - 0.45, T['c2'] - 0.35, T['c3'] - 0.35, T['c4'] - 0.35, cut[1] - 0.05]
    parts = [(0, 0.5 * cozy(dur)), (0.0, 0.5 * swipe(0.5)), (T['h1'], 0.4 * pop()), (T['h2'], 0.6 * pop()), (T['h2'] + 0.05, 0.4 * sparkle())]
    parts += [(s, swipe()) for s in outs] + [(s - 0.2, 0.5 * like(1320 + 110 * i)) for i, s in enumerate(outs)]
    parts += [(s + 0.4, 0.35 * pop(0.1)) for s in outs[1:]]
    parts += [(cut[1] + 0.15 + i * 0.07, 0.25 * tick()) for i in range(16)] + [(cut[1] + 0.3 + i * 0.05, 0.5 * deal()) for i in range(15)]
    parts += [(cut[1] + 0.5, 0.5 * pop()), (T['n2'], 0.3 * sparkle())]
    parts += [(cut[2], 0.8 * swipe(0.45)), (T['u1'] - 0.3, 0.8 * swipe(0.45)), (T['u2'] - 0.3, 0.8 * swipe(0.45))]
    parts += [(a + 0.25 + j * 0.15, 0.3 * pop(0.1)) for a in (cut[2] + 0.05, T['u1'] - 0.3, T['u2'] - 0.3) for j in range(3)]
    parts += [(cut[3], 0.4 * pop()), (T['print2'] - 0.35, flip()), (T['print2'] + 0.2, 0.5 * sparkle())]
    parts += [(cut[4] + 0.05, 0.7 * swipe(0.5)), (cut[4] + 0.55, 0.8 * deal(0.1)), (cut[4] + 0.6, 0.6 * like(1480)), (cut[4] + 0.65, 0.4 * sparkle(0.6))]
    parts += [(T['store2'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
