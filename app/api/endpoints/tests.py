from fastapi import APIRouter

from app.utils.external_requests import monster_api_rq

router = APIRouter()

@router.get("/monster/{uuid}")
async def get_monster(uuid: str):
    return monster_api_rq("monster", uuid)

@router.get("/skill/{uuid}")
async def get_skill(uuid: str):
    return monster_api_rq("skill", uuid)