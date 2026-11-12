"""Reel 43 soundtrack with voiceover: card swipes, 'like' dings, deals and flips only in the gaps; cozy plucked outro after the last line.

usage: python3 mix_reel43.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, sparkle
from sfx_reel8 import tick
from sfx_reel43 import cozy, deal, flip, like, swipe

V = [(0.21, 1.58), (2.03, 3.29), (3.54, 4.36), (4.89, 6.02), (6.49, 7.55), (8.05, 9.30), (10.05, 11.71), (11.88, 12.86), (13.47, 14.21),
     (14.62, 15.47), (15.71, 17.22), (17.95, 18.75), (19.05, 20.17), (20.63, 22.23), (22.63, 23.44), (23.96, 24.83)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "c4", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
sw = lambda f: mix((0, 0.5 * like(f)), (0.2, swipe()))
FX = {
    "h1": cut(swipe(0.5), 0.3), "h2": 0.5 * cut(pop(), 0.15),
    "c1": mix((0, 0.4 * cut(sparkle(), 0.2)), (0.25, sw(1320))), "c2": sw(1430), "c3": sw(1540), "c4": sw(1650),
    "count": mix((0, swipe()), *[(0.3 + i * 0.05, 0.5 * deal()) for i in range(6)], *[(0.3 + i * 0.07, 0.25 * tick()) for i in range(5)]),
    "n2": 0.3 * cut(sparkle(), 0.2),
    "u0": mix((0, 0.8 * swipe(0.45)), (0.4, 0.3 * pop(0.1))), "u1": 0.8 * swipe(0.45), "u2": 0.8 * swipe(0.45),
    "print": mix((0, 0.4 * pop()), (0.2, cut(flip(), 0.3))), "print2": cut(flip(), 0.3),
    "brand": mix((0, 0.7 * swipe(0.5)), (0.45, 0.8 * deal(0.1))),
    "store2": 0.5 * cut(like(1480), 0.25),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.6 * chime(1.4)), (0.05, 0.4 * sparkle(0.6)), (0.1, 0.9 * cozy(3.2))), {}))


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
