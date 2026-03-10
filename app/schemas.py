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