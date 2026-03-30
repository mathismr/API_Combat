from app.exceptions.exc_combat import IllegalCombatArgumentsException, WrongCombatArgumentsException
from app.schemas.combat import CombatCreate, CombatUpdate, MonsterDetail
from app.schemas.turn import SkillCooldown, MonsterCooldowns
from app.utils.external_requests import fetch_api
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import UUID


def _build_monster_detail(monster_id: str, monster_data: dict) -> MonsterDetail:
    return MonsterDetail(
        id=monster_id,
        element=monster_data.get("element"),
        hp=monster_data.get("hp"),
        atk=monster_data.get("atk"),
        defn=monster_data.get("def"),
        vit=monster_data.get("vit"),
        skills=[str(s) for s in monster_data.get("skills", [])],
    )


def _build_initial_cooldowns(monster_id: str, monster_data: dict) -> MonsterCooldowns:
    skill_cooldowns = []
    for skill_id in monster_data.get("skills", []):
        skill = fetch_api("skill", skill_id)
        if not skill:
            continue
        skill_cooldowns.append(SkillCooldown(
            skill_id=str(skill.get("skillId", skill_id)),
            cooldown=skill.get("cooldown", 0),
            remaining_cooldown=0,
        ))
    return MonsterCooldowns(monster_id=monster_id, skills=skill_cooldowns)


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
    result = await db.combats.find_one({"_id": new_combat.inserted_id})

    # Fetch monster data and build details + cooldowns
    monsters_data = [fetch_api("monster", mid) for mid in result["monsters"]]
    result["monster_details"] = [
        _build_monster_detail(mid, mdata).model_dump()
        for mid, mdata in zip(result["monsters"], monsters_data)
    ]
    result["cooldowns"] = [
        _build_initial_cooldowns(mid, mdata).model_dump()
        for mid, mdata in zip(result["monsters"], monsters_data)
    ]

    return result

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