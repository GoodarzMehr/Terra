'''The player ship and its bullets.'''

import math

import pygame

from . import config as C


class PlayerBullet:
    __slots__ = ('x', 'y', 'vx', 'vy', 'owner', 'alive')

    def __init__(self, x: float, y: float, vx: float, vy: float, owner: 'Player'):
        '''
        Create a player bullet.

        Args:
            x: spawn x in world px.
            y: spawn y in world px.
            vx: x velocity in px/s.
            vy: y velocity in px/s.
            owner: index of the firing player.
        '''
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.owner = owner
        self.alive = True

    def update(self, dt: float) -> None:
        '''
        Move the bullet.

        Args:
            dt: frame delta in seconds.
        '''
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y < -20 or self.x < -20 or self.x > C.WIDTH + 20:
            self.alive = False

    def rect(self) -> pygame.Rect:
        '''Current screen-space hitbox rect.'''
        return pygame.Rect(int(self.x - C.BULLET_W / 2), int(self.y - C.BULLET_H / 2),
                           C.BULLET_W, C.BULLET_H)

    def draw(self, surf: pygame.Surface, ox: float, oy: float) -> None:
        '''
        Draw the bullet.

        Args:
            surf: surface to draw on.
            ox: screen-space camera offset x in px.
            oy: screen-space camera offset y in px.
        '''
        x, y = int(self.x + ox), int(self.y + oy)

        # glow
        pygame.draw.circle(surf, (120, 200, 255), (x, y - 2), 5)

        # core capsule
        pygame.draw.rect(surf, C.WHITE, (x - 1, y - C.BULLET_H // 2, 3, C.BULLET_H))
        pygame.draw.rect(surf, C.CYAN, (x - 2, y - C.BULLET_H // 2 + 3, 5, C.BULLET_H - 6))


class Player:
    def __init__(self, index: int):
        '''
        Create a player.

        Args:
            index: player index (0 for 1P/2P, 1 for 2P only).
        '''
        self.index = index  # 0 = P1 (left), 1 = P2 (right)
        self.x = C.WIDTH * (0.3 if index == 0 else 0.7)
        self.y = C.PLAYER_Y
        self.vx = 0.0  # px/s, tracked for enemy lead-aiming

        self.lives = C.PLAYER_LIVES
        self.score = 0
        self.streak = 0  # consecutive kills without being hit
        self.multiplier = 1

        self.fire_cooldown = 0.0
        self.alive = True
        self.respawn_timer = 0.0
        self.invuln = 0.0
        self.spawn_anim = 0.0  # fly-in progress 0..1

        self.shield = False
        self.triple_t = 0.0
        self.rapid_t = 0.0
        self.bombs = C.BOMB_START

        self.bullets = []

    @property
    def multiplier_value(self) -> int:
        '''Current streak multiplier (1-6).'''
        return min(C.STREAK_MAX, 1 + self.streak // 2)

    def reset(self) -> None:
        '''Reset position, lives, and streak for a new game.'''
        self.x = C.WIDTH * (0.3 if self.index == 0 else 0.7)
        self.vx = 0.0
        self.lives = C.PLAYER_LIVES
        self.score = 0
        self.streak = 0
        self.fire_cooldown = 0.0
        self.alive = True
        self.respawn_timer = 0.0
        self.invuln = 1.0
        self.spawn_anim = 1.0
        self.shield = False
        self.triple_t = 0.0
        self.rapid_t = 0.0
        self.bombs = C.BOMB_START
        self.bullets.clear()

    def hit(self, effects: 'Effects', sound: 'SoundBank') -> bool:
        '''Player took a hit. Returns True if the player died.'''
        if self.invuln > 0:
            return False

        if self.shield:
            self.shield = False
            effects.spark(self.x, self.y, C.CYAN, 18, 200, 0.4)
            effects.flash(C.CYAN, 0.1)
            sound.play('shield_hit')
            self.invuln = 1.0

            return False

        # death
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
            dt: frame delta in seconds.
            move_dir: horizontal direction (-1/0/1).
            sound: SoundBank instance.
        '''
        # timers
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

        # respawn fly-in
        if self.spawn_anim < 1.0:
            self.spawn_anim = min(1.0, self.spawn_anim + dt / 0.5)
            self.invuln = max(self.invuln, 0.5)

            return  # no control during fly-in

        # movement
        self.vx = move_dir * C.PLAYER_SPEED
        self.x += self.vx * dt
        self.x = C.clamp(self.x, C.PLAYER_W / 2 + 8, C.WIDTH - C.PLAYER_W / 2 - 8)

        # auto-firing
        if self.fire_cooldown <= 0:
            self._fire(sound)

        # bullets
        for b in self.bullets:
            b.update(dt)

        self.bullets = [b for b in self.bullets if b.alive]

    def _respawn(self) -> None:
        '''Place the ship at its start position after a life is lost.'''
        self.x = C.WIDTH * (0.3 if self.index == 0 else 0.7)
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
        active = [b for b in self.bullets if b.alive]

        if len(active) >= C.MAX_PLAYER_BULLETS:
            return

        y = self.y - C.PLAYER_H / 2

        if self.triple_t > 0:
            for vx in (-90.0, 0.0, 90.0):
                self.bullets.append(PlayerBullet(self.x, y, vx, -C.BULLET_SPEED, self))
        else:
            self.bullets.append(PlayerBullet(self.x, y, 0.0, -C.BULLET_SPEED, self))

        sound.play('laser', 0.5)
        self.fire_cooldown = cooldown

    def bomb_fan(self, sound: 'SoundBank', effects: 'Effects') -> bool:
        '''
        Fire the 15-shot bomb fan across a 60-degree forward cone.

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
            ox: screen-space camera offset x in px.
            oy: screen-space camera offset y in px.
        '''
        if not self.alive:
            return

        # blink while invulnerable
        if self.invuln > 0 and int(self.invuln * 12) % 2 == 0:
            return

        # fly-in from below
        t = self.spawn_anim
        y = C.HEIGHT + 20 + (self.y - (C.HEIGHT + 20)) * t
        x = self.x
        px, py = int(x + ox), int(y + oy)

        # shield bubble
        if self.shield:
            pygame.draw.circle(surf, C.CYAN, (px, py), 24, 2)
            pygame.draw.circle(surf, (90, 220, 255, 40), (px, py), 22)

        # --- ship (pointing up) ---
        # wings
        pygame.draw.polygon(surf, C.GREEN, [
            (px, py - 15),
            (px - 13, py + 10),
            (px - 5, py + 6),
        ])
        pygame.draw.polygon(surf, C.GREEN, [
            (px, py - 15),
            (px + 13, py + 10),
            (px + 5, py + 6),
        ])

        # fuselage
        pygame.draw.polygon(surf, C.WHITE, [
            (px, py - 16),
            (px - 4, py + 8),
            (px + 4, py + 8),
        ])

        # cockpit
        pygame.draw.circle(surf, C.CYAN, (px, py - 4), 3)

        # engine glow
        pygame.draw.circle(surf, C.ORANGE, (px, py + 10), 3)
        pygame.draw.circle(surf, C.YELLOW, (px, py + 10), 2)

        # active power-up pips under the ship
        pip_y = py + 18

        if self.triple_t > 0:
            pygame.draw.circle(surf, C.YELLOW, (px - 8, pip_y), 3)

        if self.rapid_t > 0:
            pygame.draw.circle(surf, C.MAGENTA, (px, pip_y), 3)

        if self.shield:
            pygame.draw.circle(surf, C.CYAN, (px + 8, pip_y), 3)

        if self.bombs > 0:
            pygame.draw.circle(surf, C.ORANGE, (px + 16, pip_y), 3)
