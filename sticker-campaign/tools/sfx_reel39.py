"""Score for reel 39 (cozy autumn pop-up book): fingerpicked guitar lullaby with soft celesta, fireplace crackle,
page-flip swishes, paper pop-up flaps, a kettle whistle and a closing book thump.

usage: python3 sfx_reel39.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng
from sfx_reel13 import paper
from sfx_reel16 import crackle, page
from sfx_reel17 import pluck
from sfx_reel33 import whistle
from sfx_reel37 import celesta

G = [[196.0, 246.9, 293.7, 392.0], [164.8, 246.9, 329.6, 392.0], [130.8, 261.6, 329.6, 392.0], [146.8, 220.0, 293.7, 370.0]]


def lullaby(d, bpm=76):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2); pat = [0, 2, 3, 1, 2, 3]
    for i in range(int(d / e) + 1):
        ch = G[(i // 6) % 4]; s = int(i * e * SR)
        x = (0.5 if i % 6 == 0 else 0.25) * pluck(ch[pat[i % 6]], 1.4, 0.996); out[s:s + len(x)] += x[:len(out) - s]
        if i % 12 == 3:
            y = 0.1 * celesta(ch[3] * 2); out[s:s + len(y)] += y[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 1.4)


def flap():
    return mix((0, 0.6 * paper(0.12)), (0.06, 0.35 * pop(0.1)))


def thump():
    t = np.arange(int(0.3 * SR)) / SR
    return np.sin(2 * np.pi * 90 * t) * np.exp(-t * 18) + 0.4 * lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 30)


D = dict(h1=0.3, h2=1.2, k0=3.0, k1=5.4, count=7.8, n2=8.6, u0=10.4, u1=11.6, u2=12.8, print=14.4, brand=16.8, store=18.0, store2=18.6, end_all=21.2)


def main(out_path):
    T = D; dur = T['end_all']; opens = [0.2, T['k0'], T['k1'], T['count'], T['u0']]
    parts = [(0, 0.45 * lullaby(dur)), (0, 0.25 * crackle(dur))]
    parts += [(o - 0.6, 0.7 * page(0.55)) for o in opens[1:]]
    parts += [(o + j * 0.08 + 0.15, 0.5 * flap()) for o, n in zip(opens, [4, 3, 4, 12, 3]) for j in range(n)]
    parts += [(T['k0'] + 0.6, 0.3 * whistle(0.6))]
    parts += [(a + 0.2, 0.6 * flap()) for a in (T['u1'] - 0.15, T['u2'] - 0.15)]
    parts += [(T['print'] - 0.25, 0.6 * page(0.7)), (T['brand'] - 0.3, 0.8 * thump()), (T['store2'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
