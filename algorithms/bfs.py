"""
bfs.py — Breadth-First Search on the campus graph.

──────────────────────────────────────────────────────────────────────
HOW IT WORKS:
  BFS explores a graph level-by-level from a source node.
  It always visits all neighbours at distance k before moving to k+1.

  1. Enqueue the start node; mark it visited.
  2. While the queue is not empty:
       a. Dequeue the front node (current).
       b. Record it in the traversal order.
       c. Enqueue each unvisited neighbour; mark it visited immediately
          (not when dequeued — this prevents duplicates in the queue).
  3. Stop when the queue is empty.

DATA STRUCTURE — Queue (collections.deque):
  BFS requires FIFO ordering so that nodes are processed in the
  order they were discovered. deque.append() / deque.popleft()
  are both O(1), making this more efficient than a plain list.

SHORTEST PATH (unweighted):
  BFS naturally finds the fewest-hops path in an unweighted graph.
  We track each node's parent to reconstruct the path at the end.
  In a weighted graph this does NOT guarantee minimum distance —
  use Dijkstra for that.

TIME COMPLEXITY  : O(V + E)  — every node and edge visited once
SPACE COMPLEXITY : O(V)      — visited set + queue + parent map
──────────────────────────────────────────────────────────────────────
"""

from collections import deque
from graph.graph import Graph


def bfs_traversal(graph: Graph, start: str) -> list[str]:
    """
    Perform a full BFS traversal from a start location.

    Args:
        graph : The campus Graph
        start : Starting location name
    Returns:
        Ordered list of location names visited during traversal
    Raises:
        KeyError : If start location not in graph
    """
    graph._require_location(start)

    visited: set[str] = set()
    queue: deque[str] = deque()
    order: list[str] = []

    # ── Initialise ──────────────────────────────────────────────────
    queue.append(start)
    visited.add(start)

    # ── Explore ─────────────────────────────────────────────────────
    while queue:
        current = queue.popleft()           # FIFO — O(1) with deque
        order.append(current)

        # Iterate neighbours in sorted order for determinism
        for neighbour in sorted(graph.get_neighbors(current).keys()):
            if neighbour not in visited:
                visited.add(neighbour)      # mark on enqueue, not dequeue
                queue.append(neighbour)

    return order


def bfs_shortest_path(graph: Graph, start: str, goal: str) -> dict:
    """
    Find the shortest path by number of hops using BFS.

    This is the fewest-stops path, ignoring edge weights.
    For minimum distance, use Dijkstra instead.

    Args:
        graph : The campus Graph
        start : Starting location name
        goal  : Destination location name
    Returns:
        dict with keys:
          "path"         : list of location names from start → goal
          "hops"         : number of edges in the path
          "total_dist"   : total distance (m) along this path
          "total_time"   : total time (min) along this path
          "visited_order": order in which nodes were explored
    Raises:
        KeyError    : If start or goal not in graph
        ValueError  : If no path exists
    """
    graph._require_location(start)
    graph._require_location(goal)

    if start == goal:
        return {"path": [start], "hops": 0,
                "total_dist": 0, "total_time": 0, "visited_order": [start]}

    visited: set[str] = {start}
    queue: deque[str] = deque([start])
    parent: dict[str, str | None] = {start: None}
    visited_order: list[str] = []

    while queue:
        current = queue.popleft()
        visited_order.append(current)

        if current == goal:
            path = _reconstruct_path(parent, start, goal)
            dist, time = _path_weights(graph, path)
            return {
                "path": path,
                "hops": len(path) - 1,
                "total_dist": dist,
                "total_time": time,
                "visited_order": visited_order,
            }

        for neighbour in sorted(graph.get_neighbors(current).keys()):
            if neighbour not in visited:
                visited.add(neighbour)
                parent[neighbour] = current
                queue.append(neighbour)

    raise ValueError(f"No path found between '{start}' and '{goal}'.")


# ──────────────────────────────────────────────────────────────────────
# Shared helpers (also imported by dijkstra / astar)
# ──────────────────────────────────────────────────────────────────────

def _reconstruct_path(parent: dict, start: str, goal: str) -> list[str]:
    """Walk the parent map backwards from goal → start, then reverse."""
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def _path_weights(graph: Graph, path: list[str]) -> tuple[float, float]:
    """Sum distance and time along a path."""
    total_dist = total_time = 0.0
    for i in range(len(path) - 1):
        edge = graph.adjacency[path[i]][path[i + 1]]
        total_dist += edge["distance"]
        total_time += edge["time"]
    return total_dist, total_time