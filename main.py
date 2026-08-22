#!/usr/bin/env python3
"""GALAGA — a colorful co-op arcade shooter in pygame.

Run:      python main.py
Fullscr:  python main.py --fullscreen  (fills the monitor, fits any screen)
Selftest: python main.py --selftest   (headless, prints SELFTEST OK)

Controls
  P1: A/D move, SPACE fire
  P2: LEFT/RIGHT move, L fire
  P pause, Enter confirm, Esc quit
"""

import json
import os
import random
import sys

import pygame

from galaga import config as C
from galaga.enemies import Fleet
from galaga.hud import HUD
from galaga.levels import LevelManager
from galaga.particles import Effects
from galaga.player import Player
from galaga.powerups import PowerupManager
from galaga.sound import SoundBank
from galaga.starfield import Starfield

# Game states
MENU = "menu"
INTRO = "intro"
PLAYING = "playing"
GAME_OVER = "game_over"


class Game:
    def __init__(self, selftest=False, fullscreen=False):
        self.selftest = selftest
        if selftest:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

        pygame.init()
        pygame.display.set_caption(C.TITLE)
        # The game logic and all drawing happen in a logical C.WIDTH x C.HEIGHT
        # space; the whole frame is then upscaled by UI_SCALE (2x) to the real
        # window so that every sprite, bullet, particle and HUD element is
        # uniformly 2x larger.
        self.world = pygame.Surface((C.WIDTH, C.HEIGHT))
        flags = 0
        if fullscreen:
            flags |= pygame.FULLSCREEN | pygame.SCALED
        self.screen = pygame.display.set_mode((C.WINDOW_W, C.WINDOW_H), flags)
        self.clock = pygame.time.Clock()

        self.sound = SoundBank()
        self.starfield = Starfield()
        self.effects = Effects()
        self.fleet = Fleet()
        self.levels = LevelManager()
        self.powerups = PowerupManager()
        self.hud = HUD()

        self.mode = 1            # 1 or 2 players
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

    # ------------------------------------------------------------------
    # highscores
    # ------------------------------------------------------------------
    def _load_highscores(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), C.HIGHSCORE_FILE)
        try:
            with open(path) as f:
                data = json.load(f)
            return {"1p": int(data.get("1p", 0)), "2p": int(data.get("2p", 0))}
        except (OSError, ValueError, TypeError):
            return {"1p": 0, "2p": 0}

    def _save_highscores(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), C.HIGHSCORE_FILE)
        try:
            with open(path, "w") as f:
                json.dump(self.highscores, f, indent=2)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # flow
    # ------------------------------------------------------------------
    def start_game(self):
        self.players = [Player(0)] + ([Player(1)] if self.mode == 2 else [])
        self.fleet = Fleet()
        self.powerups.reset()
        self.effects = Effects()
        self.levels.start()
        self.highscore_flag = False
        self.state = INTRO
        self.state_time = 0.0

    def to_menu(self):
        self.state = MENU
        self.state_time = 0.0

    def quit(self):
        self.running = False

    # ------------------------------------------------------------------
    # input
    # ------------------------------------------------------------------
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.quit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.quit()
                elif ev.key == pygame.K_p:
                    if self.state == PLAYING:
                        self.paused = not self.paused
                elif self.state == MENU:
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        self.menu_select = 2 if self.menu_select == 1 else 1
                        self.sound.play("ui")
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_select = 1 if self.menu_select == 2 else 2
                        self.sound.play("ui")
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.mode = self.menu_select
                        self.sound.play("ui")
                        self.start_game()
                elif self.state == GAME_OVER:
                    if ev.key == pygame.K_RETURN:
                        self.sound.play("ui")
                        self.to_menu()
                elif self.state == PLAYING and self.selftest:
                    pass  # selftest drives itself

    def _input_dirs(self):
        keys = pygame.key.get_pressed()
        d1 = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
        f1 = keys[pygame.K_SPACE]
        d2 = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
        f2 = keys[pygame.K_l]
        return d1, f1, d2, f2

    # ------------------------------------------------------------------
    # collisions
    # ------------------------------------------------------------------
    def _collisions(self, dt):
        # player bullets vs enemies
        for p in self.players:
            for b in p.bullets:
                if not b.alive:
                    continue
                br = b.rect()
                for e in self.fleet.enemies:
                    if e.state == "dead" or (e.state == "entry" and not e.entry_started):
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
                            self.effects.popup(e.x, e.y, str(pts * p.multiplier_value),
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
                    p.hit(self.effects, self.sound)
                    self._last_streak_sound[p.index] = 0
                    break
        # enemy ships vs players (ramming)
        for e in self.fleet.enemies:
            if e.state != "dive":
                continue
            er = e.rect()
            for p in self.players:
                if not p.alive or p.invuln > 0:
                    continue
                pr = pygame.Rect(int(p.x - C.PLAYER_W / 2), int(p.y - C.PLAYER_H / 2),
                                 C.PLAYER_W, C.PLAYER_H)
                if er.colliderect(pr):
                    p.hit(self.effects, self.sound)
                    self._last_streak_sound[p.index] = 0
                    pts = self.fleet.hit_enemy(e, self.effects, self.sound)
                    if pts > 0:
                        p.score += pts * p.multiplier_value
                        self.powerups.maybe_drop(e.x, e.y, e.etype)

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------
    def update(self, dt):
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

        # Keep the fleet updating in every phase. During "clear" and "intro"
        # no enemies are alive, but in-flight enemy bullets must keep falling
        # (and cull off-screen) instead of freezing mid-air between waves.
        self.fleet.update(dt, self.players, self.effects, self.sound)
        if phase == "active":
            self.fleet.formation_fire(self.players, self.sound, dt)

        d1, f1, d2, f2 = self._input_dirs()
        for i, p in enumerate(self.players):
            d = d1 if i == 0 else d2
            f = f1 if i == 0 else f2
            p.update(dt, d, f, self.sound)

        self.powerups.update(dt, self.players, self.sound, self.effects)
        self._collisions(dt)

        # game over?
        if all(p.lives <= 0 and not p.alive for p in self.players):
            self._finish_game()

    def _finish_game(self):
        key = f"{self.mode}p"
        total = sum(p.score for p in self.players)
        if total > self.highscores[key]:
            self.highscores[key] = total
            self.highscore_flag = True
            self._save_highscores()
        self.state = GAME_OVER
        self.state_time = 0.0
        self.sound.play("player_death", 0.8)

    # ------------------------------------------------------------------
    # selftest: force the full flow deterministically
    # ------------------------------------------------------------------
    def _selftest_advance(self, dt):
        """Drive the game through menu->level1->combat->clear->game over."""
        if self.state == PLAYING:
            phase = self.levels.phase
            if phase == "active":
                # simulate combat: kill a couple of live enemies each frame
                alive = [e for e in self.fleet.enemies if e.state != "dead"]
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
            print("SELFTEST TIMEOUT at state", self.state)
            self.quit()

    # ------------------------------------------------------------------
    # draw
    # ------------------------------------------------------------------
    def draw(self):
        # Draw the whole frame into the logical-resolution world surface, then
        # upscale it 2x to the display window.
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

    def _present(self):
        """Upscale the logical frame by UI_SCALE and blit it to the window."""
        pygame.transform.scale(self.world, (C.WINDOW_W, C.WINDOW_H), self.screen)
        pygame.display.flip()

    # ------------------------------------------------------------------
    # main loop
    # ------------------------------------------------------------------
    def run(self):
        self.running = True
        while self.running:
            dt = min(self.clock.tick(C.FPS) / 1000.0, 0.05)
            self.handle_events()

            if self.selftest:
                self._selftest_advance(dt)

            self.update(dt)
            self.draw()

        pygame.quit()


def main():
    selftest = "--selftest" in sys.argv
    fullscreen = "--fullscreen" in sys.argv
    game = Game(selftest=selftest, fullscreen=fullscreen)
    if selftest:
        # force a deterministic-ish seed and run until it reaches game over + menu
        random.seed(42)
        game.run()
        # selftest passes when the loop exits cleanly after reaching game over
        if game.state in (MENU, GAME_OVER):
            print("SELFTEST OK")
        else:
            print("SELFTEST FAIL: ended in state", game.state)
            sys.exit(1)
    else:
        game.run()


if __name__ == "__main__":
    main()
