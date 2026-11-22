"""Reel 64 (heritage, camcorder home video) silent-version soundtrack: tape REC clunk + motor hum,
zoom-motor whine and autofocus beep, VHS glitch bursts on whip pans, sticker pops, scissor snip,
PAUSE clunk, warm hijaz pluck groove with a frame drum.

usage: python3 sfx_reel64.py <out.wav>
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, rng, whoosh
from sfx_reel17 import HIJAZ, pluck
from sfx_reel22 import pad


def clunk(d=0.22):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 1500) * np.exp(-t * 35) + 0.6 * np.sin(2 * np.pi * 120 * t) * np.exp(-t * 25)


def motor(d):
    n = int(d * SR); t = np.arange(n) / SR
    return lowpass(np.sign(np.sin(2 * np.pi * 60 * t)) + 0.3 * rng.standard_normal(n), 400) * 0.25


def zoomwhine(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR; f = 900 + 700 * t / d
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + lowpass(rng.standard_normal(n), 2500) * 0.15
    return y * np.sin(np.pi * t / d)


def beep(f=2400, d=0.07):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.minimum(1, (d - t) / 0.01) * 0.5


def glitch(d=0.25):
    n = int(d * SR); t = np.arange(n) / SR
    y = rng.standard_normal(n) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 37 * t)))
    return lowpass(y, 5000) * np.sin(np.pi * t / d) * 0.6


def snip():
    return mix((0, 0.7 * lowpass(rng.standard_normal(int(0.03 * SR)), 7000) * np.exp(-np.arange(int(0.03 * SR)) / 150)),
               (0.12, 0.8 * lowpass(rng.standard_normal(int(0.04 * SR)), 6000) * np.exp(-np.arange(int(0.04 * SR)) / 160)))


def drum(d=0.3, f=95):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t * (1 - 0.3 * t)) * np.exp(-t * 14) + 0.2 * lowpass(rng.standard_normal(len(t)), 2000) * np.exp(-t * 40)


def groove(d, bpm=100):
    b = 60 / bpm; out = np.zeros(int(d * SR) + SR * 3)
    pat = [0, 2, 3, 4, 3, 2, 1, 0]
    for i in range(int(d / b) + 1):
        s = int(i * b * SR); bar = (i // 8) % 2
        if i % 8 == 0:
            z = 0.07 * lowpass(pad([146.8, 220.0, 293.7] if bar == 0 else [130.8, 196.0, 261.6], 8 * b + 0.6), 1000); out[s:s + len(z)] += z[:len(out) - s]
        x = 0.22 * pluck(HIJAZ[pat[i % 8] + (2 if bar else 0)], 0.6, 0.994); out[s:s + len(x)] += x[:len(out) - s]
        dr = (0.35 * drum() if i % 4 in (0, 3) else 0.18 * drum(0.15, 220)); out[s:s + len(dr)] += dr[:len(out) - s]
    out = out[:int(d * SR)]; tt = np.arange(len(out)) / SR
    return out * np.minimum(1, tt / 0.5) * np.minimum(1, (d - tt) / 1.4)


D = dict(h1=0.3, h2=2.2, c1=4.0, c2=5.1, c3=6.2, count=7.5, n2=9.1, u0=10.9, u1=12.6, u2=14.0, print=15.7, print2=16.8, brand=18.8, store=20.4, store2=21.2, end_all=24.2)


def main(out_path):
    T = D; dur = T['end_all']
    parts = [(0, 0.8 * clunk()), (0, motor(dur)[: int(dur * SR)] * 0.25), (T['h2'] + 0.1, 0.5 * groove(dur - T['h2'] - 0.1))]
    parts += [(T['h2'] - 0.45, 0.6 * zoomwhine(0.4)), (T['h2'] - 0.3, 0.5 * glitch())]
    for k in (T['c1'], T['c2'], T['c3']):
        parts += [(k - 0.45, 0.6 * zoomwhine(0.35)), (k - 0.08, beep()), (k - 0.01, 0.8 * beep(3000, 0.05))]
    for w in (T['count'], T['u0'], T['u1'], T['u2'], T['print'], T['brand']):
        parts += [(w - 0.45, 0.6 * whoosh(0.35)), (w - 0.35, 0.5 * glitch())]
    parts += [(T['count'] - 0.1 + i * 0.04, 0.15 * pop()) for i in range(15)]
    parts += [(T['print2'] - 0.4, snip()), (T['store2'] + 0.6, 0.8 * clunk()), (T['store2'], 0.45 * chime(1.4))]
    y = norm(mix(*parts)[:int(dur * SR)], -1.5)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main(sys.argv[1])
