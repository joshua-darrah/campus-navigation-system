"""
data_manager.py — Handles persistence: saving and loading the campus graph.

Stores graph data as JSON in data/campus_map.json.

RESPONSIBILITY:
  All file I/O is isolated here so the Graph class stays pure (no I/O logic),
  following the Single Responsibility Principle.
"""

import json
import os
from graph.graph import Graph


# Default path relative to the project root
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "campus_map.json")


def save_graph(graph: Graph, filepath: str = DEFAULT_PATH) -> None:
    """
    Serialise and save the graph to a JSON file.

    Args:
        graph    : The Graph instance to save
        filepath : Destination file path (default: data/campus_map.json)
    Raises:
        IOError : If the file cannot be written
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    data = graph.to_dict()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Graph saved to {filepath}")


def load_graph(filepath: str = DEFAULT_PATH) -> Graph:
    """
    Load a Graph from a JSON file.

    Args:
        filepath : Source file path (default: data/campus_map.json)
    Returns:
        Reconstructed Graph instance
    Raises:
        FileNotFoundError : If the file does not exist
        ValueError        : If the file is malformed
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No saved graph found at '{filepath}'.")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    graph = Graph.from_dict(data)
    print(f"✅ Graph loaded from {filepath}")
    return graph


def build_default_knust_graph() -> Graph:
    """
    Build and return the default KNUST-inspired campus graph.

    Coordinates are assigned on a 0–100 grid to reflect approximate
    real-world relative positions on the KNUST campus.

    Called on first run when no saved JSON exists yet.
    """
    g = Graph()

    # ── Nodes (name, (x, y), description) ──────────────────────────
    locations = [
        ("Main Gate",         (10,  50), "Primary campus entrance"),
        ("Admin Block",       (25,  65), "University administration offices"),
        ("Library",           (40,  70), "Balme Library — central study hub"),
        ("Cafeteria",         (40,  50), "Student dining hall"),
        ("SRC",               (55,  60), "Student Representative Council"),
        ("Lecture Hall",      (55,  80), "Main lecture hall complex"),
        ("Engineering Block", (70,  70), "College of Engineering"),
        ("Sports Complex",    (70,  35), "Stadium, courts, and gym"),
    ]
    for name, coords, desc in locations:
        g.add_location(name, coords, desc)

    # ── Edges (loc1, loc2, distance_m, time_min) ────────────────────
    # Walking speed ≈ 80 m/min (casual campus walk)
    edges = [
        ("Main Gate",         "Admin Block",       250,  3.1),
        ("Main Gate",         "Cafeteria",         350,  4.4),
        ("Admin Block",       "Library",           220,  2.8),
        ("Admin Block",       "Cafeteria",         200,  2.5),
        ("Library",           "Lecture Hall",      180,  2.3),
        ("Library",           "SRC",               160,  2.0),
        ("Cafeteria",         "SRC",               220,  2.8),
        ("Cafeteria",         "Sports Complex",    450,  5.6),
        ("SRC",               "Lecture Hall",      150,  1.9),
        ("SRC",               "Engineering Block", 220,  2.8),
        ("Lecture Hall",      "Engineering Block", 180,  2.3),
        ("Engineering Block", "Sports Complex",    300,  3.8),
    ]
    for loc1, loc2, dist, t in edges:
        g.add_path(loc1, loc2, dist, t)

    return g


def get_or_create_graph(filepath: str = DEFAULT_PATH) -> Graph:
    """
    Load the graph from disk if it exists, otherwise build the default
    KNUST graph, save it, and return it.

    This is the main entry point called by main.py on startup.
    """
    try:
        return load_graph(filepath)
    except FileNotFoundError:
        print("No saved graph found. Building default KNUST campus map...")
        g = build_default_knust_graph()
        save_graph(g, filepath)
        return g