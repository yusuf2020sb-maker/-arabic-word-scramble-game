"""Reel 55 soundtrack with voiceover: fan ratchets, colour-wash swooshes and paper pops only in the gaps; boutique lo-fi after the last line.

usage: python3 mix_reel55.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav
from sfx_reel55 import boutique, ratchet, wash

V = [(0.18, 1.06), (1.66, 3.20), (4.15, 4.75), (5.70, 6.17), (6.99, 7.72), (8.76, 10.61), (11.47, 12.49), (13.52, 14.28), (14.96, 15.76),
     (16.36, 17.57), (18.54, 19.44), (19.85, 20.91), (21.70, 22.79), (23.39, 24.22), (24.71, 25.58)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
pops = lambda n: mix(*[(j * 0.06, 0.25 * pop(0.08)) for j in range(n)])
FX = {
    "h1": ratchet(5, 0.08), "h2": 0.5 * cut(pop(), 0.15),
    "c1": mix((0, 0.4 * cut(pop(), 0.15)), (0.15, wash(0.45))), "c2": wash(0.45), "c3": wash(0.45),
    "count": mix((0, ratchet(5)), (0.3, cut(wash(0.6), 0.4)), (0.6, pops(3))), "n2": 0.4 * cut(pop(), 0.15),
    "u0": mix((0, wash(0.4)), (0.35, pops(3))), "u1": mix((0, wash(0.4)), (0.35, pops(2))), "u2": mix((0, wash(0.4)), (0.35, pops(2))),
    "print": wash(0.6), "print2": 0.4 * cut(pop(), 0.15), "brand": mix((0, wash(0.5)), (0.4, 0.5 * cut(pop(), 0.15))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.05, 0.9 * boutique(3.2))), {}))


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
