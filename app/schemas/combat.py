from pydantic import (
    BaseModel,
    UUID4,
    Field
)
from typing import List

from app.schemas.turn import Turn


class CombatBase(BaseModel):
    _id: UUID4
    monsters: List[str]
    turns: List[Turn] = []
    isFinished: bool = False
    winner: str = None

class CombatOut(CombatBase):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True