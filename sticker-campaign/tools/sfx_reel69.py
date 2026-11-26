"""Reel 69 (night museum, vases pack) sound design: laser hum, power-down chirp, glass lift, gallery footsteps,
spotlight clunks, gold sparkle shine; soft string bed.

usage: python3 sfx_reel69.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, sparkle, whoosh
from sfx_reel22 import pad, piano
from sfx_reel64 import clunk
from sfx_reel65 import tick

D = {"h1": 0.3, "h1b": 1.1, "h2": 2.4, "c1": 4.4, "c2": 5.6, "c3": 6.8, "count": 8.4, "n2": 9.8, "u0": 11.4, "u1": 12.6, "u2": 13.8,
     "print": 15.4, "print2": 16.6, "brand": 18.8, "store": 20.4, "store2": 21.2, "end_all": 24.2}


def laser_hum(d):
    tt = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * 880 * tt) * 0.3 + np.sin(2 * np.pi * 1320 * tt) * 0.15) * (0.7 + 0.3 * np.sin(2 * np.pi * 6 * tt))


def chirp_down(d=0.4):
    tt = np.arange(int(d * SR)) / SR
    f = 1400 * np.exp(-tt * 6) + 200
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5)


def step():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    return lowpass(np.random.default_rng(3).uniform(-1, 1, n), 600) * np.exp(-tt * 30) * 2.5


def main(out_path):
    T = D; dur = T["end_all"]
    parts = [(0, 0.25 * laser_hum(T["h2"]) * np.minimum(1, np.arange(int(T["h2"] * SR)) / SR / 0.3)), (T["h2"], 0.6 * chirp_down()), (T["h2"] + 0.1, 0.4 * whoosh(0.6))]
    parts += [(T["h2"] + 0.3, 0.3 * pad((146.8, 220, 293.7, 370), dur - T["h2"] - 0.3))]
    for k in (T["c2"], T["c3"]):
        parts += [(k - 0.35 + i * 0.15, 0.35 * step()) for i in range(3)]
    parts += [(T["c1"] - 0.35 + i * 0.15, 0.35 * step()) for i in range(3)]
    parts += [(T["count"] - 0.1 + i * 0.07, 0.25 * tick()) for i in range(16)]
    parts += [(T["n2"], 0.5 * sparkle(0.9))]
    for u in (T["u0"], T["u1"], T["u2"]):
        parts += [(u - 0.1, 0.6 * clunk())]
    parts += [(T["print"] - 0.3, 0.3 * whoosh(0.4)), (T["print2"] - 0.2, 0.4 * whoosh(0.6)), (T["brand"] - 0.3, 0.5 * clunk())]
    parts += [(T["store2"], 0.45 * chime(1.4)), (T["store2"] + 0.05, 0.4 * mix(*[(j * 0.16, piano(f)) for j, f in enumerate((587, 740, 880, 1174))]))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
