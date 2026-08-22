# Galaga — Python Arcade

A colorful, arcade-style **Galaga** clone built with `pygame`. No external assets:
every sprite is drawn with pygame primitives and every sound effect is synthesized
at runtime with numpy, so the whole game ships in a single folder.

## Features

- **Classic enemies** — red **Bee** (fast & erratic), blue-green **Galaga** (medium),
  and the big two-part **Boss** (worth 400 pts, takes 2 hits — the first splits it in half).
- **Choreographed fleet entry** — the 40-ship formation flies in each level, with
  Bosses spiraling into their slots.
- **Dive-bomb waves** — enemies break formation in V-formations and single runs,
  curving toward your position and firing as they dive.
- **Progressive difficulty** — each level dives faster, fires more, and sends more
  simultaneous divers. The curve is capped at level 10 so the game stays beatable.
- **Streak scoring** — consecutive kills without getting hit double your points
  (×1 → ×6, the classic "streak" rule). Getting hit resets it to ×1.
- **Power-ups** — enemies drop pickups: **Triple Shot**, **Rapid Fire**, **Shield**,
  and **Extra Life**. Bosses always drop one.
- **Two-player co-op** — P1 and P2 each have their own ship, lives, and score.
- **Procedural sound** — lasers, explosions, dive whoosh, and the level-clear jingle
  are all generated in code (silently degrades if numpy is unavailable).
- **High scores** — persisted to `highscores.json`.
- **Big screen** — rendered at 2× scale in a 1600×1200 window (everything is twice as large).

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The game opens a large **1600×1200** window (2× scale). If that's bigger than
your screen, run it fullscreen instead:

```bash
python main.py --fullscreen
```

Add `--selftest` to run a headless automated smoke test (no window needed):

```bash
SDL_VIDEODRIVER=dummy python main.py --selftest
```

## Controls

| Action | Player 1 | Player 2 |
| :--- | :--- | :--- |
| Move left | `A` | `←` |
| Move right | `D` | `→` |
| Fire | `Space` | `L` |
| Pause (either) | `P` | `P` |
| Menu / confirm | `Enter` | `Enter` |
| Quit | `Esc` | `Esc` |

## Scoring

| Enemy | Points |
| :--- | :--- |
| Bee | 50 |
| Galaga | 100 |
| Boss | 400 |

Points are multiplied by your current streak (×1–×6). A kill on a diving enemy is
worth double its base value.

## Power-ups

| Pickup | Effect |
| :--- | :--- |
| ⚡ Rapid Fire | Faster fire rate for 8 s |
| ✦ Triple Shot | 3-way spread for 10 s |
| ◉ Shield | Absorbs one hit |
| ♥ Extra Life | +1 life |

## Project layout

```text
main.py            entry point, game loop, state machine
galaga/
  config.py        screen size, palette, physics, difficulty curve
  starfield.py     3-layer parallax scrolling stars
  player.py        Player + PlayerBullet
  enemies.py       enemy types, formation, entry paths, dive AI
  particles.py     explosions, trails, screen shake, score popups
  powerups.py      drop table, falling pickups, timed effects
  levels.py        per-level scaling, level-clear detection
  sound.py         procedural SFX (numpy + pygame.sndarray)
  hud.py           HUD, menu, level intro, pause, game over
highscores.json    created at runtime
```

## License

Released under the [MIT License](LICENSE).
