# Indian Cities — Shortest Road Path Finder

A Python implementation of **Dijkstra's algorithm** to find the shortest road distance and route between 20 major Indian cities.

## Cities Covered

Agra, Ahmedabad, Bengaluru, Bhubaneswar, Chennai, Delhi, Goa, Hyderabad, Jaipur, Kanpur, Kochi, Kolkata, Lucknow, Mumbai, Patna, Pune, Thiruvananthapuram, Udaipur, Varanasi, Vishakhapatnam

## Dataset

`indian-cities-dataset.csv` contains 86 road connections. Each row: `Origin, Destination, Distance (km)`

## Requirements

Python 3.x — no external libraries required.

## Usage

```bash
python dijkstras.py
```

Enter a source and destination city when prompted.

**Example:**

```
Source city: Delhi
Destination city: Chennai

Distance : 2180 km
Route    : Delhi -> Agra -> Hyderabad -> Chennai
```

## How It Works

- Parses the CSV into an adjacency list, keeping the shorter distance for any duplicate edges
- Uses a min-heap priority queue and a `prev` map to run Dijkstra's and reconstruct the full path
- Handles unreachable city pairs gracefully

## Files

```
├── dijkstras.py
├── indian-cities-dataset.csv
└── README.md
```
