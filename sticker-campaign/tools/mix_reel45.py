"""Reel 45 soundtrack with voiceover: twinkles, harp runs and shooting stars only in the gaps; celesta lullaby after the last line.

usage: python3 mix_reel45.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel45 import celesta, harp, lullaby, shoot, twinkle

V = [(0.28, 1.17), (1.57, 2.54), (3.18, 3.89), (4.48, 5.41), (5.97, 6.97), (7.13, 9.20), (9.57, 10.79), (11.02, 11.79), (12.25, 13.08),
     (13.49, 15.05), (15.58, 16.52), (16.80, 18.03), (18.49, 19.84), (20.13, 20.89), (21.27, 22.32)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
FX = {
    "h1": cut(harp(), 0.6), "h2": cut(twinkle(2093), 0.3),
    "c1": mix((0, cut(shoot(), 0.45)), (0.4, cut(twinkle(1568), 0.35))), "c2": cut(twinkle(1768), 0.4), "c3": cut(twinkle(1968), 0.4),
    "count": mix((0, cut(shoot(), 0.45)), *[(0.35 + i * 0.05, 0.4 * cut(celesta(1046.5 * (1 + (i % 5) * 0.125), 0.3), 0.15)) for i in range(5)]),
    "u0": mix((0, cut(shoot(), 0.4)), (0.3, 0.6 * cut(harp(True, 6), 0.4))), "u1": 0.6 * cut(harp(False, 6), 0.45), "u2": 0.6 * cut(harp(True, 6), 0.45),
    "print": mix((0, cut(shoot(), 0.45)), (0.35, 0.5 * cut(harp(False), 0.3))), "print2": cut(twinkle(1760), 0.3),
    "brand": mix((0, cut(shoot(), 0.45)), (0.35, cut(twinkle(1318.5), 0.3))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.8 * chime(1.6)), (0.05, 0.9 * lullaby(3.2))), {}))


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
