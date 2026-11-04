"""Builds the reel 13 soundtrack with the voiceover: board effects only in the gaps.

usage: python3 mix_reel13.py <voice_44k_mono.wav> <out.wav> <timeline.js>
"""
import json
import sys
import wave

import numpy as np

from mix_reel3 import SR, chime, mix, norm, read_wav, whoosh
from sfx_reel5 import pop, thump
from sfx_reel13 import crash, drumroll, flap_click, paper, pin, string

SEGMENTS = {
    "hook": (0.67, 3.37),    # ثلاث أشياء… محد يقولها لك عن الستيكرات
    "three": (3.93, 6.47),   # ثلاثة: تطبعها كل ما خلصت
    "two": (7.19, 12.60),    # اثنين: لكل ستايل مجموعة… ورود، طوابع، تراث، وخريف
    "one": (13.14, 15.77),   # وواحد… بدون شحن، تحميل فوري
    "uses": (16.28, 18.92),  # وتنفع للتغليف، والمدرسة، والجورنال
    "store": (19.47, 21.30), # والمتجر؟ الكود قدامك
}

STOPS = [0.35 + i * 0.22 for i in range(7)]
flaps = mix(*[(k / 36, 0.5 * flap_click()) for k in range(int(STOPS[-1] * 36))], *[(s, flap_click(0.03) + 0.5 * thump(0.03)[:int(0.03 * SR)]) for s in STOPS])
board = mix((0, whoosh(0.5)), (0.1, 0.8 * paper()), (0.3, pin()))
pan = mix((0, whoosh(1.0)), (0.05, 0.8 * string(0.9)), (0.95, pin()), (0.9, 0.7 * paper()))
pan1 = mix((0, whoosh(1.0)), (0.05, 0.8 * string(0.9)), (1.0, drumroll()), (1.75, crash()), (1.75, pin()))
zoom = mix((0, whoosh(0.9)), (0.05, 0.7 * string(0.8)), (0.55, pin()), *[(0.15 + i * 0.2, 0.6 * paper(0.15)) for i in range(3)], *[(0.25 + i * 0.2, 0.6 * pop(600 + i * 120, 0.1)) for i in range(3)])
pull = mix((0, whoosh(0.7)), (0.55, paper(0.25)))
drop = mix((0, 0.5 * whoosh(0.3)), (0.42, 0.7 * pin(0.1)), (0.6, chime(1.0)))

PLAN = [
    ("fx:flaps", norm(flaps, -12)), ("vo", "hook"), ("fx:arrow", norm(pop(700, 0.14), -13)),
    ("fx:board", norm(board, -10)), ("vo", "three"),
    ("fx:pan2", norm(pan, -11)), ("vo", "two"),
    ("fx:pan1", norm(pan1, -10)), ("vo", "one"),
    ("fx:zoom", norm(zoom, -11)), ("vo", "uses"),
    ("fx:pull", norm(pull, -10)), ("vo", "store"),
    ("fx:drop", norm(drop, -11)),
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
