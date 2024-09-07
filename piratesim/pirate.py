import random

from piratesim.common.assets import get_asset
from piratesim.common.random import RouletteSelector
from piratesim.quests.quest import QuestType
from piratesim.quests.quest_factory import QuestFactory
from piratesim.trait import BaseTrait, TraitFactory


class Pirate:
    def __init__(self, name, description, trait, navigation, combat, trickyness, level):
        self.name: str = name
        self.description: str = description
        self.trait: BaseTrait = trait
        self.navigation: int = navigation
        self.combat: int = combat
        self.trickyness: int = trickyness
        self.gold: int = random.randint(5, 15) * 10
        self.level: int = level
        self.flavor: str = random.choice(
            [
                "buccaneer",
                "scallywag",
                "do-no-good",
                "sailor",
                "pirate",
                "knife-juggler",
            ]
        )

        potential_openers = [
            "arrived at the tavern like they knew everyone.",
            "was found sleeping among the crabs.",
            "used to sail with a famous captain before a bit of drama.",
            "figured this island would be a good place to find work.",
            "had a terrible accident with a fish and a potato once.",
        ]
        self.captains_log = [f"{self.name} {random.choice(potential_openers)}"]

        self.current_quest = None

        self.idle_quest_bank = self.generate_idle_quests()

    def generate_idle_quests(self):
        quests = []
        for _, row in get_asset("quests/idle_quests.csv").iterrows():
            quests.append(QuestFactory().from_dict(row.to_dict()))
        return quests

    @classmethod
    def from_dict(cls, pirate_dict):
        return cls(
            name=pirate_dict["name"],
            description=pirate_dict["description"],
            trait=TraitFactory.get_trait(pirate_dict["trait"].lower()),
            navigation=pirate_dict["navigation"],
            combat=pirate_dict["combat"],
            trickyness=pirate_dict["trickyness"],
            level=pirate_dict["level"],
        )

    @property
    def bounty_ratio_threshold(self):
        thresh = 15
        return thresh + self.trait.apply_to_minimum_bounty_ratio()

    def get_random_idle_quest(self):
        self.idle_quest_bank = self.generate_idle_quests()
        return random.choice(self.idle_quest_bank)

    def assign_quest(self, quest):
        if self.current_quest:
            self.captains_log.append(
                f'"{self.current_quest.name}" was interrupted, I will now have to go'
                f' "{quest.name}"'
            )
        self.current_quest = quest

    def select_quest(self, quests, allow_idle=True):
        """Selects a quest based on the pirate's traits."""
        if not quests:
            return self.get_random_idle_quest()

        roulette = RouletteSelector(quests)

        if allow_idle:
            # There's a chance the pirate will just idle
            roulette.add_item(self.get_random_idle_quest(), 0.5)

        modifier_dict = self.trait.apply_to_quest_selection(roulette.get_items())
        for quest, modifier in modifier_dict.items():
            roulette.apply_modifier(quest, *modifier)

        # Bounty influence on quest selection (TODO Extract to trait class)
        for quest in quests:
            if quest.bounty_ratio > self.bounty_ratio_threshold:
                # Bounty threshold increases quests odds
                roulette.apply_modifier(quest, quest.bounty / 100, multiplicative=False)
            else:
                self.captains_log.append(
                    f'{self.name} thinks "{quest.name}" is not worth it for this'
                    " bounty."
                )
                roulette.set_chance(quest, 0.0)

        selected_quest = roulette.roll()

        if selected_quest.qtype == QuestType.idle:
            self.captains_log.append(
                f'Took some time for myself to go "{selected_quest.name}"'
            )
        elif selected_quest is roulette.get_most_likely():
            self.captains_log.append(
                f'My crew will love to go "{selected_quest.name}"!'
            )
        else:
            self.captains_log.append(
                "I'd normally prefer other stuff, but let's try to go"
                f' "{selected_quest.name}"'
            )

        return selected_quest

    @property
    def on_a_quest(self):
        if self.current_quest:
            return self.current_quest.qtype is not QuestType.idle
        else:
            return False

    def progress_quest(self):
        """
        Progress a quest for one turn, and roll for success if it's voyage
        length has been concluded.
        Returns:
         - None if the quest is still in progress.
         - A boolean indicating quest success if concluded.
        """
        if self.current_quest.progress > 1:
            base_progress = 1 if self.navigation <= 3 else 2
            trait_effect = self.trait.apply_to_quest_progress(self)
            self.current_quest.progress = max(
                1, self.current_quest.progress - (trait_effect + base_progress)
            )

            return None  # Continue

        else:
            # Time to roll for success!
            if self.current_quest.qtype is QuestType.idle:
                return True, self.current_quest.success_effects

            roulette = RouletteSelector([True, False])
            roulette.set_chance(True, 2.0)  # Base success chance is 66%

            modifier = self.trait.apply_to_quest_resolution(self.current_quest)
            roulette.apply_modifier(True, *modifier)

            # Modify based on stats (assuming the quest has a primary relevant stat)
            relevant_stat = {
                QuestType.rescue: self.trickyness,
                QuestType.treasure: self.trickyness,
                QuestType.smuggling: self.trickyness,
                QuestType.theft: self.trickyness,
                QuestType.exploration: self.navigation,
                QuestType.delivery: self.navigation,
                QuestType.fetch: self.navigation,
                QuestType.combat: self.combat,
                QuestType.escort: self.combat,
            }.get(self.current_quest.qtype, 0)

            # Each stat point above quest difficulty gives a
            # compouding 10% bonus to odds
            diff = max(0, relevant_stat - self.current_quest.difficulty)
            roulette.apply_modifier(True, 1 + (diff * 0.10), True)

            # NOTE DEBUG ONLY
            p = roulette.get_probabilities()[True]
            success = roulette.roll()
            self.captains_log.append(
                f'{"Succeeded" if success else "Failed"} the quest'
                f' "{self.current_quest.name}" with probability {round(p * 100, 1)}%'
                f" (odds = {round(p / (1 - p), 3)}:1)"
            )

            return (
                success,
                self.current_quest.success_effects
                if success
                else self.current_quest.failure_effects,
            )

    def __repr__(self):
        template = "| N {n} - C {c} - T {t} | {name}, a {trait} {flavor}"
        return template.format(
            n=self.navigation,
            c=self.combat,
            t=self.trickyness,
            name=self.name,
            trait=self.trait,
            flavor=self.flavor,
        )
