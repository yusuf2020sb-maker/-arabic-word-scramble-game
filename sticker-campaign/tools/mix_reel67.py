"""Reel 67 soundtrack with voiceover: glassy taps, pops and soft whooshes only in the gaps;
chime, piano arpeggio and ambient pad after the last line.

usage: python3 mix_reel67.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, whoosh
from sfx_reel22 import pad, piano
from sfx_reel66 import tap
from sfx_reel67 import wilt

V = [(0.0, 0.94), (1.68, 3.03), (4.10, 4.98), (5.80, 6.42), (7.04, 7.82), (8.20, 9.22), (10.09, 11.71), (12.45, 13.55),
     (14.27, 15.24), (15.26, 16.10), (16.47, 17.51), (18.22, 19.29), (19.41, 22.09), (22.77, 23.87), (24.49, 25.00), (25.52, 26.86)]
NAMES = ["h1", "h1b", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
T = lambda f: tap(f, 0.3)
FX = {
    "h1b": 0.45 * wilt(0.35), "h2": T(1568), "c1": T(880), "c2": T(1046), "c3": T(1318),
    "count": mix((0, 0.3 * whoosh(0.3)), *[(0.15 + j * 0.03, 0.25 * pop()) for j in range(6)]),
    "u0": T(1174), "u1": T(1318), "u2": T(1568), "print": mix((0, 0.3 * whoosh(0.3)), (0.2, T(1568))), "brand": 0.4 * whoosh(0.35),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.05, 0.6 * mix(*[(j * 0.12, piano(f)) for j, f in enumerate((523, 659, 784, 1046))])), (0.1, 0.35 * pad((130.8, 196, 261.6, 329.6), 3.0))), {}))


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
