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

'''
Visual effects: explosion particles, screen shake, floating score popups.
'''

import math
import random
import pygame

from . import config as C


class Particle:
    '''
    A single particle for explosions, sparks, etc.

    Args:
        x: start x in world-space (px).
        y: start y in world-space (px).
        vx: x velocity (px/s).
        vy: y velocity (px/s).
        life: lifetime (seconds).
        color: particle color.
        size: radius (px).
        drag: velocity damping factor per second.
    '''
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size', 'drag')

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        color: tuple,
        size: int = 3,
        drag: float = 2.0
    ):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.size = size
        self.drag = drag

    def update(self, dt: float) -> None:
        '''
        Advance position and lifetime.

        Args:
            dt: frame delta (seconds).
        '''
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx -= self.vx * self.drag * dt
        self.vy -= self.vy * self.drag * dt

    def draw(self, surf: pygame.Surface, ox: float, oy: float) -> None:
        '''
        Draw the particle (fades out as it dies).

        Args:
            surf: surface to draw on.
            ox: screen-space camera offset x (px).
            oy: screen-space camera offset y (px).
        '''
        k = max(0.0, self.life / self.max_life)

        size = max(1, int(self.size * k))

        col = tuple(int(c * (0.4 + 0.6 * k)) for c in self.color)

        pygame.draw.circle(surf, col, (int(self.x + ox), int(self.y + oy)), size)


class ScorePopup:
    '''
    A floating score popup that rises and fades.

    Args:
        x: start x in world-space (px).
        y: start y in world-space (px).
        text: score text to show.
        color: text color.
        life: lifetime (seconds).
    '''
    __slots__ = ('x', 'y', 'text', 'life', 'max_life', 'color')

    def __init__(self, x: float, y: float, text: str, color: tuple, life: float = 0.9):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = self.max_life = life

    def update(self, dt: float) -> None:
        '''
        Advance the rise and fade.

        Args:
            dt: frame delta (seconds).
        '''
        self.life -= dt
        self.y -= 34 * dt

    def draw(self, surf: pygame.Surface, font: pygame.font.Font, ox: float, oy: float) -> None:
        '''
        Draw the popup text.

        Args:
            surf: surface to draw on.
            font: font to render with.
            ox: screen-space camera offset x (px).
            oy: screen-space camera offset y (px).
        '''
        if self.life <= 0:
            return

        a = max(0.0, min(1.0, self.life / (self.max_life * 0.5)))

        img = font.render(self.text, True, self.color)

        img.set_alpha(int(255 * a))

        rect = img.get_rect(center=(int(self.x + ox), int(self.y + oy)))

        surf.blit(img, rect)


class Effects:
    '''Holds particles, popups, and the screen-shake state.'''
    def __init__(self):
        self.particles = []
        self.popups = []

        self.shake_t = 0.0
        self.shake_dur = 0.0
        self.shake_mag = 0.0

        self.flash_t = 0.0
        self.flash_color = (255, 255, 255)

    def explosion(
        self,
        x: float,
        y: float,
        color: tuple,
        count: int = 22,
        speed: float = 220.0,
        life: float = 0.55,
        size: int = 3
    ) -> None:
        '''
        Spawn a burst of particles at a point.

        Args:
            x: burst center x in world-space (px).
            y: burst center y in world-space (px).
            color: particle color.
            count: number of particles.
            speed: radial speed (px/s).
            life: particle lifetime (seconds).
            size: particle radius (px).
        '''
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(speed * 0.25, speed)

            self.particles.append(
                Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp, random.uniform(life * 0.5, life), color, size)
            )

        # Hot white core.
        for _ in range(count // 4):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(30, 90)

            self.particles.append(Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp, life * 0.4, C.WHITE, 2))

    def spark(
        self,
        x: float,
        y: float,
        color: tuple,
        count: int = 6,
        speed: float = 120.0,
        life: float = 0.3
    ) -> None:
        '''
        Spawn a burst of spark particles at a point.

        Args:
            x: burst center x in world-space (px).
            y: burst center y in world-space (px).
            color: particle color.
            count: number of particles.
            speed: radial speed (px/s).
            life: particle lifetime (seconds).
        '''
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(speed * 0.3, speed)

            self.particles.append(
                Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp, random.uniform(life * 0.5, life), color, 2)
            )

    def popup(self, x: float, y: float, text: str, color: tuple) -> None:
        '''
        Spawn a floating score popup.

        Args:
            x: popup x in world-space (px).
            y: popup y in world-space (px).
            text: score text to show.
            color: text color.
        '''
        self.popups.append(ScorePopup(x, y, text, color))

    def shake(self, magnitude: float, duration: float) -> None:
        '''
        Start a screen shake effect.

        Args:
            magnitude: shake amplitude (px).
            duration: shake duration (seconds).
        '''
        # Keep the strongest shake currently active.
        if self.shake_t <= 0 or magnitude > self.shake_mag:
            self.shake_mag = magnitude
            self.shake_dur = duration
            self.shake_t = duration

    def flash(self, color: tuple, duration: float = 0.12) -> None:
        '''
        Start a full-screen flash effect.

        Args:
            color: flash color.
            duration: flash duration (seconds).
        '''
        self.flash_color = color
        self.flash_t = duration

    def update(self, dt: float) -> None:
        '''
        Advance all particles, popups, and screen-shake timers.

        Args:
            dt: frame delta (seconds).
        '''
        for p in self.particles:
            p.update(dt)

        self.particles = [p for p in self.particles if p.life > 0]

        for pop in self.popups:
            pop.update(dt)

        self.popups = [p for p in self.popups if p.life > 0]

        if self.shake_t > 0:
            self.shake_t -= dt

        if self.flash_t > 0:
            self.flash_t -= dt

    def offset(self) -> tuple:
        '''
        Get the current screen-shake offset.
        
        Returns:
            The current screen-shake offset as (dx, dy) (px).
        '''
        if self.shake_t <= 0:
            return 0, 0

        k = self.shake_t / max(1e-6, self.shake_dur)
        m = self.shake_mag * k

        return (random.uniform(-m, m), random.uniform(-m, m))

    def draw(self, surf: pygame.Surface, ox: float, oy: float, popup_font: pygame.font.Font) -> None:
        '''
        Draw all particles, popups, and the flash overlay.

        Args:
            surf: surface to draw on.
            ox: screen-space camera offset x (px).
            oy: screen-space camera offset y (px).
            popup_font: font for score popups.
        '''
        for p in self.particles:
            p.draw(surf, ox, oy)

        for pop in self.popups:
            pop.draw(surf, popup_font, ox, oy)

        if self.flash_t > 0:
            a = int(90 * (self.flash_t / 0.12))
            a = max(0, min(255, a))

            flash = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)

            flash.fill((*self.flash_color, a))

            surf.blit(flash, (0, 0))