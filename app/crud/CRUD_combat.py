from app.exceptions.exc_combat import IllegalCombatArgumentsException, WrongCombatArgumentsException
from app.schemas.combat import CombatCreate, CombatUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import UUID


async def create_combat(db: AsyncIOMotorDatabase, combat_in: CombatCreate):
    combat_data = combat_in.model_dump(by_alias=True)

    if (len(combat_data.get("turns")) > 0 or
        combat_data.get("isFinished") is True or
        combat_data.get("winner") != ''):
        raise IllegalCombatArgumentsException()

    if (combat_data.get("monsters") is None or
        len(combat_data.get("monsters")) == 0 or
        len(combat_data.get("monsters")) > 2):
        raise WrongCombatArgumentsException()

    new_combat = await db.combats.insert_one(combat_data)

    return await db.combats.find_one({"_id": new_combat.inserted_id})

async def update_combat(db: AsyncIOMotorDatabase, combat_in: CombatUpdate):
    update_data = combat_in.model_dump()
    combat_id = UUID(update_data.get("combat_id"))
    user_used_skill = update_data.get("user_used_skill") # à modifier pour ajouter l'uuid d'un nouveau turn à l'entrée du combat

    if len(update_data) > 0:
        update_result = await db.combats.update_one(
            {"_id": combat_id},
            {"$set": update_data}
        )

        if update_result.modified_count == 1:
            updated_combat = await db.combats.find_one({"_id": combat_id})
            return updated_combat

    return await db.combats.find_one({"_id": combat_id})