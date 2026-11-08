"""Score for reel 27 (Saudi heritage): oud-style Hijaz plucks over a daf groove, coffee pour, tray clinks, desert wind.

usage: python3 sfx_reel27.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle, whoosh
from sfx_reel14 import pour
from sfx_reel17 import HIJAZ, clink, pluck, wind
from sfx_reel18 import bell


def daf(accent=True):
    t = np.arange(int(0.3 * SR)) / SR
    body = np.sin(2 * np.pi * (95 if accent else 160) * t) * np.exp(-t * (14 if accent else 30))
    jingle = lowpass(rng.standard_normal(len(t)), 7000) * np.exp(-t * 25) * (0.25 if accent else 0.4)
    return 0.8 * body + jingle


def oud(f, d=1.0):
    return mix((0, pluck(f, d, 0.994)), (0, 0.3 * pluck(f * 2.003, d * 0.6, 0.99)))


MEL = [0, 1, 2, 1, 3, 2, 1, 0, 4, 3, 2, 3, 1, 2, 1, 0]


def groove(d, bpm=96):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 2); i = 0
    while i * b / 2 < d:
        s = int(i * b / 2 * SR)
        if i % 8 in (0, 3, 6):
            x = 0.5 * daf(i % 8 == 0); out[s:s + len(x)] += x[:len(out) - s]
        elif i % 2 == 1:
            x = 0.2 * daf(False); out[s:s + len(x)] += x[:len(out) - s]
        if i % 2 == 0:
            x = 0.35 * oud(HIJAZ[MEL[(i // 2) % 16]], 0.9); out[s:s + len(x)] += x[:len(out) - s]
        i += 1
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 1.4)


def thud():
    t = np.arange(int(0.18 * SR)) / SR
    return np.sin(2 * np.pi * 110 * t) * np.exp(-t * 30) + 0.3 * lowpass(rng.standard_normal(len(t)), 2000) * np.exp(-t * 60)


D = dict(h1=0.2, h2=1.5, i0=3.6, i1=4.5, i2=5.4, i3=6.3, d0=8.0, d1=8.9, d2=9.8, d3=10.7, title=12.3, t2=13.3, u0=15.0, u1=16.4, u2=17.8, print=19.4, brand=22.2, store=23.6, end_all=26.5)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.3 for k in ('i0', 'd0', 'title', 'u0', 'print', 'brand')]
    parts = [(0, 0.4 * groove(dur)), (1.0, 0.7 * pour(1.4)), (T['h2'], 0.5 * daf())]
    parts += [(c - 0.35, 0.5 * whoosh(0.7)) for c in cuts]
    parts += [(a + 0.2, 0.7 * thud()) for a in (T['i0'] - 0.15, T['i1'] - 0.15, T['i2'] - 0.15, T['i3'] - 0.15)]
    parts += [(a + 0.3, 0.4 * clink()) for a in (T['i0'] - 0.15, T['i1'] - 0.15)]
    parts += [(cuts[1], 0.4 * wind(3.0)), (T['d0'] - 0.2, 0.4 * whoosh(0.9)), (T['d2'] - 0.2, 0.3 * bell())]
    parts += [(T['d3'] - 0.25, 0.5 * daf())]
    parts += [(cuts[2] + 0.1 + i * 0.05, 0.25 * oud(HIJAZ[i % 8] * 2, 0.4)) for i in range(12)]
    parts += [(a + 0.35 + j * 0.25 + 0.25, 0.6 * thud()) for a in (cuts[3] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3) for j in range(2 if a != T['u1'] - 0.3 else 3)]
    parts += [(cuts[4] + 0.1, 0.4 * whoosh(0.6)), (cuts[4] + 1.0, 0.4 * chime(0.6))]
    parts += [(T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
