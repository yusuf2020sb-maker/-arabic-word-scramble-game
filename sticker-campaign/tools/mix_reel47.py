"""Reel 47 soundtrack with voiceover: glassine slides, stamp thuds, magnifier swooshes and postmarks only in the gaps; study jazz after the last line.

usage: python3 mix_reel47.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel9 import stamp_thud
from sfx_reel16 import page
from sfx_reel47 import slide, study, swoosh

V = [(0.23, 1.38), (1.88, 3.05), (3.76, 4.54), (5.08, 5.88), (6.56, 7.75), (8.32, 10.02), (10.58, 11.46), (12.04, 12.85), (13.23, 13.97),
     (14.43, 15.74), (16.38, 17.28), (17.90, 18.89), (19.53, 21.44), (22.00, 22.84), (23.41, 24.32)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
st = lambda g=1.0, d=0.3: g * cut(stamp_thud(), d)
FX = {
    "h1": mix(*[(i * 0.07, 0.4 * slide()) for i in range(6)]),
    "h2": st(0.7),
    "c1": mix((0, cut(swoosh(), 0.35)), (0.3, st(0.4, 0.2))), "c2": cut(swoosh(), 0.4), "c3": cut(swoosh(), 0.4),
    "count": mix((0, 0.6 * cut(page(), 0.35)), *[(0.3 + i * 0.025, st(0.15, 0.1)) for i in range(10)]),
    "n2": st(0.5, 0.25),
    "u0": mix((0, 0.6 * cut(page(), 0.3)), (0.25, st(0.6, 0.2)), (0.45, st(0.9))), "u1": mix((0, st(0.5, 0.2)), (0.2, st(0.9))), "u2": mix((0, st(0.5, 0.2)), (0.2, st(0.9))),
    "print": mix((0, 0.6 * cut(page(), 0.3)), (0.25, 0.5 * slide(0.4))), "print2": st(0.4, 0.2),
    "brand": mix((0, 0.6 * cut(page(), 0.3)), (0.25, st(0.6, 0.2)), (0.45, st(0.9))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.6 * chime(1.4)), (0.05, 0.9 * study(3.2))), {}))


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
