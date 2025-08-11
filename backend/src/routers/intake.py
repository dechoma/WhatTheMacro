from fastapi import APIRouter, Form, Depends
from db import get_connection
from routers.auth import get_current_user

router = APIRouter()

@router.get("/intake/{date}")
def get_intake(date: str, user=Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM daily_intake WHERE date=?", (date,)).fetchall()
    conn.close()
    sum_macro = {"protein": 0, "carbs": 0, "fat": 0, "calories": 0}
    entries = []
    for r in rows:
        sum_macro["protein"] += r[2]
        sum_macro["carbs"] += r[3]
        sum_macro["fat"] += r[4]
        sum_macro["calories"] += r[5]
        entries.append({
            "id": r[0], "date": r[1], "protein": r[2], "carbs": r[3], "fat": r[4],
            "calories": r[5], "description": r[6]
        })
    return {"sum": sum_macro, "entries": entries}

@router.post("/intake")
async def add_intake(
    date: str = Form(...),
    protein: float = Form(...),
    carbs: float = Form(...),
    fat: float = Form(...),
    calories: float = Form(...),
    description: str = Form(""),
    user=Depends(get_current_user)
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO daily_intake (date, protein, carbs, fat, calories, description) VALUES (?, ?, ?, ?, ?, ?)",
        (date, protein, carbs, fat, calories, description)
    )
    conn.commit()
    conn.close()
    return {"success": True}

@router.delete("/intake/{entry_id}")
def delete_intake(entry_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM daily_intake WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    return {"success": True}
