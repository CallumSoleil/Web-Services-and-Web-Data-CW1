import json
from app.database import SessionLocal
from app.models import Team, Player, Match, Performance

def norm(s):
    return s.strip().lower()

def import_jsonl(path):
    db = SessionLocal()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            match_data = json.loads(line)

            # --- MATCH ---
            home = norm(match_data["home_team"])
            away = norm(match_data["away_team"])
            date = match_data["date"]

            home_team = db.query(Team).filter(Team.name == home).first()
            away_team = db.query(Team).filter(Team.name == away).first()

            match = db.query(Match).filter(
                Match.date == date,
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id
            ).first()

            if not match:
                match = Match(
                    date=date,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    home_goals=match_data["home_goals"],
                    away_goals=match_data["away_goals"]
                )
                db.add(match)
                db.commit()
                db.refresh(match)

            # --- PERFORMANCES ---
            for p in match_data["players"]:
                player_name = norm(p["player"])
                team_name = norm(p["team"])

                player = db.query(Player).filter(
                    Player.name == player_name
                ).first()

                if not player:
                    continue  # or create player if needed

                perf = Performance(
                    player_id=player.id,
                    match_id=match.id,
                    minutes=p.get("minutes", 0),
                    goals=p.get("goals", 0),
                    assists=p.get("assists", 0),
                    xg=p.get("xg", 0.0),
                    xa=p.get("xa", 0.0)
                )
                db.add(perf)

            db.commit()

    db.close()