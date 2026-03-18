from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/performances", tags=["Performances"])


@router.post("/", response_model=schemas.Performance)
def create_performance(perf: schemas.PerformanceCreate, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == perf.player_id).first()
    match = db.query(models.Match).filter(models.Match.id == perf.match_id).first()

    if not player:
        raise HTTPException(404, "Player not found")
    if not match:
        raise HTTPException(404, "Match not found")

    db_perf = models.Performance(**perf.model_dump())
    db.add(db_perf)
    db.commit()
    db.refresh(db_perf)
    return db_perf


@router.get("/player/{player_id}", response_model=list[schemas.Performance])
def get_performances_for_player(player_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Performance)
        .filter(models.Performance.player_id == player_id)
        .all()
    )


@router.get("/match/{match_id}", response_model=list[schemas.Performance])
def get_performances_for_match(match_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Performance)
        .filter(models.Performance.match_id == match_id)
        .all()
    )