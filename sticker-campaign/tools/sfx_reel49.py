"""Reel 49 score: heritage groove on plucked oud-like strings and a darbuka pattern, loom shuttle clacks, weave swishes and a coffee pour.

usage: python3 sfx_reel49.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, sparkle
from sfx_reel14 import pour
from sfx_reel16 import wood
from sfx_reel17 import HIJAZ, pluck


def dum(d=0.25):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * (70 + 80 * np.exp(-t * 25)) * t) * np.exp(-t * 14)


def tek(d=0.08):
    n = int(d * SR); t = np.arange(n) / SR
    return (lowpass(rng.standard_normal(n), 7000) * 0.5 + np.sin(2 * np.pi * 900 * t)) * np.exp(-t * 60) * 0.6


def groove(d, bpm=96):
    # maqsum-like pattern on 8 eighths: D T - T D - T -
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2)
    pat = ['D', 'T', '', 'T', 'D', '', 'T', '']
    mel = [0, 1, 2, 3, 4, 3, 2, 1, 0, 2, 4, 5, 4, 2, 1, 0]
    for i in range(int(d / e) + 1):
        s = int(i * e * SR); h = pat[i % 8]
        x = 0.5 * dum() if h == 'D' else (0.3 * tek() if h == 'T' else None)
        if x is not None:
            out[s:s + len(x)] += x[:len(out) - s]
        if i % 2 == 0:
            f = HIJAZ[mel[(i // 2) % 16] % len(HIJAZ)]
            y = 0.22 * pluck(f, 0.8, 0.995); out[s:s + len(y)] += y[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.4) * np.minimum(1, (d - tt) / 1.3)


def shuttle(n=16, gap=0.016):
    # loom: rapid wooden clacks plus a thread swish
    return mix(*[(i * gap, 0.25 * wood(0.06)) for i in range(0, n, 2)], (0, 0.5 * lowpass(rng.standard_normal(int(0.45 * SR)), 2500) * np.sin(np.linspace(0, np.pi, int(0.45 * SR)))))


D = dict(h1=0.3, h2=1.4, c1=3.2, c2=4.6, c3=6.0, count=7.8, n2=9.2, u0=10.8, u1=12.0, u2=13.2, print=15.0, print2=16.1, brand=17.8, store=19.4, store2=20.1, end_all=23.0)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * groove(dur)), (0.05, 0.6 * shuttle()), (0.35, 0.5 * pour(0.6)), (T['h2'], 0.5 * dum())]
    parts += [(c - 0.42, shuttle()) for c in cut] + [(c + 0.05, 0.6 * shuttle()) for c in cut]
    parts += [(T[k] - 0.3, 0.4 * sparkle(0.35)) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1] + 0.2 + i * 0.06, 0.25 * wood(0.06)) for i in range(12)] + [(T['n2'], 0.5 * dum())]
    parts += [(a + 0.4, 0.4 * dum()) for a in (cut[2] + 0.1, T['u1'] - 0.3, T['u2'] - 0.3)]
    parts += [(cut[4] + 0.3, 0.6 * dum()), (T['store2'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
