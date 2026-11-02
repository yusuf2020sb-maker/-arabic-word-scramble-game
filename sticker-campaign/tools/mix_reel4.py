"""Builds the reel 4 soundtrack: voice clips with sound effects only in the gaps.

usage: python3 mix_reel4.py <voice_44k_mono.wav> <out.wav>
Prints the timeline so reel4.html can be synced to it.
"""
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, lowpass, mix, norm, pop, read_wav, rng, sparkle, whoosh

# Voice segments (seconds in the source), cut only at detected pauses.
SEGMENTS = {
    "hook": (0.58, 4.05),      # ستيكرات فنتج… لكل واحد استخدام
    "biz_a": (4.76, 5.85),     # أصحاب المشاريع
    "biz_b": (6.47, 8.67),     # تغليف يخلي طلبك ينحفظ
    "teach_a": (9.38, 11.04),  # المعلمين والمعلمات
    "teach_b": (11.65, 14.16), # تحفيز للطلاب وتزيين للدفاتر
    "jour_a": (14.74, 15.87),  # ومحبين الجورنال
    "jour_b": (16.38, 18.27),  # صفحات ما تكون فاضية
    "sets": (18.95, 23.33),    # إحدعش مجموعة، ملف PDF، تطبع كل ما احتجت
    "store": (23.85, 27.24),   # والمتجر؟ الكود يوصلك على طول
}


def flip(d=0.3):
    # quick card swish with a soft tick at the end
    n = int(d * SR); t = np.linspace(0, 1, n)
    y = lowpass(rng.standard_normal(n), 1500 + 6000 * t) * np.sin(np.pi * t) ** 2
    tick = np.zeros(n); k = int(0.8 * n)
    tick[k:k + 400] = np.sin(2 * np.pi * 1800 * np.arange(400) / SR) * np.exp(-np.arange(400) / 60)
    return y + 0.5 * tick


def rise(d=0.6):
    # upward swell for the sticker wall reveal
    n = int(d * SR); t = np.linspace(0, 1, n)
    y = lowpass(rng.standard_normal(n), 300 + 7000 * t ** 2) * t ** 1.5 * np.exp(-((t - 0.85) ** 2) * 8)
    return y


def main(voice_path, out_path):
    voice = read_wav(voice_path)
    clip = {k: voice[int(a * SR):int(b * SR)] for k, (a, b) in SEGMENTS.items()}
    plan = [
        ("fx", norm(sparkle(0.5), -11)),
        ("vo", "hook"),
        ("fx", norm(whoosh(0.42), -10)), ("vo", "biz_a"), ("fx", norm(flip(), -12)), ("vo", "biz_b"),
        ("fx", norm(whoosh(0.42), -10)), ("vo", "teach_a"), ("fx", norm(flip(), -12)), ("vo", "teach_b"),
        ("fx", norm(whoosh(0.42), -10)), ("vo", "jour_a"), ("fx", norm(flip(), -12)), ("vo", "jour_b"),
        ("fx", norm(rise(0.6), -9)),
        ("vo", "sets"),
        ("fx", norm(mix((0, pop(0.16)), (0.08, 0.6 * sparkle(0.4))), -9)),
        ("vo", "store"),
        ("fx", norm(chime(0.8), -11)),
    ]
    GAP = 0.06
    out = [np.zeros(int(0.1 * SR))]; t = 0.1
    for kind, item in plan:
        x = clip[item] if kind == "vo" else item
        label = item if kind == "vo" else ""
        print(f"{kind}\t{label}\t{t:.2f}\t{t + len(x) / SR:.2f}")
        out += [x, np.zeros(int(GAP * SR))]
        t += len(x) / SR + GAP
    y = np.clip(np.concatenate(out + [np.zeros(int(0.5 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(f"total\t\t0\t{len(y) / SR:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
