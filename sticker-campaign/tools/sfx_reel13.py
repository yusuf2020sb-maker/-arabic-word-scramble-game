"""Sound effects for reel 13 (split-flap hook + corkboard countdown).

usage: python3 sfx_reel13.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import pop, thump

DUR = 24.0
FLAP_STOPS = [0.35 + i * 0.22 for i in range(7)]


def flap_click(d=0.018):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 5000) * np.exp(-t * 400) + 0.4 * np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 300)


def pin(d=0.12):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (300 + 500 * np.exp(-t * 60)) * t) * np.exp(-t * 40) + 0.5 * lowpass(rng.standard_normal(n), 2500) * np.exp(-t * 120)


def string(d=0.9):
    # yarn pulled taut: thin rising squeak with fibre noise
    n = int(d * SR); t = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(500 + 700 * t) / SR) * 0.25
    fibre = lowpass(rng.standard_normal(n), 3000) * (rng.random(n) > 0.5)
    return (tone + 0.5 * fibre) * np.sin(np.pi * t) ** 0.8


def drumroll(d=0.75):
    n = int(d * SR); y = np.zeros(n)
    k = 0.0
    while k < d:
        i = int(k * SR); m = min(int(0.05 * SR), n - i)
        y[i:i + m] += lowpass(rng.standard_normal(m), 2500) * np.exp(-np.arange(m) / 300) * (0.4 + 0.6 * k / d)
        k += 0.035
    return y


def crash(d=0.9):
    n = int(d * SR); t = np.arange(n) / SR
    cym = (lowpass(rng.standard_normal(n), 9000) - lowpass(rng.standard_normal(n), 3000)) * np.exp(-t * 4)
    return mix((0, cym), (0, thump(0.3)))


def paper(d=0.2):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 3500) * np.exp(-t * 25)


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
# split-flap clatter: every still-flipping tile clicks at ~18 per second, then a final clack
t = 0.0
while t < FLAP_STOPS[-1]:
    active = sum(1 for s in FLAP_STOPS if t < s)
    add(t, flap_click(), -22 + min(6, active))
    t += 1 / 36
for s in FLAP_STOPS:
    add(s, flap_click(0.03) + 0.5 * thump(0.03)[:int(0.03 * SR)], -13)
add(2.2, pop(700, 0.12), -13)
add(2.95, whoosh(0.5), -12)
for at in [3.1, 8.3, 12.9]:
    add(at, paper(), -13)
for at in [3.3, 8.5, 13.1, 17.0]:
    add(at, pin(), -9)
for at, d in [(7.4, 1.0), (12.0, 1.0), (16.4, 0.9)]:
    add(at, whoosh(d), -16)
for a, d in [(7.4, 1.0), (12.0, 0.9), (16.4, 0.8)]:
    add(a + 0.05, string(d), -16)
add(12.2, drumroll(), -12)
add(12.95, crash(), -10)
for i in range(3):
    add(16.5 + i * 0.2, paper(0.15), -15)
    add(16.6 + i * 0.2, pop(600 + i * 120, 0.1), -16)
add(19.35, whoosh(0.7), -10)
add(19.9, paper(0.25), -11)
add(20.2, whoosh(0.3), -20)
add(20.65, pin(0.1), -16)
add(21.0, chime(1.0), -12)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
