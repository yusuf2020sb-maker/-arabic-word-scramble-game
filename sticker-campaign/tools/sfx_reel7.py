"""Sound effects for reel 7 (group chat), placed on each on-screen event.

usage: python3 sfx_reel7.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop

DUR = 22.0
THEM = [0.9, 1.9, 5.0, 6.0, 8.8, 9.6, 10.6, 13.2, 16.3]
ME = [3.4, 7.6, 12.2, 14.9]
TYPING = [(0.3, 0.9), (4.3, 5.0), (8.2, 8.8), (12.7, 13.2), (15.6, 16.3)]
REACTS = [4.0, 6.6, 10.0, 11.2, 13.8]


def ding(d=0.35):
    # soft two-note "message received"
    n = int(d * SR); t = np.arange(n) / SR
    a = np.sin(2 * np.pi * 1046 * t) * np.exp(-t * 14)
    b = np.zeros(n); k = int(0.09 * SR)
    b[k:] = np.sin(2 * np.pi * 1568 * t[:n - k]) * np.exp(-t[:n - k] * 12)
    return a + b


def sent(d=0.22):
    # quick upward chirp "message sent"
    n = int(d * SR); t = np.arange(n) / SR
    f = 500 + 1800 * (t / d) ** 1.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 1.2


def tap(d=0.03):
    n = int(d * SR)
    return lowpass(rng.standard_normal(n), 3500) * np.exp(-np.arange(n) / 120)


def buzz(d=0.4):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * 150 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t))) * 0.5


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
for at in THEM:
    add(at, ding(), -12)
for at in ME:
    add(at, sent(), -12)
    for k in range(9):  # keyboard taps while typing
        add(at - 1.0 + k * 0.095 + rng.random() * 0.02, tap(), -24)
for a, b in TYPING:  # soft ticks for the typing indicator
    for x in np.arange(a, b, 0.18):
        add(float(x), tap(0.02), -30)
for at in REACTS:
    add(at, pop(900, 0.1), -14)
add(14.9, buzz(), -20)
add(16.35, sparkle(0.5), -14)
add(18.35, whoosh(0.7), -11)
add(19.25, chime(1.0), -11)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
