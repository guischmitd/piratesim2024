import random
from collections import OrderedDict


class RouletteSelector:
    def __init__(self) -> None:
        self.roulette: OrderedDict = OrderedDict()

    def add_item(self, item, base_chance: float = 1.0):
        assert item not in self.roulette, (
            f"Item {item} is already in this roulette. To modify chances use the"
            " update_chance() method"
        )
        self.roulette[item] = base_chance

    def update_chance(self, item, modifier: float, multiplicative: bool = False):
        assert item in self.roulette, (
            f"Item {item} is not in this roulette. To add a new item chances use the"
            " add_item() method"
        )
        new_chance = (
            self.roulette[item] + modifier
            if not multiplicative
            else self.roulette[item] * modifier
        )
        self.roulette[item] = new_chance

    def roll(self):
        self._remove_impossible_items()
        roll = random.random()
        total_chances = sum([c for _, c in self.roulette.items()])

        lower_bound = 0.0
        for item, chance in self.roulette.items():
            print(lower_bound, roll, chance / total_chances)
            upper_bound = lower_bound + chance / total_chances
            if lower_bound <= roll < upper_bound:
                return item
            lower_bound = upper_bound

    def _remove_impossible_items(self):
        negative_chance_items = []
        for item, chance in self.roulette.items():
            if chance <= 0.0:
                negative_chance_items.append(item)

        for item in negative_chance_items:
            self.roulette.pop(item)
