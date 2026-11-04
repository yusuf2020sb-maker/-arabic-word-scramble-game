"""Sound effects for reel 9 (before/after reveal for each audience).

usage: python3 sfx_reel9.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick

DUR = 23.5
STORIES = [2.6, 8.0, 13.4]


def zip_sweep(d=1.4):
    # slider drag: filtered noise with a rising band and a fast grain
    n = int(d * SR); t = np.linspace(0, 1, n)
    grain = (rng.random(n) > 0.6) * rng.standard_normal(n)
    y = lowpass(grain, 1200 + 4000 * t) - lowpass(grain, 500 + 1500 * t)
    return y * np.sin(np.pi * t) ** 0.6


def stamp_thud(d=0.4):
    n = int(d * SR); t = np.arange(n) / SR
    return thump(d) * 1.2 + 0.4 * lowpass(rng.standard_normal(n), 900) * np.exp(-t * 30)


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
for i, at in enumerate([0.15, 0.8, 1.4]):
    add(at, pop(500 + i * 150, 0.16), -9)
for a in STORIES:
    add(a - 0.05, whoosh(0.6), -11)      # object slides in
    add(a + 0.55, thump(0.2), -12)       # lands on the desk
    add(a + 1.0, zip_sweep(1.4), -13)    # reveal sweep
    for k in range(5):                   # line passes stickers
        add(a + 1.25 + k * 0.24, tick(0.03), -16)
    add(a + 2.9, zip_sweep(0.6), -16)    # little back-and-forth
    add(a + 2.5, pop(800, 0.12), -14)    # caption
add(8.0 + 3.0, stamp_thud(), -6)         # "ممتاز" stamp
for k, at in enumerate([18.9, 19.05, 19.2]):
    add(at - 0.05, whoosh(0.35), -14)
    add(at + 0.4, pop(600 + k * 120, 0.12), -12)
add(20.1, pop(450, 0.2), -9)
add(20.6, chime(1.0), -11)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
