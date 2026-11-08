"""Score for reel 34 (journal, scrapbook stop-motion): ukulele strum groove with shaker,
pencil scribbles, tape rips, paper slaps, scissor snips and a page-flip sweep at each cut.

usage: python3 sfx_reel34.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, rng
from sfx_reel5 import rip, scribble
from sfx_reel13 import paper
from sfx_reel16 import page
from sfx_reel17 import pluck
from sfx_reel24 import snip

UKE = [[261.6, 329.6, 392.0, 523.3], [220.0, 261.6, 329.6, 440.0], [174.6, 220.0, 261.6, 349.2], [196.0, 246.9, 293.7, 392.0]]


def strum(ch, down=True, amp=0.3):
    notes = ch if down else ch[::-1]
    return mix(*[(i * 0.012, amp * pluck(f, 0.7, 0.993)) for i, f in enumerate(notes)])


def shaker():
    t = np.arange(int(0.06 * SR)) / SR
    return lowpass(rng.standard_normal(len(t)), 8000) * np.sin(np.pi * t / 0.06) * 0.25


def groove(d, bpm=110):
    e = 60 / bpm / 2; out = np.zeros(int(d * SR) + SR * 2); pat = [1, 0, 1, 1, 0, 1, 1, 0]
    for i in range(int(d / e) + 1):
        s = int(i * e * SR); ch = UKE[(i // 8) % 4]; parts = [shaker()]
        if pat[i % 8]: parts.append(strum(ch, i % 2 == 0, 0.32 if i % 8 == 0 else 0.2))
        for x in parts:
            out[s:s + len(x)] += x[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.4) * np.minimum(1, (d - tt) / 1.2)


D = dict(h1=0.2, h2=1.4, k0=3.2, k1=4.0, k2=4.8, k3=5.6, count=7.0, c2=8.0, s0=9.6, s1=10.4, s2=11.2, print=13.2, brand=15.8, store=17.2, end_all=20.0)


def main(out_path):
    T = D; dur = T['end_all']; cuts = [T[k] - 0.25 for k in ('k0', 'count', 's0', 'print', 'brand')]
    parts = [(0, 0.45 * groove(dur)), (T['h1'], 0.4 * scribble(0.5)), (0.5, 0.4 * scribble(0.8)), (T['h2'] + 0.3, 0.5 * scribble(0.5))]
    parts += [(c - 0.3, 0.7 * page(0.5)) for c in cuts]
    for k in ('k0', 'k1', 'k2', 'k3'):
        a = T[k] - 0.15; parts += [(a, 0.6 * paper(0.15)), (a + 0.2, 0.5 * rip(0.25)), (a + 0.35, 0.35 * scribble(0.35))]
    parts += [(T['count'] - 0.1, 0.7 * paper(0.15)), (T['count'] + 0.15, 0.7 * paper(0.15)), (T['c2'] - 0.1, 0.5 * rip(0.25))]
    parts += [(T['count'] + 0.5 + i * 0.17, 0.4 * paper(0.12)) for i in range(6)]
    parts += [(T['s0'] - 0.1 + i * 0.16, 0.5 * snip()) for i in range(int((T['s1'] - T['s0']) / 0.16))]
    parts += [(T['s1'] - 0.05, 0.6 * rip(0.3))] + [(T['s2'] - 0.2 + i * 0.08, 0.3 * paper(0.1)) for i in range(13)]
    parts += [(cuts[3] + 0.1, 0.5 * paper(0.2)), (cuts[3] + 0.9, 0.5 * rip(0.25)), (cuts[3] + 1.05, 0.5 * rip(0.25))]
    parts += [(cuts[4] + 0.2, 0.6 * paper(0.2)), (cuts[4] + 0.55, 0.5 * rip(0.25)), (cuts[4] + 0.65, 0.5 * rip(0.25)), (T['store'] + 0.4, 0.4 * scribble(0.5)), (T['store'], 0.6 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
