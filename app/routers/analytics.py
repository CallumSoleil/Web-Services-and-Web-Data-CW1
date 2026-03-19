from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app import models

router = APIRouter(prefix="/analytics", tags=["Analytics"])

DECAY_ALPHA = 0.8  # recency weighting factor


# ------------------------------------------------------------
# Utility: resolve team by ID or name
# ------------------------------------------------------------
def resolve_team(identifier: str, db: Session):
    if identifier.isdigit():
        team = db.query(models.Team).filter(models.Team.id == int(identifier)).first()
    else:
        team = (
            db.query(models.Team)
            .filter(models.Team.name.ilike(identifier))
            .first()
        )
    if not team:
        raise HTTPException(404, f"Team '{identifier}' not found")
    return team


# ------------------------------------------------------------
# Utility: resolve player by ID or name
# ------------------------------------------------------------
def resolve_player(identifier: str, db: Session):
    if identifier.isdigit():
        player = db.query(models.Player).filter(models.Player.id == int(identifier)).first()
    else:
        player = (
            db.query(models.Player)
            .filter(models.Player.name.ilike(identifier))
            .first()
        )
    if not player:
        raise HTTPException(404, f"Player '{identifier}' not found")
    return player


# ------------------------------------------------------------
# PLAYER FORM ENDPOINT
# ------------------------------------------------------------
@router.get("/players/{identifier}/form")
def get_player_form(identifier: str, matches: int = 5, db: Session = Depends(get_db)):
    player = resolve_player(identifier, db)

    performances = (
        db.query(models.Performance)
        .filter(models.Performance.player_id == player.id)
        .order_by(models.Performance.id.desc())
        .limit(matches)
        .all()
    )

    if not performances:
        raise HTTPException(404, "No performances found for this player")

    def performance_score(p):
        raw = (
            4 * p.goals +
            3 * p.assists +
            1 * p.shots_on_target +
            0.5 * p.shots +
            1 * p.tackles_won +
            0.2 * p.crosses -
            1 * p.fouls -
            3 * p.yellow_cards -
            5 * p.red_cards
        )
        if p.minutes <= 0:
            return 0
        return raw * (90 / p.minutes)

    weighted_sum = 0
    weight_total = 0

    for i, perf in enumerate(performances):
        w = DECAY_ALPHA ** i
        weighted_sum += w * performance_score(perf)
        weight_total += w

    form_score = weighted_sum / weight_total if weight_total > 0 else 0

    return {
        "player": player.name,
        "form_score": round(form_score, 2),
    }


# ------------------------------------------------------------
# TEAM FORM ENDPOINT
# ------------------------------------------------------------
@router.get("/teams/{identifier}/form")
def get_team_form(identifier: str, matches: int = 5, db: Session = Depends(get_db)):
    team = resolve_team(identifier, db)

    team_matches = (
        db.query(models.Match)
        .filter(or_(models.Match.home_team_id == team.id,
                    models.Match.away_team_id == team.id))
        .order_by(models.Match.date.desc())
        .limit(matches)
        .all()
    )

    if not team_matches:
        raise HTTPException(404, "No matches found for this team")

    def match_score(m):
        if m.home_team_id == team.id:
            gf, ga = m.home_goals, m.away_goals
        else:
            gf, ga = m.away_goals, m.home_goals

        if gf > ga:
            points = 3
        elif gf == ga:
            points = 1
        else:
            points = 0

        return points + 0.5 * (gf - ga)

    weighted_sum = 0
    weight_total = 0

    for i, match in enumerate(team_matches):
        w = DECAY_ALPHA ** i
        weighted_sum += w * match_score(match)
        weight_total += w

    form_score = weighted_sum / weight_total if weight_total > 0 else 0

    return {
        "team": team.name,
        "form_score": round(form_score, 2),
    }


# ------------------------------------------------------------
# MATCH PREDICTION ENDPOINT
# ------------------------------------------------------------



@router.get("/predict")
def predict_match(home_team: str, away_team: str, db: Session = Depends(get_db)):
    home = resolve_team(home_team, db)
    away = resolve_team(away_team, db)

    if home.id == away.id:
        raise HTTPException(400, "Cannot predict a match between the same team")

    # ---- TEAM FORM ----
    def compute_team_form(team_id):
        matches = (
            db.query(models.Match)
            .filter(or_(models.Match.home_team_id == team_id,
                        models.Match.away_team_id == team_id))
            .order_by(models.Match.date.desc())
            .limit(5)
            .all()
        )

        if not matches:
            return 0

        def score(m):
            if m.home_team_id == team_id:
                gf, ga = m.home_goals, m.away_goals
            else:
                gf, ga = m.away_goals, m.home_goals

            if gf > ga:
                pts = 3
            elif gf == ga:
                pts = 1
            else:
                pts = 0

            return pts + 0.5 * (gf - ga)

        weighted_sum = 0
        weight_total = 0

        for i, match in enumerate(matches):
            w = DECAY_ALPHA ** i
            weighted_sum += w * score(match)
            weight_total += w

        return weighted_sum / weight_total if weight_total > 0 else 0

    home_form = compute_team_form(home.id)
    away_form = compute_team_form(away.id)

    # ---- HOME ADVANTAGE ----
    home_form_adj = home_form * 1.07

    # ---- HEAD TO HEAD ----
    h2h_matches = (
        db.query(models.Match)
        .filter(
            or_(
                (models.Match.home_team_id == home.id) & (models.Match.away_team_id == away.id),
                (models.Match.home_team_id == away.id) & (models.Match.away_team_id == home.id),
            )
        )
        .order_by(models.Match.date.desc())
        .limit(5)
        .all()
    )

    h2h_score = 0
    h2h_home_goals = []
    h2h_away_goals = []

    for m in h2h_matches:
        if m.home_team_id == home.id:
            gf, ga = m.home_goals, m.away_goals
        else:
            gf, ga = m.away_goals, m.home_goals

        h2h_home_goals.append(gf)
        h2h_away_goals.append(ga)

        if gf > ga:
            h2h_score += 3
        elif gf == ga:
            h2h_score += 1
        else:
            h2h_score -= 2

    h2h_norm = (h2h_score / (3 * len(h2h_matches))) if h2h_matches else 0

    import math
    # ---- PROBABILITIES ----
    Rh = home_form_adj + 0.2 * h2h_norm
    Ra = away_form - 0.2 * h2h_norm

    exp_h = math.exp(Rh)
    exp_a = math.exp(Ra)

    home_prob = exp_h / (exp_h + exp_a)
    away_prob = exp_a / (exp_h + exp_a)
    draw_prob = 1 - home_prob - away_prob


    # ---- SCORELINE ----
    def goals_per_game(team_id):
        matches = (
            db.query(models.Match)
            .filter(or_(models.Match.home_team_id == team_id,
                        models.Match.away_team_id == team_id))
            .all()
        )
        if not matches:
            return 1.0, 1.0

        gf_total = 0
        ga_total = 0

        for m in matches:
            if m.home_team_id == team_id:
                gf_total += m.home_goals
                ga_total += m.away_goals
            else:
                gf_total += m.away_goals
                ga_total += m.home_goals

        n = len(matches)
        return gf_total / n, ga_total / n

    home_gf, home_ga = goals_per_game(home.id)
    away_gf, away_ga = goals_per_game(away.id)

    expected_home = (home_gf + away_ga) / 2
    expected_away = (away_gf + home_ga) / 2

    if h2h_matches:
        expected_home = 0.7 * expected_home + 0.3 * (sum(h2h_home_goals) / len(h2h_home_goals))
        expected_away = 0.7 * expected_away + 0.3 * (sum(h2h_away_goals) / len(h2h_away_goals))

    def round_goals(x):
        if x < 0.4: return 0
        if x < 1.2: return 1
        if x < 2.0: return 2
        if x < 3.0: return 3
        return 4

    hg = round_goals(expected_home)
    ag = round_goals(expected_away)

    if home_prob > max(draw_prob, away_prob) and hg <= ag:
        hg = ag + 1
    elif away_prob > max(draw_prob, home_prob) and ag <= hg:
        ag = hg + 1
    elif draw_prob > max(home_prob, away_prob):
        hg = ag

    scoreline = f"{hg}-{ag}"

    return {
        "home_team": home.name,
        "away_team": away.name,
        "home_win_probability": round(home_prob, 3),
        "draw_probability": round(draw_prob, 3),
        "away_win_probability": round(away_prob, 3),
        "predicted_scoreline": scoreline,
    }