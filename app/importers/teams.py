from app.database import SessionLocal
from app.models import Team

TEAMS_2425 = [
    "Arsenal",
    "Aston Villa",
    "Bournemouth",
    "Brentford",
    "Brighton",
    "Chelsea",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Liverpool",
    "Manchester City",
    "Manchester Utd",
    "Newcastle United",
    "Nottingham Forest",
    "Tottenham Hotspur",
    "West Ham United",
    "Wolves",
    "Leicester City",
    "Ipswich Town",
    "Southampton",
]

def run():
    db = SessionLocal()

    for name in TEAMS_2425:
        existing = db.query(Team).filter(Team.name == name).first()
        if existing:
            continue

        team = Team(name=name, league="Premier League")
        db.add(team)

    db.commit()
    db.close()

if __name__ == "__main__":
    run()