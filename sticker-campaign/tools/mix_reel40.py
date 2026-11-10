"""Reel 40 soundtrack with voiceover: countdown beeps first, then projector clicks/clunks only in the gaps; stride piano after the last line.

usage: python3 mix_reel40.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle, whoosh
from sfx_reel5 import rattle
from sfx_reel8 import clunk, tick
from sfx_reel35 import beep
from sfx_reel40 import stride

V = [(0.25, 1.87), (2.63, 3.44), (4.30, 5.03), (5.32, 6.03), (6.22, 7.05), (7.78, 8.25), (8.48, 9.05), (9.31, 10.15), (11.03, 12.49),
     (13.14, 14.35), (15.38, 16.18), (16.55, 17.26), (17.90, 18.98), (19.82, 22.08), (22.96, 24.07), (24.58, 25.41), (25.98, 26.70)]
SEG = dict(zip(["h1", "h2", "k0", "k1", "k2", "k3", "k4", "k5", "count", "n2", "u0", "u1", "u2", "print", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
tk = lambda: 0.6 * tick(0.03)
PLAN = [
    ("fx", mix((0, 0.5 * beep(1000, 0.12)), (0.27, 0.5 * beep(1000, 0.12)), (0.53, 0.5 * beep(1000, 0.12)), (0.62, np.zeros(int(0.18 * SR)))), {"h1": 0.8}), ("vo", "h1", {}),
    ("fx", mix((0, 0.4 * cut(whoosh(0.5), 0.35)), (0.1, 0.5 * cut(sparkle(0.6), 0.35))), {"h2": 0.1}), ("vo", "h2", {}),
    ("fx", mix((0, 0.5 * cut(rattle(0.6), 0.5)), (0.45, tk())), {"k0": 0.55}), ("vo", "k0", {}),
    ("fx", mix((0.15, tk()), (0, np.zeros(int(0.2 * SR)))), {"k1": 0.25}), ("vo", "k1", {}),
    ("fx", mix((0.15, tk()), (0, np.zeros(int(0.2 * SR)))), {"k2": 0.25}), ("vo", "k2", {}),
    ("fx", mix((0.15, tk()), (0, np.zeros(int(0.2 * SR)))), {"k3": 0.25}), ("vo", "k3", {}),
    ("fx", mix((0.15, tk()), (0, np.zeros(int(0.2 * SR)))), {"k4": 0.25}), ("vo", "k4", {}),
    ("fx", mix((0.15, tk()), (0, np.zeros(int(0.2 * SR)))), {"k5": 0.25}), ("vo", "k5", {}),
    ("fx", mix((0.05, 0.8 * cut(clunk(), 0.3)), (0.3, 0.4 * cut(rattle(0.5), 0.4))), {"count": 0.3}), ("vo", "count", {}), ("vo", "n2", {"n2": 0}),
    ("fx", mix((0.1, tk()), (0, np.zeros(int(0.3 * SR)))), {"u0": 0.3}), ("vo", "u0", {}),
    ("fx", mix((0.05, tk()), (0, np.zeros(int(0.2 * SR)))), {"u1": 0.2}), ("vo", "u1", {}),
    ("fx", mix((0.05, tk()), (0, np.zeros(int(0.2 * SR)))), {"u2": 0.2}), ("vo", "u2", {}),
    ("fx", 0.4 * cut(whoosh(0.5), 0.4), {"print": 0.35}), ("vo", "print", {}),
    ("fx", mix((0.05, 0.6 * cut(clunk(), 0.3))), {"brand": 0.3}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.9 * stride(2.8)), (0.05, 0.6 * chime(1.4))), {}),
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
