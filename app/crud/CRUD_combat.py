from app.schemas.combat import  CombatCreate
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_combat(db: AsyncIOMotorDatabase, combat_in: CombatCreate):
    combat_data = combat_in.model_dump(by_alias=True)

    if len(combat_data.get("turns")) > 0 or combat_data.get("winner") is not None:
        return None

    combat_data["winner"] = ''
    new_combat = await db.combats.insert_one(combat_data)

    return await db.combats.find_one({"_id": new_combat.inserted_id})