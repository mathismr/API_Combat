from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class MonsterInfo(BaseModel):
    id: str
    used_skill: UUID
    element: str | None = None
    hp: float | None = None
    atk: float | None = None
    defn: float | None = None
    vit: float | None = None
    priority: int | None = None # 0: Monster attacked first | 1: Monster attacked second

class SkillCooldown(BaseModel):
    skill_id: str
    cooldown: int
    remaining_cooldown: int

class MonsterCooldowns(BaseModel):
    monster_id: str
    skills: List[SkillCooldown]

class TurnBase(BaseModel):
    combat_id: str
    monsters: List[MonsterInfo]
    isLastTurn: bool = False

class TurnCreate(TurnBase):
    id: UUID = Field(default_factory=uuid4, alias='_id')
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "combat_id": "example_UUID_1",
                    "user_used_skill_id": "example_UUID_2"
                }
            ]
        }
    }

class TurnOut(TurnBase):
    id: UUID = Field(alias='_id')
    cooldowns: List[MonsterCooldowns] = []

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "combat_id": "c1d2e3f4-a5b6-7890-abcd-ef1234567890",
                    "monsters": [
                        {
                            "id": "m1-uuid",
                            "used_skill": "s1-uuid",
                            "element": "fire",
                            "hp": 850.0,
                            "atk": 120.0,
                            "defn": 60.0,
                            "vit": 90.0,
                            "priority": 0
                        },
                        {
                            "id": "m2-uuid",
                            "used_skill": "s2-uuid",
                            "element": "water",
                            "hp": 720.0,
                            "atk": 110.0,
                            "defn": 55.0,
                            "vit": 85.0,
                            "priority": 1
                        }
                    ],
                    "isLastTurn": False,
                    "cooldowns": [
                        {
                            "monster_id": "m1-uuid",
                            "skills": [
                                {"skill_id": "s1-uuid", "cooldown": 3, "remaining_cooldown": 3},
                                {"skill_id": "s3-uuid", "cooldown": 0, "remaining_cooldown": 0}
                            ]
                        },
                        {
                            "monster_id": "m2-uuid",
                            "skills": [
                                {"skill_id": "s2-uuid", "cooldown": 2, "remaining_cooldown": 2},
                                {"skill_id": "s4-uuid", "cooldown": 1, "remaining_cooldown": 0}
                            ]
                        }
                    ]
                }
            ]
        }
    }

class TurnRequest(BaseModel):
    combat_id: str
    user_used_skill_id: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "combat_id": "example_UUID_combat",
                    "user_used_skill_id": "example_UUID_skill"
                }
            ]
        }
    }