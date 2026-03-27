from uuid import UUID

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.exceptions.exc_combat import CombatNotFoundException
from app.schemas.turn import TurnCreate, TurnRequest, MonsterInfo
from app.utils.ai import AI, affinity_chart
from app.utils.external_requests import fetch_api


async def get_turn(db: AsyncIOMotorDatabase, turn_id: str):
    turn = await db.turns.find_one({"_id": UUID(turn_id)})
    if turn is None:
        raise HTTPException(status_code=404, detail=f"Turn {turn_id} not found")
    return turn

DEF_SCALING_FACTOR = 100


def _determine_priority(u_vit: float, ai_vit: float) -> tuple[int, int]:
    if u_vit >= ai_vit:
        return 0, 1
    return 1, 0


def _affinity_multiplier(attacker_element: str, defender_element: str) -> float:
    atk_el = (attacker_element or "").lower()
    def_el = (defender_element or "").lower()
    chart = affinity_chart.get(atk_el, {})
    if def_el in chart.get("strengths", []):
        return 1.5
    if def_el in chart.get("weaknesses", []):
        return 0.5
    return 1.0


def _calculate_damage(skill: dict, attacker: dict, defender: dict) -> float:
    base = skill.get("damage", 0.0)
    ratio = skill.get("ratio", {})
    stat_map = {
        "HP":  attacker.get("hp",  0.0),
        "ATK": attacker.get("atk", 0.0),
        "DEF": attacker.get("def", 0.0),
        "VIT": attacker.get("vit", 0.0),
    }
    ratio_bonus = stat_map.get(ratio.get("stat", "").upper(), 0.0) * ratio.get("percent", 0.0)
    raw_damage = base + ratio_bonus
    affinity = _affinity_multiplier(attacker.get("element", ""), defender.get("element", ""))
    def_mitigation = 1.0 + (defender.get("def", 0.0) / DEF_SCALING_FACTOR)
    return max(0.0, (raw_damage * affinity) / def_mitigation)


async def create_turn(db: AsyncIOMotorDatabase, turn_in: TurnRequest):
    # Récupération du combat
    combat = await db.combats.find_one({"_id": UUID(turn_in.combat_id)})
    if combat is None:
        raise CombatNotFoundException(turn_in.combat_id)

    # Récupération des stats de base depuis l'API externe
    u_monster  = fetch_api("monster", combat["monsters"][0])
    ai_monster = fetch_api("monster", combat["monsters"][1])

    # Récupération des tours passés depuis la DB (pour l'IA et le HP courant)
    turns = combat.get("turns", [])
    turns_data = []
    for turn_id in turns:
        t = await db.turns.find_one({"_id": UUID(turn_id)})
        if t:
            turns_data.append(t)

    # HP courant : issu du dernier tour si disponible, sinon HP de base
    if turns_data:
        for m in turns_data[-1].get("monsters", []):
            if m["id"] == combat["monsters"][0]:
                u_monster["hp"] = m["hp"]
            elif m["id"] == combat["monsters"][1]:
                ai_monster["hp"] = m["hp"]

    # L'IA choisit son skill (reçoit les tours déjà chargés pour éviter un appel HTTP circulaire)
    ai = AI(combat, turn_in.user_used_skill_id, turns_data=turns_data)
    ai_skill_id = ai.choose_skill()

    # Récupération des skills utilisés
    u_skill  = fetch_api("skill", turn_in.user_used_skill_id)
    ai_skill = fetch_api("skill", ai_skill_id)

    # Calcul des priorités d'attaque (basé sur la vitesse)
    u_priority, ai_priority = _determine_priority(
        u_vit  = u_monster.get("vit",  0.0),
        ai_vit = ai_monster.get("vit", 0.0),
    )

    # Application des dégâts dans l'ordre de priorité
    u_hp  = float(u_monster.get("hp",  0.0))
    ai_hp = float(ai_monster.get("hp", 0.0))

    first_attacker,  first_skill,  first_hp_ref,  other_hp_ref  = (
        (u_monster, u_skill,  "u",  "ai") if u_priority == 0
        else (ai_monster, ai_skill, "ai", "u")
    )
    second_attacker, second_skill = (
        (ai_monster, ai_skill) if u_priority == 0
        else (u_monster, u_skill)
    )

    # Premier attaquant
    if first_hp_ref == "u":
        dmg = _calculate_damage(first_skill, u_monster, ai_monster)
        ai_hp = max(0.0, ai_hp - dmg)
    else:
        dmg = _calculate_damage(first_skill, ai_monster, u_monster)
        u_hp = max(0.0, u_hp - dmg)

    # Deuxième attaquant (seulement s'il est encore en vie)
    if first_hp_ref == "u" and ai_hp > 0:
        dmg2 = _calculate_damage(second_skill, ai_monster, u_monster)
        u_hp = max(0.0, u_hp - dmg2)
    elif first_hp_ref == "ai" and u_hp > 0:
        dmg2 = _calculate_damage(second_skill, u_monster, ai_monster)
        ai_hp = max(0.0, ai_hp - dmg2)

    # Construction des MonsterInfo avec HP mis à jour
    monsters = [
        MonsterInfo(
            id        = combat["monsters"][0],
            used_skill= UUID(turn_in.user_used_skill_id),
            element   = u_monster.get("element"),
            hp        = u_hp,
            atk       = u_monster.get("atk"),
            defn      = u_monster.get("def"),
            vit       = u_monster.get("vit"),
            priority  = u_priority,
        ),
        MonsterInfo(
            id        = combat["monsters"][1],
            used_skill= UUID(ai_skill_id),
            element   = ai_monster.get("element"),
            hp        = ai_hp,
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

    # Mise à jour du combat : ajout du tour + fin éventuelle
    combat_update: dict = {"$push": {"turns": str(turn.id)}}

    if u_hp <= 0 or ai_hp <= 0:
        winner = combat["monsters"][1] if u_hp <= 0 else combat["monsters"][0]
        combat_update["$set"] = {"isFinished": True, "winner": winner}

    await db.combats.update_one({"_id": UUID(turn_in.combat_id)}, combat_update)

    return turn_data
