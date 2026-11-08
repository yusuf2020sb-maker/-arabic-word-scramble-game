"""Score for reel 28 (Saudi night majlis): rababa-like bowed melody over a drone and hand claps, fire crackle, crickets,
coin scratch, light clicks, pin drops, printer.

usage: python3 sfx_reel28.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, sparkle, whoosh
from sfx_reel5 import printer, thump
from sfx_reel8 import tick
from sfx_reel10 import creak
from sfx_reel14 import scratch
from sfx_reel16 import crackle
from sfx_reel17 import HIJAZ
from sfx_reel22 import pad


def bow(f, d):
    t = np.arange(int(d * SR)) / SR
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.3)
    ph = np.cumsum(f * vib) / SR
    y = sum(np.sin(2 * np.pi * ph * m) / m ** 1.2 for m in range(1, 7))
    return lowpass(y, 2400) * np.minimum(1, t / 0.12) * np.minimum(1, (d - t) / 0.15)


def clap():
    t = np.arange(int(0.12 * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 3500) * (np.exp(-t * 40) + 0.6 * np.exp(-np.maximum(0, t - 0.012) * 45) * (t > 0.012))


def crickets(d):
    t = np.arange(int(d * SR)) / SR
    chirp = (np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 30 * t) > 0.6) * (np.sin(2 * np.pi * 1.3 * t) > 0))
    return 0.15 * chirp


MEL = [(0, 1), (1, .5), (2, .5), (3, 1), (2, .5), (1, .5), (0, 2), (4, 1), (3, .5), (2, .5), (3, 1), (1, 1), (0, 2)]


def samri(d, bpm=88):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    drone = 0.25 * pad([73.4, 146.8, 220.0], d + 1); out[:len(drone)] += drone[:len(out)]
    i = 0
    while i * b < d:
        for off in ((0, 0.5) if i % 2 == 0 else (0,)):
            s = int((i + off) * b * SR); x = 0.35 * clap(); out[s:s + len(x)] += x[:len(out) - s]
        i += 1
    tt, k = 0.0, 0
    while tt < d:
        n, ln = MEL[k % len(MEL)]; x = 0.22 * bow(HIJAZ[n], ln * b * 0.95); s = int(tt * SR); out[s:s + len(x)] += x[:len(out) - s]; tt += ln * b; k += 1
    out = out[:int(d * SR)]; t2 = np.arange(len(out)) / SR
    return out * np.minimum(1, t2 / 0.6) * np.minimum(1, (d - t2) / 1.4)


D = dict(h1=0.2, h2=0.9, oud=3.0, dal=5.2, her=7.6, title=9.8, t2=11.0, u0=13.0, u1=14.6, u2=16.2, print=17.8, brand=20.8, store=22.2, end_all=25.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.25 for k in ('oud', 'dal', 'her', 'title', 'u0', 'print', 'brand')]
    parts = [(0, 0.45 * samri(dur)), (0, 0.5 * crackle(dur)), (0, crickets(dur))]
    parts += [(c - 0.4, 0.4 * whoosh(0.6)) for c in cuts]
    parts += [(cuts[0] + 0.3, 0.3 * lowpass(rng.standard_normal(int(1.5 * SR)), 900) * np.hanning(int(1.5 * SR)))]
    parts += [(cuts[1] + 0.3, 0.6 * scratch(cuts[2] - cuts[1] - 0.8))]
    parts += [(cuts[2] + 0.1 + i * 0.06, 0.4 * tick(0.02)) for i in range(11)]
    parts += [(cuts[3] + 0.5 + i * 0.22, 0.5 * pop(0.12)) for i in range(6)]
    parts += [(cuts[4] + 0.5, 0.6 * creak(0.4)), (cuts[4] + 0.8, 0.5 * sparkle(0.5))]
    parts += [(T['u1'] - 0.05 + i * 0.15 + 0.3, 0.6 * thump(0.15)) for i in range(3)]
    parts += [(T['u2'], 0.5 * whoosh(0.4))]
    parts += [(cuts[5] + 0.3, 0.6 * printer(1.7))]
    parts += [(cuts[6] + 0.3, 0.4 * creak(0.45)), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
