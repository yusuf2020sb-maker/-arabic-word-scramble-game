"""Reel 39 soundtrack with voiceover: page flips and paper pop-up flaps only in the gaps; the lullaby after the last line.

usage: python3 mix_reel39.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel16 import page
from sfx_reel39 import flap, lullaby, thump

V = [(0.00, 1.14), (1.79, 2.45), (3.33, 3.87), (4.29, 5.05), (5.65, 6.42), (7.24, 7.89), (8.41, 8.89), (9.44, 9.95), (10.94, 12.25),
     (12.59, 13.58), (14.44, 15.10), (15.63, 16.42), (16.89, 18.12), (18.88, 19.79), (20.07, 21.27), (22.11, 23.26), (23.90, 24.67), (25.25, 25.88)]
SEG = dict(zip(["h1", "h2", "k0", "k0m", "k0b", "k1", "k1m", "k1b", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"], V))
flaps = lambda n, o=0.0: [(o + j * 0.08, 0.5 * flap()) for j in range(n)]
PLAN = [
    ("vo", "h1", {"h1": 0.0}), ("fx", 0.6 * flap(), {}), ("vo", "h2", {"h2": 0}),
    ("fx", mix((0, 0.7 * page(0.55)), *flaps(3, 0.65)), {"k0": 0.6}), ("vo", "k0", {}), ("vo", "k0m", {}), ("vo", "k0b", {"k0b": 0}),
    ("fx", mix((0, 0.7 * page(0.55)), *flaps(4, 0.65)), {"k1": 0.6}), ("vo", "k1", {}), ("vo", "k1m", {}), ("vo", "k1b", {"k1b": 0}),
    ("fx", mix((0, 0.7 * page(0.55)), *flaps(12, 0.65)), {"count": 0.6}), ("vo", "count", {}), ("vo", "n2", {"n2": 0}),
    ("fx", mix((0, 0.7 * page(0.55)), *flaps(3, 0.65)), {"u0": 0.6}), ("vo", "u0", {}),
    ("fx", 0.6 * flap(), {"u1": 0.15}), ("vo", "u1", {}),
    ("fx", 0.6 * flap(), {"u2": 0.15}), ("vo", "u2", {}),
    ("fx", 0.7 * page(0.6), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0.1, 0.8 * thump())), {"brand": 0.45}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.9 * lullaby(2.8)), (0.05, 0.6 * chime(1.4))), {}),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.05
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else norm(item, -12)
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
