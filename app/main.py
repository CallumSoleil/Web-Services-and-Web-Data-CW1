from fastapi import FastAPI
from app.database import Base, engine
from app import models

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API is running"}

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models

# PLAYERS

@app.post("/players", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/players/{player_id}", response_model=schemas.Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.get("/players/by-name/{name}", response_model=list[schemas.Player])
def get_player_by_name(name: str, db: Session = Depends(get_db)):
    players = (
        db.query(models.Player)
        .filter(models.Player.name.ilike(name))
        .all()
    )
    if not players:
        raise HTTPException(status_code=404, detail="No players found with that name")
    return players




# PERFORMANCE
@app.post("/performances", response_model=schemas.Performance)
def create_performance(perf: schemas.PerformanceCreate, db: Session = Depends(get_db)):
    # Check player exists
    player = db.query(models.Player).filter(models.Player.id == perf.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    db_perf = models.Performance(**perf.model_dump())
    db.add(db_perf)
    db.commit()
    db.refresh(db_perf)
    return db_perf

@app.get("/players/{player_id}/performances", response_model=list[schemas.Performance])
def get_performances_for_player(player_id: int, db: Session = Depends(get_db)):
    performances = (
        db.query(models.Performance)
        .filter(models.Performance.player_id == player_id)
        .all()
    )
    if not performances:
        raise HTTPException(status_code=404, detail="No performances found for this player")
    return performances