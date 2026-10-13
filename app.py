"""
Football Player Performance Analytics Dashboard
================================================
A portfolio-quality Streamlit app that analyses synthetic football (soccer)
player statistics across multiple seasons, teams and positions.

NOTE: All data is synthetic and generated for demonstration purposes only.
      Statistics do NOT represent real-world players or clubs.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Global CSS — dark pitch theme, metric cards, table tweaks
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ---- sidebar ---- */
        [data-testid="stSidebar"] { background-color: #12151c; }

        /* ---- metric cards ---- */
        [data-testid="stMetric"] {
            background: #1a1d24;
            border: 1px solid #2a2d35;
            border-radius: 10px;
            padding: 14px 18px;
        }
        [data-testid="stMetricLabel"]  { color: #9aa0aa !important; font-size: 0.78rem; }
        [data-testid="stMetricValue"]  { color: #00ff87 !important; font-size: 1.6rem; }
        [data-testid="stMetricDelta"]  { font-size: 0.75rem; }

        /* ---- divider accent line ---- */
        hr { border-color: #00ff8733; }

        /* ---- tab bar ---- */
        [data-testid="stTabs"] button { font-size: 0.9rem; font-weight: 600; }

        /* ---- download button ---- */
        [data-testid="stDownloadButton"] > button {
            background: #00ff87;
            color: #0e1117;
            font-weight: 700;
            border-radius: 8px;
            border: none;
        }
        [data-testid="stDownloadButton"] > button:hover { background: #00cc6e; }

        /* ---- section headers ---- */
        h3 { color: #00ff87; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
PLOTLY_THEME = "plotly_dark"
ACCENT_COLORS = ["#00ff87", "#00b09b", "#1db954", "#00d4ff", "#f7b731", "#fc5c65"]
POS_COLOR_MAP = {
    "GK":  "#f7b731",
    "DEF": "#00d4ff",
    "MID": "#1db954",
    "FWD": "#fc5c65",
}

# ──────────────────────────────────────────────────────────────────────────────
# Data layer
# ──────────────────────────────────────────────────────────────────────────────
def _generate_synthetic_data() -> pd.DataFrame:
    """Create a reproducible synthetic dataset of 120 players × 3 seasons."""
    FIRST_NAMES = [
        "Luca","Marco","Carlos","João","Andrés","Kai","Ryo","Leon","Omar","Yusuf",
        "Ethan","Mason","Hugo","Diego","Serge","Nils","Ivan","Paulo","Matteo","Rafael",
        "Sven","Alexei","Kwame","Tariq","Finn","Emre","Takeshi","Chidera","Lamine","Nico",
    ]
    LAST_NAMES = [
        "Silva","Müller","García","Rossi","Santos","Kim","Nakamura","Okafor","Benzara",
        "Kovač","Walker","Tremblay","Dubois","Andersen","Eriksen","Nkosi","Diallo",
        "Öztürk","Papadopoulos","Ferreira","Petrov","Hassan","Messaoudi","Yamamoto","Perreira",
    ]
    TEAMS = [
        "Atletico Verde","FC Nordheim","Sparta United","Dynamo Eastside",
        "Red Lions FC","Porto Azul","Olympia City","Ajax Nova","Thunder FC","Celtic Rangers",
    ]
    NATIONALITIES = [
        "Brazil","Germany","Spain","Italy","France","England","Portugal","Argentina",
        "Japan","Nigeria","Senegal","Turkey","Netherlands","Poland","Mexico",
    ]
    SEASONS = ["2022-23","2023-24","2024-25"]
    POS_DIST = {"GK": 10,"DEF": 30,"MID": 40,"FWD": 40}

    rng = np.random.default_rng(42)
    players = []
    pid = 1
    for pos, count in POS_DIST.items():
        for _ in range(count):
            players.append({
                "player_id": pid,
                "player_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                "team": rng.choice(TEAMS),
                "position": pos,
                "nationality": rng.choice(NATIONALITIES),
                "age": int(rng.integers(18, 37)),
            })
            pid += 1

    records = []
    for season in SEASONS:
        for p in players:
            pos = p["position"]
            matches = int(rng.integers(5, 39))
            minutes = int(np.clip(matches * int(rng.integers(60, 91)), 100, 3420))
            if pos == "GK":
                goals, assists = int(rng.poisson(0.05)), int(rng.poisson(0.3))
                shots = int(rng.integers(0, 3))
                passes = int(rng.integers(600, 1400))
                pass_acc = round(float(rng.uniform(0.65, 0.92)), 2)
                dribbles, tackles = int(rng.integers(0, 5)), int(rng.integers(0, 10))
                clean_sheets = int(rng.integers(0, int(matches * 0.5) + 1))
            elif pos == "DEF":
                goals, assists = int(rng.poisson(1.5)), int(rng.poisson(2.0))
                shots = int(rng.integers(2, 25))
                passes = int(rng.integers(800, 2000))
                pass_acc = round(float(rng.uniform(0.68, 0.90)), 2)
                dribbles, tackles = int(rng.integers(5, 50)), int(rng.integers(30, 120))
                clean_sheets = int(rng.integers(0, int(matches * 0.4) + 1))
            elif pos == "MID":
                goals, assists = int(rng.poisson(4.0)), int(rng.poisson(6.0))
                shots = int(rng.integers(10, 70))
                passes = int(rng.integers(1000, 3000))
                pass_acc = round(float(rng.uniform(0.72, 0.93)), 2)
                dribbles, tackles = int(rng.integers(15, 120)), int(rng.integers(20, 100))
                clean_sheets = 0
            else:  # FWD
                goals, assists = int(rng.poisson(10.0)), int(rng.poisson(5.0))
                shots = int(rng.integers(20, 120))
                passes = int(rng.integers(400, 1200))
                pass_acc = round(float(rng.uniform(0.60, 0.85)), 2)
                dribbles, tackles = int(rng.integers(20, 150)), int(rng.integers(5, 40))
                clean_sheets = 0

            sot = int(np.clip(rng.integers(int(shots * 0.3), int(shots * 0.65) + 2), 0, shots))
            yellow = int(rng.poisson(1.5))
            red = int(rng.poisson(0.08))
            g_norm = min(goals / 20, 1.0)
            a_norm = min(assists / 15, 1.0)
            rating = round(float(np.clip(
                5.0 + g_norm*2.0 + a_norm*1.5 + pass_acc*1.0 + min(tackles/100,1.0)*0.5
                + rng.uniform(-0.5, 0.5), 4.0, 10.0
            )), 1)

            records.append({
                **p, "season": season, "matches_played": matches, "minutes_played": minutes,
                "goals": goals, "assists": assists, "shots": shots, "shots_on_target": sot,
                "passes": passes, "pass_accuracy": pass_acc, "dribbles": dribbles,
                "tackles": tackles, "yellow_cards": yellow, "red_cards": red,
                "clean_sheets": clean_sheets, "rating": rating,
            })
    return pd.DataFrame(records)


@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    """Load CSV if present; otherwise generate and cache synthetic data."""
    try:
        df = pd.read_csv("football_players.csv")
    except FileNotFoundError:
        df = _generate_synthetic_data()

    # Ensure correct types and handle missing values
    numeric_cols = [
        "goals","assists","shots","shots_on_target","passes","dribbles",
        "tackles","yellow_cards","red_cards","clean_sheets","matches_played",
        "minutes_played","age","rating","pass_accuracy",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df.dropna(subset=["player_name"], inplace=True)
    df["position"] = df["position"].fillna("Unknown")
    df["team"]     = df["team"].fillna("Unknown")
    df["season"]   = df["season"].fillna("Unknown")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar filters
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Football_pictogram.svg/"
        "120px-Football_pictogram.svg.png",
        width=60,
    )
    st.sidebar.title("⚽ Football Analytics")
    st.sidebar.markdown("---")

    seasons   = sorted(df["season"].unique().tolist())
    teams     = sorted(df["team"].unique().tolist())
    positions = sorted(df["position"].unique().tolist())

    sel_seasons = st.sidebar.multiselect("📅 Season", seasons, default=seasons)
    sel_teams   = st.sidebar.multiselect("🏟 Team",   teams,   default=teams)
    sel_pos     = st.sidebar.multiselect("🎽 Position", positions, default=positions)

    min_rating  = st.sidebar.slider("⭐ Min Rating",  float(df["rating"].min()),
                                     float(df["rating"].max()), float(df["rating"].min()), 0.1)
    min_minutes = st.sidebar.slider("⏱ Min Minutes", int(df["minutes_played"].min()),
                                     int(df["minutes_played"].max()), int(df["minutes_played"].min()), 10)

    st.sidebar.markdown("---")

    filtered = df[
        df["season"].isin(sel_seasons) &
        df["team"].isin(sel_teams) &
        df["position"].isin(sel_pos) &
        (df["rating"] >= min_rating) &
        (df["minutes_played"] >= min_minutes)
    ]

    st.sidebar.markdown(f"**{len(filtered):,}** records match filters")
    st.sidebar.download_button(
        label="⬇ Download Filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="football_filtered.csv",
        mime="text/csv",
    )
    return filtered


# ──────────────────────────────────────────────────────────────────────────────
# Helper — guard for empty frame
# ──────────────────────────────────────────────────────────────────────────────
def _empty_check(df: pd.DataFrame) -> bool:
    if df.empty:
        st.warning("⚠️ No players match the current filters. Try broadening your selection.")
        return True
    return False


def _chart(fig):
    """Render a Plotly figure with consistent dark background settings."""
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#1a1d24",
        font_color="#f0f2f6",
        title_font_color="#00ff87",
        legend_bgcolor="#1a1d24",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# Page 1 — Overview
# ──────────────────────────────────────────────────────────────────────────────
def render_overview(df: pd.DataFrame, full_df: pd.DataFrame):
    st.header("📊 Overview")
    if _empty_check(df):
        return

    # ---- KPI cards ----
    total_players  = df["player_id"].nunique()
    total_goals    = int(df["goals"].sum())
    total_assists  = int(df["assists"].sum())
    total_minutes  = int(df["minutes_played"].sum())
    avg_rating     = round(df["rating"].mean(), 2)

    # Deltas vs full dataset
    fp_all = full_df["player_id"].nunique()
    tg_all = int(full_df["goals"].sum())
    ta_all = int(full_df["assists"].sum())
    tm_all = int(full_df["minutes_played"].sum())
    ar_all = round(full_df["rating"].mean(), 2)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Players",       f"{total_players:,}",   f"{total_players - fp_all:+,} vs all")
    c2.metric("⚽ Total Goals",          f"{total_goals:,}",     f"{total_goals - tg_all:+,} vs all")
    c3.metric("🎯 Total Assists",        f"{total_assists:,}",   f"{total_assists - ta_all:+,} vs all")
    c4.metric("⏱ Total Minutes",        f"{total_minutes:,}",   f"{total_minutes - tm_all:+,} vs all")
    c5.metric("⭐ Avg Rating",           f"{avg_rating}",        f"{avg_rating - ar_all:+.2f} vs all")

    st.markdown("---")

    # ---- Top 10 goal scorers ----
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🥇 Top 10 Goal Scorers")
        top_goals = (
            df.groupby("player_name", as_index=False)["goals"]
            .sum().nlargest(10, "goals")
        )
        fig = px.bar(
            top_goals, x="goals", y="player_name", orientation="h",
            color="goals", color_continuous_scale=["#1a1d24","#00ff87"],
            labels={"goals":"Goals","player_name":"Player"},
            template=PLOTLY_THEME,
        )
        fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False)
        _chart(fig)

    with col_b:
        st.subheader("⭐ Top 10 Rated Players")
        top_rated = (
            df.groupby("player_name", as_index=False)["rating"]
            .mean().round(2).nlargest(10, "rating")
        )
        fig = px.bar(
            top_rated, x="rating", y="player_name", orientation="h",
            color="rating", color_continuous_scale=["#1a1d24","#f7b731"],
            labels={"rating":"Avg Rating","player_name":"Player"},
            template=PLOTLY_THEME,
        )
        fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False)
        _chart(fig)

    st.markdown("---")

    # ---- Goals by position & season trend ----
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("⚽ Goals Distribution by Position")
        pos_goals = df.groupby("position", as_index=False)["goals"].sum()
        fig = px.bar(
            pos_goals, x="position", y="goals",
            color="position", color_discrete_map=POS_COLOR_MAP,
            labels={"goals":"Total Goals","position":"Position"},
            template=PLOTLY_THEME,
        )
        _chart(fig)

    with col_d:
        st.subheader("📈 Season Trend — Goals & Assists")
        season_trend = df.groupby("season", as_index=False).agg(
            Goals=("goals","sum"), Assists=("assists","sum")
        ).sort_values("season")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=season_trend["season"], y=season_trend["Goals"],
                                  mode="lines+markers+text", name="Goals",
                                  line=dict(color="#00ff87", width=3),
                                  text=season_trend["Goals"], textposition="top center"))
        fig.add_trace(go.Scatter(x=season_trend["season"], y=season_trend["Assists"],
                                  mode="lines+markers+text", name="Assists",
                                  line=dict(color="#00d4ff", width=3),
                                  text=season_trend["Assists"], textposition="bottom center"))
        fig.update_layout(template=PLOTLY_THEME, xaxis_title="Season",
                           yaxis_title="Count", legend_title="Metric")
        _chart(fig)


# ──────────────────────────────────────────────────────────────────────────────
# Page 2 — Player Analysis
# ──────────────────────────────────────────────────────────────────────────────
def render_player_analysis(df: pd.DataFrame):
    st.header("🔍 Player Analysis")
    if _empty_check(df):
        return

    # ---- Player comparison radar ----
    st.subheader("🕸 Player Comparison Radar")
    player_list = sorted(df["player_name"].unique().tolist())
    selected_players = st.multiselect(
        "Select 2–5 players to compare:",
        player_list,
        default=player_list[:3] if len(player_list) >= 3 else player_list,
        max_selections=5,
    )
    if len(selected_players) < 2:
        st.info("ℹ️ Select at least 2 players to display the radar chart.")
    else:
        radar_cols  = ["goals","assists","passes","dribbles","tackles","rating"]
        radar_labels = ["Goals","Assists","Passes (÷100)","Dribbles","Tackles","Rating (×10)"]
        pdata = df[df["player_name"].isin(selected_players)].groupby("player_name")[radar_cols].sum()
        # Normalize: passes /100, rating *10 for comparable scale
        pdata["passes"]  = pdata["passes"]  / 100
        pdata["rating"]  = pdata["rating"]  * 10

        fig = go.Figure()
        for i, pname in enumerate(selected_players):
            if pname not in pdata.index:
                continue
            vals = pdata.loc[pname, radar_cols].tolist()
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                name=pname,
                line_color=ACCENT_COLORS[i % len(ACCENT_COLORS)],
                opacity=0.75,
            ))
        fig.update_layout(
            polar=dict(bgcolor="#1a1d24",
                       radialaxis=dict(visible=True, gridcolor="#2a2d35"),
                       angularaxis=dict(gridcolor="#2a2d35")),
            template=PLOTLY_THEME,
            showlegend=True,
        )
        _chart(fig)

    st.markdown("---")

    # ---- Goals vs Assists scatter ----
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("⚽ Goals vs Assists")
        scatter_df = df.groupby(["player_name","position","team"], as_index=False).agg(
            goals=("goals","sum"), assists=("assists","sum"),
            minutes_played=("minutes_played","sum"), rating=("rating","mean"),
        ).round({"rating": 2})
        fig = px.scatter(
            scatter_df, x="goals", y="assists",
            color="position", color_discrete_map=POS_COLOR_MAP,
            size="minutes_played", size_max=20,
            hover_name="player_name",
            hover_data={"team": True, "rating": True,
                        "goals": True, "assists": True, "minutes_played": False},
            labels={"goals":"Goals","assists":"Assists","position":"Position"},
            template=PLOTLY_THEME,
        )
        _chart(fig)

    # ---- Shots vs Goals with trend ----
    with col_b:
        st.subheader("🎯 Shots vs Goals (Conversion)")
        shot_df = df[df["shots"] > 0].groupby(["player_name","position"], as_index=False).agg(
            goals=("goals","sum"), shots=("shots","sum"),
        )
        shot_df["conversion_rate"] = (shot_df["goals"] / shot_df["shots"] * 100).clip(upper=100).round(1)
        fig = px.scatter(
            shot_df, x="shots", y="goals",
            color="position", color_discrete_map=POS_COLOR_MAP,
            hover_name="player_name",
            hover_data={"conversion_rate": True, "shots": True, "goals": True},
            trendline="ols",
            trendline_scope="overall",
            trendline_color_override="#ffffff",
            labels={"shots":"Total Shots","goals":"Goals","position":"Position"},
            template=PLOTLY_THEME,
        )
        _chart(fig)

    st.markdown("---")

    # ---- Searchable player stats table ----
    st.subheader("📋 Player Statistics Table")
    search = st.text_input("🔎 Search by player name, team or position:", "")
    display_cols = [
        "player_name","team","position","season","age","matches_played",
        "minutes_played","goals","assists","shots","shots_on_target",
        "passes","pass_accuracy","dribbles","tackles",
        "yellow_cards","red_cards","clean_sheets","rating",
    ]
    show_df = df[display_cols].copy() if all(c in df.columns for c in display_cols) else df.copy()
    if search.strip():
        mask = (
            show_df["player_name"].str.contains(search, case=False, na=False) |
            show_df["team"].str.contains(search, case=False, na=False) |
            show_df["position"].str.contains(search, case=False, na=False)
        )
        show_df = show_df[mask]

    if show_df.empty:
        st.info("No players match your search query.")
    else:
        st.dataframe(
            show_df.reset_index(drop=True),
            use_container_width=True,
            height=380,
        )
        st.caption(f"Showing {len(show_df):,} records")


# ──────────────────────────────────────────────────────────────────────────────
# Page 3 — Team Analysis
# ──────────────────────────────────────────────────────────────────────────────
def render_team_analysis(df: pd.DataFrame):
    st.header("🏟 Team Analysis")
    if _empty_check(df):
        return

    team_agg = df.groupby("team", as_index=False).agg(
        Goals=("goals","sum"),
        Assists=("assists","sum"),
        Players=("player_id","nunique"),
        Avg_Rating=("rating","mean"),
    ).round({"Avg_Rating": 2}).sort_values("Goals", ascending=False)

    # ---- Goals + Assists grouped bar ----
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("⚽ Team Goals & Assists")
        fig = go.Figure(data=[
            go.Bar(name="Goals",   x=team_agg["team"], y=team_agg["Goals"],
                   marker_color="#00ff87"),
            go.Bar(name="Assists", x=team_agg["team"], y=team_agg["Assists"],
                   marker_color="#00d4ff"),
        ])
        fig.update_layout(barmode="group", template=PLOTLY_THEME,
                           xaxis_tickangle=-35,
                           xaxis_title="Team", yaxis_title="Count")
        _chart(fig)

    # ---- Avg rating horizontal bar ----
    with col_b:
        st.subheader("⭐ Team Average Rating")
        rated = team_agg.sort_values("Avg_Rating", ascending=True)
        fig = px.bar(
            rated, x="Avg_Rating", y="team", orientation="h",
            color="Avg_Rating", color_continuous_scale=["#1a1d24","#f7b731"],
            labels={"Avg_Rating":"Avg Rating","team":"Team"},
            template=PLOTLY_THEME,
        )
        fig.update_layout(coloraxis_showscale=False)
        _chart(fig)

    st.markdown("---")

    col_c, col_d = st.columns(2)

    # ---- Player count donut ----
    with col_c:
        st.subheader("👥 Player Distribution by Team")
        fig = px.pie(
            team_agg, values="Players", names="team", hole=0.45,
            color_discrete_sequence=ACCENT_COLORS,
            template=PLOTLY_THEME,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        _chart(fig)

    # ---- Team stats table ----
    with col_d:
        st.subheader("📋 Team Summary Table")
        st.dataframe(
            team_agg.rename(columns={"Avg_Rating":"Avg Rating"})
                    .reset_index(drop=True),
            use_container_width=True,
            height=380,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Page 4 — Position Analysis
# ──────────────────────────────────────────────────────────────────────────────
def render_position_analysis(df: pd.DataFrame):
    st.header("🎽 Position Analysis")
    if _empty_check(df):
        return

    # ---- Position profile radar ----
    st.subheader("🕸 Position Profile Radar")
    pos_agg = df.groupby("position").agg(
        Goals=("goals","mean"),
        Assists=("assists","mean"),
        Passes=("passes","mean"),
        Dribbles=("dribbles","mean"),
        Tackles=("tackles","mean"),
        Rating=("rating","mean"),
    ).round(2)
    # Normalize 0–100 per column for fair comparison
    norm = (pos_agg - pos_agg.min()) / (pos_agg.max() - pos_agg.min() + 1e-9) * 100

    radar_cats = list(norm.columns) + [norm.columns[0]]
    fig = go.Figure()
    for pos, color in POS_COLOR_MAP.items():
        if pos not in norm.index:
            continue
        vals = norm.loc[pos].tolist()
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=radar_cats,
            fill="toself",
            name=pos,
            line_color=color,
            opacity=0.7,
        ))
    fig.update_layout(
        polar=dict(bgcolor="#1a1d24",
                   radialaxis=dict(visible=True, range=[0,100], gridcolor="#2a2d35"),
                   angularaxis=dict(gridcolor="#2a2d35")),
        template=PLOTLY_THEME,
    )
    _chart(fig)

    st.markdown("---")

    # ---- Box plots for goals / assists / rating ----
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📦 Goals Distribution by Position")
        fig = px.box(df, x="position", y="goals",
                      color="position", color_discrete_map=POS_COLOR_MAP,
                      template=PLOTLY_THEME,
                      labels={"goals":"Goals","position":"Position"})
        fig.update_layout(showlegend=False)
        _chart(fig)

    with col_b:
        st.subheader("📦 Rating Distribution by Position")
        fig = px.box(df, x="position", y="rating",
                      color="position", color_discrete_map=POS_COLOR_MAP,
                      template=PLOTLY_THEME,
                      labels={"rating":"Rating","position":"Position"})
        fig.update_layout(showlegend=False)
        _chart(fig)

    st.markdown("---")

    # ---- Age violin ----
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("🎻 Age Distribution by Position")
        fig = px.violin(df, x="position", y="age",
                         color="position", color_discrete_map=POS_COLOR_MAP,
                         box=True, points="outliers",
                         template=PLOTLY_THEME,
                         labels={"age":"Age","position":"Position"})
        fig.update_layout(showlegend=False)
        _chart(fig)

    # ---- Top 3 per position ----
    with col_d:
        st.subheader("🏆 Top 3 Players by Position")
        for pos, color in POS_COLOR_MAP.items():
            pos_df = df[df["position"] == pos]
            if pos_df.empty:
                continue
            top3 = (
                pos_df.groupby("player_name", as_index=False)
                ["rating"].mean().round(2)
                .nlargest(3, "rating")
            )
            st.markdown(
                f"<span style='color:{color};font-weight:700;font-size:1rem;'>— {pos} —</span>",
                unsafe_allow_html=True,
            )
            for _, row in top3.iterrows():
                goal_sum = int(df[df["player_name"] == row["player_name"]]["goals"].sum())
                st.markdown(
                    f"&nbsp;&nbsp;**{row['player_name']}** &nbsp; "
                    f"<span style='color:#00ff87;'>★ {row['rating']}</span> &nbsp; "
                    f"⚽ {goal_sum} goals",
                    unsafe_allow_html=True,
                )
            st.markdown("")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # Synthetic data disclaimer banner
    st.markdown(
        """
        <div style="background:#1a2e1a;border:1px solid #00ff8755;border-radius:8px;
                    padding:10px 16px;margin-bottom:16px;">
            ⚽ <strong style="color:#00ff87;">Synthetic Data Notice:</strong>
            <span style="color:#ccc;"> This dashboard uses <em>generated synthetic data</em>
            for demonstration purposes only. Statistics do not represent real-world players,
            clubs, or competitions.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    full_df   = load_data()
    filtered  = render_sidebar(full_df)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🔍 Player Analysis",
        "🏟 Team Analysis",
        "🎽 Position Analysis",
    ])

    with tab1:
        render_overview(filtered, full_df)
    with tab2:
        render_player_analysis(filtered)
    with tab3:
        render_team_analysis(filtered)
    with tab4:
        render_position_analysis(filtered)


if __name__ == "__main__":
    main()
