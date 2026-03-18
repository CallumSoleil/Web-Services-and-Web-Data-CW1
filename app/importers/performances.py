import json
from datetime import datetime
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Match, Player, Team, Performance


def norm(name: str) -> str:
    return name.strip().lower()


TEAM_MAP = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "Bournemouth",
    "Brentford": "Brentford",
    "Brighton": "Brighton",
    "Brighton & Hove Albion": "Brighton",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Liverpool": "Liverpool",
    "Manchester City": "Manchester City",
    "Manchester Utd": "Manchester Utd",
    "Manchester United": "Manchester Utd",
    "Newcastle Utd": "Newcastle United",
    "Newcastle United": "Newcastle United",
    "Nott'ham Forest": "Nottingham Forest",
    "Nottingham Forest": "Nottingham Forest",
    "Tottenham": "Tottenham Hotspur",
    "Tottenham Hotspur": "Tottenham Hotspur",
    "West Ham": "West Ham United",
    "West Ham United": "West Ham United",
    "Wolves": "Wolves",
    "Wolverhampton Wanderers": "Wolves",
    "Leicester City": "Leicester City",
    "Ipswich Town": "Ipswich Town",
    "Southampton": "Southampton",
}


def run():
    db = SessionLocal()
    path = "app/data/match_reports.jsonl"

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)

            if "match_report" not in row:
                continue

            report = row["match_report"]
            if "player_stats" not in report:
                continue

            stats = report["player_stats"]

            # Match info
            date = datetime.strptime(report["date"], "%Y-%m-%d").date()

            raw_home = report["teams"]["home"]["name"]
            raw_away = report["teams"]["away"]["name"]

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

            match = db.query(Match).filter(
                Match.date == date,
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id
            ).first()

            if not match:
                print(f"No match found for {home_name} vs {away_name} on {date}")
                continue

            # Process home + away players
            for side in ["home", "away"]:
                players = stats[side]

                for p in players:
                    raw_name = p["Player"]

                    # Skip summary rows like "15 Players"
                    if "players" in raw_name.lower():
                        continue

                    player_name = norm(raw_name)

                    player = db.query(Player).filter(
                        func.lower(Player.name) == player_name
                    ).first()

                    if not player:
                        print(f"Player not found: {raw_name}")
                        continue

                    # Skip if already imported
                    existing = db.query(Performance).filter(
                        Performance.match_id == match.id,
                        Performance.player_id == player.id
                    ).first()

                    if existing:
                        continue

                    # Skip players with 0 minutes
                    if p.get("Min", 0) == 0:
                        continue

                    perf = Performance(
                        match_id=match.id,
                        player_id=player.id,

                        minutes=p.get("Min", 0),

                        goals=p.get("Performance_Gls", 0),
                        assists=p.get("Performance_Ast", 0),

                        shots=p.get("Performance_Sh", 0),
                        shots_on_target=p.get("Performance_SoT", 0),
                        crosses=p.get("Performance_Crs", 0),
                        offsides=p.get("Performance_Off", 0),

                        tackles_won=p.get("Performance_TklW", 0),
                        interceptions=p.get("Performance_Int", 0),

                        fouls=p.get("Performance_Fls", 0),
                        fouled=p.get("Performance_Fld", 0),

                        yellow_cards=p.get("Performance_CrdY", 0),
                        red_cards=p.get("Performance_CrdR", 0),
                    )

                    db.add(perf)

    db.commit()
    db.close()

if __name__ == "__main__":
    run()