"""
streamlit_utils.py
Shared helpers: session state initialisation, Plotly graph builder,
result formatters used across all pages.
"""

import math
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── colour palette ────────────────────────────────────────────────────
PAL = {
    "navy":        "#0D2137",
    "blue":        "#1565C0",
    "accent":      "#0288D1",
    "teal":        "#00838F",
    "green":       "#2E7D32",
    "orange":      "#E65100",
    "purple":      "#6A1B9A",
    "red":         "#C62828",
    "white":       "#FFFFFF",
    "light":       "#E3F2FD",
    "mid_gray":    "#90A4AE",
    "dark":        "#1A2332",
}

ALGO_COLORS = {
    "BFS":      PAL["accent"],
    "DFS":      PAL["teal"],
    "Dijkstra": PAL["green"],
    "A*":       PAL["orange"],
}


# ── session state init ────────────────────────────────────────────────
def init_state():
    if "graph" not in st.session_state:
        from storage.data_manager import get_or_create_graph
        import os, sys
        sys.path.insert(0, os.path.dirname(__file__))
        st.session_state.graph = get_or_create_graph()
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_algo" not in st.session_state:
        st.session_state.last_algo = None
    if "compare_results" not in st.session_state:
        st.session_state.compare_results = None


# ── Plotly campus map builder ─────────────────────────────────────────
def build_plotly_graph(
    graph,
    highlight_path: list = None,
    visited_order: list = None,
    step_index: int = None,
    title: str = "KNUST Campus Map",
    height: int = 520,
):
    """
    Build and return a Plotly figure of the campus graph.

    Args:
        graph          : Graph instance
        highlight_path : list of node names forming the shortest path
        visited_order  : list of node names in traversal order
        step_index     : if set, only show traversal up to this step
        title          : figure title
        height         : figure height in px
    """
    path_set  = set(highlight_path or [])
    path_edges = set()
    if highlight_path:
        for i in range(len(highlight_path) - 1):
            a, b = highlight_path[i], highlight_path[i + 1]
            path_edges.add((a, b))
            path_edges.add((b, a))

    visited_set = set()
    if visited_order and step_index is not None:
        visited_set = set(visited_order[:step_index + 1])

    fig = go.Figure()

    # ── edges ──────────────────────────────────────────────────────────
    for loc1, neighbours in graph.adjacency.items():
        for loc2, weights in neighbours.items():
            if loc1 >= loc2:
                continue
            x0, y0 = graph.locations[loc1].coords
            x1, y1 = graph.locations[loc2].coords
            is_path_edge = (loc1, loc2) in path_edges

            fig.add_trace(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode="lines",
                line=dict(
                    color=PAL["orange"] if is_path_edge else "#B0BEC5",
                    width=4.5 if is_path_edge else 1.8,
                    dash="solid" if is_path_edge else "dot",
                ),
                hoverinfo="none",
                showlegend=False,
            ))

            # edge weight label
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            fig.add_annotation(
                x=mx, y=my,
                text=f"{weights['distance']:.0f}m<br>{weights['time']:.1f}min",
                showarrow=False,
                font=dict(size=8, color="#546E7A"),
                bgcolor="rgba(255,255,255,0.75)",
                bordercolor="rgba(0,0,0,0)",
                borderpad=2,
            )

    # ── nodes ──────────────────────────────────────────────────────────
    for name, node in graph.locations.items():
        x, y = node.coords

        # determine colour
        if name in path_set:
            col  = PAL["red"]
            size = 30
            sym  = "circle"
        elif name in visited_set:
            col  = PAL["green"]
            size = 26
            sym  = "circle"
        else:
            col  = PAL["blue"]
            size = 24
            sym  = "circle"

        neighbours = graph.adjacency[name]
        hover = (
            f"<b>{name}</b><br>"
            f"Coords: {node.coords}<br>"
            f"Connected to: {', '.join(neighbours.keys())}"
        )

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(
                color=col,
                size=size,
                symbol=sym,
                line=dict(color="white", width=2),
            ),
            text=[name],
            textposition="top center",
            textfont=dict(size=10, color=PAL["dark"], family="Arial Black"),
            hovertemplate=hover + "<extra></extra>",
            showlegend=False,
        ))

    # ── legend ─────────────────────────────────────────────────────────
    legend_items = [
        (PAL["blue"],   "Location"),
        (PAL["red"],    "Shortest Path"),
        (PAL["green"],  "Visited"),
        (PAL["orange"], "Route Edge"),
    ]
    for col, lbl in legend_items:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(color=col, size=10),
            name=lbl,
            showlegend=True,
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=PAL["navy"]), x=0.5),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#F0F4F8",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
            font=dict(size=10),
        ),
        hovermode="closest",
    )
    return fig


# ── result metric cards ───────────────────────────────────────────────
def show_result_metrics(result: dict, algo: str, weight: str = "distance"):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🛤 Distance",  f"{result['total_dist']:.0f} m")
    col2.metric("⏱ Time",      f"{result['total_time']:.1f} min")
    col3.metric("🔢 Hops",      len(result["path"]) - 1)
    col4.metric("🔍 Explored",  len(result["visited_order"]))


def show_path_ribbon(path: list, algo: str):
    col = ALGO_COLORS.get(algo, PAL["blue"])
    arrows = " → ".join(path)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, {col}22, {col}11);
            border-left: 5px solid {col};
            border-radius: 8px;
            padding: 12px 18px;
            font-size: 14px;
            font-weight: 600;
            color: {PAL['dark']};
            margin: 8px 0;
        ">
        🗺 &nbsp; {arrows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_traversal_table(visited_order: list, path: list):
    path_set = set(path)
    rows = []
    for i, node in enumerate(visited_order, 1):
        on_path = "✅" if node in path_set else ""
        rows.append({"Step": i, "Node Visited": node, "On Path": on_path})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ── algorithm runner ──────────────────────────────────────────────────
def run_algorithm(graph, algo: str, start: str, goal: str, weight: str) -> dict:
    from algorithms.bfs      import bfs_shortest_path
    from algorithms.dfs      import dfs_path
    from algorithms.dijkstra import dijkstra
    from algorithms.astar    import astar

    if algo == "BFS":
        r = bfs_shortest_path(graph, start, goal)
    elif algo == "DFS":
        r = dfs_path(graph, start, goal)
    elif algo == "Dijkstra":
        r = dijkstra(graph, start, goal, weight)
    else:
        r = astar(graph, start, goal, weight)
    r["algo"] = algo
    return r


def run_all_algorithms(graph, start: str, goal: str, weight: str) -> list:
    results = []
    for algo in ["BFS", "DFS", "Dijkstra", "A*"]:
        try:
            r = run_algorithm(graph, algo, start, goal, weight)
            r["error"] = None
        except Exception as e:
            r = {"algo": algo, "error": str(e),
                 "path": [], "total_dist": 0, "total_time": 0,
                 "visited_order": [], "hops": 0}
        results.append(r)
    return results


# ── algo info cards ───────────────────────────────────────────────────
ALGO_INFO = {
    "BFS": {
        "full":      "Breadth-First Search",
        "emoji":     "🔵",
        "color":     PAL["accent"],
        "structure": "Queue (deque — FIFO)",
        "time":      "O(V + E)",
        "space":     "O(V)",
        "optimal":   "Yes — fewest hops",
        "weights":   "No",
        "heuristic": "No",
        "best_for":  "Fewest stops, unweighted shortest path",
        "how":       (
            "BFS explores all neighbours at distance k before moving to k+1. "
            "It uses a Queue (FIFO) so nodes discovered first are processed first. "
            "This guarantees the fewest-hops path but ignores edge weights."
        ),
    },
    "DFS": {
        "full":      "Depth-First Search",
        "emoji":     "🟣",
        "color":     PAL["teal"],
        "structure": "Stack / Recursion (LIFO)",
        "time":      "O(V + E)",
        "space":     "O(V)",
        "optimal":   "No — finds any path",
        "weights":   "No",
        "heuristic": "No",
        "best_for":  "Cycle detection, exploring all possible routes",
        "how":       (
            "DFS goes as deep as possible along each branch before backtracking. "
            "It uses the call stack (recursion) or an explicit list as a stack (LIFO). "
            "DFS does NOT guarantee shortest path — it finds A path, not the BEST path."
        ),
    },
    "Dijkstra": {
        "full":      "Dijkstra's Algorithm",
        "emoji":     "🟢",
        "color":     PAL["green"],
        "structure": "Min-Heap (heapq)",
        "time":      "O((V+E) log V)",
        "space":     "O(V)",
        "optimal":   "Yes — minimum weight",
        "weights":   "Yes",
        "heuristic": "No",
        "best_for":  "Shortest weighted path, minimum distance or time",
        "how":       (
            "Dijkstra greedily expands the node with the lowest known cumulative cost "
            "using a min-heap (priority queue). Edge relaxation updates cheaper paths as "
            "they are discovered. Guaranteed optimal for non-negative edge weights."
        ),
    },
    "A*": {
        "full":      "A* Search Algorithm",
        "emoji":     "🟠",
        "color":     PAL["orange"],
        "structure": "Min-Heap + Heuristic",
        "time":      "O((V+E) log V)",
        "space":     "O(V)",
        "optimal":   "Yes — minimum weight",
        "weights":   "Yes",
        "heuristic": "Yes — Euclidean distance",
        "best_for":  "Fastest optimal path when coordinates are available",
        "how":       (
            "A* combines Dijkstra's optimality with a heuristic h(n) — the straight-line "
            "Euclidean distance to the goal. It prioritises nodes by f(n) = g(n) + h(n), "
            "steering the search toward the destination and skipping irrelevant nodes."
        ),
    },
}