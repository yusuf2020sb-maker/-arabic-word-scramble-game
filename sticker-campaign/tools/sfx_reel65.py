"""Reel 65 (bakery oven) sound design: timer ticks, oven ding, door clunk, steam hiss, pops, peel; café jazz bed.

usage: python3 sfx_reel65.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel18 import bell, tear
from sfx_reel42 import jazz
from sfx_reel64 import clunk

D = {"h1": 0.3, "h2": 2.0, "c1": 4.0, "c2": 5.1, "c3": 6.2, "count": 7.8, "n2": 9.4, "u0": 11.2, "u1": 12.6, "u2": 14.0,
     "print": 15.6, "print2": 16.7, "brand": 18.8, "store": 20.4, "store2": 21.2, "end_all": 24.2}


def tick(d=0.03):
    n = int(d * SR); tt = np.arange(n) / SR
    return (rng.uniform(-1, 1, n) * 0.5 + np.sin(2 * np.pi * 3200 * tt)) * np.exp(-tt * 260)


def ding():
    n = int(1.4 * SR); tt = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * k) for f, a, k in ((1760, 1, 3), (2640, 0.5, 5), (4400, 0.25, 8)))


def hiss(d=1.0):
    n = int(d * SR); tt = np.arange(n) / SR
    x = rng.uniform(-1, 1, n) - lowpass(rng.uniform(-1, 1, n), 2500)
    return x * np.minimum(1, tt / 0.08) * np.exp(-tt * 2.2)


def ticking(d):
    return mix(*[(i * 0.25, 0.35 * tick()) for i in range(int(d / 0.25))])


def main(out_path):
    T = D; dur = T["end_all"]
    parts = [(0, ticking(T["h2"] - 0.05)), (T["h2"] - 0.05, 0.7 * ding()), (T["h2"] + 0.35, 0.9 * clunk()), (T["h2"] + 0.4, 0.6 * hiss(1.4)),
             (T["h2"] + 0.5, 0.5 * whoosh(0.6)), (T["h2"] + 0.2, 0.55 * jazz(dur - T["h2"] - 0.2))]
    for k in (T["c1"], T["c2"], T["c3"]):
        parts += [(k - 0.3, 0.35 * whoosh(0.3)), (k - 0.05, 0.5 * pop())]
    for w in (T["count"], T["u0"], T["u1"], T["u2"], T["print"], T["brand"]):
        parts += [(w - 0.5, 0.45 * hiss(0.6)), (w - 0.4, 0.4 * whoosh(0.4))]
    parts += [(T["count"] - 0.1 + i * 0.07, 0.2 * pop()) for i in range(12)]
    parts += [(T["print2"] - 0.1, 0.6 * tear()), (T["brand"] + 0.1, 0.4 * clunk()), (T["store2"], 0.45 * chime(1.4)), (T["store2"] + 0.3, 0.35 * bell())]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
