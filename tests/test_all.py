"""
test_all.py — Comprehensive pytest test suite for the Campus Navigation System.

Run with:  pytest tests/test_all.py -v
"""

import pytest
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from graph.graph import Graph
from graph.node import Node
from algorithms.bfs import bfs_traversal, bfs_shortest_path
from algorithms.dfs import dfs_traversal, dfs_path, dfs_traversal_iterative
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar


# ══════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def small_graph() -> Graph:
    """
    Simple 5-node graph used across most tests.

    Topology:
        A ──(1)── B ──(2)── C
        |                   |
       (4)                 (1)
        |                   |
        D ──────(3)──────── E
    """
    g = Graph()
    for name, coords in [("A", (0, 0)), ("B", (1, 0)),
                          ("C", (2, 0)), ("D", (0, 1)), ("E", (2, 1))]:
        g.add_location(name, coords)
    g.add_path("A", "B", distance=1,  time=1)
    g.add_path("B", "C", distance=2,  time=2)
    g.add_path("C", "E", distance=1,  time=1)
    g.add_path("A", "D", distance=4,  time=4)
    g.add_path("D", "E", distance=3,  time=3)
    return g


@pytest.fixture
def knust_graph() -> Graph:
    """Full KNUST-inspired graph built by the data_manager."""
    from storage.data_manager import build_default_knust_graph
    return build_default_knust_graph()


# ══════════════════════════════════════════════════════════════════════
# Node tests
# ══════════════════════════════════════════════════════════════════════

class TestNode:
    def test_creation(self):
        n = Node("Library", (40, 70), "Main library")
        assert n.name == "Library"
        assert n.coords == (40, 70)
        assert n.description == "Main library"

    def test_invalid_name(self):
        with pytest.raises(ValueError):
            Node("", (0, 0))

    def test_invalid_coords(self):
        with pytest.raises(ValueError):
            Node("X", [1, 2])   # list, not tuple

    def test_equality(self):
        n1 = Node("A", (0, 0))
        n2 = Node("A", (5, 5))
        assert n1 == n2          # equality based on name only

    def test_serialisation_round_trip(self):
        n = Node("Library", (40, 70), "Books")
        assert Node.from_dict(n.to_dict()) == n


# ══════════════════════════════════════════════════════════════════════
# Graph tests
# ══════════════════════════════════════════════════════════════════════

class TestGraph:
    def test_add_location(self, small_graph):
        small_graph.add_location("F", (3, 3))
        assert "F" in small_graph.locations

    def test_duplicate_location_raises(self, small_graph):
        with pytest.raises(ValueError):
            small_graph.add_location("A", (0, 0))

    def test_remove_location(self, small_graph):
        small_graph.remove_location("D")
        assert "D" not in small_graph.locations
        assert "D" not in small_graph.adjacency["A"]

    def test_add_path(self, small_graph):
        small_graph.add_location("F", (3, 3))
        small_graph.add_path("C", "F", 5, 5)
        assert small_graph.has_path("C", "F")
        assert small_graph.has_path("F", "C")    # undirected

    def test_add_path_negative_distance_raises(self, small_graph):
        with pytest.raises(ValueError):
            small_graph.add_path("A", "C", -1, 1)

    def test_remove_path(self, small_graph):
        small_graph.remove_path("A", "B")
        assert not small_graph.has_path("A", "B")

    def test_remove_nonexistent_path_raises(self, small_graph):
        with pytest.raises(KeyError):
            small_graph.remove_path("A", "C")

    def test_update_path(self, small_graph):
        small_graph.update_path("A", "B", distance=99)
        assert small_graph.adjacency["A"]["B"]["distance"] == 99
        assert small_graph.adjacency["B"]["A"]["distance"] == 99  # undirected

    def test_get_neighbors(self, small_graph):
        neighbours = set(small_graph.get_neighbors("A").keys())
        assert neighbours == {"B", "D"}

    def test_stats(self, small_graph):
        s = small_graph.stats()
        assert s["nodes"] == 5
        assert s["edges"] == 5

    def test_serialisation_round_trip(self, small_graph):
        data = small_graph.to_dict()
        g2 = Graph.from_dict(data)
        assert set(g2.locations.keys()) == set(small_graph.locations.keys())
        assert g2.adjacency["A"]["B"]["distance"] == small_graph.adjacency["A"]["B"]["distance"]


# ══════════════════════════════════════════════════════════════════════
# BFS tests
# ══════════════════════════════════════════════════════════════════════

class TestBFS:
    def test_traversal_visits_all_nodes(self, small_graph):
        order = bfs_traversal(small_graph, "A")
        assert set(order) == set(small_graph.locations.keys())

    def test_traversal_start_is_first(self, small_graph):
        order = bfs_traversal(small_graph, "A")
        assert order[0] == "A"

    def test_bfs_visits_neighbours_before_deeper_nodes(self, small_graph):
        order = bfs_traversal(small_graph, "A")
        # B and D (A's direct neighbours) must appear before C and E
        assert order.index("B") < order.index("C")
        assert order.index("D") < order.index("E")

    def test_shortest_path_a_to_e(self, small_graph):
        r = bfs_shortest_path(small_graph, "A", "E")
        # Shortest hop path: A → B → C → E  (3 hops)  or  A → D → E  (2 hops)?
        # BFS finds fewest hops: A → D → E = 2 hops
        assert r["hops"] == 2

    def test_same_start_goal(self, small_graph):
        r = bfs_shortest_path(small_graph, "A", "A")
        assert r["path"] == ["A"]
        assert r["hops"] == 0

    def test_no_path_raises(self):
        g = Graph()
        g.add_location("X", (0, 0))
        g.add_location("Y", (1, 1))
        with pytest.raises(ValueError):
            bfs_shortest_path(g, "X", "Y")

    def test_invalid_start_raises(self, small_graph):
        with pytest.raises(KeyError):
            bfs_traversal(small_graph, "NONEXISTENT")


# ══════════════════════════════════════════════════════════════════════
# DFS tests
# ══════════════════════════════════════════════════════════════════════

class TestDFS:
    def test_traversal_visits_all_nodes(self, small_graph):
        order = dfs_traversal(small_graph, "A")
        assert set(order) == set(small_graph.locations.keys())

    def test_traversal_start_is_first(self, small_graph):
        assert dfs_traversal(small_graph, "A")[0] == "A"

    def test_iterative_visits_all_nodes(self, small_graph):
        order = dfs_traversal_iterative(small_graph, "A")
        assert set(order) == set(small_graph.locations.keys())

    def test_dfs_path_finds_a_path(self, small_graph):
        r = dfs_path(small_graph, "A", "E")
        assert r["path"][0] == "A"
        assert r["path"][-1] == "E"

    def test_dfs_path_same_start_goal(self, small_graph):
        r = dfs_path(small_graph, "A", "A")
        assert r["path"] == ["A"]

    def test_no_path_raises(self):
        g = Graph()
        g.add_location("X", (0, 0))
        g.add_location("Y", (1, 1))
        with pytest.raises(ValueError):
            dfs_path(g, "X", "Y")


# ══════════════════════════════════════════════════════════════════════
# Dijkstra tests
# ══════════════════════════════════════════════════════════════════════

class TestDijkstra:
    def test_shortest_distance_a_to_e(self, small_graph):
        r = dijkstra(small_graph, "A", "E", "distance")
        # A→B=1, B→C=2, C→E=1 → total 4
        # A→D=4, D→E=3       → total 7
        # Dijkstra must choose A→B→C→E = 4
        assert r["total_dist"] == pytest.approx(4.0)
        assert r["path"] == ["A", "B", "C", "E"]

    def test_shortest_time_a_to_e(self, small_graph):
        r = dijkstra(small_graph, "A", "E", "time")
        assert r["total_time"] == pytest.approx(4.0)

    def test_visited_order_starts_with_source(self, small_graph):
        r = dijkstra(small_graph, "A", "E")
        assert r["visited_order"][0] == "A"

    def test_invalid_weight_raises(self, small_graph):
        with pytest.raises(ValueError):
            dijkstra(small_graph, "A", "E", weight="speed")

    def test_no_path_raises(self):
        g = Graph()
        g.add_location("X", (0, 0))
        g.add_location("Y", (1, 1))
        with pytest.raises(ValueError):
            dijkstra(g, "X", "Y")

    def test_knust_main_gate_to_engineering(self, knust_graph):
        r = dijkstra(knust_graph, "Main Gate", "Engineering Block", "distance")
        assert r["total_dist"] > 0
        assert r["path"][0] == "Main Gate"
        assert r["path"][-1] == "Engineering Block"


# ══════════════════════════════════════════════════════════════════════
# A* tests
# ══════════════════════════════════════════════════════════════════════

class TestAStar:
    def test_same_optimal_path_as_dijkstra(self, small_graph):
        d = dijkstra(small_graph, "A", "E", "distance")
        a = astar(small_graph, "A", "E", "distance")
        assert a["path"] == d["path"]
        assert a["total_dist"] == pytest.approx(d["total_dist"])

    def test_astar_explores_fewer_or_equal_nodes(self, knust_graph):
        d = dijkstra(knust_graph, "Main Gate", "Engineering Block", "distance")
        a = astar(knust_graph, "Main Gate", "Engineering Block", "distance")
        # A* should explore ≤ nodes than Dijkstra for spatial graphs
        assert len(a["visited_order"]) <= len(d["visited_order"])

    def test_astar_same_start_goal(self, small_graph):
        r = astar(small_graph, "A", "A")
        assert r["path"] == ["A"]

    def test_invalid_weight_raises(self, small_graph):
        with pytest.raises(ValueError):
            astar(small_graph, "A", "E", weight="speed")

    def test_no_path_raises(self):
        g = Graph()
        g.add_location("X", (0, 0))
        g.add_location("Y", (1, 1))
        with pytest.raises(ValueError):
            astar(g, "X", "Y")

    def test_knust_astar_optimal(self, knust_graph):
        r_dijk = dijkstra(knust_graph, "Main Gate", "Lecture Hall", "distance")
        r_ast  = astar(knust_graph,   "Main Gate", "Lecture Hall", "distance")
        assert r_ast["total_dist"] == pytest.approx(r_dijk["total_dist"])