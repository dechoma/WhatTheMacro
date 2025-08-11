from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import intake, targets, food_macros, auth
from db import init_db

init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(intake.router, prefix="/api")
app.include_router(targets.router, prefix="/api")
app.include_router(food_macros.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
