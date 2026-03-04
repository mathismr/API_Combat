from typing import List

from pydantic import BaseModel


class MonsterInfo(BaseModel):
    id: str
    element: str
    hp: float
    atk: float
    defn: float
    vit: float

class Ratio(BaseModel):
    stat: str
    percent: float

class Skill(BaseModel):
    id: str
    monster_id: str
    num: int
    dmg: float
    ratio: Ratio
    cd: int

class Turn(BaseModel):
    number: int
    monsters: List[MonsterInfo] = []