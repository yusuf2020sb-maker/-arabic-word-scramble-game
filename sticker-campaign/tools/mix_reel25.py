"""Reel 25 soundtrack with voiceover: effects only in the gaps; timeline keys anchored to the effects.

usage: python3 mix_reel25.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel5 import printer, thump
from sfx_reel9 import stamp_thud
from sfx_reel10 import creak
from sfx_reel17 import pluck
from sfx_reel18 import bell, slide, tear
from sfx_reel25 import gust, punch

SEG = {"h1": (0.17, 2.13), "h2": (2.41, 3.11), "d1": (3.77, 4.36), "d2": (4.88, 5.57), "k1": (6.42, 6.87), "k2": (7.58, 8.37),
       "k3": (8.90, 9.71), "count": (10.42, 13.67), "u0": (14.39, 15.07), "u1": (15.62, 16.88), "u2": (17.47, 18.56),
       "print": (19.31, 20.03), "print2": (20.46, 21.98), "brand": (22.66, 23.54), "store": (23.97, 24.48)}
clack2 = lambda: mix((0, 0.6 * thump(0.12)), (0.11, 0.6 * thump(0.12)))
press3 = lambda o: [(o + j * 0.25, 0.7 * thump(0.12)) for j in range(3)]
PLAN = [
    ("fx", 0.7 * printer(0.5), {"h1": 0.15}),
    ("vo", "h1", {}),
    ("fx", mix((0, punch()), (0.1, 0.7 * stamp_thud())), {"h2": 0.05}), ("vo", "h2", {}),
    ("fx", mix((0, 1.1 * tear(0.6)), (0.15, 0.6 * gust(0.9))), {"tear": 0.0}),
    ("vo", "d1", {"dest": 0.1}), ("vo", "d2", {"dest2": 0}),
    ("fx", mix((0, 0.6 * gust(0.6)), (0.55, clack2())), {"k1": 0.5}), ("vo", "k1", {}),
    ("fx", clack2(), {}), ("vo", "k2", {"k2": 0}),
    ("fx", clack2(), {}), ("vo", "k3", {"k3": 0}),
    ("fx", mix((0, 0.6 * gust(0.6)), *[(0.65 + i * 0.07, 0.5 * thump(0.15)) for i in range(8)]), {"count": 0.45}), ("vo", "count", {}),
    ("fx", mix((0, 0.6 * gust(0.6)), *press3(0.8)), {"u0": 0.3}), ("vo", "u0", {}),
    ("fx", mix((0, 0.5 * slide(0.5)), *press3(0.75)), {"u1": 0.45}), ("vo", "u1", {}),
    ("fx", mix((0, 0.5 * slide(0.5)), *press3(0.75)), {"u2": 0.45}), ("vo", "u2", {}),
    ("fx", mix((0, 0.6 * gust(0.6)), (0.55, 0.5 * slide(0.6)), (1.0, 0.4 * chime(0.4))), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0, 0.6 * gust(0.6)), (0.6, 0.5 * creak(0.45))), {"brand": 0.45}), ("vo", "brand", {}),
    ("fx", np.zeros(int(0.08 * SR)), {}), ("vo", "store", {"store": 0}),
    ("fx", mix((0, 0.5 * pluck(110.0, 2.2)), (0.04, 0.4 * pluck(220.0, 2.2)), (0.08, 0.4 * pluck(261.6, 2.2)), (0.12, 0.4 * pluck(329.6, 2.2)), (0.4, 0.5 * chime(1.3))), {}),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.06
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else (norm(item, -13) if np.abs(item).max() > 0 else item)
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
