"""Builds the reel 20 soundtrack with the voiceover: lo-fi music and desk sounds only in the gaps.

usage: python3 mix_reel20.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick
from sfx_reel18 import pen, slide, tear
from sfx_reel20 import lofi, pat, peel

SEGMENTS = {
    "pov": (0.29, 2.08),      # POV: ساعتك المفضلة في الأسبوع
    "daftar": (2.88, 3.69),   # دفتر فاضي
    "stk": (4.22, 6.07),      # وستيكرات جورنال فنتج
    "saa": (6.79, 7.66),      # ساعة وحدة
    "page": (8.19, 9.63),     # وصفحتك صارت كذا
    "count": (10.77, 12.24),  # ثمانية وستين تصميم
    "kinds": (12.86, 16.88),  # ورق عتيق، زهور مجففة، ريش وحبر
    "next": (17.68, 18.52),   # صفحتك الجاية؟
    "starts": (19.16, 19.69), # تبدأ من هنا
}

N, STEP = 11, 0.6
LAPSE = 0.2 + N * STEP + 0.3
lapse = mix((0, 0.8 * lofi(LAPSE)),
            *[(0.2 + k / 8, 0.25 * tick(0.02)) for k in range(int(N * STEP * 8))],
            (0.2, 0.7 * tear(0.22)), (0.3, 0.4 * slide(0.45)),
            *[x for i in range(1, N) for x in ((0.2 + i * STEP, 0.6 * peel()), (0.2 + i * STEP + 0.2, 0.25 * whoosh(0.28)), (0.2 + i * STEP + 0.5, 0.8 * pat()))])
PLAN = [
    ("fx:intro", norm(mix((0, lofi(1.6)), (0.3, 0.3 * tick(0.03)), (1.3, 0.3 * tick(0.03))), -17)), ("vo", "pov"),
    ("fx:open", norm(mix((0, whoosh(0.6)), (0.75, thump(0.3)), (0.75, 0.4 * slide(0.2))), -13)), ("vo", "daftar"), ("vo", "stk"),
    ("fx:lapse", norm(lapse, -13)), ("vo", "saa"),
    ("fx:pen", norm(pen(0.8), -18)), ("vo", "page"),
    ("fx:zoom", norm(mix((0, slide(0.6)), (0.1, 0.6 * whoosh(0.7))), -16)), ("vo", "count"),
    ("fx:chips", norm(mix(*[(i * 0.15, pop(600 + i * 100, 0.1)) for i in range(4)]), -16)), ("vo", "kinds"),
    ("fx:close", norm(mix((0, whoosh(0.5)), (0.55, thump(0.3)), (0.75, whoosh(0.5))), -13)), ("vo", "next"), ("vo", "starts"),
    ("fx:outro", norm(mix((0, lofi(2.6)), (0.1, 0.8 * chime(1.0))), -15)),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path)
    GAP = 0.06
    out = [np.zeros(int(0.1 * SR))]; t = 0.1; tl = {"n": N, "step": STEP}
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
