import random
from abc import ABC
from enum import Enum

from piratesim.quest import Quest, QuestType


class BaseTrait(ABC):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        """Returns a dictionary with selection modifiers for a given quest list"""
        return {q: (0.0, False) for q in quests}

    def apply_to_quest_progress(self, quest) -> int:
        """Override to apply a different progress amount depending on the quest"""
        return 1

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        """Returns success modifiers for a given quest"""
        return (0.0, False)


class BoldTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {q: (2.0, False) for q in quests if q.difficulty_min >= 3}

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.difficulty >= 3:
            return 10.0, False  # Add 10% to success chance
        else:
            return -10.0, False  # Subtract 10% from success chance


class CautiousTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {q: (2.0, False) for q in quests if q.difficulty_max <= 3}

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.difficulty <= 3:
            return 10.0, False  # Add 10% to success chance
        else:
            return -10.0, False  # Subtract 10% from success chance


class GreedyTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {q: (2.0, False) for q in quests if q.bounty >= 100}

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.reward >= 200:
            return 5.0, False  # Add 5% to success chance
        else:
            return -5.0, False  # Subtract 5% from success chance


class LoyalTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (2.0, False)
            for q in quests
            if q.qtype in {QuestType.rescue, QuestType.escort}
        }

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.rescue, QuestType.escort}:
            return 15.0, False  # Add 15% to success chance
        else:
            return -5.0, False  # Subtract 5% from success chance


class ImpulsiveTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {q: (random.uniform(0.5, 2.0), False) for q in quests}

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        return random.uniform(-50.0, 50.0), False  # Random success chance


class StrategicTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (3.0, False)
            for q in quests
            if q.qtype in {QuestType.delivery, QuestType.exploration}
        }

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.delivery, QuestType.exploration}:
            return 10.0, False  # Add 10% to success chance
        return 0.0, False  # No change


class SuperstitiousTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (0.0, False) for q in quests if "cursed" in q.name.lower()
        }  # Avoid cursed quests

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if "cursed" in quest.name.lower():
            return -10.0, False  # Subtract 10% from success chance
        return -5.0, False  # Subtract 5% from success chance


class BrutalTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {q: (2.0, False) for q in quests if q.qtype == QuestType.combat}

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.qtype == QuestType.combat:
            return 20.0, False  # Add 20% to success chance
        return -10.0, False  # Subtract 10% from success chance


class ResourcefulTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (3.0, False)
            for q in quests
            if q.qtype in {QuestType.exploration, QuestType.fetch}
        }

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.exploration, QuestType.fetch}:
            return 10.0, False  # Add 10% to success chance
        return 0.0, False  # No change


class CowardlyTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (3.0, False) for q in quests if q.difficulty_max <= 2
        }  # Prefer low-risk quests

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.difficulty <= 2:
            return 20.0, False  # Add 20% to success chance
        return -15.0, False  # Subtract 15% from success chance


class TrickyTrait(BaseTrait):
    def apply_to_quest_selection(self, quests) -> dict[Quest, tuple[float, bool]]:
        return {
            q: (3.0, False)
            for q in quests
            if q.qtype in {QuestType.smuggling, QuestType.theft}
        }

    def apply_to_quest_resolution(self, quest) -> tuple[float, bool]:
        if quest.qtype in {QuestType.smuggling, QuestType.theft}:
            return 15.0, False  # Add 15% to success chance
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
