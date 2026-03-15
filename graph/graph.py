"""
graph.py — Core graph data structure for the Campus Navigation System.

REPRESENTATION:
  Adjacency List using nested Python dictionaries (hash maps).

  self.adjacency[node_name][neighbour_name] = {
      "distance": float,   # metres
      "time":     float    # minutes
  }

  This gives O(1) average-case lookup for both nodes and edges,
  and O(V + E) space — efficient for the sparse graphs typical of
  a campus map.

DATA STRUCTURES USED:
  • dict (hash map) — node registry and adjacency list
  • set              — fast membership testing when adding edges
"""

import json
from graph.node import Node


class Graph:
    """
    Undirected, weighted graph representing a campus map.

    Nodes  → campus buildings / locations
    Edges  → paths between locations, weighted by distance (m) and time (min)
    """

    def __init__(self):
        # Hash map: name → Node object
        self.locations: dict[str, Node] = {}

        # Adjacency list: name → {neighbour_name: {"distance": d, "time": t}}
        self.adjacency: dict[str, dict] = {}

    # ==================================================================
    # Node operations
    # ==================================================================

    def add_location(self, name: str, coords: tuple[float, float], description: str = "") -> None:
        """
        Add a campus location (node) to the graph.

        Args:
            name        : Unique location name
            coords      : (x, y) map coordinates
            description : Optional description
        Raises:
            ValueError  : If the location already exists
        """
        if name in self.locations:
            raise ValueError(f"Location '{name}' already exists.")
        node = Node(name, coords, description)
        self.locations[name] = node
        self.adjacency[name] = {}

    def remove_location(self, name: str) -> None:
        """
        Remove a location and all its connected paths.

        Args:
            name : Location to remove
        Raises:
            KeyError : If the location does not exist
        """
        self._require_location(name)
        # Remove all edges that referenced this node
        for neighbour in list(self.adjacency[name].keys()):
            del self.adjacency[neighbour][name]
        del self.adjacency[name]
        del self.locations[name]

    def get_location(self, name: str) -> Node:
        """Return the Node object for a given name."""
        self._require_location(name)
        return self.locations[name]

    def list_locations(self) -> list[str]:
        """Return a sorted list of all location names."""
        return sorted(self.locations.keys())

    # ==================================================================
    # Edge operations
    # ==================================================================

    def add_path(self, loc1: str, loc2: str, distance: float, time: float) -> None:
        """
        Add an undirected weighted path between two locations.

        Args:
            loc1     : First location name
            loc2     : Second location name
            distance : Path distance in metres
            time     : Walking time in minutes
        Raises:
            ValueError : If either location doesn't exist, or if a path
                         between them already exists
        """
        self._require_location(loc1)
        self._require_location(loc2)
        if loc1 == loc2:
            raise ValueError("Cannot connect a location to itself.")
        if loc2 in self.adjacency[loc1]:
            raise ValueError(f"Path between '{loc1}' and '{loc2}' already exists.")
        if distance <= 0 or time <= 0:
            raise ValueError("Distance and time must be positive numbers.")

        edge_data = {"distance": distance, "time": time}
        # Undirected → add in both directions
        self.adjacency[loc1][loc2] = edge_data
        self.adjacency[loc2][loc1] = edge_data

    def remove_path(self, loc1: str, loc2: str) -> None:
        """
        Remove the path between two locations.

        Raises:
            KeyError : If either location or the path doesn't exist
        """
        self._require_location(loc1)
        self._require_location(loc2)
        if loc2 not in self.adjacency[loc1]:
            raise KeyError(f"No path exists between '{loc1}' and '{loc2}'.")
        del self.adjacency[loc1][loc2]
        del self.adjacency[loc2][loc1]

    def update_path(self, loc1: str, loc2: str, distance: float = None, time: float = None) -> None:
        """
        Update the weight(s) of an existing path.

        Only the provided arguments are updated; omitted ones stay unchanged.
        """
        self._require_location(loc1)
        self._require_location(loc2)
        if loc2 not in self.adjacency[loc1]:
            raise KeyError(f"No path exists between '{loc1}' and '{loc2}'.")
        if distance is not None:
            if distance <= 0:
                raise ValueError("Distance must be positive.")
            self.adjacency[loc1][loc2]["distance"] = distance
            self.adjacency[loc2][loc1]["distance"] = distance
        if time is not None:
            if time <= 0:
                raise ValueError("Time must be positive.")
            self.adjacency[loc1][loc2]["time"] = time
            self.adjacency[loc2][loc1]["time"] = time

    def get_neighbors(self, name: str) -> dict:
        """
        Return the adjacency dictionary for a location.

        Returns:
            {neighbour_name: {"distance": d, "time": t}, ...}
        """
        self._require_location(name)
        return self.adjacency[name]

    def has_path(self, loc1: str, loc2: str) -> bool:
        """Check whether a direct path exists between two locations."""
        return (loc1 in self.adjacency and loc2 in self.adjacency[loc1])

    # ==================================================================
    # Display
    # ==================================================================

    def display_graph(self) -> str:
        """
        Return a formatted string representation of the full graph.

        Used by both the CLI and for debugging.
        """
        if not self.locations:
            return "Graph is empty."

        lines = ["=" * 60, "  CAMPUS MAP — ADJACENCY LIST", "=" * 60]
        for name in self.list_locations():
            node = self.locations[name]
            lines.append(f"\n📍 {name}  (coords: {node.coords})")
            neighbours = self.adjacency[name]
            if neighbours:
                for neighbour, weights in sorted(neighbours.items()):
                    d = weights["distance"]
                    t = weights["time"]
                    lines.append(f"     └─ {neighbour:<22} {d:>6.0f} m  |  {t:.1f} min")
            else:
                lines.append("     └─ (no connections)")
        lines.append("=" * 60)
        return "\n".join(lines)

    def stats(self) -> dict:
        """Return basic graph statistics."""
        edge_count = sum(len(v) for v in self.adjacency.values()) // 2
        return {
            "nodes": len(self.locations),
            "edges": edge_count,
        }

    # ==================================================================
    # Serialisation
    # ==================================================================

    def to_dict(self) -> dict:
        """Serialise the full graph to a JSON-compatible dictionary."""
        return {
            "nodes": {name: node.to_dict() for name, node in self.locations.items()},
            "edges": {
                loc1: {
                    loc2: weights
                    for loc2, weights in neighbours.items()
                    # Only store each undirected edge once (loc1 < loc2)
                    if loc1 < loc2
                }
                for loc1, neighbours in self.adjacency.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Graph":
        """Reconstruct a Graph from a serialised dictionary."""
        g = cls()
        for name, node_data in data["nodes"].items():
            node = Node.from_dict(node_data)
            g.locations[name] = node
            g.adjacency[name] = {}
        for loc1, neighbours in data["edges"].items():
            for loc2, weights in neighbours.items():
                if loc2 not in g.adjacency[loc1]:
                    g.adjacency[loc1][loc2] = weights
                    g.adjacency[loc2][loc1] = weights
        return g

    # ==================================================================
    # Private helpers
    # ==================================================================

    def _require_location(self, name: str) -> None:
        """Raise KeyError if the location does not exist in the graph."""
        if name not in self.locations:
            raise KeyError(f"Location '{name}' not found in the graph.")