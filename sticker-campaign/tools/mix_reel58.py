"""Reel 58 soundtrack with voiceover: door creaks, light-switch clicks, pops and a doorbell only in the gaps; winter music box after the last line.

usage: python3 mix_reel58.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav
from sfx_reel10 import creak
from sfx_reel58 import doorbell, mbox, night, switch, wind

V = [(0.22, 1.04), (1.58, 3.37), (3.97, 4.52), (5.15, 5.79), (6.32, 7.18), (7.99, 10.30), (10.64, 11.47), (12.16, 12.88), (13.49, 14.31),
     (14.82, 16.03), (16.82, 17.94), (18.64, 19.80), (20.58, 21.93), (22.59, 23.47), (24.08, 24.72)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
lamp = lambda: mix((0, cut(switch(), 0.3)), (0.05, 0.25 * pop(0.08)))
FX = {
    "h1": cut(wind(1.0), 0.5), "h2": 0.3 * cut(mbox(1318.5, 0.5), 0.25),
    "c1": mix((0, 0.6 * cut(creak(), 0.4)), (0.4, lamp())), "c2": lamp(), "c3": lamp(),
    "count": mix(*[(i * 0.08, 0.2 * pop(0.08)) for i in range(5)]), "n2": 0.3 * cut(mbox(1318.5, 0.5), 0.25),
    "u0": 0.3 * cut(pop(), 0.15), "u1": 0.3 * cut(pop(), 0.15), "u2": 0.3 * cut(pop(), 0.15),
    "print": 0.3 * cut(mbox(1174.7, 0.5), 0.3), "print2": 0.25 * cut(pop(), 0.15),
    "brand": mix((0, 0.5 * cut(creak(), 0.4)), (0.4, 0.3 * cut(pop(), 0.15))),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, doorbell()), (0.1, 0.4 * chime(1.4)), (0.15, 0.9 * night(3.2))), {}))


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
