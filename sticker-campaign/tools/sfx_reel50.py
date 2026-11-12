"""Reel 50 score: rainy-window lullaby on soft felt piano over rain ambience, distant thunder, finger squeaks on glass and a fireplace crackle.

usage: python3 sfx_reel50.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng
from sfx_reel16 import crackle, rain, squeak, thunder
from sfx_reel22 import pad, piano

# Fmaj7 - Em7 - Dm7 - Cmaj7, slow and sparse
CH = [[174.6, 220.0, 261.6, 329.6], [164.8, 196.0, 246.9, 293.7], [146.8, 174.6, 220.0, 261.6], [130.8, 164.8, 196.0, 246.9]]
MEL = [659.3, 587.3, 523.3, 493.9, 523.3, 440.0, 392.0, 440.0]


def felt(d, bpm=70):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    for i in range(int(d / b) + 1):
        bar = (i // 4) % 4; s = int(i * b * SR)
        if i % 4 == 0:
            z = mix(*[(0.03 * j, 0.10 * lowpass(piano(f, 3.0), 1500)) for j, f in enumerate(CH[bar])]); out[s:s + len(z)] += z[:len(out) - s]
            q = 0.04 * lowpass(pad(CH[bar], 4 * b + 0.4), 700); out[s:s + len(q)] += q[:len(out) - s]
        if i % 2 == 1:
            m = 0.12 * lowpass(piano(MEL[(i // 2) % 8], 1.6), 2500); out[s:s + len(m)] += m[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 1.0) * np.minimum(1, (d - tt) / 1.6)


def wipe(d=0.45):
    # cloth/palm wipe on glass: breathy band-limited noise swell
    n = int(d * SR); x = np.linspace(0, 1, n)
    return (lowpass(rng.standard_normal(n), 3500) - lowpass(rng.standard_normal(n), 600)) * np.sin(np.pi * x) * 0.45


def breath(d=0.4):
    n = int(d * SR); x = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 1200) * np.sin(np.pi * x) ** 2 * 0.5


D = dict(h1=0.3, h2=1.5, c1=3.4, c2=4.8, c3=6.2, count=8.0, n2=9.4, u0=11.0, u1=12.2, u2=13.4, print=15.2, print2=16.3, brand=18.0, store=19.6, store2=20.3, end_all=23.4)


def main(out_path):
    T = D; dur = T['end_all']
    cut = [T['c1'] - 0.4, T['count'] - 0.35, T['u0'] - 0.35, T['print'] - 0.35, T['brand'] - 0.35]
    parts = [(0, 0.5 * felt(dur)), (0, 0.35 * rain(dur)), (0.1, 0.3 * thunder(2.0)), (T['h1'], 0.4 * squeak(0.6)), (T['h2'], 0.4 * squeak(0.6)), (T['h2'] + 0.25, 0.5 * wipe()), (T['h2'] + 0.3, 0.25 * crackle(1.5))]
    parts += [(c, breath()) for c in cut]
    parts += [(T[k] - 0.3, 0.5 * wipe()) for k in ('c1', 'c2', 'c3')] + [(T[k] - 0.05, 0.35 * squeak(0.45)) for k in ('c1', 'c2', 'c3')]
    parts += [(cut[1] + 0.3 + i * 0.07, 0.15 * wipe(0.25)) for i in range(12)] + [(cut[1] + 0.1, 0.4 * squeak(0.5)), (T['n2'], 0.35 * squeak(0.5))]
    parts += [(a, 0.5 * wipe()) for a in (cut[2] + 0.05, T['u1'] - 0.3, T['u2'] - 0.3)]
    parts += [(cut[3] + 0.2, 0.5 * wipe(0.5)), (T['print'], 0.3 * squeak(0.45)), (T['print2'], 0.3 * squeak(0.5))]
    parts += [(cut[4] + 0.25, 0.5 * wipe(0.5)), (T['brand'], 0.3 * squeak(0.6)), (T['store2'], 0.4 * squeak(0.5)), (T['store2'] + 0.1, 0.5 * chime(1.6))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
