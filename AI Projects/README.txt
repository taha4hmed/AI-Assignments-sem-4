# AI Search & Turing Test Programs in C

This repository contains three C programs related to Artificial Intelligence concepts:

1. **Missionaries and Cannibals using BFS**
2. **Missionaries and Cannibals using DFS**
3. **Simple Turing Test with CAPTCHA**

These programs demonstrate search algorithms and a basic human verification system.

---

# 1. Missionaries and Cannibals Problem (BFS)

## Description

This program solves the classic **Missionaries and Cannibals river crossing problem** using the **Breadth First Search (BFS)** algorithm.

### Problem Rules

* There are **3 missionaries and 3 cannibals**.
* They must cross a river using a **boat that holds at most 2 people**.
* If **cannibals outnumber missionaries on either side**, the missionaries get eaten.
* The goal is to move everyone from the **left bank to the right bank safely**.

### State Representation

Each state is represented as:

(m, c, b)

Where:

* **m** = missionaries on the left side
* **c** = cannibals on the left side
* **b** = boat position

  * `1` → boat on the left side
  * `0` → boat on the right side

Example:

(3,3,1) → Start state
(0,0,0) → Goal state

### Algorithm Used

The program uses **Breadth First Search (BFS)** to explore states level by level until the goal state is reached.

### Compile

```bash
gcc bfs_missionaries.c -o bfs
```

### Run

```bash
./bfs
```

### Input

No user input is required.

### Output

The program prints the sequence of states explored:

Example:

(3,3,1)
(3,1,0)
(3,2,1)
(3,0,0)
...
(0,0,0)

Each line shows the number of missionaries, cannibals, and the boat position.

---

# 2. Missionaries and Cannibals Problem (DFS)

## Description

This program solves the same problem using **Depth First Search (DFS)** with recursion.

### Algorithm Used

DFS explores one branch of the state space completely before moving to another branch.

### Differences from BFS

* Uses **recursion instead of a queue**
* Does **not guarantee the shortest solution**
* Uses less memory

### Compile

```bash
gcc dfs_missionaries.c -o dfs
```

### Run

```bash
./dfs
```

### Input

No input is required.

### Output

The program prints states visited during DFS traversal.

Example:

(3,3,1)
(3,1,0)
(3,2,1)
(3,0,0)
...

---

# 3. Simple Turing Test with CAPTCHA

## Description

This program simulates a **simple Turing Test** combined with a **CAPTCHA verification system**.

The program first verifies whether the user is human using a randomly generated CAPTCHA and then runs a small chatbot conversation.

### Features

* Random **4-digit CAPTCHA**
* Simple human verification
* Keyword-based chatbot responses

### Compile

```bash
gcc turing_test.c -o turing
```

### Run

```bash
./turing
```

### Input Instructions

Step 1: Enter the CAPTCHA number displayed.

Example:

Enter the CAPTCHA to continue: 4821
User input: 4821

If the CAPTCHA is incorrect, the program will terminate.

Step 2: Answer chatbot questions.

Example conversation:

Bot: Hello! How are you today?
You: I am good

Bot: What is your favorite programming language?
You: C

### Output Example

==== Human Verification Test ====

Enter the CAPTCHA to continue: 5824
5824

Verification Successful.

Bot: Hello! How are you today?
You: I am good
Bot: Glad to hear that!

Bot: What is your favorite programming language?
You: C
Bot: Nice! C is powerful and fast.

Bot: Thanks for chatting. Test complete.

---

# Requirements

* GCC compiler
* Any C compiler compatible with C99
* Linux / macOS / Windows (with MinGW)

---

# Concepts Demonstrated

* State Space Search
* Breadth First Search (BFS)
* Depth First Search (DFS)
* Recursion
* CAPTCHA Verification
* Simple Chatbot Interaction

---

# Author

Mohammed Taha Ahmed
Computer Science Engineering
