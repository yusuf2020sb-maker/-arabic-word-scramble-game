"""Reel 57 soundtrack with voiceover: gear ratchets, ticks and small bells only in the gaps; clockwork waltz + hour bell after the last line.

usage: python3 mix_reel57.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel8 import tick
from sfx_reel57 import bell, clockwork, ratchet, ticks

V = [(0.24, 1.22), (2.07, 3.92), (4.80, 5.83), (6.73, 7.54), (8.11, 8.99), (9.54, 11.21), (11.48, 12.36), (13.15, 14.00), (14.68, 15.58),
     (15.87, 17.24), (18.33, 19.29), (19.79, 20.96), (21.50, 23.68), (24.43, 25.21), (25.82, 26.55)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
cut = lambda x, d: x[:int(d * SR)]
FX = {
    "h1": ticks(0.5, 4), "h2": 0.3 * cut(bell(523.3, 1.0), 0.3),
    "c1": mix((0, ticks(0.25, 4)), (0.2, ratchet(8, 0.05)), (0.6, 0.3 * cut(bell(659.3, 0.6), 0.25))), "c2": mix((0, ratchet(7, 0.05)), (0.38, 0.3 * cut(bell(659.3, 0.6), 0.25))), "c3": mix((0, ratchet(7, 0.05)), (0.38, 0.3 * cut(bell(659.3, 0.6), 0.25))),
    "count": mix((0, ratchet(14, 0.04)), *[(0.6 + i * 0.06, 0.3 * tick(0.03)) for i in range(3)]), "n2": 0.3 * cut(bell(587.3, 0.6), 0.25),
    "u0": ratchet(5), "u1": ratchet(4), "u2": ratchet(4), "print": ratchet(6), "print2": 0.3 * cut(bell(659.3, 0.6), 0.25), "brand": ratchet(7),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.6 * bell(440.0, 2.0)), (0.05, 0.4 * chime(1.4)), (0.1, 0.9 * clockwork(3.2))), {}))


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
