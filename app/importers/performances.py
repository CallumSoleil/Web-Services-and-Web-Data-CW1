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
        matches=0
        for line in f:
            row = json.loads(line)
            count=0
            matches+=1

            # Your structure: match_report contains player_stats
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

            # Find the match
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

                    # Skip summary rows like "15 Players", "16 Players"
                    if "players" in raw_name.lower():
                        continue

                    player_name = norm(raw_name)

                    # Case-insensitive lookup
                    player = db.query(Player).filter(
                        func.lower(Player.name) == player_name
                    ).first()

                    if not player:
                        print(f"Player not found: {raw_name}")
                        continue

                    # Avoid duplicates
                    existing = db.query(Performance).filter(
                        Performance.match_id == match.id,
                        Performance.player_id == player.id
                    ).first()

                    if p.get("Min", 0) == 0:
                        continue

                    if existing:
                        continue

                    perf = Performance(
                        match_id=match.id,
                        player_id=player.id,
                        minutes=p.get("Min", 0),
                        goals=p.get("Performance_Gls", 0),
                        assists=p.get("Performance_Ast", 0),
                        xg=p.get("Performance_xG", 0.0) or 0.0,
                        xa=p.get("Performance_xA", 0.0) or 0.0,
                    )
                    count+=1

                    db.add(perf)
            print(count)
        print(matches)

    db.commit()
    db.close()


if __name__ == "__main__":
    run()