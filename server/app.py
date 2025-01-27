import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from server.database.connection import database
from server.routers.auth_router import auth_router
from server.routers.report_router import report_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    await database.connect()
    print("Database connected.")
    yield  # Lifespan 동안 실행될 코드
    # 앱 종료 시 실행
    await database.disconnect()
    print("Database disconnected.")


app = FastAPI(lifespan=lifespan)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_KEY"),
    max_age=180 * 24 * 60 * 60,  # 180일
    same_site="lax",
    https_only=True,
)

app.include_router(auth_router)
app.include_router(report_router)


@app.get("/")
async def root():
    return {"message": "Hello Meail Mail World!"}
