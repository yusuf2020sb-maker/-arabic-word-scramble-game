"""Reel 36 soundtrack with voiceover: machine sounds only in the gaps; factory groove only after the last line.

usage: python3 mix_reel36.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, pop, read_wav, whoosh
from sfx_reel5 import printer
from sfx_reel8 import clunk
from sfx_reel9 import stamp_thud
from sfx_reel25 import punch
from sfx_reel36 import factory, hum

V = [(0.28, 1.18), (1.92, 2.56), (3.56, 4.04), (4.73, 5.47), (6.15, 6.72), (7.57, 9.34), (9.92, 10.70), (11.52, 12.03), (12.52, 13.15),
     (13.60, 14.64), (15.43, 16.30), (16.64, 17.38), (17.87, 19.00), (19.76, 20.60), (20.82, 21.91), (22.84, 23.97), (24.36, 25.27), (25.69, 26.61)]
SEG = dict(zip(["h1", "h1b", "k0", "k1", "k2", "count", "n2", "q0", "q1", "q2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
PLAN = [
    ("vo", "h1", {"h1": 0.0}), ("fx", 0.6 * cut(clunk(), 0.25), {}), ("vo", "h1b", {"h1b": 0.0}),
    ("fx", mix((0, 0.5 * whoosh(0.5)), (0, 0.8 * hum(1.0)), (0.5, 0.7 * cut(printer(0.5), 0.5))), {"k0": 0.55}), ("vo", "k0", {}),
    ("fx", mix((0, 0.9 * hum(0.95)), (0.1, 0.4 * cut(clunk(), 0.3)), *[(0.6 + i * 0.07, 0.5 * punch()) for i in range(4)]), {"k1": 0.65}), ("vo", "k1", {}),
    ("fx", mix((0, 0.9 * hum(1.0)), (0.1, 0.4 * cut(clunk(), 0.3)), (0.7, cut(stamp_thud(), 0.3))), {"k2": 0.75}), ("vo", "k2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.5)), *[(0.45 + i * 0.06, 0.3 * pop(0.1)) for i in range(4)]), {"count": 0.45}), ("vo", "count", {}), ("vo", "n2", {"n2": 0}),
    ("fx", 0.6 * whoosh(0.4), {"q0": 0.3}), ("vo", "q0", {}),
    ("fx", 0.5 * whoosh(0.3), {"q1": 0.15}), ("vo", "q1", {}),
    ("fx", 0.5 * whoosh(0.3), {"q2": 0.15}), ("vo", "q2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.45)), (0.8, 0.8 * cut(stamp_thud(), 0.25))), {"u0": 0.4}), ("vo", "u0", {}),
    ("fx", mix((0, 0.4 * whoosh(0.3)), (0.55, 0.8 * cut(stamp_thud(), 0.25))), {"u1": 0.25}), ("vo", "u1", {}),
    ("fx", mix((0, 0.4 * whoosh(0.3)), (0.55, 0.8 * cut(stamp_thud(), 0.25))), {"u2": 0.25}), ("vo", "u2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.45)), (0.4, 0.5 * cut(printer(0.5), 0.5))), {"print": 0.45}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", mix((0, 0.6 * whoosh(0.45)), (0.5, 0.7 * cut(stamp_thud(), 0.3))), {"brand": 0.45}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.8 * factory(2.6)), (0.1, 0.6 * chime(1.4))), {}),
]


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
