"""
page_navigate.py  —  🗺 Find Path
Main pathfinding page: select locations, run algorithm, see results + animated graph.
"""

import time
import streamlit as st
from streamlit_utils import (
    build_plotly_graph, show_result_metrics,
    show_path_ribbon, show_traversal_table,
    run_algorithm, ALGO_COLORS, PAL,
)


def render():
    g = st.session_state.graph
    locs = g.list_locations()

    # ── page header ───────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D2137,#1565C0);
                border-radius:14px; padding:22px 28px; margin-bottom:20px;'>
        <h1 style='color:white; margin:0; font-size:1.75rem;'>🗺 Campus Pathfinder</h1>
        <p style='color:#90CAF9; margin:6px 0 0 0; font-size:0.92rem;'>
            Find the optimal route between any two campus locations using graph algorithms
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── layout: controls left | graph right ──────────────────────────
    ctrl_col, graph_col = st.columns([1, 2], gap="large")

    with ctrl_col:
        st.markdown("### ⚙️ Route Settings")

        start = st.selectbox("📍 Start Location", locs,
                             index=locs.index("Main Gate") if "Main Gate" in locs else 0,
                             key="nav_start")
        goal  = st.selectbox("🏁 Destination",    locs,
                             index=locs.index("Engineering Block") if "Engineering Block" in locs else 1,
                             key="nav_goal")

        st.markdown("---")

        algo = st.selectbox(
            "🧠 Algorithm",
            ["Dijkstra", "A*", "BFS", "DFS"],
            format_func=lambda x: {
                "Dijkstra": "🟢 Dijkstra — Shortest weighted path",
                "A*":       "🟠 A* — Fastest optimal (heuristic)",
                "BFS":      "🔵 BFS — Fewest stops",
                "DFS":      "🟣 DFS — Any path (explore)",
            }[x],
            key="nav_algo",
        )

        weight = st.radio(
            "⚖️ Optimise by",
            ["distance", "time"],
            format_func=lambda x: "📏 Distance (metres)" if x == "distance" else "⏱ Time (minutes)",
            horizontal=True,
            key="nav_weight",
        )

        st.markdown("---")

        find_btn  = st.button("🚀 Find Path",      use_container_width=True)
        anim_btn  = st.button("🎬 Animate Traversal", use_container_width=True)

        st.markdown("---")

        # quick algorithm info card
        col_info = {
            "Dijkstra": ("🟢", PAL["green"],  "Min-Heap",  "O((V+E)logV)", "Yes", "No"),
            "A*":       ("🟠", PAL["orange"], "Min-Heap+h","O((V+E)logV)", "Yes", "Yes"),
            "BFS":      ("🔵", PAL["accent"], "Queue",     "O(V+E)",       "Hops","No"),
            "DFS":      ("🟣", PAL["teal"],   "Stack",     "O(V+E)",       "No",  "No"),
        }
        em, col, ds, tc, opt, heu = col_info[algo]
        st.markdown(f"""
        <div style='background:{col}18; border:1.5px solid {col}55;
                    border-radius:10px; padding:13px 15px; font-size:0.83rem;'>
            <div style='font-weight:800; color:{col}; font-size:1rem;
                        margin-bottom:8px;'>{em} {algo}</div>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:5px;'>
                <span style='color:#546E7A;'>Structure</span>
                <span style='font-weight:700; color:#1A2332;'>{ds}</span>
                <span style='color:#546E7A;'>Time</span>
                <span style='font-weight:700; color:#1A2332;'>{tc}</span>
                <span style='color:#546E7A;'>Optimal</span>
                <span style='font-weight:700; color:#1A2332;'>{opt}</span>
                <span style='color:#546E7A;'>Heuristic</span>
                <span style='font-weight:700; color:#1A2332;'>{heu}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── graph panel ───────────────────────────────────────────────────
    with graph_col:
        result = st.session_state.get("last_result")
        path   = result["path"] if result else None
        visited = result["visited_order"] if result else None

        fig = build_plotly_graph(
            g,
            highlight_path=path,
            title="KNUST Campus — Interactive Map",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        if result and st.session_state.get("last_algo") == algo:
            st.markdown("---")
            st.markdown(f"#### ✅ Route Found — {algo}")
            show_path_ribbon(result["path"], algo)
            show_result_metrics(result, algo, weight)

            with st.expander("📋 Step-by-Step Traversal", expanded=False):
                show_traversal_table(result["visited_order"], result["path"])

    # ── find path logic ───────────────────────────────────────────────
    if find_btn:
        if start == goal:
            st.warning("⚠️ Start and destination are the same location.")
        else:
            with st.spinner(f"Running {algo}..."):
                try:
                    result = run_algorithm(g, algo, start, goal, weight)
                    st.session_state.last_result = result
                    st.session_state.last_algo   = algo
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    # ── animation logic ───────────────────────────────────────────────
    if anim_btn:
        if start == goal:
            st.warning("⚠️ Start and destination are the same location.")
        else:
            try:
                result = run_algorithm(g, algo, start, goal, weight)
                visited = result["visited_order"]
                path    = result["path"]

                st.markdown(f"### 🎬 Animating {algo} — {start} → {goal}")
                anim_col, _ = st.columns([2, 1])

                placeholder = anim_col.empty()
                step_text   = st.empty()
                prog_bar    = st.progress(0)

                for i in range(len(visited)):
                    fig = build_plotly_graph(
                        g,
                        visited_order=visited,
                        step_index=i,
                        title=f"{algo} — Step {i+1}/{len(visited)} — Visiting: {visited[i]}",
                        height=460,
                    )
                    placeholder.plotly_chart(fig, use_container_width=True,
                                             config={"displayModeBar": False})
                    step_text.markdown(
                        f"**Step {i+1}:** Visiting `{visited[i]}`"
                        + (" ← 🏁 GOAL REACHED!" if visited[i] == goal else "")
                    )
                    prog_bar.progress((i + 1) / len(visited))
                    time.sleep(0.65)

                # Final frame: show shortest path
                fig = build_plotly_graph(
                    g,
                    highlight_path=path,
                    title=f"✅ {algo} Complete — Shortest Path Highlighted",
                    height=460,
                )
                placeholder.plotly_chart(fig, use_container_width=True,
                                         config={"displayModeBar": False})
                step_text.markdown(f"✅ **Done!** Path: `{' → '.join(path)}`")
                prog_bar.progress(1.0)

                st.session_state.last_result = result
                st.session_state.last_algo   = algo

            except Exception as e:
                st.error(f"❌ {e}")