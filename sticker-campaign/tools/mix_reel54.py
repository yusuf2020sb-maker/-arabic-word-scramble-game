"""Reel 54 soundtrack with voiceover: soil thuds, sprout rises, blooms, rustles and chirps only in the gaps; spring waltz after the last line.

usage: python3 mix_reel54.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel10 import rustle
from sfx_reel54 import bloom, chirp, sprout, spring, thud

V = [(0.17, 1.15), (1.78, 3.13), (3.90, 4.57), (4.97, 5.71), (6.21, 7.19), (7.82, 9.37), (9.76, 10.48), (10.98, 11.77), (12.20, 12.90),
     (13.41, 14.62), (15.35, 16.23), (16.82, 18.02), (18.67, 20.11), (20.78, 21.70), (22.45, 23.40)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
grow = lambda: mix((0, sprout(0.4, 250, 800)), (0.4, cut(bloom(), 0.3)))
FX = {
    "h1": mix((0, 0.3 * cut(chirp(), 0.35)), (0.3, cut(thud(), 0.2))),
    "h2": mix(*[(i * 0.15, cut(sprout(), 0.25)) for i in range(3)], (0.45, cut(bloom(), 0.25))),
    "c1": mix((0, 0.5 * cut(rustle(0.6), 0.35)), (0.3, grow())), "c2": grow(), "c3": grow(),
    "count": mix((0, 0.5 * cut(rustle(0.6), 0.35)), *[(0.3 + i * 0.05, 0.25 * sprout(0.2, 400 + 30 * i, 1100)) for i in range(6)]),
    "n2": 0.3 * cut(chirp(3600), 0.3),
    "u0": mix((0, 0.5 * cut(rustle(0.6), 0.35)), (0.3, 0.6 * thud()), (0.5, cut(sprout(), 0.25))), "u1": mix((0, 0.6 * thud()), (0.2, cut(sprout(), 0.25))), "u2": mix((0, 0.6 * thud()), (0.2, cut(sprout(), 0.25))),
    "print": mix((0, 0.5 * cut(rustle(0.6), 0.35)), (0.3, 0.5 * thud()), (0.45, cut(sprout(), 0.25))), "print2": 0.3 * cut(chirp(), 0.3),
    "brand": mix((0, 0.5 * cut(rustle(0.6), 0.35)), (0.3, 0.6 * thud()), (0.5, cut(sprout(), 0.25))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.05, bloom()), (0.1, 0.9 * spring(3.2)), (0.6, 0.3 * chirp(3400))), {}))


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
