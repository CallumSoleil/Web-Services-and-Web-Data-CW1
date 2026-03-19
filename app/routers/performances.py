from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/performances", tags=["Performances"])


@router.post("/", response_model=schemas.Performance)
def create_performance(perf: schemas.PerformanceCreate, db: Session = Depends(get_db)):
    """
    Creates a new performance record for a player in a specific match.

    Parameters:
    - perf (PerformanceCreate): Performance details including player_id, match_id, goals, assists, minutes, etc.
    - db (Session): Database session.

    Returns:
    - Performance: The newly created performance record.

    Example Request:
    POST /performances
    {
        "player_id": 12,
        "match_id": 5,
        "minutes": 90,
        "goals": 1,
        "assists": 0,
        "shots": 3,
        "shots_on_target": 2,
        "tackles_won": 1,
        "crosses": 4,
        "fouls": 1,
        "yellow_cards": 0,
        "red_cards": 0
    }

    Example Response:
    {
        "id": 44,
        "player_id": 12,
        "match_id": 5,
        "minutes": 90,
        "goals": 1,
        "assists": 0,
        "shots": 3,
        "shots_on_target": 2,
        "tackles_won": 1,
        "crosses": 4,
        "fouls": 1,
        "yellow_cards": 0,
        "red_cards": 0
    }
    """
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
    """
    Retrieves all performance records for a specific player.

    Parameters:
    - player_id (int): Unique player identifier.
    - db (Session): Database session.

    Returns:
    - List[Performance]: All performances recorded for the player.

    Example Request:
    GET /performances/player/12

    Example Response:
    [
        {
            "id": 44,
            "player_id": 12,
            "match_id": 5,
            "minutes": 90,
            "goals": 1,
            "assists": 0,
            "shots": 3,
            "shots_on_target": 2,
            "tackles_won": 1,
            "crosses": 4,
            "fouls": 1,
            "yellow_cards": 0,
            "red_cards": 0
        }
    ]
    """
    return (
        db.query(models.Performance)
        .filter(models.Performance.player_id == player_id)
        .all()
    )


@router.get("/match/{match_id}", response_model=list[schemas.Performance])
def get_performances_for_match(match_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all performance records for a specific match.

    Parameters:
    - match_id (int): Unique match identifier.
    - db (Session): Database session.

    Returns:
    - List[Performance]: All performances recorded in the match.

    Example Request:
    GET /performances/match/5

    Example Response:
    [
        {
            "id": 44,
            "player_id": 12,
            "match_id": 5,
            "minutes": 90,
            "goals": 1,
            "assists": 0,
            "shots": 3,
            "shots_on_target": 2,
            "tackles_won": 1,
            "crosses": 4,
            "fouls": 1,
            "yellow_cards": 0,
            "red_cards": 0
        }
    ]
    """
    return (
        db.query(models.Performance)
        .filter(models.Performance.match_id == match_id)
        .all()
    )