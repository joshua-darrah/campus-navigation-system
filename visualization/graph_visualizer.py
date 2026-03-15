"""
graph_visualizer.py — Visual rendering of the campus graph and algorithm animations.

Uses:
  • networkx  — graph layout and structure
  • matplotlib — rendering, animation, colour coding

Colour scheme:
  Blue   (#4A90D9) — unexplored nodes
  Yellow (#F5A623) — currently visiting
  Green  (#7ED321) — visited / finalised
  Red    (#D0021B) — shortest path highlight
  Gray               — default edge colour
  Orange             — highlighted path edge
"""

import time
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
from graph.graph import Graph


# ── Colours ────────────────────────────────────────────────────────
C_DEFAULT  = "#4A90D9"   # unexplored
C_VISITING = "#F5A623"   # currently visiting
C_VISITED  = "#7ED321"   # visited
C_PATH     = "#D0021B"   # shortest path
C_EDGE     = "#AAAAAA"
C_EDGE_PATH = "#FF6B00"


def _build_nx_graph(graph: Graph) -> tuple[nx.Graph, dict]:
    """Convert our Graph into a networkx Graph + position dict."""
    G = nx.Graph()
    pos = {}

    for name, node in graph.locations.items():
        G.add_node(name)
        pos[name] = node.coords

    for loc1, neighbours in graph.adjacency.items():
        for loc2, weights in neighbours.items():
            if loc1 < loc2:  # avoid duplicate edges
                G.add_edge(loc1, loc2,
                           distance=weights["distance"],
                           time=weights["time"])
    return G, pos


def visualize_graph(graph: Graph, path: list[str] = None, title: str = "KNUST Campus Map") -> None:
    """
    Render the campus graph as a static image.

    Args:
        graph : The campus Graph
        path  : Optional list of node names to highlight as a route
        title : Window / figure title
    """
    G, pos = _build_nx_graph(graph)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#FFFFFF")

    # ── Determine colours ──────────────────────────────────────────
    node_colors = []
    path_set = set()
    path_edges = set()

    if path:
        path_set = set(path)
        for i in range(len(path) - 1):
            path_edges.add((path[i], path[i + 1]))
            path_edges.add((path[i + 1], path[i]))

    for node in G.nodes():
        if node in path_set:
            node_colors.append(C_PATH)
        else:
            node_colors.append(C_DEFAULT)

    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        if (u, v) in path_edges or (v, u) in path_edges:
            edge_colors.append(C_EDGE_PATH)
            edge_widths.append(4.0)
        else:
            edge_colors.append(C_EDGE)
            edge_widths.append(1.5)

    # ── Draw graph ─────────────────────────────────────────────────
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=1200, ax=ax, alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=8,
                            font_weight="bold", ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                           width=edge_widths, ax=ax, alpha=0.8)

    # ── Edge distance labels ───────────────────────────────────────
    edge_labels = {(u, v): f"{d['distance']:.0f}m\n{d['time']:.1f}min"
                   for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=6.5, ax=ax,
                                 bbox=dict(boxstyle="round,pad=0.2",
                                           fc="white", alpha=0.6))

    # ── Legend ─────────────────────────────────────────────────────
    legend_elements = [
        mpatches.Patch(color=C_DEFAULT,   label="Campus location"),
        mpatches.Patch(color=C_PATH,      label="Shortest path"),
        mpatches.Patch(color=C_EDGE_PATH, label="Route edge"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=9)

    stats = graph.stats()
    ax.set_xlabel(
        f"Nodes: {stats['nodes']}   Edges: {stats['edges']}   "
        "(coordinates are relative campus grid units)",
        fontsize=8, color="#666666"
    )
    plt.tight_layout()
    plt.show()


def animate_traversal(
    graph: Graph,
    visited_order: list[str],
    path: list[str] = None,
    title: str = "Algorithm Animation",
    interval: int = 700
) -> None:
    """
    Animate a BFS/DFS/Dijkstra/A* traversal step-by-step.

    Args:
        graph         : The campus Graph
        visited_order : Node names in the order they were explored
        path          : Optional shortest path to highlight at the end
        title         : Animation title
        interval      : Milliseconds between frames
    """
    G, pos = _build_nx_graph(graph)
    all_nodes = list(G.nodes())

    # Total frames = traversal steps + 1 final frame showing path
    total_frames = len(visited_order) + (1 if path else 0)

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor("#FFFFFF")

    path_set = set(path) if path else set()
    path_edges = set()
    if path:
        for i in range(len(path) - 1):
            path_edges.add((path[i], path[i + 1]))
            path_edges.add((path[i + 1], path[i]))

    def update(frame):
        ax.clear()
        ax.set_facecolor("#F8F9FA")

        # Determine which nodes have been visited up to this frame
        is_final = path and frame >= len(visited_order)
        visited_so_far = set(visited_order[:frame]) if not is_final else set(visited_order)
        current_node = visited_order[frame - 1] if 0 < frame <= len(visited_order) else None

        node_colors = []
        for node in all_nodes:
            if is_final and node in path_set:
                node_colors.append(C_PATH)
            elif node == current_node:
                node_colors.append(C_VISITING)
            elif node in visited_so_far:
                node_colors.append(C_VISITED)
            else:
                node_colors.append(C_DEFAULT)

        edge_colors = []
        edge_widths = []
        for u, v in G.edges():
            if is_final and ((u, v) in path_edges or (v, u) in path_edges):
                edge_colors.append(C_EDGE_PATH)
                edge_widths.append(4.0)
            else:
                edge_colors.append(C_EDGE)
                edge_widths.append(1.5)

        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                               node_size=1200, ax=ax, alpha=0.9)
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                               width=edge_widths, ax=ax, alpha=0.8)

        edge_labels = {(u, v): f"{d['distance']:.0f}m"
                       for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                     font_size=6.5, ax=ax,
                                     bbox=dict(boxstyle="round,pad=0.2",
                                               fc="white", alpha=0.6))

        if is_final and path:
            step_label = f"✅ Shortest path: {' → '.join(path)}"
        elif current_node:
            step_label = f"Step {frame}/{len(visited_order)}  →  Visiting: {current_node}"
        else:
            step_label = "Initialising..."

        ax.set_title(f"{title}\n{step_label}", fontsize=13, fontweight="bold")

        legend_elements = [
            mpatches.Patch(color=C_DEFAULT,   label="Unexplored"),
            mpatches.Patch(color=C_VISITING,  label="Currently visiting"),
            mpatches.Patch(color=C_VISITED,   label="Visited"),
            mpatches.Patch(color=C_PATH,      label="Shortest path"),
        ]
        ax.legend(handles=legend_elements, loc="upper left", fontsize=9)

    anim = FuncAnimation(fig, update, frames=total_frames + 1,
                         interval=interval, repeat=False)
    plt.tight_layout()
    plt.show()