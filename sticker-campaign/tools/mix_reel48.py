"""Reel 48 soundtrack with voiceover: pours, tea-wave sloshes, bubbles and clinks only in the gaps; tea-house lo-fi after the last line.

usage: python3 mix_reel48.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel14 import pour
from sfx_reel17 import clink
from sfx_reel48 import bubble, lofi, slosh

V = [(0.18, 1.05), (1.53, 2.27), (3.00, 3.77), (4.52, 5.25), (5.87, 6.56), (7.36, 8.69), (9.05, 10.11), (10.80, 11.75), (12.22, 13.27),
     (13.65, 14.80), (15.46, 16.45), (16.81, 18.08), (18.70, 20.02), (20.60, 21.56), (22.21, 22.88)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
bub3 = mix(*[(j * 0.05, bubble(500 + 150 * j)) for j in range(3)])
FX = {
    "h1": 0.6 * cut(pour(0.8), 0.5), "h2": 0.5 * cut(clink(), 0.3),
    "c1": mix((0, 0.7 * slosh(0.8)), (0.6, bub3)), "c2": bub3, "c3": bub3,
    "count": mix((0, 0.7 * slosh(0.75)), *[(0.45 + i * 0.07, 0.6 * bubble(400 + 60 * i)) for i in range(4)]),
    "u0": mix((0, 0.7 * slosh(0.75)), (0.55, 0.4 * cut(clink(), 0.25))), "u1": 0.4 * cut(clink(), 0.3), "u2": 0.4 * cut(clink(), 0.3),
    "print": mix((0, 0.7 * slosh(0.75)), (0.55, 0.4 * cut(sparkle(), 0.25))), "print2": cut(bub3, 0.2),
    "brand": mix((0, 0.7 * slosh(0.75)), (0.55, 0.4 * cut(clink(), 0.25))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.6 * chime(1.4)), (0.05, 0.9 * lofi(3.2))), {}))


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
