'''HUD and full-screen overlays: top bar, menu, wave intro, pause, game over.'''

import pygame

from . import config as C


class HUD:
    def __init__(self):
        '''Create the fonts used by the HUD.'''
        self.font_xs = pygame.font.Font(None, 18)
        self.font_s = pygame.font.Font(None, 22)
        self.font_m = pygame.font.Font(None, 30)
        self.font_l = pygame.font.Font(None, 48)
        self.font_xl = pygame.font.Font(None, 92)

    def draw_top(self, surf: pygame.Surface, players: list,
                 level: int, highscores: dict) -> None:
        '''
        Draw the in-game top bar (lives, score, level, wave stats).

        Args:
            surf: surface to draw on.
            players: list of Player objects.
            level: current 1-based level number.
            highscores: high scores dict keyed by player index.
        '''
        # 1P block (left)
        self._text(surf, '1UP', C.YELLOW, 16, 10, self.font_s)
        s1 = self._text(surf, f'{players[0].score:07d}', C.WHITE, 16, 28, self.font_m)
        m1 = players[0].multiplier_value

        if m1 > 1:
            self._text(surf, f'x{m1} STREAK', C.ORANGE, s1.right + 8, 30, self.font_s)

        # 2P block (right)
        if len(players) > 1:
            label = self._text(surf, '2UP', C.CYAN, 0, 10, self.font_s,
                               align='right', anchor_x=C.WIDTH - 16)

            s2 = self._text(surf, f'{players[1].score:07d}', C.WHITE, 0, 28, self.font_m,
                            align='right', anchor_x=C.WIDTH - 16)

            m2 = players[1].multiplier_value

            if m2 > 1:
                self._text(surf, f'x{m2} STREAK', C.ORANGE, s2.left - 8, 30, self.font_s,
                           align='right')

        # high score (center)
        hs = max(highscores.get('1p', 0), highscores.get('2p', 0))
        self._text(surf, f'HIGH {hs:07d}', C.WHITE, C.WIDTH // 2, 10, self.font_s,
                   align='center')

        # wave (center, below)
        self._text(surf, f'WAVE {level}', C.GREEN, C.WIDTH // 2, 30, self.font_m,
                   align='center')

        # lives as tiny ships
        for i, p in enumerate(players):
            base_x = 16 if i == 0 else C.WIDTH - 16

            for j in range(max(0, p.lives - 1)):  # spare ships (current one is on field)
                x = base_x + j * 22 if i == 0 else base_x - j * 22 - 16
                self._ship_icon(surf, x + 8, 58, C.GREEN)

        # enemy status (top right, small font)
        p = C.level_params(level)
        status = (f'DIVE {int(p["dive_speed"])}   '
                  f'FIRE {p["enemy_fire_chance"]:.0%}   '
                  f'DIVERS {p["max_divers"]}')

        self._text(surf, status, C.LIGHT_GRAY, 0, 74, self.font_xs,
                   align='right', anchor_x=C.WIDTH - 16)

    def _ship_icon(self, surf: pygame.Surface, x: int, y: int, color: tuple) -> None:
        '''
        Draw a small player-ship icon.

        Args:
            surf: surface to draw on.
            x: icon center x in px.
            y: icon center y in px.
            color: hull color.
        '''
        pts = [(x, y + 6), (x - 6, y - 5), (x - 2, y - 5), (x, y - 2),
               (x + 2, y - 5), (x + 6, y - 5), (x, y + 6)]

        pygame.draw.polygon(surf, color, pts)

    def draw_menu(self, surf: pygame.Surface, highscores: dict,
                  selected_mode: int) -> None:
        '''
        Draw the main menu with the selected mode highlighted.

        Args:
            surf: surface to draw on.
            highscores: high scores dict keyed by player index.
            selected_mode: index of the highlighted menu mode.
        '''
        # title with layered color
        title = self.font_xl.render('GALAGA', True, C.RED)
        t2 = self.font_xl.render('GALAGA', True, C.ORANGE)
        surf.blit(t2, t2.get_rect(center=(C.WIDTH // 2, 150)))
        surf.blit(title, title.get_rect(center=(C.WIDTH // 2, 148)))
        sub = self.font_m.render('CO-OP ARCADE ACTION', True, C.CYAN)
        surf.blit(sub, sub.get_rect(center=(C.WIDTH // 2, 205)))

        # mode select
        opts = [('1 PLAYER', 1), ('2 PLAYERS (CO-OP)', 2)]
        y = 290

        for text, mode in opts:
            color = C.WHITE if mode == selected_mode else C.GRAY
            img = self.font_l.render(text, True, color)
            surf.blit(img, img.get_rect(center=(C.WIDTH // 2 + (28 if mode == selected_mode else 0), y)))

            if mode == selected_mode:
                arrow = self.font_l.render('>', True, C.YELLOW)
                surf.blit(arrow, (C.WIDTH // 2 - img.get_width() // 2 - 30, y - 22))

            y += 56

        # high scores
        hs1 = highscores.get('1p', 0)
        hs2 = highscores.get('2p', 0)
        h1 = self.font_m.render(f'HIGH SCORE  1P: {hs1:07d}', True, C.YELLOW)
        surf.blit(h1, h1.get_rect(center=(C.WIDTH // 2, 430)))
        h2 = self.font_m.render(f'HIGH SCORE  2P: {hs2:07d}', True, C.YELLOW)
        surf.blit(h2, h2.get_rect(center=(C.WIDTH // 2, 460)))

        # footer hints
        f1 = self.font_s.render('UP/DOWN: SELECT MODE      ENTER: START      P: PAUSE      ESC: QUIT',
                                True, C.LIGHT_GRAY)

        surf.blit(f1, f1.get_rect(center=(C.WIDTH // 2, 540)))
        f2 = self.font_s.render('P1: ARROWS MOVE (AUTO-FIRE)        P2: A/D MOVE (AUTO-FIRE)',
                                True, C.LIGHT_GRAY)

        surf.blit(f2, f2.get_rect(center=(C.WIDTH // 2, 566)))

    def draw_intro(self, surf: pygame.Surface, level: int, params: dict) -> None:
        '''
        Draw the wave-intro banner with the level's parameters.

        Args:
            surf: surface to draw on.
            level: 1-based level number.
            params: level parameters dict from config.level_params.
        '''
        banner = self.font_xl.render(f'WAVE {level}', True, C.YELLOW)
        surf.blit(banner, banner.get_rect(center=(C.WIDTH // 2, 250)))
        ready = self.font_l.render('GET READY', True, C.WHITE)
        surf.blit(ready, ready.get_rect(center=(C.WIDTH // 2, 330)))

        # difficulty readout
        p = params
        diff = self.font_m.render(
            f'ENEMY FIRE {p["enemy_fire_chance"]:.0%}   DIVE SPEED {int(p["dive_speed"])}   '
            f'MAX DIVERS {p["max_divers"]}', True, C.GREEN)

        surf.blit(diff, diff.get_rect(center=(C.WIDTH // 2, 395)))

    def draw_pause(self, surf: pygame.Surface) -> None:
        '''
        Draw the pause overlay.

        Args:
            surf: surface to draw on.
        '''
        veil = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 150))
        surf.blit(veil, (0, 0))

        t = self.font_xl.render('PAUSED', True, C.WHITE)
        surf.blit(t, t.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 - 20)))
        h = self.font_m.render('PRESS P TO RESUME', True, C.LIGHT_GRAY)
        surf.blit(h, h.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 + 40)))

    def draw_game_over(self, surf: pygame.Surface, players: list,
                       highscore_flag: bool) -> None:
        '''
        Draw the game-over screen with final scores.

        Args:
            surf: surface to draw on.
            players: list of Player objects.
            highscore_flag: True if a new high score was set.
        '''

        veil = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 170))
        surf.blit(veil, (0, 0))

        t = self.font_xl.render('GAME OVER', True, C.RED)
        surf.blit(t, t.get_rect(center=(C.WIDTH // 2, 220)))

        for i, p in enumerate(players):
            label = 'PLAYER 1' if i == 0 else 'PLAYER 2'
            line = self.font_l.render(f'{label}: {p.score:07d}', True, C.WHITE)
            surf.blit(line, line.get_rect(center=(C.WIDTH // 2, 310 + i * 50)))

        if highscore_flag:
            flag = self.font_l.render('*** NEW HIGH SCORE ***', True, C.YELLOW)
            surf.blit(flag, flag.get_rect(center=(C.WIDTH // 2, 410)))

        h = self.font_m.render('PRESS ENTER FOR MENU', True, C.LIGHT_GRAY)
        surf.blit(h, h.get_rect(center=(C.WIDTH // 2, 480)))

    def _text(self, surf: pygame.Surface, text: str, color: tuple, x: int, y: int,
              font: pygame.font.Font, align: str = 'left',
              anchor_x: int = None) -> pygame.Rect:
        '''
        Blit a centered text string and return its rect.

        Args:
            surf: surface to draw on.
            text: string to render.
            color: text color.
            x: anchor x in px.
            y: anchor y in px.
            font: font to render with.
            align: vertical alignment ('top', 'center', or 'bottom').
            anchor_x: anchor x from 0.0 (left) to 1.0 (right).

        Returns:
            Rect of the rendered text.
        '''

        img = font.render(text, True, color)
        r = img.get_rect()

        if align == 'left':
            r.topleft = (x, y)
        elif align == 'center':
            r.center = (anchor_x if anchor_x is not None else C.WIDTH // 2, y + r.height // 2)
        elif align == 'right':
            r.topright = (anchor_x if anchor_x is not None else C.WIDTH - x, y)

        surf.blit(img, r)

        return r
