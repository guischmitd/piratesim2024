import random
import time
from collections import OrderedDict
from typing import Iterable, Optional


def get_seed():
    large_prime1 = 314105291
    large_prime2 = 914105341

    current_time = time.time()

    fractional_time = current_time - int(current_time)
    seed = int((fractional_time * large_prime1) % large_prime2)

    return seed


class RouletteSelector:
    def __init__(self, items: Optional[Iterable] = None) -> None:
        self.roulette: OrderedDict = OrderedDict()

        if items:
            for item in items:
                self.add_item(item)

    def get_most_likely(self):
        if len(self.roulette) == 0 or self.total_chances == 0:
            return None
        else:
            return max(self.roulette.items(), key=lambda x: x[1])[0]

    def add_item(self, item, base_chance: float = 1.0):
        assert item not in self.roulette, (
            f"Item {item} is already in this roulette. To modify chances use the"
            " update_chance() or apply_modifier() methods"
        )
        self.roulette[item] = base_chance

    def set_chance(self, item, chance):
        assert item in self.roulette, (
            f"Item {item} is not in this roulette. To add a new item chances use the"
            " add_item() method"
        )
        self.roulette[item] = chance

    def apply_modifier(self, item, modifier: float, multiplicative: bool = False):
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

    @property
    def total_chances(self):
        return sum([c for _, c in self.roulette.items()])

    def get_items(self):
        return list(self.roulette.keys())

    def get_probabilities(self):
        return {
            item: chance / self.total_chances for item, chance in self.roulette.items()
        }

    def roll(self):
        self._remove_impossible_items()
        roll = random.random()

        lower_bound = 0.0
        for item, chance in self.roulette.items():
            upper_bound = lower_bound + chance / self.total_chances
            # NOTE Debug only
            print(
                lower_bound,
                "<=",
                roll,
                "<",
                upper_bound,
                ":",
                item,
                "✔️" if lower_bound <= roll < upper_bound else "",
            )
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


class Deck(RouletteSelector):
    def __init__(
        self, items: Iterable | None = None, n_cards: Iterable[int] | None = None
    ) -> None:
        super().__init__(items)

        if n_cards:
            assert len(items) == len(
                n_cards
            ), "If n_cards is provided, it must be the same len as items"
            for i, n in zip(items, n_cards):
                self.set_chance(i, n)

        self.initial_deck = self.roulette.copy()

    def draw(self, n_draws: int = 1, reshuffle: bool = False):
        assert n_draws >= 1, "n_draws must be >= 1"

        drawn_items = []
        for _ in range(n_draws):
            if len(self.roulette) == 0 or self.total_chances == 0 and reshuffle:
                # Restart the deck
                self.roulette = self.initial_deck.copy()

            drawn_item = self.roll()
            if drawn_item:
                self.apply_modifier(drawn_item, -1)

            drawn_items.append(drawn_item)

        return drawn_items
