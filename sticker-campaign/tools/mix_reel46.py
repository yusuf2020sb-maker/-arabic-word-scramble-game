"""Reel 46 soundtrack with voiceover: paper rustles, flower thuds, ribbon zip and shop bell only in the gaps; waltz after the last line.

usage: python3 mix_reel46.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel10 import rustle
from sfx_reel18 import bell
from sfx_reel46 import thud, waltz, zipr

V = [(0.10, 0.69), (1.40, 2.73), (3.24, 3.85), (4.52, 5.03), (5.51, 6.06), (6.59, 8.03), (8.52, 9.58), (10.29, 11.27), (11.95, 12.61),
     (13.12, 13.82), (14.45, 15.58), (15.96, 17.03), (17.67, 19.16), (19.59, 20.38), (21.13, 21.84)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
FX = {
    "h1": mix((0, 0.6 * cut(rustle(0.6), 0.5)), *[(0.15 + i * 0.12, 0.4 * thud()) for i in range(4)]),
    "h2": mix((0, 0.6 * thud()), (0.05, 0.4 * cut(sparkle(), 0.3))),
    "c1": mix((0, 0.5 * cut(rustle(0.45), 0.35)), (0.3, 0.7 * thud())), "c2": 0.7 * thud(), "c3": 0.7 * thud(),
    "count": mix((0, 0.6 * zipr()), (0.35, 0.5 * cut(rustle(0.45), 0.35)), *[(0.5 + i * 0.05, 0.2 * thud(0.15)) for i in range(5)]),
    "n2": cut(0.4 * sparkle(), 0.2),
    "u0": mix((0, 0.5 * cut(rustle(0.4), 0.35)), (0.3, 0.6 * thud())), "u1": mix((0, 0.5 * cut(rustle(0.4), 0.3)), (0.25, 0.6 * thud())),
    "u2": mix((0, 0.5 * cut(rustle(0.4), 0.3)), (0.25, 0.6 * thud())),
    "print": mix((0, 0.5 * cut(rustle(0.45), 0.35)), (0.2, 0.6 * cut(rustle(0.9), 0.4))), "print2": 0.5 * thud(),
    "brand": mix((0, 0.5 * cut(rustle(0.45), 0.35)), *[(0.2 + i * 0.08, 0.3 * thud(0.2)) for i in range(3)]),
    "store": 0.5 * zipr(),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.7 * bell()), (0.05, 0.5 * chime(1.4)), (0.1, 0.9 * waltz(3.2))), {}))


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
