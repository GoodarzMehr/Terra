<div align="center">

# 🚀 GALAGA

### *A classic arcade shooter, rebuilt in Python*

A colorful, arcade-style **Galaga** clone built with [`pygame`](https://www.pygame.org).
**Zero external assets** — every sprite is drawn with pygame primitives and every
sound effect is synthesized at runtime with numpy, so the entire game ships in a
single folder.

[![Python](https://img.shields.io/badge/Python-3.8%2B-4B8BBE?logo=python&logoColor=white)](https://www.python.org/)
[![pygame](https://img.shields.io/badge/pygame-2.1%2B-699D66?logo=pygame)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## ✨ Features

| | |
| :-- | :-- |
| 🐝 **Classic enemies** | Red **Bee** (fast & erratic), blue-green **Galaga** (medium), and the big two-part **Boss** (400 pts, takes 2 hits — the first splits it in half). From level 25, **elite** Bosses (tinted yellow) take 3 hits, and from level 50 they take 4. |
| 🛰️ **Choreographed entry** | The formation flies in every level, with Bosses spiraling into their slots. It starts as the classic 40-ship layout and scales up to 76 ships as the levels climb (extra Galaga rows, a 3rd Bee row, and a 5th/6th Boss). |
| 💥 **Dive-bomb waves** | Enemies break formation in V-formations and single runs, curving toward your position and firing as they dive. When your ship is destroyed, divers scatter back to formation instead of hunting your respawn, and no new dive waves start until you respawn and your blinking immunity wears off. A diver that loses its target flies straight through and exits the screen. |
| 📈 **Progressive difficulty** | Each level dives faster, fires more, and sends more simultaneous divers. Bosses get meaner too: their aimed fire can fan out into a 3-way spread, and their homing-bullet chance ramps from 15% to 90% over the first ~95 levels. The ramp is deliberately slow: every parameter keeps escalating for roughly levels 60–100 before it saturates at a sanity bound (dodgeable speeds, minimum gaps), so the game stays in a long "endless escalation" arc. |
| 🔥 **Streak scoring** | Consecutive kills without getting hit double your points (×1 → ×6, the classic "streak" rule). Getting hit resets it to ×1. |
| 🎁 **Power-ups** | Enemies drop **Triple Shot**, **Rapid Fire**, **Shield**, **Bomb**, and **Extra Life**. Bosses always drop one. |
| 👥 **Two-player co-op** | P1 and P2 each have their own ship, lives, and score. |
| 🔊 **Procedural sound** | Lasers, explosions, dive whoosh, and the level-clear jingle are all generated in code (silently degrades if numpy is unavailable). |
| 🏅 **High scores** | Persisted to `highscores.json`. |
| 🖥️ **Any display** | Rendered at 2× scale; the window auto-fits your screen size. |

## 📦 Install

```bash
pip install -r requirements.txt
```

## 🎮 Run

```bash
python main.py
```

The game opens a large **1600×1200** window (2× scale) and automatically
shrinks to fit smaller displays (or scaled displays like 1440p at 175%),
keeping the 4:3 aspect ratio. You can also resize the window manually, or
fill the monitor entirely:

```bash
python main.py --fullscreen
```

<details>
<summary>🧪 Headless self-test (CI / no window needed)</summary>

```bash
python main.py --selftest   # prints SELFTEST OK on success
```

</details>

## 🎯 Controls

| Action | Player 1 | Player 2 |
| :--- | :---: | :---: |
| Move left | `←` | `A` |
| Move right | `→` | `D` |
| Fire | auto | auto |
| Bomb | `↑` | `W` |
| Pause (either) | `P` | `P` |
| Menu / confirm | `Enter` | `Enter` |
| Quit | `Esc` | `Esc` |

## 💯 Scoring

| Enemy | Points |
| :--- | :---: |
| 🐝 Bee | 50 |
| 🛸 Galaga | 100 |
| 👾 Boss | 400 |

Points are multiplied by your current streak (×1–×6). A kill on a **diving**
enemy is worth double its base value.

## 🎁 Power-ups

| Pickup | Effect |
| :--- | :--- |
| ⚡ **Rapid Fire** | Faster fire rate for 8 s |
| ✦ **Triple Shot** | 3-way spread for 10 s |
| ◉ **Shield** | Absorbs one hit |
| 💣 **Bomb** | Stacks; press `↑` (P1) or `W` (P2) to fire a 15-shot fan across a 60° forward cone |
| ♥ **Extra Life** | +1 life |

## 🗂️ Project layout

```text
Galaga/
├── main.py            entry point, game loop, state machine
├── requirements.txt   pygame + numpy
├── LICENSE            MIT
└── galaga/
    ├── config.py      screen size, palette, physics, difficulty curve
    ├── starfield.py   3-layer parallax scrolling stars
    ├── player.py      Player + PlayerBullet
    ├── enemies.py     enemy types, formation, entry paths, dive AI
    ├── particles.py   explosions, trails, screen shake, score popups
    ├── powerups.py    drop table, falling pickups, timed effects
    ├── levels.py      per-level scaling, level-clear detection
    ├── sound.py       procedural SFX (numpy + pygame.sndarray)
    └── hud.py         HUD, menu, level intro, pause, game over
```

> `highscores.json` is created automatically at runtime.

---

<div align="center">

## 📄 License

Released under the [MIT License](LICENSE).

</div>
