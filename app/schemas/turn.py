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

class TurnBase(BaseModel):
    combat_id: str
    monsters: List[MonsterInfo]

class TurnCreate(TurnBase):
    id: UUID = Field(default_factory=uuid4, alias='_id')
    created_at: str = datetime.now().isoformat()

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

    class Config:
        populate_by_name = True

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