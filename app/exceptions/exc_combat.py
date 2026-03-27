class CombatNotFoundException(Exception):
    def __init__(self, combat_id: str):
        super().__init__(
            f"Combat with id {combat_id} not found"
        )

class IllegalCombatArgumentsException(Exception):
    def __init__(self):
        super().__init__(
            "Illegal arguments passed to combat creation"
        )

class WrongCombatArgumentsException(Exception):
    def __init__(self):
        super().__init__(
            "Arguments passed to combat creation contain wrong values"
        )