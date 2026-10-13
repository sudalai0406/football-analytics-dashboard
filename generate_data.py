"""
Standalone script to generate the synthetic football_players.csv dataset.
Run once: python generate_data.py
"""
import numpy as np
import pandas as pd

np.random.seed(42)

FIRST_NAMES = [
    "Luca", "Marco", "Carlos", "João", "Andrés", "Kai", "Ryo", "Leon",
    "Omar", "Yusuf", "Ethan", "Mason", "Hugo", "Diego", "Serge", "Nils",
    "Ivan", "Paulo", "Matteo", "Rafael", "Sven", "Alexei", "Kwame", "Tariq",
    "Finn", "Emre", "Takeshi", "Chidera", "Lamine", "Nico",
]
LAST_NAMES = [
    "Silva", "Müller", "García", "Rossi", "Santos", "Kim", "Nakamura",
    "Okafor", "Benzara", "Kovač", "Walker", "Tremblay", "Dubois",
    "Andersen", "Eriksen", "Nkosi", "Diallo", "Öztürk", "Papadopoulos",
    "Ferreira", "Petrov", "Hassan", "Messaoudi", "Yamamoto", "Perreira",
]
TEAMS = [
    "Atletico Verde", "FC Nordheim", "Sparta United", "Dynamo Eastside",
    "Red Lions FC", "Porto Azul", "Olympia City", "Ajax Nova",
    "Thunder FC", "Celtic Rangers",
]
NATIONALITIES = [
    "Brazil", "Germany", "Spain", "Italy", "France", "England",
    "Portugal", "Argentina", "Japan", "Nigeria", "Senegal",
    "Turkey", "Netherlands", "Poland", "Mexico",
]
SEASONS = ["2022-23", "2023-24", "2024-25"]
POSITIONS = ["GK", "DEF", "MID", "FWD"]

# Players per position per season (120 unique players × 3 seasons = 360 rows)
POS_DIST = {"GK": 10, "DEF": 30, "MID": 40, "FWD": 40}

def _make_name(rng_state):
    return f"{rng_state.choice(FIRST_NAMES)} {rng_state.choice(LAST_NAMES)}"

def generate():
    rng = np.random.default_rng(42)
    records = []
    pid = 1

    # Generate 120 unique players
    players = []
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

    for season in SEASONS:
        for p in players:
            pos = p["position"]
            matches = int(rng.integers(5, 39))
            minutes = int(np.clip(matches * rng.integers(60, 91), 100, 3420))

            # Position-weighted stats
            if pos == "GK":
                goals = int(rng.poisson(0.05))
                assists = int(rng.poisson(0.3))
                shots = int(rng.integers(0, 3))
                passes = int(rng.integers(600, 1400))
                pass_acc = round(float(rng.uniform(0.65, 0.92)), 2)
                dribbles = int(rng.integers(0, 5))
                tackles = int(rng.integers(0, 10))
                clean_sheets = int(rng.integers(0, int(matches * 0.5) + 1))
            elif pos == "DEF":
                goals = int(rng.poisson(1.5))
                assists = int(rng.poisson(2.0))
                shots = int(rng.integers(2, 25))
                passes = int(rng.integers(800, 2000))
                pass_acc = round(float(rng.uniform(0.68, 0.90)), 2)
                dribbles = int(rng.integers(5, 50))
                tackles = int(rng.integers(30, 120))
                clean_sheets = int(rng.integers(0, int(matches * 0.4) + 1))
            elif pos == "MID":
                goals = int(rng.poisson(4.0))
                assists = int(rng.poisson(6.0))
                shots = int(rng.integers(10, 70))
                passes = int(rng.integers(1000, 3000))
                pass_acc = round(float(rng.uniform(0.72, 0.93)), 2)
                dribbles = int(rng.integers(15, 120))
                tackles = int(rng.integers(20, 100))
                clean_sheets = 0
            else:  # FWD
                goals = int(rng.poisson(10.0))
                assists = int(rng.poisson(5.0))
                shots = int(rng.integers(20, 120))
                passes = int(rng.integers(400, 1200))
                pass_acc = round(float(rng.uniform(0.60, 0.85)), 2)
                dribbles = int(rng.integers(20, 150))
                tackles = int(rng.integers(5, 40))
                clean_sheets = 0

            shots_on_target = int(np.clip(rng.integers(int(shots * 0.3), int(shots * 0.65) + 2), 0, shots))
            yellow_cards = int(rng.poisson(1.5))
            red_cards = int(rng.poisson(0.08))

            # Composite rating (1–10)
            g_norm = min(goals / 20, 1.0)
            a_norm = min(assists / 15, 1.0)
            pa_norm = pass_acc
            t_norm = min(tackles / 100, 1.0)
            rating = round(float(np.clip(
                5.0 + g_norm * 2.0 + a_norm * 1.5 + pa_norm * 1.0 + t_norm * 0.5
                + rng.uniform(-0.5, 0.5), 4.0, 10.0
            )), 1)

            records.append({
                **p,
                "season": season,
                "matches_played": matches,
                "minutes_played": minutes,
                "goals": goals,
                "assists": assists,
                "shots": shots,
                "shots_on_target": shots_on_target,
                "passes": passes,
                "pass_accuracy": pass_acc,
                "dribbles": dribbles,
                "tackles": tackles,
                "yellow_cards": yellow_cards,
                "red_cards": red_cards,
                "clean_sheets": clean_sheets,
                "rating": rating,
            })

    df = pd.DataFrame(records)
    df.to_csv("football_players.csv", index=False)
    print(f"Generated football_players.csv — {len(df)} rows, {df['player_id'].nunique()} unique players.")
    return df

if __name__ == "__main__":
    generate()
