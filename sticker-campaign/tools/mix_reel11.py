"""Builds the reel 11 soundtrack with the voiceover: news sound effects only in the
gaps between voice lines (never over speech).

usage: python3 mix_reel11.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, read_wav, rng, whoosh
from sfx_reel5 import thump
from sfx_reel8 import tick
from sfx_reel11 import beep, ding, static, sting, whirl

SEGMENTS = {
    "breaking": (1.29, 2.16),  # خبر عاجل
    "headline": (2.65, 5.89),  # الطابعة اللي في بيتك… صارت مصنع ستيكرات
    "biz_a": (6.31, 7.44),     # أصحاب المشاريع
    "biz_b": (7.83, 9.23),     # تغليف الطلبات صار أحلى
    "teach_a": (9.78, 10.42),  # المعلمين
    "teach_b": (10.78, 12.43), # مكافآت ملونة للطلاب
    "jour": (12.84, 16.00),    # ومحبين الجورنال: صفحات مليانة حياة
    "numbers": (16.64, 17.13), # بالأرقام
    "facts": (17.57, 21.49),   # إحدعش مجموعة، أكثر من سبعمية وثمانين تصميم
    "store": (22.08, 24.27),   # وللتفاصيل… المتجر، الكود قدامك
}

alarm = mix(*[(k * 0.24, beep(1500 if k % 2 == 0 else 1200, 0.12)) for k in range(4)])
slap = thump(0.25) + 0.5 * lowpass(rng.standard_normal(int(0.25 * SR)), 2000) * np.exp(-np.arange(int(0.25 * SR)) / 1500)
paper = mix((0, whirl(1.0)), (1.0, slap))
cut = mix((0, static(0.28)), (0.2, 0.6 * whoosh(0.35)))
ODO = 1.4
odo = mix(*[(k * 0.2, 0.6 * whoosh(0.3)) for k in range(3)],
          *[(ODO * (1 - (1 - k / 50) ** 0.6), 0.5 * tick(0.02)) for k in range(50)],
          *[(0.95 + k * 0.2, 0.6 * thump(0.15)) for k in range(3)])

PLAN = [
    ("fx:intro", norm(sting(), -7)), ("fx:alarm", norm(alarm, -14)), ("vo", "breaking"),
    ("fx:paper", norm(paper, -9)), ("vo", "headline"),
    ("fx:cut0", norm(cut, -13)), ("vo", "biz_a"), ("fx:ding0", norm(ding(), -15)), ("vo", "biz_b"),
    ("fx:cut1", norm(cut, -13)), ("vo", "teach_a"), ("fx:ding1", norm(ding(), -15)), ("vo", "teach_b"),
    ("fx:cut2", norm(cut, -13)), ("vo", "jour"),
    ("fx:cut3", norm(cut, -13)), ("vo", "numbers"), ("fx:odo", norm(odo, -12)), ("vo", "facts"),
    ("fx:cut4", norm(mix((0, static(0.28)), (0.2, sting())), -8)), ("vo", "store"),
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
