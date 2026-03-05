from app.schemas.combat import CombatCreate, CombatUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import UUID


async def create_combat(db: AsyncIOMotorDatabase, combat_in: CombatCreate):
    combat_data = combat_in.model_dump(by_alias=True)

    if (len(combat_data.get("turns")) > 0 or
            combat_data.get("isFinished") is True or
            combat_data.get("winner") != ''):
        return None

    new_combat = await db.combats.insert_one(combat_data)

    return await db.combats.find_one({"_id": new_combat.inserted_id})

async def update_combat(db: AsyncIOMotorDatabase, combat_id: UUID, combat_in: CombatUpdate):
    update_data = combat_in.model_dump(exclude_unset=True)

    if len(update_data) > 0:
        update_result = await db.combats.update_one(
            {"_id": combat_id},
            {"$set": update_data}
        )

        if update_result.modified_count == 1:
            updated_combat = await db.combats.find_one({"_id": combat_id})
            return updated_combat

    return await db.combats.find_one({"_id": combat_id})