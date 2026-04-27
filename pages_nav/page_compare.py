"""
page_compare.py  —  📊 Compare Algorithms
Run all 4 algorithms on the same route and compare side by side.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from streamlit_utils import (
    build_plotly_graph, show_path_ribbon,
    run_all_algorithms, ALGO_COLORS, PAL,
)


def render():
    g    = st.session_state.graph
    locs = g.list_locations()

    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D2137,#1565C0);
                border-radius:14px; padding:22px 28px; margin-bottom:20px;'>
        <h1 style='color:white; margin:0; font-size:1.75rem;'>📊 Algorithm Comparison</h1>
        <p style='color:#90CAF9; margin:6px 0 0 0; font-size:0.92rem;'>
            Run all four algorithms on the same route and see exactly how they differ
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── controls ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    with c1:
        start = st.selectbox("📍 Start", locs,
                             index=locs.index("Main Gate") if "Main Gate" in locs else 0,
                             key="cmp_start")
    with c2:
        goal = st.selectbox("🏁 Goal", locs,
                            index=locs.index("Engineering Block") if "Engineering Block" in locs else 1,
                            key="cmp_goal")
    with c3:
        weight = st.radio("⚖️ Optimise by", ["distance", "time"],
                          format_func=lambda x: "📏 Distance" if x == "distance" else "⏱ Time",
                          horizontal=True, key="cmp_weight")
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("▶ Compare", use_container_width=True)

    if run_btn:
        if start == goal:
            st.warning("⚠️ Start and goal must be different.")
            return
        with st.spinner("Running all 4 algorithms..."):
            results = run_all_algorithms(g, start, goal, weight)
            st.session_state.compare_results = results

    results = st.session_state.get("compare_results")
    if not results:
        st.info("👆 Select a route above and click **Compare** to run all four algorithms.")
        # Show static campus map while waiting
        st.plotly_chart(
            build_plotly_graph(g, title="KNUST Campus Map", height=440),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        return

    # ── summary metrics row ───────────────────────────────────────────
    st.markdown("### 📈 Results Overview")
    cols = st.columns(4)
    for i, r in enumerate(results):
        col   = ALGO_COLORS[r["algo"]]
        emoji = {"BFS":"🔵","DFS":"🟣","Dijkstra":"🟢","A*":"🟠"}[r["algo"]]
        with cols[i]:
            if r["error"]:
                st.markdown(f"""
                <div style='background:#FFEBEE; border:1.5px solid #EF9A9A;
                            border-radius:12px; padding:16px; text-align:center;'>
                    <div style='font-size:1.2rem; font-weight:800; color:#C62828;'>
                        {emoji} {r['algo']}</div>
                    <div style='color:#C62828; font-size:0.8rem; margin-top:6px;'>
                        No path found</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:{col}14; border:1.5px solid {col}55;
                            border-radius:12px; padding:16px; text-align:center;'>
                    <div style='font-size:1.1rem; font-weight:800; color:{col};'>
                        {emoji} {r['algo']}</div>
                    <div style='font-size:1.6rem; font-weight:900; color:#0D2137; margin:6px 0;'>
                        {r['total_dist']:.0f}m</div>
                    <div style='font-size:0.8rem; color:#546E7A;'>
                        {r['total_time']:.1f} min &nbsp;|&nbsp;
                        {len(r['path'])-1} hops &nbsp;|&nbsp;
                        {len(r['visited_order'])} explored
                    </div>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── comparison table ──────────────────────────────────────────────
    st.markdown("### 🔎 Detailed Comparison")
    rows = []
    for r in results:
        if r["error"]:
            rows.append({
                "Algorithm": r["algo"], "Path": "No path found",
                "Distance (m)": "—", "Time (min)": "—",
                "Hops": "—", "Nodes Explored": "—",
            })
        else:
            rows.append({
                "Algorithm":      r["algo"],
                "Path":           " → ".join(r["path"]),
                "Distance (m)":   f"{r['total_dist']:.0f}",
                "Time (min)":     f"{r['total_time']:.1f}",
                "Hops":           len(r["path"]) - 1,
                "Nodes Explored": len(r["visited_order"]),
            })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── bar charts ────────────────────────────────────────────────────
    st.markdown("### 📊 Visual Comparison")
    chart_c1, chart_c2 = st.columns(2)

    valid = [r for r in results if not r["error"]]
    algos  = [r["algo"] for r in valid]
    colors = [ALGO_COLORS[a] for a in algos]

    with chart_c1:
        fig = go.Figure(go.Bar(
            x=algos,
            y=[r["total_dist"] for r in valid],
            marker_color=colors,
            text=[f"{r['total_dist']:.0f}m" for r in valid],
            textposition="outside",
        ))
        fig.update_layout(
            title="Distance (metres)",
            height=300, margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="#F8FAFC", plot_bgcolor="#F8FAFC",
            yaxis_title="metres",
            font=dict(family="Segoe UI"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with chart_c2:
        fig2 = go.Figure(go.Bar(
            x=algos,
            y=[len(r["visited_order"]) for r in valid],
            marker_color=colors,
            text=[str(len(r["visited_order"])) for r in valid],
            textposition="outside",
        ))
        fig2.update_layout(
            title="Nodes Explored (efficiency)",
            height=300, margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="#F8FAFC", plot_bgcolor="#F8FAFC",
            yaxis_title="nodes",
            font=dict(family="Segoe UI"),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── side-by-side maps ─────────────────────────────────────────────
    st.markdown("### 🗺 Path Maps — All Four Algorithms")
    map_cols = st.columns(2)
    for i, r in enumerate(results):
        with map_cols[i % 2]:
            if not r["error"]:
                fig = build_plotly_graph(
                    g,
                    highlight_path=r["path"],
                    title=f"{r['algo']} — {r['total_dist']:.0f}m",
                    height=340,
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})
                show_path_ribbon(r["path"], r["algo"])

    # ── key insight ───────────────────────────────────────────────────
    if valid:
        best_dist  = min(valid, key=lambda r: r["total_dist"])
        least_exp  = min(valid, key=lambda r: len(r["visited_order"]))
        st.markdown("---")
        st.markdown("### 💡 Key Insights")
        i1, i2 = st.columns(2)
        with i1:
            col = ALGO_COLORS[best_dist["algo"]]
            st.markdown(f"""
            <div style='background:{col}14; border-left:5px solid {col};
                        border-radius:8px; padding:14px 18px;'>
                <b>Shortest Route:</b> {best_dist['algo']}<br>
                <span style='color:#546E7A; font-size:0.88rem;'>
                {best_dist['total_dist']:.0f}m — {' → '.join(best_dist['path'])}
                </span>
            </div>""", unsafe_allow_html=True)
        with i2:
            col2 = ALGO_COLORS[least_exp["algo"]]
            st.markdown(f"""
            <div style='background:{col2}14; border-left:5px solid {col2};
                        border-radius:8px; padding:14px 18px;'>
                <b>Most Efficient:</b> {least_exp['algo']}<br>
                <span style='color:#546E7A; font-size:0.88rem;'>
                Explored only {len(least_exp['visited_order'])} nodes to find the answer
                </span>
            </div>""", unsafe_allow_html=True)