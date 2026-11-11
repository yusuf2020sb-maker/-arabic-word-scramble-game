"""Reel 44 soundtrack with voiceover: error bonks, clicks, blips and printer buzz only in the gaps; chiptune + success jingle after the last line.

usage: python3 mix_reel44.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, mix, norm, read_wav
from sfx_reel44 import blip, bonk, buzz, chip, click, sq, tada

V = [(0.20, 1.13), (1.88, 3.57), (4.34, 4.75), (5.21, 6.58), (7.24, 9.49), (10.37, 12.43), (13.12, 14.97), (15.78, 17.17), (17.58, 19.40),
     (19.94, 20.57), (21.01, 21.72), (22.01, 23.38), (24.17, 24.97), (25.49, 26.49), (27.23, 28.37), (28.84, 29.52), (30.25, 30.99)]
SEG = dict(zip(["h1", "h2", "q", "a", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
win = lambda f=800: mix((0, click()), (0.02, blip(f)))
cascade = mix(*[(i * 0.12, 0.6 * cut(bonk(), 0.12)) for i in range(7)], (0.95, blip(700)))
ticks = lambda n, gap=0.08: mix(*[(i * gap, 0.3 * sq(1500 + i * 40, 0.02, 0.5, 120)) for i in range(n)])
PLAN = [
    ("fx", cut(bonk(), 0.4), {}), ("vo", "h1", {"h1": 0}), ("vo", "h2", {"h2": 0}),
    ("fx", cascade, {"casc": 0.0}), ("vo", "q", {"q": 0}),
    ("fx", win(900), {}), ("vo", "a", {"a": 0}),
    ("fx", mix((0, ticks(6)), (0.5, win(800))), {}), ("vo", "c1", {"c1": 0}),
    ("fx", win(920), {}), ("vo", "c2", {"c2": 0}),
    ("fx", win(1040), {}), ("vo", "c3", {"c3": 0}),
    ("fx", mix((0, blip(700)), (0.1, ticks(6, 0.05))), {}), ("vo", "count", {"count": 0}), ("vo", "n2", {"n2": 0}),
    ("fx", win(900), {}), ("vo", "u0", {"u0": 0}),
    ("fx", win(1000), {}), ("vo", "u1", {"u1": 0}),
    ("fx", win(1100), {}), ("vo", "u2", {"u2": 0}),
    ("fx", win(700), {}), ("vo", "print", {"print": 0}),
    ("fx", buzz(0.45), {}), ("vo", "print2", {"print2": 0}),
    ("fx", blip(1000), {}), ("vo", "brand", {"brand": 0}), ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, click()), (0.03, tada()), (0.1, 0.8 * chip(3.0))), {}),
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
