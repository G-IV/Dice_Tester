from Scripts.Modules.Dice import dice, pips_by_count

class DiceFactory:
    _registry = {
        "dice": dice.Dice,
        "pips_by_count": pips_by_count.Dice
    }

    @classmethod
    def create_dice(cls, dice_type: str, **kwargs) -> dice.Dice:
        dice_class = cls._registry.get(dice_type)
        if not dice_class:
            raise ValueError(f"Dice type '{dice_type}' is not registered.")
        return dice_class(**kwargs)