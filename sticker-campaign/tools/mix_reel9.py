"""Builds the reel 9 soundtrack with the voiceover: voice clips in order and the
before/after sound effects only in the gaps (never over speech).

usage: python3 mix_reel9.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick
from sfx_reel9 import stamp_thud, zip_sweep

SEGMENTS = {
    "intro": (1.76, 4.02),     # ستيكر واحد… ثلاث حكايات
    "biz_a": (4.61, 5.46),     # أصحاب المشاريع
    "biz_b": (5.87, 8.41),     # تغليف يلفت النظر من أول نظرة
    "teach_a": (9.03, 10.32),  # المعلمين والمعلمات
    "teach_b": (10.62, 12.74), # مكافأة صغيرة تفرق مع الطالب
    "jour_a": (13.38, 15.51),  # ومحبين الجورنال
    "jour_b": (15.75, 18.62),  # صفحة عادية، صارت ذكرى
    "end": (18.92, 22.99),     # لكل واحد حكايته… ملف PDF، وتطبع كل ما احتجت
    "store_a": (23.38, 23.87), # والمتجر؟
    "store_b": (24.30, 25.31), # الكود قدامك
}

enter = mix((0, whoosh(0.5)), (0.45, 0.7 * thump(0.2)))
sweep = mix((0, zip_sweep(1.0)), *[(0.15 + k * 0.17, 0.5 * tick(0.03)) for k in range(5)])
cards = mix(*[(k * 0.15, 0.6 * whoosh(0.3)) for k in range(3)], *[(0.4 + k * 0.15, pop(600 + k * 120, 0.12)) for k in range(3)])

PLAN = [
    ("fx:introfx", norm(pop(500, 0.16), -9)), ("vo", "intro"),
    ("fx:enter0", norm(enter, -11)), ("vo", "biz_a"), ("fx:sweep0", norm(sweep, -13)), ("vo", "biz_b"),
    ("fx:enter1", norm(enter, -11)), ("vo", "teach_a"), ("fx:sweep1", norm(sweep, -13)), ("fx:stamp", norm(stamp_thud(), -6)), ("vo", "teach_b"),
    ("fx:enter2", norm(enter, -11)), ("vo", "jour_a"), ("fx:sweep2", norm(sweep, -13)), ("vo", "jour_b"),
    ("fx:cards", norm(cards, -11)), ("vo", "end"),
    ("fx:qr", norm(pop(450, 0.2), -9)), ("vo", "store_a"), ("vo", "store_b"),
    ("fx:chime", norm(chime(1.0), -11)),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path)
    GAP = 0.06
    out = [np.zeros(int(0.15 * SR))]; t = 0.15; tl = {}
    for kind, item in PLAN:
        x = voice[int(SEGMENTS[item][0] * SR):int(SEGMENTS[item][1] * SR)] if kind == "vo" else item
        label = item if kind == "vo" else kind[3:]
        tl[label] = round(t, 3); tl[label + "_end"] = round(t + len(x) / SR, 3)
        print(f"{kind[:2]}\t{label}\t{t:.2f}\t{t + len(x) / SR:.2f}")
        out += [x, np.zeros(int(GAP * SR))]
        t += len(x) / SR + GAP
    tl["end_all"] = round(t + 0.6, 3)
    y = np.clip(np.concatenate(out + [np.zeros(int(0.6 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    with open(tl_path, "w") as f:
        f.write("window.TL = " + json.dumps(tl) + ";\n")
    print(f"total\t\t0\t{tl['end_all']:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
