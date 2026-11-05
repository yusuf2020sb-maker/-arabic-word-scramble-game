"""Builds the reel 16 soundtrack with the voiceover: rain and room sounds only in the gaps.

usage: python3 mix_reel16.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, mix, norm, read_wav, sparkle, whoosh
from sfx_reel5 import pop, thump
from sfx_reel16 import crackle, musicbox, page, rain, squeak, thunder, wood

SEGMENTS = {
    "mtr": (0.29, 0.71),     # مطر
    "shay": (1.33, 1.81),    # شاي
    "kitab": (2.37, 2.91),   # وكتاب
    "shuur": (3.47, 4.32),   # الشعور هذا
    "sar": (4.60, 5.70),     # صار ستيكرات
    "title": (6.29, 7.59),   # ستيكرات البيت الدافئ
    "count": (7.98, 9.90),   # مية وستة وثلاثين تصميم
    "pg0": (10.62, 12.11),   # لصفحة جورنال هادية
    "pg1": (12.64, 14.15),   # لبطاقة هدية شتوية
    "pg2": (14.64, 16.14),   # ولطلب يوصل دافي
    "d1": (16.89, 17.37),    # الدفء؟
    "d2": (17.81, 19.45),    # في ملف… تطبعه في بيتك
}

gap_rain = lambda d: rain(d, 0.5)
N_DROP, DROP_D = 12, 0.18
drops = mix(*[(i * DROP_D + 0.17, wood()) for i in range(N_DROP)], *[(i * DROP_D + 0.18, 0.3 * whoosh(0.12)) for i in range(N_DROP)])
PLAN = [
    ("fx:intro", norm(mix((0, gap_rain(1.3)), (0, thunder(1.3))), -14)), ("vo", "mtr"),
    ("fx:r1", norm(mix((0, gap_rain(0.45)), (0.05, sparkle(0.3))), -20)), ("vo", "shay"),
    ("fx:r2", norm(mix((0, gap_rain(0.45)), (0.05, sparkle(0.3))), -20)), ("vo", "kitab"),
    ("fx:r3", norm(gap_rain(0.5), -20)), ("vo", "shuur"), ("vo", "sar"),
    ("fx:wipe", norm(mix((0, gap_rain(0.4)), (0.3, squeak(0.5)), (0.32, whoosh(0.5))), -15)),
    ("fx:drops", norm(drops, -11)), ("vo", "title"),
    ("fx:s3fx", norm(mix((0, whoosh(0.45)), (0.2, crackle(0.8))), -14)), ("vo", "count"),
    ("fx:bookfx", norm(mix((0, whoosh(0.4)), (0.4, 0.6 * thump(0.15))), -14)), ("vo", "pg0"),
    ("fx:flip0", norm(page(), -12)), ("vo", "pg1"),
    ("fx:flip1", norm(page(), -12)), ("vo", "pg2"),
    ("fx:endfx", norm(mix((0, gap_rain(0.8)), (0.35, thump(0.2))), -15)), ("vo", "d1"), ("vo", "d2"),
    ("fx:box", norm(musicbox(), -13)),
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
    tl["end_all"] = round(t + 0.3, 3); tl["n_drop"] = N_DROP; tl["drop_d"] = DROP_D
    y = np.clip(np.concatenate(out + [np.zeros(int(0.3 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    with open(tl_path, "w") as f:
        f.write("window.TL = " + json.dumps(tl) + ";\n")
    print(f"total\t\t0\t{tl['end_all']:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
