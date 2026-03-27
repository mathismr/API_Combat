from fastapi import APIRouter

from app.api.endpoints import combat, tests, turn

main_router = APIRouter()

main_router.include_router(combat.router, prefix="/combats", tags=["combats"])
main_router.include_router(turn.router, prefix="/turns", tags=["turns"])
main_router.include_router(tests.router, prefix="/tests", tags=["tests"])