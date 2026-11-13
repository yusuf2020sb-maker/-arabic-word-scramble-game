"""Reel 56 soundtrack with voiceover: turntable whirs, spotlight glints and soft swooshes only in the gaps; lounge strings after the last line.

usage: python3 mix_reel56.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, read_wav, whoosh
from sfx_reel56 import lounge, shing, whir

V = [(0.27, 1.04), (1.38, 2.21), (2.99, 3.88), (4.50, 5.50), (6.08, 7.18), (7.88, 8.84), (9.20, 10.38), (10.81, 11.45), (11.91, 12.56),
     (12.88, 13.85), (14.36, 15.38), (15.68, 16.76), (17.38, 18.49), (18.87, 19.68), (20.23, 21.08)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
sw = lambda d=0.4: 0.5 * lowpass(whoosh(d), 3000)
FX = {
    "h1": cut(whir(0.8), 0.5), "h2": 0.4 * cut(shing(), 0.3),
    "c1": mix((0, cut(whir(0.6), 0.5)), (0.45, cut(shing(), 0.3))), "c2": mix((0, 0.7 * whir(0.4)), (0.35, cut(shing(), 0.3))), "c3": mix((0, 0.7 * whir(0.4)), (0.35, cut(shing(), 0.3))),
    "count": cut(whir(1.0), 0.7), "n2": 0.4 * cut(shing(), 0.3),
    "u0": mix((0, sw()), (0.35, 0.4 * cut(shing(), 0.3))), "u1": mix((0, sw()), (0.3, 0.4 * cut(shing(), 0.25))), "u2": mix((0, sw()), (0.3, 0.4 * cut(shing(), 0.25))),
    "print": mix((0, sw(0.5)), (0.35, 0.4 * cut(shing(), 0.3))), "print2": 0.3 * cut(shing(), 0.25),
    "brand": mix((0, sw(0.5)), (0.35, cut(shing(), 0.3))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.6 * chime(1.6)), (0.05, 0.9 * lounge(3.4))), {}))


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
