from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    league = Column(String, nullable=True)

    # Relationships
    players = relationship("Player", back_populates="team")
    home_matches = relationship("Match", back_populates="home_team", foreign_keys="Match.home_team_id")
    away_matches = relationship("Match", back_populates="away_team", foreign_keys="Match.away_team_id")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    position = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"))

    # Relationships
    team = relationship("Team", back_populates="players")
    performances = relationship("Performance", back_populates="player")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)

    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))

    home_goals = Column(Integer)
    away_goals = Column(Integer)
    competition = Column(String, nullable=True)

    # Relationships
    home_team = relationship("Team", back_populates="home_matches", foreign_keys=[home_team_id])
    away_team = relationship("Team", back_populates="away_matches", foreign_keys=[away_team_id])
    performances = relationship("Performance", back_populates="match")


class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))

    minutes = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    xg = Column(Float)
    xa = Column(Float)

    # Relationships
    player = relationship("Player", back_populates="performances")
    match = relationship("Match", back_populates="performances")