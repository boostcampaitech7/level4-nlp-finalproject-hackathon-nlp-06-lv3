import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from server._core.errors.exceptions.custom_exception import CustomException
from server._core.errors.exceptions.error_code import ErrorCode
from server._core.utils.api_response import ApiResponse
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


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(ApiResponse.error(exc.error_code, exc.detail)),
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(ApiResponse.error(ErrorCode.UNKNOWN_SERVER_ERROR, repr(exc))),
    )


app.include_router(auth_router)
app.include_router(report_router)


@app.get("/")
async def root():
    return {"message": "Hello Meail Mail World!"}
