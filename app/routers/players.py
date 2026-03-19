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
    """
    Creates a new player and assigns them to an existing team.

    Parameters:
    - player (PlayerCreate): Player data including name and team_id.
    - db (Session): Database session.

    Returns:
    - Player: The newly created player record.

    Example Request:
    POST /players
    {
        "name": "Bukayo Saka",
        "team_id": 1
    }

    Example Response:
    {
        "id": 12,
        "name": "Bukayo Saka",
        "team_id": 1
    }
    """

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
    """
    Retrieves all players in the database.

    Parameters:
    - db (Session): Database session.

    Returns:
    - List[Player]: All player records.

    Example Request:
    GET /players

    Example Response:
    [
        {"id": 1, "name": "Erling Haaland", "team_id": 3},
        {"id": 2, "name": "Kevin De Bruyne", "team_id": 3}
    ]
    """

    return db.query(models.Player).all()


@router.get("/{player_id}", response_model=schemas.Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single player by their ID.

    Parameters:
    - player_id (int): Unique player identifier.
    - db (Session): Database session.

    Returns:
    - Player: Player record matching the ID.

    Example Request:
    GET /players/5

    Example Response:
    {
        "id": 5,
        "name": "Martin Ødegaard",
        "team_id": 1
    }
    """

    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/by-name/{name}", response_model=list[schemas.Player])
def get_players_by_name(name: str, db: Session = Depends(get_db)):
    """
    Searches for players whose names contain the given text.

    Parameters:
    - name (str): Partial or full player name to search for.
    - db (Session): Database session.

    Returns:
    - List[Player]: Players whose names match the search query.

    Example Request:
    GET /players/by-name/harry

    Example Response:
    [
        {"id": 7, "name": "Harry Kane", "team_id": 2}
    ]
    """

    return db.query(models.Player).filter(models.Player.name.ilike(f"%{name}%")).all()


