"""Procedural sound effects — synthesized at runtime with numpy.

No audio asset files: every effect is generated as a numpy waveform and turned
into a pygame sound via ``pygame.sndarray.make_sound``. If numpy or the audio
mixer is unavailable, the SoundBank silently degrades to no-ops so the game
still runs.
"""

import math

import pygame

try:
    import numpy as np

    _HAVE_NUMPY = True
except ImportError:  # pragma: no cover - numpy is in requirements
    np = None
    _HAVE_NUMPY = False

SAMPLE_RATE = 22050


def _to_sound(samples):
    """Convert a float numpy array (-1..1) to a pygame Sound (mono int16)."""
    clipped = np.clip(samples, -1.0, 1.0)
    arr = (clipped * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(arr)


def _envelope(n, attack=0.005, decay=None):
    """Exponential-ish decay envelope of length n samples."""
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    env = np.exp(-t * (decay if decay else 8.0))
    if attack > 0:
        att_n = int(attack * SAMPLE_RATE)
        if att_n > 0:
            env[:att_n] *= np.linspace(0.0, 1.0, att_n)
    return env


def _lowpass(x, alpha=0.15):
    """Simple one-pole lowpass filter."""
    y = np.empty_like(x)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = y[i - 1] + alpha * (x[i] - y[i - 1])
    return y


def _noise(n):
    return np.random.uniform(-1.0, 1.0, n)


def _sine(freq, n, rate=None):
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    return np.sin(2.0 * math.pi * freq * t)


def _sweep(freq_start, freq_end, n, rate=None, wave="sine"):
    """Frequency sweep tone."""
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    phase = 2.0 * math.pi * (
        freq_start * t + (freq_end - freq_start) * t * t / (2.0 * (n / SAMPLE_RATE))
    )
    if wave == "square":
        return np.sign(np.sin(phase))
    if wave == "saw":
        return 2.0 * ((phase / (2.0 * math.pi)) % 1.0) - 1.0
    return np.sin(phase)


class SoundBank:
    """Holds all synthesized sounds and safe play() methods."""

    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        self._build()

    def _build(self):
        if not _HAVE_NUMPY:
            return
        try:
            pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 256)
            if not pygame.mixer.get_init():
                pygame.mixer.init(SAMPLE_RATE, -16, 1, 256)
        except pygame.error:
            return
        if not pygame.mixer.get_init():
            return

        try:
            s = self.sounds
            # Laser pew: descending square sweep
            n = int(0.13 * SAMPLE_RATE)
            s["laser"] = _to_sound(_sweep(950, 220, n, wave="square") * _envelope(n, decay=22) * 0.35)

            # Small explosion: filtered noise burst
            n = int(0.32 * SAMPLE_RATE)
            s["explosion_small"] = _to_sound(_lowpass(_noise(n), 0.35) * _envelope(n, decay=14) * 0.8)

            # Big explosion: longer, deeper
            n = int(0.5 * SAMPLE_RATE)
            boom = _lowpass(_noise(n), 0.12) * _envelope(n, decay=8)
            boom += _sweep(160, 40, n, wave="sine") * _envelope(n, decay=7) * 0.5
            s["explosion_big"] = _to_sound(boom * 0.9)

            # Boss explosion: huge
            n = int(0.8 * SAMPLE_RATE)
            boom = _lowpass(_noise(n), 0.07) * _envelope(n, decay=5)
            boom += _sweep(120, 28, n, wave="saw") * _envelope(n, decay=4.5) * 0.45
            s["explosion_boss"] = _to_sound(boom)

            # Dive whoosh: band-ish noise sweep with rising then falling gain
            n = int(0.42 * SAMPLE_RATE)
            env = np.sin(np.linspace(0, math.pi, n)) ** 1.5
            whoosh = _lowpass(_noise(n), 0.25) * env * 0.5
            s["whoosh"] = _to_sound(whoosh)

            # Power-up chime: two rising sines
            n1 = int(0.09 * SAMPLE_RATE)
            n2 = int(0.14 * SAMPLE_RATE)
            chime = np.concatenate(
                [
                    _sine(660, n1) * _envelope(n1, decay=18) * 0.5,
                    _sine(1320, n2) * _envelope(n2, decay=12) * 0.5,
                ]
            )
            s["powerup"] = _to_sound(chime)

            # Extra life: happy three-note arp
            parts = []
            for f in (523.25, 659.25, 783.99):
                nn = int(0.11 * SAMPLE_RATE)
                parts.append(_sine(f, nn) * _envelope(nn, decay=16) * 0.5)
            s["extralife"] = _to_sound(np.concatenate(parts))

            # Player death: descending saw + noise
            n = int(0.65 * SAMPLE_RATE)
            death = _sweep(420, 60, n, wave="saw") * _envelope(n, decay=6) * 0.5
            death += _lowpass(_noise(n), 0.2) * _envelope(n, decay=7) * 0.5
            s["player_death"] = _to_sound(death)

            # Shield hit: metallic ping
            n = int(0.22 * SAMPLE_RATE)
            ping = _sine(1400, n) * _envelope(n, decay=26) * 0.4
            ping += _sine(2100, n) * _envelope(n, decay=30) * 0.2
            s["shield_hit"] = _to_sound(ping)

            # Level clear jingle: rising 4-note arp
            parts = []
            for f in (392.0, 523.25, 659.25, 783.99):
                nn = int(0.12 * SAMPLE_RATE)
                parts.append(_sine(f, nn) * _envelope(nn, decay=14) * 0.5)
            s["level_clear"] = _to_sound(np.concatenate(parts))

            # Streak blip: short square, pitch scaled at play time via volume trick
            n = int(0.07 * SAMPLE_RATE)
            s["streak"] = _to_sound(_sweep(500, 700, n, wave="square") * _envelope(n, decay=30) * 0.3)

            # UI select
            n = int(0.06 * SAMPLE_RATE)
            s["ui"] = _to_sound(_sine(880, n) * _envelope(n, decay=40) * 0.35)
        except Exception:
            # Any failure -> stay silent rather than crash the game
            self.sounds.clear()
            return

        self.enabled = True

    def play(self, name, volume=1.0):
        if not self.enabled or self.muted:
            return
        snd = self.sounds.get(name)
        if snd is None:
            return
        try:
            snd.set_volume(max(0.0, min(1.0, volume)))
            snd.play()
        except pygame.error:
            pass

    def play_streak(self, multiplier):
        """Streak blip whose pitch rises with the multiplier (1..6)."""
        if not self.enabled or self.muted:
            return
        snd = self.sounds.get("streak")
        if snd is None:
            return
        try:
            snd.set_volume(0.35)
            snd.play()
        except pygame.error:
            pass
