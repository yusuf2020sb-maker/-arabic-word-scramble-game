"""Builds the reel 22 soundtrack with the voiceover: score and effects only in the gaps.

usage: python3 mix_reel22.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, sparkle, whoosh
from sfx_reel8 import tick
from sfx_reel10 import boom, riser
from sfx_reel22 import PROG, pad, piano, ping

SEGMENTS = {
    "h1": (0.27, 1.27),      # بعض الأشياء…
    "h2": (1.47, 2.70),      # ما تطلع من الموضة أبد
    "title": (3.28, 5.04),   # ستيكرات فنتج كلاسيكية
    "kinds": (5.84, 9.41),   # كتب، ساعات، شموع، ورسائل
    "count": (10.07, 12.50), # اثنين وستين تصميم بطابع عتيق
    "ready": (12.91, 13.84), # جاهزة للطباعة
    "u0": (14.47, 15.90),    # للهدايا والرسائل
    "u1": (16.39, 17.88),    # للدفاتر والجورنال
    "u2": (18.31, 19.36),    # ولتغليف طلباتك
    "brand": (19.99, 21.71), # ستيكرات فنتج كلاسيكية
    "store": (22.33, 22.85), # في المتجر
}

def faded(x, fin=0.25, fout=0.35):
    n = len(x); e = np.ones(n); a = int(fin * SR); b = int(fout * SR)
    e[:a] = np.linspace(0, 1, a); e[-b:] = np.linspace(1, 0, b); return x * e

opening = mix((0, faded(pad(PROG[0], 1.4), 0.5, 0.4)), (0.2, 0.5 * tick(0.03)), (0.7, 0.5 * tick(0.03)), (0.3, 0.8 * piano(659.3, 1.1)))
fly = mix((0, riser(0.7)), (0.7, boom(0.9)), (0.75, faded(pad(PROG[1], 0.8), 0.2, 0.4)))
wall = mix((0, boom(0.7)), (0.05, sparkle(0.8)), (0.1, faded(pad(PROG[2], 1.0), 0.2, 0.5)))
sheet = mix((0, whoosh(0.6)), (0.3, 0.6 * sparkle(0.8)), (0.6, 0.7 * ping()), (0.9, 0.7 * ping()), (1.2, 0.7 * ping()))
pan = lambda f: mix((0, whoosh(0.45)), (0.15, 0.6 * piano(f, 0.5)))
end = mix((0, boom(0.8)), (0.1, sparkle(1.0)), (0.2, faded(pad(PROG[3], 1.1), 0.3, 0.5)))
outro = mix((0, piano(220.0, 2.6)), (0, piano(329.6, 2.6)), (0, piano(440.0, 2.6)), (0.02, piano(659.3, 2.6)), (0.6, 0.6 * chime(1.2)), (0, faded(pad(PROG[0], 2.8), 0.3, 1.2)))

PLAN = [
    ("fx:open", norm(opening, -15)), ("vo", "h1"), ("vo", "h2"),
    ("fx:fly", norm(fly, -12)), ("vo", "title"), ("vo", "kinds"),
    ("fx:wall", norm(wall, -12)), ("vo", "count"),
    ("fx:sheet", norm(sheet, -14)), ("vo", "ready"),
    ("fx:p0", norm(pan(392.0), -15)), ("vo", "u0"),
    ("fx:p1", norm(pan(440.0), -15)), ("vo", "u1"),
    ("fx:p2", norm(pan(523.3), -15)), ("vo", "u2"),
    ("fx:end", norm(end, -13)), ("vo", "brand"), ("vo", "store"),
    ("fx:outro", norm(outro, -13)),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path)
    GAP = 0.06
    out = [np.zeros(int(0.1 * SR))]; t = 0.1; tl = {}
    for kind, item in PLAN:
        x = voice[int(SEGMENTS[item][0] * SR):int(SEGMENTS[item][1] * SR)] if kind == "vo" else item
        label = item if kind == "vo" else kind[3:]
        tl[label] = round(t, 3); tl[label + "_end"] = round(t + len(x) / SR, 3)
        print(f"{kind[:2]}\t{label}\t{t:.2f}\t{t + len(x) / SR:.2f}")
        out += [x, np.zeros(int(GAP * SR))]
        t += len(x) / SR + GAP
    tl["end_all"] = round(t + 0.2, 3)
    y = np.clip(np.concatenate(out + [np.zeros(int(0.2 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    with open(tl_path, "w") as f:
        f.write("window.TL = " + json.dumps(tl) + ";\n")
    print(f"total\t\t0\t{tl['end_all']:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
