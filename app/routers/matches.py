from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
# ============================
# MATCH ENDPOINTS
# ============================

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/", response_model=schemas.Match)
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


@router.get("/", response_model=list[schemas.Match])
def get_matches(db: Session = Depends(get_db)):
    return db.query(models.Match).all()


@router.get("/{match_id}", response_model=schemas.Match)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

