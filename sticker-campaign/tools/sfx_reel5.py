"""Sound effects for reel 5 (stop-motion), each placed on the visual event it belongs to.

usage: python3 sfx_reel5.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh

DUR = 22.5


def pop(f0=700, d=0.14):
    n = int(d * SR); t = np.arange(n) / SR
    f = f0 * np.exp(-t * 28) + f0 * 0.22
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 32)
    y[:50] += rng.standard_normal(50) * 0.5
    return y


def boing(d=0.45):
    n = int(d * SR); t = np.arange(n) / SR
    f = 220 + 260 * np.exp(-t * 6) + 25 * np.sin(2 * np.pi * 14 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)


def scribble(d=0.5):
    # marker on paper: band-limited noise with fast stroke tremolo
    n = int(d * SR); t = np.arange(n) / SR
    y = lowpass(rng.standard_normal(n), 4500) - lowpass(rng.standard_normal(n), 900)
    return y * (0.55 + 0.45 * np.sin(2 * np.pi * 11 * t)) * np.sin(np.pi * t / d) ** 0.5


def printer(d=0.5):
    # short motor push: buzzy low tone + mechanical clicks
    n = int(d * SR); t = np.arange(n) / SR
    buzz = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.4 + np.sin(2 * np.pi * 220 * t) * 0.3
    clicks = np.zeros(n)
    for k in range(0, n, int(SR / 16)):
        clicks[k:k + 200] += rng.standard_normal(min(200, n - k)) * np.exp(-np.arange(min(200, n - k)) / 40)
    return lowpass(buzz, 1800) * np.sin(np.pi * t / d) ** 0.3 + 0.6 * clicks


def rip(d=0.9):
    # sticker peel: crackly noise that rises then releases
    n = int(d * SR); t = np.linspace(0, 1, n)
    crackle = rng.standard_normal(n) * (rng.random(n) > 0.75)
    y = lowpass(crackle, 2000 + 5000 * t) * np.sin(np.pi * t) ** 0.8
    return y + 0.4 * lowpass(rng.standard_normal(n), 1200) * np.sin(np.pi * t)


def rattle(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    taps = np.zeros(n)
    for k in range(0, n, int(SR / 15)):
        m = min(300, n - k); taps[k:k + m] += np.sin(2 * np.pi * 900 * np.arange(m) / SR) * np.exp(-np.arange(m) / 50)
    return taps * 0.6


def thump(d=0.25):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 18)


# (start second, signal, peak dB)
EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))

# S1: sticker slaps, the "إيه!" boing, marker underline
for i, at in enumerate([0.4, 0.65, 0.9, 1.15]):
    add(at, pop(600 + i * 120), -10)
add(0.25, pop(450, 0.18), -9)
add(1.6, boing(), -8)
add(1.9, scribble(0.5), -14)
# colour-bar wipes at every cut
for c in [3.4, 7.0, 13.4, 17.4]:
    add(c - 0.3, whoosh(0.6), -11)
# S2: printer pushes
for at in [3.8, 4.8, 5.8]:
    add(at, printer(0.5), -12)
# S3: title pop, then each beat: swish + sticker pop
add(7.2, pop(500, 0.18), -9)
for i in range(4):
    at = 8.2 + i * 1.3
    add(at, whoosh(0.25), -14)
    add(at + 0.25, pop(650 + i * 90), -9)
# S4: 12 quick pops rising in pitch, then the chips land
for i in range(12):
    add(13.6 + i * 0.125, pop(500 + i * 45, 0.1), -13)
add(15.2, thump(), -8)
# S5: cover wiggles, peels off, marker circle, final chime
add(18.0, rattle(1.0), -18)
add(19.0, rip(0.9), -10)
add(20.1, scribble(0.6), -14)
add(20.8, chime(0.9), -11)


def main(out_path):
    y = mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)]
    y = norm(y, -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
