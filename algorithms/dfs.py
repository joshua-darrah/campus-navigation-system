"""
dfs.py — Depth-First Search on the campus graph.

──────────────────────────────────────────────────────────────────────
HOW IT WORKS:
  DFS explores as far as possible along each branch before backtracking.

  Recursive version (used here — natural call stack acts as the stack):
    1. Mark the current node visited; record it.
    2. For each unvisited neighbour, recurse.
    3. Backtrack when all neighbours are explored.

  Iterative version (also implemented below for comparison):
    1. Push start onto an explicit stack.
    2. While stack is not empty: pop, visit, push unvisited neighbours.

DATA STRUCTURE — Call stack / explicit Stack (list):
  DFS uses LIFO ordering. The recursive implementation uses Python's
  call stack implicitly. The iterative version uses a list as a stack
  (list.append() / list.pop() are both O(1) amortised).

TIME COMPLEXITY  : O(V + E)  — every node and edge examined once
SPACE COMPLEXITY : O(V)      — visited set + recursion depth / stack

NOTE ON DFS vs BFS:
  • BFS finds shortest hop-count path; DFS does NOT guarantee shortest
    path in any sense.
  • DFS is useful for: cycle detection, topological sort, maze solving,
    connectivity checks.
──────────────────────────────────────────────────────────────────────
"""

from graph.graph import Graph
from algorithms.bfs import _reconstruct_path, _path_weights


def dfs_traversal(graph: Graph, start: str) -> list[str]:
    """
    Perform a full DFS traversal from a start location (recursive).

    Args:
        graph : The campus Graph
        start : Starting location name
    Returns:
        Ordered list of location names in DFS visit order
    """
    graph._require_location(start)
    visited: set[str] = set()
    order: list[str] = []

    def _dfs(node: str) -> None:
        visited.add(node)
        order.append(node)
        for neighbour in sorted(graph.get_neighbors(node).keys()):
            if neighbour not in visited:
                _dfs(neighbour)

    _dfs(start)
    return order


def dfs_traversal_iterative(graph: Graph, start: str) -> list[str]:
    """
    Iterative DFS using an explicit stack (list).

    Produces a different (but equally valid) DFS order vs the recursive
    version, because the stack reverses neighbour processing order.
    Provided here so students can compare both approaches.
    """
    graph._require_location(start)
    visited: set[str] = set()
    stack: list[str] = [start]
    order: list[str] = []

    while stack:
        node = stack.pop()                  # LIFO — O(1)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        # Push in reverse-sorted order so smaller names are explored first
        for neighbour in sorted(graph.get_neighbors(node).keys(), reverse=True):
            if neighbour not in visited:
                stack.append(neighbour)

    return order


def dfs_path(graph: Graph, start: str, goal: str) -> dict:
    """
    Find *a* path from start to goal using DFS.

    WARNING: This is NOT necessarily the shortest path.
    The path found depends entirely on the order neighbours are explored.
    Use Dijkstra or A* for optimal routing.

    Args:
        graph : The campus Graph
        start : Starting location name
        goal  : Destination location name
    Returns:
        dict with keys:
          "path"         : list of location names from start → goal
          "hops"         : number of edges
          "total_dist"   : total distance (m)
          "total_time"   : total time (min)
          "visited_order": exploration order
    Raises:
        KeyError  : If start or goal not in graph
        ValueError: If no path exists
    """
    graph._require_location(start)
    graph._require_location(goal)

    if start == goal:
        return {"path": [start], "hops": 0,
                "total_dist": 0, "total_time": 0, "visited_order": [start]}

    visited: set[str] = set()
    parent: dict[str, str | None] = {start: None}
    visited_order: list[str] = []
    found = [False]  # mutable flag accessible inside nested function

    def _dfs(node: str) -> None:
        if found[0]:
            return
        visited.add(node)
        visited_order.append(node)

        if node == goal:
            found[0] = True
            return

        for neighbour in sorted(graph.get_neighbors(node).keys()):
            if neighbour not in visited and not found[0]:
                parent[neighbour] = node
                _dfs(neighbour)

    _dfs(start)

    if not found[0]:
        raise ValueError(f"No path found between '{start}' and '{goal}'.")

    path = _reconstruct_path(parent, start, goal)
    dist, time = _path_weights(graph, path)
    return {
        "path": path,
        "hops": len(path) - 1,
        "total_dist": dist,
        "total_time": time,
        "visited_order": visited_order,
    }