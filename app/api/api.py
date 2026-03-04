from fastapi import APIRouter

from app.api.endpoints import combat

main_router = APIRouter()

main_router.include_router(combat.router, prefix="/combats", tags=["combats"])