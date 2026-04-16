from Scripts.Modules.Dice import dice
from Scripts.Modules.Dice.Six_Sided_Pips import by_pattern as six_sided_pips

class DiceFactory:
    _registry = {
        "six_sided_pips": six_sided_pips.SixSidedPips
    }

    @classmethod
    def create_dice(cls, dice_type: str, **kwargs) -> dice.Dice:
        dice_class = cls._registry.get(dice_type)
        if not dice_class:
            raise ValueError(f"Dice type '{dice_type}' is not registered.")
        return dice_class(**kwargs)