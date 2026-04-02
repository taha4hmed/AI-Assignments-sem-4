# UGV Path Planning — Battlefield Navigation

A simulation of an **Unmanned Ground Vehicle (UGV)** navigating a 70×70 km battlefield using **Dijkstra's algorithm**, covering both static and dynamic obstacle scenarios.

---

## Problem Overview

Design a navigation system that routes a UGV from a start position to a goal while avoiding obstacles, and report Measures of Effectiveness (MoE).

Two scenarios are covered:

**Part 1 — Static Terrain:** Obstacles are fixed and known before the mission starts.

**Part 2 — Dynamic Patrols:** Enemy patrols move during navigation and are unknown in advance.

---

## How It Works

### Part 1: Static Navigation

- A 70×70 binary grid is generated at a configurable obstacle density.
- Dijkstra's algorithm finds the shortest route from `(0,0)` to `(69,69)`.
- Diagonal moves cost `1.41`; cardinal moves cost `1.0`.
- Visited nodes are tracked separately for MoE reporting.

**MoE Reported:**

| Metric | Description |
|---|---|
| Path Distance | Total edge-weight cost (km) |
| Path Efficiency | Straight-line distance ÷ actual path distance (%) |
| Search Effort | Percentage of grid cells explored (%) |

---

### Part 2: Dynamic Patrol Simulation

Uses a **Sense → Replan → Step** loop:

1. **Move patrols** — 40 patrols slide +1 on the column axis each turn (wraps at boundary).
2. **Replan** — Dijkstra runs from the UGV's current position on an updated map.
3. **Step** — UGV moves one cell forward along the new route.

**Safety cutoffs:**
- No path found → mission failure (cornered).
- Steps exceed `4 × grid size` → mission failure (thrashing).

**MoE Reported:**

| Metric | Description |
|---|---|
| Steps Taken | Total moves made |
| Total Distance | Cumulative km travelled |
| Evasive Penalty | Extra km vs. static baseline (success only) |

---

## Visualization

- **Static path** — red solid line; cyan dots show explored area.
- **Dynamic path** — orange dashed line.
- Start = green dot · Goal = blue star.

---

## Requirements

```
Python 3.8+
numpy
matplotlib
jupyter
```

Install:
```bash
pip install numpy matplotlib jupyter
```

## Running

```bash
jupyter notebook ugv.ipynb
```

Run the four cells in order:
1. Static terrain + Dijkstra
2. Static path visualization + MoE
3. Dynamic patrol simulation
4. Dynamic path visualization + MoE

---

## Configuration

Edit the constants at the top of **Cell 1**:

| Parameter | Default | Description |
|---|---|---|
| `GRID` | 70 | Grid side length (km) |
| `OBS` | 0.2 | Obstacle density (0.0 – 1.0) |
| `ORIGIN` | (0, 0) | Start cell |
| `TARGET` | (69, 69) | Goal cell |
| `NUM_PATROLS` | 40 | Number of moving enemy patrols |

---

## Files

```
├── ugv.ipynb
└── README.md
```
