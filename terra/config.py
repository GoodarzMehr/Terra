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

import math

############################## Display Window ################################

WIDTH, HEIGHT = 800, 600
UI_SCALE = 2
WINDOW_W, WINDOW_H = WIDTH * UI_SCALE, HEIGHT * UI_SCALE
FPS = 60
TITLE = 'TERRA'

################################## Palette ###################################

BLACK =      (  8,  10,  24)
DEEP_BLUE =  ( 16,  22,  48)
WHITE =      (240, 244, 252)
YELLOW =     (252, 220,  80)
ORANGE =     (252, 160,  60)
RED =        (252,  70,  70)
DARK_RED =   (150,  40,  50)
GREEN =      ( 90, 230, 120)
DARK_GREEN = ( 30, 120,  70)
CYAN =       ( 90, 220, 252)
BLUE =       ( 90, 140, 252)
MAGENTA =    (232, 110, 252)
PINK =       (252, 130, 200)
GRAY =       (140, 144, 160)
LIGHT_GRAY = (200, 204, 220)

# Enemy colors
BEE_COLOR = RED
TERRA_COLOR = CYAN
BOSS_COLOR = MAGENTA

############################## Player Physics ################################

PLAYER_SPEED = 380.0         # player's horizontal speed (px/s)
PLAYER_Y = HEIGHT - 40       # player's vertical position (px, fixed lane)
PLAYER_W, PLAYER_H = 30, 30  # player ship size (px)
PLAYER_FIRE_COOLDOWN = 0.24  # time between shots (seconds)
PLAYER_RAPID_COOLDOWN = 0.12 # time between shots when rapid-fire powerup is
                             # active (seconds)
PLAYER_RESPAWN_INVULN = 2.0  # time of invulnerability (blinking) after
                             # respawn (seconds)
PLAYER_RESPAWN_TIME = 1.0    # time a dead ship waits before respawn fly-in
                             # (seconds)
PLAYER_LIVES = 3             # initial player lives

# Player bullets
BULLET_SPEED = 720.0         # player bullet speed (px/s)
BULLET_W, BULLET_H = 4, 14   # player bullet size (px)

################################### Enemy ####################################

# 40 enemies at Level 1.
#
# Row layout (top -> bottom):
#
# Boss row:    4 bosses centered
# Hornet rows: 2 rows x 8 (centered)
# Bee rows:    2 rows x 10 (centered)
#
# Later levels widen the Hornet and Bee rows and add more rows and bosses.

FORMATION_TOP = 70      # enemy formation's vertical position (px)
FORMATION_SLOT_W = 34.0 # enemy formation slot width (px)
FORMATION_SLOT_H = 34.0 # enemy formation slot height (px)
FORMATION_COLS = 12     # number of columns in the formation

FORMATION_W = FORMATION_COLS * FORMATION_SLOT_W # enemy formation width (px)
FORMATION_CX = WIDTH / 2.0                      # enemy formation center (px)

# Base refers to the value at level 1; growth is per-level increase; max/min
# is the upper/lower bound (if any).

ENEMY_BULLET_SPEED_BASE = 300.0        # base enemy bullet speed (px/s)
ENEMY_BULLET_SPEED_GROWTH = 6.0        # enemy bullet speed increase per level
                                       # (px/s)
ENEMY_BULLET_MAX_SPEED = 600.0         # maximum enemy bullet speed (px/s)
ENEMY_BULLET_W, ENEMY_BULLET_H = 5, 12 # enemy bullet size (px)

DIVE_INTERVAL_BASE = 3.0  # base time between enemy dive waves (seconds)
DIVE_INTERVAL_DROP = 0.05 # decrease in time between enemy dive waves per
                          # level (seconds)
DIVE_INTERVAL_MIN = 0.6   # minimum time between enemy dive waves (seconds)
DIVE_SPEED_BASE = 200.0   # base enemy dive speed (px/s)
DIVE_SPEED_GROWTH = 6.0   # increase in enemy dive speed per level (px/s)
DIVE_SPEED_MAX = 500.0    # maximum enemy dive speed (px/s)
FIRE_CHANCE_BASE = 0.16   # base chance of enemy firing a bullet
FIRE_CHANCE_GROWTH = 0.02 # increase in chance of enemy firing a bullet per
                          # level
FIRE_CHANCE_MAX = 1.0     # maximum chance of enemy firing a bullet
MAX_DIVERS_GROWTH = 8     # number of levels required to increase the maximum
                          # number of simultaneous divers by 1
MAX_DIVERS_CAP = 8        # maximum number of simultaneous divers

ENTRY_DELAY_BASE = 0.6      # base time between entry of enemy groups
                            # (seconds)
ENTRY_DELAY_DROP = 0.01     # decrease in time between entry of enemy groups
                            # per level (seconds)
ENTRY_DELAY_MIN = 0.2       # minimum time between entry of enemy groups
                            # (seconds)
ENTRY_PATH_TIME_BASE = 3.0  # base time for an enemy to fly from off-screen to
                            # its formation slot (seconds)
ENTRY_PATH_TIME_DROP = 0.04 # decrease in time for an enemy to fly from
                            # off-screen to its formation slot per level
ENTRY_PATH_TIME_MIN = 1.0   # minimum time for an enemy to fly from off-screen
                            # to its formation slot (seconds)

# Formation wobble
WOBBLE_AMP_BASE = 24.0
WOBBLE_AMP_GROWTH = 1.2
WOBBLE_AMP_MAX = 88.0
WOBBLE_SPEED_BASE = 0.6
WOBBLE_SPEED_GROWTH = 0.03
WOBBLE_SPEED_MAX = 2.4

# Slow whole-formation drift (sits on top of the wobble)
FORMATION_DRIFT_AMP = 36.0     # px of horizontal drift
FORMATION_DRIFT_SPEED = 0.2   # rad/s (~42 s period)

# Meaner dives: turn rate, target spread, pincer V waves, re-aim cadence
DIVE_TURN_BASE = 2.4
DIVE_TURN_GROWTH = 0.04
DIVE_TURN_MAX = 4.0
DIVE_SPREAD_BASE = 40.0
DIVE_SPREAD_GROWTH = 0.8
DIVE_SPREAD_MAX = 72.0
DIVE_PINCER_CHANCE_BASE = 0.0
DIVE_PINCER_CHANCE_GROWTH = 0.01
DIVE_PINCER_CHANCE_MAX = 0.5
DIVE_REAIM_MIN = 0.8           # s between target re-aims while diving
DIVE_REAIM_MAX = 1.6

# Smarter formation fire: rate multiplier, row bursts, terra homing, 3-way
FORMATION_FIRE_RATE = 2.0      # multiplier on enemy_fire_chance
FORMATION_BURST_CHANCE_BASE = 0.1
FORMATION_BURST_CHANCE_GROWTH = 0.02
FORMATION_BURST_CHANCE_MAX = 0.9
FORMATION_BURST_STEP = 50      # +1 burst shooter per 50 levels
FORMATION_BURST_MAX = 4
TERRA_HOMING_CHANCE_GROWTH = 0.01
TERRA_HOMING_CHANCE_MAX = 0.4
SPREAD_CHANCE_GROWTH = 0.01
SPREAD_CHANCE_MAX = 0.5

# Boss upgrades (Tier 3): 3-way spread and level-scaled homing
BOSS_SPREAD_CHANCE_GROWTH = 0.01
BOSS_SPREAD_CHANCE_MAX = 0.5
BOSS_HOMING_BASE = 0.1
BOSS_HOMING_GROWTH = 0.02
BOSS_HOMING_MAX = 0.9

# Elite bosses: extra hit point every 25 levels (cap 4)
ELITE_BOSS_STEP = 20
ELITE_BOSS_MAX_HITS = 4

# Fleet scaling (Tier 3): level thresholds for bigger formations
FLEET_TERRA_ROW_LEVEL = 10     # +1 terra row
FLEET_FIFTH_BOSS_LEVEL = 20     # 5th boss
WIDEN_TERRA_ROWS_LEVEL = 30                # terra rows widen to 10-wide
FLEET_THIRD_BEE_ROW_LEVEL = 40   # 3rd bee row
FLEET_SIXTH_BOSS_LEVEL = 50     # 6th boss
FLEET_FOURTH_BEE_ROW_LEVEL = 60    # 4th bee row
SECOND_WIDEN_TERRA_ROWS_LEVEL = 70  # 2nd time terra rows widen
FLEET_SEVENTH_BOSS_LEVEL = 80   # 7th boss
FLEET_FIFTH_BEE_ROW_LEVEL = 90     # 5th bee row
FLEET_EIGHTH_BOSS_LEVEL = 100    # 8th boss
FLEET_SECOND_TERRA_ROW_LEVEL = 110     # +1 terra row
FLEET_NINTH_BOSS_LEVEL = 120    # 9th boss
FLEET_TENTH_BOSS_LEVEL = 140    # 10th boss
FLEET_ELEVENTH_BOSS_LEVEL = 160    # 11th boss
FLEET_TWELFTH_BOSS_LEVEL = 180    # 12th boss
# Streak scoring
STREAK_MAX = 100

# Power-ups
POWERUP_DROP_CHANCE = 0.128
POWERUP_BOSS_DROP = 1.0
POWERUP_FALL_SPEED = 120.0
POWERUP_W, POWERUP_H = 26, 26
TRIPLE_DURATION = 8.0
RAPID_DURATION = 8.0

# Bomb: one-shot fan of 15 shots in a 60-degree forward cone
BOMB_FAN_SHOTS = 20
BOMB_FAN_ANGLE = math.radians(60.0)
BOMB_BULLET_SPEED = 800.0
BOMB_START = 0

# Score values
SCORE_BEE = 5
SCORE_TERRA = 10
SCORE_BOSS = 40
DIVE_BONUS_MULTIPLIER = 2

# Screen shake
SHAKE_MAGNITUDE = 6.0
SHAKE_DURATION = 0.25
BOSS_SHAKE_MAGNITUDE = 14.0
BOSS_SHAKE_DURATION = 0.5

HIGHSCORE_FILE = 'highscores.json'


def clamp(v: float, lo: float, hi: float) -> float:
    '''
    Clamp v to the inclusive range [lo, hi].

    Args:
        v: value to clamp.
        lo: lower bound.
        hi: upper bound.

    Returns:
        The clamped value.
    '''
    return max(lo, min(hi, v))


def level_params(level: int) -> dict:
    '''Return the difficulty scaling parameters for a given level (1-based).

    The ramp is deliberately slow: every parameter keeps escalating for
    roughly levels 60-100 before it saturates at its bound, which is a
    sanity floor/ceiling (dodgeable speeds, non-negative gaps, chance <= 1),
    not a difficulty cap.
    '''
    L = max(1, level)
    p = {
        'dive_interval': clamp(
            DIVE_INTERVAL_BASE - DIVE_INTERVAL_DROP * (L - 1), DIVE_INTERVAL_MIN, 999),
        'enemy_fire_chance': clamp(
            FIRE_CHANCE_BASE + FIRE_CHANCE_GROWTH * (L - 1), 0.0, FIRE_CHANCE_MAX),
        'enemy_bullet_speed': clamp(
            ENEMY_BULLET_SPEED_BASE + ENEMY_BULLET_SPEED_GROWTH * (L - 1),
            ENEMY_BULLET_SPEED_BASE, ENEMY_BULLET_MAX_SPEED),
        'dive_speed': clamp(
            DIVE_SPEED_BASE + DIVE_SPEED_GROWTH * (L - 1), DIVE_SPEED_BASE, DIVE_SPEED_MAX),
        'max_divers': min(MAX_DIVERS_CAP, 1 + (L - 1) // MAX_DIVERS_GROWTH),
        'entry_delay': clamp(
            ENTRY_DELAY_BASE - ENTRY_DELAY_DROP * (L - 1), ENTRY_DELAY_MIN, 999),
        'entry_path_time': clamp(
            ENTRY_PATH_TIME_BASE - ENTRY_PATH_TIME_DROP * (L - 1),
            ENTRY_PATH_TIME_MIN, 999),
        'formation_wobble_amp': WOBBLE_AMP_BASE + min(
            WOBBLE_AMP_MAX - WOBBLE_AMP_BASE, WOBBLE_AMP_GROWTH * (L - 1)),
        'formation_wobble_speed': min(
            WOBBLE_SPEED_MAX, WOBBLE_SPEED_BASE + WOBBLE_SPEED_GROWTH * (L - 1)),
        'dive_turn': min(
            DIVE_TURN_MAX, DIVE_TURN_BASE + DIVE_TURN_GROWTH * (L - 1)),
        'dive_spread': min(
            DIVE_SPREAD_MAX, DIVE_SPREAD_BASE + DIVE_SPREAD_GROWTH * (L - 1)),
        'dive_pincer_chance': min(
            DIVE_PINCER_CHANCE_MAX,
            DIVE_PINCER_CHANCE_BASE + DIVE_PINCER_CHANCE_GROWTH * (L - 1)),
        'formation_burst_chance': min(
            FORMATION_BURST_CHANCE_MAX,
            FORMATION_BURST_CHANCE_BASE + FORMATION_BURST_CHANCE_GROWTH * (L - 1)),
        'formation_burst_shooters': min(
            FORMATION_BURST_MAX, 1 + (L - 1) // FORMATION_BURST_STEP),
        'terra_homing_chance': min(
            TERRA_HOMING_CHANCE_MAX, TERRA_HOMING_CHANCE_GROWTH * (L - 1)),
        'spread_chance': min(
            SPREAD_CHANCE_MAX, SPREAD_CHANCE_GROWTH * (L - 1)),
        'boss_spread_chance': min(
            BOSS_SPREAD_CHANCE_MAX, BOSS_SPREAD_CHANCE_GROWTH * (L - 1)),
        'boss_homing_chance': min(
            BOSS_HOMING_MAX, BOSS_HOMING_BASE + BOSS_HOMING_GROWTH * (L - 1)),
    }

    return p


def fleet_composition(level: int) -> list:
    '''Build the (type, column, row) formation slots for a level's fleet.

    Level 1 is the classic 40-enemy layout (8-wide terra rows); later
    levels widen the terra rows, add more rows, and add extra bosses.

    Args:
        level: 1-based level number.

    Returns:
        List of (etype, col, row) tuples (max 76 enemies).
    '''
    L = max(1, level)
    n_bosses = 4
    terra_rows = 2
    terra_width = 8   # classic layout is 8-wide; widens to 10 later
    bee_rows = 2
    bee_width = 10

    if L >= FLEET_TERRA_ROW_LEVEL:
        terra_rows = 3

    if L >= FLEET_FIFTH_BOSS_LEVEL:
        n_bosses = 5

    if L >= WIDEN_TERRA_ROWS_LEVEL:
        terra_width = 10
        bee_width = FORMATION_COLS  # bees fill the row

    if L >= FLEET_THIRD_BEE_ROW_LEVEL:
        bee_rows = 3

    if L >= FLEET_SIXTH_BOSS_LEVEL:
        n_bosses = 6

    if L >= FLEET_FOURTH_BEE_ROW_LEVEL:
        bee_rows = 4

    if L >= SECOND_WIDEN_TERRA_ROWS_LEVEL:
        terra_width = FORMATION_COLS

    if L >= FLEET_SEVENTH_BOSS_LEVEL:
        n_bosses = 7

    if L >= FLEET_FIFTH_BEE_ROW_LEVEL:
        bee_rows = 5

    if L >= FLEET_EIGHTH_BOSS_LEVEL:
        n_bosses = 8

    if L >= FLEET_SECOND_TERRA_ROW_LEVEL:
        terra_rows = 4

    if L >= FLEET_NINTH_BOSS_LEVEL:
        n_bosses = 9

    if L >= FLEET_TENTH_BOSS_LEVEL:
        n_bosses = 10

    if L >= FLEET_ELEVENTH_BOSS_LEVEL:
        n_bosses = 11

    if L >= FLEET_TWELFTH_BOSS_LEVEL:
        n_bosses = 12

    slots = []

    # Boss row (centered)
    first = (FORMATION_COLS - n_bosses) // 2

    for i in range(n_bosses):
        slots.append(('boss', first + i, 0))

    # TERRA rows (centered)
    g_first = (FORMATION_COLS - terra_width) // 2

    for row in range(1, terra_rows + 1):
        for col in range(g_first, g_first + terra_width):
            slots.append(('terra', col, row))

    b_first = (FORMATION_COLS - bee_width) // 2

    # Bee rows (10 wide)
    for row in range(terra_rows + 1, terra_rows + bee_rows + 1):
        for col in range(b_first, b_first + bee_width):
            slots.append(('bee', col, row))

    return slots


def slot_to_world(slot_index: int, slot: tuple, wobble_x: float) -> tuple:
    '''Convert a formation slot to world coordinates with the wobble offset.'''
    etype, col, row = slot
    x = FORMATION_CX + (col - (FORMATION_COLS - 1) / 2.0) * FORMATION_SLOT_W + wobble_x
    y = FORMATION_TOP + row * FORMATION_SLOT_H

    return x, y
