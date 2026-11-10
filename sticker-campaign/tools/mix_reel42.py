"""Reel 42 soundtrack with voiceover: chalk scratches, clinks and eraser rubs only in the gaps; café jazz after the last line.

usage: python3 mix_reel42.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel17 import clink
from sfx_reel42 import chalk, jazz, rub

V = [(0.21, 0.61), (1.18, 1.84), (2.74, 3.28), (3.86, 4.44), (4.99, 5.60), (6.56, 7.14), (7.86, 8.38), (9.02, 9.78), (10.57, 12.02),
     (12.48, 13.85), (14.75, 15.68), (16.36, 17.17), (17.78, 18.89), (19.72, 20.73), (21.24, 22.26), (23.01, 24.72), (25.34, 26.28), (26.40, 26.82)]
SEG = dict(zip(["h1", "h2", "d0", "d1", "d2", "s0", "s1", "s2", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
PLAN = [
    ("vo", "h1", {"h1": 0.0}), ("fx", 0.5 * cut(clink(), 0.25), {"h2": 0.15}), ("vo", "h2", {}),
    ("fx", mix((0, cut(rub(0.5), 0.4)), (0.3, 0.8 * cut(chalk(0.3), 0.3))), {"d0": 0.55}), ("vo", "d0", {}),
    ("fx", 0.8 * cut(chalk(0.3), 0.3), {"d1": 0.15}), ("vo", "d1", {}),
    ("fx", 0.8 * cut(chalk(0.3), 0.3), {"d2": 0.15}), ("vo", "d2", {}),
    ("fx", 0.8 * cut(chalk(0.45), 0.45), {"s0": 0.45}), ("vo", "s0", {}),
    ("fx", 0.8 * cut(chalk(0.3), 0.3), {"s1": 0.15}), ("vo", "s1", {}),
    ("fx", 0.8 * cut(chalk(0.3), 0.3), {"s2": 0.15}), ("vo", "s2", {}),
    ("fx", mix((0, cut(rub(0.5), 0.4)), (0.3, 0.8 * cut(chalk(0.3), 0.3))), {"count": 0.45}), ("vo", "count", {}), ("vo", "n2", {"n2": 0}),
    ("fx", mix((0, cut(rub(0.5), 0.4)), (0.3, 0.8 * cut(chalk(0.3), 0.3))), {"u0": 0.45}), ("vo", "u0", {}),
    ("fx", 0.8 * cut(chalk(0.35), 0.35), {"u1": 0.25}), ("vo", "u1", {}),
    ("fx", 0.8 * cut(chalk(0.35), 0.35), {"u2": 0.25}), ("vo", "u2", {}),
    ("fx", cut(rub(0.5), 0.45), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0, cut(rub(0.5), 0.4)), (0.3, 0.8 * cut(chalk(0.3), 0.3))), {"brand": 0.45}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.9 * jazz(3.0)), (0.05, 0.6 * chime(1.4))), {}),
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
