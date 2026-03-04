from fastapi import FastAPI
from app.api.api import main_router

app = FastAPI(
    title="GatchAPI - Combat API",
    description="API for Gatcha's Combat System",
    version="0.1.0"
)

app.include_router(main_router)

@app.get("/")
async def root():
    return {"message": "API is running"}