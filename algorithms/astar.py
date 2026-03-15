"""
astar.py — A* Pathfinding Algorithm on the campus graph.

──────────────────────────────────────────────────────────────────────
HOW IT WORKS:
  A* is an informed search algorithm that combines Dijkstra's guaranteed
  optimality with a heuristic that guides the search toward the goal,
  reducing the number of nodes explored.

  For each node n, A* maintains:
    f(n) = g(n) + h(n)

    g(n) = exact cost from start to n (like Dijkstra)
    h(n) = heuristic estimated cost from n to goal

  The heuristic used here is the Euclidean distance between node
  coordinates — an admissible heuristic because it never overestimates
  the real path distance.

  Algorithm:
    1. Push (f(start), g(start), start) onto the min-heap.
    2. While heap not empty:
         a. Pop node with smallest f value.
         b. If goal reached, reconstruct path.
         c. For each neighbour, compute g(neighbour) = g(current) + edge_weight.
         d. If better than known g, update and push (f, g, neighbour).

DATA STRUCTURE — Min-Heap (heapq):
  Same as Dijkstra. The only difference is the heap key: Dijkstra uses
  g(n) alone, A* uses f(n) = g(n) + h(n).

  This means A* "steers" toward the goal rather than expanding evenly
  in all directions, making it faster in practice on spatial graphs.

ADMISSIBILITY:
  A heuristic is admissible if h(n) ≤ true cost to goal.
  Euclidean distance on a coordinate grid is admissible as long as
  the actual path cannot be shorter than a straight line.

WHY A* BEATS DIJKSTRA HERE:
  On our campus map, nodes have (x, y) coordinates. A* can skip
  exploring nodes that are far from the goal, while Dijkstra explores
  all reachable nodes up to the goal's cost.

TIME COMPLEXITY  : O((V + E) log V)  — worst case same as Dijkstra,
                   but typically much faster in practice
SPACE COMPLEXITY : O(V)
──────────────────────────────────────────────────────────────────────
"""

import heapq
import math
from graph.graph import Graph
from algorithms.bfs import _reconstruct_path, _path_weights


def _euclidean_heuristic(graph: Graph, node: str, goal: str) -> float:
    """
    Euclidean distance between two nodes' coordinates.

    Used as an admissible heuristic for A*.
    The coordinate grid is unitless (0–100 scale), so we apply a
    scaling factor to bring the heuristic into the same ballpark as
    real distances (metres). Scale factor ≈ 10 m per grid unit.
    """
    SCALE = 10.0
    x1, y1 = graph.locations[node].coords
    x2, y2 = graph.locations[goal].coords
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * SCALE


def astar(
    graph: Graph,
    start: str,
    goal: str,
    weight: str = "distance"
) -> dict:
    """
    Find the shortest path using A* with a Euclidean heuristic.

    Args:
        graph  : The campus Graph (nodes must have .coords for heuristic)
        start  : Starting location name
        goal   : Destination location name
        weight : Edge attribute to minimise — "distance" (default) or "time"
    Returns:
        dict with keys:
          "path"         : list of location names, start → goal
          "cost"         : minimum total weight
          "total_dist"   : total distance (m)
          "total_time"   : total time (min)
          "visited_order": nodes popped from heap in exploration order
    Raises:
        KeyError  : If start or goal not in graph
        ValueError: If weight invalid or no path exists
    """
    graph._require_location(start)
    graph._require_location(goal)
    if weight not in ("distance", "time"):
        raise ValueError("weight must be 'distance' or 'time'.")

    INF = float("inf")
    g: dict[str, float] = {node: INF for node in graph.locations}
    g[start] = 0.0
    parent: dict[str, str | None] = {start: None}
    visited_order: list[str] = []

    # Heap entries: (f_score, g_score, node_name)
    # g_score included as tiebreaker so equal-f nodes are compared by cost
    h_start = _euclidean_heuristic(graph, start, goal)
    heap: list[tuple[float, float, str]] = [(h_start, 0.0, start)]

    while heap:
        f, g_curr, current = heapq.heappop(heap)

        # Skip stale entries
        if g_curr > g[current]:
            continue

        visited_order.append(current)

        if current == goal:
            break

        for neighbour, edge_data in graph.get_neighbors(current).items():
            tentative_g = g[current] + edge_data[weight]

            if tentative_g < g[neighbour]:
                g[neighbour] = tentative_g
                parent[neighbour] = current
                h = _euclidean_heuristic(graph, neighbour, goal)
                f_new = tentative_g + h
                heapq.heappush(heap, (f_new, tentative_g, neighbour))

    if g[goal] == INF:
        raise ValueError(f"No path found between '{start}' and '{goal}'.")

    path = _reconstruct_path(parent, start, goal)
    total_dist, total_time = _path_weights(graph, path)

    return {
        "path": path,
        "cost": g[goal],
        "total_dist": total_dist,
        "total_time": total_time,
        "visited_order": visited_order,
    }