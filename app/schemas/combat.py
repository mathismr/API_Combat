from pydantic import (
    BaseModel,
    Field,
)
from typing import List, Optional
from uuid import UUID, uuid4

from app.schemas.turn import Turn


class CombatBase(BaseModel):
    monsters: List[str]
    turns: List[Turn] | None= []
    isFinished: bool | None = False
    winner: str | None = ''

class CombatCreate(CombatBase):
    id: UUID = Field(default_factory=uuid4, alias='_id')

class CombatUpdate(BaseModel):
    turns: Optional[List[Turn]] = None
    isFinished: Optional[bool] = None
    winner: Optional[str] = None

class CombatOut(CombatBase):
    id: UUID = Field(alias='_id')

    class Config:
        populate_by_name = True
