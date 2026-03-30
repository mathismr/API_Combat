from uuid import UUID

from fastapi import APIRouter, Request, HTTPException

from app.exceptions.exc_combat import IllegalCombatArgumentsException
from app.schemas.combat import CombatOut, CombatCreate
from app.crud.CRUD_combat import create_combat

router = APIRouter()


@router.get("/get/{uuid}", response_model=CombatOut)
async def http_get_combat(request: Request, uuid: str):
    db = request.app.combat_db
    combat = await db.combats.find_one({"_id": UUID(uuid)})

    if combat is None:
        raise HTTPException(status_code=404, detail="Combat not found")

    return combat

#
# This route is called when user validates combat creation in web UI
# IMPORTANT: ["PLAYER_MONSTER_UUID", "AI_MONSTER_UUID"]
#
@router.post(
"/new",
     response_model=CombatOut,
     responses={400: {"description": "Bad format for combat creation"}}
)
async def http_create_combat(request: Request, combat_in: CombatCreate):
    db = request.app.combat_db
    try:
        created_combat = await create_combat(db, combat_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return created_combat

# à implémenter
# méthode patch pour ajouter un tour (UUID) au combat