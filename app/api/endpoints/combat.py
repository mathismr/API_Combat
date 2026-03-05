from fastapi import APIRouter, Request, HTTPException

from app.schemas.combat import CombatOut, CombatCreate
from app.crud.CRUD_combat import create_combat

router = APIRouter()

#
# This route is called when user validates combat creation in web UI
#
@router.post(
"/new",
     response_model=CombatOut,
     responses={400: {"description": "Bad format for combat creation"}}
)
async def http_create_combat(request: Request, combat_in: CombatCreate):
    db = request.app.combat_db
    created_combat = await create_combat(db, combat_in)

    if created_combat is None:
        raise HTTPException(status_code=400, detail="Bad format for combat model")

    return created_combat