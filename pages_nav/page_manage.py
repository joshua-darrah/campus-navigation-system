"""
page_manage.py  —  ⚙️ Manage Graph
Add/remove campus locations and paths. Save/load the graph.
"""

import streamlit as st
from streamlit_utils import build_plotly_graph, PAL


def render():
    g = st.session_state.graph

    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D2137,#1565C0);
                border-radius:14px; padding:22px 28px; margin-bottom:20px;'>
        <h1 style='color:white; margin:0; font-size:1.75rem;'>⚙️ Manage Campus Graph</h1>
        <p style='color:#90CAF9; margin:6px 0 0 0; font-size:0.92rem;'>
            Add or remove locations and paths · Save and reload the campus map
        </p>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.6], gap="large")

    # ── left: forms ───────────────────────────────────────────────────
    with left_col:

        # ── Add location ──────────────────────────────────────────────
        with st.expander("➕ Add New Location", expanded=True):
            new_name = st.text_input("Location Name", placeholder="e.g. Medical Centre",
                                     key="mgmt_name")
            cx, cy = st.columns(2)
            with cx:
                new_x = st.number_input("X Coordinate", 0.0, 100.0, 50.0, step=1.0, key="mgmt_x")
            with cy:
                new_y = st.number_input("Y Coordinate", 0.0, 100.0, 50.0, step=1.0, key="mgmt_y")
            new_desc = st.text_input("Description (optional)", placeholder="Brief description",
                                     key="mgmt_desc")

            if st.button("Add Location", key="btn_add_loc", use_container_width=True):
                if not new_name.strip():
                    st.error("Location name cannot be empty.")
                elif new_name in g.locations:
                    st.warning(f"'{new_name}' already exists.")
                else:
                    try:
                        g.add_location(new_name.strip(), (new_x, new_y), new_desc)
                        st.success(f"✅ '{new_name}' added!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # ── Remove location ───────────────────────────────────────────
        with st.expander("🗑️ Remove Location"):
            locs = g.list_locations()
            if locs:
                rm_loc = st.selectbox("Select location to remove", locs, key="mgmt_rm_loc")
                if st.button("Remove Location", key="btn_rm_loc", use_container_width=True):
                    try:
                        g.remove_location(rm_loc)
                        st.success(f"✅ '{rm_loc}' removed.")
                        # clear cached results
                        st.session_state.last_result    = None
                        st.session_state.compare_results = None
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            else:
                st.info("No locations to remove.")

        st.markdown("---")

        # ── Connect locations ─────────────────────────────────────────
        with st.expander("🔗 Add Path Between Locations", expanded=True):
            locs = g.list_locations()
            if len(locs) < 2:
                st.info("Add at least 2 locations first.")
            else:
                p1 = st.selectbox("From",  locs, key="mgmt_p1")
                p2 = st.selectbox("To",    locs, key="mgmt_p2",
                                  index=min(1, len(locs)-1))
                pc1, pc2 = st.columns(2)
                with pc1:
                    p_dist = st.number_input("Distance (m)", 1.0, 5000.0, 200.0,
                                             step=10.0, key="mgmt_dist")
                with pc2:
                    p_time = st.number_input("Time (min)",   0.1, 120.0,  3.0,
                                             step=0.1,  key="mgmt_time")
                if st.button("Add Path", key="btn_add_path", use_container_width=True):
                    if p1 == p2:
                        st.error("Cannot connect a location to itself.")
                    elif g.has_path(p1, p2):
                        st.warning(f"Path {p1} ↔ {p2} already exists.")
                    else:
                        try:
                            g.add_path(p1, p2, p_dist, p_time)
                            st.success(f"✅ Path {p1} ↔ {p2} added!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        # ── Remove path ───────────────────────────────────────────────
        with st.expander("🗑️ Remove Path"):
            locs = g.list_locations()
            rp1  = st.selectbox("From", locs, key="mgmt_rp1")
            # only show actual neighbours
            neighbours = list(g.adjacency.get(rp1, {}).keys())
            if not neighbours:
                st.info(f"'{rp1}' has no connected paths.")
            else:
                rp2 = st.selectbox("To (connected)",  neighbours, key="mgmt_rp2")
                edge = g.adjacency[rp1][rp2]
                st.markdown(
                    f"Current: **{edge['distance']:.0f}m** · **{edge['time']:.1f}min**"
                )
                if st.button("Remove Path", key="btn_rm_path", use_container_width=True):
                    try:
                        g.remove_path(rp1, rp2)
                        st.success(f"✅ Path {rp1} ↔ {rp2} removed.")
                        st.session_state.last_result     = None
                        st.session_state.compare_results = None
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        st.markdown("---")

        # ── Save / Load ───────────────────────────────────────────────
        st.markdown("### 💾 Persistence")
        sv1, sv2 = st.columns(2)
        with sv1:
            if st.button("💾 Save Graph", use_container_width=True):
                try:
                    from storage.data_manager import save_graph, DEFAULT_PATH
                    save_graph(g, DEFAULT_PATH)
                    st.success("Graph saved ✅")
                except Exception as e:
                    st.error(str(e))
        with sv2:
            if st.button("📂 Load Graph", use_container_width=True):
                try:
                    from storage.data_manager import load_graph, DEFAULT_PATH
                    loaded = load_graph(DEFAULT_PATH)
                    g.locations = loaded.locations
                    g.adjacency = loaded.adjacency
                    st.session_state.last_result     = None
                    st.session_state.compare_results = None
                    st.success("Graph loaded ✅")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        if st.button("🔄 Reset to Default KNUST Map", use_container_width=True):
            from storage.data_manager import build_default_knust_graph, save_graph, DEFAULT_PATH
            default = build_default_knust_graph()
            g.locations = default.locations
            g.adjacency = default.adjacency
            save_graph(g, DEFAULT_PATH)
            st.session_state.last_result     = None
            st.session_state.compare_results = None
            st.success("Reset to default KNUST map ✅")
            st.rerun()

    # ── right: live map + adjacency table ─────────────────────────────
    with right_col:
        st.markdown("### 🗺 Live Campus Map")
        fig = build_plotly_graph(g, title="Current Campus Graph", height=430)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── adjacency list viewer ─────────────────────────────────────
        st.markdown("### 📋 Adjacency List")
        locs = g.list_locations()
        if not locs:
            st.info("Graph is empty.")
        else:
            rows = []
            for loc in locs:
                for nbr, w in g.adjacency[loc].items():
                    if loc < nbr:
                        rows.append({
                            "From":         loc,
                            "To":           nbr,
                            "Distance (m)": f"{w['distance']:.0f}",
                            "Time (min)":   f"{w['time']:.1f}",
                        })
            if rows:
                import pandas as pd
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No paths defined yet.")

        # ── stats ─────────────────────────────────────────────────────
        stats = g.stats()
        st.markdown("### 📊 Graph Statistics")
        s1, s2 = st.columns(2)
        s1.metric("📍 Locations", stats["nodes"])
        s2.metric("🔗 Paths",     stats["edges"])