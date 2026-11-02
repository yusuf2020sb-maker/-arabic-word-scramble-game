"""Builds the reel 3 soundtrack: voice clips placed on a timeline with synthesized
sound effects in the gaps between them, so effects never overlap speech.

usage: python3 mix_reel3.py <voice_44k_mono.wav> <out.wav>
Prints the timeline (start/end of every clip) so the video can be synced to it.
"""
import sys
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(7)

# Voice segments (seconds in the source recording), cut only at detected pauses.
SEGMENTS = [
    ("hook", 0.27, 1.60),      # مين يحتاج ستيكرات؟
    ("all", 1.89, 2.46),       # الكل!
    ("biz", 2.71, 5.55),       # أصحاب المشاريع… تغليف يلفت النظر
    ("teach", 5.75, 9.03),     # المعلمين والمعلمات… تحفيز وتزيين للدفاتر
    ("journal", 9.24, 12.66),  # ومحبين الجورنال… صفحات ما تكون فاضية
    ("sets", 12.90, 19.49),    # إحدعش مجموعة فنتج… وتطبع كل ما احتجت
    ("store", 19.84, 21.73),   # والمتجر؟ الكود يوصلك له على طول
]


def env(n, attack, release):
    a = int(attack * SR); r = int(release * SR)
    e = np.ones(n)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.exp(-np.linspace(0, 6, r))
    return e


def lowpass(x, cutoff):
    # one-pole lowpass; cutoff may vary per sample
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); prev = 0.0
    for i in range(len(x)):
        prev = (1 - a[i]) * x[i] + a[i] * prev
        y[i] = prev
    return y


def whoosh(d=0.5):
    n = int(d * SR); t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    sweep = 400 + 5200 * np.sin(np.pi * t) ** 2
    y = lowpass(noise, sweep) - lowpass(noise, sweep * 0.25)
    return y * np.sin(np.pi * t) ** 1.5


def pop(d=0.16):
    n = int(d * SR); t = np.arange(n) / SR
    f = 700 * np.exp(-t * 28) + 160
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    y[:60] += rng.standard_normal(60) * 0.6
    return y


def sparkle(d=0.45):
    n = int(d * SR); y = np.zeros(n)
    for k, f in enumerate([2637, 3136, 3951, 4699, 3520]):
        s = int(k * 0.06 * SR); m = n - s; t = np.arange(m) / SR
        y[s:] += np.sin(2 * np.pi * f * t) * np.exp(-t * 14) * 0.5
    return y


def stamp(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 25)) * t) * np.exp(-t * 14)
    click = lowpass(rng.standard_normal(n), 2500) * np.exp(-t * 60) * 2
    return thud + click


def chime(d=0.6):
    n = int(d * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dec) * a
            for f, dec, a in [(880, 5, 1), (1320, 7, .6), (1760, 9, .4), (2640, 12, .25)])
    return y * env(n, 0.005, 0.2)


def mix(*parts):
    """Sum (offset_seconds, signal) parts into one buffer."""
    n = max(int(o * SR) + len(x) for o, x in parts)
    y = np.zeros(n)
    for o, x in parts:
        y[int(o * SR):int(o * SR) + len(x)] += x
    return y


def norm(x, peak_db):
    return x / (np.abs(x).max() + 1e-9) * 10 ** (peak_db / 20)


def read_wav(path):
    with wave.open(path) as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768


def main(voice_path, out_path):
    voice = read_wav(voice_path)
    clip = {name: voice[int(a * SR):int(b * SR)] for name, a, b in SEGMENTS}

    # (kind, payload) in order; effects only ever sit between voice clips
    GAP = 0.05
    plan = [
        ("fx", norm(mix((0, sparkle(0.45)), (0, 0.6 * pop())), -9)),
        ("vo", "hook"),
        ("fx", norm(pop(0.2), -7)),
        ("vo", "all"),
        ("fx", norm(mix((0, whoosh(0.42)), (0.3, 0.5 * pop(0.12))), -10)),
        ("vo", "biz"),
        ("fx", norm(whoosh(0.5), -10)),
        ("vo", "teach"),
        ("fx", norm(whoosh(0.5), -10)),
        ("vo", "journal"),
        ("fx", norm(mix((0, whoosh(0.35)), (0.05, 0.7 * sparkle(0.4))), -9)),
        ("vo", "sets"),
        ("fx", norm(stamp(0.38), -6)),
        ("vo", "store"),
        ("fx", norm(chime(0.7), -11)),
    ]

    out = []; t = 0.0
    for kind, item in plan:
        x = clip[item] if kind == "vo" else item
        print(f"{kind}\t{item if kind == 'vo' else ''}\t{t:.2f}\t{t + len(x) / SR:.2f}")
        out.append(x); out.append(np.zeros(int(GAP * SR)))
        t += len(x) / SR + GAP
    y = np.concatenate(out + [np.zeros(int(0.4 * SR))])
    y = np.clip(y, -1, 1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(f"total\t\t0\t{len(y) / SR:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
