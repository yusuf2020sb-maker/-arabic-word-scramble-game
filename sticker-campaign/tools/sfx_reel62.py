"""Reel 62 (stamps, envelope delivery) silent-version soundtrack: phone-buzz envelope, seal pop, flap,
stamps flying out, perforated-sheet clacks, typing, whip pans, mail-slot printer, postmark, jazz bed.

usage: python3 sfx_reel62.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel5 import printer
from sfx_reel16 import page
from sfx_reel18 import clack, postmark, typing
from sfx_reel42 import jazz


def buzz(d=0.5):
    # phone vibration: low rattly hum with a tremolo
    n = int(d * SR); t = np.arange(n) / SR
    y = np.sign(np.sin(2 * np.pi * 150 * t)) * 0.5 + np.sin(2 * np.pi * 75 * t)
    y = lowpass(y, 500) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t)))
    return y * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.03)


def whip(d=0.35):
    n = int(d * SR); x = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 800 + 6000 * np.sin(np.pi * x)) * np.sin(np.pi * x) ** 1.5


D = dict(h1=0.05, h2=1.6, c1=3.2, c2=4.5, c3=5.8, count=7.4, n2=9.0, u0=10.8, u1=12.2, u2=13.5, print=15.2, print2=16.3, brand=18.0, store=19.8, store2=20.6, end_all=23.6)


def main(out_path):
    T = D; dur = T['end_all']
    parts = [(T['h2'] + 0.2, 0.45 * jazz(dur - T['h2'] - 0.2))]
    t = 0.0
    while t < T['h2'] - 0.6:
        parts.append((t, 0.5 * buzz(min(0.5, T['h2'] - 0.6 - t)))); t += 0.9
    parts += [(T['h2'] - 0.55, 0.7 * pop()), (T['h2'] - 0.5, 0.6 * page())]
    for k in (T['c1'], T['c2'], T['c3']):
        parts += [(k - 0.45, 0.5 * whoosh(0.4)), (k - 0.1, 0.4 * pop())]
    parts += [(T['count'] - 0.45 + i * 0.025 + 0.38, 0.12 * clack(0.08)) for i in range(16)]
    parts += [(T['n2'] - 0.55, 0.4 * whoosh(0.3)), (T['n2'] - 0.35, 0.6 * typing(6, 0.05))]
    parts += [(k - 0.45, 0.5 * whip()) for k in (T['u0'], T['u1'] + 0.05, T['u2'] + 0.05, T['print'])]
    parts += [(T['print'] - 0.4, 0.35 * printer(0.9))]
    parts += [(T['brand'] - 0.45, 0.5 * whoosh(0.4)), (T['brand'] - 0.08, 0.9 * postmark()), (T['store2'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
