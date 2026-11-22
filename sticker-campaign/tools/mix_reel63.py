"""Reel 63 soundtrack with voiceover: pour, tea floods, bloops and splashes only in the gaps; warm plucked tune after the last line.

usage: python3 mix_reel63.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel14 import pour
from sfx_reel63 import bloop, flood, splash, tune

V = [(0.15, 2.02), (2.42, 3.36), (3.61, 4.35), (4.79, 5.72), (6.06, 6.80), (7.30, 8.84), (8.86, 10.16), (10.28, 11.57), (11.78, 13.09),
     (13.33, 14.62), (15.04, 16.24), (16.58, 17.87), (18.23, 19.53), (19.94, 20.82), (21.09, 21.76)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
FX = {
    "h2": flood(0.55), "c1": bloop(300), "c2": bloop(360), "c3": bloop(420),
    "count": mix((0, flood(0.5)), *[(0.45 + j * 0.05, 0.25 * splash(0.15)) for j in range(6)]),
    "u0": flood(0.5), "u1": flood(0.5), "u2": flood(0.5), "print": mix((0, flood(0.5)), (0.45, 0.5 * bloop(250, 0.2))), "brand": flood(0.55),
}
PLAN = [("fx", 0.6 * pour(0.4), {})]
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.05, 0.9 * tune(3.0))), {}))


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
