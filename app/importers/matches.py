import csv
from app.database import SessionLocal
from app.models import Match, Team
from datetime import datetime

TEAM_MAP = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "Bournemouth",
    "Brentford": "Brentford",
    "Brighton": "Brighton",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Liverpool": "Liverpool",
    "Manchester City": "Manchester City",
    "Manchester Utd": "Manchester Utd",
    "Newcastle Utd": "Newcastle United",
    "Newcastle United": "Newcastle United",
    "Nott'ham Forest": "Nottingham Forest",
    "Nottingham Forest": "Nottingham Forest",
    "Tottenham": "Tottenham Hotspur",          # ← FIXED
    "Tottenham Hotspur": "Tottenham Hotspur",
    "West Ham": "West Ham United",
    "West Ham United": "West Ham United",
    "Wolves": "Wolves",
    "Leicester City": "Leicester City",
    "Ipswich Town": "Ipswich Town",
    "Southampton": "Southampton",
}

def run():
    db = SessionLocal()
    path = "app/data/pl_24-25_matches_clean.csv"

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date()

            raw_home = row["home_team"].strip()
            raw_away = row["away_team"].strip()

            # Map weird CSV names → DB names
            home_name = TEAM_MAP.get(raw_home)
            away_name = TEAM_MAP.get(raw_away)

            if not home_name or not away_name:
                print(f"Unknown team(s): {raw_home} vs {raw_away}")
                continue

            home_team = db.query(Team).filter(Team.name == home_name).first()
            away_team = db.query(Team).filter(Team.name == away_name).first()

            if not home_team or not away_team:
                print(f"Team not found in DB: {home_name} / {away_name}")
                continue

            # Fix Unicode dash in score
            score = row["score"].strip().replace("–", "-")

            try:
                home_goals, away_goals = map(int, score.split("-"))
            except:
                print(f"Bad score format: {score}")
                continue

            existing = db.query(Match).filter(
                Match.date == date,
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id
            ).first()

            if existing:
                continue

            match = Match(
                date=date,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                home_goals=home_goals,
                away_goals=away_goals
            )

            db.add(match)

        db.commit()
        db.close()

if __name__ == "__main__":
    run()