"""Sound effects for reel 18 (stamps: mail slot, wax seal, pen, perforation tear, postmark).

usage: python3 sfx_reel18.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import pop, thump
from sfx_reel16 import page

DUR = 24.5


def clack(d=0.18):
    # brass mail-slot flap
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1450 * t) + 0.7 * np.sin(2 * np.pi * 2330 * t)) * np.exp(-t * 30) + 0.5 * lowpass(rng.standard_normal(n), 4000) * np.exp(-t * 90)


def slide(d=0.5):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 3000) * np.sin(np.pi * t) ** 0.8


def crack(d=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    snap = lowpass(rng.standard_normal(n), 6000) * np.exp(-t * 70)
    bits = np.zeros(n)
    for k in range(5):
        s = int((0.03 + rng.random() * 0.2) * SR); m = min(400, n - s)
        bits[s:s + m] += lowpass(rng.standard_normal(m), 5000) * np.exp(-np.arange(m) / 50) * 0.5
    return snap + bits + 0.4 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40)


def pen(d):
    # nib scratching on paper: bursts of bright noise following handwriting strokes
    n = int(d * SR); t = np.arange(n) / SR
    strokes = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (6 + 2 * np.sin(2 * np.pi * 0.7 * t)) * t))
    y = (lowpass(rng.standard_normal(n), 7000) - lowpass(rng.standard_normal(n), 2500)) * strokes
    return y * np.minimum(1, t * 20) * np.minimum(1, (d - t) * 20)


def tear(d=0.3):
    # perforations ripping: a fast run of tiny pops
    n = int(d * SR); y = np.zeros(n)
    for k in range(int(d * 90)):
        s = int(k / 90 * SR); m = min(220, n - s)
        y[s:s + m] += lowpass(rng.standard_normal(m), 4500) * np.exp(-np.arange(m) / 25)
    return y


def postmark(d=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    return thump(d) * 1.2 + 0.4 * lowpass(rng.standard_normal(n), 1200) * np.exp(-t * 40)


def typing(n_keys, gap=0.17):
    return mix(*[(k * gap, lowpass(rng.standard_normal(int(0.03 * SR)), 3500) * np.exp(-np.arange(int(0.03 * SR)) / 100)) for k in range(n_keys)])


def flyby(d=1.4):
    # paper plane passing: noise with a doppler-like filter sweep up then down
    n = int(d * SR); t = np.linspace(0, 1, n)
    f = 600 + 3000 * np.exp(-((t - 0.55) ** 2) * 18)
    return lowpass(rng.standard_normal(n), f) * np.exp(-((t - 0.55) ** 2) * 10)


def bell():
    # two rings of a small bicycle-style bell
    def ring():
        t = np.arange(int(0.6 * SR)) / SR
        return sum(np.sin(2 * np.pi * f * t) * a for f, a in [(2637, 1), (3951, .5), (5274, .25)]) * np.exp(-t * 6)
    return mix((0, ring()), (0.16, ring()))


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.3, chime(0.9), -16)
add(1.4, pop(700, 0.12), -16)
add(1.9, clack(), -11)
add(2.0, slide(0.5), -14)
add(2.95, clack(), -14)
add(3.05, mix((0, thump(0.2)), (0, 0.6 * slide(0.15))), -12)
add(3.45, whoosh(0.55), -14)
add(4.3, crack(), -9)
add(4.7, page(0.5), -13)
add(5.2, slide(0.8), -15)
for a, b in [(6.4, 7.3), (7.5, 8.2), (8.4, 9.4), (9.7, 10.9)]:
    add(a, pen(b - a), -16)
add(11.6, whoosh(0.5), -15)
for at in [12.4, 13.6, 14.8]:
    add(at, tear(0.28), -11)
    add(at + 0.3, whoosh(0.55), -16)
    add(at + 1.0, postmark(), -8)
add(16.45, pop(600, 0.14), -13)
add(17.4, typing(len('مع حبي ♡')), -16)
add(19.9, flyby(1.4), -11)
add(21.2, pop(500, 0.18), -12)
add(21.35, bell(), -13)
add(22.0, chime(1.0), -14)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
