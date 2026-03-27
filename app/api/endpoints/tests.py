from fastapi import APIRouter

from app.utils.external_requests import fetch_api

router = APIRouter()

@router.get("/monster/{uuid}")
async def get_monster(uuid: str):
    return fetch_api("monster", uuid)

@router.get("/skill/{uuid}")
async def get_skill(uuid: str):
    return fetch_api("skill", uuid)