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
HORNET_COLOR = CYAN
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

FORMATION_CX = WIDTH / 2.0                      # enemy formation center (px)

# Base refers to the value at level 1; growth is per-level increase; max/min
# is the upper/lower bound (if any).

ENEMY_BULLET_SPEED_BASE = 300.0        # base enemy bullet speed (px/s)
ENEMY_BULLET_SPEED_GROWTH = 12.0        # enemy bullet speed increase per level
                                       # (px/s)
ENEMY_BULLET_MAX_SPEED = 1500.0         # maximum enemy bullet speed (px/s)
ENEMY_BULLET_W, ENEMY_BULLET_H = 5, 12 # enemy bullet size (px)

DIVE_INTERVAL_BASE = 3.0  # base time between enemy dive waves (seconds)
DIVE_INTERVAL_DROP = 0.05 # decrease in time between enemy dive waves per
                          # level (seconds)
DIVE_INTERVAL_MIN = 0.1   # minimum time between enemy dive waves (seconds)
DIVE_SPEED_BASE = 200.0   # base enemy dive speed (px/s)
DIVE_SPEED_GROWTH = 5.0   # increase in enemy dive speed per level (px/s)
DIVE_SPEED_MAX = 800.0    # maximum enemy dive speed (px/s)
FIRE_CHANCE_BASE = 0.16   # base chance of enemy firing a bullet
FIRE_CHANCE_GROWTH = 0.02 # increase in chance of enemy firing a bullet per
                          # level
FIRE_CHANCE_MAX = 1.0     # maximum chance of enemy firing a bullet
MAX_DIVERS_GROWTH = 8     # number of levels required to increase the maximum
                          # number of simultaneous divers by 1
MAX_DIVERS_CAP = 16       # maximum number of simultaneous divers

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
WOBBLE_AMP_BASE = 24.0     # base amplitude of enemy formation wobble (px)
WOBBLE_AMP_GROWTH = 1.0    # increase in amplitude of enemy formation wobble
                           # per level (px)
WOBBLE_AMP_MAX = 100.0      # maximum amplitude of enemy formation wobble (px)
WOBBLE_SPEED_BASE = 0.4    # base speed of enemy formation wobble (rad/s)
WOBBLE_SPEED_GROWTH = 0.04 # increase in speed of enemy formation wobble per
                           # level (rad/s)
WOBBLE_SPEED_MAX = 3.2     # maximum speed of enemy formation wobble (rad/s)

# Slow whole-formation drift (in addition to the wobble)
FORMATION_DRIFT_AMP = 36.0  # amplitude of whole-formation drift (px)
FORMATION_DRIFT_SPEED = 0.2 # speed of whole-formation drift (rad/s)

# Dive mechanics
DIVE_TURN_BASE = 2.4             # base turn rate (rad/s) for divers to turn
                                 # toward the player
DIVE_TURN_GROWTH = 0.04          # increase in turn rate (rad/s) per level for
                                 # divers to turn toward the player
DIVE_TURN_MAX = 7.2              # maximum turn rate (rad/s) for divers to
                                 # turn toward the player
DIVE_SPREAD_BASE = 40.0          # base spread angle for divers to fan out
                                 # when diving (degrees)
DIVE_SPREAD_GROWTH = 0.8         # increase in spread angle for divers to fan
                                 # out when diving per level (degrees)
DIVE_SPREAD_MAX = 104.0           # maximum spread angle for divers to fan out
                                 # when diving (degrees)
DIVE_PINCER_CHANCE_BASE = 0.0    # base chance of a pincer dive
DIVE_PINCER_CHANCE_GROWTH = 0.01 # increase in chance of a pincer dive per
                                 # level
DIVE_PINCER_CHANCE_MAX = 0.8     # maximum chance of a pincer dive
DIVE_REAIM_MIN = 0.8             # minimum time between re-aims for divers
                                 # (seconds)
DIVE_REAIM_MAX = 1.6             # maximum time between re-aims for divers
                                 # (seconds)

# Formation fire
FORMATION_FIRE_RATE = 2.0            # multiplier on enemy fire chance
FORMATION_BURST_CHANCE_BASE = 0.1    # base chance of a formation burst (shots
                                     # from multiple enemies in a formation) 
FORMATION_BURST_CHANCE_GROWTH = 0.02 # increase in chance of a formation burst
                                     # per level
FORMATION_BURST_CHANCE_MAX = 0.9     # maximum chance of a formation burst
FORMATION_BURST_STEP = 20            # number of levels required to increase
                                     # the number of shooters in a formation
                                     # burst by 1
FORMATION_BURST_MAX = 8              # maximum number of shooters in a
                                     # formation burst

# Hornet characteristics
HORNET_HOMING_CHANCE_GROWTH = 0.01   # increase in chance of hornet homing in
                                     # on the player per level
HORNET_HOMING_CHANCE_MAX = 0.6       # maximum chance of hornet homing in on
                                     # the player
SPREAD_CHANCE_GROWTH = 0.01          # increase in chance of spread shot per
                                     # level
SPREAD_CHANCE_MAX = 0.5              # maximum chance of spread shot

# Boss characteristics
BOSS_SPREAD_CHANCE_GROWTH = 0.01 # increase in chance of boss spread shot per
                                 # level
BOSS_SPREAD_CHANCE_MAX = 0.9     # maximum chance of boss spread shot
BOSS_HOMING_BASE = 0.1           # base chance of boss homing in on the player
BOSS_HOMING_GROWTH = 0.02        # increase in chance of boss homing in on the
                                 # player per level
BOSS_HOMING_MAX = 1.0            # maximum chance of boss homing in on the
                                 # player

# Elite boss characteristics
ELITE_BOSS_STEP = 30    # number of levels required to increase the maximum
                        # number of hits an elite boss can take by 1
ELITE_BOSS_MAX_HITS = 6 # maximum number of hits an elite boss can take

# Fleet scaling
FLEET_THIRD_HORNET_ROW_LEVEL = 10    # 3rd hornet row level
FLEET_FIFTH_BOSS_LEVEL = 20          # 5th boss level
FLEET_TEN_WIDE_HORNET_LEVEL = 30     # 10-wide hornet row level
FLEET_THIRD_BEE_ROW_LEVEL = 40       # 3rd bee row level
FLEET_SIXTH_BOSS_LEVEL = 50          # 6th boss level
FLEET_FOURTH_BEE_ROW_LEVEL = 60      # 4th bee row level
FLEET_TWELVE_WIDE_HORNET_LEVEL = 70  # 12-wide hornet row level
FLEET_SEVENTH_BOSS_LEVEL = 80        # 7th boss level
FLEET_FIFTH_BEE_ROW_LEVEL = 90       # 5th bee row level
FLEET_EIGHTH_BOSS_LEVEL = 100        # 8th boss level
FLEET_FOURTH_HORNET_ROW_LEVEL = 110  # 4th hornet row level
FLEET_NINTH_BOSS_LEVEL = 120         # 9th boss level
FLEET_TENTH_BOSS_LEVEL = 140         # 10th boss level
FLEET_ELEVENTH_BOSS_LEVEL = 160      # 11th boss level
FLEET_TWELFTH_BOSS_LEVEL = 180       # 12th boss level

# Scoring streak
STREAK_MAX = 100

# Power-ups
POWERUP_DROP_CHANCE = 0.128   # chance of a power-up dropping when an enemy is
                              # destroyed
POWERUP_BOSS_DROP = 1.0       # chance of a power-up dropping when a boss is
                              # destroyed
POWERUP_FALL_SPEED = 120.0    # speed of falling power-ups (px/s)
POWERUP_W, POWERUP_H = 26, 26 # power-up size (px)
TRIPLE_DURATION = 8.0         # duration of triple-shot power-up (seconds)
RAPID_DURATION = 8.0          # duration of rapid-fire power-up (seconds)

# Bomb
BOMB_FAN_SHOTS = 30                 # number of shots in a bomb fan
BOMB_FAN_ANGLE = math.radians(60.0) # angle of bomb fan (radians)
BOMB_BULLET_SPEED = 800.0           # speed of bomb bullets (px/s)
BOMB_START = 3                      # initial number of bombs

# Score values
SCORE_BEE = 5             # score for destroying a bee
SCORE_HORNET = 10         # score for destroying a hornet
SCORE_BOSS = 40           # score for destroying a boss
DIVE_BONUS_MULTIPLIER = 2 # multiplier on score for destroying a diving enemy

# Screen shake
SHAKE_MAGNITUDE = 6.0       # magnitude of screen shake (px)
SHAKE_DURATION = 0.25       # duration of screen shake (seconds)
BOSS_SHAKE_MAGNITUDE = 14.0 # magnitude of screen shake when a boss is hit
                            # (px)
BOSS_SHAKE_DURATION = 0.5   # duration of screen shake when a boss is hit
                            # (seconds)

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
    '''
    Return the difficulty scaling parameters for a given level.
    
    Args:
        level: level number.
    
    Returns:
        p: dictionary of level-scaled parameters.
    '''
    L = max(1, level)

    p = {
        'dive_interval': clamp(DIVE_INTERVAL_BASE - DIVE_INTERVAL_DROP * (L - 1), DIVE_INTERVAL_MIN, 9),
        'enemy_fire_chance': clamp(FIRE_CHANCE_BASE + FIRE_CHANCE_GROWTH * (L - 1), 0.0, FIRE_CHANCE_MAX),
        'enemy_bullet_speed': clamp(
            ENEMY_BULLET_SPEED_BASE + ENEMY_BULLET_SPEED_GROWTH * (L - 1),
            ENEMY_BULLET_SPEED_BASE,
            ENEMY_BULLET_MAX_SPEED
        ),
        'dive_speed': clamp(DIVE_SPEED_BASE + DIVE_SPEED_GROWTH * (L - 1), DIVE_SPEED_BASE, DIVE_SPEED_MAX),
        'max_divers': clamp(1 + (L - 1) // MAX_DIVERS_GROWTH, 1, MAX_DIVERS_CAP),
        'entry_delay': clamp(ENTRY_DELAY_BASE - ENTRY_DELAY_DROP * (L - 1), ENTRY_DELAY_MIN, 9),
        'entry_path_time': clamp(ENTRY_PATH_TIME_BASE - ENTRY_PATH_TIME_DROP * (L - 1), ENTRY_PATH_TIME_MIN, 9),
        'formation_wobble_amp': clamp(WOBBLE_AMP_BASE + WOBBLE_AMP_GROWTH * (L - 1), WOBBLE_AMP_BASE, WOBBLE_AMP_MAX),
        'formation_wobble_speed': clamp(
            WOBBLE_SPEED_BASE + WOBBLE_SPEED_GROWTH * (L - 1),
            WOBBLE_SPEED_BASE,
            WOBBLE_SPEED_MAX
        ),
        'dive_turn': clamp(DIVE_TURN_BASE + DIVE_TURN_GROWTH * (L - 1), DIVE_TURN_BASE, DIVE_TURN_MAX),
        'dive_spread': clamp(DIVE_SPREAD_BASE + DIVE_SPREAD_GROWTH * (L - 1), DIVE_SPREAD_BASE, DIVE_SPREAD_MAX),
        'dive_pincer_chance': clamp(
            DIVE_PINCER_CHANCE_BASE + DIVE_PINCER_CHANCE_GROWTH * (L - 1),
            DIVE_PINCER_CHANCE_BASE,
            DIVE_PINCER_CHANCE_MAX
        ),
        'formation_burst_chance': clamp(
            FORMATION_BURST_CHANCE_BASE + FORMATION_BURST_CHANCE_GROWTH * (L - 1),
            FORMATION_BURST_CHANCE_BASE,
            FORMATION_BURST_CHANCE_MAX
        ),
        'formation_burst_shooters': clamp(1 + (L - 1) // FORMATION_BURST_STEP, 1, FORMATION_BURST_MAX),
        'terra_homing_chance': clamp(HORNET_HOMING_CHANCE_GROWTH * (L - 1), 0.0, HORNET_HOMING_CHANCE_MAX),
        'spread_chance': clamp(SPREAD_CHANCE_GROWTH * (L - 1), 0.0, SPREAD_CHANCE_MAX),
        'boss_spread_chance': clamp(BOSS_SPREAD_CHANCE_GROWTH * (L - 1), 0.0, BOSS_SPREAD_CHANCE_MAX),
        'boss_homing_chance': clamp(
            BOSS_HOMING_BASE + BOSS_HOMING_GROWTH * (L - 1),
            BOSS_HOMING_BASE,
            BOSS_HOMING_MAX
        ),
    }

    return p


# Fleet scaling milestones: (level threshold, changes to apply at that level).
# Baseline (level 1) is 4 bosses, 2 hornet rows (8-wide), 2 bee rows (10-wide).
_FLEET_MILESTONES = [
    (FLEET_THIRD_HORNET_ROW_LEVEL, {'hornet_rows': 3}),
    (FLEET_FIFTH_BOSS_LEVEL, {'n_bosses': 5}),
    (FLEET_TEN_WIDE_HORNET_LEVEL, {'hornet_width': 10, 'bee_width': FORMATION_COLS}),
    (FLEET_THIRD_BEE_ROW_LEVEL, {'bee_rows': 3}),
    (FLEET_SIXTH_BOSS_LEVEL, {'n_bosses': 6}),
    (FLEET_FOURTH_BEE_ROW_LEVEL, {'bee_rows': 4}),
    (FLEET_TWELVE_WIDE_HORNET_LEVEL, {'hornet_width': FORMATION_COLS}),
    (FLEET_SEVENTH_BOSS_LEVEL, {'n_bosses': 7}),
    (FLEET_FIFTH_BEE_ROW_LEVEL, {'bee_rows': 5}),
    (FLEET_EIGHTH_BOSS_LEVEL, {'n_bosses': 8}),
    (FLEET_FOURTH_HORNET_ROW_LEVEL, {'hornet_rows': 4}),
    (FLEET_NINTH_BOSS_LEVEL, {'n_bosses': 9}),
    (FLEET_TENTH_BOSS_LEVEL, {'n_bosses': 10}),
    (FLEET_ELEVENTH_BOSS_LEVEL, {'n_bosses': 11}),
    (FLEET_TWELFTH_BOSS_LEVEL, {'n_bosses': 12}),
]


def fleet_composition(level: int) -> list:
    '''
    Build the (type, column, row) formation slots for a level's enemy fleet.

    Level 1 is the classic 40-enemy layout (8-wide hornet rows); later levels
    widen the hornet and bee rows, add more rows, and add extra bosses.

    Args:
        level: level number.

    Returns:
        List of (etype, col, row) tuples.
    '''
    L = max(1, level)

    fleet = {
        'n_bosses': 4,
        'hornet_rows': 2,
        'hornet_width': 8,
        'bee_rows': 2,
        'bee_width': 10,
    }

    for threshold, changes in _FLEET_MILESTONES:
        if L >= threshold:
            fleet.update(changes)

    n_bosses = fleet['n_bosses']
    hornet_rows = fleet['hornet_rows']
    hornet_width = fleet['hornet_width']
    bee_rows = fleet['bee_rows']
    bee_width = fleet['bee_width']

    slots = []

    # Boss row (centered)
    first = (FORMATION_COLS - n_bosses) // 2

    for i in range(n_bosses):
        slots.append(('boss', first + i, 0))

    # Hornet rows (centered)
    h_first = (FORMATION_COLS - hornet_width) // 2

    for row in range(1, hornet_rows + 1):
        for col in range(h_first, h_first + hornet_width):
            slots.append(('hornet', col, row))

    b_first = (FORMATION_COLS - bee_width) // 2

    # Bee rows (centered)
    for row in range(hornet_rows + 1, hornet_rows + bee_rows + 1):
        for col in range(b_first, b_first + bee_width):
            slots.append(('bee', col, row))

    return slots


def slot_to_world(slot: tuple, wobble_x: float) -> tuple:
    '''
    Convert a formation slot to world coordinates with the wobble offset.
    
    Args:
        slot: (etype, col, row) of the formation slot.
        wobble_x: current horizontal wobble offset (px).

    Returns:
        Tuple of (x, y) world coordinates.
    '''
    _, col, row = slot

    x = FORMATION_CX + (col - (FORMATION_COLS - 1) / 2.0) * FORMATION_SLOT_W + wobble_x
    y = FORMATION_TOP + row * FORMATION_SLOT_H

    return x, y
