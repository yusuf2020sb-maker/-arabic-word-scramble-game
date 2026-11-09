"""Reel 37 soundtrack with voiceover: ink swells, booms and shimmers only in the gaps; the score plays after the last line.

usage: python3 mix_reel37.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel10 import boom
from sfx_reel37 import score, swell

V = [(0.23, 0.88), (1.28, 2.43), (2.91, 3.67), (4.27, 4.76), (5.35, 5.90), (6.34, 8.33), (8.87, 9.76), (10.25, 11.35), (11.72, 12.46),
     (12.95, 14.05), (14.34, 16.66), (17.09, 18.50), (18.81, 19.79), (20.21, 21.10)]
SEG = dict(zip(["h1", "h2", "c0", "c1", "c2", "count", "n2", "u0", "u1", "u2", "print", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
PLAN = [
    ("fx", mix((0, 0.5 * swell(0.45)), (0.35, 0.3 * cut(boom(0.6), 0.1))), {"h1": 0.4}), ("vo", "h1", {}),
    ("fx", 0.4 * cut(sparkle(0.5), 0.3), {"h2": 0.3}), ("vo", "h2", {}),
    ("fx", mix((0, 0.5 * swell(0.55)), (0.55, 0.3 * cut(boom(0.6), 0.3))), {"c0": 0.75}), ("vo", "c0", {}),
    ("fx", mix((0, 0.5 * swell(0.45)), (0.45, 0.2 * cut(boom(0.6), 0.25))), {"c1": 0.65}), ("vo", "c1", {}),
    ("fx", mix((0, 0.5 * swell(0.45)), (0.45, 0.2 * cut(boom(0.6), 0.25))), {"c2": 0.65}), ("vo", "c2", {}),
    ("fx", mix((0, 0.5 * swell(0.5)), (0.5, 0.4 * cut(chime(1.0), 0.35))), {"count": 0.5}), ("vo", "count", {}), ("vo", "n2", {"n2": 0}),
    ("fx", mix((0, 0.5 * swell(0.5)), (0.5, 0.25 * cut(boom(0.6), 0.25))), {"u0": 0.5}), ("vo", "u0", {}),
    ("fx", mix((0, 0.5 * swell(0.45)), (0.45, 0.2 * cut(boom(0.6), 0.25))), {"u1": 0.7}), ("vo", "u1", {}),
    ("fx", mix((0, 0.5 * swell(0.45)), (0.45, 0.2 * cut(boom(0.6), 0.25))), {"u2": 0.7}), ("vo", "u2", {}),
    ("fx", mix((0, 0.5 * swell(0.5)), (0.5, 0.35 * cut(chime(0.6), 0.3))), {"print": 0.5}), ("vo", "print", {}),
    ("fx", mix((0, 0.5 * swell(0.55)), (0.55, 0.3 * cut(boom(0.6), 0.3))), {"brand": 0.55}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.9 * score(3.0)), (0.05, 0.6 * chime(1.6)), (0.1, 0.35 * sparkle(1.0))), {}),
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
