"""Builds the reel 15 soundtrack with the voiceover: effects only in the gaps.

usage: python3 mix_reel15.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, whoosh
from sfx_reel5 import pop, thump
from sfx_reel8 import tick
from sfx_reel10 import boom
from sfx_reel14 import alarm, hiss, pour, powerup, scratch, tada, trombone
from sfx_reel15 import rimshot, slide_down

SEGMENTS = {
    "hook": (0.26, 2.49),    # مين أكثر واحد يحتاج ستيكرات قهوة؟
    "a1": (3.39, 5.36),      # اللي يغلّف خمسين طلب قبل الظهر
    "a2": (5.73, 7.24),      # ستيكر قهوة على كل طلب
    "b1": (8.13, 9.99),      # اللي يدخل الفصل الساعة سبعة الصبح
    "b2": (10.41, 12.20),    # وستيكر على دفتر كل طالب
    "c1": (13.13, 14.53),    # واللي يكتب يومه في دفتر
    "c2": (14.75, 16.80),    # وصفحته صارت مليانة ستيكرات
    "ans": (17.29, 17.71),   # الجواب؟
    "all": (18.27, 18.70),   # كلنا
    "says": (18.87, 20.74),  # ستيكرات تقول اللي في خاطرنا
    "count": (21.67, 23.94), # مية وأربعطعش ستيكر قهوة وميمز
    "pdf": (24.38, 25.95),   # ملف PDF تطبعه في بيتك
    "store": (26.17, 27.77), # والمتجر؟ الكود قدامك
}

enter = mix((0, whoosh(0.45)), (0.45, thump(0.25)))
short_tada = lambda: tada()[:int(0.5 * SR)] * np.linspace(1, 0, int(0.5 * SR)) ** 0.5
yay = lambda n: mix((0, short_tada()), *[(0.05 + i * 0.12, 0.7 * pop(650 + i * 110, 0.12)) for i in range(n)])
memes = mix(*[x for i in range(4) for x in ((i * 0.42, 0.6 * whoosh(0.2)), (i * 0.42 + 0.14, 0.8 * thump(0.15)))])
count = mix(*[(1.0 * (1 - (1 - k / 30) ** 0.5), 0.5 * tick(0.02)) for k in range(30)], (1.0, pop(1000, 0.12)))
chips = mix(*[(i * 0.15, pop(600 + i * 100, 0.1)) for i in range(4)])
cup = mix((0, whoosh(0.5)), (0.5, thump(0.25)), (0.5, 0.5 * hiss(0.5)))

PLAN = [
    ("fx:alarm", norm(alarm(0.8), -16)), ("fx:slam", norm(mix((0, scratch()), (0.07, boom(0.7))), -8)), ("vo", "hook"),
    ("fx:h3", norm(pop(650, 0.14), -13)),
    ("fx:enter0", norm(enter, -11)), ("vo", "a1"), ("fx:sad0", norm(slide_down(0.6), -14)), ("fx:pour0", norm(pour(0.8), -10)), ("fx:yay0", norm(yay(4), -10)), ("vo", "a2"),
    ("fx:enter1", norm(enter, -11)), ("vo", "b1"), ("fx:sad1", norm(slide_down(0.6), -14)), ("fx:pour1", norm(mix((0, pour(0.8)), (0.1, 0.6 * powerup(0.5))), -10)), ("fx:yay1", norm(yay(2), -10)), ("vo", "b2"),
    ("fx:enter2", norm(enter, -11)), ("vo", "c1"), ("fx:sad2", norm(slide_down(0.6), -14)), ("fx:pour2", norm(pour(0.8), -10)), ("fx:yay2", norm(yay(3), -10)), ("vo", "c2"),
    ("fx:ansfx", norm(whoosh(0.4), -13)), ("vo", "ans"), ("vo", "all"), ("fx:rim", norm(rimshot(), -8)),
    ("fx:memes", norm(memes, -12)), ("vo", "says"),
    ("fx:countfx", norm(count, -13)), ("vo", "count"), ("fx:chips", norm(chips, -14)), ("vo", "pdf"),
    ("fx:cup", norm(cup, -11)), ("vo", "store"), ("fx:chime", norm(chime(1.0), -12)),
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
    tl["end_all"] = round(t + 0.5, 3)
    y = np.clip(np.concatenate(out + [np.zeros(int(0.5 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    with open(tl_path, "w") as f:
        f.write("window.TL = " + json.dumps(tl) + ";\n")
    print(f"total\t\t0\t{tl['end_all']:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
