"""Builds the reel 19 soundtrack with the voiceover: album effects only in the gaps.

usage: python3 mix_reel19.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick
from sfx_reel18 import postmark, tear, typing
from sfx_reel19 import reveal, swish

SEGMENTS = {
    "hook": (0.20, 1.38),    # أي ستيكر يشبهك؟
    "sub": (1.93, 3.75),     # ستيكرات على شكل طوابع زهور
    "nums": (4.28, 7.37),    # واحد، ولا اثنين، ولا ثلاثة، ولا أربعة؟
    "n0": (8.11, 9.88),      # واحد: حضور يلفت
    "n1": (10.33, 12.06),    # اثنين: هدوء وأناقة
    "n2": (12.58, 14.28),    # ثلاثة: طاقة وفرح
    "n3": (14.80, 16.52),    # أربعة: خيال وإبداع
    "you": (16.99, 18.80),   # وأنت؟ رقمك في التعليقات
    "count": (19.52, 23.42), # خمسة وثلاثين ستيكر طابع زهور… تطبعها في بيتك وتلصقها
    "store": (23.87, 24.90), # وستيكرك في المتجر
}

short = lambda x, d: x[:int(d * SR)] * np.linspace(1, 0, int(d * SR)) ** 0.6
shuffle = mix((0, whoosh(0.4)), *[(0.3 + s * 0.6 + k * 0.06, 0.7 * swish(0.3)) for s in range(3) for k in range(4)],
              (1.9, mix(*[(k * 0.06, pop(800 + k * 120, 0.08)) for k in range(4)])), *[(2.1 + k * 0.2, 0.6 * tick(0.03)) for k in range(4)])
rev = lambda f: mix((0, 0.6 * whoosh(0.35)), (0.2, short(reveal(f), 0.7)))
s4 = mix((0, whoosh(0.45)), (0.25, pop(600, 0.14)))
s5 = mix((0, whoosh(0.45)), *[(0.2 + i * 0.15, pop(600 + i * 100, 0.1)) for i in range(3)], (0.5, tear(0.25)), (0.85, postmark()))

PLAN = [
    ("fx:slam", norm(mix((0, whoosh(0.3)), (0.25, thump(0.3)), (0.27, pop(500, 0.18))), -9)), ("vo", "hook"), ("vo", "sub"), ("vo", "nums"),
    ("fx:shuffle", norm(shuffle, -11)),
    ("fx:rev0", norm(rev(523), -10)), ("vo", "n0"),
    ("fx:rev1", norm(rev(659), -10)), ("vo", "n1"),
    ("fx:rev2", norm(rev(784), -10)), ("vo", "n2"),
    ("fx:rev3", norm(rev(988), -10)), ("vo", "n3"),
    ("fx:s4fx", norm(s4, -12)), ("vo", "you"),
    ("fx:typefx", norm(typing(4, 0.25), -16)), ("vo", "count"),
    ("fx:s5fx", norm(s5, -10)), ("vo", "store"),
    ("fx:chime", norm(chime(1.0), -12)),
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
    tl["end_all"] = round(t + 0.4, 3)
    y = np.clip(np.concatenate(out + [np.zeros(int(0.4 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    with open(tl_path, "w") as f:
        f.write("window.TL = " + json.dumps(tl) + ";\n")
    print(f"total\t\t0\t{tl['end_all']:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
