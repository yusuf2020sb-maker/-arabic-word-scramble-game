"""Reel 61 soundtrack with voiceover: zoom-out swells and stamp thuds only in the gaps; strings outro after the last line.

usage: python3 mix_reel61.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel9 import stamp_thud
from sfx_reel61 import strings, zoomout

V = [(0.10, 0.93), (1.78, 2.64), (3.30, 3.87), (4.36, 4.99), (5.42, 6.06), (6.61, 8.28), (8.33, 9.50), (9.98, 11.06), (11.39, 12.33),
     (12.65, 13.90), (14.56, 15.49), (15.75, 16.86), (17.47, 18.74), (19.30, 20.10), (20.57, 21.42)]
NAMES = ["h1", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
z = lambda: zoomout(0.5)
FX = {
    "h2": mix((0, zoomout(0.7)), (0.75, 0.6 * stamp_thud())),
    "c1": z(), "c2": z(), "c3": z(), "count": mix((0, z()), (0.55, 0.3 * sparkle())),
    "n2": 0.5 * stamp_thud(), "u0": z(), "u1": z(), "u2": z(), "print": z(), "brand": z(),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.5 * chime(1.4)), (0.05, 0.8 * strings(3.0))), {}))


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
