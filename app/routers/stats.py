from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel

from app.database import get_db
from app import models

router = APIRouter(prefix="/stats", tags=["Stats"])


# ============================================================
# TOP SCORERS
# ============================================================

class TopScorerOut(BaseModel):
    player_id: int
    player_name: str
    goals: int


@router.get("/top-scorers", response_model=list[TopScorerOut])
def top_scorers(limit: int = 10, db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.Player.id.label("player_id"),
            models.Player.name.label("player_name"),
            func.sum(models.Performance.goals).label("goals")
        )
        .join(models.Performance, models.Performance.player_id == models.Player.id)
        .group_by(models.Player.id)
        .order_by(desc("goals"))
        .limit(limit)
        .all()
    )
    return rows


# ============================================================
# PLAYER SEASON SUMMARY
# ============================================================

class PlayerSeasonSummary(BaseModel):
    player_id: int
    name: str
    appearances: int
    minutes: int
    goals: int
    assists: int
    shots: int
    tackles: int
    crosses: int


@router.get("/players/{identifier}/summary", response_model=PlayerSeasonSummary)
def player_summary(identifier: str, db: Session = Depends(get_db)):

    # Resolve identifier → player
    if identifier.isdigit():
        player = db.query(models.Player).filter(models.Player.id == int(identifier)).first()
    else:
        player = db.query(models.Player).filter(models.Player.name.ilike(identifier)).first()

    if not player:
        raise HTTPException(404, "Player not found")

    player_id = player.id

    stats = (
        db.query(
            func.count(models.Performance.id).label("apps"),
            func.sum(models.Performance.minutes).label("minutes"),
            func.sum(models.Performance.goals).label("goals"),
            func.sum(models.Performance.assists).label("assists"),
            func.sum(models.Performance.shots).label("shots"),
            func.sum(models.Performance.tackles_won).label("tackles"),
            func.sum(models.Performance.crosses).label("crosses"),
        )
        .filter(models.Performance.player_id == player_id)
        .first()
    )

    return PlayerSeasonSummary(
        player_id=player.id,
        name=player.name,
        appearances=stats.apps or 0,
        minutes=stats.minutes or 0,
        goals=stats.goals or 0,
        assists=stats.assists or 0,
        shots=stats.shots or 0,
        tackles=stats.tackles or 0,
        crosses=stats.crosses or 0,
    )


# ============================================================
# TEAM SEASON SUMMARY
# ============================================================

class TeamSummaryOut(BaseModel):
    team_id: int
    team_name: str
    goals_for: int
    goals_against: int
    shots_for: int
    shots_against: int


@router.get("/teams/{identifier}/summary", response_model=TeamSummaryOut)
def team_summary(identifier: str, db: Session = Depends(get_db)):

    # Resolve identifier → team
    if identifier.isdigit():
        team = db.query(models.Team).filter(models.Team.id == int(identifier)).first()
    else:
        team = db.query(models.Team).filter(models.Team.name.ilike(identifier)).first()

    if not team:
        raise HTTPException(404, "Team not found")

    team_id = team.id

    # Goals For
    gf = (
        db.query(func.sum(models.Performance.goals))
        .filter(models.Performance.player.has(models.Player.team_id == team_id))
        .scalar() or 0
    )

    # Goals Against
    ga = (
        db.query(func.sum(models.Performance.goals))
        .join(models.Match, models.Performance.match_id == models.Match.id)
        .filter(models.Performance.player.has(models.Player.team_id != team_id))
        .filter(
            (models.Match.home_team_id == team_id) |
            (models.Match.away_team_id == team_id)
        )
        .scalar() or 0
    )

    # Shots For
    sf = (
        db.query(func.sum(models.Performance.shots))
        .filter(models.Performance.player.has(models.Player.team_id == team_id))
        .scalar() or 0
    )

    # Shots Against
    sa = (
        db.query(func.sum(models.Performance.shots))
        .join(models.Match, models.Performance.match_id == models.Match.id)
        .filter(models.Performance.player.has(models.Player.team_id != team_id))
        .filter(
            (models.Match.home_team_id == team_id) |
            (models.Match.away_team_id == team_id)
        )
        .scalar() or 0
    )

    return TeamSummaryOut(
        team_id=team.id,
        team_name=team.name,
        goals_for=gf,
        goals_against=ga,
        shots_for=sf,
        shots_against=sa,
    )


# ============================================================
# MATCH ANALYTICS (NO xG/xA)
# ============================================================

class MatchAnalytics(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    home_shots: int
    away_shots: int
    home_tackles: int
    away_tackles: int


@router.get("/matches/{match_id}/analytics", response_model=MatchAnalytics)
def match_analytics(match_id: int, db: Session = Depends(get_db)):

    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match not found")

    # Home stats
    home_shots = (
        db.query(func.sum(models.Performance.shots))
        .filter(models.Performance.match_id == match_id)
        .filter(models.Performance.player.has(team_id=match.home_team_id))
        .scalar() or 0
    )

    home_tackles = (
        db.query(func.sum(models.Performance.tackles_won))
        .filter(models.Performance.match_id == match_id)
        .filter(models.Performance.player.has(team_id=match.home_team_id))
        .scalar() or 0
    )

    # Away stats
    away_shots = (
        db.query(func.sum(models.Performance.shots))
        .filter(models.Performance.match_id == match_id)
        .filter(models.Performance.player.has(team_id=match.away_team_id))
        .scalar() or 0
    )

    away_tackles = (
        db.query(func.sum(models.Performance.tackles_won))
        .filter(models.Performance.match_id == match_id)
        .filter(models.Performance.player.has(team_id=match.away_team_id))
        .scalar() or 0
    )

    return MatchAnalytics(
        match_id=match.id,
        home_team=match.home_team.name,
        away_team=match.away_team.name,
        home_goals=match.home_goals,
        away_goals=match.away_goals,
        home_shots=home_shots,
        away_shots=away_shots,
        home_tackles=home_tackles,
        away_tackles=away_tackles,
    )