from piratesim.common.random import Deck
from piratesim.quests.quest import Quest, QuestType
from piratesim.quests.quest_effect import QuestEffect
from piratesim.trait import TraitFactory


class RewardEffect(QuestEffect):
    def __init__(self, reward_value) -> None:
        self.reward_value = reward_value

    def resolve(self, game) -> list[str]:
        game.gold += self.reward_value

        quest_log = []
        if self.reward_value > 0:
            quest_log.append(
                f"🤑 {self.reward_value} gold pieces were added to the coffers!"
            )
        elif self.reward_value < 0:
            quest_log.append(f"💸 {self.reward_value} gold pieces were lost")

        return quest_log


class IncapacitateQuestTakerEffect(QuestEffect):
    def __init__(
        self, n_turns: int = 1, quest_name: str = "Fix the damage, heal the wounds"
    ) -> None:
        self.n_turns = n_turns
        self.quest_name = quest_name

    def resolve(self, game):
        from piratesim.quests.quest_factory import QuestFactory

        quest_log = []

        self.target_pirate.assign_quest(
            quest=QuestFactory().from_dict(
                {
                    "name": self.quest_name,
                    "type": "idle",
                    "difficulty_min": self.n_turns,
                    "difficulty_max": self.n_turns,
                    "reward_min": 0,
                    "reward_max": 0,
                }
            )
        )
        quest_log.append(
            f'{self.target_pirate.name} needs some time to "{self.quest_name}"'
            f" ({self.n_turns} turns)"
        )
        return quest_log

    def on_selected(self, quest_taker):
        self.target_pirate = quest_taker
        return None


class IncapacitateRandomPiratesEffect(QuestEffect):
    def __init__(
        self,
        exclude=[],
        n_pirates: int = 1,
        n_turns: int = 1,
        condition=None,
        quest_name: str = "Fix the damage, heal the wounds",
    ) -> None:
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
            pirate.assign_quest(
                quest=QuestFactory().from_dict(
                    {
                        "name": self.quest_name,
                        "type": "idle",
                        "difficulty_min": self.n_turns,
                        "difficulty_max": self.n_turns,
                        "reward_min": 0,
                        "reward_max": 0,
                    }
                )
            )
            quest_log.append(
                f'{pirate.name} will "{self.quest_name}" ({self.n_turns} turns)'
            )

        return quest_log


class NewQuestEffect(QuestEffect):
    def __init__(self, new_quests: list[Quest]) -> None:
        self.new_quests = new_quests
        super().__init__()

    def resolve(self, game):
        quest_log = []

        quests_to_add = []
        for q in self.new_quests:
            if q.name not in game.available_quests:
                quests_to_add.append(q)

        if quests_to_add:
            quest_log.append("❕ New quests unlocked:")
            for q in quests_to_add:
                game.available_quests.append(q)
                quest_log.append("\t" + q.name)

        return quest_log


class BountyEffect(QuestEffect):
    def __init__(self) -> None:
        self.bounty_value = None
        self.quest_taker = None

    def resolve(self, game) -> str:
        if self.bounty_value:
            self.quest_taker.gold += self.bounty_value
            game.gold -= self.bounty_value

            quest_log = [
                f"You paid them {self.bounty_value} gold pieces for their troubles"
            ]

            return quest_log
        return []

    def on_pinned(self, quest):
        self.bounty_value = quest.bounty

    def on_selected(self, pirate):
        self.quest_taker = pirate


class NotorietyEffect(QuestEffect):
    def __init__(self, notoriety_value) -> None:
        self.notoriety_value = notoriety_value

    def resolve(self, game) -> str:
        if self.notoriety_value:
            quest_log = []

            if self.quest_taker.trait == TraitFactory.get_trait("cautious"):
                self.notoriety_value = min(0, self.notoriety_value)

            game.notoriety += self.notoriety_value

            if self.notoriety_value > 0:
                quest_log.append(f"⚠️ 🔼  Notoriety increased by {self.notoriety_value}")
            elif self.notoriety_value < 0:
                quest_log.append(f"⚠️ 🔽  Notoriety decreased by {self.notoriety_value}")

            return quest_log
        return []

    def on_selected(self, pirate):
        self.quest_taker = pirate


class NewPirateEffect(QuestEffect):
    def __init__(self, pirate) -> None:
        self.pirate = pirate

    def resolve(self, game) -> str:
        game.pirates.append(self.pirate)

        quest_log = [f"{self.pirate.name} is ready for sailing!"]
        return quest_log


class NewRandomPirateEffect(QuestEffect):
    def resolve(self, game) -> str:
        import random

        unlocked_pirate_names = [p.name for p in game.unlocked_pirates]
        new_pirate = random.choice(
            [p for p in game.pirate_bank if p.name not in unlocked_pirate_names]
        )

        game.pirates.append(new_pirate)

        quest_log = [f"{new_pirate.name} is ready for sailing!"]
        return quest_log


class NewQuestRescueQuestTakerEffect(QuestEffect):
    def on_selected(self, pirate):
        self.quest_taker = pirate

    def resolve(self, game) -> str:
        from piratesim.quests.quest import Quest

        game.pirates.remove(self.quest_taker)
        rescue_quest = Quest(
            name=f"Rescue {self.quest_taker.name}",
            difficulty=1,
            expiration=10,
            qtype=QuestType["rescue"],
            success_effects=[NewPirateEffect(self.quest_taker)],
        )

        quest_log = [
            f"❕ {self.quest_taker.name} is stranded! New rescue quest available"
        ]
        game.available_quests.append(rescue_quest)

        return quest_log
