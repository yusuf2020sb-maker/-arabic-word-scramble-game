"""Sound effects for reel 10 (treasure chest), placed on each on-screen event.

usage: python3 sfx_reel10.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick

DUR = 24.0


def boom(d=0.9):
    n = int(d * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (45 + 90 * np.exp(-t * 9)) * t) * np.exp(-t * 4)
    return body + 0.5 * lowpass(rng.standard_normal(n), 400) * np.exp(-t * 10)


def squeak(d=0.4):
    # highlighter swipe: bright felt-tip squeal with a slight wobble
    n = int(d * SR); t = np.arange(n) / SR
    f = 1700 + 500 * (t / d) + 60 * np.sin(2 * np.pi * 23 * t)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    hiss = lowpass(rng.standard_normal(n), 6000) - lowpass(rng.standard_normal(n), 2500)
    return (tone + 0.6 * hiss) * np.sin(np.pi * t / d) ** 0.7


def creak(d=0.45):
    n = int(d * SR); t = np.arange(n) / SR
    pulses = np.zeros(n)
    rate = 40 + 80 * (t / d)
    phase = np.cumsum(rate) / SR
    pulses[np.diff(np.floor(phase), prepend=0) > 0] = 1
    return lowpass(np.convolve(pulses, np.exp(-np.arange(300) / 40), "same"), 2200) * np.sin(np.pi * t / d)


def riser(d=0.7):
    n = int(d * SR); t = np.linspace(0, 1, n)
    y = lowpass(rng.standard_normal(n), 300 + 9000 * t ** 2) * t ** 2
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * t ** 2) / SR) * t ** 2 * 0.3
    return y + tone


def magic(f0, d=0.9):
    # soft bell with vibrato and a little upward glint
    n = int(d * SR); t = np.arange(n) / SR
    f = f0 * (1 + 0.006 * np.sin(2 * np.pi * 6 * t))
    y = sum(np.sin(2 * np.pi * np.cumsum(f * m) / SR) * a for m, a in [(1, 1), (2, .35), (3.01, .15)])
    return y * np.exp(-t * 3.5) * np.minimum(1, t * 80)


def rustle(d=0.6):
    n = int(d * SR); t = np.linspace(0, 1, n)
    crack = rng.standard_normal(n) * (rng.random(n) > 0.85)
    return lowpass(crack, 3500) * np.sin(np.pi * t) + 0.3 * lowpass(rng.standard_normal(n), 1500) * np.sin(np.pi * t)


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.1, whoosh(0.5), -16)
add(1.3, boom(), -6)
add(1.9, squeak(0.4), -15)
add(3.15, whoosh(0.5), -11)
add(3.62, mix((0, boom(0.6)), (0, thump(0.3))), -6)
for k in range(5):
    add(3.72 + k * 0.1, tick(0.03) + 0.6 * thump(0.03)[:int(0.03 * SR)], -16)
add(4.18, creak(), -14)
add(4.25, sparkle(0.6), -12)
add(4.6, riser(0.7), -10)
add(5.3, mix((0, boom(0.7)), (0.02, chime(0.9))), -9)
PENTA = [523, 587, 659, 784, 880, 1046, 1175, 1318]
for g, at in enumerate([5.6, 7.5, 9.4, 11.3]):
    add(at, magic(PENTA[g * 2]), -12)
    add(at + 0.25, magic(PENTA[g * 2 + 1]), -12)
    add(at + 0.3, pop(800, 0.1), -16)
add(13.7, pop(500, 0.16), -10)
for i, at in enumerate([14.3, 14.75, 15.2, 15.65, 16.1]):
    add(at, mix(*[(k * 0.03, pop(500 + i * 120 + k * 40, 0.1)) for k in range(min(4, i + 1))]), -10)
add(16.3, pop(700, 0.12), -12)
add(16.6, squeak(0.4), -15)
add(17.55, rustle(0.6), -11)
for k in range(14):
    add(18.3 + k * 0.12, tick(0.025), -20)
add(20.0, thump(0.3), -7)
add(20.8, sparkle(0.6), -12)
add(21.3, chime(1.1), -11)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
