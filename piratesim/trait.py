import random
from abc import ABC
from enum import Enum

from piratesim.quests.quest import Quest, QuestType


class BaseTrait(ABC):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        """Returns a dictionary with selection modifiers for a given quest list"""
        return {q: (0.0, False) for q in quests}

    def apply_to_quest_progress(self, pirate) -> int:
        """Override to apply a different progress amount depending on the quest"""
        return 0

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        """Returns success modifiers for a given quest"""
        return (0.0, False)

    def apply_to_minimum_bounty(self) -> int:
        return 0

    def __repr__(self) -> str:
        return self.__class__.__name__.upper().removesuffix("TRAIT")


class BoldTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {q: (2.0, False) for q in quests if q.difficulty >= 3}

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.difficulty >= 3:
            return 0.5, False
        else:
            return -0.5, False 


class CautiousTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {q: (2.0, False) for q in quests if q.difficulty <= 3}

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.difficulty <= 3:
            return 0.5, False  # Add 10% to success chance
        else:
            return -0.5, False  # Subtract 10% from success chance


class GreedyTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {q: (2.0, False) for q in quests if q.bounty >= 100}

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.reward >= 200:
            return 0.85, False
        else:
            return -0.5, False

    def apply_to_minimum_bounty(self) -> int:
        return 10  # needs 10% more bounty / reward than other pirates


class LoyalTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (2.0, False)
            for q in quests
            if q.qtype in {QuestType.rescue, QuestType.escort}
        }

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.rescue, QuestType.escort}:
            return 1.0, False
        else:
            return -0.5, False


class ImpulsiveTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {q: (random.uniform(-0.5, 1.0), False) for q in quests}

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        return random.uniform(-0.5, 0.5), False  # Random success chance


class StrategicTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (1.0, False)
            for q in quests
            if q.qtype in {QuestType.delivery, QuestType.exploration}
        }

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.delivery, QuestType.exploration}:
            return 0.5, False  # Add 10% to success chance
        return 0.0, False  # No change


class SuperstitiousTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {q: (0.5, True) for q in quests if q.is_cursed}  # Avoid cursed quests

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.is_cursed:
            return 0.5, True
        return 0.0, False


class BrutalTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {q: (1.5, True) for q in quests if q.qtype == QuestType.combat}

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.qtype == QuestType.combat:
            return 0.85, False
        return -0.3, False


class ResourcefulTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (1.0, False)
            for q in quests
            if q.qtype in {QuestType.exploration, QuestType.fetch}
        }

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.exploration, QuestType.fetch}:
            return 0.5, False
        return 0.0, False  # No change


class CowardlyTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (1.0, False) for q in quests if q.difficulty <= 2
        }  # Prefer low-risk quests

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.difficulty <= 2:
            return 0.5, False
        return -0.5, False


class TrickyTrait(BaseTrait):
    def apply_to_quest_selection(
        self, quests: list[Quest]
    ) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (3.0, False)
            for q in quests
            if q.qtype in {QuestType.smuggling, QuestType.theft}
        }

    def apply_to_quest_resolution(self, quest: Quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.smuggling, QuestType.theft}:
            return 1.0, False
        return 0.0, False  # No change


class TraitFactory(Enum):
    bold = BoldTrait
    cautious = CautiousTrait
    greedy = GreedyTrait
    loyal = LoyalTrait
    impulsive = ImpulsiveTrait
    strategic = StrategicTrait
    superstitious = SuperstitiousTrait
    brutal = BrutalTrait
    resourceful = ResourcefulTrait
    cowardly = CowardlyTrait
    tricky = TrickyTrait

    @staticmethod
    def get_trait(trait_name: str):
        try:
            return TraitFactory[trait_name].value()
        except KeyError:
            raise ValueError(f"Trait '{trait_name}' is not defined in TraitFactory.")
