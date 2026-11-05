"""Sound effects for reel 17 (Arabic heritage: dusk, door, majlis, sadu loom, chest).

usage: python3 sfx_reel17.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop, thump
from sfx_reel14 import pour

DUR = 24.5


def pluck(f, d=1.2, damp=0.996):
    # Karplus-Strong plucked string (oud-like)
    n = int(d * SR); period = int(SR / f)
    buf = rng.standard_normal(period) * 0.5; y = np.empty(n)
    for i in range(n):
        y[i] = buf[i % period]
        buf[i % period] = damp * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return lowpass(y, 4000)


HIJAZ = [293.7, 311.1, 370.0, 392.0, 440.0, 466.2, 523.3, 587.3]   # D hijaz


def phrase(idx, step=0.22, d=1.2):
    return mix(*[(k * step, pluck(HIJAZ[i], d)) for k, i in enumerate(idx)])


def wind(d):
    n = int(d * SR); t = np.linspace(0, 1, n)
    sweep = 400 + 900 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t * d))
    y = lowpass(rng.standard_normal(n), sweep) - lowpass(rng.standard_normal(n), 200)
    return y * np.minimum(1, t * 4) * np.minimum(1, (1 - t) * 4)


def creak(d=0.8):
    n = int(d * SR); t = np.arange(n) / SR
    f = 140 + 60 * np.sin(2 * np.pi * 1.3 * t)
    saw = ((np.cumsum(f) / SR) % 1) * 2 - 1
    return lowpass(saw * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 35 * t))), 1500) * np.sin(np.pi * t / d)


def clink(f=3200, d=0.35):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.51 * t)) * np.exp(-t * 14)


def loom(d=0.08):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 110 * t) * np.exp(-t * 50) + 0.4 * lowpass(rng.standard_normal(n), 900) * np.exp(-t * 60)


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.0, wind(4.4), -20)
add(0.2, phrase([0, 2, 3, 4], 0.3, 1.6), -12)          # hook motif
for at in [1.6, 2.2, 2.8]:
    add(at, pluck(HIJAZ[4] * 2, 0.8), -18)
add(4.1, creak(0.9), -12)
add(4.75, thump(0.3), -12)
add(4.8, whoosh(0.8), -12)
add(5.4, sparkle(0.6), -14)
add(6.0, clink(2200, 0.5), -18)                         # lantern chain
add(6.5, whoosh(0.4), -16)
add(7.3, pour(1.1), -15)                                # coffee from the dallah
for at in [6.9, 7.4]:
    add(at, clink(), -14)
for k, at in enumerate([7.8, 8.2, 8.6, 8.9, 9.2, 9.6, 10.0, 10.3]):
    add(at, pop(450 + k * 40, 0.1), -18)
add(10.8, phrase([0, 1, 2, 3, 4, 3, 2], 0.14, 0.9), -13)   # star draws
add(12.4, whoosh(0.5), -14)
for i in range(20):
    add(13.0 + i * 0.09, loom(), -14)
for i in range(4):
    add(14.9 + i * 0.15, pop(600 + i * 90, 0.1), -15)
for i in range(3):
    add(16.3 + i * 1.35, whoosh(0.45), -14)
    add(16.75 + i * 1.35, pluck(HIJAZ[[4, 5, 7][i]], 0.9), -14)
add(20.9, creak(0.7), -13)
add(21.4, sparkle(0.7), -12)
add(21.5, phrase([7, 6, 4, 2, 3, 0], 0.2, 1.8), -11)    # closing phrase


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
