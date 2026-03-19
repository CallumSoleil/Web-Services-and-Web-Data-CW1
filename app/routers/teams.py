from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import verify_credentials

router = APIRouter(prefix="/teams", tags=["Teams"])

# ============================
# TEAM ENDPOINTS
# ============================

@router.post("/", response_model=schemas.Team, dependencies=[Depends(verify_credentials)])
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    """
    Creates a new team and stores it in the database.

    Parameters:
    - team (TeamCreate): Team data including name.
    - db (Session): Database session.

    Returns:
    - Team: The newly created team record.

    Example Request:
    POST /teams
    {
        "name": "Arsenal"
    }

    Example Response:
    {
        "id": 1,
        "name": "Arsenal"
    }
    """
    db_team = models.Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.get("/", response_model=list[schemas.Team])
def get_teams(db: Session = Depends(get_db)):
    """
    Retrieves all teams in the database.

    Parameters:
    - db (Session): Database session.

    Returns:
    - List[Team]: All team records.

    Example Request:
    GET /teams

    Example Response:
    [
        {"id": 1, "name": "Arsenal"},
        {"id": 2, "name": "Chelsea"}
    ]
    """
    return db.query(models.Team).all()


@router.get("/{team_id}", response_model=schemas.Team)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single team by its ID.

    Parameters:
    - team_id (int): Unique team identifier.
    - db (Session): Database session.

    Returns:
    - Team: Team record matching the ID.

    Example Request:
    GET /teams/2

    Example Response:
    {
        "id": 2,
        "name": "Chelsea"
    }
    """
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team