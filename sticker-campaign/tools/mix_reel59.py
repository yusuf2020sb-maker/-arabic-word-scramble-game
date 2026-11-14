"""Reel 59 soundtrack with voiceover: comic slams, boings, scratches and pops only in the gaps; cartoon funk + brass hit after the last line.

usage: python3 mix_reel59.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav
from sfx_reel5 import boing, thump
from sfx_reel8 import scratch
from sfx_reel59 import brass, funk, slam, whistle

V = [(0.17, 1.08), (1.82, 3.23), (3.74, 4.71), (5.23, 6.37), (6.83, 8.17), (9.07, 10.76), (11.15, 12.19), (12.77, 13.44), (13.90, 14.77),
     (15.24, 16.13), (16.86, 17.62), (18.03, 19.04), (19.84, 21.21), (21.70, 22.48), (23.06, 23.95)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
sl = lambda: cut(slam(), 0.25)
FX = {
    "h1": sl(), "h2": mix((0, 0.4 * cut(whistle(0.6, False), 0.35)), (0.3, sl())),
    "c1": mix((0, 0.5 * cut(boing(), 0.3)), (0.3, 0.6 * cut(scratch(0.3), 0.25)), (0.55, sl())), "c2": sl(), "c3": sl(),
    "count": mix((0, 0.6 * cut(scratch(0.3), 0.25)), (0.25, sl()), *[(0.5 + i * 0.06, 0.3 * cut(thump(), 0.1)) for i in range(4)]), "n2": 0.4 * cut(boing(), 0.3),
    "u0": mix((0, 0.6 * cut(scratch(0.3), 0.25)), (0.25, sl())), "u1": sl(), "u2": sl(),
    "print": mix((0, 0.6 * cut(scratch(0.3), 0.25)), (0.25, sl())), "print2": 0.4 * cut(whistle(0.4), 0.3),
    "brand": mix((0, 0.6 * cut(scratch(0.3), 0.25)), (0.25, sl()), (0.5, 0.4 * cut(boing(), 0.25))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * brass([523.3, 659.3, 784.0], 0.6)), (0.05, 0.5 * chime(1.2)), (0.1, 0.9 * funk(3.2))), {}))


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
