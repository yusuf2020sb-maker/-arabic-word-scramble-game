"""Reel 35 soundtrack with voiceover: beeps, boings, power-up and swooshes only in the gaps; funk only after the last line.

usage: python3 mix_reel35.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, whoosh
from sfx_reel5 import boing
from sfx_reel14 import pour, powerup
from sfx_reel35 import beep, funk

V = [(0.00, 0.91), (1.35, 2.43), (2.87, 3.28), (3.95, 4.45), (5.05, 6.04), (6.39, 7.51), (8.04, 8.76), (9.22, 10.45), (10.84, 11.85),
     (12.17, 12.83), (13.34, 14.07), (14.32, 15.04), (15.34, 16.35), (16.88, 17.69), (17.86, 18.78), (19.29, 20.13), (20.44, 21.29), (21.45, 22.06)]
SEG = dict(zip(["h1", "one", "h2", "qahwa", "title", "t2", "b0", "b1", "b2", "b2b", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
PLAN = [
    ("vo", "h1", {"h1": 0.0}),
    ("fx", mix((0, 0.5 * beep(1200)), (0.15, 0.5 * beep(1000))), {}), ("vo", "one", {}),
    ("fx", 0.6 * beep(600, 0.3), {}), ("vo", "h2", {"h2": 0.0}),
    ("fx", cut(boing(0.35), 0.3), {}), ("vo", "qahwa", {}),
    ("fx", mix((0, 0.7 * cut(powerup(0.85), 0.7)), (0, 0.4 * cut(pour(0.7), 0.7))), {}),
    ("fx", mix((0, 0.6 * whoosh(0.5)), *[(0.35 + i * 0.05, 0.25 * pop(0.1)) for i in range(4)]), {"title": 0.45}), ("vo", "title", {}), ("vo", "t2", {"t2": 0}),
    ("fx", mix((0, 0.6 * whoosh(0.5)), (0.4, 0.6 * cut(boing(0.35), 0.3))), {"b0": 0.55}), ("vo", "b0", {}),
    ("fx", cut(boing(0.35), 0.3), {"b1": 0.15}), ("vo", "b1", {}),
    ("fx", cut(boing(0.35), 0.3), {"b2": 0.15}), ("vo", "b2", {}), ("vo", "b2b", {}),
    ("fx", mix((0, 0.6 * whoosh(0.5)), (0.65, 0.4 * pop(0.12)), (0.8, 0.4 * pop(0.12))), {"u0": 0.45}), ("vo", "u0", {}),
    ("fx", mix((0, 0.4 * whoosh(0.3)), (0.35, 0.4 * pop(0.12)), (0.5, 0.4 * pop(0.12))), {"u1": 0.2}), ("vo", "u1", {}),
    ("fx", mix((0, 0.4 * whoosh(0.3)), (0.35, 0.4 * pop(0.12))), {"u2": 0.2}), ("vo", "u2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.5)), (0.45, 0.5 * cut(boing(0.3), 0.3))), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.5)), (0.5, 0.5 * cut(boing(0.4), 0.35))), {"brand": 0.45}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.8 * funk(2.6)), (0.1, 0.6 * chime(1.4))), {}),
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
