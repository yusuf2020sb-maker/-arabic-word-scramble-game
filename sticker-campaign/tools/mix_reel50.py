"""Reel 50 soundtrack with voiceover: wipes/squeaks/breaths only in the gaps; felt-piano lullaby after the last line.

usage: python3 mix_reel50.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel16 import crackle, squeak, thunder
from sfx_reel50 import breath, felt, wipe

V = [(0.16, 1.14), (1.72, 2.49), (3.24, 4.04), (4.60, 5.48), (6.02, 7.04), (7.83, 9.35), (9.68, 10.60), (11.21, 11.99), (12.40, 13.49),
     (14.00, 15.11), (15.69, 16.70), (17.17, 18.33), (18.97, 20.38), (20.94, 21.70), (22.21, 23.00)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
FX = {
    "h1": mix((0, 0.5 * cut(thunder(2.0), 0.5)), (0.25, 0.4 * cut(squeak(0.6), 0.3))), "h2": 0.4 * cut(squeak(0.6), 0.25),
    "c1": mix((0, breath()), (0.4, 0.5 * wipe())), "c2": 0.5 * cut(wipe(), 0.4), "c3": 0.5 * cut(wipe(), 0.4),
    "count": mix((0, breath()), (0.4, 0.4 * cut(squeak(0.5), 0.3))), "n2": 0.3 * cut(squeak(0.5), 0.2),
    "u0": mix((0, breath()), (0.4, 0.5 * wipe())), "u1": 0.5 * cut(wipe(), 0.4), "u2": 0.5 * cut(wipe(), 0.4),
    "print": mix((0, breath()), (0.4, 0.5 * cut(wipe(0.5), 0.4))), "print2": 0.3 * cut(squeak(0.5), 0.25),
    "brand": mix((0, breath()), (0.4, 0.5 * cut(wipe(0.5), 0.4))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.6 * chime(1.6)), (0.05, 0.9 * felt(3.4)), (0.2, 0.3 * crackle(3.0))), {}))


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
