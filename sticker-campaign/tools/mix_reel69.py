"""Reel 69 soundtrack with voiceover: laser chirp, glass whoosh, gallery footsteps, spotlight clunks and sparkle only in the gaps;
chime and piano after the last line.

usage: python3 mix_reel69.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle, whoosh
from sfx_reel22 import piano
from sfx_reel64 import clunk
from sfx_reel65 import tick
from sfx_reel69 import chirp_down, step

V = [(0.0, 0.49), (1.17, 2.19), (2.58, 3.46), (4.03, 5.04), (5.17, 6.11), (6.34, 7.62), (8.18, 9.46), (9.72, 10.71),
     (11.41, 12.04), (12.16, 12.88), (13.05, 13.79), (14.46, 15.35), (15.44, 17.42), (17.88, 19.49), (19.68, 20.33), (20.42, 21.11)]
NAMES = ["h1", "h1b", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
STEPS = mix(*[(i * 0.13, 0.35 * step()) for i in range(3)])
FX = {
    "h2": mix((0, 0.6 * chirp_down(0.3)), (0.05, 0.35 * whoosh(0.3))),
    "c1": STEPS, "c2": STEPS, "c3": STEPS,
    "count": mix(*[(i * 0.03, 0.2 * tick()) for i in range(6)]), "n2": 0.45 * sparkle(0.35),
    "u0": 0.6 * clunk(), "u1": 0.6 * clunk(), "u2": 0.6 * clunk(), "print": 0.3 * whoosh(0.35), "print2": 0.35 * whoosh(0.3), "brand": 0.5 * clunk(),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.45 * chime(1.4)), (0.05, 0.5 * mix(*[(j * 0.16, piano(f)) for j, f in enumerate((587, 740, 880, 1174))]))), {}))


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
