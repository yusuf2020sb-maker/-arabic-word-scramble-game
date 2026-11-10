"""Reel 38 soundtrack with voiceover: creaks, knocks, chimes and sparkles only in the gaps; the maqsum groove after the last line.

usage: python3 mix_reel38.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel10 import creak
from sfx_reel16 import wood
from sfx_reel38 import maqsum, windchime

V = [(0.25, 1.42), (2.14, 2.89), (3.30, 5.04), (5.92, 8.35), (8.95, 10.45), (11.18, 12.25), (12.44, 13.39), (14.03, 14.97),
     (15.12, 16.09), (16.27, 17.39), (17.73, 18.51), (18.86, 19.75), (20.25, 21.12), (21.41, 22.31), (22.53, 23.26)]
SEG = dict(zip(["h1", "h1b", "a0", "a1", "a2", "title", "t2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
knocks = lambda: mix(*[(j * 0.12, 0.6 * wood()) for j in range(3)])
PLAN = [
    ("fx", 0.6 * wood(), {"h1": 0.1}), ("vo", "h1", {}),
    ("fx", mix((0, 0.5 * cut(creak(0.45), 0.4)), (0.2, 0.4 * cut(sparkle(0.6), 0.4))), {}), ("vo", "h1b", {"h1b": 0}),
    ("fx", mix((0, 0.45 * cut(windchime(), 0.5)), (0.5, knocks())), {"a0": 0.65}), ("vo", "a0", {}),
    ("fx", knocks(), {"a1": 0.15}), ("vo", "a1", {}),
    ("fx", knocks(), {"a2": 0.15}), ("vo", "a2", {}),
    ("fx", mix((0, 0.45 * cut(windchime(), 0.5)), (0.5, 0.4 * cut(sparkle(0.6), 0.35))), {"title": 0.55}), ("vo", "title", {}), ("vo", "t2", {"t2": 0}),
    ("fx", mix((0, 0.45 * cut(windchime(), 0.5)), (0.55, 0.6 * wood())), {"u0": 0.45}), ("vo", "u0", {}),
    ("fx", 0.6 * wood(), {"u1": 0.2}), ("vo", "u1", {}),
    ("fx", 0.6 * wood(), {"u2": 0.2}), ("vo", "u2", {}),
    ("fx", mix((0, 0.45 * cut(windchime(), 0.5)), (0.5, 0.3 * cut(chime(0.5), 0.3))), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0, 0.45 * cut(windchime(), 0.5)), (0.5, 0.4 * cut(sparkle(0.6), 0.35))), {"brand": 0.45}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.9 * maqsum(2.8)), (0.05, 0.6 * chime(1.4))), {}),
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
