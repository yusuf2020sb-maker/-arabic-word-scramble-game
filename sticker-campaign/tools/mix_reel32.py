"""Reel 32 soundtrack with voiceover: shutters, thuds and ticks only in the gaps; timeline keys anchored to them.

usage: python3 mix_reel32.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, whoosh
from sfx_reel8 import tick
from sfx_reel18 import pen
from sfx_reel32 import house, shutter, thud

V = [(0.21, 1.38), (1.98, 2.67), (3.42, 4.06), (4.40, 4.75), (5.60, 6.03), (6.55, 7.13), (7.77, 8.19), (8.84, 9.27),
     (9.86, 10.80), (11.00, 12.08), (12.58, 13.60), (13.76, 14.57), (14.97, 16.23), (16.74, 18.14), (18.52, 19.10)]
SEG = dict(zip(["h1", "h2", "c1", "c2", "k0", "k1", "k2", "k3", "print", "p2", "u0", "u1", "u2", "brand", "store"], V))
PLAN = [
    ("fx", 0.6 * thud(), {"h1": 0.1}), ("vo", "h1", {}), ("vo", "h2", {"h2": 0}),
    ("fx", mix((0, shutter()), (0.15, 0.4 * whoosh(0.2))), {"c1": 0.25}), ("vo", "c1", {}),
    ("fx", 0.6 * tick(0.02), {"c2": 0.1}), ("vo", "c2", {}),
    ("fx", mix(*[(i * 0.28, 0.5 * tick(0.02)) for i in range(3)]), {}),
    ("fx", mix((0, shutter()), (0.15, 0.8 * thud())), {"k0": 0.3}), ("vo", "k0", {}),
    ("fx", mix((0, 0.8 * thud()), (0.12, 0.5 * thud())), {"k1": 0.15}), ("vo", "k1", {}),
    ("fx", mix((0, 0.8 * thud()), (0.12, 0.5 * thud())), {"k2": 0.15}), ("vo", "k2", {}),
    ("fx", 0.8 * thud(), {"k3": 0.15}), ("vo", "k3", {}),
    ("fx", mix((0, shutter()), (0.1, 0.5 * whoosh(0.4))), {"print": 0.4}), ("vo", "print", {}),
    ("fx", 0.5 * pen(0.45), {"p2": 0.2}), ("vo", "p2", {}),
    ("fx", mix((0, shutter()), (0.1, 0.5 * whoosh(0.35)), (0.5, 0.7 * thud())), {"u0": 0.3}), ("vo", "u0", {}),
    ("fx", mix((0, 0.5 * whoosh(0.35)), (0.5, 0.7 * thud())), {"u1": 0.2}), ("vo", "u1", {}),
    ("fx", mix((0, 0.5 * whoosh(0.35)), (0.5, 0.7 * thud())), {"u2": 0.2}), ("vo", "u2", {}),
    ("fx", mix((0, shutter()), (0.3, 0.7 * thud())), {"brand": 0.3}), ("vo", "brand", {}),
    ("fx", np.zeros(int(0.08 * SR)), {}), ("vo", "store", {"store": 0}),
    ("fx", mix((0, 0.8 * house(2.6)), (0.1, 0.6 * chime(1.4))), {}),
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
