"""Sound effects for reel 12 (guess-the-sticker quiz), placed on each on-screen event.

usage: python3 sfx_reel12.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import fanfare, tick

DUR = 26.0
ROUNDS = [(2.6, "pixel"), (7.8, "light"), (13.0, "puzzle")]


def marimba(f, d=0.35):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)) * np.exp(-t * 9)


def jingle():
    return mix(*[(i * 0.11, marimba(f)) for i, f in enumerate([523, 659, 784, 1046])])


def clock(hi=True, d=0.06):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * (2000 if hi else 1500) * t) * np.exp(-t * 120) + 0.3 * lowpass(rng.standard_normal(len(t)), 4000) * np.exp(-t * 200)


def correct():
    return mix((0, marimba(784, 0.5)), (0.09, marimba(988, 0.5)), (0.18, marimba(1175, 0.7)))


def shimmer(d=0.5):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return sum(np.sin(2 * np.pi * f * np.arange(n) / SR) * np.exp(-t * 4) * (rng.random() * .5 + .5) for f in [2093, 2637, 3136, 3951]) * np.minimum(1, t * 20)


def switch_on():
    n = int(0.5 * SR); t = np.arange(n) / SR
    click = np.zeros(n); click[:300] = lowpass(rng.standard_normal(300), 5000) * np.exp(-np.arange(300) / 40)
    hum = (np.sin(2 * np.pi * 120 * t) * 0.3 + np.sin(2 * np.pi * 240 * t) * 0.15) * np.minimum(1, t * 10) * np.exp(-t * 4)
    return click + hum


def clack(d=0.06):
    t = np.arange(int(d * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 90) + np.sin(2 * np.pi * 700 * t) * np.exp(-t * 80)


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.1, whoosh(0.5), -14)
add(0.8, jingle(), -9)
add(1.6, pop(600, 0.12), -14)
for a, mode in ROUNDS:
    add(a, mix((0, marimba(659)), (0.12, marimba(880))), -11)   # round badge
    add(a + 0.2, pop(500, 0.16), -12)                           # frame pops
    for k in range(3):
        add(a + 0.6 + k * 0.12, whoosh(0.25), -18)              # options slide in
    t, hi = a + 1.0, True
    while t < a + 3.4:                                          # ticking clock, faster near the end
        add(t, clock(hi), -17 if t < a + 2.6 else -14)
        t += 0.25 if t < a + 2.6 else 0.13; hi = not hi
    if mode == "pixel":
        add(a + 3.4, shimmer(0.6), -12)
    if mode == "light":
        add(a + 0.2, switch_on()[:int(0.08 * SR)], -18)
        add(a + 3.4, switch_on(), -10)
    if mode == "puzzle":
        for order in range(9):
            add(a + 1.0 + order * 0.24 + 0.38, clack(), -14)
        add(a + 3.4, sparkle(0.5), -14)
    add(a + 3.9, correct(), -8)
add(18.2, whoosh(0.7), -12)
add(18.7, pop(700, 0.14), -12)
add(19.8, pop(550, 0.12), -15)
for i in range(3):
    add(22.1 + i * 0.3, marimba([880, 1046, 1318][i], 0.5), -10)
add(22.8, pop(600, 0.14), -13)
add(23.0, fanfare(), -9)
add(23.7, chime(1.0), -12)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
