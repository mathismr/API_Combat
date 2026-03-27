from fastapi import APIRouter, Request

from app.crud.CRUD_turn import create_turn
from app.schemas.turn import TurnOut, TurnRequest

router = APIRouter()


@router.post(
    "/new",
    response_model=TurnOut
)
async def http_create_turn(request: Request, turn_in: TurnRequest):
    db = request.app.combat_db
    created_turn = await create_turn(db, turn_in)
    return created_turn