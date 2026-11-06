"""Sound effects for reel 21 (vintage roses: wilt and revive, growing garden, bouquet, card).

usage: python3 sfx_reel21.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop, thump
from sfx_reel15 import slide_down
from sfx_reel16 import musicbox, page
from sfx_reel17 import pluck

DUR = 23.5
PENTA = [392.0, 440.0, 523.3, 587.3, 659.3, 784.0, 880.0]


def grow(d=1.3, f0=220):
    # soft rising sine glide with a breathy layer: a stem growing
    n = int(d * SR); t = np.linspace(0, 1, n)
    f = f0 * (1 + 0.8 * t)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t) ** 1.5
    air = lowpass(rng.standard_normal(n), 1500 + 2000 * t) * np.sin(np.pi * t) * 0.25
    return 0.6 * tone + air


def petal(d=0.4):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 2500) * np.sin(np.pi * t) ** 2


def crinkle(d=0.6):
    n = int(d * SR); y = np.zeros(n)
    for _ in range(int(d * 120)):
        s = int(rng.random() * (n - 300)); y[s:s + 300] += lowpass(rng.standard_normal(300), 6000) * np.exp(-np.arange(300) / 40) * rng.random()
    return y


def zip_tie(d=0.35):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 60 * t * d))), 4000 + 3000 * t) * np.sin(np.pi * t)


def revive():
    return mix(*[(i * 0.09, pluck(f, 1.2)) for i, f in enumerate([523.3, 659.3, 784.0, 1046.5, 1318.5])])


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.2, whoosh(0.4), -18)
add(0.6, slide_down(1.6), -16)
for k in range(6):
    add(0.9 + k * 0.25, petal(), -24)
add(2.55, mix((0, thump(0.25)), (0.02, pop(500, 0.16))), -10)
add(2.6, revive(), -11)
add(2.7, sparkle(0.7), -14)
add(4.2, whoosh(0.5), -16)
for i in range(7):
    add(4.4 + i * 0.22, grow(1.3, 200 + i * 25), -19)
for i in range(5):
    add(5.2 + i * 0.25, petal(0.3), -22)
for i in range(7):
    add(5.6 + i * 0.28, pluck(PENTA[i], 1.0), -13)
add(7.8, sparkle(0.5), -16)
add(10.6, whoosh(0.8), -14)
add(11.2, crinkle(0.6), -12)
add(12.0, zip_tie(), -13)
add(12.3, thump(0.15), -16)
add(14.6, whoosh(0.5), -16)
add(15.1, page(0.6), -12)
for i in range(2):
    add(15.7 + i * 0.2, pop(650 + i * 120, 0.1), -15)
for i in range(3):
    add(16.6 + i * 0.2, pop(600 + i * 100, 0.1), -16)
add(18.6, whoosh(0.5), -16)
add(19.1, mix((0, thump(0.25)), (0.05, sparkle(0.6))), -12)
add(19.7, musicbox(), -13)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
