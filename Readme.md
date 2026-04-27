# 🗺 KNUST Campus Navigation System

> An interactive campus pathfinding system demonstrating graph data structures and classic graph algorithms — built as a portfolio-quality DSA project.

---

## 📌 Project Overview

This system models a university campus as a **weighted undirected graph**, where:

- **Nodes** = campus buildings / locations
- **Edges** = walkable paths between locations  
- **Weights** = distance (metres) + time (minutes)

Users can explore the campus map, compute optimal routes, and watch algorithms explore the graph step-by-step through both a **CLI** and a **Tkinter GUI**.

---

## 🏗 Project Structure

```
campus_navigation_system/
│
├── main.py                      # Entry point
│
├── graph/
│   ├── node.py                  # Node class (campus location)
│   └── graph.py                 # Graph class (adjacency list)
│
├── algorithms/
│   ├── bfs.py                   # Breadth-First Search
│   ├── dfs.py                   # Depth-First Search
│   ├── dijkstra.py              # Dijkstra's shortest path
│   └── astar.py                 # A* pathfinding
│
├── ui/
│   ├── cli_interface.py         # Menu-driven CLI
│   └── gui_interface.py         # Tkinter GUI
│
├── visualization/
│   └── graph_visualizer.py      # networkx + matplotlib rendering
│
├── storage/
│   └── data_manager.py          # JSON save / load / default graph
│
├── tests/
│   └── test_all.py              # pytest test suite (40+ tests)
│
└── data/
    └── campus_map.json          # Persisted graph data
```

---

## 🏫 Campus Locations (Nodes)

| Location | Coordinates | Description |
|---|---|---|
| Main Gate | (10, 50) | Primary campus entrance |
| Admin Block | (25, 65) | University administration |
| Library | (40, 70) | Central study hub |
| Cafeteria | (40, 50) | Student dining hall |
| SRC | (55, 60) | Student Representative Council |
| Lecture Hall | (55, 80) | Main lecture complex |
| Engineering Block | (70, 70) | College of Engineering |
| Sports Complex | (70, 35) | Stadium, courts, gym |

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/asieducodes/campus-navigation-system.git
cd campus-navigation-system

# Install dependencies
pip install networkx matplotlib pytest
```

---

## 🚀 Running the System

```bash
# CLI (default)
python main.py

# Tkinter GUI
python main.py --gui
```

---

## 🧪 Running Tests

```bash
pytest tests/test_all.py -v
```

---

## 📐 Data Structures Used

| Structure | Where Used | Why |
|---|---|---|
| **dict (Hash Map)** | `Graph.locations`, `Graph.adjacency` | O(1) node and edge lookup |
| **Adjacency List** | `Graph.adjacency` | O(V+E) space — efficient for sparse campus graphs |
| **deque (Queue)** | BFS | FIFO traversal; O(1) enqueue/dequeue |
| **list (Stack)** | DFS iterative | LIFO traversal; O(1) push/pop |
| **Call Stack** | DFS recursive | Implicit LIFO via Python recursion |
| **heapq (Min-Heap)** | Dijkstra, A* | O(log V) priority extraction |

---

## 🧠 Algorithms

### 1. Breadth-First Search (BFS)
- **How it works:** Explores level by level using a queue (FIFO).
- **Guarantees:** Shortest path by number of hops (unweighted).
- **Time:** O(V + E) &nbsp; **Space:** O(V)
- **Best for:** Fewest-stops routing, connectivity checks.

### 2. Depth-First Search (DFS)
- **How it works:** Explores as deep as possible before backtracking. Uses recursion (call stack) or an explicit stack.
- **Guarantees:** Finds *a* path but NOT the shortest.
- **Time:** O(V + E) &nbsp; **Space:** O(V)
- **Best for:** Cycle detection, exploring all possible paths.

### 3. Dijkstra's Algorithm
- **How it works:** Greedily expands the lowest-cost frontier using a min-heap. Relaxes edge weights iteratively.
- **Guarantees:** Shortest weighted path (requires non-negative weights).
- **Time:** O((V + E) log V) &nbsp; **Space:** O(V)
- **Best for:** Minimum distance or minimum time routing.

### 4. A* Pathfinding
- **How it works:** Like Dijkstra, but uses a heuristic `h(n)` — the Euclidean distance to the goal — to guide the search. Expands nodes by `f(n) = g(n) + h(n)`.
- **Guarantees:** Optimal if the heuristic is admissible (never overestimates).
- **Time:** O((V + E) log V) worst case, faster in practice.
- **Space:** O(V)
- **Best for:** Faster routing when spatial coordinates are available.

---

## 🆚 Algorithm Comparison

| Feature | BFS | DFS | Dijkstra | A* |
|---|---|---|---|---|
| Guarantees shortest path? | ✅ (hops) | ❌ | ✅ (weight) | ✅ (weight) |
| Uses edge weights? | ❌ | ❌ | ✅ | ✅ |
| Uses heuristic? | ❌ | ❌ | ❌ | ✅ |
| Data structure | Queue | Stack / Recursion | Min-Heap | Min-Heap |
| Time complexity | O(V+E) | O(V+E) | O((V+E)logV) | O((V+E)logV) |
| Explores fewer nodes? | ⚖️ | ⚖️ | ⚖️ | ✅ |

---

## 🎨 Visualization Colour Coding

| Colour | Meaning |
|---|---|
| 🔵 Blue | Unexplored node |
| 🟡 Yellow | Currently visiting |
| 🟢 Green | Already visited |
| 🔴 Red | Shortest path node |
| Orange edge | Route edge |

---

## 📂 JSON Storage Format

```json
{
  "nodes": {
    "Library": { "name": "Library", "coords": [40, 70], "description": "..." }
  },
  "edges": {
    "Library": {
      "Admin Block": { "distance": 220, "time": 2.8 }
    }
  }
}
```

---

## 👤 Author

**Group13** — Computer Engineering, KNUST  
GitHub: [@joshua-darrah](https://github.com/joshua-darrah)

---

## 📚 Learning Objectives

After completing this project, you will understand:
- How to represent graphs using adjacency lists
- Why hash maps give O(1) lookup
- How BFS and DFS differ in traversal order
- Why Dijkstra needs a priority queue
- How A* uses spatial heuristics to outperform Dijkstra
- How to animate algorithms using matplotlib
- How to structure a modular Python project