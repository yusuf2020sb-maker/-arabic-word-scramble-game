"""Cinematic score for reel 22 (vintage classic, premium ad): pad, piano, risers, hits.

usage: python3 sfx_reel22.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel8 import tick
from sfx_reel10 import boom, riser

DUR = 24.5
PROG = [[220.0, 261.6, 329.6, 440.0], [174.6, 220.0, 261.6, 349.2], [130.8, 164.8, 196.0, 261.6], [196.0, 246.9, 293.7, 392.0]]


def pad(freqs, d):
    t = np.arange(int(d * SR)) / SR
    y = np.zeros_like(t)
    for f in freqs:
        for det in (-0.004, 0.0, 0.004):
            ph = (f * (1 + det) * t) % 1
            y += (2 * ph - 1) * 0.25
    y = lowpass(y, 1400)
    env = np.minimum(1, t / 0.9) * np.minimum(1, (d - t) / 0.9)
    return y * env


def piano(f, d=1.6):
    t = np.arange(int(d * SR)) / SR
    y = sum(np.sin(2 * np.pi * f * m * t) * a * np.exp(-t * (2.5 + m)) for m, a in [(1, 1), (2, .45), (3, .2), (4, .1)])
    return y * np.minimum(1, t * 300)


def ping(f=1800, d=0.25):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 25)


def rumble(d):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 250 + 500 * np.sin(np.pi * t)) * np.sin(np.pi * t) ** 0.7


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
bed = mix(*[(i * 3.0, pad(PROG[i % 4], 3.4)) for i in range(8)])
fade = np.minimum(1, np.arange(len(bed)) / (1.5 * SR)) * np.minimum(1, (len(bed) - np.arange(len(bed))) / (1.8 * SR))
add(0.0, bed[:int(DUR * SR)] * fade[:int(DUR * SR)], -19)
for k in range(7):
    add(0.3 + k * 0.5, tick(0.03), -26)
for i, (f, at) in enumerate([(659.3, 0.6), (523.3, 1.0), (587.3, 1.4), (440.0, 1.9)]):
    add(at, piano(f), -15)
add(2.6, riser(0.8), -14)
add(3.4, boom(0.9), -10)
add(3.45, rumble(5.4), -19)
add(5.6, mix((0, piano(440.0, 2.0)), (0, piano(659.3, 2.0)), (0.05, 0.5 * sparkle(0.6))), -14)
add(8.6, riser(0.4), -18)
add(9.0, mix((0, boom(0.7)), (0.05, sparkle(0.8))), -12)
add(10.4, piano(523.3, 1.6), -17)
add(12.75, whoosh(0.6), -15)
add(13.6, sparkle(0.9), -18)
for at in [14.0, 14.4, 14.8]:
    add(at, ping(), -17)
for at in [16.4, 17.65, 18.9]:
    add(at - 0.05, whoosh(0.5), -15)
    add(at + 0.2, piano(392.0 if at < 18 else 440.0, 1.2), -19)
add(20.15, boom(0.8), -13)
add(20.3, sparkle(1.0), -18)
add(21.0, mix((0, piano(220.0, 3.0)), (0, piano(329.6, 3.0)), (0, piano(440.0, 3.0)), (0.02, piano(659.3, 3.0))), -12)
add(22.3, chime(1.2), -16)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    end = np.ones(len(y)); n = int(0.6 * SR); end[-n:] = np.linspace(1, 0, n)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y * end, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
