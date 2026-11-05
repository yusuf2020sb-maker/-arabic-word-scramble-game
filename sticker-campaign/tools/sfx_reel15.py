"""Sound effects for reel 15 (coffee, indirect audience situations).

usage: python3 sfx_reel15.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick
from sfx_reel10 import boom
from sfx_reel14 import alarm, hiss, pour, powerup, scratch, tada, trombone

DUR = 26.5
SIT = [3.2, 7.2, 11.2]


def slide_down(d=0.9):
    # slide whistle falling: the "so tired" sound
    n = int(d * SR); t = np.linspace(0, 1, n)
    f = 1400 * (1 - 0.7 * t ** 0.8)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t) ** 0.5 * (1 + 0.1 * np.sin(2 * np.pi * 7 * t * d))


def rimshot():
    # ba-dum-tss: two tom hits then a cymbal
    def tom(f, d=0.18):
        t = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * (f + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 16)
    n = int(0.9 * SR); t = np.arange(n) / SR
    cym = (lowpass(rng.standard_normal(n), 10000) - lowpass(rng.standard_normal(n), 4000)) * np.exp(-t * 5)
    return mix((0, tom(180)), (0.14, tom(130)), (0.3, cym), (0.3, 0.5 * thump(0.2)))


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.0, alarm(0.8), -16)
add(0.95, scratch(), -11)
add(1.02, boom(0.7), -8)
add(2.1, pop(650, 0.14), -13)
for k, a in enumerate(SIT):
    add(a - 0.05, whoosh(0.45), -13)
    add(a + 0.75, thump(0.25), -11)
    if k == 0:
        add(a + 0.9, trombone(), -11)
    else:
        add(a + 0.9, slide_down(0.65), -14)
    add(a + 1.55, pour(1.2), -10)
    add(a + 2.3, tada(), -11)
    for i in range(4 if k == 0 else (2 if k == 1 else 3)):
        add(a + 2.4 + i * 0.15, pop(650 + i * 110, 0.12), -14)
    add(a + 2.8, pop(800, 0.12), -15)
add(7.2 + 1.75, powerup(0.5), -14)
add(7.2 + 2.2, pop(1200, 0.12), -13)
add(15.3, pop(550, 0.14), -13)
add(15.85, rimshot(), -8)
for i in range(5):
    at = 16.6 + i * 0.5
    add(at - 0.04, whoosh(0.22), -15)
    add(at + 0.13, thump(0.15), -12)
for k in range(30):
    add(19.3 + 1.0 * (1 - (1 - k / 30) ** 0.5), tick(0.02), -22)
add(20.3, pop(1000, 0.12), -12)
for i in range(4):
    add(20.5 + i * 0.15, pop(600 + i * 100, 0.1), -15)
add(22.25, whoosh(0.6), -12)
add(22.85, thump(0.25), -10)
add(23.0, hiss(1.0), -18)
add(23.6, chime(1.0), -12)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
