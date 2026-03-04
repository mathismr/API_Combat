from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.api.api import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(settings.MONOGODB_URI)
    app.db = app.mongodb_client[settings.DATABASE_NAME]
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")

    yield

    app.mongodb_client.close()
    print(f"Disconnected from MongoDB: {settings.DATABASE_NAME}")

app = FastAPI(
    title="GatchAPI - Combat API",
    description="API for Gatcha's Combat System",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(main_router)

@app.get("/")
async def root():
    return {"message": "API is running"}