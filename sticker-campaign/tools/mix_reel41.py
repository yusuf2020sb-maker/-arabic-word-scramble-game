"""Reel 41 soundtrack with voiceover: firework whistles/booms and sparkler fizz only in the gaps; the zaffa after the last line.

usage: python3 mix_reel41.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle
from sfx_reel10 import boom
from sfx_reel41 import fizz, whistle_up, zaffa

V = [(0.22, 1.42), (1.61, 2.92), (3.47, 3.99), (4.34, 4.87), (5.25, 5.75), (6.28, 6.78), (7.15, 7.69), (8.01, 8.75), (9.23, 10.50),
     (10.70, 11.76), (12.19, 13.12), (13.30, 14.19), (14.53, 15.70), (16.15, 17.05), (17.29, 18.35), (18.96, 20.06), (20.38, 21.31), (21.69, 22.56)]
SEG = dict(zip(["h1", "h2", "a0", "a1", "a2", "b0", "b1", "b2", "title", "t2", "u0", "u1", "u2", "print", "print2", "brand", "store", "store2"], V))
cut = lambda x, d: x[:int(d * SR)]
fw = lambda: mix((0, whistle_up()), (0.45, 0.8 * cut(boom(0.9), 0.3)))
PLAN = [
    ("vo", "h1", {"h1": 0.0}),
    ("fx", fw(), {"h2": 0.6}), ("vo", "h2", {}),
    ("fx", fw(), {"a0": 0.65}), ("vo", "a0", {}),
    ("fx", fw(), {"a1": 0.65}), ("vo", "a1", {}),
    ("fx", fw(), {"a2": 0.65}), ("vo", "a2", {}),
    ("fx", fw(), {"b0": 0.65}), ("vo", "b0", {}),
    ("fx", fw(), {"b1": 0.65}), ("vo", "b1", {}),
    ("fx", fw(), {"b2": 0.65}), ("vo", "b2", {}),
    ("fx", mix((0, fw()), (0.75, 0.4 * cut(sparkle(0.5), 0.3))), {"title": 0.7}), ("vo", "title", {}),
    ("fx", 0.5 * cut(fizz(0.3), 0.25), {"t2": 0.1}), ("vo", "t2", {}),
    ("fx", 0.5 * cut(fizz(0.4), 0.35), {"u0": 0.3}), ("vo", "u0", {}),
    ("fx", 0.5 * cut(fizz(0.3), 0.25), {"u1": 0.2}), ("vo", "u1", {}),
    ("fx", 0.5 * cut(fizz(0.3), 0.25), {"u2": 0.2}), ("vo", "u2", {}),
    ("fx", 0.5 * cut(fizz(0.4), 0.4), {"print": 0.35}), ("vo", "print", {}), ("vo", "print2", {}),
    ("fx", fw(), {"brand": 0.7}), ("vo", "brand", {}),
    ("vo", "store", {"store": 0}), ("vo", "store2", {"store2": 0}),
    ("fx", mix((0, 0.9 * zaffa(2.8)), (0.05, 0.6 * chime(1.4)), (0.1, 0.4 * sparkle(1.0))), {}),
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
