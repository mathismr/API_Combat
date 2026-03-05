from fastapi import APIRouter, Request, HTTPException
from uuid import UUID

from app.schemas.combat import CombatOut, CombatCreate, CombatUpdate
from app.crud.CRUD_combat import create_combat, update_combat

router = APIRouter()

@router.post(
"/combat/new",
     response_model=CombatOut,
     responses={400: {"description": "Bad format for combat creation"}}
)
async def http_create_combat(request: Request, combat_in: CombatCreate):
    db = request.app.db
    created_combat = await create_combat(db, combat_in)

    if created_combat is None:
        raise HTTPException(status_code=400, detail="Bad format for combat model")

    return created_combat

@router.patch(
    "/combat/update/{combat_id}",
    response_model=CombatOut,
    responses={400: {"description": "Bad format for combat update"}}
)
async def http_update_combat(request: Request, combat_id: str, combat_in: CombatUpdate):
    db = request.app.db

    combat = await db.combats.find_one({"_id": UUID(combat_id)})
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")

    updated_combat = await update_combat(db, UUID(combat_id), combat_in)
    return updated_combat