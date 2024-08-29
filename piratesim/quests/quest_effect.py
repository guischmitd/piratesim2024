from abc import ABC, abstractmethod


class QuestEffect(ABC):
    @abstractmethod
    def resolve(self, game):
        pass


class RewardEffect(QuestEffect):
    def __init__(self, reward_value) -> None:
        self.reward_value = reward_value

    def resolve(self, game):
        game.gold += self.reward_value


class IncapacitatePirateEffect(QuestEffect):
    def __init__(self, reward_value) -> None:
        self.reward_value = reward_value

    def resolve(self, game):
        potential_targets = []
        for pirate in game.pirates:
            if pirate.current_quest is None:
                potential_targets.append(pirate)
