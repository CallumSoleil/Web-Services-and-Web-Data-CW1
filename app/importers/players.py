import csv
from app.database import SessionLocal
from app.models import Player, Team

def norm(s: str) -> str:
    return s.strip().lower()

def run():
    db = SessionLocal()

    # Path to your CSV
    path = "app/data/Squad_PlayerStats__stats_standard.csv"

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_name = row["Player"]
            raw_team = row["Squad"]
            raw_pos = row.get("Pos", None)
            raw_age = row.get("Age", None)

            # Normalise
            name = norm(raw_name)
            team_name = norm(raw_team)

            # Find team
            team = db.query(Team).filter(Team.name == raw_team).first()
            if not team:
                # Try normalised match if raw doesn't match
                team = db.query(Team).filter(Team.name.ilike(raw_team)).first()

            if not team:
                print(f"Skipping player {raw_name}: team '{raw_team}' not found.")
                continue

            # Check if player already exists
            existing = db.query(Player).filter(
                Player.name == name,
                Player.team_id == team.id
            ).first()

            if existing:
                continue

            # Convert age safely
            try:
                age = int(raw_age) if raw_age else None
            except:
                age = None

            player = Player(
                name=name,
                age=age,
                position=raw_pos,
                team_id=team.id
            )

            db.add(player)

        db.commit()
        db.close()

if __name__ == "__main__":
    run()