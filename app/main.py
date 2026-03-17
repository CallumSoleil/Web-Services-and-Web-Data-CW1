from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Football Analytics API is running",
        "endpoints": {
            "teams": "/teams",
            "players": "/players",
            "matches": "/matches",
            "performances": "/performances",
            "docs": "/docs"
        }
    }

# ============================
# TEAM ENDPOINTS
# ============================

@app.post("/teams", response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    db_team = models.Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@app.get("/teams", response_model=list[schemas.Team])
def get_teams(db: Session = Depends(get_db)):
    return db.query(models.Team).all()


@app.get("/teams/{team_id}", response_model=schemas.Team)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team



# ============================
# PLAYER ENDPOINTS
# ============================

@app.post("/players", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    # Ensure team exists
    team = db.query(models.Team).filter(models.Team.id == player.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@app.get("/players", response_model=list[schemas.Player])
def get_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()


@app.get("/players/{player_id}", response_model=schemas.Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.get("/players/by-name/{name}", response_model=list[schemas.Player])
def get_players_by_name(name: str, db: Session = Depends(get_db)):
    return db.query(models.Player).filter(models.Player.name.ilike(f"%{name}%")).all()



# ============================
# MATCH ENDPOINTS
# ============================

@app.post("/matches", response_model=schemas.Match)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    # Validate teams
    home = db.query(models.Team).filter(models.Team.id == match.home_team_id).first()
    away = db.query(models.Team).filter(models.Team.id == match.away_team_id).first()

    if not home or not away:
        raise HTTPException(status_code=404, detail="One or both teams not found")

    db_match = models.Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@app.get("/matches", response_model=list[schemas.Match])
def get_matches(db: Session = Depends(get_db)):
    return db.query(models.Match).all()


@app.get("/matches/{match_id}", response_model=schemas.Match)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match



# ============================
# PERFORMANCE ENDPOINTS
# ============================

@app.post("/performances", response_model=schemas.Performance)
def create_performance(perf: schemas.PerformanceCreate, db: Session = Depends(get_db)):
    # Validate player + match
    player = db.query(models.Player).filter(models.Player.id == perf.player_id).first()
    match = db.query(models.Match).filter(models.Match.id == perf.match_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    db_perf = models.Performance(**perf.model_dump())
    db.add(db_perf)
    db.commit()
    db.refresh(db_perf)
    return db_perf


@app.get("/players/{player_id}/performances", response_model=list[schemas.Performance])
def get_performances_for_player(player_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Performance)
        .filter(models.Performance.player_id == player_id)
        .all()
    )


@app.get("/matches/{match_id}/performances", response_model=list[schemas.Performance])
def get_performances_for_match(match_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Performance)
        .filter(models.Performance.match_id == match_id)
        .all()
    )