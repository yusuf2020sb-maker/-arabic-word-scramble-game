"""Reel 24 soundtrack with voiceover: effects only in the gaps; timeline keys anchored to the effects.

usage: python3 mix_reel24.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel8 import clunk
from sfx_reel20 import kick
from sfx_reel24 import PENTA, flip, kalimba, swoosh_col

SEG = {"h1": (0.22, 0.92), "h2": (1.25, 1.91), "c0": (2.71, 3.56), "c1": (4.15, 4.93), "c2": (5.73, 7.16),
       "count": (7.92, 9.40), "count2": (9.93, 10.72), "art": (11.57, 12.25), "art2": (12.75, 13.60),
       "u0": (14.36, 15.41), "u1": (15.47, 16.39), "u2": (16.89, 17.88), "print": (18.51, 19.41), "print2": (19.83, 21.83),
       "brand": (22.39, 23.66), "store": (24.09, 24.58)}
cut = lambda x, d: x[:int(d * SR)]
PLAN = [
    ("fx", 0.6 * cut(kalimba(784), 0.3), {}),
    ("vo", "h1", {"h1": 0}), ("vo", "h2", {"h2": 0}),
    ("fx", mix((0, swoosh_col(True)), (0.5, 0.6 * cut(kalimba(523.3), 0.35))), {"c0": 0.45}), ("vo", "c0", {}),
    ("fx", mix((0, swoosh_col(False)), (0.3, 0.6 * cut(kalimba(659.3), 0.3))), {"c1": 0.3}), ("vo", "c1", {}),
    ("fx", mix((0, swoosh_col(True)), (0.3, 0.6 * cut(kalimba(784.0), 0.3))), {"c2": 0.3}), ("vo", "c2", {}),
    ("fx", mix((0, swoosh_col(False)), *[(0.7 + (i % 4 + i // 4) * 0.09, 0.5 * flip()) for i in range(16)], (1.15, 0.5 * sparkle(0.4))), {"count": 0.45}),
    ("vo", "count", {}), ("vo", "count2", {}),
    ("fx", mix((0, swoosh_col(True)), (0.5, clunk())), {"art": 0.45}), ("vo", "art", {}), ("vo", "art2", {"art2": 0}),
    ("fx", mix((0, swoosh_col(False)), (0.6, 0.7 * kick(0.2))), {"u0": 0.25}), ("vo", "u0", {}),
    ("fx", mix((0, 0.6 * swoosh_col(True, 0.4)), (0.55, 0.7 * kick(0.2))), {"u1": 0.25}), ("vo", "u1", {}),
    ("fx", mix((0, 0.6 * swoosh_col(False, 0.4)), (0.55, 0.7 * kick(0.2))), {"u2": 0.25}), ("vo", "u2", {}),
    ("fx", mix((0, swoosh_col(True)), (0.5, 0.5 * chime(0.4))), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0, swoosh_col(False)), *[(0.45 + i * 0.05, 0.3 * cut(kalimba(PENTA[i % 7] * 2, 0.4), 0.3)) for i in range(11)]), {"brand": 0.45}),
    ("vo", "brand", {}), ("vo", "store", {"store": 0}),
    ("fx", mix((0, 0.5 * kalimba(392.0, 1.6)), (0, 0.5 * kalimba(587.3, 1.6)), (0.05, 0.5 * kalimba(784.0, 1.6)), (0.3, 0.6 * chime(1.3))), {}),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.06
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else norm(item, -13)
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
