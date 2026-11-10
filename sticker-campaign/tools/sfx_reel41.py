"""Score for reel 41 (majlis heritage, fireworks motion graphics): festive zaffa-style drums and claps with a bright
bell melody in Hijaz, firework whistles, booms and crackles, sparkler fizz on text.

usage: python3 sfx_reel41.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle
from sfx_reel10 import boom
from sfx_reel16 import crackle
from sfx_reel17 import HIJAZ
from sfx_reel27 import daf
from sfx_reel28 import clap

MEL = [4, 5, 6, 5, 4, 3, 2, 3, 4, 2, 1, 0, 1, 2, 3, 4]


def bell(f, d=0.5):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 10)) * np.exp(-t * 6) * np.minimum(1, t * 800)


def zaffa(d, bpm=112):
    s8 = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2)
    for i in range(int(d / s8) + 1):
        s = int(i * s8 * SR); parts = []
        if i % 8 in (0, 3): parts.append(0.6 * daf(True))
        if i % 8 in (2, 6): parts.append(0.4 * clap())
        if i % 8 in (5, 7): parts.append(0.3 * daf(False))
        if i % 2 == 0: parts.append(0.25 * bell(HIJAZ[MEL[(i // 2) % 16]] * 2))
        for x in parts:
            out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.4) * np.minimum(1, (d - tt) / 1.3)


def whistle_up(d=0.45):
    t = np.arange(int(d * SR)) / SR
    f = 900 + 1600 * (t / d)
    return 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) + 0.1 * lowpass(rng.standard_normal(len(t)), 4000) * (t / d)


def fizz(d=0.6):
    t = np.arange(int(d * SR)) / SR
    return 0.3 * lowpass(rng.standard_normal(len(t)), 9000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 30 * t))) * np.sin(np.pi * t / d)


def firework(s=1.0):
    return mix((0, whistle_up()), (0.45, 0.8 * s * boom(0.9)), (0.5, 0.35 * crackle(1.0)))


D = dict(h1=0.2, h2=1.5, a0=2.9, a1=3.7, a2=4.5, b0=5.7, b1=6.5, b2=7.3, title=8.7, t2=9.9, u0=11.5, u1=12.7, u2=13.9, print=15.5, brand=17.9, store=19.1, store2=19.7, end_all=22.3)


def main(out_path):
    T = D; dur = T['end_all']
    bursts = [0.15, 0.6, T['h2'] - 0.15, T['h2'] + 0.3, T['h2'] + 0.5] + [T[k] - 0.2 for k in ('a0', 'a1', 'a2', 'b0', 'b1', 'b2')] + [T['title'] - 0.25, T['title'] + 0.1, T['t2'] - 0.1] + [T[k] + 0.1 for k in ('u0', 'u1', 'u2')] + [T['brand'] - 0.25, T['brand'] + 0.2, T['store2'] - 0.1, T['store2'] + 0.3]
    parts = [(0, 0.42 * zaffa(dur))] + [(max(0.0, b - 0.45), 0.55 * firework()) for b in bursts]
    parts += [(a, 0.5 * fizz(0.6)) for a in (T['h1'], T['h2'], T['title'], T['t2'], T['brand'])]
    parts += [(T['store2'], 0.6 * chime(1.4)), (T['store2'], 0.4 * sparkle(1.0))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
