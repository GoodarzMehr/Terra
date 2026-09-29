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

'''The player ship and its bullets.'''

import math
import pygame

from . import config as C


class PlayerBullet:
    '''
    Player's bullet. Moves straight up or in a fan pattern for the bomb.
    
    Args:
        x: spawn x in world-space (px).
        y: spawn y in world-space (px).
        vx: x velocity (px/s).
        vy: y velocity (px/s).
        owner: index of the firing player.
    '''
    __slots__ = ('x', 'y', 'vx', 'vy', 'owner', 'alive')

    def __init__(self, x: float, y: float, vx: float, vy: float, owner: 'Player'):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.owner = owner
        self.alive = True

    def update(self, dt: float) -> None:
        '''
        Move the bullet.

        Args:
            dt: frame delta (seconds).
        '''
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y < -20 or self.x < -20 or self.x > C.WIDTH + 20:
            self.alive = False

    def rect(self) -> pygame.Rect:
        '''
        Get the current screen-space hitbox rect.
        
        Returns:
            The hitbox rectangle.
        '''
        return pygame.Rect(int(self.x - C.BULLET_W / 2), int(self.y - C.BULLET_H / 2), C.BULLET_W, C.BULLET_H)

    def draw(self, surf: pygame.Surface, ox: float, oy: float) -> None:
        '''
        Draw the bullet.

        Args:
            surf: surface to draw on.
            ox: screen-space camera offset x (px).
            oy: screen-space camera offset y (px).
        '''
        x, y = int(self.x + ox), int(self.y + oy)

        # Glow.
        pygame.draw.circle(surf, (120, 200, 255), (x, y - 2), 5)

        # Core capsule.
        pygame.draw.rect(surf, C.WHITE, (x - 1, y - C.BULLET_H // 2, 3, C.BULLET_H))
        pygame.draw.rect(surf, C.CYAN, (x - 2, y - C.BULLET_H // 2 + 3, 5, C.BULLET_H - 6))


class Player:
    '''
    Player ship. Can move, fire, and take damage.
    
    Args:
        index: player index (0 for 1P/2P, 1 for 2P only).
        oneP: True if this is a 1P game, False if it's a 2P game.
    '''
    def __init__(self, index: int, oneP: bool = True):
        self.index = index # 0 = P1 (left), 1 = P2 (right)
        self.oneP = oneP

        self.x = C.WIDTH * (0.5 if oneP else 0.7 if index == 0 else 0.3)
        self.y = C.PLAYER_Y

        self.vx = 0.0

        self.lives = C.PLAYER_LIVES
        self.score = 0
        self.streak = 0 # consecutive kills without being hit
        self.multiplier = 1
        self.muted = False

        self.alive = True
        self.fire_cooldown = 0.0
        self.respawn_timer = 0.0
        self.invuln = 0.0
        self.spawn_anim = 0.0 # fly-in progress 0-1

        self.shield = False
        self.triple_t = 0.0
        self.rapid_t = 0.0
        self.bombs = C.BOMB_START

        self.bullets = []

    @property
    def multiplier_value(self) -> int:
        '''
        Get the current streak multiplier.

        Returns:
            The current streak multiplier.
        '''
        return min(C.STREAK_MAX, 1 + self.streak // 2)

    def reset(self) -> None:
        '''Reset position, lives, and streak for a new game.'''
        self.x = C.WIDTH * (0.5 if self.oneP else 0.7 if self.index == 0 else 0.3)

        self.vx = 0.0

        self.lives = C.PLAYER_LIVES
        self.score = 0
        self.streak = 0

        self.alive = True
        self.fire_cooldown = 0.0
        self.respawn_timer = 0.0
        self.invuln = 1.0
        self.spawn_anim = 1.0

        self.shield = False
        self.triple_t = 0.0
        self.rapid_t = 0.0
        self.bombs = C.BOMB_START

        self.bullets.clear()

    def hit(self, effects: 'Effects', sound: 'SoundBank') -> bool:
        '''
        Handle the player being hit by an enemy or bullet.
        
        Args:
            effects: Effects instance for explosions, shake, and flash.
            sound: SoundBank instance for playing hit sounds.

        Returns:
            True if the player died, False otherwise.
        '''
        if self.invuln > 0:
            return False

        if self.shield:
            self.shield = False

            effects.spark(self.x, self.y, C.CYAN, 18, 200, 0.4)
            effects.flash(C.CYAN, 0.1)

            sound.play('shield_hit')

            self.invuln = 1.0

            return False

        # Death.
        self.lives -= 1
        self.streak = 0

        self.bullets.clear()

        effects.explosion(self.x, self.y, C.GREEN, 40, 300, 0.8, 4)
        effects.explosion(self.x, self.y, C.WHITE, 16, 160, 0.5, 2)

        effects.shake(C.SHAKE_MAGNITUDE * 1.6, C.SHAKE_DURATION)
        effects.flash(C.RED, 0.15)

        sound.play('player_death')

        self.alive = False

        self.respawn_timer = C.PLAYER_RESPAWN_TIME

        return True

    def update(self, dt: float, move_dir: int, sound: 'SoundBank') -> None:
        '''
        Move, auto-fire, and tick shield/respawn timers.

        Args:
            dt: frame delta (seconds).
            move_dir: horizontal movement direction (-1/0/1).
            sound: SoundBank instance.
        '''
        # Timers.
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

        if self.invuln > 0:
            self.invuln -= dt

        if self.triple_t > 0:
            self.triple_t -= dt

        if self.rapid_t > 0:
            self.rapid_t -= dt

        if not self.alive:
            self.respawn_timer -= dt

            if self.respawn_timer <= 0 and self.lives > 0:
                self._respawn()

            return

        # Respawn fly-in.
        if self.spawn_anim < 1.0:
            self.spawn_anim = min(1.0, self.spawn_anim + dt / 0.5)
            self.invuln = max(self.invuln, 0.5)

            return  # no control during fly-in

        # Movement.
        self.vx = move_dir * C.PLAYER_SPEED

        self.x += self.vx * dt

        self.x = C.clamp(self.x, C.PLAYER_W / 2 + 8, C.WIDTH - C.PLAYER_W / 2 - 8)

        # Auto-firing.
        if self.fire_cooldown <= 0:
            self._fire(sound)

        # Bullets.
        for b in self.bullets:
            b.update(dt)

        self.bullets = [b for b in self.bullets if b.alive]

    def _respawn(self) -> None:
        '''Place the ship at its start position after a life is lost.'''
        self.x = C.WIDTH * (0.5 if self.oneP else 0.7 if self.index == 0 else 0.3)

        self.alive = True

        self.spawn_anim = 0.0

        self.invuln = C.PLAYER_RESPAWN_INVULN

        self.bullets.clear()

    def _fire(self, sound: 'SoundBank') -> None:
        '''
        Fire bullets (single or triple depending on powerups).

        Args:
            sound: SoundBank instance for the shot sound.
        '''
        rapid = self.rapid_t > 0

        cooldown = C.PLAYER_RAPID_COOLDOWN if rapid else C.PLAYER_FIRE_COOLDOWN

        y = self.y - C.PLAYER_H / 2

        if self.triple_t > 0:
            for vx in (-90.0, 0.0, 90.0):
                self.bullets.append(PlayerBullet(self.x, y, vx, -C.BULLET_SPEED, self))
        else:
            self.bullets.append(PlayerBullet(self.x, y, 0.0, -C.BULLET_SPEED, self))

        if not self.muted:
            sound.play('laser', 0.5)

        self.fire_cooldown = cooldown

    def bomb_fan(self, sound: 'SoundBank', effects: 'Effects') -> bool:
        '''
        Fire the multi-shot bomb fan across the forward cone.

        Args:
            sound: SoundBank instance for the blast sound.
            effects: Effects instance for the blast flash and shake.

        Returns:
            True if a bomb was fired, False if none were available.
        '''
        if self.bombs <= 0:
            return False

        self.bombs -= 1

        for i in range(C.BOMB_FAN_SHOTS):
            t = i / (C.BOMB_FAN_SHOTS - 1)

            ang = math.radians(-90.0) + (t - 0.5) * C.BOMB_FAN_ANGLE

            vx = math.cos(ang) * C.BOMB_BULLET_SPEED
            vy = math.sin(ang) * C.BOMB_BULLET_SPEED

            self.bullets.append(PlayerBullet(self.x, self.y, vx, vy, self))

        effects.flash(C.WHITE, 0.08)
        effects.shake(C.SHAKE_MAGNITUDE, C.SHAKE_DURATION)

        sound.play('bomb', 1.0)

        return True

    def draw(self, surf: pygame.Surface, ox: float, oy: float) -> None:
        '''
        Draw the ship and shield bubble (if active).

        Args:
            surf: surface to draw on.
            ox: screen-space camera offset x (px).
            oy: screen-space camera offset y (px).
        '''
        if not self.alive:
            return

        # Blink while invulnerable.
        if self.invuln > 0 and int(self.invuln * 12) % 2 == 0:
            return

        # Fly-in from below.
        t = self.spawn_anim

        x = self.x
        y = C.HEIGHT + 20 + (self.y - (C.HEIGHT + 20)) * t

        px, py = int(x + ox), int(y + oy)

        # Shield bubble.
        if self.shield:
            pygame.draw.circle(surf, C.CYAN, (px, py), 24, 2)
            pygame.draw.circle(surf, (90, 220, 255, 40), (px, py), 22)

        # Ship (pointing up).
        # wings.
        pygame.draw.polygon(surf, C.GREEN, [(px, py - 15), (px - 13, py + 10), (px - 5, py + 6)])
        pygame.draw.polygon(surf, C.GREEN, [(px, py - 15), (px + 13, py + 10), (px + 5, py + 6)])

        # Fuselage.
        pygame.draw.polygon(surf, C.WHITE, [(px, py - 16), (px - 4, py + 8), (px + 4, py + 8)])

        # Cockpit.
        pygame.draw.circle(surf, C.CYAN, (px, py - 4), 3)

        # Engine glow.
        pygame.draw.circle(surf, C.ORANGE, (px, py + 10), 3)
        pygame.draw.circle(surf, C.YELLOW, (px, py + 10), 2)

        # Active power-up pips under the ship.
        pip_y = py + 18

        if self.triple_t > 0:
            pygame.draw.circle(surf, C.YELLOW, (px - 8, pip_y), 3)

        if self.rapid_t > 0:
            pygame.draw.circle(surf, C.MAGENTA, (px, pip_y), 3)

        if self.shield:
            pygame.draw.circle(surf, C.CYAN, (px + 8, pip_y), 3)