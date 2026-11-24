"""Reel 64 soundtrack with voiceover: REC clunk, autofocus beeps, zoom whines, glitches and whooshes only in the gaps;
PAUSE clunk, chime and hijaz groove after the last line.

usage: python3 mix_reel64.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, whoosh
from sfx_reel64 import beep, clunk, glitch, groove, snip, zoomwhine

V = [(0.20, 3.37), (3.86, 4.93), (4.93, 5.73), (6.01, 6.77), (7.18, 8.90), (9.29, 10.51), (11.09, 12.55), (12.77, 13.84),
     (14.11, 15.28), (15.97, 16.84), (17.31, 19.09), (19.56, 21.34), (21.65, 22.25), (22.27, 22.87)]
NAMES = ["h1", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
AF = mix((0, 0.6 * zoomwhine(0.3)), (0.2, beep()), (0.29, 0.8 * beep(3000, 0.05)))
WIPE = mix((0, 0.6 * whoosh(0.35)), (0.1, 0.5 * glitch()))
FX = {
    "c1": AF, "c2": AF, "c3": AF,
    "count": mix((0, 0.5 * whoosh(0.3)), *[(0.12 + j * 0.03, 0.2 * pop()) for j in range(8)]),
    "u0": WIPE, "u1": WIPE, "u2": WIPE, "print": WIPE, "print2": 0.8 * snip(), "brand": WIPE,
}
PLAN = [("fx", 0.8 * clunk(), {})]
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.8 * clunk()), (0.1, 0.5 * chime(1.4)), (0.15, 0.7 * groove(3.0))), {}))


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.05
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else norm(item, -12)
        for k, off in keys.items():
            tl[k] = round(t + off, 3)
        if kind == "vo" and item == "h1":
            tl["h2"] = round(t + 1.69, 3)  # "لحظة... هذي ستيكرات" starts inside the first take
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
