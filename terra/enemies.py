'''Enemy fleet: types, formation, entry choreography, and dive-bomb AI.

This is the heart of the game. A :class:`Fleet` owns 40 enemies and drives:
  * the whole-formation side-to-side wobble,
  * the staggered fly-in (choreographed entry) at the start of each level,
  * periodic dive-bomb waves (V-formations and single runs) that curve
    toward the player and fire on the way down,

  * re-entry of divers back into the formation, and
  * the enemy bullet list.

'''

import math
import random

import pygame

from . import config as C


# Enemy states
ENTRY = 'entry'
FORMATION = 'formation'
DIVE = 'dive'
REENTER = 'reenter'
DEAD = 'dead'


class Enemy:
    __slots__ = (
        'etype', 'slot_index', 'slot', 'state', 'x', 'y', 'vx', 'vy',
        'anim_t', 'entry_t', 'entry_start', 'entry_duration', 'entry_started',
        'dive_delay', 'dive_target_offset', 'dive_fire_t', 'dive_aim_t',
        'dive_target', 'hits', 'split', 'elite', 'p0', 'p1', 'spiral_side', 'flash',
    )

    def __init__(self, etype: str, slot_index: int, slot: tuple,
                 level: int = 1):
        '''
        Create an enemy of the given type in its formation slot.

        Args:
            etype: enemy type ('bee', 'hornet', or 'boss').
            slot_index: index of this enemy's formation slot.
            slot: (col, row) of the formation slot.
            level: 1-based level (bosses gain extra hits over time).
        '''
        self.etype = etype
        self.slot_index = slot_index
        self.slot = slot
        self.state = ENTRY

        self.x = 0.0
        self.y = -60.0
        self.vx = 0.0
        self.vy = 0.0

        self.anim_t = random.uniform(0, math.tau)

        self.entry_t = 0.0
        self.entry_start = 0.0
        self.entry_duration = 1.0
        self.entry_started = False

        self.dive_delay = 0.0
        self.dive_target_offset = 0.0
        self.dive_fire_t = random.uniform(0.2, 0.8)
        self.dive_aim_t = 0.0
        self.dive_target = None

        # elite bosses keep gaining hit points as the levels climb
        if etype == 'boss':
            self.hits = min(C.ELITE_BOSS_MAX_HITS,
                            2 + max(1, level) // C.ELITE_BOSS_STEP)
        else:
            self.hits = 1
        self.elite = etype == 'boss' and self.hits > 2
        self.split = False

        self.p0 = (0.0, 0.0)
        self.p1 = (0.0, 0.0)

        self.spiral_side = 1 if random.random() < 0.5 else -1
        self.flash = 0.0

    def size(self) -> int:
        '''Side length in px of this enemy's hitbox.'''
        if self.etype == 'boss':
            return 34

        if self.etype == 'hornet':
            return 24

        return 20

    def rect(self) -> pygame.Rect:
        '''Current screen-space hitbox rect.'''
        s = self.size()
        w = s + 6
        h = s

        return pygame.Rect(int(self.x - w / 2), int(self.y - h / 2), w, h)

    def score(self, diving: bool) -> int:
        '''
        Points awarded for this kill.

        Args:
            diving: double the base score when the enemy is diving.

        Returns:
            The score value.
        '''
        base = {'bee': C.SCORE_BEE, 'hornet': C.SCORE_HORNET, 'boss': C.SCORE_BOSS}[self.etype]

        if diving:
            base *= C.DIVE_BONUS_MULTIPLIER

        return base

    def color(self) -> tuple:
        '''Primary sprite color for this enemy type.'''
        return {'bee': C.BEE_COLOR, 'hornet': C.HORNET_COLOR, 'boss': C.BOSS_COLOR}[self.etype]

    def slot_world(self, wobble_x: float) -> tuple:
        '''
        World-space position of this enemy's formation slot.

        Args:
            wobble_x: current formation wobble offset in px.

        Returns:
            (x, y) world position.
        '''
        return C.slot_to_world(self.slot_index, self.slot, wobble_x)

    def _begin_entry(self, wobble_x: float, params: dict) -> None:
        '''
        Start the curved entry flight toward the formation slot.

        Args:
            wobble_x: current formation wobble offset in px.
            params: level parameters dict from config.level_params.
        '''
        self.entry_started = True
        self.entry_duration = params['entry_path_time']
        side = self.spiral_side
        sx, sy = self.slot_world(wobble_x)

        if self.etype == 'boss':
            self.entry_duration = params['entry_path_time'] + 0.8
            # off-screen start so the boss doesn't pop in at the corner
            self.p0 = (sx + side * random.uniform(140, 220), -70.0)
            self.p1 = (C.WIDTH / 2 + side * random.uniform(120, 300), random.uniform(40, 100))

            return

        # quadratic bezier start points (alternate sides for a nice spread)
        self.p0 = (sx + side * random.uniform(120, 260), -50.0)
        self.p1 = (C.WIDTH / 2 + side * random.uniform(120, 320), random.uniform(60, 140))

    def update_entry(self, dt: float, wobble_x: float) -> bool:
        '''
        Advance the entry flight; snap into formation when close.

        Args:
            dt: frame delta in seconds.
            wobble_x: current formation wobble offset in px.

        Returns:
            True once the enemy has joined the formation.
        '''
        if not self.entry_started:
            self.x, self.y = self.p0 if self.p0 else (self.x, -60.0)

            return False

        self.entry_t += dt / self.entry_duration
        t = min(1.0, self.entry_t)
        tx, ty = self.slot_world(wobble_x)

        if self.etype == 'boss':
            # spiral into the slot
            ang = self.spiral_side * (3.5 - 3.5 * t) * math.pi
            rad = (1 - t) * 260.0
            self.x = tx + math.cos(ang) * rad
            self.y = ty + math.sin(ang) * rad * 0.6 - (1 - t) * 120.0
        else:
            # quadratic bezier
            u = 1 - t
            self.x = u * u * self.p0[0] + 2 * u * t * self.p1[0] + t * t * tx
            self.y = u * u * self.p0[1] + 2 * u * t * self.p1[1] + t * t * ty

        if t >= 1.0:
            self.state = FORMATION
            self.x, self.y = tx, ty

            return True

        return False


class EnemyBullet:
    __slots__ = ('x', 'y', 'vx', 'vy', 'alive', 'homing')

    def __init__(self, x: float, y: float, vx: float, vy: float, homing: bool = False):
        '''
        Create an enemy bullet.

        Args:
            x: spawn x in world px.
            y: spawn y in world px.
            vx: horizontal velocity in px/s.
            vy: vertical velocity in px/s.
            homing: steer toward the nearest player each frame.
        '''
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.alive = True
        self.homing = homing

    def update(self, dt: float, players: list = None) -> None:
        '''
        Move the bullet, optionally homing toward the nearest player.

        Args:
            dt: frame delta in seconds.
            players: list of Player objects to home toward.
        '''
        # only chase players that can actually be hit right now (a ship
        # that just respawned blinks and is immune for a few seconds)
        if self.homing and players:
            vulnerable = [p for p in players if p.alive and p.invuln <= 0]

            if vulnerable:
                tgt = random.choice(vulnerable)
                dx, dy = tgt.x - self.x, tgt.y - self.y
                d = math.hypot(dx, dy) or 1.0
                sp = math.hypot(self.vx, self.vy)
                self.vx += (dx / d - self.vx / sp) * 1.6 * dt
                self.vy += (dy / d - self.vy / sp) * 1.6 * dt
                self.vx, self.vy = _rescale(self.vx, self.vy, sp)

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y > C.HEIGHT + 20 or self.x < -20 or self.x > C.WIDTH + 20 or self.y < -40:
            self.alive = False

    def rect(self) -> pygame.Rect:
        '''Current screen-space hitbox rect.'''
        return pygame.Rect(int(self.x - 3), int(self.y - C.ENEMY_BULLET_H / 2),
                           6, C.ENEMY_BULLET_H)

    def draw(self, surf: pygame.Surface, ox: float, oy: float) -> None:
        '''
        Draw the bullet.

        Args:
            surf: surface to draw on.
            ox: screen-space camera offset x in px.
            oy: screen-space camera offset y in px.
        '''
        x, y = int(self.x + ox), int(self.y + oy)
        pygame.draw.circle(surf, C.ORANGE, (x, y), 4)
        pygame.draw.rect(surf, C.YELLOW, (x - 1, y - 6, 3, 12))


def _rescale(vx: float, vy: float, sp: float) -> tuple:
    '''
    Scale a velocity vector to the given speed.

    Args:
        vx: current x velocity in px/s.
        vy: current y velocity in px/s.
        sp: target speed in px/s.

    Returns:
        (vx, vy) rescaled velocity.
    '''
    m = math.hypot(vx, vy) or 1.0

    return vx / m * sp, vy / m * sp


class Fleet:
    def __init__(self):
        '''Create an empty fleet (no enemies or bullets).'''
        self.enemies = []
        self.bullets = []
        self.wobble_t = 0.0
        self.fleet_time = 0.0
        self.dive_timer = 2.0
        self.params = C.level_params(1)
        self.level = 1

    def setup(self, level: int) -> None:
        '''
        Populate the fleet for a level.

        Args:
            level: 1-based level number.
        '''
        self.level = level
        self.params = C.level_params(level)
        self.wobble_t = 0.0
        self.fleet_time = 0.0
        self.bullets.clear()
        self.dive_timer = 1.6

        self.enemies = []
        slots = C.fleet_composition(level)
        n_bosses = sum(1 for s in slots if s[0] == 'boss')

        for i, (etype, col, row) in enumerate(slots):
            e = Enemy(etype, i, (etype, col, row), level)
            self._assign_entry(e, i, level, n_bosses)
            self.enemies.append(e)

    def _assign_entry(self, e: Enemy, i: int, level: int, n_bosses: int) -> None:
        '''
        Schedule an enemy's entry flight with a staggered delay.

        Args:
            e: the Enemy to schedule.
            i: index of the enemy in the formation.
            level: 1-based level number (tightens the stagger).
            n_bosses: number of bosses in this fleet (entry stagger).
        '''
        delay = self.params['entry_delay']

        if e.etype == 'boss':
            # bosses enter first, one after another (count scales with level)
            e.entry_start = 0.5 + (i % max(1, n_bosses)) * 0.28
        else:
            # group the non-boss enemies into waves of 6
            non_boss_index = i - n_bosses
            group = non_boss_index // 6
            e.entry_start = 0.9 + group * delay + random.uniform(0.0, 0.12)

        # precompute an off-screen start position so it doesn't pop in
        # at (0,0)
        e._begin_entry(0.0, self.params)
        e.entry_started = False  # wait until its entry_start time
        e.x, e.y = e.p0

    @property
    def wobble_x(self) -> float:
        '''Current horizontal formation offset in px (wobble + slow drift).'''
        wobble = (math.sin(self.wobble_t * self.params['formation_wobble_speed'])
                  * self.params['formation_wobble_amp'])
        # slow drift keeps the formation mobile even when wobble is small
        drift = math.sin(self.fleet_time * C.FORMATION_DRIFT_SPEED) * C.FORMATION_DRIFT_AMP
        return wobble + drift

    def alive_enemies(self) -> list:
        '''Enemies that are not dead or off-screen.'''
        return [e for e in self.enemies if e.state != DEAD]

    def all_in_formation(self) -> bool:
        '''True when every surviving enemy is in its formation slot.'''
        # DEAD enemies count as 'settled' — a kill during the entry fly-in
        # must not stall the entry->active transition (it used to lock the
        # level in 'entry' forever, so no further waves ever started).
        return all(e.state in (FORMATION, DIVE, REENTER, DEAD) for e in self.enemies)

    def diving_count(self) -> int:
        '''Number of enemies currently dive-bombing.'''
        return sum(1 for e in self.enemies if e.state == DIVE)

    def scatter_divers(self) -> None:
        '''Send every dive-bomber back to its slot (a player was destroyed).'''
        for e in self.enemies:
            if e.state == DIVE:
                e.state = REENTER
                e.entry_t = 0.0
                e.dive_target = None
                sx, _sy = e.slot_world(0)
                e.p0 = (e.x, e.y)
                e.p1 = (sx + e.spiral_side * 160, max(60.0, e.y - 200.0))

    def update(self, dt: float, players: list, effects: 'Effects', sound: 'SoundBank') -> None:
        '''
        Advance the fleet: entries, wobble, dive waves, and bullets.

        Args:
            dt: frame delta in seconds.
            players: list of Player objects.
            effects: Effects instance for explosions.
            sound: SoundBank instance.
        '''
        self.wobble_t += dt
        self.fleet_time += dt
        wx = self.wobble_x

        # --- entry ---
        for e in self.enemies:
            if e.state == ENTRY:
                if not e.entry_started and self.fleet_time >= e.entry_start:
                    e._begin_entry(wx, self.params)

                e.update_entry(dt, wx)

        # --- formation & dive ---
        for e in self.enemies:
            if e.state == FORMATION:
                e.x, e.y = e.slot_world(wx)
                e.anim_t += dt * 6
            elif e.state == DIVE:
                self._update_dive(e, dt, players, effects, sound)
            elif e.state == REENTER:
                self._update_reenter(e, dt, wx)

        # --- dive wave scheduling ---
        # no new dive waves while every player is dead or still blinking
        # (immune): the timer holds at zero so the first wave fires the
        # moment a player becomes vulnerable again
        vulnerable = [p for p in players if p.alive and p.invuln <= 0]

        if self.all_in_formation():
            self.dive_timer -= dt

            if self.dive_timer <= 0 and vulnerable:
                self._start_dive_wave(players, sound)
                self.dive_timer = self.params['dive_interval'] * random.uniform(0.75, 1.25)
            elif self.dive_timer <= 0:
                self.dive_timer = 0.0

        # --- enemy bullets ---
        for b in self.bullets:
            b.update(dt, players)

        self.bullets = [b for b in self.bullets if b.alive]

    def _start_dive_wave(self, players: list, sound: 'SoundBank') -> None:
        '''
        Pick up to the dive cap of formation enemies to dive-bomb.

        Args:
            players: list of Player objects to target.
            sound: SoundBank instance for dive sounds.
        '''
        if self.diving_count() >= self.params['max_divers']:
            return

        candidates = [e for e in self.enemies if e.state == FORMATION]

        if not candidates:
            return

        # Decide wave shape: a V of 3-5, a pincer V from the wings,
        # or a single/double run
        r = random.random()

        if r < self.params['dive_pincer_chance']:
            shape = 'pincer'
            n = random.randint(3, 5)
        elif r < self.params['dive_pincer_chance'] + 0.45:
            shape = 'v'
            n = random.randint(3, 5)
        else:
            shape = 'run'
            n = random.randint(1, 2)

        n = max(1, min(n, len(candidates)))

        if shape == 'pincer':
            left = [e for e in candidates if e.slot[1] < C.FORMATION_COLS / 2]
            right = [e for e in candidates if e.slot[1] >= C.FORMATION_COLS / 2]
            half = (n + 1) // 2
            wing = random.choice([left, right])
            other = right if wing is left else left
            if len(wing) < half or len(other) < n - half:
                wave = random.sample(candidates, n)
            else:
                wave = (random.sample(wing, half)
                        + random.sample(other, n - half))
        else:
            wave = random.sample(candidates, n)

        n = max(1, min(len(wave), self.params['max_divers']))
        wave = wave[:n]
        mid = len(wave) // 2
        spread = self.params['dive_spread']

        for i, e in enumerate(wave):
            e.state = DIVE
            e.dive_delay = 0.0 if shape == 'run' else abs(i - mid) * 0.12
            e.dive_target_offset = (i - mid) * spread if shape != 'run' else 0.0
            e.dive_aim_t = 0.0
            e.vx = 0.0
            e.vy = 60.0
            e.dive_fire_t = random.uniform(0.3, 0.9)

        sound.play('whoosh', 0.5)

    def _update_dive(self, e: Enemy, dt: float, players: list,
                     effects: 'Effects', sound: 'SoundBank') -> None:
        '''
        Advance a dive-bomber; boss splits and may fire while diving.

        Args:
            e: the diving Enemy.
            dt: frame delta in seconds.
            players: list of Player objects.
            effects: Effects instance for explosions.
            sound: SoundBank instance.
        '''

        if e.dive_delay > 0:
            e.dive_delay -= dt
            e.y += e.vy * dt * 0.4

            return

        # only target players that can actually be hit right now (a ship
        # that just respawned blinks and is immune for a few seconds); a
        # diver with no legal target flies straight through
        vulnerable = [p for p in players if p.alive and p.invuln <= 0]

        # re-aim on a cadence (with jitter) so the dive keeps a committed
        # curve instead of re-locking every frame; a target that is dead
        # or has just become immune (blinking) is dropped immediately
        e.dive_aim_t -= dt

        if (e.dive_aim_t <= 0 or e.dive_target is None
                or not (e.dive_target.alive and e.dive_target.invuln <= 0)):
            e.dive_target = random.choice(vulnerable) if vulnerable else None
            e.dive_aim_t = random.uniform(C.DIVE_REAIM_MIN, C.DIVE_REAIM_MAX)

        tgt = e.dive_target

        if tgt is not None and tgt.alive and tgt.invuln <= 0:
            # lead the target so the dive meets it where it will be
            dist = max(0.0, (C.HEIGHT - 60) - e.y)
            t = dist / max(1.0, self.params['dive_speed'])
            target_x = tgt.x + tgt.vx * t + e.dive_target_offset
            target_y = C.HEIGHT - 60.0
        else:
            # no legal target (player dead or blinking): fly straight
            # down and exit the screen, then re-enter the formation
            target_x = e.x
            target_y = C.HEIGHT + 80.0

        dx, dy = target_x - e.x, target_y - e.y
        d = math.hypot(dx, dy) or 1.0
        sp = self.params['dive_speed']
        desired_vx, desired_vy = dx / d * sp, dy / d * sp

        # steering toward desired velocity -> smooth curve
        turn = self.params['dive_turn']
        e.vx += (desired_vx - e.vx) * min(1.0, turn * dt)
        e.vy += (desired_vy - e.vy) * min(1.0, turn * dt)

        # bees wobble
        if e.etype == 'bee':
            e.x += math.sin(self.fleet_time * 8 + e.anim_t) * 40 * dt

        e.x += e.vx * dt
        e.y += e.vy * dt
        e.anim_t += dt * 10

        # fire while diving
        e.dive_fire_t -= dt

        if e.dive_fire_t <= 0 and vulnerable and e.y < C.HEIGHT - 120:
            self._fire_aimed(e, players, sound)
            e.dive_fire_t = random.uniform(0.5, 1.1)

        # exited off screen -> re-enter formation
        if e.y > C.HEIGHT + 30 or e.x < -40 or e.x > C.WIDTH + 40:
            e.state = REENTER
            e.entry_t = 0.0
            side = e.spiral_side
            sx, sy = e.slot_world(0)
            e.p0 = (sx + side * 160, -50)
            e.p1 = (C.WIDTH / 2 + side * 200, 90)

    def _update_reenter(self, e: Enemy, dt: float, wx: float) -> None:
        '''
        Advance the arc back toward the formation slot.

        Args:
            e: the re-entering Enemy.
            dt: frame delta in seconds.
            wx: current formation wobble offset in px.
        '''
        e.entry_t += dt / (self.params['entry_path_time'] * 0.8)
        t = min(1.0, e.entry_t)
        u = 1 - t
        tx, ty = e.slot_world(wx)
        e.x = u * u * e.p0[0] + 2 * u * t * e.p1[0] + t * t * tx
        e.y = u * u * e.p0[1] + 2 * u * t * e.p1[1] + t * t * ty
        e.anim_t += dt * 8

        if t >= 1.0:
            e.state = FORMATION
            e.x, e.y = tx, ty

    def _fire_aimed(self, e: Enemy, players: list, sound: 'SoundBank') -> None:
        '''
        Fire an aimed shot; terras may home, and shots may fan out 3-way.

        Args:
            e: the firing Enemy.
            players: list of Player objects to aim at.
            sound: SoundBank instance for the shot sound.
        '''
        alive = [p for p in players if p.alive]

        if not alive:
            return

        tgt = random.choice(alive)
        dx, dy = tgt.x - e.x, tgt.y - e.y
        d = math.hypot(dx, dy) or 1.0
        sp = self.params['enemy_bullet_speed']
        homing = (e.etype == 'boss'
                  and random.random() < self.params['boss_homing_chance']) or (
            e.etype == 'hornet'
            and random.random() < self.params['terra_homing_chance'])
        self.bullets.append(EnemyBullet(e.x, e.y + 10, dx / d * sp, dy / d * sp, homing))

        # 3-way spread: two extra bullets fanned around the aim direction;
        # bosses use their own (later-ramping) chance, others the base one
        chance = (self.params['boss_spread_chance'] if e.etype == 'boss'
                  else self.params['spread_chance'])

        if random.random() < chance:
            ang = math.atan2(dy, dx)

            for off in (-0.22, 0.22):
                a = ang + off
                self.bullets.append(EnemyBullet(
                    e.x, e.y + 10, math.cos(a) * sp, math.sin(a) * sp, False))

    def formation_fire(self, players: list, sound: 'SoundBank', dt: float) -> None:
        '''Formation fire: a stray aimed shot, or a coordinated row burst.'''
        if random.random() < self.params['enemy_fire_chance'] * dt * C.FORMATION_FIRE_RATE:
            cands = [e for e in self.enemies if e.state == FORMATION]

            if cands:
                if random.random() < self.params['formation_burst_chance']:
                    self._row_burst(cands, players, sound)
                else:
                    self._fire_aimed(random.choice(cands), players, sound)

    def _row_burst(self, cands: list, players: list, sound: 'SoundBank') -> None:
        '''
        Fire a coordinated volley from a single formation row.

        Args:
            cands: formation enemies eligible to fire.
            players: list of Player objects to aim at.
            sound: SoundBank instance for the shot sound.
        '''
        rows: dict = {}

        for e in cands:
            rows.setdefault(e.slot[2], []).append(e)

        row = random.choice(list(rows.values()))
        row.sort(key=lambda e: e.slot[1])
        n = min(len(row), self.params['formation_burst_shooters'])
        shooters = random.sample(row, n)

        for e in shooters:
            self._fire_aimed(e, players, sound)

    def hit_enemy(self, e: Enemy, effects: 'Effects', sound: 'SoundBank') -> int:
        '''Apply a hit to an enemy. Returns points scored (0 if still alive).'''
        if e.state == DEAD:
            return 0

        diving = e.state == DIVE  # capture before any state mutation
        e.hits -= 1

        if e.hits > 0:
            # boss first hit -> split
            e.split = True
            e.flash = 0.15
            effects.spark(e.x, e.y, e.color(), 14, 180, 0.4)
            sound.play('explosion_small')

            return 0

        # destroyed
        e.state = DEAD
        color = e.color()

        if e.etype == 'boss':
            effects.explosion(e.x, e.y, C.WHITE, 20, 200, 0.6, 3)
            effects.shake(C.BOSS_SHAKE_MAGNITUDE, C.BOSS_SHAKE_DURATION)
            effects.flash(color, 0.12)
            sound.play('explosion_boss')
        elif e.etype == 'hornet':
            effects.explosion(e.x, e.y, color, 26, 250, 0.6, 3)
            effects.shake(C.SHAKE_MAGNITUDE, C.SHAKE_DURATION)
            sound.play('explosion_small')
        else:
            effects.explosion(e.x, e.y, color, 18, 200, 0.5, 3)
            effects.spark(e.x, e.y, C.WHITE, 8, 140, 0.3)
            sound.play('explosion_small')

        return e.score(diving)

    def draw(self, surf: pygame.Surface, ox: float, oy: float) -> None:
        '''
        Draw all surviving enemies and enemy bullets.

        Args:
            surf: surface to draw on.
            ox: screen-space camera offset x in px.
            oy: screen-space camera offset y in px.
        '''
        for e in self.enemies:
            if e.state == DEAD:
                continue

            if e.state == ENTRY and not e.entry_started:
                continue

            self._draw_enemy(surf, e, ox, oy)

        for b in self.bullets:
            b.draw(surf, ox, oy)

    def _draw_enemy(self, surf: pygame.Surface, e: Enemy, ox: float, oy: float) -> None:
        '''
        Draw one enemy using the sprite for its type.

        Args:
            surf: surface to draw on.
            e: the Enemy to draw.
            ox: screen-space camera offset x in px.
            oy: screen-space camera offset y in px.
        '''
        x, y = int(e.x + ox), int(e.y + oy)

        if e.flash > 0:
            e.flash -= 0.016
            col = C.WHITE
        else:
            col = e.color()

        flap = math.sin(e.anim_t) * 0.5 + 0.5  # 0..1 wing flap

        if e.etype == 'bee':
            self._draw_bee(surf, x, y, col, flap)
        elif e.etype == 'hornet':
            self._draw_terra(surf, x, y, col, flap)
        else:
            self._draw_boss(surf, x, y, col, flap, e.split, e.elite)

    def _draw_bee(self, surf: pygame.Surface, x: int, y: int, col: tuple, flap: float) -> None:
        '''
        Draw a bee sprite (wings flap with the flap phase).

        Args:
            surf: surface to draw on.
            x: screen-space center x in px.
            y: screen-space center y in px.
            col: body color.
            flap: wing flap phase in [0, 1].
        '''
        # wings
        wing = int(6 + 5 * flap)
        pygame.draw.ellipse(surf, (200, 220, 255), (x - 12, y - 6 - wing, 9, wing + 6))
        pygame.draw.ellipse(surf, (200, 220, 255), (x + 3, y - 6 - wing, 9, wing + 6))

        # body
        pygame.draw.ellipse(surf, col, (x - 6, y - 8, 12, 18))

        # stripes
        pygame.draw.line(surf, C.DARK_RED, (x - 6, y - 2), (x + 6, y - 2), 2)
        pygame.draw.line(surf, C.DARK_RED, (x - 5, y + 3), (x + 5, y + 3), 2)

        # eyes
        pygame.draw.circle(surf, C.WHITE, (x - 3, y - 6), 1)
        pygame.draw.circle(surf, C.WHITE, (x + 3, y - 6), 1)

    def _draw_terra(self, surf: pygame.Surface, x: int, y: int, col: tuple, flap: float) -> None:
        '''
        Draw a terra sprite (wings flap with the flap phase).

        Args:
            surf: surface to draw on.
            x: screen-space center x in px.
            y: screen-space center y in px.
            col: body color.
            flap: wing flap phase in [0, 1].
        '''
        # side fins (flap)
        fin = int(4 + 6 * flap)
        pygame.draw.polygon(surf, C.BLUE, [(x - 8, y), (x - 8 - fin, y - 6), (x - 8 - fin, y + 4)])
        pygame.draw.polygon(surf, C.BLUE, [(x + 8, y), (x + 8 + fin, y - 6), (x + 8 + fin, y + 4)])

        # body
        pygame.draw.ellipse(surf, col, (x - 8, y - 10, 16, 20))

        # head
        pygame.draw.circle(surf, C.WHITE, (x, y - 8), 4)

        # tail
        pygame.draw.polygon(surf, col, [(x - 4, y + 8), (x, y + 14), (x + 4, y + 8)])

        # eyes
        pygame.draw.circle(surf, C.RED, (x - 2, y - 9), 1)
        pygame.draw.circle(surf, C.RED, (x + 2, y - 9), 1)

    def _draw_boss(self, surf: pygame.Surface, x: int, y: int, col: tuple,
                   flap: float, split: bool, elite: bool = False) -> None:
        '''
        Draw a boss sprite (wings flap; split state shown in red).

        Args:
            surf: surface to draw on.
            x: screen-space center x in px.
            y: screen-space center y in px.
            col: body color.
            flap: wing flap phase in [0, 1].
            split: boss has split and is flashing red.
            elite: multi-hit boss, tinted yellow.
        '''

        gap = 4 if split else 0
        body = C.YELLOW if elite else col

        # two halves
        for sgn in (-1, 1):
            hx = x + sgn * (4 + gap)
            # claw/wing
            wing = int(5 + 5 * flap)
            pygame.draw.ellipse(surf, C.PINK, (hx - 8 * sgn - (4 if sgn < 0 else 0),
                                               y - 4 - wing, 8, wing + 8))
            # body half
            pygame.draw.ellipse(surf, body, (hx - 6, y - 12, 12, 24))
            pygame.draw.ellipse(surf, C.DARK_RED, (hx - 4, y - 8, 8, 16))

        # central face
        pygame.draw.circle(surf, C.WHITE, (x, y - 6), 4)
        pygame.draw.circle(surf, C.YELLOW, (x - 2, y - 6), 1)
        pygame.draw.circle(surf, C.YELLOW, (x + 2, y - 6), 1)

        # mandibles
        pygame.draw.line(surf, body, (x - 3, y + 8), (x - 6, y + 14), 2)
        pygame.draw.line(surf, body, (x + 3, y + 8), (x + 6, y + 14), 2)
