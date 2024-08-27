from abc import ABC, abstractmethod

from piratesim.quest import Quest


class BaseTrait(ABC):
    @abstractmethod
    def apply_to_quest_selection(self, quests) -> dict[Quest, float]:
        """Returns a dictionary with preferences for a given quest list"""
        pass

    def apply_to_quest_progress(self, quest) -> int:
        """Override to apply a different progress amount depending on the quest"""
        return 1

    def apply_to_quest_resolution(self, quest, base_chance) -> int:
        return base_chance
