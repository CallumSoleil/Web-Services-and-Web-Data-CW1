from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/matches", tags=["Matches"])

# ============================
# MATCH ENDPOINTS
# ============================

@router.post("/", response_model=schemas.Match)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    """
    Creates a new match between two teams.

    Parameters:
    - match (MatchCreate): Match details including team IDs, goals, and date.
    - db (Session): Database session.

    Returns:
    - Match: The newly created match record.

    Example Request:
    POST /matches
    {
        "home_team_id": 1,
        "away_team_id": 2,
        "home_goals": 2,
        "away_goals": 1,
        "date": "2024-05-12"
    }

    Example Response:
    {
        "id": 15,
        "home_team_id": 1,
        "away_team_id": 2,
        "home_goals": 2,
        "away_goals": 1,
        "date": "2024-05-12"
    }
    """
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
    """
    Retrieves all matches in the database.

    Parameters:
    - db (Session): Database session.

    Returns:
    - List[Match]: All match records.

    Example Request:
    GET /matches

    Example Response:
    [
        {
            "id": 1,
            "home_team_id": 1,
            "away_team_id": 3,
            "home_goals": 3,
            "away_goals": 1,
            "date": "2024-02-10"
        }
    ]
    """
    return db.query(models.Match).all()


@router.get("/{match_id}", response_model=schemas.Match)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single match by its ID.

    Parameters:
    - match_id (int): Unique match identifier.
    - db (Session): Database session.

    Returns:
    - Match: Match record matching the ID.

    Example Request:
    GET /matches/12

    Example Response:
    {
        "id": 12,
        "home_team_id": 4,
        "away_team_id": 6,
        "home_goals": 1,
        "away_goals": 1,
        "date": "2024-03-18"
    }
    """
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match