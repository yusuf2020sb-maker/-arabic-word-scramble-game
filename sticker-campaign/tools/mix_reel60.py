"""Reel 60 soundtrack with voiceover: ASMR peels and pops only in the gaps; lo-fi journal beat after the last line.
The hook peel is the one exception by design: it is placed in the gap right after "قشّره!".

usage: python3 mix_reel60.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav
from sfx_reel60 import lofi, peel, rip

V = [(0.22, 1.14), (1.64, 2.83), (3.51, 4.83), (5.29, 6.66), (7.46, 8.18), (9.07, 10.59), (11.11, 11.97), (12.65, 13.22), (13.83, 15.02),
     (15.71, 16.72), (17.59, 18.63), (19.00, 20.14), (20.91, 22.81), (23.17, 24.00), (24.59, 25.32)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
pk = lambda d: mix((0, peel(d)), (d * 0.75, mix(*[(j * 0.06, 0.25 * pop(0.08)) for j in range(3)])))
FX = {
    "h1": 0.2 * peel(0.3)[: int(0.3 * SR)],
    "c1": mix((0, peel(0.85)), (0.75, mix(*[(j * 0.06, 0.25 * pop(0.08)) for j in range(6)])), (1.2, pk(0.5))),  # reveal + first item
    "c2": pk(0.5), "c3": pk(0.5), "count": pk(0.5), "n2": 0.4 * rip(),
    "u0": pk(0.55), "u1": pk(0.45), "u2": pk(0.45), "print": pk(0.5), "brand": pk(0.55),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {"peel0": 0} if n == "c1" else {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.05, 0.9 * lofi(3.2))), {}))


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
