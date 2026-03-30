from pydantic import (
    BaseModel,
    Field,
)
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from app.schemas.turn import MonsterCooldowns


class MonsterDetail(BaseModel):
    id: str
    element: str | None = None
    hp: float | None = None
    atk: float | None = None
    defn: float | None = None
    vit: float | None = None
    skills: List[str] = []


class CombatBase(BaseModel):
    monsters: List[str]
    turns: List[str] | None = []
    isFinished: bool | None = False
    winner: str | None = ''

class CombatCreate(CombatBase):
    id: UUID = Field(default_factory=uuid4, alias='_id')
    created_at: str = datetime.now().isoformat()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "monsters": ["example_UUID_1", "example_UUID_2"]
                }
            ]
        }
    }

class CombatUpdate(BaseModel):
    combat_id: str
    user_used_skill: str

class CombatOut(CombatBase):
    id: UUID = Field(alias='_id')
    monster_details: List[MonsterDetail] = []
    cooldowns: List[MonsterCooldowns] = []

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "monsters": ["m1-uuid", "m2-uuid"],
                    "turns": [],
                    "isFinished": False,
                    "winner": "",
                    "monster_details": [
                        {
                            "id": "m1-uuid",
                            "element": "fire",
                            "hp": 1000.0,
                            "atk": 120.0,
                            "defn": 60.0,
                            "vit": 90.0,
                            "skills": ["s1-uuid", "s2-uuid"]
                        },
                        {
                            "id": "m2-uuid",
                            "element": "water",
                            "hp": 950.0,
                            "atk": 110.0,
                            "defn": 55.0,
                            "vit": 85.0,
                            "skills": ["s3-uuid", "s4-uuid"]
                        }
                    ],
                    "cooldowns": [
                        {
                            "monster_id": "m1-uuid",
                            "skills": [
                                {"skill_id": "s1-uuid", "cooldown": 3, "remaining_cooldown": 0},
                                {"skill_id": "s2-uuid", "cooldown": 0, "remaining_cooldown": 0}
                            ]
                        },
                        {
                            "monster_id": "m2-uuid",
                            "skills": [
                                {"skill_id": "s3-uuid", "cooldown": 2, "remaining_cooldown": 0},
                                {"skill_id": "s4-uuid", "cooldown": 1, "remaining_cooldown": 0}
                            ]
                        }
                    ]
                }
            ]
        }
    }
