from fastapi import APIRouter, HTTPException, Depends, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import sqlite3
import bcrypt
import jwt
import datetime
import os
from db import get_connection
import os


ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


def require_admin(x_admin_password: str = Header(default="")):
    if not ADMIN_PASSWORD or x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin password required",
        )


JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14  # 14 days


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


class SignupBody(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def get_user_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT id, email, password_hash FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "email": row[1], "password_hash": row[2]}


@router.post("/signup", response_model=TokenResponse, dependencies=[Depends(require_admin)])
def signup(body: SignupBody):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")
    existing = get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    try:
        cur.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (body.email, password_hash, now),
        )
        conn.commit()
    finally:
        conn.close()

    return _issue_token_for_email(body.email)


def _issue_token_for_email(email: str) -> TokenResponse:
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user")
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not bcrypt.checkpw(form_data.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return _issue_token_for_email(user["email"])


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
        email = payload.get("email")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": int(user_id), "email": email}


