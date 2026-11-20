"""Reel 63 (herbal tea, liquid motion) silent-version soundtrack: pour into the hook text, tea flood wipes,
bloops as stickers surface, splashes for the sticker rain, warm oud-like plucked tune.

usage: python3 sfx_reel63.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng
from sfx_reel14 import pour
from sfx_reel17 import pluck
from sfx_reel22 import pad

CH = [[146.8, 220.0, 293.7], [130.8, 196.0, 261.6], [116.5, 174.6, 233.1], [130.8, 196.0, 261.6]]
MEL = [587.3, 523.3, 466.2, 440.0, 466.2, 523.3, 440.0, 392.0]


def tune(d, bpm=88):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 4) % 4; s = int(i * b * SR)
        if i % 4 == 0:
            z = 0.08 * lowpass(pad(CH[bar], 4 * b + 0.6), 1100); out[s:s + len(z)] += z[:len(out) - s]
        x = 0.25 * pluck(CH[bar][0], 0.8, 0.993); out[s:s + len(x)] += x[:len(out) - s]
        if i % 2 == 0:
            y = 0.18 * pluck(MEL[(i // 2) % 8], 0.5, 0.995); out[s:s + len(y)] += y[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


def flood(d=0.6):
    # rising slosh of liquid: filtered noise swelling, then a gurgling drain
    n = int(d * SR); x = np.linspace(0, 1, n)
    y = lowpass(rng.standard_normal(n), 300 + 1600 * np.sin(np.pi * x)) * np.sin(np.pi * x) ** 1.2
    g = np.zeros(n)
    for k in range(10):
        s = int((0.45 + 0.5 * rng.random()) * (n - 1600)); m = 1500; tt = np.arange(m) / SR; f = 200 + rng.random() * 300
        g[s:s + m] += 0.4 * np.sin(2 * np.pi * (f + 700 * tt) * tt) * np.exp(-tt * 35)
    return y + g


def bloop(f=380, d=0.18):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * (f + 1400 * t) * t) * np.exp(-t * 22)


def splash(d=0.25):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 3500) * np.exp(-t * 18) * 0.6 + 0.5 * bloop(260, d)


D = dict(h1=0.4, h2=2.0, c1=3.4, c2=4.6, c3=5.8, count=7.3, n2=9.0, u0=10.6, u1=12.0, u2=13.4, print=15.0, print2=16.1, brand=17.8, store=19.6, store2=20.4, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    parts = [(0, 0.55 * pour(T['h2'] - 0.5)), (T['h2'] + 0.1, 0.5 * tune(dur - T['h2'] - 0.1))]
    parts += [(w - 0.4, 0.6 * flood()) for w in (T['h2'], T['count'], T['u0'], T['u1'], T['u2'], T['print'], T['brand'])]
    parts += [(k - 0.25, 0.5 * bloop(300 + 60 * i)) for i, k in enumerate((T['c1'], T['c2'], T['c3']))]
    parts += [(T['count'] + 0.1 + j * 0.07, 0.18 * splash()) for j in range(12)]
    parts += [(T['print'] + 0.1, 0.4 * bloop(250, 0.3)), (T['store2'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
