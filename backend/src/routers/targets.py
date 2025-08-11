from fastapi import APIRouter, Depends
from pydantic import BaseModel
import datetime
from db import get_connection
from routers.auth import get_current_user

router = APIRouter()

class Targets(BaseModel):
    protein: float
    carbs: float
    fat: float
    calories: float

@router.get("/targets")
def get_targets(user=Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT protein, carbs, fat, calories FROM user_targets_history ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row:
        return {"protein": row[0], "carbs": row[1], "fat": row[2], "calories": row[3]}
    return {"protein": 120, "carbs": 195, "fat": 60, "calories": 1800}

@router.post("/targets")
def update_targets(targets: Targets, user=Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_targets_history (ts, protein, carbs, fat, calories) VALUES (?, ?, ?, ?, ?)",
        (datetime.datetime.now().isoformat(), targets.protein, targets.carbs, targets.fat, targets.calories)
    )
    conn.commit()
    conn.close()
    return {"success": True}

@router.get("/targets/history")
def get_targets_history(user=Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT ts, protein, carbs, fat, calories FROM user_targets_history ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [
        {"ts": r[0], "protein": r[1], "carbs": r[2], "fat": r[3], "calories": r[4]}
        for r in rows
    ]
