"""Reel 52 soundtrack with voiceover: camera glides, card flicks and cup clinks only in the gaps; tea-party waltz after the last line.

usage: python3 mix_reel52.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel17 import clink
from sfx_reel52 import flick, glide, party, stir

V = [(0.31, 1.13), (1.82, 3.25), (4.01, 4.60), (5.12, 5.87), (6.10, 6.82), (7.26, 8.77), (9.12, 10.02), (10.62, 11.40), (11.76, 12.57),
     (13.06, 13.69), (14.39, 15.33), (15.76, 16.99), (17.69, 19.10), (19.38, 20.26), (20.94, 21.81)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
mv = lambda: mix((0, glide(0.4)), (0.35, flick()))
FX = {
    "h1": mix((0, glide(0.5)), (0.4, flick())), "h2": flick(),
    "c1": mix((0, 0.4 * cut(stir(), 0.35)), (0.35, glide(0.4)), (0.7, flick())), "c2": mv(), "c3": mv(),
    "count": mix((0, glide(0.6)), (0.5, flick())), "n2": flick(),
    "u0": mv(), "u1": mv(), "u2": mv(), "print": mv(), "print2": flick(), "brand": mv(),
    "store2": 0.4 * cut(clink(), 0.2),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * clink()), (0.05, 0.6 * chime(1.4)), (0.1, 0.9 * party(3.2))), {}))


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
