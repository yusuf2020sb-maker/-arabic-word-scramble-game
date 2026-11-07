"""Score for reel 25 (autumn tickets): fingerpicked guitar in A minor, train clatter, ticket print, punch, tear, leaf gusts.

usage: python3 sfx_reel25.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel5 import printer, thump
from sfx_reel9 import stamp_thud
from sfx_reel10 import creak, rustle
from sfx_reel17 import pluck, wind
from sfx_reel18 import bell, slide, tear

AM = [[110.0, 220.0, 261.6, 329.6], [87.3, 174.6, 220.0, 261.6], [130.8, 196.0, 261.6, 329.6], [98.0, 196.0, 246.9, 293.7]]


def guitar(d, bpm=84):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2); i = 0
    pat = [0, 2, 1, 3, 2, 1, 3, 2]
    while i * e < d:
        ch = AM[(i // 8) % 4]; f = ch[pat[i % 8]] if i % 8 else ch[0]
        x = (0.55 if i % 8 == 0 else 0.28) * pluck(f, 1.8, 0.997); s = int(i * e * SR); out[s:s + len(x)] += x[:len(out) - s]; i += 1
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 1.5)


def clatter(d):
    out = np.zeros(int(d * SR)); beat = 0.42; k = 0
    while k * beat < d:
        for off in (0, 0.11):
            s = int((k * beat + off) * SR); x = 0.5 * thump(0.12)[:max(0, len(out) - s)]
            out[s:s + len(x)] += x
        k += 1
    return lowpass(out, 900) + 0.15 * lowpass(rng.standard_normal(len(out)), 300)


def punch():
    t = np.arange(int(0.12 * SR)) / SR
    return np.sin(2 * np.pi * 900 * t) * np.exp(-t * 60) * 0.5 + rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.5


def gust(d=1.2):
    return mix((0, 0.7 * wind(d)), (0.2, 0.8 * rustle(min(0.8, d - 0.2))))


D = dict(h1=0.2, h2=1.5, tear=3.2, dest=3.9, k1=6.4, k2=7.4, k3=8.4, count=10.6, u0=13.6, u1=15.2, u2=16.8, print=18.6, brand=21.6, store=23.0, end_all=26.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T['k1'] - 0.3] + [T[k] - 0.2 for k in ('count', 'u0', 'print', 'brand')]
    parts = [(0, 0.4 * guitar(dur)), (0.15, 0.6 * printer(1.1)), (1.3, 0.35 * bell()), (T['h2'] - 0.05, punch()), (T['h2'] + 0.05, 0.6 * stamp_thud())]
    parts += [(T['tear'], 1.1 * tear(0.6)), (T['tear'] + 0.1, 0.6 * gust(1.3))]
    parts += [(c - 0.7, 0.55 * gust(1.2)) for c in cuts[1:]]
    parts += [(cuts[0], 0.5 * clatter(cuts[1] - cuts[0]))]
    parts += [(cuts[1] + 0.1 + i * 0.07 + 0.3, 0.5 * thump(0.15)) for i in range(18)]
    at = [cuts[2] + 0.05, T['u1'] - 0.35, T['u2'] - 0.35]
    parts += [(a - 0.1, 0.5 * slide(0.5)) for a in at[1:]]
    parts += [(a + 0.4 + j * 0.25 + 0.25, 0.6 * thump(0.12)) for a in at for j in range(3)]
    parts += [(cuts[3] + 0.1, 0.6 * slide(0.7)), (cuts[3] + 1.0, 0.4 * chime(0.6))]
    parts += [(cuts[4] + 0.3, 0.5 * creak(0.45)), (cuts[4] + 1.6, 0.35 * creak(0.4)), (T['store'], 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
