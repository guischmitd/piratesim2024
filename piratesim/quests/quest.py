from enum import Enum, auto
from typing import Optional

from piratesim.quests.quest_effect import QuestEffect


class QuestType(Enum):
    treasure = auto()
    combat = auto()
    delivery = auto()
    rescue = auto()
    smuggling = auto()
    fetch = auto()
    exploration = auto()
    escort = auto()
    theft = auto()
    idle = auto()


class Quest:
    def __init__(
        self,
        name: str,
        qtype: QuestType,
        difficulty: int,
        success_effects: list[QuestEffect] = [],
        failure_effects: list[QuestEffect] = [],
        reward: int = 0,
        notoriety: int = 1,
        expiration: Optional[int] = None,
    ) -> None:
        self.name = name
        self.qtype = qtype
        self.difficulty = difficulty
        self.reward = reward
        self._bounty = 0
        self.progress = self.difficulty  # TODO Improve this
        self.success_effects = success_effects
        self.failure_effects = failure_effects
        self.notoriety = notoriety
        self.expiration = expiration

    @property
    def is_cursed(self) -> bool:
        cursed_words = [
            "magic",
            "curse",
            "kraken",
            "monster",
            "ghost",
            "haunted",
            "mermaid",
        ]
        return any([w in self.name.lower() for w in cursed_words])

    @property
    def bounty(self) -> int:
        return self._bounty

    @property
    def all_effects(self) -> list[QuestEffect]:
        return self.success_effects + self.failure_effects

    @property
    def bounty_ratio(self) -> int:
        return int(100 * self.bounty / self.reward) if self.reward else 0

    @bounty.setter
    def bounty(self, value):
        if value is not None:
            assert isinstance(value, int), "bounty must be an integer!"
            assert int(value) >= 0
            self._bounty = int(value)

    def __repr__(self) -> str:
        return (
            f"D {self.difficulty} - R {self.reward}\t[{self.qtype.name}]\t| {self.name}"
        )

    def on_selected(self, *args):
        for effect in self.all_effects:
            effect.on_selected(*args)

    def on_pinned(self):
        for effect in self.all_effects:
            effect.on_pinned(self)
