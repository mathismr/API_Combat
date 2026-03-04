from fastapi import APIRouter, Request, HTTPException

from app.schemas.combat import CombatOut, CombatCreate
from app.crud.CRUD_combat import create_combat

router = APIRouter()

@router.post(
"/combat",
     response_model=CombatOut,
     responses={400: {"description": "Bad format for combat creation"}}
)
async def http_create_combat(request: Request, user_in: CombatCreate):
    db = request.app.db
    created_combat = await create_combat(db, user_in)

    if created_combat is None:
        raise HTTPException(status_code=400, detail="Bad format for combat model")

    return created_combat