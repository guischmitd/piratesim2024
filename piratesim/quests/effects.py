
from piratesim.quests.quest import Quest
from piratesim.quests.quest_effect import QuestEffect

from piratesim.common.random import Deck


class RewardEffect(QuestEffect):
    def __init__(self, reward_value) -> None:
        self.reward_value = reward_value

    def resolve(self, game) -> list[str]:
        game.gold += self.reward_value
        
        quest_log = []
        if self.reward_value > 0:
            quest_log.append(f'🤑 {self.reward_value} gold pieces were added to the coffers!')
        elif self.reward_value < 0:
            quest_log.append(f'💸 {self.reward_value} gold pieces were lost')

        return quest_log


class IncapacitateQuestTakerEffect(QuestEffect):
    def __init__(self,
                 n_turns: int = 1,
                 quest_name: str = 'Fix the damage, heal the wounds') -> None:
        
        self.n_turns = n_turns
        self.quest_name = quest_name

    def resolve(self, game):
        from piratesim.quests.quest_factory import QuestFactory
        
        quest_log = []

        self.target_pirate.assign_quest(quest=QuestFactory.from_dict({
                "name": self.quest_name,
                "type": "idle",
                "difficulty_min": self.n_turns,
                "difficulty_max": self.n_turns,
                "reward_min": 0,
                "reward_max": 0,
                })
            )
        quest_log.append(f'{self.target_pirate.name} needs some time to "{self.quest_name}" ({self.n_turns} turns)')
        return quest_log

    def on_selected(self, quest_taker):
        self.target_pirate = quest_taker
        return None


class IncapacitateRandomPiratesEffect(QuestEffect):
    def __init__(self, 
                 exclude = [],
                 n_pirates: int = 1,
                 n_turns: int = 1,
                 condition = None,
                 quest_name: str = 'Fix the damage, heal the wounds') -> None:
        
        self.exclude = exclude
        self.condition = condition if condition else lambda _: True
        self.n_pirates = n_pirates
        self.n_turns = n_turns
        self.quest_name = quest_name

    def resolve(self, game):
        from piratesim.quests.quest_factory import QuestFactory

        deck = Deck()
        for pirate in game.pirates:
            if self.condition(pirate) and pirate not in self.exclude:
                deck.add_item(pirate)
        
        self.target_pirates = deck.draw(self.n_pirates)
        
        quest_log = []

        for pirate in self.target_pirates:
            pirate.assign_quest(quest=QuestFactory.from_dict({
                    "name": self.quest_name,
                    "type": "idle",
                    "difficulty_min": self.n_turns,
                    "difficulty_max": self.n_turns,
                    "reward_min": 0,
                    "reward_max": 0,
                    })
                )
            quest_log.append(f'{pirate.name} will "{self.quest_name}" ({self.n_turns} turns)')
        
        return quest_log


class NewQuestEffect(QuestEffect):
    def __init__(self, new_quests: list[Quest]) -> None:
        self.new_quests = new_quests
        super().__init__()

    def resolve(self, game):
        game.available_quests.extend(self.new_quests)
        
        quest_log = ['❕ New quests unlocked:']
        for q in self.new_quests:
            quest_log.append('\t' + q.name)

        return quest_log
