from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    position = Column(String)
    club = Column(String)

class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    goals = Column(Integer)
    assists = Column(Integer)
    minutes = Column(Integer)
    xg = Column(Float)
    xa = Column(Float)