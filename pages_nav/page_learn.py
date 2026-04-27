"""
page_learn.py  —  📚 Learn Algorithms
Interactive educational page explaining each algorithm with complexity tables.
"""

import streamlit as st
from streamlit_utils import build_plotly_graph, ALGO_INFO, ALGO_COLORS, PAL


def render():
    g = st.session_state.graph

    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D2137,#1565C0);
                border-radius:14px; padding:22px 28px; margin-bottom:20px;'>
        <h1 style='color:white; margin:0; font-size:1.75rem;'>📚 Learn the Algorithms</h1>
        <p style='color:#90CAF9; margin:6px 0 0 0; font-size:0.92rem;'>
            Understand how each algorithm works — explained clearly with complexity analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── algorithm selector tabs ───────────────────────────────────────
    tab_bfs, tab_dfs, tab_dijk, tab_astar, tab_compare = st.tabs([
        "🔵 BFS", "🟣 DFS", "🟢 Dijkstra", "🟠 A*", "⚔️ Compare All"
    ])

    for tab, algo_key in [
        (tab_bfs,  "BFS"),
        (tab_dfs,  "DFS"),
        (tab_dijk, "Dijkstra"),
        (tab_astar,"A*"),
    ]:
        with tab:
            _render_algo_tab(algo_key, g)

    with tab_compare:
        _render_compare_tab()


def _render_algo_tab(key: str, g):
    info = ALGO_INFO[key]
    col  = info["color"]

    # header card
    st.markdown(f"""
    <div style='background:{col}18; border:2px solid {col}44;
                border-radius:14px; padding:20px 24px; margin-bottom:18px;'>
        <div style='font-size:1.5rem; font-weight:900; color:{col};'>
            {info['emoji']} {info['full']}
        </div>
        <div style='color:#546E7A; margin-top:8px; font-size:0.95rem; line-height:1.6;'>
            {info['how']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("#### ⚙️ Properties")
        props = [
            ("Data Structure",  info["structure"]),
            ("Time Complexity",  info["time"]),
            ("Space Complexity", info["space"]),
            ("Finds Optimal?",   info["optimal"]),
            ("Uses Weights?",    info["weights"]),
            ("Uses Heuristic?",  info["heuristic"]),
            ("Best For",         info["best_for"]),
        ]
        for label, val in props:
            highlight = val.startswith("Yes")
            bg = f"{col}22" if highlight else "#F8FAFC"
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        background:{bg}; border-radius:7px; padding:9px 14px; margin-bottom:5px;
                        border:1px solid {col}33;'>
                <span style='color:#546E7A; font-size:0.85rem; font-weight:600;'>{label}</span>
                <span style='color:#0D2137; font-size:0.88rem; font-weight:700;'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

        # pseudocode
        st.markdown("#### 💻 Pseudocode")
        pseudos = {
            "BFS": """\
BFS(graph, start, goal):
  queue ← deque([start])
  visited ← {start}
  parent ← {start: None}

  while queue not empty:
    current ← queue.popleft()
    if current == goal: break

    for neighbour in graph[current]:
      if neighbour not in visited:
        visited.add(neighbour)
        parent[neighbour] = current
        queue.append(neighbour)

  return reconstruct_path(parent, goal)""",

            "DFS": """\
DFS(graph, node, goal, visited):
  visited.add(node)

  if node == goal: return True

  for neighbour in graph[node]:
    if neighbour not in visited:
      parent[neighbour] = node
      if DFS(graph, neighbour, goal, visited):
        return True

  return False""",

            "Dijkstra": """\
Dijkstra(graph, start, goal, weight):
  dist ← {node: ∞}
  dist[start] ← 0
  heap ← [(0, start)]

  while heap not empty:
    cost, current ← heappop(heap)
    if cost > dist[current]: continue
    if current == goal: break

    for neighbour, edge in graph[current]:
      tentative ← dist[current] + edge[weight]
      if tentative < dist[neighbour]:
        dist[neighbour] ← tentative
        heappush(heap, (tentative, neighbour))

  return reconstruct_path(parent, goal)""",

            "A*": """\
A_Star(graph, start, goal, weight):
  g ← {node: ∞}
  g[start] ← 0
  heap ← [(g[start], start)]

  while heap not empty:
    f, current ← heappop(heap)
    if current == goal: break

    for neighbour, edge in graph[current]:
      tentative_g ← g[current] + edge[weight]
      if tentative_g < g[neighbour]:
        g[neighbour] ← tentative_g
        heappush(heap, (tentative_g, neighbour))

  return reconstruct_path(parent, goal)""",
        }
        st.code(pseudos[key], language="python")

    with right:
        st.markdown("#### 🗺 Live Demo on Campus Map")

        locs  = g.list_locations()
        start = st.selectbox("Start", locs, key=f"learn_start_{key}")
        goal  = st.selectbox("Goal",  locs, key=f"learn_goal_{key}")

        if st.button(f"Run {key} →", key=f"learn_run_{key}", use_container_width=True):
            if start == goal:
                st.warning("Pick different locations.")
            else:
                from streamlit_utils import run_algorithm
                try:
                    r = run_algorithm(g, key, start, goal, "distance")
                    st.session_state[f"learn_result_{key}"] = r
                except Exception as e:
                    st.error(str(e))

        r = st.session_state.get(f"learn_result_{key}")

        chart_key = f"{key}_{start}_{goal}"

        if r:
            fig = build_plotly_graph(
                g, highlight_path=r["path"],
                title=f"{key} — {start} → {goal}",
                height=340,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key=f"learn_chart_{chart_key}_result"
            )

        else:
            fig = build_plotly_graph(
                g,
                height=340,
                title="Select locations and click Run"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key=f"learn_chart_{chart_key}_default"
            )


def _render_compare_tab():
    st.markdown("### ⚔️ All Four Algorithms — Side by Side")

    compare_data = [
        ["Guarantees optimal path?", "✅ Yes", "❌ No", "✅ Yes", "✅ Yes"],
        ["Uses edge weights?", "❌ No", "❌ No", "✅ Yes", "✅ Yes"],
        ["Uses heuristic?", "❌ No", "❌ No", "❌ No", "✅ Yes"],
    ]

    for row in compare_data:
        st.write(row)