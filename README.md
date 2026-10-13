# ⚽ Football Player Performance Analytics Dashboard

A portfolio-quality interactive dashboard built with **Python + Streamlit** to analyse and compare synthetic football (soccer) player statistics across multiple seasons, teams and positions.

> **⚠️ Synthetic Data Notice**
> All data is machine-generated for demonstration purposes only. Statistics do **not** represent real-world players, clubs, or competitions.

---

## 📸 Features

| Tab | What you get |
|---|---|
| **Overview** | 5 KPI cards, top scorers, top-rated players, goals by position, season trend |
| **Player Analysis** | Radar comparison (2–5 players), goals vs assists scatter, shots vs goals with trend line, searchable stats table |
| **Team Analysis** | Grouped bar (goals & assists), avg rating bar, player-count donut, summary table |
| **Position Analysis** | Normalised radar, box plots, age violin, top-3 per position |

**Sidebar filters:** Season · Team · Position · Min Rating · Min Minutes · CSV download

---

## 🗂 Project Structure

```
football arena/
├── app.py                    # Main Streamlit application
├── football_players.csv      # Synthetic dataset (360 rows, 120 players × 3 seasons)
├── generate_data.py          # Standalone script to regenerate the dataset
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .streamlit/
    └── config.toml           # Dark pitch theme
```

---

## 🚀 Run Locally

### 1. Prerequisites

- Python 3.9 or later
- pip

### 2. Clone / download the project

```bash
# If using git:
git clone https://github.com/YOUR_USERNAME/football-analytics-dashboard.git
cd football-analytics-dashboard

# Or simply open the folder in your terminal.
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Regenerate the dataset

The CSV is already included. Run this only if you want a fresh copy:

```bash
python generate_data.py
```

### 5. Launch the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

1. Push this folder to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo → set **Main file path** to `app.py`.
4. Click **Deploy** — no environment variables or secrets needed.

Your dashboard will be live at `https://<your-app>.streamlit.app` within ~2 minutes.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| streamlit | ≥ 1.32 | Web app framework |
| pandas | ≥ 2.0 | Data manipulation |
| numpy | ≥ 1.26 | Numerical operations |
| plotly | ≥ 5.20 | Interactive charts |
| statsmodels | ≥ 0.14 | OLS trend line in scatter |

---

## 🗃 Dataset Schema

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique player identifier (1–120) |
| `player_name` | str | Fictional full name |
| `team` | str | One of 10 fictional clubs |
| `position` | str | GK / DEF / MID / FWD |
| `season` | str | 2022-23, 2023-24, or 2024-25 |
| `age` | int | 18–36 |
| `matches_played` | int | 5–38 |
| `minutes_played` | int | Derived from matches |
| `goals` | int | Position-weighted Poisson |
| `assists` | int | Position-weighted Poisson |
| `shots` | int | Proportional to goals |
| `shots_on_target` | int | ~50 % of shots |
| `passes` | int | Position-weighted |
| `pass_accuracy` | float | 0.60 – 0.93 |
| `dribbles` | int | Position-weighted |
| `tackles` | int | Position-weighted |
| `yellow_cards` | int | Poisson(λ=1.5) |
| `red_cards` | int | Poisson(λ=0.08) |
| `clean_sheets` | int | GK & DEF only |
| `rating` | float | Composite score 4.0–10.0 |
| `nationality` | str | One of 15 nationalities |

---

## 🧮 KPI Calculations

All KPIs are computed live from the filtered DataFrame — nothing is hardcoded.

```python
total_players  = df["player_id"].nunique()
total_goals    = df["goals"].sum()
total_assists  = df["assists"].sum()
total_minutes  = df["minutes_played"].sum()
avg_rating     = df["rating"].mean().round(2)
```

---

## 🎨 Theme

Dark pitch-green theme configured in `.streamlit/config.toml`:

- Background: `#0e1117`
- Surface: `#1a1d24`
- Primary accent: `#00ff87` (pitch green)
- All charts use `plotly_dark` template

---

## 📄 Licence

This project is released for educational and portfolio use. No real player data is included.
