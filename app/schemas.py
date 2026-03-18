from pydantic import BaseModel
from datetime import date

# ============================
# TEAM SCHEMAS
# ============================

class TeamBase(BaseModel):
    name: str
    league: str | None = None

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    model_config = {"from_attributes": True}


# ============================
# PLAYER SCHEMAS
# ============================

class PlayerBase(BaseModel):
    name: str
    age: int
    position: str
    team_id: int

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int
    model_config = {"from_attributes": True}


# ============================
# MATCH SCHEMAS
# ============================

class MatchBase(BaseModel):
    date: date
    home_team_id: int
    away_team_id: int
    home_goals: int
    away_goals: int
    competition: str | None = None

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int
    model_config = {"from_attributes": True}


# ============================
# PERFORMANCE SCHEMAS
# ============================

class PerformanceBase(BaseModel):
    player_id: int
    match_id: int
    minutes: int
    goals: int
    assists: int
    shots: int
    shots_on_target: int
    crosses: int
    offsides: int
    tackles_won: int
    interceptions: int
    fouls: int
    fouled: int
    yellow_cards: int
    red_cards: int

class PerformanceCreate(PerformanceBase):
    pass

class Performance(PerformanceBase):
    id: int
    model_config = {"from_attributes": True}