from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.exceptions.exc_combat import CombatNotFoundException
from app.schemas.turn import TurnCreate, TurnRequest, MonsterInfo
from app.utils.ai import AI
from app.utils.external_requests import fetch_api


def _determine_priority(u_vit: float, ai_vit: float) -> tuple[int, int]:
    if u_vit >= ai_vit:
        return 0, 1
    return 1, 0


async def create_turn(db: AsyncIOMotorDatabase, turn_in: TurnRequest):
    # Récupération du combat
    combat = await db.combats.find_one({"_id": UUID(turn_in.combat_id)})
    if combat is None:
        raise CombatNotFoundException(turn_in.combat_id)

    # Récupération des monstres via l'API externe
    u_monster  = fetch_api("monster", combat["monsters"][0])
    ai_monster = fetch_api("monster", combat["monsters"][1])

    # Premier tour : aucun historique de cooldown
    if len(combat.get("turns", [])) == 0:
        pass  # _build_cooldown_map retournera {} (tous les skills dispo)

    # L'IA choisit son skill
    ai = AI(combat, turn_in.user_used_skill_id)
    ai_skill_id = ai.choose_skill()

    # Calcul des priorités d'attaque (basé sur la vitesse)
    u_priority, ai_priority = _determine_priority(
        u_vit  = u_monster.get("vit",  0.0),
        ai_vit = ai_monster.get("vit", 0.0),
    )

    # Construction des MonsterInfo pour les deux combattants
    monsters = [
        MonsterInfo(
            id        = combat["monsters"][0],
            used_skill= UUID(turn_in.user_used_skill_id),
            element   = u_monster.get("element"),
            hp        = u_monster.get("hp"),
            atk       = u_monster.get("atk"),
            defn      = u_monster.get("def"),
            vit       = u_monster.get("vit"),
            priority  = u_priority,
        ),
        MonsterInfo(
            id        = combat["monsters"][1],
            used_skill= UUID(ai_skill_id),
            element   = ai_monster.get("element"),
            hp        = ai_monster.get("hp"),
            atk       = ai_monster.get("atk"),
            defn      = ai_monster.get("def"),
            vit       = ai_monster.get("vit"),
            priority  = ai_priority,
        ),
    ]

    # Création et persistance du tour
    turn = TurnCreate(combat_id=turn_in.combat_id, monsters=monsters)
    turn_data = turn.model_dump(by_alias=True)

    await db.turns.insert_one(turn_data)

    # Mise à jour de la liste des tours dans le combat
    await db.combats.update_one(
        {"_id": turn_in.combat_id},
        {"$push": {"turns": str(turn.id)}}
    )

    return turn_data