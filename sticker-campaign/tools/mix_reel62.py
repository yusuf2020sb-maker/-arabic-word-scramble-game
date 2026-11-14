"""Reel 62 soundtrack with voiceover: buzz, seal pop, whooshes, whips, typing and postmark only in the gaps; jazz outro after the last line.

usage: python3 mix_reel62.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, whoosh
from sfx_reel5 import printer
from sfx_reel16 import page
from sfx_reel18 import clack, postmark, typing
from sfx_reel42 import jazz
from sfx_reel62 import buzz, whip

V = [(0.15, 1.10), (2.03, 2.52), (3.27, 4.30), (5.17, 6.07), (6.87, 8.00), (8.74, 10.58), (11.02, 12.30), (12.74, 14.27), (14.71, 15.51),
     (16.06, 16.92), (17.32, 18.80), (19.16, 20.65), (21.07, 23.03), (23.53, 24.44), (25.02, 26.44)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
hero = lambda: mix((0, 0.8 * whoosh(0.4)), (0.36, 0.5 * pop()))
FX = {
    "h2": mix((0, 0.6 * pop()), (0.05, 0.8 * page())),
    "c1": hero(), "c2": hero(), "c3": hero(),
    "count": mix(*[(0.3 + i * 0.025, 0.25 * clack(0.08)) for i in range(16)]),
    "n2": mix((0, 0.5 * whoosh(0.3)), (0.2, 0.8 * typing(6, 0.05))),
    "u0": whip(), "u1": whip(), "u2": whip(), "print": mix((0, whip()), (0.15, 0.4 * printer(0.35))),
    "brand": mix((0, 0.6 * whoosh(0.4)), (0.37, postmark())),
}
PLAN = [("fx", 0.5 * buzz(0.35), {})]
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.05, 0.9 * jazz(3.0))), {}))


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
