"""Reel 68 (flashlight in the dark, ephemera pack) sound design: torch click, power-down drone, beam swishes,
fluorescent flicker when the power comes back, paper pops, music-box chime at the end.

usage: python3 sfx_reel68.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel18 import clack
from sfx_reel22 import pad, piano

D = {"h1": 0.3, "h2": 1.9, "c1": 3.8, "c2": 5.0, "c3": 6.2, "count": 7.8, "n2": 9.4, "u0": 11.0, "u1": 12.2, "u2": 13.4,
     "print": 15.0, "print2": 16.2, "brand": 18.2, "store": 19.8, "store2": 20.6, "end_all": 23.6}


def powerdown(d=0.9):
    tt = np.arange(int(d * SR)) / SR
    f = 120 * np.exp(-tt * 1.6) + 30
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.5) * 0.8


def flicker(d=0.5):
    tt = np.arange(int(d * SR)) / SR
    gate = np.array([[1, 0, 1, 0, 1][min(4, int(x / d * 5))] for x in tt])
    hum = np.sin(2 * np.pi * 100 * tt) + 0.5 * np.sin(2 * np.pi * 200 * tt) + 0.3 * rng.uniform(-1, 1, len(tt))
    return hum * gate * 0.5


def swish(d=0.35):
    n = int(d * SR); tt = np.arange(n) / SR
    return (rng.uniform(-1, 1, n) - lowpass(rng.uniform(-1, 1, n), 2500)) * np.sin(np.pi * tt / d) ** 2


def music_box(notes, gap=0.18):
    return mix(*[(i * gap, 0.6 * piano(f * 2, 1.4)) for i, f in enumerate(notes)])


def main(out_path):
    T = D; dur = T["end_all"]
    parts = [(0, 0.7 * powerdown()), (0.05, 0.8 * clack()), (0.2, 0.25 * pad((110, 130.8, 164.8), dur - 0.2))]
    parts += [(T["h2"] + 0.2 + i * 0.4, 0.35 * swish()) for i in range(3)]
    for c in (T["c1"], T["c2"], T["c3"]):
        parts += [(c - 0.25, 0.4 * swish(0.3)), (c, 0.3 * pop())]
    parts += [(T["count"] - 0.25, 0.8 * flicker()), (T["count"] - 0.25, 0.5 * clack())]
    parts += [(T["count"] + 0.05 + i * 0.05, 0.12 * pop()) for i in range(16)]
    parts += [(T["n2"] - 0.1 + i * 0.16, 0.3 * piano([523, 587, 659, 784, 880][i], 0.6)) for i in range(5)]
    parts += [(T["u0"] - 0.35, 0.6 * clack()), (T["u0"] - 0.3, 0.4 * powerdown(0.5))]
    for u in (T["u0"], T["u1"], T["u2"], T["print"]):
        parts += [(u - 0.25, 0.35 * swish(0.3))]
    parts += [(T["print2"] - 0.1, 0.7 * flicker(0.5)), (T["print2"] + 0.3, 0.3 * whoosh(0.4)), (T["brand"] - 0.35, 0.6 * clack())]
    parts += [(T["store2"], 0.4 * chime(1.4)), (T["store2"] + 0.1, 0.5 * music_box((523, 659, 784, 1046, 784)))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
