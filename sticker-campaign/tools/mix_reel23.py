"""Reel 23 soundtrack with voiceover: effects only in the gaps; timeline keys anchored to the effects they pair with.

usage: python3 mix_reel23.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle, whoosh
from sfx_reel16 import page
from sfx_reel20 import peel
from sfx_reel23 import bloom, drip, harp_gliss, inkswell, press

SEG = {
    "h1": (0.27, 0.67), "h2": (1.19, 2.02), "h3": (2.42, 3.54), "rev": (4.08, 5.39),
    "count": (6.01, 8.62), "k1": (9.11, 9.49), "k2": (9.80, 10.30), "k3": (10.46, 11.20), "k4": (11.47, 12.38),
    "u0": (12.94, 14.26), "u1": (14.84, 15.41), "u2": (15.86, 17.07), "print": (17.67, 19.80),
    "brand": (20.31, 21.69), "store": (22.18, 22.61),
}
uses = lambda: mix((0, 0.6 * inkswell(0.45)), (0.5, press()), (0.8, press()), (1.1, press()))

# (kind, payload, {timeline key: offset from this block's start})
PLAN = [
    ("fx", 0.5 * harp_gliss(n=8, step=0.04)[:int(0.55 * SR)], {}),
    ("vo", "h1", {"h1": 0}), ("vo", "h2", {"h2": 0}),
    ("fx", mix(*[(i * 0.1, 0.5 * drip(800 + i * 120)) for i in range(3)]), {}),
    ("vo", "h3", {"h3": 0}),
    ("fx", mix((0, 1.3 * peel(0.5)), (0.35, 0.7 * sparkle(0.6))), {"rev": 0.1}),
    ("vo", "rev", {}),
    ("fx", mix((0, 0.6 * whoosh(0.5)), *[(0.3 + i * 0.045, 0.35 * bloom(i)) for i in range(16)]), {"count": 0.25}),
    ("vo", "count", {}),
    ("fx", mix((0, 0.6 * whoosh(0.45)), (0.4, page(0.45))), {"kinds": 0.35}),
    ("vo", "k1", {}),
    ("fx", page(0.3), {"k2": 0.25}), ("vo", "k2", {}),
    ("fx", page(0.3), {"k3": 0.25}), ("vo", "k3", {}),
    ("fx", page(0.3), {"k4": 0.25}), ("vo", "k4", {}),
    ("fx", mix((0, 0.6 * whoosh(0.45)), (0.5, press()), (0.8, press()), (1.1, press())), {"u0": 0.15}),
    ("vo", "u0", {}),
    ("fx", uses(), {"u1": 0.2}), ("vo", "u1", {}),
    ("fx", uses(), {"u2": 0.2}), ("vo", "u2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.45)), (0.2, page(0.7)), (0.8, 0.5 * chime(0.6))), {"print": 0.15}),
    ("vo", "print", {}),
    ("fx", mix((0, 0.6 * whoosh(0.45)), *[(0.25 + i * 0.05, 0.25 * bloom(12 + i % 12)) for i in range(16)]), {"brand": 0.15}),
    ("vo", "brand", {}),
    ("fx", np.zeros(int(0.1 * SR)), {}),
    ("vo", "store", {"store": 0.05}),
    ("fx", mix((0, 0.6 * harp_gliss(False)), (0.4, 0.6 * chime(1.4))), {}),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path)
    GAP = 0.06
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else norm(item, -13)
        for k, off in keys.items():
            tl[k] = round(t + off, 3)
        print(f"{kind}\t{item if kind == 'vo' else '':6}\t{t:.2f}\t{t + len(x) / SR:.2f}\t{keys}")
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
