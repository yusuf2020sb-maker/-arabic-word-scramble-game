"""Reel 67 (dark explainer line, botanical pack) sound design: soft ambient pad, glassy taps when the dot lands,
a sinking "wilt" tone for the real flower, petal ticks, tiny pops for stickers, piano chime at the end.

usage: python3 sfx_reel67.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel22 import pad, piano

D = {"h1": 0.3, "h1b": 1.3, "h2": 2.6, "c1": 4.2, "c2": 5.0, "c3": 5.8, "count": 7.0, "n2": 8.6, "u0": 10.0, "u1": 11.0, "u2": 12.0,
     "print": 13.8, "print2": 15.0, "brand": 17.2, "store": 18.8, "store2": 19.6, "end_all": 22.8}


def tap(f=1320, d=0.5):
    tt = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.01 * tt)) * np.exp(-tt * 14) * np.minimum(1, tt * 800)


def swish(d=0.3):
    n = int(d * SR); tt = np.arange(n) / SR
    x = rng.uniform(-1, 1, n) - lowpass(rng.uniform(-1, 1, n), 1800)
    return x * np.sin(np.pi * tt / d) ** 2


def wilt(d=1.4):
    tt = np.arange(int(d * SR)) / SR
    f = 660 * np.exp(-tt * 0.9)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt * 20) * np.exp(-tt * 1.6) * 0.6


def ambient(d):
    chords = [(110, 164.8, 220, 277.2), (98, 146.8, 196, 246.9), (87.3, 130.8, 174.6, 261.6), (98, 146.8, 196, 293.7)]
    seg = d / 4
    return mix(*[(i * seg * 0.97, pad(c, seg + 0.8)) for i, c in enumerate(chords)])


def main(out_path):
    T = D; dur = T["end_all"]
    parts = [(0, 0.35 * ambient(dur)), (0.05, 0.4 * tap(990))]
    parts += [(T["h1"] + i * 0.33, 0.3 * tap(1760, 0.25)) for i in range(3)]
    parts += [(T["h1b"] - 0.15, 0.5 * wilt()), (T["h1b"] + 0.4, 0.3 * tap(2093, 0.3)), (T["h1b"] + 0.6, 0.3 * tap(1760, 0.3)), (T["h2"] - 0.3, 0.5 * tap(1568))]
    for i, k in enumerate((T["c1"], T["c2"], T["c3"])):
        parts += [(k - 0.1, 0.5 * tap([880, 1046, 1318][i]))]
    parts += [(T["count"] + 0.1 + i * 0.09, 0.18 * pop()) for i in range(12)]
    for i, u in enumerate((T["u0"], T["u1"], T["u2"])):
        parts += [(u - 0.05, 0.45 * tap([1174, 1318, 1568][i])), (u, 0.2 * pop())]
    for w in (T["h2"], T["c1"], T["count"], T["u0"], T["print"], T["brand"]):
        parts += [(w - 0.45, 0.25 * whoosh(0.45))]
    parts += [(T["print"], 0.45 * tap(1568)), (T["print2"] + 0.15, 0.2 * pop()), (T["print2"] + 0.5, 0.2 * pop()), (T["print2"] + 0.85, 0.2 * pop())]
    parts += [(T["store2"], 0.4 * chime(1.4)), (T["store2"] + 0.05, 0.35 * mix(*[(j * 0.12, piano(f)) for j, f in enumerate((523, 659, 784, 1046))]))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
