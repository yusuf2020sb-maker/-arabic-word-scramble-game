"""Sound effects for reel 16 (cozy home: rain, shelves, fireplace, page flips).

usage: python3 sfx_reel16.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop, thump

DUR = 24.5


def rain(d, density=0.35):
    # soft steady rain with scattered droplet ticks
    n = int(d * SR)
    bed = lowpass(rng.standard_normal(n), 3500) - lowpass(rng.standard_normal(n), 700)
    ticks = np.zeros(n)
    for _ in range(int(d * 40 * density)):
        s = int(rng.random() * (n - 400)); ticks[s:s + 400] += np.sin(2 * np.pi * (2500 + rng.random() * 2500) * np.arange(400) / SR) * np.exp(-np.arange(400) / 60) * rng.random()
    env = np.minimum(1, np.arange(n) / (0.6 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.6 * SR))
    return (0.7 * bed + 0.5 * ticks) * env


def thunder(d=2.0):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 180) * np.exp(-t * 1.6) * np.minimum(1, t * 6) * 3


def squeak(d=0.5):
    # finger on fogged glass
    n = int(d * SR); t = np.arange(n) / SR
    f = 900 + 300 * np.sin(np.pi * t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 30 * t)) * np.sin(np.pi * t / d) * 0.5


def wood(d=0.12):
    # sticker landing on a wooden shelf
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 220 * t) + 0.6 * np.sin(2 * np.pi * 470 * t)) * np.exp(-t * 45) + 0.3 * lowpass(rng.standard_normal(n), 2000) * np.exp(-t * 80)


def crackle(d):
    n = int(d * SR); y = np.zeros(n)
    for _ in range(int(d * 25)):
        s = int(rng.random() * (n - 300)); y[s:s + 300] += lowpass(rng.standard_normal(300), 5000) * np.exp(-np.arange(300) / 30) * rng.random()
    return y + 0.25 * lowpass(rng.standard_normal(n), 300)


def page(d=0.45):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 2500 + 2500 * t) * np.sin(np.pi * t) ** 1.5


def musicbox():
    # gentle music-box phrase for the ending
    notes = [(1318, 0), (1175, .22), (1046, .44), (1175, .66), (1318, .88), (1568, 1.1), (1318, 1.4)]
    parts = []
    for f, at in notes:
        tt = np.arange(int(0.9 * SR)) / SR
        parts.append((at, (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt * 20)) * np.exp(-tt * 5)))
    return mix(*parts)


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.0, rain(4.9), -20)
add(0.2, thunder(2.2), -14)
for at in [0.3, 1.0, 1.7]:
    add(at, sparkle(0.35), -24)
add(2.7, sparkle(0.5), -18)
add(3.3, sparkle(0.6), -16)
add(4.6, squeak(0.5), -16)
add(4.62, whoosh(0.5), -16)
for i in range(12):
    at = 5.2 + i * 0.5
    add(at + 0.33, wood(), -11)
    add(at + 0.34, whoosh(0.15), -26)
add(5.8, crackle(6.8), -28)        # candle flicker / room tone on the shelves
add(12.55, whoosh(0.5), -15)
for i in range(5):
    add(12.8 + i * 0.25, pop(500 + i * 60, 0.1), -17)
add(13.0, crackle(3.4), -19)        # fireplace
add(16.4, whoosh(0.5), -14)
for f in [17.6, 18.8]:
    add(f, page(), -12)
add(19.95, rain(4.5, 0.25), -24)
add(20.4, thump(0.2), -14)
add(20.6, musicbox(), -13)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
