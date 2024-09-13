import random

from piratesim.common.assets import get_asset
from piratesim.quests.effects import (
    BountyEffect,
    IncapacitateQuestTakerEffect,
    IncapacitateRandomPiratesEffect,
    NewQuestEffect,
    NotorietyEffect,
    RewardEffect,
    NewQuestRescueQuestTakerEffect,
    NewRandomPirateEffect,
    RetryQuestEffect,
    RegionDiscoveredEffect,
)
from piratesim.quests.quest import Quest, QuestType


class QuestFactory:
    def __init__(self) -> None:
        self.quest_bank = get_asset("quests/quests.csv").set_index("quest_id")

    def build_quest(self,
        name,
        qtype,
        expiration,
        distance,
        difficulty=3,
        reward=0,
        success_effects=[],
        failure_effects=[],
    ):
        return Quest(
            name=name,
            distance=distance,
            qtype=qtype,
            difficulty=difficulty,
            expiration=expiration,
            reward=reward,
            success_effects=success_effects,
            failure_effects=failure_effects,
        )

    def from_dict(self, template_dict, parent_region=None):
        difficulty = random.randint(
            template_dict["difficulty_min"], template_dict["difficulty_max"]
        )
        min_reward = template_dict["reward_min"] // 10
        max_reward = template_dict["reward_max"] // 10


        reward = random.randint(min_reward, max_reward) * 10
        reward_effect = RewardEffect(reward)

        success_effects = []
        failure_effects = []

        # Handle region discovery
        if parent_region:
            if not parent_region.discovered:
                success_effects.append(RegionDiscoveredEffect(region=parent_region))
                if parent_region.available_quest:
                    success_effects.append(
                        NewQuestEffect(new_quests=[parent_region.available_quest])
                    )

        # Handle reward
        if reward > 0 or QuestType[template_dict["type"]] == QuestType.idle:
            success_effects.append(reward_effect)
        elif reward < 0:
            failure_effects.append(reward_effect)

        # Handle retry
        if template_dict.get('retry', 1):
            failure_effects.append(RetryQuestEffect())

        # Handle chains
        if template_dict.get("next_in_chain", -1) >= 0:
            success_effects.append(
                NewQuestEffect(
                    [
                        self.from_dict(
                            self.quest_bank.loc[
                                template_dict["next_in_chain"]
                            ].to_dict()
                        )
                    ]
                )
            )

        # Handle unlockable pirates
        if template_dict['name'] == 'Rescue the Stranded Pirate':
            success_effects.append(NewRandomPirateEffect())

        # Handle bounty and notoriety
        if QuestType[template_dict["type"]] != QuestType.idle:
            success_effects.append(NotorietyEffect(template_dict["success_notoriety"]))
            failure_effects.append(NotorietyEffect(template_dict["failure_notoriety"]))

            bounty_effect = BountyEffect()
            success_effects.append(bounty_effect)
            failure_effects.append(bounty_effect)

        # Handle combat failure states
        if QuestType[template_dict["type"]] == QuestType.combat:
            if difficulty >= 4:
                failure_effects.append(
                    NewQuestRescueQuestTakerEffect()
                )
            else:
                failure_effects.append(
                    IncapacitateQuestTakerEffect(
                        n_turns=random.randint(1, 3), quest_name="Fix the holes in the hull"
                    )
                )

        # Handle other incapacitated states
        elif QuestType[template_dict["type"]] == QuestType.theft:
            failure_effects.append(
                IncapacitateQuestTakerEffect(
                    n_turns=random.randint(1, 3), quest_name="Be locked up for a while"
                )
            )
        elif (
            QuestType[template_dict["type"]] == QuestType.idle
            and "drink" in template_dict["name"].lower()
        ):
            success_effects.append(
                IncapacitateQuestTakerEffect(
                    n_turns=random.randint(1, 3), quest_name="Get over the hangover"
                )
            )
        elif (
            QuestType[template_dict["type"]] == QuestType.idle
            and "fight" in template_dict["name"].lower()
        ):
            success_effects.append(
                IncapacitateRandomPiratesEffect(
                    n_pirates=random.randint(1, 2),
                    n_turns=random.randint(1, 3),
                    quest_name="Heal the wounds",
                    condition=lambda p: not p.on_a_quest,
                )
            )

        return self.build_quest(
            name=template_dict["name"],
            qtype=QuestType[template_dict["type"]],
            difficulty=difficulty,
            distance=parent_region.distance if parent_region else 3,
            expiration=template_dict.get('expiration', 10),
            reward=reward,
            success_effects=success_effects,
            failure_effects=failure_effects,
        )
