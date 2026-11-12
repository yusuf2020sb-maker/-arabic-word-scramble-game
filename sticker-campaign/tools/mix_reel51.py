"""Reel 51 soundtrack with voiceover: beeps, coil whirs, thunks and neon buzz only in the gaps; vending-machine pop + cha-ching after the last line.

usage: python3 mix_reel51.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, mix, norm, pop, read_wav
from sfx_reel51 import beep, bop, buzz, ching, thunk, whir

V = [(0.27, 1.07), (1.44, 2.48), (3.31, 3.78), (4.48, 5.02), (5.53, 6.46), (7.48, 8.96), (9.39, 10.42), (11.21, 11.91), (12.37, 13.59),
     (14.08, 15.04), (15.91, 16.76), (17.18, 18.23), (18.86, 20.33), (20.75, 21.53), (22.04, 22.90)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
# visual timing per item: key press at k-0.6, coil k-0.4..k-0.15, item drops k-0.15..k+0.25 (thunk lands after the word starts, so keep it in the gap before)
vend = mix((0, beep(1500)), (0.15, whir(0.25)), (0.42, 0.5 * thunk(0.15)))
FX = {
    "h1": cut(buzz(), 0.25), "h2": cut(buzz(), 0.25),
    "c1": mix((0, 0.5 * whir(0.3)), (0.35, vend)), "c2": vend, "c3": vend,
    "count": mix((0, cut(buzz(), 0.25)), *[(0.3 + i * 0.1, 0.2 * pop(0.08)) for i in range(4)]), "n2": 0.4 * beep(1800),
    "u0": mix((0, 0.5 * whir(0.4)), (0.4, 0.4 * pop())), "u1": 0.4 * pop(), "u2": 0.4 * pop(),
    "print": mix((0, 0.5 * whir(0.4)), (0.35, 0.5 * whir(0.4))), "print2": 0.4 * beep(1800),
    "brand": mix((0, cut(buzz(), 0.25)), (0.3, 0.5 * pop())), "store": 0.4 * beep(1500), "store2": cut(buzz(), 0.2),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, ching()), (0.1, 0.9 * bop(3.2))), {}))


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
