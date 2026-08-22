"""Central configuration: window, palette, physics constants, difficulty curve.

All tuning knobs for the game live here so balancing is a one-file affair.
"""

import math

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600   # logical (game-space) resolution
UI_SCALE = 2               # everything is rendered at this scale
WINDOW_W, WINDOW_H = WIDTH * UI_SCALE, HEIGHT * UI_SCALE
FPS = 60
TITLE = "GALAGA — Python Arcade"

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
PLAYER_SPEED = 380.0          # px/s horizontal
PLAYER_Y = HEIGHT - 70       # fixed vertical lane
PLAYER_W, PLAYER_H = 30, 30
PLAYER_FIRE_COOLDOWN = 0.24  # s between shots
PLAYER_RAPID_COOLDOWN = 0.09
PLAYER_RESPAWN_INVULN = 2.2  # s of blinking after respawn
PLAYER_RESPAWN_TIME = 1.2    # s dead ship sits before respawn fly-in
PLAYER_LIVES = 3

# Bullet physics
BULLET_SPEED = 720.0         # player bullet, px/s
BULLET_W, BULLET_H = 4, 14
MAX_PLAYER_BULLETS = 4       # on screen per player (classic limit)

# ---------------------------------------------------------------------------
# Enemy / formation geometry
# ---------------------------------------------------------------------------
FORMATION_TOP = 90
FORMATION_SLOT_W = 34.0
FORMATION_SLOT_H = 34.0
FORMATION_COLS = 10
# 40 enemies: row layout (top -> bottom)
#   Boss row:    4 bosses centered
#   Galaga rows: 2 rows x 10
#   Bee rows:    2 rows x 10 + 2 extra bees flanking the top
FORMATION_W = FORMATION_COLS * FORMATION_SLOT_W
FORMATION_CX = WIDTH / 2.0

ENEMY_BASE_FIRE_CHANCE = 0.16
ENEMY_BULLET_BASE_SPEED = 300.0
ENEMY_BULLET_SPEED_GROWTH = 20.0
ENEMY_BULLET_MAX_SPEED = 550.0
ENEMY_BULLET_W, ENEMY_BULLET_H = 5, 12

DIVE_BASE_INTERVAL = 3.0     # s between dive waves at level 1
DIVE_INTERVAL_DROP = 0.22    # faster each level
DIVE_INTERVAL_MIN = 0.85
DIVE_BASE_SPEED = 185.0
DIVE_SPEED_GROWTH = 14.0
DIVE_SPEED_MAX = 330.0
FIRE_CHANCE_GROWTH = 0.065
FIRE_CHANCE_MAX = 0.85
MAX_DIVERS_GROWTH = 2        # +1 simultaneous diver per 2 levels
MAX_DIVERS_CAP = 4

ENTRY_BASE_DELAY = 0.55      # s between entry groups at level 1
ENTRY_DELAY_DROP = 0.05
ENTRY_DELAY_MIN = 0.18
ENTRY_PATH_BASE_TIME = 2.6   # s for an enemy to fly from off-screen to slot
ENTRY_PATH_TIME_DROP = 0.15
ENTRY_PATH_TIME_MIN = 1.1

# Streak scoring
STREAK_MAX = 6

# Power-ups
POWERUP_DROP_CHANCE = 0.12
POWERUP_BOSS_DROP = 1.0
POWERUP_FALL_SPEED = 110.0
POWERUP_W, POWERUP_H = 26, 26
TRIPLE_DURATION = 10.0
RAPID_DURATION = 8.0

# Score values
SCORE_BEE = 50
SCORE_GALAGA = 100
SCORE_BOSS = 400
DIVE_BONUS_MULTIPLIER = 2

# Screen shake
SHAKE_MAGNITUDE = 6.0
SHAKE_DURATION = 0.25
BOSS_SHAKE_MAGNITUDE = 14.0
BOSS_SHAKE_DURATION = 0.5

HIGHSCORE_FILE = "highscores.json"


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def level_params(level):
    """Return the difficulty scaling parameters for a given level (1-based).

    Everything is capped so that from ~level 10 onward the game stops getting
    harder (classic curve, still beatable).
    """
    L = max(1, level)
    p = {
        "dive_interval": clamp(
            DIVE_BASE_INTERVAL - DIVE_INTERVAL_DROP * (L - 1), DIVE_INTERVAL_MIN, 999
        ),
        "enemy_fire_chance": clamp(
            ENEMY_BASE_FIRE_CHANCE + FIRE_CHANCE_GROWTH * (L - 1), 0.0, FIRE_CHANCE_MAX
        ),
        "enemy_bullet_speed": clamp(
            ENEMY_BULLET_BASE_SPEED + ENEMY_BULLET_SPEED_GROWTH * (L - 1),
            ENEMY_BULLET_BASE_SPEED,
            ENEMY_BULLET_MAX_SPEED,
        ),
        "dive_speed": clamp(
            DIVE_BASE_SPEED + DIVE_SPEED_GROWTH * (L - 1), DIVE_BASE_SPEED, DIVE_SPEED_MAX
        ),
        "max_divers": min(MAX_DIVERS_CAP, 1 + (L - 1) // MAX_DIVERS_GROWTH),
        "entry_delay": clamp(
            ENTRY_BASE_DELAY - ENTRY_DELAY_DROP * (L - 1), ENTRY_DELAY_MIN, 999
        ),
        "entry_path_time": clamp(
            ENTRY_PATH_BASE_TIME - ENTRY_PATH_TIME_DROP * (L - 1),
            ENTRY_PATH_TIME_MIN,
            999,
        ),
        "formation_wobble_amp": 26.0 + min(20.0, 2.0 * (L - 1)),
        "formation_wobble_speed": 0.7 + 0.05 * (L - 1),
    }
    return p


def formation_slots():
    """Return the 40 (type, column, row) formation slots, classic stacked layout.

    Layout (40 enemies):
        row 0:      B  B  B  B          (4 bosses, centered)
        row 1:   G G G G G G G G        (8 galagas, centered)
        row 2:   G G G G G G G G        (8 galagas, centered)
        row 3:  B B B B B B B B B B     (10 bees)
        row 4:  B B B B B B B B B B     (10 bees)
    Total: 4 + 16 + 20 = 40
    """
    slots = []
    # Boss row (4 centered)
    for i in range(4):
        slots.append(("boss", 3 + i, 0))
    # Galaga rows (8 x 2, centered)
    for row in (1, 2):
        for col in range(1, 9):
            slots.append(("galaga", col, row))
    # Bee rows (10 x 2)
    for row in (3, 4):
        for col in range(10):
            slots.append(("bee", col, row))
    return slots


def slot_to_world(slot_index, slot, wobble_x):
    """Convert a formation slot to world coordinates with the wobble offset."""
    etype, col, row = slot
    x = FORMATION_CX + (col - (FORMATION_COLS - 1) / 2.0) * FORMATION_SLOT_W + wobble_x
    y = FORMATION_TOP + row * FORMATION_SLOT_H
    return x, y
