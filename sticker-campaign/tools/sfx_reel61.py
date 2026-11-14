"""Reel 61 score: romantic chamber strings (pizzicato + legato pad), camera 'zoom-out' whooshes with a reverse swell, shutter clicks and a soft stamp.

usage: python3 sfx_reel61.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel9 import stamp_thud
from sfx_reel17 import pluck
from sfx_reel22 import pad

CH = [[146.8, 220.0, 293.7, 349.2], [116.5, 233.1, 293.7, 349.2], [130.8, 196.0, 261.6, 329.6], [110.0, 220.0, 277.2, 329.6]]


def strings(d, bpm=96):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 4) % 4; s = int(i * b * SR)
        if i % 4 == 0:
            z = 0.09 * lowpass(pad(CH[bar], 4 * b + 0.6), 1300); out[s:s + len(z)] += z[:len(out) - s]
        x = 0.16 * pluck(CH[bar][1 + i % 3] * 2, 0.5, 0.99); out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.4)


def zoomout(d=0.6):
    # reverse swell into a whoosh: builds anticipation then releases
    n = int(d * SR); x = np.linspace(0, 1, n)
    sw = lowpass(rng.standard_normal(n), 600 + 5000 * x ** 2) * x ** 2 * 0.6
    return mix((0, sw), (d * 0.7, 0.7 * lowpass(whoosh(0.5), 4000)))


def shutter():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return mix((0, lowpass(rng.standard_normal(n), 6000) * np.exp(-t * 200) * 0.7), (0.06, lowpass(rng.standard_normal(n), 4000) * np.exp(-t * 250) * 0.5))


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    outs = [T['h2'] - 0.05, T['c1'] - 0.1, T['c2'] - 0.1, T['c3'] - 0.1, T['count'] - 0.3, T['u0'] - 0.1, T['u1'] - 0.1, T['u2'] - 0.1, T['print'] - 0.3, T['brand'] - 0.3]
    parts = [(T['h2'] + 0.6, 0.5 * strings(dur - T['h2'] - 0.6)), (0, 0.15 * lowpass(rng.standard_normal(int(1.6 * SR)), 300))]
    parts += [(max(0, a - 0.4), zoomout()) for a in outs] + [(a + 0.45, shutter()) for a in outs]
    parts += [(T['h2'] + 0.35, 0.7 * stamp_thud()), (T['n2'] - 0.05, 0.6 * stamp_thud()), (T['count'] + 0.2, 0.4 * sparkle())]
    parts += [(T['store2'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
