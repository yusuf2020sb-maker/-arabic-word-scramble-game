"""Reel 68 soundtrack with voiceover: fluorescent flicker, torch clicks, beam swishes and pops only in the gaps;
chime and music box after the last line.

usage: python3 mix_reel68.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav
from sfx_reel18 import clack
from sfx_reel68 import flicker, music_box, powerdown, swish

V = [(0.0, 0.85), (1.51, 2.18), (2.70, 3.93), (4.58, 5.66), (5.96, 6.71), (7.06, 8.63), (9.21, 11.26), (11.31, 12.20),
     (12.75, 13.52), (13.87, 14.82), (15.12, 16.32), (16.88, 17.79), (18.18, 20.17), (20.93, 22.52), (22.80, 23.79), (23.81, 24.40)]
NAMES = ["h1", "h1b", "h2", "c1", "c2", "c3", "count", "n2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"]
SEG = dict(zip(NAMES, V))
SW = lambda: mix((0, 0.4 * swish(0.3)), (0.22, 0.25 * pop()))
FX = {
    "h1b": 0.6 * flicker(0.45), "h2": mix((0, 0.5 * powerdown(0.3)), (0.12, 0.8 * clack())),
    "c1": SW(), "c2": SW(), "c3": SW(),
    "count": mix((0, 0.7 * flicker(0.45)), (0.0, 0.5 * clack())),
    "u0": mix((0, 0.7 * clack()), (0.05, 0.4 * powerdown(0.3))), "u1": 0.4 * swish(0.3), "u2": 0.4 * swish(0.3), "print": 0.4 * swish(0.3),
    "print2": 0.6 * flicker(0.4), "brand": 0.7 * clack(),
}
PLAN = []
for n in NAMES:
    if n in FX:
        PLAN.append(("fx", FX[n], {}))
    PLAN.append(("vo", n, {n: 0}))
PLAN.append(("fx", mix((0, 0.45 * chime(1.4)), (0.1, 0.6 * music_box((523, 659, 784, 1046, 784)))), {}))


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
