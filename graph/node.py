"""
node.py — Represents a single campus location (graph node).

Each node stores:
  - name        : unique identifier (e.g. "Library")
  - coordinates : (x, y) tuple used by A* heuristic
  - metadata    : optional description for the UI

DATA STRUCTURE NOTE:
  Node objects are stored in the Graph's 'locations' dictionary (hash map),
  keyed by name. O(1) lookup by name.
"""


class Node:
    """A campus location node in the navigation graph."""

    def __init__(self, name: str, coords: tuple[float, float], description: str = ""):
        """
        Initialise a campus node.

        Args:
            name        : Unique location name, e.g. "Library"
            coords      : (x, y) position on the campus map grid
            description : Optional short description shown in the GUI
        """
        if not name or not isinstance(name, str):
            raise ValueError("Node name must be a non-empty string.")
        if not (isinstance(coords, tuple) and len(coords) == 2):
            raise ValueError("Coordinates must be a tuple of two numbers: (x, y).")

        self.name: str = name
        self.coords: tuple[float, float] = coords
        self.description: str = description

    # ------------------------------------------------------------------
    # Representation helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Node(name={self.name!r}, coords={self.coords})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Node) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    # ------------------------------------------------------------------
    # Serialisation (for JSON storage)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Convert node to a JSON-serialisable dictionary."""
        return {
            "name": self.name,
            "coords": list(self.coords),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        """Reconstruct a Node from a dictionary (loaded from JSON)."""
        return cls(
            name=data["name"],
            coords=tuple(data["coords"]),
            description=data.get("description", ""),
        )