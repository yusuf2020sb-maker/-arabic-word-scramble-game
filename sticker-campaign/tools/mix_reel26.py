"""Reel 26 soundtrack with voiceover: effects only in the gaps; timeline keys anchored to the effects.

usage: python3 mix_reel26.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle, whoosh
from sfx_reel9 import stamp_thud
from sfx_reel10 import rustle
from sfx_reel18 import crack, slide
from sfx_reel22 import piano
from sfx_reel26 import drawer, flap, riffle

V = [(0.18, 0.75), (1.21, 2.70), (3.45, 4.22), (4.66, 5.55), (6.29, 6.92), (7.30, 8.28), (9.00, 9.74), (10.21, 10.78), (11.26, 11.85),
     (12.34, 13.01), (13.98, 14.84), (15.62, 16.16), (16.72, 17.12), (17.77, 18.20), (18.59, 19.12), (20.01, 21.84), (22.55, 23.15),
     (23.73, 24.41), (24.87, 26.07), (27.00, 27.75), (28.16, 29.25), (29.93, 30.94), (31.49, 32.02)]
NAMES = ["h1", "h2", "h3", "h4", "title", "t2", "k0", "k1", "k2", "k3", "colors", "c0", "c1", "c2", "c3", "count", "u0", "u1", "u2", "print", "print2", "brand", "store"]
SEG = dict(zip(NAMES, V))
fl = lambda: 0.6 * flap(8, 0.06)
PLAN = [
    ("fx", 0.5 * slide(0.3), {"h1": 0.15}), ("vo", "h1", {}), ("vo", "h2", {"h2": 0}),
    ("fx", mix((0, crack(0.3)), (0.3, 0.5 * slide(0.4))), {"open": 0.0}), ("vo", "h3", {"h3": 0}),
    ("fx", mix((0, 0.8 * rustle(0.6)), (0.1, 0.5 * sparkle(0.5))), {"h4": 0.1}), ("vo", "h4", {}),
    ("fx", mix((0, fl()), (0.25, 0.5 * whoosh(0.4))), {"title": 0.45}), ("vo", "title", {}), ("vo", "t2", {"t2": 0}),
    ("fx", mix((0, fl()), (0.25, 0.5 * whoosh(0.35))), {"k0": 0.4}), ("vo", "k0", {}),
    ("fx", 0.5 * whoosh(0.3), {"k1": 0.15}), ("vo", "k1", {}),
    ("fx", 0.5 * whoosh(0.3), {"k2": 0.15}), ("vo", "k2", {}),
    ("fx", 0.5 * whoosh(0.3), {"k3": 0.15}), ("vo", "k3", {}),
    ("fx", mix((0, fl()), (0.2, 0.4 * whoosh(0.4))), {"colors": 0.45}), ("vo", "colors", {}),
    ("fx", drawer(), {"c0": 0.2}), ("vo", "c0", {}),
    ("fx", drawer(), {"c1": 0.2}), ("vo", "c1", {}),
    ("fx", drawer(), {"c2": 0.2}), ("vo", "c2", {}),
    ("fx", drawer(), {"c3": 0.2}), ("vo", "c3", {}),
    ("fx", mix((0, fl()), (0.5, riffle(0.7))), {"count": 0.4}), ("vo", "count", {}),
    ("fx", mix((0, fl()), (0.3, 0.6 * whoosh(0.45))), {"u0": 0.45}), ("vo", "u0", {}),
    ("fx", 0.6 * whoosh(0.4), {"u1": 0.25}), ("vo", "u1", {}),
    ("fx", 0.6 * whoosh(0.4), {"u2": 0.25}), ("vo", "u2", {}),
    ("fx", mix((0, fl()), (0.3, 0.6 * slide(0.6)), (0.9, 0.4 * chime(0.5))), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0, fl()), (1.32, stamp_thud())), {"brand": 0.45}), ("vo", "brand", {}), ("vo", "store", {"store": 0}),
    ("fx", mix((0, 0.5 * piano(146.8, 2.4)), (0.03, 0.4 * piano(293.7, 2.4)), (0.06, 0.4 * piano(349.2, 2.4)), (0.09, 0.4 * piano(440.0, 2.4)), (0.4, 0.5 * chime(1.3))), {}),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.06
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else norm(item, -13)
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
