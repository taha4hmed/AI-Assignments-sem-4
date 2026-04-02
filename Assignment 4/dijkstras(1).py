import heapq
import csv
import os
import sys


def build_graph(filepath):
    graph = {}
    with open(filepath, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            src = row['Origin'].strip()
            dst = row['Destination'].strip()
            dist = int(row['Distance'].strip())
            for a, b in [(src, dst), (dst, src)]:
                if a not in graph:
                    graph[a] = {}
                if b not in graph[a] or graph[a][b] > dist:
                    graph[a][b] = dist
    return graph


def shortest_path(graph, source, target):
    dist = {source: 0}
    prev = {source: None}
    heap = [(0, source)]

    while heap:
        cost, node = heapq.heappop(heap)
        if node == target:
            break
        if cost > dist.get(node, float('inf')):
            continue
        for neighbor, weight in graph.get(node, {}).items():
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_cost
                prev[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))

    if target not in dist:
        return float('inf'), []

    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return dist[target], path


def main():
    csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indian-cities-dataset.csv')

    if not os.path.exists(csv_file):
        print(f"Dataset not found: {csv_file}")
        sys.exit(1)

    graph = build_graph(csv_file)
    cities = sorted(graph.keys())

    print("-" * 48)
    print("   Indian Cities — Shortest Road Path Finder")
    print("-" * 48)
    print(f"\n{len(cities)} cities available:\n")
    for i, city in enumerate(cities, 1):
        print(f"  {i:2}. {city}")

    print()
    source = input("Source city: ").strip()
    if source not in graph:
        print(f"'{source}' not found in dataset.")
        return

    target = input("Destination city: ").strip()
    if target not in graph:
        print(f"'{target}' not found in dataset.")
        return

    if source == target:
        print("Source and destination are the same.")
        return

    total, route = shortest_path(graph, source, target)

    print()
    if not route:
        print(f"No path exists between {source} and {target}.")
    else:
        print(f"Distance : {total} km")
        print(f"Route    : {' -> '.join(route)}")


if __name__ == '__main__':
    main()
