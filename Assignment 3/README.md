# Missionaries and Cannibals — Uninformed Search

A Python implementation of classic uninformed search algorithms applied to the Missionaries and Cannibals river crossing problem.

> **Author:** Mohammed Taha Ahmed (SE24UCSE073)

---

## Problem Statement

Three missionaries and three cannibals need to cross a river. A boat is available that can carry at most two people at a time.

**Rules:**
- At least one person must be in the boat for each crossing.
- On either bank, if cannibals outnumber missionaries, the missionaries are killed.
- The goal is to transport everyone to the right bank without any violations.

---

## Algorithms Used

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Depth-Limited Search (DLS)
- Iterative Deepening Search (IDS)

---

## How to Run
```bash
python search_algorithms.py
```

---

## Output Includes

- State expansion order for each algorithm
- Final solution path
- Total nodes explored
- Time taken

---

## Algorithm Comparison

| Algorithm | Optimal? | Memory |
|-----------|----------|--------|
| BFS       | Yes      | High   |
| DFS       | No       | Low    |
| DLS       | Depends  | Low    |
| IDS       | Yes      | Moderate |
