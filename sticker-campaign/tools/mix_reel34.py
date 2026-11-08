"""Reel 34 soundtrack with voiceover: paper, tape, scissor and pencil sounds only in the gaps.

usage: python3 mix_reel34.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav
from sfx_reel5 import rip, scribble
from sfx_reel13 import paper
from sfx_reel16 import page
from sfx_reel24 import snip
from sfx_reel34 import groove

V = [(0.29, 1.21), (1.87, 2.82), (3.69, 4.45), (4.78, 5.53), (5.95, 6.87), (7.02, 7.96), (8.62, 10.24), (10.73, 11.62),
     (12.24, 12.70), (13.35, 13.83), (14.27, 15.80), (16.49, 18.19), (18.74, 19.80), (20.38, 20.94)]
SEG = dict(zip(["h1", "h2", "k0", "k1", "k2", "k3", "count", "c2", "s0", "s1", "s2", "print", "brand", "store"], V))
slap = lambda: mix((0, 0.7 * paper(0.15)), (0.2, 0.5 * rip(0.2)))
PLAN = [
    ("fx", 0.5 * scribble(0.3), {"h1": 0.05}), ("vo", "h1", {}),
    ("fx", 0.5 * scribble(0.35), {"h2": 0.0}), ("vo", "h2", {}),
    ("fx", mix((0, 0.7 * page(0.45)), (0.3, 0.7 * paper(0.15))), {"k0": 0.45}), ("vo", "k0", {}),
    ("fx", slap(), {"k1": 0.15}), ("vo", "k1", {}),
    ("fx", slap(), {"k2": 0.15}), ("vo", "k2", {}),
    ("fx", slap(), {"k3": 0.15}), ("vo", "k3", {}),
    ("fx", mix((0, 0.7 * page(0.45)), (0.35, 0.7 * paper(0.15)), (0.6, 0.7 * paper(0.15))), {"count": 0.45}), ("vo", "count", {}),
    ("fx", 0.6 * rip(0.25), {"c2": 0.1}), ("vo", "c2", {}),
    ("fx", mix((0, 0.7 * page(0.45)), (0.35, 0.5 * snip())), {"s0": 0.45}), ("vo", "s0", {}),
    ("fx", mix(*[(i * 0.13, 0.5 * snip()) for i in range(3)], (0.4, 0.6 * rip(0.25))), {"s1": 0.45}), ("vo", "s1", {}),
    ("fx", mix(*[(i * 0.08, 0.35 * paper(0.1)) for i in range(13)]), {"s2": 0.2}), ("vo", "s2", {}),
    ("fx", mix((0, 0.7 * page(0.45)), (0.35, 0.5 * paper(0.2))), {"print": 0.45}), ("vo", "print", {}),
    ("fx", mix((0, 0.7 * page(0.45)), (0.4, 0.6 * paper(0.2)), (0.75, 0.5 * rip(0.2)), (0.85, 0.5 * rip(0.2))), {"brand": 0.45}), ("vo", "brand", {}),
    ("fx", np.zeros(int(0.08 * SR)), {}), ("vo", "store", {"store": 0}),
    ("fx", mix((0, 0.8 * groove(2.6)), (0.1, 0.6 * chime(1.4)), (0.3, 0.4 * scribble(0.5))), {}),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path); GAP = 0.05
    out = [np.zeros(int(0.05 * SR))]; t = 0.05; tl = {}
    for kind, item, keys in PLAN:
        x = voice[int(SEG[item][0] * SR):int(SEG[item][1] * SR)] if kind == "vo" else (norm(item, -12) if np.abs(item).max() > 0 else item)
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
