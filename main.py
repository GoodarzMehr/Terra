#!/usr/bin/env python3
'''TERRA — a colorful co-op arcade shooter in pygame.

Run:      python main.py
Fullscr:  python main.py --fullscreen  (fills the monitor, fits any screen)
Selftest: python main.py --selftest   (headless, prints SELFTEST OK)

Controls
  P1: LEFT/RIGHT move (auto-fire)
  P2: A/D move (auto-fire)
  P: pause, M: mute/unmute, Enter: confirm, Esc: quit

'''

import json
import os
import random
import sys

import pygame

from terra import config as C
from terra.enemies import Fleet
from terra.hud import HUD
from terra.levels import LevelManager
from terra.particles import Effects
from terra.player import Player
from terra.powerups import PowerupManager
from terra.sound import SAMPLE_RATE, SoundBank
from terra.starfield import Starfield

# Game states
MENU = 'menu'
INTRO = 'intro'
PLAYING = 'playing'
GAME_OVER = 'game_over'


class Game:
    def __init__(self, selftest: bool = False, fullscreen: bool = False):
        '''Initialize the game window, subsystems, and main menu state.'''
        self.selftest = selftest

        if selftest:
            os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
            os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

        pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption(C.TITLE)

        # The game logic and all drawing happen in a logical C.WIDTH x
        # C.HEIGHT space; the whole frame is then upscaled by UI_SCALE (2x)
        # to the real window so that every sprite, bullet, particle and HUD
        # element is uniformly 2x larger.
        self.world = pygame.Surface((C.WIDTH, C.HEIGHT))

        if fullscreen:
            flags = pygame.FULLSCREEN | pygame.SCALED
            self.screen = pygame.display.set_mode((C.WINDOW_W, C.WINDOW_H), flags)
        else:
            # Fit the window to the display. A fixed 1600x1200 window is
            # fine on a 4K screen but overflows smaller displays (or
            # displays with OS scaling), so shrink it to the largest size
            # that fits, keeping the 4:3 aspect ratio.
            win_w, win_h = C.WINDOW_W, C.WINDOW_H

            try:
                dw, dh = pygame.display.get_desktop_sizes()[0]
            except (IndexError, TypeError, ValueError):
                dw = dh = None

            if dw and dh:
                margin = 320  # headroom for title bar / taskbar
                scale = min(1.0, (dw - margin) / C.WINDOW_W, (dh - margin) / C.WINDOW_H)

                if scale < 1.0:
                    win_w = max(C.WIDTH, int(C.WINDOW_W * scale))
                    win_h = max(C.HEIGHT, int(C.WINDOW_H * scale))

            self.screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)

        self.clock = pygame.time.Clock()

        self.sound = SoundBank()
        self.starfield = Starfield()
        self.effects = Effects()
        self.fleet = Fleet()
        self.levels = LevelManager()
        self.powerups = PowerupManager()
        self.hud = HUD()

        self.mode = 1  # 1 or 2 players
        self.players = []
        self.state = MENU
        self.menu_select = 1
        self.paused = False
        self.highscores = self._load_highscores()
        self.highscore_flag = False
        self.state_time = 0.0
        self.selftest_kills = 0
        self._selftest_frames = 0
        self._last_streak_sound = {}

    def _load_highscores(self) -> dict:
        '''
        Load high scores from the save file (empty dict if missing).

        Returns:
            High scores dict keyed by player index.
        '''
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), C.HIGHSCORE_FILE)

        try:
            with open(path) as f:
                data = json.load(f)

            return {'1p': int(data.get('1p', 0)), '2p': int(data.get('2p', 0))}
        except (OSError, ValueError, TypeError):
            return {'1p': 0, '2p': 0}

    def _save_highscores(self) -> None:
        '''Persist the current high scores to the save file.'''
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), C.HIGHSCORE_FILE)

        try:
            with open(path, 'w') as f:
                json.dump(self.highscores, f, indent=2)
        except OSError:
            pass

    def start_game(self) -> None:
        '''Start a new game for the selected number of players.'''
        self.players = [Player(0)] + ([Player(1)] if self.mode == 2 else [])
        self.fleet = Fleet()
        self.powerups.reset()
        self.effects = Effects()
        self.levels.start()

        self.highscore_flag = False
        self.state = INTRO
        self.state_time = 0.0

    def to_menu(self) -> None:
        '''Return to the main menu, resetting per-game state.'''
        self.state = MENU
        self.state_time = 0.0

    def quit(self) -> None:
        '''Set the running flag to False to end the main loop.'''
        self.running = False

    def handle_events(self) -> None:
        '''Process window close, pause, quit, and menu navigation keys.'''
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.quit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.quit()
                elif ev.key == pygame.K_m:
                    self.sound.muted = not self.sound.muted
                elif ev.key == pygame.K_p:
                    if self.state == PLAYING:
                        self.paused = not self.paused
                elif self.state == MENU:
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        self.menu_select = 2 if self.menu_select == 1 else 1
                        self.sound.play('ui')
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_select = 1 if self.menu_select == 2 else 2
                        self.sound.play('ui')
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.mode = self.menu_select
                        self.sound.play('ui')
                        self.start_game()
                elif self.state == GAME_OVER:
                    if ev.key == pygame.K_RETURN:
                        self.sound.play('ui')
                        self.to_menu()
                elif self.state == PLAYING and not self.selftest and not self.paused:
                    if ev.key == pygame.K_UP:
                        self.players[0].bomb_fan(self.sound, self.effects)
                    elif ev.key == pygame.K_w and len(self.players) > 1:
                        self.players[1].bomb_fan(self.sound, self.effects)
                elif self.state == PLAYING and self.selftest:
                    pass  # selftest drives itself

    def _input_dirs(self) -> tuple:
        '''
        Read the current keyboard state for both players.

        Returns:
            (d1, d2): per-player horizontal direction (-1/0/1).
        '''
        keys = pygame.key.get_pressed()

        d1 = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
        d2 = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)

        return d1, d2

    def _collisions(self, dt: float) -> None:
        '''
        Resolve bullets-vs-enemies, enemies-vs-players, and
        powerup pickups.

        Args:
            dt: frame delta in seconds.
        '''
        # player bullets vs enemies
        for p in self.players:
            for b in p.bullets:
                if not b.alive:
                    continue

                br = b.rect()

                for e in self.fleet.enemies:
                    if e.state == 'dead' or (e.state == 'entry' and not e.entry_started):
                        continue

                    if br.colliderect(e.rect()):
                        b.alive = False
                        pts = self.fleet.hit_enemy(e, self.effects, self.sound)

                        if pts > 0:
                            p.score += pts * p.multiplier_value
                            p.streak += 1
                            new_mult = p.multiplier_value

                            if new_mult != self._last_streak_sound.get(p.index, 0):
                                self.sound.play_streak(new_mult)
                                self._last_streak_sound[p.index] = new_mult

                            self.effects.popup(
                                e.x, e.y, str(pts * p.multiplier_value),
                                C.WHITE if p.index == 0 else C.CYAN)

                            self.powerups.maybe_drop(e.x, e.y, e.etype)
                            self.selftest_kills += 1

                        break

        # enemy bullets vs players
        for b in self.fleet.bullets:
            if not b.alive:
                continue

            br = b.rect()

            for p in self.players:
                if not p.alive or p.invuln > 0:
                    continue

                pr = pygame.Rect(int(p.x - C.PLAYER_W / 2), int(p.y - C.PLAYER_H / 2),
                                 C.PLAYER_W, C.PLAYER_H)

                if br.colliderect(pr):
                    b.alive = False
                    died = p.hit(self.effects, self.sound)
                    self._last_streak_sound[p.index] = 0

                    if died:
                        self.fleet.scatter_divers()

                    break

        # enemy ships vs players (ramming)
        for e in self.fleet.enemies:
            if e.state != 'dive':
                continue

            er = e.rect()

            for p in self.players:
                if not p.alive or p.invuln > 0:
                    continue

                pr = pygame.Rect(int(p.x - C.PLAYER_W / 2), int(p.y - C.PLAYER_H / 2),
                                 C.PLAYER_W, C.PLAYER_H)

                if er.colliderect(pr):
                    died = p.hit(self.effects, self.sound)
                    self._last_streak_sound[p.index] = 0
                    pts = self.fleet.hit_enemy(e, self.effects, self.sound)

                    if pts > 0:
                        p.score += pts * p.multiplier_value
                        self.powerups.maybe_drop(e.x, e.y, e.etype)

                    if died:
                        self.fleet.scatter_divers()

    def update(self, dt: float) -> None:
        '''
        Advance one frame of gameplay (players, fleet, powerups,
        effects, and wave progression).

        Args:
            dt: frame delta in seconds.
        '''
        self.state_time += dt
        self.starfield.update(dt, 1.6 if self.state == PLAYING else 1.0)
        self.effects.update(dt)

        if self.state == MENU:
            if self.selftest:
                self.start_game()

            return

        if self.state == INTRO:
            if self.state_time >= 2.2:
                self.state = PLAYING
                self.state_time = 0.0

            return

        if self.state == GAME_OVER:
            if self.selftest:
                self.quit()

            return

        if self.state != PLAYING or self.paused:
            return

        # --- playing ---
        self.levels.update(dt, self.fleet, self.sound)
        phase = self.levels.phase

        # Keep the fleet updating in every phase. During 'clear' and
        # 'intro' no enemies are alive, but in-flight enemy bullets must
        # keep falling (and cull off-screen) instead of freezing mid-air
        # between waves.
        self.fleet.update(dt, self.players, self.sound)

        if phase == 'active':
            self.fleet.formation_fire(self.players, dt)

        d1, d2 = self._input_dirs()

        for i, p in enumerate(self.players):
            d = d1 if i == 0 else d2
            p.update(dt, d, self.sound)

        self.powerups.update(dt, self.players, self.sound, self.effects)
        self._collisions(dt)

        # game over?
        if all(p.lives <= 0 and not p.alive for p in self.players):
            self._finish_game()

    def _finish_game(self) -> None:
        '''Enter the game-over state and persist the high scores.'''
        key = f'{self.mode}p'
        total = sum(p.score for p in self.players)

        if total > self.highscores[key]:
            self.highscores[key] = total
            self.highscore_flag = True
            self._save_highscores()

        self.state = GAME_OVER
        self.state_time = 0.0
        self.sound.play('player_death', 0.8)

    def _selftest_advance(self, dt: float) -> None:
        '''Drive the game through menu->level1->combat->clear->game over.'''
        if self.state == PLAYING:
            phase = self.levels.phase

            if phase == 'active':
                # simulate combat: kill a couple of live enemies each frame
                alive = [e for e in self.fleet.enemies if e.state != 'dead']

                for _ in range(min(2, len(alive))):
                    e = random.choice(alive)
                    alive.remove(e)
                    p = self.players[0]
                    pts = self.fleet.hit_enemy(e, self.effects, self.sound)

                    if pts > 0:
                        p.score += pts * p.multiplier_value
                        p.streak += 1
                        self.powerups.maybe_drop(e.x, e.y, e.etype)
                        self.selftest_kills += 1

                # once level 1 is cleared and a new wave begins, end the run
                if self.levels.level >= 2:
                    for p in self.players:
                        p.alive = False
                        p.lives = 0

        # safety cap
        self._selftest_frames += 1

        if self._selftest_frames > C.FPS * 120:
            print('SELFTEST TIMEOUT at state', self.state)
            self.quit()

    def draw(self) -> None:
        '''Render the current frame for the active game state.'''
        # Draw the whole frame into the logical-resolution world surface,
        # then upscale it 2x to the display window.
        surf = self.world
        self.starfield.draw(surf)
        ox, oy = self.effects.offset()

        if self.state == MENU:
            self.hud.draw_menu(surf, self.highscores, self.menu_select)
            self._present()

            return

        # world (shaken)
        self.fleet.draw(surf, ox, oy)

        for p in self.players:
            p.draw(surf, ox, oy)

        for p in self.players:
            for b in p.bullets:
                b.draw(surf, ox, oy)

        self.powerups.draw(surf, self.hud.font_m, ox, oy)
        self.effects.draw(surf, ox, oy, self.hud.font_s)

        if self.state == INTRO:
            self.hud.draw_intro(surf, self.levels.level, self.levels.params)
        elif self.state == PLAYING:
            self.hud.draw_top(surf, self.players, self.levels.level, self.highscores)

            if self.paused:
                self.hud.draw_pause(surf)
        elif self.state == GAME_OVER:
            self.hud.draw_top(surf, self.players, self.levels.level, self.highscores)
            self.hud.draw_game_over(surf, self.players, self.highscore_flag)

        self._present()

    def _present(self) -> None:
        '''Upscale the logical frame to the window and blit it.'''
        pygame.transform.scale(self.world, self.screen.get_size(), self.screen)
        pygame.display.flip()

    def run(self) -> None:
        '''Run the main loop at 60 FPS until the game is quit.'''
        self.running = True

        while self.running:
            dt = min(self.clock.tick(C.FPS) / 1000.0, 0.05)
            self.handle_events()

            if self.selftest:
                self._selftest_advance(dt)

            self.update(dt)
            self.draw()

        pygame.quit()


def main() -> None:
    '''Parse CLI flags and launch the game.'''
    selftest = '--selftest' in sys.argv
    fullscreen = '--fullscreen' in sys.argv
    game = Game(selftest=selftest, fullscreen=fullscreen)

    if selftest:
        # force a deterministic-ish seed and run until it reaches game over
        # + menu
        random.seed(42)
        game.run()

        # selftest passes when the loop exits cleanly after reaching game
        # over
        if game.state in (MENU, GAME_OVER):
            print('SELFTEST OK')
        else:
            print('SELFTEST FAIL: ended in state', game.state)
            sys.exit(1)
    else:
        game.run()


if __name__ == '__main__':
    main()
