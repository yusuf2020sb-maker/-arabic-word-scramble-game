"""Sound effects for reel 8 (sticker slot machine), placed on each on-screen event.
Reel ticks are computed from the same motion curve reel8.html uses.

usage: python3 sfx_reel8.py <out.wav>
"""
import math
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop, thump

DUR = 22.5
N, LOOPS = 12, 3
SPINS = [
    dict(lever=2.5, start=2.65, stops=[4.0, 4.4, 4.8], land=0),
    dict(lever=6.5, start=6.65, stops=[7.6, 7.85, 8.1], land=4),
    dict(lever=8.8, start=8.95, stops=[9.8, 10.0, 10.2], land=8),
]


def reel_pos(r, t):
    pos = 6
    for s in SPINS:
        target = math.ceil((pos + LOOPS * N - s["land"]) / N) * N + s["land"]
        if t < s["start"]:
            return pos
        u = min(1, max(0, (t - s["start"]) / (s["stops"][r] - s["start"])))
        if u < 1:
            return pos + (target - pos) * (1 - (1 - u) ** 3)
        pos = target
    return pos


def tick(d=0.025):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 260)


def clunk(d=0.2):
    n = int(d * SR); t = np.arange(n) / SR
    return thump(d) + 0.5 * lowpass(rng.standard_normal(n), 1500) * np.exp(-t * 40)


def lever(d=0.35):
    n = int(d * SR); t = np.linspace(0, 1, n)
    ratchet = np.zeros(n)
    for k in range(0, n, int(SR / 40)):
        m = min(220, n - k); ratchet[k:k + m] += lowpass(rng.standard_normal(m), 3000) * np.exp(-np.arange(m) / 50)
    return ratchet * (1 - t) + 0.6 * clunk(d)[:n]


def fanfare():
    # rising major arpeggio, then a held chord
    notes = [523, 659, 784, 1046]
    parts = []
    for i, f in enumerate(notes):
        d = 0.16 if i < 3 else 0.7
        tt = np.arange(int(d * SR)) / SR
        tone = (np.sign(np.sin(2 * np.pi * f * tt)) * 0.25 + np.sin(2 * np.pi * f * tt)) * np.exp(-tt * (8 if i < 3 else 3))
        parts.append((i * 0.12, lowpass(tone, 5000)))
    return mix(*parts)


def coin(d=0.18):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1975 * t) + 0.6 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 22)


def scratch(d):
    n = int(d * SR); t = np.arange(n) / SR
    y = lowpass(rng.standard_normal(n), 6000) - lowpass(rng.standard_normal(n), 1200)
    return y * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 3 * t)))


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.3, whoosh(0.5), -11)           # machine drops in
add(0.85, thump(0.3), -7)            # lands
for s in SPINS:
    add(s["lever"], lever(), -10)
    for r, st in enumerate(s["stops"]):
        add(st, clunk(), -8)
    # ticks as cells pass the payline (last reel)
    prev = math.floor(reel_pos(2, s["start"]))
    for k in range(int((s["stops"][2] - s["start"]) * 200)):
        t = s["start"] + k / 200
        cur = math.floor(reel_pos(2, t))
        if cur != prev:
            add(t, tick(), -20)
        prev = cur
    win = s["stops"][2] + 0.1
    add(win, fanfare(), -9)
    for i in range(6):
        add(win + 0.25 + i * 0.13, coin(), -16)
add(11.2, whoosh(0.5), -12)          # to the lens
add(11.25, sparkle(0.5), -15)
for i in range(8):                   # slices
    add(14.7 + i * 0.045, whoosh(0.12), -22)
    add(15.4 + i * 0.045, whoosh(0.12), -22)
add(17.4, whoosh(0.5), -11)          # card flies in
add(17.85, thump(0.25), -9)
add(18.6, scratch(1.8), -15)         # coin scratching
add(20.4, fanfare(), -9)             # reveal
add(20.45, sparkle(0.6), -13)
add(21.3, chime(0.9), -12)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
