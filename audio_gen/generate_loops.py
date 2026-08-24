"""
AR Sound Garden - 5 part EDM loop auto-generator
128 BPM, 8 bars (15.0 sec exact), 44.1kHz / 16-bit WAV
deps: numpy only
"""
from __future__ import annotations
import io
import math
import sys
import wave
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BPM = 128.0
SR = 44100
BARS = 8
BEATS_PER_BAR = 4
SEC_PER_BEAT = 60.0 / BPM
LOOP_SEC = BARS * BEATS_PER_BAR * SEC_PER_BEAT
N_SAMPLES = int(round(LOOP_SEC * SR))

OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "audio"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def midi_to_hz(n: float) -> float:
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


def envelope(length: int, attack: float = 0.005, decay: float = 0.1, sustain: float = 0.6, release: float = 0.05) -> np.ndarray:
    a = int(attack * SR)
    d = int(decay * SR)
    r = int(release * SR)
    s = max(0, length - a - d - r)
    env = np.concatenate([
        np.linspace(0.0, 1.0, a, endpoint=False) if a > 0 else np.array([]),
        np.linspace(1.0, sustain, d, endpoint=False) if d > 0 else np.array([]),
        np.full(s, sustain),
        np.linspace(sustain, 0.0, r, endpoint=True) if r > 0 else np.array([]),
    ])
    if env.shape[0] < length:
        env = np.pad(env, (0, length - env.shape[0]))
    return env[:length]


def add_at(buf: np.ndarray, sample: np.ndarray, start: int, gain: float = 1.0) -> None:
    end = min(start + sample.shape[0], buf.shape[0])
    if end > start:
        buf[start:end] += gain * sample[: end - start]


def synth_sine(freq: float, dur_sec: float, env_kwargs: dict | None = None) -> np.ndarray:
    n = int(dur_sec * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * math.pi * freq * t)
    env = envelope(n, **(env_kwargs or {}))
    return sig * env


def synth_saw(freq: float, dur_sec: float, env_kwargs: dict | None = None, detune_cents: float = 0.0) -> np.ndarray:
    n = int(dur_sec * SR)
    t = np.arange(n) / SR
    f = freq * (2.0 ** (detune_cents / 1200.0))
    phase = (t * f) % 1.0
    sig = 2.0 * phase - 1.0
    env = envelope(n, **(env_kwargs or {}))
    return sig * env


def synth_square(freq: float, dur_sec: float, env_kwargs: dict | None = None) -> np.ndarray:
    n = int(dur_sec * SR)
    t = np.arange(n) / SR
    sig = np.sign(np.sin(2 * math.pi * freq * t))
    env = envelope(n, **(env_kwargs or {}))
    return sig * env


def synth_kick(dur_sec: float = 0.25) -> np.ndarray:
    n = int(dur_sec * SR)
    t = np.arange(n) / SR
    f0, f1 = 110.0, 45.0
    freq = f1 + (f0 - f1) * np.exp(-t * 25)
    phase = 2 * math.pi * np.cumsum(freq) / SR
    sig = np.sin(phase)
    env = np.exp(-t * 8)
    click = np.exp(-t * 200) * (np.random.rand(n) - 0.5) * 0.3
    return sig * env + click * env


def synth_snare(dur_sec: float = 0.18) -> np.ndarray:
    n = int(dur_sec * SR)
    t = np.arange(n) / SR
    noise = np.random.rand(n) * 2 - 1
    tone = np.sin(2 * math.pi * 190 * t) * 0.5
    env = np.exp(-t * 18)
    return (noise * 0.8 + tone) * env


def synth_hat(dur_sec: float = 0.05, open_: bool = False) -> np.ndarray:
    n = int(dur_sec * SR)
    t = np.arange(n) / SR
    noise = np.random.rand(n) * 2 - 1
    fft = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    fft[freqs < 6000] *= 0.05
    hp = np.fft.irfft(fft, n)
    decay = 12 if not open_ else 4
    env = np.exp(-t * decay)
    return hp * env


def write_wav(path: Path, samples: np.ndarray) -> None:
    peak = np.max(np.abs(samples))
    if peak > 0:
        samples = samples / peak * 0.95
    pcm = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"  wrote {path.name}  ({samples.shape[0]/SR:.3f}s, peak={peak:.3f})")


def beat_to_sample(beat: float) -> int:
    return int(round(beat * SEC_PER_BEAT * SR))


CHORDS = [
    ("Am", [57, 60, 64]),
    ("Am", [57, 60, 64]),
    ("F",  [53, 57, 60]),
    ("F",  [53, 57, 60]),
    ("C",  [48, 52, 55]),
    ("C",  [48, 52, 55]),
    ("G",  [55, 59, 62]),
    ("G",  [55, 59, 62]),
]


def make_drums() -> np.ndarray:
    buf = np.zeros(N_SAMPLES, dtype=np.float32)
    np.random.seed(42)
    for bar in range(BARS):
        for beat in range(BEATS_PER_BAR):
            t = bar * BEATS_PER_BAR + beat
            add_at(buf, synth_kick(0.28), beat_to_sample(t), gain=1.0)
            if beat in (1, 3):
                add_at(buf, synth_snare(0.18), beat_to_sample(t), gain=0.85)
            for sub in range(2):
                t8 = t + sub * 0.5
                add_at(buf, synth_hat(0.04, open_=(sub == 1 and beat in (0, 2))), beat_to_sample(t8), gain=0.35)
    return buf


def make_bass() -> np.ndarray:
    buf = np.zeros(N_SAMPLES, dtype=np.float32)
    np.random.seed(7)
    for bar in range(BARS):
        root = CHORDS[bar][1][0] - 24
        pattern_beats = [0.0, 0.75, 1.5, 2.0, 2.75, 3.5]
        for pb in pattern_beats:
            t = bar * BEATS_PER_BAR + pb
            note = synth_saw(midi_to_hz(root), 0.20, env_kwargs={"attack": 0.005, "decay": 0.08, "sustain": 0.6, "release": 0.05}, detune_cents=0)
            sub = synth_sine(midi_to_hz(root - 12), 0.20, env_kwargs={"attack": 0.005, "decay": 0.08, "sustain": 0.7, "release": 0.05})
            add_at(buf, note, beat_to_sample(t), gain=0.6)
            add_at(buf, sub, beat_to_sample(t), gain=0.7)
    return buf


def make_pad() -> np.ndarray:
    buf = np.zeros(N_SAMPLES, dtype=np.float32)
    bar_sec = BEATS_PER_BAR * SEC_PER_BEAT
    for bar in range(BARS):
        chord = CHORDS[bar][1]
        t = bar * BEATS_PER_BAR
        for note in chord:
            for detune in (-8.0, 0.0, 8.0):
                s = synth_saw(midi_to_hz(note + 12), bar_sec * 1.05, env_kwargs={"attack": 0.25, "decay": 0.1, "sustain": 0.85, "release": 0.3}, detune_cents=detune)
                add_at(buf, s, beat_to_sample(t), gain=0.18)
    buf = lowpass_simple(buf, cutoff=2500)
    return buf


def lowpass_simple(x: np.ndarray, cutoff: float = 3000.0) -> np.ndarray:
    rc = 1.0 / (2 * math.pi * cutoff)
    dt = 1.0 / SR
    a = dt / (rc + dt)
    y = np.zeros_like(x)
    y[0] = x[0] * a
    for i in range(1, len(x)):
        y[i] = a * x[i] + (1 - a) * y[i - 1]
    return y


def make_melody() -> np.ndarray:
    buf = np.zeros(N_SAMPLES, dtype=np.float32)
    A_MINOR_PENTA = [57, 60, 62, 64, 67]
    np.random.seed(123)
    phrase_per_bar = [
        [(0.0, 64, 0.5), (0.5, 67, 0.5), (1.0, 69, 1.0), (2.0, 67, 0.5), (2.5, 64, 0.5), (3.0, 60, 1.0)],
        [(0.0, 60, 0.5), (0.5, 64, 0.5), (1.0, 67, 1.5), (2.5, 64, 0.5), (3.0, 62, 1.0)],
        [(0.0, 65, 0.5), (0.5, 69, 0.5), (1.0, 72, 1.0), (2.0, 69, 0.5), (2.5, 65, 0.5), (3.0, 64, 1.0)],
        [(0.0, 64, 0.5), (0.5, 60, 0.5), (1.0, 57, 1.5), (2.5, 60, 0.5), (3.0, 64, 1.0)],
        [(0.0, 67, 0.5), (0.5, 72, 0.5), (1.0, 76, 1.0), (2.0, 72, 0.5), (2.5, 67, 0.5), (3.0, 64, 1.0)],
        [(0.0, 67, 0.5), (0.5, 64, 0.5), (1.0, 60, 1.5), (2.5, 64, 0.5), (3.0, 67, 1.0)],
        [(0.0, 71, 0.5), (0.5, 74, 0.5), (1.0, 79, 1.0), (2.0, 74, 0.5), (2.5, 71, 0.5), (3.0, 67, 1.0)],
        [(0.0, 67, 0.5), (0.5, 62, 0.5), (1.0, 59, 0.5), (1.5, 55, 1.0), (2.5, 57, 0.5), (3.0, 57, 1.0)],
    ]
    for bar in range(BARS):
        for (offset, note, dur) in phrase_per_bar[bar]:
            t = bar * BEATS_PER_BAR + offset
            d = dur * SEC_PER_BEAT
            sq = synth_square(midi_to_hz(note), d * 0.95, env_kwargs={"attack": 0.005, "decay": 0.08, "sustain": 0.7, "release": 0.04})
            saw = synth_saw(midi_to_hz(note), d * 0.95, env_kwargs={"attack": 0.005, "decay": 0.08, "sustain": 0.7, "release": 0.04}, detune_cents=5)
            add_at(buf, sq, beat_to_sample(t), gain=0.45)
            add_at(buf, saw, beat_to_sample(t), gain=0.35)
    return buf


def make_arp() -> np.ndarray:
    buf = np.zeros(N_SAMPLES, dtype=np.float32)
    sixteenth = 0.25
    note_dur = sixteenth * SEC_PER_BEAT * 0.9
    for bar in range(BARS):
        chord = CHORDS[bar][1]
        arp_notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 24, chord[0] + 24, chord[1] + 12, chord[2] + 12, chord[1] + 12] * 2
        for i in range(BEATS_PER_BAR * 4):
            t = bar * BEATS_PER_BAR + i * sixteenth
            note = arp_notes[i % len(arp_notes)]
            tone = synth_saw(midi_to_hz(note), note_dur, env_kwargs={"attack": 0.002, "decay": 0.05, "sustain": 0.3, "release": 0.02})
            add_at(buf, tone, beat_to_sample(t), gain=0.5)
    return lowpass_simple(buf, cutoff=4500)


def main():
    print(f"AR Sound Garden - audio loop generation")
    print(f"  BPM={BPM}  bars={BARS}  loop={LOOP_SEC:.3f}s  samples={N_SAMPLES}  sr={SR}")
    print(f"  output: {OUT_DIR}")
    print()
    tracks = [
        ("drum_loop.wav",    make_drums),
        ("bass_loop.wav",    make_bass),
        ("melody_loop.wav",  make_melody),
        ("pad_loop.wav",     make_pad),
        ("arp_loop.wav",     make_arp),
    ]
    for name, fn in tracks:
        print(f"generating {name}...")
        sig = fn()
        write_wav(OUT_DIR / name, sig)
    print("\nall done.")


if __name__ == "__main__":
    main()
