"""
cli_interface.py — Menu-driven Command Line Interface for the Campus Navigation System.
"""

from graph.graph import Graph
from storage.data_manager import save_graph, load_graph, DEFAULT_PATH
from algorithms.bfs import bfs_traversal, bfs_shortest_path
from algorithms.dfs import dfs_traversal, dfs_path
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar


MENU = """
╔══════════════════════════════════════════════════╗
║       KNUST CAMPUS NAVIGATION SYSTEM  🗺          ║
╠══════════════════════════════════════════════════╣
║  1.  Add Location                                ║
║  2.  Connect Locations (add path)                ║
║  3.  Remove Location                             ║
║  4.  Remove Path                                 ║
║  5.  Show Campus Graph                           ║
║  6.  BFS Traversal                               ║
║  7.  DFS Traversal                               ║
║  8.  Shortest Path — Dijkstra                    ║
║  9.  Shortest Path — A*                          ║
║  10. Compare All Algorithms (same route)         ║
║  11. Visualise Campus Map                        ║
║  12. Save Graph                                  ║
║  13. Load Graph                                  ║
║  14. Exit                                        ║
╚══════════════════════════════════════════════════╝
"""


def _input(prompt: str) -> str:
    return input(prompt).strip()


def _pick_location(graph: Graph, prompt: str) -> str:
    locations = graph.list_locations()
    print(f"\n  Locations: {', '.join(locations)}")
    name = _input(prompt)
    if name not in graph.locations:
        raise KeyError(f"'{name}' not found.")
    return name


def _print_path_result(result: dict, label: str, weight: str = "distance") -> None:
    print(f"\n  ── {label} ──")
    print(f"  Path : {' → '.join(result['path'])}")
    print(f"  Hops : {result.get('hops', len(result['path']) - 1)}")
    print(f"  Distance : {result['total_dist']:.0f} m")
    print(f"  Time     : {result['total_time']:.1f} min")
    if "cost" in result:
        print(f"  Optimised by {weight}: {result['cost']:.1f}")
    print(f"  Nodes explored : {len(result['visited_order'])}")
    print(f"  Visited order  : {' → '.join(result['visited_order'])}")


def run_cli(graph: Graph) -> None:
    """Entry point for the CLI. Runs until the user chooses Exit."""

    print("\n  Welcome to the KNUST Campus Navigation System!")

    while True:
        print(MENU)
        choice = _input("  Enter option: ")

        try:
            # ── 1. Add Location ──────────────────────────────────────
            if choice == "1":
                name = _input("  Location name: ")
                x = float(_input("  X coordinate (0–100): "))
                y = float(_input("  Y coordinate (0–100): "))
                desc = _input("  Description (optional): ")
                graph.add_location(name, (x, y), desc)
                print(f"  ✅ '{name}' added.")

            # ── 2. Connect Locations ─────────────────────────────────
            elif choice == "2":
                loc1 = _pick_location(graph, "  First location : ")
                loc2 = _pick_location(graph, "  Second location: ")
                dist = float(_input("  Distance (metres): "))
                time = float(_input("  Time (minutes)  : "))
                graph.add_path(loc1, loc2, dist, time)
                print(f"  ✅ Path {loc1} ↔ {loc2} added.")

            # ── 3. Remove Location ───────────────────────────────────
            elif choice == "3":
                loc = _pick_location(graph, "  Location to remove: ")
                graph.remove_location(loc)
                print(f"  ✅ '{loc}' removed.")

            # ── 4. Remove Path ───────────────────────────────────────
            elif choice == "4":
                loc1 = _pick_location(graph, "  First location : ")
                loc2 = _pick_location(graph, "  Second location: ")
                graph.remove_path(loc1, loc2)
                print(f"  ✅ Path {loc1} ↔ {loc2} removed.")

            # ── 5. Show Graph ─────────────────────────────────────────
            elif choice == "5":
                print(graph.display_graph())

            # ── 6. BFS Traversal ─────────────────────────────────────
            elif choice == "6":
                start = _pick_location(graph, "  Start location: ")
                order = bfs_traversal(graph, start)
                print(f"\n  BFS from '{start}':")
                for i, loc in enumerate(order, 1):
                    print(f"    Step {i:>2} → {loc}")

            # ── 7. DFS Traversal ─────────────────────────────────────
            elif choice == "7":
                start = _pick_location(graph, "  Start location: ")
                order = dfs_traversal(graph, start)
                print(f"\n  DFS from '{start}':")
                for i, loc in enumerate(order, 1):
                    print(f"    Step {i:>2} → {loc}")

            # ── 8. Dijkstra ───────────────────────────────────────────
            elif choice == "8":
                start = _pick_location(graph, "  Start location: ")
                goal  = _pick_location(graph, "  Goal location : ")
                w = _input("  Optimise by [distance/time] (default=distance): ") or "distance"
                result = dijkstra(graph, start, goal, weight=w)
                _print_path_result(result, "Dijkstra", w)

            # ── 9. A* ─────────────────────────────────────────────────
            elif choice == "9":
                start = _pick_location(graph, "  Start location: ")
                goal  = _pick_location(graph, "  Goal location : ")
                w = _input("  Optimise by [distance/time] (default=distance): ") or "distance"
                result = astar(graph, start, goal, weight=w)
                _print_path_result(result, "A*", w)

            # ── 10. Compare All ───────────────────────────────────────
            elif choice == "10":
                start = _pick_location(graph, "  Start location: ")
                goal  = _pick_location(graph, "  Goal location : ")
                print(f"\n  ═══ Algorithm Comparison: {start} → {goal} ═══")

                r_bfs  = bfs_shortest_path(graph, start, goal)
                r_dfs  = dfs_path(graph, start, goal)
                r_dijk = dijkstra(graph, start, goal, "distance")
                r_ast  = astar(graph, start, goal, "distance")

                rows = [
                    ("BFS (min hops)",  r_bfs),
                    ("DFS (any path)",  r_dfs),
                    ("Dijkstra",        r_dijk),
                    ("A*",             r_ast),
                ]
                print(f"\n  {'Algorithm':<20} {'Path':<55} {'Dist(m)':<10} {'Time(min)':<10} {'Explored'}")
                print(f"  {'─'*20} {'─'*55} {'─'*10} {'─'*10} {'─'*8}")
                for label, r in rows:
                    path_str = " → ".join(r["path"])
                    print(f"  {label:<20} {path_str:<55} {r['total_dist']:<10.0f} {r['total_time']:<10.1f} {len(r['visited_order'])}")

            # ── 11. Visualise ─────────────────────────────────────────
            elif choice == "11":
                try:
                    from visualization.graph_visualizer import visualize_graph
                    visualize_graph(graph)
                except ImportError:
                    print("  ⚠ matplotlib/networkx not installed. Run: pip install matplotlib networkx")

            # ── 12. Save ──────────────────────────────────────────────
            elif choice == "12":
                save_graph(graph, DEFAULT_PATH)

            # ── 13. Load ──────────────────────────────────────────────
            elif choice == "13":
                loaded = load_graph(DEFAULT_PATH)
                graph.locations = loaded.locations
                graph.adjacency = loaded.adjacency
                print("  Graph reloaded.")

            # ── 14. Exit ──────────────────────────────────────────────
            elif choice == "14":
                print("\n  Goodbye! 👋\n")
                break

            else:
                print("  Invalid option. Please enter 1–14.")

        except (KeyError, ValueError) as e:
            print(f"  ⚠  Error: {e}")
        except KeyboardInterrupt:
            print("\n  Interrupted.")
            break