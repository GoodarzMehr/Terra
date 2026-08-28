'''Central configuration: window, palette, physics, difficulty curve.

All tuning knobs for the game live here so balancing is a one-file affair.
'''

import math

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600  # logical (game-space) resolution
UI_SCALE = 2              # everything is rendered at this scale
WINDOW_W, WINDOW_H = WIDTH * UI_SCALE, HEIGHT * UI_SCALE
FPS = 60
TITLE = 'GALAGA — Python Arcade'

# ---------------------------------------------------------------------------
# Palette (neon on space-black)
# ---------------------------------------------------------------------------
BLACK = (8, 10, 24)
DEEP_BLUE = (16, 22, 48)
WHITE = (240, 244, 255)
YELLOW = (255, 220, 80)
ORANGE = (255, 160, 60)
RED = (255, 70, 70)
DARK_RED = (150, 40, 50)
GREEN = (90, 230, 120)
DARK_GREEN = (30, 120, 70)
CYAN = (90, 220, 255)
BLUE = (90, 140, 255)
MAGENTA = (235, 110, 255)
PINK = (255, 130, 200)
GRAY = (140, 145, 165)
LIGHT_GRAY = (200, 205, 220)

# Enemy colors
BEE_COLOR = RED
GALAGA_COLOR = CYAN
BOSS_COLOR = MAGENTA

# ---------------------------------------------------------------------------
# Player physics
# ---------------------------------------------------------------------------
PLAYER_SPEED = 380.0           # px/s horizontal
PLAYER_Y = HEIGHT - 40         # fixed vertical lane
PLAYER_W, PLAYER_H = 30, 30
PLAYER_FIRE_COOLDOWN = 0.24    # s between shots
PLAYER_RAPID_COOLDOWN = 0.16
PLAYER_RESPAWN_INVULN = 2.0    # s of blinking after respawn
PLAYER_RESPAWN_TIME = 1.0      # s dead ship sits before respawn fly-in
PLAYER_LIVES = 3

# Bullet physics
BULLET_SPEED = 720.0           # player bullet, px/s
BULLET_W, BULLET_H = 4, 14

# ---------------------------------------------------------------------------
# Enemy / formation geometry
# ---------------------------------------------------------------------------
FORMATION_TOP = 70
FORMATION_SLOT_W = 34.0
FORMATION_SLOT_H = 34.0
FORMATION_COLS = 12
# 40 enemies at level 1: row layout (top -> bottom)
#   Boss row:    4 bosses centered
#   Galaga rows: 2 rows x 8 (centered)
#   Bee rows:    2 rows x 10
#   (later levels widen the galaga rows and add more rows / bosses)
FORMATION_W = FORMATION_COLS * FORMATION_SLOT_W
FORMATION_CX = WIDTH / 2.0

ENEMY_BASE_FIRE_CHANCE = 0.16
ENEMY_BULLET_BASE_SPEED = 300.0
ENEMY_BULLET_SPEED_GROWTH = 6.0
ENEMY_BULLET_MAX_SPEED = 600.0
ENEMY_BULLET_W, ENEMY_BULLET_H = 5, 12

DIVE_BASE_INTERVAL = 3.0       # s between dive waves at level 1
DIVE_INTERVAL_DROP = 0.05    # faster each level
DIVE_INTERVAL_MIN = 0.6
DIVE_BASE_SPEED = 200.0
DIVE_SPEED_GROWTH = 6.0
DIVE_SPEED_MAX = 500.0
FIRE_CHANCE_GROWTH = 0.02
FIRE_CHANCE_MAX = 1.0
MAX_DIVERS_GROWTH = 8         # +1 simultaneous diver per 10 levels
MAX_DIVERS_CAP = 8

ENTRY_BASE_DELAY = 0.6        # s between entry groups at level 1
ENTRY_DELAY_DROP = 0.01
ENTRY_DELAY_MIN = 0.2
ENTRY_PATH_BASE_TIME = 3.0     # s to fly from off-screen to slot
ENTRY_PATH_TIME_DROP = 0.04
ENTRY_PATH_TIME_MIN = 1.0

# Formation wobble (bounds are sanity limits, not a difficulty cap)
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

# Smarter formation fire: rate multiplier, row bursts, galaga homing, 3-way
FORMATION_FIRE_RATE = 2.0      # multiplier on enemy_fire_chance
FORMATION_BURST_CHANCE_BASE = 0.1
FORMATION_BURST_CHANCE_GROWTH = 0.02
FORMATION_BURST_CHANCE_MAX = 0.9
FORMATION_BURST_STEP = 50      # +1 burst shooter per 50 levels
FORMATION_BURST_MAX = 4
GALAGA_HOMING_CHANCE_GROWTH = 0.01
GALAGA_HOMING_CHANCE_MAX = 0.4
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
FLEET_GALAGA_ROW_LEVEL = 10     # +1 galaga row
FLEET_FIFTH_BOSS_LEVEL = 20     # 5th boss
WIDEN_GALAGA_ROWS_LEVEL = 30                # galaga rows widen to 10-wide
FLEET_THIRD_BEE_ROW_LEVEL = 40   # 3rd bee row
FLEET_SIXTH_BOSS_LEVEL = 50     # 6th boss
FLEET_FOURTH_BEE_ROW_LEVEL = 60    # 4th bee row
SECOND_WIDEN_GALAGA_ROWS_LEVEL = 70  # 2nd time galaga rows widen
FLEET_SEVENTH_BOSS_LEVEL = 80   # 7th boss
FLEET_FIFTH_BEE_ROW_LEVEL = 90     # 5th bee row
FLEET_EIGHTH_BOSS_LEVEL = 100    # 8th boss
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
SCORE_GALAGA = 10
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
            DIVE_BASE_INTERVAL - DIVE_INTERVAL_DROP * (L - 1), DIVE_INTERVAL_MIN, 999),
        'enemy_fire_chance': clamp(
            ENEMY_BASE_FIRE_CHANCE + FIRE_CHANCE_GROWTH * (L - 1), 0.0, FIRE_CHANCE_MAX),
        'enemy_bullet_speed': clamp(
            ENEMY_BULLET_BASE_SPEED + ENEMY_BULLET_SPEED_GROWTH * (L - 1),
            ENEMY_BULLET_BASE_SPEED, ENEMY_BULLET_MAX_SPEED),
        'dive_speed': clamp(
            DIVE_BASE_SPEED + DIVE_SPEED_GROWTH * (L - 1), DIVE_BASE_SPEED, DIVE_SPEED_MAX),
        'max_divers': min(MAX_DIVERS_CAP, 1 + (L - 1) // MAX_DIVERS_GROWTH),
        'entry_delay': clamp(
            ENTRY_BASE_DELAY - ENTRY_DELAY_DROP * (L - 1), ENTRY_DELAY_MIN, 999),
        'entry_path_time': clamp(
            ENTRY_PATH_BASE_TIME - ENTRY_PATH_TIME_DROP * (L - 1),
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
        'galaga_homing_chance': min(
            GALAGA_HOMING_CHANCE_MAX, GALAGA_HOMING_CHANCE_GROWTH * (L - 1)),
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

    Level 1 is the classic 40-enemy layout (8-wide galaga rows); later
    levels widen the galaga rows, add more rows, and add extra bosses.

    Args:
        level: 1-based level number.

    Returns:
        List of (etype, col, row) tuples (max 76 enemies).
    '''
    L = max(1, level)
    n_bosses = 4
    galaga_rows = 2
    galaga_width = 8   # classic layout is 8-wide; widens to 10 later
    bee_rows = 2
    bee_width = 10

    if L >= FLEET_GALAGA_ROW_LEVEL:
        galaga_rows = 3

    if L >= FLEET_FIFTH_BOSS_LEVEL:
        n_bosses = 5

    if L >= WIDEN_GALAGA_ROWS_LEVEL:
        galaga_width = 10
        bee_width = FORMATION_COLS  # bees fill the row

    if L >= FLEET_THIRD_BEE_ROW_LEVEL:
        bee_rows = 3

    if L >= FLEET_SIXTH_BOSS_LEVEL:
        n_bosses = 6

    if L >= FLEET_FOURTH_BEE_ROW_LEVEL:
        bee_rows = 4

    if L >= SECOND_WIDEN_GALAGA_ROWS_LEVEL:
        galaga_width = FORMATION_COLS

    if L >= FLEET_SEVENTH_BOSS_LEVEL:
        n_bosses = 7

    if L >= FLEET_FIFTH_BEE_ROW_LEVEL:
        bee_rows = 5

    if L >= FLEET_EIGHTH_BOSS_LEVEL:
        n_bosses = 8

    slots = []

    # Boss row (centered)
    first = (FORMATION_COLS - n_bosses) // 2

    for i in range(n_bosses):
        slots.append(('boss', first + i, 0))

    # Galaga rows (centered)
    g_first = (FORMATION_COLS - galaga_width) // 2

    for row in range(1, galaga_rows + 1):
        for col in range(g_first, g_first + galaga_width):
            slots.append(('galaga', col, row))

    b_first = (FORMATION_COLS - bee_width) // 2

    # Bee rows (10 wide)
    for row in range(galaga_rows + 1, galaga_rows + bee_rows + 1):
        for col in range(b_first, b_first + bee_width):
            slots.append(('bee', col, row))

    return slots


def slot_to_world(slot_index: int, slot: tuple, wobble_x: float) -> tuple:
    '''Convert a formation slot to world coordinates with the wobble offset.'''
    etype, col, row = slot
    x = FORMATION_CX + (col - (FORMATION_COLS - 1) / 2.0) * FORMATION_SLOT_W + wobble_x
    y = FORMATION_TOP + row * FORMATION_SLOT_H

    return x, y
