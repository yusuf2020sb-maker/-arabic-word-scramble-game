"""Reel 49 soundtrack with voiceover: loom shuttles, darbuka hits, pours and sparkles only in the gaps; heritage groove after the last line.

usage: python3 mix_reel49.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel14 import pour
from sfx_reel16 import wood
from sfx_reel49 import dum, groove, shuttle

V = [(0.20, 1.19), (1.54, 2.38), (2.85, 3.94), (4.50, 5.78), (6.38, 7.57), (8.27, 9.43), (9.84, 10.77), (11.50, 12.39), (12.87, 13.95),
     (14.58, 15.33), (16.03, 17.16), (17.45, 18.71), (19.35, 21.03), (21.68, 22.55), (23.06, 23.93)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
loom = mix((0, shuttle()), (0.45, 0.6 * shuttle()))
FX = {
    "h1": mix((0, 0.6 * shuttle()), (0.2, 0.4 * cut(pour(0.6), 0.3))), "h2": 0.5 * cut(dum(), 0.2),
    "c1": mix((0, loom), (0.8, 0.4 * cut(sparkle(), 0.2))), "c2": 0.4 * cut(sparkle(), 0.3), "c3": 0.4 * cut(sparkle(), 0.3),
    "count": mix((0, loom), *[(0.8 + i * 0.05, 0.25 * wood(0.05)) for i in range(4)]),
    "u0": mix((0, loom), (0.85, 0.4 * cut(dum(), 0.15))), "u1": 0.4 * cut(dum(), 0.25), "u2": 0.4 * cut(dum(), 0.25),
    "print": loom, "print2": 0.4 * cut(dum(), 0.2), "brand": mix((0, loom), (0.85, 0.5 * cut(dum(), 0.15))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.6 * chime(1.4)), (0.05, 0.9 * groove(3.2))), {}))


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
