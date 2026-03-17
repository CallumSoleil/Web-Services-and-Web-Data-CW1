from pydantic import BaseModel

class PlayerBase(BaseModel):
    name: str
    age: int
    position: str
    club: str

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class PerformanceBase(BaseModel):
    goals: int
    assists: int
    minutes: int
    xg: float
    xa: float

class PerformanceCreate(PerformanceBase):
    player_id: int

class Performance(PerformanceBase):
    id: int
    player_id: int

    model_config = {
        "from_attributes": True
    }