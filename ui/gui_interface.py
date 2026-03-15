"""
gui_interface.py — Tkinter GUI for the Campus Navigation System.

Layout:
  Left panel  : Controls (add location, connect, algorithm selection)
  Right panel : Results display + embedded matplotlib canvas
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading

from graph.graph import Graph
from storage.data_manager import save_graph, load_graph, DEFAULT_PATH
from algorithms.bfs import bfs_traversal, bfs_shortest_path
from algorithms.dfs import dfs_traversal, dfs_path
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar


class CampusNavApp(tk.Tk):
    """Main Tkinter application window."""

    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.title("KNUST Campus Navigation System 🗺")
        self.geometry("1100x720")
        self.resizable(True, True)
        self.configure(bg="#1E1E2E")
        self._build_ui()
        self._refresh_location_dropdowns()

    # ==================================================================
    # UI construction
    # ==================================================================

    def _build_ui(self):
        # ── Header bar ────────────────────────────────────────────────
        header = tk.Frame(self, bg="#313244", pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="🗺  KNUST Campus Navigation System",
                 font=("Helvetica", 16, "bold"),
                 fg="#CDD6F4", bg="#313244").pack()

        # ── Main content: left panel + right panel ────────────────────
        content = tk.Frame(self, bg="#1E1E2E")
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_left_panel(content)
        self._build_right_panel(content)

    def _build_left_panel(self, parent):
        left = tk.Frame(parent, bg="#313244", width=340, relief=tk.RAISED, bd=1)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)

        style_label = {"bg": "#313244", "fg": "#CDD6F4", "font": ("Helvetica", 9)}
        style_section = {"bg": "#45475A", "fg": "#89B4FA",
                         "font": ("Helvetica", 10, "bold"), "pady": 4}

        # ── Section: Add Location ──────────────────────────────────────
        tk.Label(left, text="➕  ADD LOCATION", **style_section).pack(fill=tk.X, padx=8, pady=(10,2))

        tk.Label(left, text="Name:", **style_label).pack(anchor=tk.W, padx=12)
        self.ent_name = tk.Entry(left, bg="#45475A", fg="#CDD6F4",
                                  insertbackground="white", font=("Helvetica", 10))
        self.ent_name.pack(fill=tk.X, padx=12, pady=2)

        coord_row = tk.Frame(left, bg="#313244")
        coord_row.pack(fill=tk.X, padx=12)
        tk.Label(coord_row, text="X:", **style_label).pack(side=tk.LEFT)
        self.ent_x = tk.Entry(coord_row, bg="#45475A", fg="#CDD6F4",
                               insertbackground="white", width=6)
        self.ent_x.pack(side=tk.LEFT, padx=4)
        tk.Label(coord_row, text="Y:", **style_label).pack(side=tk.LEFT)
        self.ent_y = tk.Entry(coord_row, bg="#45475A", fg="#CDD6F4",
                               insertbackground="white", width=6)
        self.ent_y.pack(side=tk.LEFT, padx=4)

        tk.Button(left, text="Add Location", bg="#89B4FA", fg="#1E1E2E",
                  font=("Helvetica", 9, "bold"), cursor="hand2",
                  command=self._add_location).pack(padx=12, pady=5, fill=tk.X)

        # ── Section: Connect Locations ────────────────────────────────
        tk.Label(left, text="🔗  CONNECT LOCATIONS", **style_section).pack(fill=tk.X, padx=8, pady=(10,2))

        tk.Label(left, text="From:", **style_label).pack(anchor=tk.W, padx=12)
        self.cmb_from = ttk.Combobox(left, state="readonly", font=("Helvetica", 9))
        self.cmb_from.pack(fill=tk.X, padx=12, pady=2)

        tk.Label(left, text="To:", **style_label).pack(anchor=tk.W, padx=12)
        self.cmb_to = ttk.Combobox(left, state="readonly", font=("Helvetica", 9))
        self.cmb_to.pack(fill=tk.X, padx=12, pady=2)

        dist_row = tk.Frame(left, bg="#313244")
        dist_row.pack(fill=tk.X, padx=12)
        tk.Label(dist_row, text="Dist(m):", **style_label).pack(side=tk.LEFT)
        self.ent_dist = tk.Entry(dist_row, bg="#45475A", fg="#CDD6F4",
                                  insertbackground="white", width=7)
        self.ent_dist.pack(side=tk.LEFT, padx=4)
        tk.Label(dist_row, text="Time(min):", **style_label).pack(side=tk.LEFT)
        self.ent_time = tk.Entry(dist_row, bg="#45475A", fg="#CDD6F4",
                                  insertbackground="white", width=7)
        self.ent_time.pack(side=tk.LEFT, padx=4)

        tk.Button(left, text="Connect", bg="#A6E3A1", fg="#1E1E2E",
                  font=("Helvetica", 9, "bold"), cursor="hand2",
                  command=self._connect_locations).pack(padx=12, pady=5, fill=tk.X)

        # ── Section: Pathfinding ──────────────────────────────────────
        tk.Label(left, text="🧭  PATHFINDING", **style_section).pack(fill=tk.X, padx=8, pady=(10,2))

        tk.Label(left, text="Start:", **style_label).pack(anchor=tk.W, padx=12)
        self.cmb_start = ttk.Combobox(left, state="readonly", font=("Helvetica", 9))
        self.cmb_start.pack(fill=tk.X, padx=12, pady=2)

        tk.Label(left, text="Goal:", **style_label).pack(anchor=tk.W, padx=12)
        self.cmb_goal = ttk.Combobox(left, state="readonly", font=("Helvetica", 9))
        self.cmb_goal.pack(fill=tk.X, padx=12, pady=2)

        tk.Label(left, text="Algorithm:", **style_label).pack(anchor=tk.W, padx=12)
        self.cmb_algo = ttk.Combobox(left, state="readonly", font=("Helvetica", 9),
                                      values=["BFS (min hops)", "DFS (any path)",
                                              "Dijkstra (distance)", "Dijkstra (time)",
                                              "A* (distance)", "A* (time)"])
        self.cmb_algo.current(2)
        self.cmb_algo.pack(fill=tk.X, padx=12, pady=2)

        tk.Button(left, text="▶  Find Path", bg="#F38BA8", fg="#1E1E2E",
                  font=("Helvetica", 10, "bold"), cursor="hand2",
                  command=self._find_path).pack(padx=12, pady=5, fill=tk.X)

        tk.Button(left, text="🎬  Animate Traversal", bg="#FAB387", fg="#1E1E2E",
                  font=("Helvetica", 9, "bold"), cursor="hand2",
                  command=self._animate).pack(padx=12, pady=2, fill=tk.X)

        # ── Section: Utilities ────────────────────────────────────────
        tk.Label(left, text="🛠  UTILITIES", **style_section).pack(fill=tk.X, padx=8, pady=(10,2))

        btn_row = tk.Frame(left, bg="#313244")
        btn_row.pack(fill=tk.X, padx=12, pady=4)

        tk.Button(btn_row, text="Show Graph", bg="#CBA6F7", fg="#1E1E2E",
                  font=("Helvetica", 9), cursor="hand2",
                  command=self._show_graph).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        tk.Button(btn_row, text="Visualise Map", bg="#CBA6F7", fg="#1E1E2E",
                  font=("Helvetica", 9), cursor="hand2",
                  command=self._visualise).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        btn_row2 = tk.Frame(left, bg="#313244")
        btn_row2.pack(fill=tk.X, padx=12, pady=2)
        tk.Button(btn_row2, text="💾 Save", bg="#89DCEB", fg="#1E1E2E",
                  font=("Helvetica", 9), cursor="hand2",
                  command=self._save).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        tk.Button(btn_row2, text="📂 Load", bg="#89DCEB", fg="#1E1E2E",
                  font=("Helvetica", 9), cursor="hand2",
                  command=self._load).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

    def _build_right_panel(self, parent):
        right = tk.Frame(parent, bg="#1E1E2E")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Results", fg="#89B4FA", bg="#1E1E2E",
                 font=("Helvetica", 11, "bold")).pack(anchor=tk.W)

        self.txt_output = tk.Text(right, bg="#181825", fg="#CDD6F4",
                                   font=("Courier New", 10),
                                   wrap=tk.WORD, relief=tk.FLAT)
        scrollbar = tk.Scrollbar(right, command=self.txt_output.yview)
        self.txt_output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_output.pack(fill=tk.BOTH, expand=True)

        self._print("Welcome to KNUST Campus Navigation System!\n")
        self._print("The default campus map has been loaded.\n")
        self._print("Use the controls on the left to explore.\n")

    # ==================================================================
    # Output helper
    # ==================================================================

    def _print(self, text: str) -> None:
        self.txt_output.insert(tk.END, text + "\n")
        self.txt_output.see(tk.END)

    def _clear(self) -> None:
        self.txt_output.delete("1.0", tk.END)

    def _refresh_location_dropdowns(self) -> None:
        locs = self.graph.list_locations()
        for cmb in (self.cmb_from, self.cmb_to, self.cmb_start, self.cmb_goal):
            cmb["values"] = locs

    # ==================================================================
    # Button handlers
    # ==================================================================

    def _add_location(self):
        name = self.ent_name.get().strip()
        try:
            x = float(self.ent_x.get())
            y = float(self.ent_y.get())
            self.graph.add_location(name, (x, y))
            self._print(f"✅ Added location: {name} at ({x}, {y})")
            self._refresh_location_dropdowns()
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", str(e))

    def _connect_locations(self):
        loc1 = self.cmb_from.get()
        loc2 = self.cmb_to.get()
        try:
            dist = float(self.ent_dist.get())
            t    = float(self.ent_time.get())
            self.graph.add_path(loc1, loc2, dist, t)
            self._print(f"✅ Connected: {loc1} ↔ {loc2}  ({dist:.0f}m, {t:.1f}min)")
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", str(e))

    def _find_path(self):
        start = self.cmb_start.get()
        goal  = self.cmb_goal.get()
        algo  = self.cmb_algo.get()
        if not start or not goal:
            messagebox.showwarning("Input", "Please select Start and Goal.")
            return
        try:
            if algo == "BFS (min hops)":
                r = bfs_shortest_path(self.graph, start, goal)
                label = "BFS"
            elif algo == "DFS (any path)":
                r = dfs_path(self.graph, start, goal)
                label = "DFS"
            elif algo == "Dijkstra (distance)":
                r = dijkstra(self.graph, start, goal, "distance")
                label = "Dijkstra (distance)"
            elif algo == "Dijkstra (time)":
                r = dijkstra(self.graph, start, goal, "time")
                label = "Dijkstra (time)"
            elif algo == "A* (distance)":
                r = astar(self.graph, start, goal, "distance")
                label = "A* (distance)"
            else:
                r = astar(self.graph, start, goal, "time")
                label = "A* (time)"

            self._clear()
            self._print(f"═══ {label}: {start} → {goal} ═══\n")
            self._print(f"Path     : {' → '.join(r['path'])}")
            self._print(f"Distance : {r['total_dist']:.0f} m")
            self._print(f"Time     : {r['total_time']:.1f} min")
            self._print(f"Explored : {len(r['visited_order'])} node(s)")
            self._print(f"Order    : {' → '.join(r['visited_order'])}\n")

            # Show graph with highlighted path in a thread
            def _show():
                from visualization.graph_visualizer import visualize_graph
                visualize_graph(self.graph, path=r["path"],
                                title=f"{label}: {start} → {goal}")
            threading.Thread(target=_show, daemon=True).start()

        except (KeyError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def _animate(self):
        start = self.cmb_start.get()
        goal  = self.cmb_goal.get()
        algo  = self.cmb_algo.get()
        if not start:
            messagebox.showwarning("Input", "Please select a Start location.")
            return
        try:
            if "BFS" in algo:
                order = bfs_traversal(self.graph, start)
                path  = bfs_shortest_path(self.graph, start, goal)["path"] if goal else None
                title = "BFS Traversal Animation"
            elif "DFS" in algo:
                order = dfs_traversal(self.graph, start)
                path  = dfs_path(self.graph, start, goal)["path"] if goal else None
                title = "DFS Traversal Animation"
            elif "Dijkstra" in algo:
                w = "time" if "time" in algo else "distance"
                r = dijkstra(self.graph, start, goal, w)
                order, path = r["visited_order"], r["path"]
                title = f"Dijkstra Animation ({w})"
            else:
                w = "time" if "time" in algo else "distance"
                r = astar(self.graph, start, goal, w)
                order, path = r["visited_order"], r["path"]
                title = f"A* Animation ({w})"

            def _run():
                from visualization.graph_visualizer import animate_traversal
                animate_traversal(self.graph, order, path=path, title=title)
            threading.Thread(target=_run, daemon=True).start()

        except (KeyError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def _show_graph(self):
        self._clear()
        self._print(self.graph.display_graph())

    def _visualise(self):
        def _run():
            from visualization.graph_visualizer import visualize_graph
            visualize_graph(self.graph)
        threading.Thread(target=_run, daemon=True).start()

    def _save(self):
        try:
            save_graph(self.graph, DEFAULT_PATH)
            self._print("✅ Graph saved.")
        except IOError as e:
            messagebox.showerror("Error", str(e))

    def _load(self):
        try:
            loaded = load_graph(DEFAULT_PATH)
            self.graph.locations = loaded.locations
            self.graph.adjacency = loaded.adjacency
            self._refresh_location_dropdowns()
            self._print("✅ Graph loaded from file.")
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))


def run_gui(graph: Graph) -> None:
    """Launch the Tkinter GUI application."""
    app = CampusNavApp(graph)
    app.mainloop()