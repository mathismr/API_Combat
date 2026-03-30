from fastapi import APIRouter, Request

from app.crud.CRUD_turn import create_turn, get_turn
from app.schemas.turn import TurnOut, TurnRequest

router = APIRouter()


@router.get(
    "/get/{turn_id}",
    response_model=TurnOut
)
async def http_get_turn(request: Request, turn_id: str):
    db = request.app.combat_db
    return await get_turn(db, turn_id)


@router.post(
    "/new",
    response_model=TurnOut
)
async def http_create_turn(request: Request, turn_in: TurnRequest):
    db = request.app.combat_db
    created_turn = await create_turn(db, turn_in)
    return created_turn