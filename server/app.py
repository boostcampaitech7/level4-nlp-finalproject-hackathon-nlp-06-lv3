from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.database.connection import database
from server.routers.auth_router import auth_router

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

app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello Meail Mail World!"}
