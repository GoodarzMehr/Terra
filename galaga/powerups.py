'''Power-up drops: falling pickups and their timed effects.'''

import math
import random

import pygame

from . import config as C

# (kind, weight, color, label char)
TABLE = [
    ('triple', 30, C.YELLOW, '3'),
    ('rapid', 30, C.MAGENTA, 'R'),
    ('shield', 25, C.CYAN, 'S'),
    ('life', 15, C.PINK, '+'),
]


class Powerup:
    __slots__ = ('kind', 'x', 'y', 't', 'alive', 'color', 'label')

    def __init__(self, kind: str, x: float, y: float):
        '''
        Create a falling powerup.

        Args:
            kind: powerup kind ('triple', 'rapid', 'shield', or 'life').
            x: spawn x in world px.
            y: spawn y in world px.
        '''
        self.kind = kind
        self.x = x
        self.y = y
        self.t = 0.0
        self.alive = True

        for k, _w, c, lab in TABLE:
            if k == kind:
                self.color = c
                self.label = lab
                break

    def update(self, dt: float) -> None:
        '''
        Move the powerup downward.

        Args:
            dt: frame delta in seconds.
        '''
        self.t += dt
        self.y += C.POWERUP_FALL_SPEED * dt
        self.x += math.sin(self.t * 2.0) * 30 * dt  # gentle sway

        if self.y > C.HEIGHT + 20:
            self.alive = False

    def rect(self) -> pygame.Rect:
        '''Current screen-space hitbox rect.'''
        s = C.POWERUP_W

        return pygame.Rect(int(self.x - s / 2), int(self.y - s / 2), s, s)

    def draw(self, surf: pygame.Surface, font: pygame.font.Font,
             ox: float, oy: float) -> None:
        '''
        Draw the powerup letter and label.

        Args:
            surf: surface to draw on.
            font: font to render the label with.
            ox: screen-space camera offset x in px.
            oy: screen-space camera offset y in px.
        '''

        pulse = 0.6 + 0.4 * math.sin(self.t * 6.0)
        x, y = int(self.x + ox), int(self.y + oy)

        # glow
        glow = pygame.Surface((C.POWERUP_W * 2, C.POWERUP_W * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, int(60 * pulse)),
                           (C.POWERUP_W, C.POWERUP_W), C.POWERUP_W)

        surf.blit(glow, (x - C.POWERUP_W, y - C.POWERUP_W))

        # capsule
        pygame.draw.rect(surf, self.color, (x - 10, y - 10, 20, 20), border_radius=6)
        pygame.draw.rect(surf, C.WHITE, (x - 10, y - 10, 20, 20), 2, border_radius=6)
        img = font.render(self.label, True, C.WHITE)
        surf.blit(img, img.get_rect(center=(x, y)))


class PowerupManager:
    def __init__(self):
        '''Create an empty powerup list.'''
        self.pickups = []

    def reset(self) -> None:
        '''Clear all active powerups (new game).'''
        self.pickups.clear()

    def maybe_drop(self, x: float, y: float, etype: str) -> None:
        '''Roll for a drop from a kill. Bosses always drop.'''
        chance = C.POWERUP_BOSS_DROP if etype == 'boss' else C.POWERUP_DROP_CHANCE

        if random.random() > chance:
            return

        kind = self._roll_kind()
        self.pickups.append(Powerup(kind, x, y))

    def _roll_kind(self) -> str:
        '''Roll a random powerup kind using the config weights.'''
        total = sum(w for _k, w, _c, _l in TABLE)
        r = random.uniform(0, total)
        acc = 0.0

        for kind, w, _c, _l in TABLE:
            acc += w

            if r <= acc:
                return kind

        return TABLE[-1][0]

    def update(self, dt: float, players: list, sound: 'SoundBank',
               effects: 'Effects') -> None:
        '''
        Advance falling powerups and handle player pickups.

        Args:
            dt: frame delta in seconds.
            players: list of Player objects.
            sound: SoundBank instance.
            effects: Effects instance for pickup feedback.
        '''

        for p in self.pickups:
            p.update(dt)

        # collection
        for p in self.pickups:
            if not p.alive:
                continue

            pr = p.rect()

            for player in players:
                if not player.alive:
                    continue

                prct = pygame.Rect(int(player.x - C.PLAYER_W / 2),
                                   int(player.y - C.PLAYER_H / 2),
                                   C.PLAYER_W, C.PLAYER_H)

                if prct.inflate(14, 14).colliderect(pr):
                    p.alive = False
                    self._apply(p.kind, player, sound, effects)
                    break

        self.pickups = [p for p in self.pickups if p.alive]

    def _apply(self, kind: str, player: 'Player', sound: 'SoundBank',
               effects: 'Effects') -> None:
        '''
        Apply a picked-up powerup to the collecting player.

        Args:
            kind: powerup kind.
            player: the Player that collected it.
            sound: SoundBank instance.
            effects: Effects instance for pickup feedback.
        '''

        if kind == 'triple':
            player.triple_t = C.TRIPLE_DURATION
            effects.popup(player.x, player.y - 24, 'TRIPLE!', C.YELLOW)
            sound.play('powerup')
        elif kind == 'rapid':
            player.rapid_t = C.RAPID_DURATION
            effects.popup(player.x, player.y - 24, 'RAPID!', C.MAGENTA)
            sound.play('powerup')
        elif kind == 'shield':
            player.shield = True
            effects.popup(player.x, player.y - 24, 'SHIELD!', C.CYAN)
            sound.play('powerup')
        elif kind == 'life':
            player.lives += 1
            effects.popup(player.x, player.y - 24, '1UP!', C.PINK)
            sound.play('extralife')

    def draw(self, surf: pygame.Surface, font: pygame.font.Font,
             ox: float, oy: float) -> None:
        '''
        Draw all active powerups.

        Args:
            surf: surface to draw on.
            font: font to render the labels with.
            ox: screen-space camera offset x in px.
            oy: screen-space camera offset y in px.
        '''

        for p in self.pickups:
            p.draw(surf, font, ox, oy)
