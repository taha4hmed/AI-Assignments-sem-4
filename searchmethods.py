from collections import deque
import time

MISSIONARIES = 3
CANNIBALS = 3

class RiverNode:
    def __init__(self, left_m, left_c, side, prev=None):
        self.left_m = left_m
        self.left_c = left_c
        self.side = side  # 1 = boat on left, 0 = boat on right
        self.prev = prev

    def reached_goal(self):
        return self.left_m == 0 and self.left_c == 0 and self.side == 0

    def is_safe(self):
        right_m = MISSIONARIES - self.left_m
        right_c = CANNIBALS - self.left_c

        if not (0 <= self.left_m <= MISSIONARIES and 0 <= self.left_c <= CANNIBALS):
            return False
        if self.left_m > 0 and self.left_c > self.left_m:
            return False
        if right_m > 0 and right_c > right_m:
            return False
        return True

    def __repr__(self):
        location = "Left" if self.side == 1 else "Right"
        return f"[M={self.left_m}, C={self.left_c}, Boat@{location}]"


CROSSING_OPTIONS = [(1,0), (2,0), (0,1), (0,2), (1,1)]

def expand_node(node):
    children = []
    for dm, dc in CROSSING_OPTIONS:
        if node.side == 1:
            nxt = RiverNode(node.left_m - dm, node.left_c - dc, 0, node)
        else:
            nxt = RiverNode(node.left_m + dm, node.left_c + dc, 1, node)
        if nxt.is_safe():
            children.append(nxt)
    return children

def trace_back(node):
    steps = []
    while node:
        steps.append(node)
        node = node.prev
    return steps[::-1]

def fingerprint(node):
    return (node.left_m, node.left_c, node.side)


# ---------------- BFS ----------------
def breadth_first(root):
    seen = set()
    frontier = deque([root])
    count = 0
    print("\nBFS Traversal:")
    while frontier:
        curr = frontier.popleft()
        count += 1
        print(curr)
        if curr.reached_goal():
            return trace_back(curr), count
        fp = fingerprint(curr)
        if fp in seen:
            continue
        seen.add(fp)
        for child in expand_node(curr):
            if fingerprint(child) not in seen:
                frontier.append(child)
    return None, count


# ---------------- DFS ----------------
def depth_first(root):
    seen = set()
    frontier = [root]
    count = 0
    print("\nDFS Traversal:")
    while frontier:
        curr = frontier.pop()
        count += 1
        print(curr)
        if curr.reached_goal():
            return trace_back(curr), count
        fp = fingerprint(curr)
        if fp in seen:
            continue
        seen.add(fp)
        for child in expand_node(curr):
            if fingerprint(child) not in seen:
                frontier.append(child)
    return None, count


# ---------------- Depth Limited Search ----------------
def depth_limited(root, cap):
    frontier = [(root, 0)]
    seen = set()
    count = 0
    print(f"\nDepth-Limited Search (cap={cap}):")
    while frontier:
        curr, lvl = frontier.pop()
        count += 1
        print(curr, " level=", lvl)
        if curr.reached_goal():
            return trace_back(curr), count
        seen.add(fingerprint(curr))
        if lvl < cap:
            for child in expand_node(curr):
                if fingerprint(child) not in seen:
                    frontier.append((child, lvl + 1))
    return None, count


# ---------------- Iterative Deepening ----------------
def iterative_deepening(root, ceiling):
    grand_total = 0
    for threshold in range(ceiling):
        print(f"\nIDS — threshold = {threshold}")
        result, count = depth_limited(root, threshold)
        grand_total += count
        if result:
            return result, grand_total
    return None, grand_total


# ---------------- MAIN ----------------
origin = RiverNode(3, 3, 1)

print("\n========== BFS ==========")
t = time.time()
path, n = breadth_first(origin)
print("\nPath Found:", path)
print("Nodes Visited:", n)
print("Elapsed:", round(time.time() - t, 6), "s")

print("\n========== DFS ==========")
t = time.time()
path, n = depth_first(origin)
print("\nPath Found:", path)
print("Nodes Visited:", n)
print("Elapsed:", round(time.time() - t, 6), "s")

print("\n========== Depth Limited DFS ==========")
t = time.time()
path, n = depth_limited(origin, 20)
print("\nPath Found:", path)
print("Nodes Visited:", n)
print("Elapsed:", round(time.time() - t, 6), "s")

print("\n========== Iterative Deepening ==========")
t = time.time()
path, n = iterative_deepening(origin, 20)
print("\nPath Found:", path)
print("Nodes Visited:", n)
print("Elapsed:", round(time.time() - t, 6), "s")