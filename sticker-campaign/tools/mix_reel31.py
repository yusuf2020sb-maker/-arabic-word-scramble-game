"""Reel 31 soundtrack with voiceover: motion-graphics hits only in the gaps; timeline keys anchored to the hits.

usage: python3 mix_reel31.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, sparkle, whoosh
from sfx_reel5 import boing
from sfx_reel9 import zip_sweep
from sfx_reel29 import beat, slam

V = [(0.23, 1.82), (1.95, 2.80), (3.30, 3.79), (4.32, 5.23), (5.88, 7.84), (8.20, 9.19), (9.23, 9.91), (10.14, 10.79), (11.48, 11.93),
     (12.37, 12.83), (13.17, 13.49), (14.09, 14.76), (15.10, 15.93), (16.07, 17.37), (18.02, 19.10), (19.60, 20.13)]
SEG = dict(zip(["h1", "h2", "j1", "j2", "count", "k0", "k1", "k2", "s0", "s1", "s2", "u0", "u1", "u2", "brand", "store"], V))
cut = lambda x, d: x[:int(d * SR)]
PLAN = [
    ("fx", cut(slam(), 0.3), {"h1": 0.0}), ("vo", "h1", {}),
    ("fx", cut(boing(0.4), 0.3), {"h2": 0.0}), ("vo", "h2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.35)), (0.3, 0.5 * pop(0.12))), {"j1": 0.3}), ("vo", "j1", {}),
    ("fx", cut(slam(), 0.35), {"j2": 0.05}), ("vo", "j2", {}),
    ("fx", mix((0, 0.6 * zip_sweep(0.45)), (0.45, 0.6 * zip_sweep(0.4)), (0.7, cut(slam(), 0.4))), {"count": 0.2}), ("vo", "count", {}),
    ("fx", mix((0, 0.5 * whoosh(0.3)), (0.3, 0.5 * pop(0.12))), {"k0": 0.15}), ("vo", "k0", {}),
    ("fx", mix((0, 0.5 * whoosh(0.3)), (0.3, 0.5 * pop(0.12))), {"k1": 0.15}), ("vo", "k1", {}),
    ("fx", mix((0, 0.5 * whoosh(0.3)), (0.3, 0.5 * pop(0.12))), {"k2": 0.15}), ("vo", "k2", {}),
    ("fx", cut(boing(0.35), 0.35), {"s0": 0.1}), ("vo", "s0", {}),
    ("fx", cut(boing(0.35), 0.35), {"s1": 0.1}), ("vo", "s1", {}),
    ("fx", cut(boing(0.35), 0.35), {"s2": 0.1}), ("vo", "s2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.35)), (0.3, cut(slam(), 0.4))), {"u0": 0.2}), ("vo", "u0", {}),
    ("fx", mix((0, cut(slam(), 0.35)), (0.3, 0.4 * pop(0.1))), {"u1": 0.2}), ("vo", "u1", {}),
    ("fx", mix((0, cut(slam(), 0.35)), (0.3, 0.4 * pop(0.1))), {"u2": 0.2}), ("vo", "u2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.35)), (0.3, cut(slam(), 0.4)), (0.4, 0.4 * sparkle(0.4))), {"brand": 0.25}), ("vo", "brand", {}),
    ("fx", np.zeros(int(0.08 * SR)), {}), ("vo", "store", {"store": 0}),
    ("fx", mix((0, 0.8 * beat(2.2)), (0.1, 0.6 * chime(1.4))), {}),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.05
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else (norm(item, -12) if np.abs(item).max() > 0 else item)
        for k, off in keys.items():
            tl[k] = round(t + off, 3)
        out += [x, np.zeros(int(GAP * SR))]; t += len(x) / SR + GAP
    tl["end_all"] = round(t + 0.2, 3)
    y = np.clip(np.concatenate(out + [np.zeros(int(0.3 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    with open(tl_path, "w") as f:
        f.write("window.TL = " + json.dumps(tl) + ";\n")
    print(json.dumps(tl))


if __name__ == "__main__":
    main(*sys.argv[1:4])
