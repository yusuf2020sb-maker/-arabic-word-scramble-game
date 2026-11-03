"""Builds the reel 5 soundtrack with the voiceover: voice clips in order, and the
stop-motion sound effects only in the gaps between them (never over speech).

usage: python3 mix_reel5.py <voice_44k_mono.wav> <out.wav> <timeline.js>
Writes timeline.js (window.TL = {label: start_second}) for reel5.html to sync to.
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, whoosh
from sfx_reel5 import boing, pop, printer, rattle, rip, scribble, thump

# Voice segments (seconds in the source), cut only at detected pauses.
SEGMENTS = {
    "hook": (1.11, 2.45),      # ستيكرات ما تخلص؟
    "yes": (2.63, 3.08),       # إيه!
    "print": (3.39, 6.00),     # طبعة… وطبعة… وكل ما تبي طبعة
    "where": (6.32, 7.53),     # وين تلصقها؟
    "cup": (7.93, 8.60),       # على الكوب
    "book": (8.84, 9.53),      # على الدفتر
    "gift": (9.87, 10.66),     # على الهدية
    "orders": (10.81, 12.09),  # وعلى الطلبات
    "style": (12.62, 13.70),   # ستايلك موجود
    "kinds": (14.13, 17.93),   # طوابع، ورود، خريف، تراث، وجورنال
    "store": (18.41, 18.95),   # والمتجر؟
    "under": (19.35, 20.14),   # تحت الملصق
    "peel": (20.39, 21.17),    # شيله وشوف
}

grid = mix(*[(i * 0.08, pop(500 + i * 45, 0.08)) for i in range(12)])
beat = lambda i: mix((0, whoosh(0.2)), (0.12, pop(650 + i * 90, 0.12)))

PLAN = [
    ("fx:title", norm(pop(450, 0.16), -9)), ("vo", "hook"),
    ("fx:boing", norm(boing(0.4), -8)), ("vo", "yes"),
    ("fx:underline", norm(scribble(0.45), -14)),
    ("fx:wipe1", norm(whoosh(0.6), -11)),
    ("fx:printer", norm(printer(0.6), -12)), ("vo", "print"),
    ("fx:wipe2", norm(whoosh(0.6), -11)), ("vo", "where"),
    ("fx:beat0", norm(beat(0), -9)), ("vo", "cup"),
    ("fx:beat1", norm(beat(1), -9)), ("vo", "book"),
    ("fx:beat2", norm(beat(2), -9)), ("vo", "gift"),
    ("fx:beat3", norm(beat(3), -9)), ("vo", "orders"),
    ("fx:wipe3", norm(whoosh(0.6), -11)),
    ("fx:grid", norm(grid, -12)), ("vo", "style"),
    ("fx:chips", norm(thump(0.25), -8)), ("vo", "kinds"),
    ("fx:wipe4", norm(whoosh(0.6), -11)), ("vo", "store"),
    ("fx:rattle", norm(rattle(0.35), -18)), ("vo", "under"),
    ("fx:rattle2", norm(rattle(0.3), -18)), ("vo", "peel"),
    ("fx:rip", norm(rip(0.8), -10)),
    ("fx:circle", norm(scribble(0.55), -14)),
    ("fx:chime", norm(chime(0.9), -11)),
]


def main(voice_path, out_path, tl_path):
    voice = read_wav(voice_path)
    GAP = 0.06
    out = [np.zeros(int(0.15 * SR))]; t = 0.15; tl = {}
    for kind, item in PLAN:
        x = voice[int(SEGMENTS[item][0] * SR):int(SEGMENTS[item][1] * SR)] if kind == "vo" else item
        label = item if kind == "vo" else kind[3:]
        tl[label] = round(t, 3)
        print(f"{kind[:2]}\t{label}\t{t:.2f}\t{t + len(x) / SR:.2f}")
        out += [x, np.zeros(int(GAP * SR))]
        t += len(x) / SR + GAP
    tl["end"] = round(t + 0.6, 3)
    y = np.clip(np.concatenate(out + [np.zeros(int(0.6 * SR))]), -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    with open(tl_path, "w") as f:
        f.write("window.TL = " + json.dumps(tl) + ";\n")
    print(f"total\t\t0\t{tl['end']:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
