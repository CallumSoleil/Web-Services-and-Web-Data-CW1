from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
from app.routers import players, teams, performances, matches, stats, analytics


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(players.router)
app.include_router(teams.router)
app.include_router(performances.router)
app.include_router(matches.router)
app.include_router(stats.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    """
    Root endpoint confirming the API is running.

    Returns:
    - message: Status message.
    - endpoints: Key route groups in the API.
    """

    return {
        "message": "Football Analytics API is running",
        "endpoints": {
            "teams": "/teams",
            "players": "/players",
            "matches": "/matches",
            "performances": "/performances",
            "stats": "/stats",
            "analytics": "/analytics",
        }

    }

