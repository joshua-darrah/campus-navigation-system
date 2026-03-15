"""
dijkstra.py — Dijkstra's Shortest Path Algorithm on the campus graph.

──────────────────────────────────────────────────────────────────────
HOW IT WORKS:
  Dijkstra finds the minimum-cost path from a source to all other nodes
  in a graph with non-negative edge weights.

  1. Assign distance 0 to the source; ∞ to all others.
  2. Insert source into a min-heap (priority queue) as (0, source).
  3. While the heap is not empty:
       a. Pop the node with the smallest known distance (current).
       b. If already finalised, skip (stale heap entry).
       c. For each neighbour, compute tentative distance =
          dist[current] + edge_weight.
       d. If tentative < dist[neighbour], update and push to heap.
  4. Reconstruct the shortest path using the parent map.

DATA STRUCTURE — Min-Heap / Priority Queue (heapq):
  heapq.heappush / heappop provide O(log V) insertion and extraction,
  giving Dijkstra its overall O((V + E) log V) complexity with a
  binary heap. Without a priority queue, the naive version is O(V²).

  We support optimisation by DISTANCE or by TIME — both are valid
  weights stored on each edge.

TIME COMPLEXITY  : O((V + E) log V)  with a binary heap
SPACE COMPLEXITY : O(V)              dist map + parent map + heap
──────────────────────────────────────────────────────────────────────
"""

import heapq
from graph.graph import Graph
from algorithms.bfs import _reconstruct_path, _path_weights


def dijkstra(
    graph: Graph,
    start: str,
    goal: str,
    weight: str = "distance"
) -> dict:
    """
    Find the shortest (minimum-weight) path using Dijkstra's algorithm.

    Args:
        graph  : The campus Graph
        start  : Starting location name
        goal   : Destination location name
        weight : Edge attribute to minimise — "distance" (default) or "time"
    Returns:
        dict with keys:
          "path"         : list of location names, start → goal
          "cost"         : minimum total weight (distance or time)
          "total_dist"   : total distance in metres along the path
          "total_time"   : total time in minutes along the path
          "visited_order": nodes popped from the heap in exploration order
    Raises:
        KeyError  : If start or goal not in graph
        ValueError: If weight is not "distance" or "time", or no path exists
    """
    graph._require_location(start)
    graph._require_location(goal)
    if weight not in ("distance", "time"):
        raise ValueError("weight must be 'distance' or 'time'.")

    # ── Initialise ──────────────────────────────────────────────────
    INF = float("inf")
    dist: dict[str, float] = {node: INF for node in graph.locations}
    dist[start] = 0.0
    parent: dict[str, str | None] = {start: None}
    visited_order: list[str] = []

    # Min-heap entries: (cost, node_name)
    heap: list[tuple[float, str]] = [(0.0, start)]

    # ── Main loop ───────────────────────────────────────────────────
    while heap:
        current_cost, current = heapq.heappop(heap)   # O(log V)

        # Skip stale entries (node already finalised with lower cost)
        if current_cost > dist[current]:
            continue

        visited_order.append(current)

        if current == goal:
            break

        for neighbour, edge_data in graph.get_neighbors(current).items():
            tentative = dist[current] + edge_data[weight]

            if tentative < dist[neighbour]:
                dist[neighbour] = tentative
                parent[neighbour] = current
                heapq.heappush(heap, (tentative, neighbour))   # O(log V)

    # ── Result ──────────────────────────────────────────────────────
    if dist[goal] == INF:
        raise ValueError(f"No path found between '{start}' and '{goal}'.")

    path = _reconstruct_path(parent, start, goal)
    total_dist, total_time = _path_weights(graph, path)

    return {
        "path": path,
        "cost": dist[goal],
        "total_dist": total_dist,
        "total_time": total_time,
        "visited_order": visited_order,
    }