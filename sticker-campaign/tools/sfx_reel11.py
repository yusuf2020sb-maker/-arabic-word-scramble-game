"""Sound effects for reel 11 (breaking-news style), placed on each on-screen event.

usage: python3 sfx_reel11.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import thump
from sfx_reel8 import tick

DUR = 23.5
SWITCHES = [6.6, 9.2, 11.8, 14.4, 18.2]


def stab(freqs, d=0.45):
    # brassy chord hit: stacked saw-ish tones through a lowpass
    n = int(d * SR); t = np.arange(n) / SR
    y = sum(np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t) for f in freqs)
    return lowpass(y, 3500) * np.exp(-t * 4) * np.minimum(1, t * 200)


def timpani(d=0.7):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (90 + 30 * np.exp(-t * 12)) * t) * np.exp(-t * 4) + 0.3 * lowpass(rng.standard_normal(n), 300) * np.exp(-t * 15)


def sting():
    return mix((0, timpani()), (0, stab([220, 277, 330])), (0.22, stab([247, 311, 370])), (0.44, stab([294, 370, 440], 0.8)), (0.44, timpani(0.9)))


def beep(f=1400, d=0.12):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.minimum(1, (d - t) * 60) * np.minimum(1, t * 300)


def static(d=0.28):
    n = int(d * SR)
    return (lowpass(rng.standard_normal(n), 7000) - lowpass(rng.standard_normal(n), 400)) * np.sin(np.pi * np.arange(n) / n) ** 0.3


def whirl(d=1.0):
    n = int(d * SR); t = np.linspace(0, 1, n)
    flutter = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(30 - 24 * t) / SR)
    return lowpass(rng.standard_normal(n), 2500) * flutter * np.sin(np.pi * t) ** 0.5


def ding(d=0.4):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 9)


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.0, sting(), -7)
for i in range(3):
    add(0.05 + i * 0.12, whoosh(0.6), -14)
add(0.5, whoosh(0.5), -13)
for k in range(4):                      # breaking alarm
    add(1.45 + k * 0.28, beep(1500 if k % 2 == 0 else 1200), -14)
add(2.8, whirl(1.0), -11)
add(3.8, thump(0.25) + 0.5 * lowpass(rng.standard_normal(int(0.25 * SR)), 2000) * np.exp(-np.arange(int(0.25 * SR)) / 1500), -7)
for c in SWITCHES:
    add(c - 0.1, static(0.28), -14)
for at in [6.6, 9.2, 11.8]:             # lower thirds
    add(at + 0.58, whoosh(0.35), -14)
    add(at + 0.95, ding(), -15)
for i, (at, digits) in enumerate([(14.7, 2), (15.4, 3), (16.1, 1)]):
    add(at - 0.2, whoosh(0.4), -15)
    for k in range(int((0.9 + digits * 0.12) * 40)):   # odometer clicks, slowing down
        x = k / ((0.9 + digits * 0.12) * 40)
        add(at + (1 - (1 - x) ** 0.6) * (0.9 + digits * 0.12), tick(0.02), -24)
    add(at + 0.95 + digits * 0.12, thump(0.15), -14)
add(18.3, sting(), -8)
add(19.6, chime(1.0), -12)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
