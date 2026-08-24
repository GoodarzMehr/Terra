'''Three-layer parallax scrolling starfield background.'''

import math
import random

import pygame

from . import config as C


class Star:
    __slots__ = ('x', 'y', 'speed', 'size', 'color', 'twinkle')

    def __init__(self, layer: int) -> None:
        self.x = random.uniform(0, C.WIDTH)
        self.y = random.uniform(0, C.HEIGHT)

        # Layer 0 = far/dim/slow, layer 2 = near/bright/fast
        self.speed = (14.0, 34.0, 72.0)[layer]
        self.size = (1, 1, 2)[layer]
        self.color = (
            (70, 80, 120),
            (120, 130, 170),
            (200, 210, 240),
        )[layer]
        self.twinkle = random.uniform(0.0, 6.28)


class Starfield:
    def __init__(self, count: tuple = (50, 34, 18)) -> None:
        self.stars = []

        for layer in range(3):
            for _ in range(count[layer]):
                self.stars.append(Star(layer))

        self.t = 0.0

    def update(self, dt: float, speed_mult: float = 1.0) -> None:
        self.t += dt

        for s in self.stars:
            s.y += s.speed * speed_mult * dt

            if s.y > C.HEIGHT:
                s.y -= C.HEIGHT
                s.x = random.uniform(0, C.WIDTH)

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(C.BLACK)

        # Subtle vertical nebula gradient bands
        band = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)

        for i in range(0, C.HEIGHT, 4):
            a = int(6 * (1.0 - i / C.HEIGHT))
            pygame.draw.line(band, (20, 16, 50, a), (0, i), (C.WIDTH, i))

        surf.blit(band, (0, 0))

        for s in self.stars:
            # Gentle twinkle
            tw = 0.75 + 0.25 * math.sin(self.t * 2.0 + s.twinkle)
            col = tuple(int(c * tw) for c in s.color)

            if s.size == 1:
                surf.set_at((int(s.x), int(s.y)), col)
            else:
                pygame.draw.rect(surf, col, (int(s.x), int(s.y), s.size, s.size))
