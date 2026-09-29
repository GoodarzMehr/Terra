# Terra
# Copyright (C) 2026  Goodarz Mehr

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''Sound synthesis and playback for Terra.'''

import math
import pygame
import numpy as np


SAMPLE_RATE = 48000


def _to_sound(samples: np.ndarray) -> pygame.mixer.Sound:
    '''
    Convert a float numpy array to a pygame Sound (mono int16).
    
    Args:
        samples: array of samples in [-1, 1].
    
    Returns:
        pygame Sound object.
    '''
    clipped = np.clip(samples, -1.0, 1.0)
    
    arr = (clipped * 32767).astype(np.int16)
    
    stereo = np.column_stack([arr, arr])

    return pygame.sndarray.make_sound(stereo)


def _envelope(n: int, attack: float = 0.005, decay: float = None) -> np.ndarray:
    '''
    Exponential-ish decay envelope of n samples.
    
    Args:
        n: number of samples.
        attack: attack time in seconds.
        decay: decay time in seconds.

    Returns:
        env: decay envelope array of n samples.
    '''
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    
    env = np.exp(-t * (decay if decay else 8.0))

    if attack > 0:
        att_n = int(attack * SAMPLE_RATE)

        if att_n > 0:
            env[:att_n] *= np.linspace(0.0, 1.0, att_n)

    return env


def _lowpass(x: np.ndarray, alpha: float = 0.15) -> np.ndarray:
    '''
    Simple one-pole lowpass filter.

    Args:
        x: input samples.
        alpha: smoothing factor in [0, 1].
    
    Returns:
        y: filtered samples.
    '''
    y = np.empty_like(x)
    
    y[0] = x[0]

    for i in range(1, len(x)):
        y[i] = y[i - 1] + alpha * (x[i] - y[i - 1])

    return y


def _noise(n: int) -> np.ndarray:
    '''
    Generate white noise samples.

    Args:
        n: number of samples.

    Returns:
        White noise array of n samples in [-1, 1].
    '''
    return np.random.uniform(-1.0, 1.0, n)


def _sine(freq: float, n: int, rate: float = None) -> np.ndarray:
    '''
    Generate a sine wave.

    Args:
        freq: frequency (Hz).
        n: number of samples.
        rate: sample rate (Hz).

    Returns:
        Sine wave array of n samples in [-1, 1].
    '''
    t = np.arange(n, dtype=np.float64) / (SAMPLE_RATE if rate is None else rate)

    return np.sin(2.0 * math.pi * freq * t)


def _sweep(freq_start: float, freq_end: float, n: int, rate: float = None, wave: str = 'sine') -> np.ndarray:
    '''
    Generate a frequency sweep tone.

    Args:
        freq_start: start frequency (Hz).
        freq_end: end frequency (Hz).
        n: number of samples.
        rate: sample rate (Hz).
        wave: waveform type ('sine', 'square', or 'saw').

    Returns:
        Sweep tone array of n samples in [-1, 1].
    '''
    sample_rate = SAMPLE_RATE if rate is None else rate

    t = np.arange(n, dtype=np.float64) / sample_rate
   
    phase = 2.0 * math.pi * (freq_start * t + (freq_end - freq_start) * t * t / (2.0 * (n / sample_rate)))

    if wave == 'square':
        return np.sign(np.sin(phase))

    if wave == 'saw':
        return 2.0 * ((phase / (2.0 * math.pi)) % 1.0) - 1.0

    return np.sin(phase)


def _boom_env(n: int, fast: float = 15.0, slow: float = 5.0, slow_w: float = 0.35) -> np.ndarray:
    '''
    Two-stage decay envelope, fast initial drop followed by a slow tail.

    Args:
        n: number of samples.
        fast: fast-stage decay rate (1/s).
        slow: slow-stage decay rate (1/s).
        slow_w: weight of the slow stage in [0, 1].

    Returns:
        Envelope array of n samples.
    '''
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    return (1.0 - slow_w) * np.exp(-t * fast) + slow_w * np.exp(-t * slow)


def _crackle(n: int, events: float = 15.0) -> np.ndarray:
    '''
    Slow-varying random gate that mimics turbulent crackle in a rumble.

    Args:
        n: number of samples.
        events: approximate gate variation rate (per second).

    Returns:
        Gate array of n samples in [0, 1].
    '''
    m = max(2, int(n / (SAMPLE_RATE / events)))

    g = _lowpass(np.random.uniform(0.0, 1.0, m), 0.35)

    if g.max() > 0.0:
        g = g / g.max()

    return np.interp(np.linspace(0.0, 1.0, n), np.linspace(0.0, 1.0, m), g)


def _peak(x: np.ndarray, level: float = 0.85) -> np.ndarray:
    '''
    Scale a buffer to a target peak amplitude.

    Args:
        x: input samples.
        level: target peak in (0, 1].

    Returns:
        Scaled samples.
    '''
    p = float(np.max(np.abs(x)))

    if p > 0.0:
        return x / p * level

    return x


class SoundBank:
    '''Holds all synthesized sounds and provides playback methods.'''
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False
        self.sounds = {}

        self._build()

    def _build(self) -> None:
        '''Synthesize every sound into the bank.'''
        try:
            pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)

            if not pygame.mixer.get_init():
                pygame.mixer.init(SAMPLE_RATE, -16, 2, 512)
        
        except pygame.error:
            print('Warning: audio mixer unavailable, sound disabled.')
            
            return

        if not pygame.mixer.get_init():
            print('Warning: audio mixer failed to initialize, sound disabled.')
            
            return

        try:
            s = self.sounds

            # Laser pew: descending square sweep.
            n = int(0.13 * SAMPLE_RATE)
            
            s['laser'] = _to_sound(_sweep(950, 250, n, wave='square') * _envelope(n, decay=22) * 0.35)

            # Small explosion: filtered noise burst.
            n = int(0.32 * SAMPLE_RATE)
            
            s['explosion_small'] = _to_sound(_lowpass(_noise(n), 0.35) * _envelope(n, decay=14) * 0.2)

            # Big explosion: longer, deeper.
            n = int(0.5 * SAMPLE_RATE)
            
            boom = _lowpass(_noise(n), 0.12) * _envelope(n, decay=8) + \
                _sweep(160, 40, n, wave='sine') * _envelope(n, decay=7) * 0.5
            
            s['explosion_big'] = _to_sound(boom * 0.6)

            # Boss explosion: huge, layered noise blast with an initial crack.
            n = int(0.9 * SAMPLE_RATE)
            
            boom = _lowpass(_noise(n), 0.06) * _envelope(n, decay=4.5) + \
                _sweep(90, 30, n, wave='sine') * _envelope(n, decay=5) * 0.6
            
            crack_n = int(0.05 * SAMPLE_RATE)
            
            boom[:crack_n] += _lowpass(_noise(crack_n), 0.5) * _envelope(crack_n, decay=40) * 0.8
            
            s['explosion_boss'] = _to_sound(boom * 0.9)

            # Bomb: deep blast with a low rumble.
            n = int(0.5 * SAMPLE_RATE)
            
            boom = _lowpass(_noise(n), 0.15) * _envelope(n, decay=9) + \
                _sweep(190, 40, n, wave='sine') * _envelope(n, decay=8) * 0.55
            
            s['bomb'] = _to_sound(boom)

            # Dive whoosh: band-ish noise sweep with rising then falling gain.
            n = int(0.42 * SAMPLE_RATE)
            
            env = np.sin(np.linspace(0, math.pi, n)) ** 1.5
            
            whoosh = _lowpass(_noise(n), 0.25) * env * 0.5
            
            s['whoosh'] = _to_sound(whoosh)

            # Power-up chime: two rising sines.
            n1 = int(0.09 * SAMPLE_RATE)
            n2 = int(0.14 * SAMPLE_RATE)
            
            chime = np.concatenate([
                _sine(660, n1) * _envelope(n1, decay=18) * 0.5,
                _sine(1320, n2) * _envelope(n2, decay=12) * 0.5
            ])
            
            s['powerup'] = _to_sound(chime)

            # Extra life: happy three-note arp.
            parts = []

            for f in (523.25, 659.25, 783.99):
                nn = int(0.11 * SAMPLE_RATE)
                
                parts.append(_sine(f, nn) * _envelope(nn, decay=16) * 0.5)

            s['extralife'] = _to_sound(np.concatenate(parts))

            # Player death: descending saw + noise.
            n = int(0.65 * SAMPLE_RATE)
            
            death = _sweep(420, 60, n, wave='saw') * _envelope(n, decay=6) * 0.5 + \
                _lowpass(_noise(n), 0.2) * _envelope(n, decay=7) * 0.5
            
            s['player_death'] = _to_sound(death)

            # Shield hit: metallic ping.
            n = int(0.22 * SAMPLE_RATE)
            
            ping = _sine(1400, n) * _envelope(n, decay=26) * 0.4 + _sine(2100, n) * _envelope(n, decay=30) * 0.2
            
            s['shield_hit'] = _to_sound(ping)

            # Level clear jingle: rising 4-note arp.
            parts = []

            for f in (392.0, 523.25, 659.25, 783.99):
                nn = int(0.12 * SAMPLE_RATE)
                
                parts.append(_sine(f, nn) * _envelope(nn, decay=14) * 0.5)

            s['level_clear'] = _to_sound(np.concatenate(parts))

            # UI select.
            n = int(0.06 * SAMPLE_RATE)
            
            s['ui'] = _to_sound(_sine(880, n) * _envelope(n, decay=40) * 0.35)
        
        except Exception as e:
            print('Warning: sound synthesis failed, sound disabled.')
            print(f'Error: {e}')
            
            self.sounds.clear()

            return

        self.enabled = True

    def play(self, name: str, volume: float = 1.0) -> None:
        '''
        Play a named sound at the given volume.

        Args:
            name: key of the sound in the bank.
            volume: playback volume in [0, 1].
        '''
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
