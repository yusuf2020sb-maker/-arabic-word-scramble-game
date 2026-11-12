"""Reel 52 score: garden tea-party waltz on harp and flute-like tones, camera whooshes, card flicks, cup clinks and a spoon stir.

usage: python3 sfx_reel52.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng, whoosh
from sfx_reel17 import clink, pluck
from sfx_reel22 import pad

CH = [[196.0, 246.9, 293.7], [164.8, 196.0, 246.9], [130.8, 164.8, 196.0], [146.8, 185.0, 220.0]]
MEL = [587.3, 659.3, 587.3, 493.9, 440.0, 493.9, 392.0, 440.0, 493.9, 587.3, 523.3, 440.0]


def flute(f, d=0.8):
    t = np.arange(int(d * SR)) / SR
    v = 1 + 0.004 * np.sin(2 * np.pi * 5 * t)
    y = np.sin(2 * np.pi * f * v * t) + 0.2 * np.sin(4 * np.pi * f * v * t) + 0.02 * rng.standard_normal(len(t))
    return y * np.minimum(1, t / 0.06) * np.minimum(1, (d - t) / 0.15)


def party(d, bpm=132):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 2)
    for i in range(int(d / b) + 1):
        bar = (i // 3) % 4; s = int(i * b * SR)
        x = 0.3 * pluck(CH[bar][0] / 2 if i % 3 == 0 else CH[bar][i % 3], 0.8, 0.995); out[s:s + len(x)] += x[:len(out) - s]
        if i % 3 == 0:
            z = 0.05 * lowpass(pad(CH[bar], 3 * b + 0.2), 1200); out[s:s + len(z)] += z[:len(out) - s]
        m = 0.1 * flute(MEL[i % 12], b * 0.95); out[s:s + len(m)] += m[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


def glide(d=0.5):
    return 0.5 * lowpass(whoosh(d), 2500)


def flick(d=0.08):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 6000) * np.exp(-t * 60) * 0.6


def stir(d=0.6):
    return mix(*[(i * 0.12, 0.25 * clink()[:int(0.08 * SR)]) for i in range(int(d / 0.12))])


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * party(dur)), (0.05, glide(0.8)), (T['h1'], flick()), (T['h2'], flick()), (T['h2'] + 0.3, 0.4 * stir())]
    parts += [(T[k] - 0.45, glide()) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.05, flick()) for k in ('c1', 'c2', 'c3')] + [(T[k] + 0.15, 0.3 * clink()) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1], glide(0.7)), (cut[1] + 0.35, flick()), (T['n2'], flick())]
    parts += [(T[k] - 0.45, glide()) for k in ('u0', 'u1', 'u2')] + [(T[k] - 0.1, flick()) for k in ('u0', 'u1', 'u2')]
    parts += [(cut[3], glide(0.6)), (T['print'], flick()), (cut[4], glide(0.7)), (T['brand'], flick()), (T['store2'], 0.5 * clink()), (T['store2'] + 0.05, 0.5 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
