"""Sound effects for reel 19 (which stamp are you: album shuffle, spotlight, reveals).

usage: python3 sfx_reel19.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick
from sfx_reel18 import postmark, tear, typing

DUR = 24.5
REV = [6.6, 9.0, 11.4, 13.8]


def swish(d=0.35):
    # card shuffle swish with a papery flutter
    n = int(d * SR); t = np.linspace(0, 1, n)
    flutter = 0.6 + 0.4 * np.sin(2 * np.pi * 45 * t * d)
    return lowpass(rng.standard_normal(n), 2500 + 3000 * t) * np.sin(np.pi * t) * flutter


def reveal(f):
    # soft bell + shimmer, tuned per stamp
    t = np.arange(int(1.4 * SR)) / SR
    bell = sum(np.sin(2 * np.pi * f * m * t) * a * np.exp(-t * d) for m, a, d in [(1, 1, 2.5), (2.01, .5, 3.5), (3.02, .25, 5)])
    return mix((0, bell * np.minimum(1, t * 200)), (0.05, 0.4 * sparkle(0.5)))


EVENTS = []
add = lambda at, sig, db: EVENTS.append((at, norm(sig, db)))
add(0.15, whoosh(0.4), -15)
add(0.8, mix((0, thump(0.3)), (0.02, pop(500, 0.18))), -8)
add(1.7, pop(700, 0.12), -14)
add(3.0, whoosh(0.5), -14)
for at in [3.3, 4.0, 4.7]:
    for k in range(4):
        add(at + k * 0.06, swish(0.3), -17)
add(4.9, mix(*[(k * 0.06, pop(800 + k * 120, 0.08)) for k in range(4)]), -15)   # numbers pop on
for k in range(int((6.6 - 5.0) * 4)):
    add(5.0 + k * 0.25, tick(0.03), -16)                                         # spotlight hops
for i, (a, f) in enumerate(zip(REV, [523, 659, 784, 988])):
    add(a, whoosh(0.4), -16)
    add(a + 0.35, reveal(f), -10)
add(16.4, whoosh(0.5), -14)
add(16.6, pop(600, 0.14), -13)
add(16.8, typing(8, 0.25), -16)
add(18.8, pop(750, 0.12), -15)
add(19.8, whoosh(0.5), -14)
for i in range(3):
    add(20.2 + i * 0.15, pop(600 + i * 100, 0.1), -15)
add(20.6, tear(0.25), -12)
add(20.95, postmark(), -8)
add(21.4, chime(1.0), -12)


def main(out_path):
    y = norm(mix(*EVENTS, (DUR, np.zeros(1)))[:int(DUR * SR)], -1.5)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
