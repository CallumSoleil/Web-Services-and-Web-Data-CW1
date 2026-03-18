from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
from app.routers import players, teams, performances, matches


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(players.router)
app.include_router(teams.router)
app.include_router(performances.router)
app.include_router(matches.router)

@app.get("/")
def root():
    return {
        "message": "Football Analytics API is running",
        "endpoints": {
            "teams": "/teams",
            "players": "/players",
            "matches": "/matches",
            "performances": "/performances",
            "docs": "/docs"
        }
    }

