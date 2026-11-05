"""Sound effects for reel 14 (coffee memes), placed on each on-screen event.

usage: python3 sfx_reel14.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import boing, pop, thump
from sfx_reel8 import tick
from sfx_reel10 import boom

DUR = 24.0


def alarm(d=0.9):
    # old twin-bell alarm clock: fast hammer between two bells
    n = int(d * SR); t = np.arange(n) / SR
    ham = (np.sign(np.sin(2 * np.pi * 22 * t)) + 1) / 2
    bell = np.sin(2 * np.pi * 2600 * t) * 0.6 + np.sin(2 * np.pi * 3400 * t) * 0.4
    return bell * (0.3 + 0.7 * ham) * np.minimum(1, (d - t) * 8)


def scratch(d=0.45):
    # record scratch: noisy tone sweeping down then up
    n = int(d * SR); t = np.linspace(0, 1, n)
    f = 900 - 700 * np.sin(np.pi * t) ** 0.7
    tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3
    return lowpass(tone + 0.6 * rng.standard_normal(n), 2500) * np.sin(np.pi * t) ** 0.4


def trombone():
    # "wah wah wah wahhh": four falling notes with vibrato on the last
    parts = []
    for i, (f, d) in enumerate([(311, .32), (293, .32), (277, .32), (262, 1.0)]):
        t = np.arange(int(d * SR)) / SR
        vib = 1 + (0.02 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0)
        ph = np.cumsum(f * vib * (1 - (0.06 * t / d if i == 3 else 0))) / SR
        y = (np.sign(np.sin(2 * np.pi * ph)) * 0.35 + np.sin(2 * np.pi * ph) + 0.4 * np.sin(4 * np.pi * ph))
        env = np.minimum(1, t * 25) * np.minimum(1, (d - t) * 10) * (0.8 + 0.2 * np.sin(2 * np.pi * 3 * t))
        parts.append((i * 0.34, lowpass(y * env, 1800)))
    return mix(*parts)


def pour(d=1.1):
    # liquid pour + glugs + bubbles
    n = int(d * SR); t = np.linspace(0, 1, n)
    stream = lowpass(rng.standard_normal(n), 1800) * (0.6 + 0.4 * np.sin(np.pi * t))
    bubbles = np.zeros(n)
    for k in range(18):
        s = int(rng.random() * (n - 2000)); m = 1500; tt = np.arange(m) / SR; f = 300 + rng.random() * 500
        bubbles[s:s + m] += np.sin(2 * np.pi * (f + 900 * tt) * tt) * np.exp(-tt * 40)
    return stream + 0.6 * bubbles


def powerup(d=0.85):
    n = int(d * SR); t = np.linspace(0, 1, n)
    f = 200 + 1300 * t ** 1.6
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * 0.4
    return lowpass(y, 4000) * t * np.minimum(1, (1 - t) * 30 + 0.2)


def tada():
    t = np.arange(int(0.8 * SR)) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 3) for f in [523, 659, 784, 1046]) * np.minimum(1, t * 100)


def hiss(d=1.0):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return (lowpass(rng.standard_normal(n), 9000) - lowpass(rng.standard_normal(n), 3500)) * np.sin(np.pi * t) ** 0.4


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.0, alarm(0.9), -16)
add(1.2, scratch(), -11)
add(1.32, boom(0.7), -8)
add(2.3, pop(650, 0.14), -12)
add(3.3, whoosh(0.5), -13)
add(3.75, thump(0.25), -11)
add(4.4, whoosh(0.4), -15)
add(4.6, trombone(), -10)
add(6.15, pour(1.15), -10)
add(6.4, powerup(0.85), -14)
add(7.22, pop(1200, 0.12), -12)
add(7.45, whoosh(0.5), -14)
add(7.6, tada(), -10)
add(7.8, boing(0.45), -11)
add(8.6, pop(700, 0.14), -12)
add(9.4, pop(850, 0.14), -12)
add(11.6, pop(600, 0.14), -12)
for i in range(7):
    at = 12.4 + i * 0.52
    add(at - 0.04, whoosh(0.22), -14)
    add(at + 0.12, thump(0.15), -11)
for k in range(30):
    add(16.1 + 1.1 * (1 - (1 - k / 30) ** 0.5), tick(0.02), -22)
add(17.2, pop(1000, 0.12), -12)
for i in range(4):
    add(17.5 + i * 0.15, pop(600 + i * 100, 0.1), -15)
add(19.25, whoosh(0.6), -12)
add(19.85, thump(0.25), -10)
add(20.0, hiss(1.0), -18)
add(20.6, chime(1.0), -12)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
