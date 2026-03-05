from fastapi import APIRouter

from app.api.endpoints import combat, tests

main_router = APIRouter()

main_router.include_router(combat.router, prefix="/combats", tags=["combats"])
main_router.include_router(tests.router, prefix="/tests", tags=["tests"])