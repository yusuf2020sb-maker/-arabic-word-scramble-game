"""Soundtrack for reel 20 (journal session POV): a soft lo-fi loop plus desk sounds.

usage: python3 sfx_reel20.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick
from sfx_reel18 import pen, slide, tear

DUR = 23.5
BEAT = 0.75                       # 80 bpm
CHORDS = [[174.6, 220.0, 261.6, 329.6], [164.8, 196.0, 246.9, 293.7], [146.8, 174.6, 220.0, 261.6], [130.8, 164.8, 196.0, 246.9]]  # Fmaj7 Em7 Dm7 Cmaj7


def keys(freqs, d):
    # soft electric-piano chord with slow tremolo
    t = np.arange(int(d * SR)) / SR
    y = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3) for f in freqs)
    return y * np.exp(-t * 0.9) * (0.85 + 0.15 * np.sin(2 * np.pi * 4 * t)) * np.minimum(1, t * 60)


def kick(d=0.3):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * (50 + 70 * np.exp(-t * 30)) * t) * np.exp(-t * 12)


def hat(d=0.05):
    n = int(d * SR)
    return (lowpass(rng.standard_normal(n), 12000) - lowpass(rng.standard_normal(n), 6000)) * np.exp(-np.arange(n) / 300)


def crackle(d):
    n = int(d * SR); y = np.zeros(n)
    for _ in range(int(d * 18)):
        s = int(rng.random() * (n - 60)); y[s:s + 60] += rng.standard_normal(60) * np.exp(-np.arange(60) / 10) * rng.random()
    return y + 0.15 * lowpass(rng.standard_normal(n), 800)


def lofi(d):
    parts = []
    bars = int(d / (4 * BEAT)) + 1
    for b in range(bars):
        t0 = b * 4 * BEAT
        parts.append((t0, 0.5 * keys(CHORDS[b % 4], 4 * BEAT + 0.6)))
        for k in range(4):
            if k in (0, 2): parts.append((t0 + k * BEAT, 0.5 * kick()))
            if k in (1, 3): parts.append((t0 + k * BEAT, 0.25 * lowpass(rng.standard_normal(int(0.12 * SR)), 3000) * np.exp(-np.arange(int(0.12 * SR)) / 900)))
        for k in range(8):
            parts.append((t0 + k * BEAT / 2 + (0.03 if k % 2 else 0), 0.12 * hat()))
    y = mix(*parts)[:int(d * SR)]
    y = lowpass(y, 5000) + 0.3 * crackle(d)
    fade = np.minimum(1, np.arange(len(y)) / (1.0 * SR)) * np.minimum(1, (len(y) - np.arange(len(y))) / (1.5 * SR))
    return y * fade


def peel(d=0.18):
    n = int(d * SR); t = np.linspace(0, 1, n)
    crack = rng.standard_normal(n) * (rng.random(n) > 0.7)
    return lowpass(crack, 2500 + 3000 * t) * np.sin(np.pi * t)


def pat(d=0.08):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 1500) * np.exp(-t * 70) + 0.5 * np.sin(2 * np.pi * 160 * t) * np.exp(-t * 60)


T0, STEP, N = 6.2, 0.6, 11
EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.0, lofi(DUR), -20)
for s in range(6):                                  # slow clock before the time-lapse
    add(0.3 + s * 1.0, tick(0.03), -26)
for k in range(int((13.6 - T0) * 8)):               # fast clock during the time-lapse
    add(T0 + k / 8, tick(0.02), -30)
add(3.2, whoosh(0.6), -18)
add(3.95, mix((0, thump(0.3)), (0, 0.4 * slide(0.2))), -13)
add(T0, tear(0.22), -15)
add(T0 + 0.1, slide(0.45), -20)
for i in range(1, N):
    at = T0 + i * STEP
    add(at, peel(), -15)
    add(at + 0.2, whoosh(0.28), -22)
    add(at + 0.5, pat(), -14)
add(12.9, pen(0.8), -19)
add(13.8, slide(0.6), -18)
add(14.2, whoosh(0.7), -20)
for i in range(4):
    add(15.4 + i * 0.15, pop(600 + i * 100, 0.1), -18)
add(18.5, whoosh(0.5), -18)
add(19.05, thump(0.3), -12)
add(19.3, whoosh(0.5), -16)
add(19.9, chime(1.0), -15)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
