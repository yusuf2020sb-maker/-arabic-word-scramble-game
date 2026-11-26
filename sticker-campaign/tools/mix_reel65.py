"""Reel 65 soundtrack with voiceover: timer ticks, oven ding, door clunk, steam hiss, whooshes and pops only in the gaps;
chime, bell and café jazz after the last line.

usage: python3 mix_reel65.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, whoosh
from sfx_reel18 import bell, tear
from sfx_reel42 import jazz
from sfx_reel64 import clunk
from sfx_reel65 import ding, hiss, ticking

V = [(0.0, 0.90), (1.91, 4.04), (4.86, 5.42), (6.34, 7.05), (8.01, 9.21), (10.00, 11.30), (11.92, 14.16), (15.09, 16.18),
     (16.77, 18.07), (18.40, 19.21), (20.21, 21.09), (21.66, 23.94), (24.87, 26.41), (26.71, 27.51), (27.94, 28.67)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
WIPE = mix((0, 0.45 * hiss(0.5)), (0.05, 0.4 * whoosh(0.35)))
FX = {
    "h2": mix((0, 0.25 * ticking(0.5)), (0.45, 0.7 * ding()[:int(0.35 * SR)]), (0.55, 0.9 * clunk()), (0.6, 0.6 * hiss(0.35))),
    "c1": mix((0, 0.35 * whoosh(0.25)), (0.2, 0.5 * pop())), "c2": mix((0, 0.35 * whoosh(0.25)), (0.2, 0.5 * pop())), "c3": mix((0, 0.35 * whoosh(0.25)), (0.2, 0.5 * pop())),
    "count": mix((0, WIPE), *[(0.2 + j * 0.03, 0.2 * pop()) for j in range(8)]),
    "u0": WIPE, "u1": WIPE, "u2": WIPE, "print": WIPE, "print2": 0.6 * tear(), "brand": WIPE,
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.25, 0.35 * bell()), (0.1, 0.8 * jazz(3.2))), {}))


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.05
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else norm(item, -12)
        for k, off in keys.items():
            tl[k] = round(t + off, 3)
        out += [x, np.zeros(int(GAP * SR))]; t += len(x) / SR + GAP
    # word onsets inside lines that carry a spoken pause (caption line index -> per-word offsets)
    tl["woff"] = {"1": [0, 0.2, 0.45, 1.39], "5": [0, 0.3, 1.33, 1.5, 1.7], "10": [0, 0.84, 1.64]}
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
