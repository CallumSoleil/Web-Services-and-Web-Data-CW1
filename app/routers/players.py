from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
# ============================
# PLAYER ENDPOINTS
# ============================

router = APIRouter(prefix="/players", tags=["Players"])

@router.post("/", response_model=schemas.Player)
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


@router.get("/", response_model=list[schemas.Player])
def get_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()


@router.get("/{player_id}", response_model=schemas.Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/by-name/{name}", response_model=list[schemas.Player])
def get_players_by_name(name: str, db: Session = Depends(get_db)):
    return db.query(models.Player).filter(models.Player.name.ilike(f"%{name}%")).all()


