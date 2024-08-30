import random

from piratesim.common.os import get_asset
from piratesim.common.random import RouletteSelector
from piratesim.quests import Quest, QuestType
from piratesim.trait import BaseTrait, TraitFactory


class Pirate:
    def __init__(self, name, description, trait, navigation, combat, trickyness):
        self.name: str = name
        self.description: str = description
        self.trait: BaseTrait = trait
        self.navigation: int = navigation
        self.combat: int = combat
        self.trickyness: int = trickyness
        self.gold: int = random.randint(5, 15) * 10
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
            quests.append(Quest.from_dict(row.to_dict()))
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
        )

    @property
    def bounty_ratio_threshold(self):
        thresh = 15
        return thresh + self.trait.apply_to_minimum_bounty_ratio()

    def get_random_idle_quest(self):
        self.idle_quest_bank = self.generate_idle_quests()
        return random.choice(self.idle_quest_bank)

    def select_quest(self, quests):
        """Selects a quest based on the pirate's traits."""
        if not quests:
            return self.get_random_idle_quest()

        roulette = RouletteSelector(quests)

        # There's always a chance the pirate will just idle
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
                roulette.update_chance(quest, 0.0)

        selected_quest = roulette.roll()

        if selected_quest.qtype == QuestType.idle:
            self.captains_log.append("There's nothing worth doing on the board")
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
            trait_effect = self.trait.apply_to_quest_progress(self.current_quest)
            self.current_quest.progress -= max(
                1, self.current_quest.progress - (trait_effect + base_progress)
            )

            return None  # Continue

        else:
            # Time to roll for success!
            if self.current_quest.qtype is QuestType.idle:
                return True

            roulette = RouletteSelector([True, False])
            modifier = self.trait.apply_to_quest_resolution(self.current_quest)
            roulette.apply_modifier(True, *modifier)

            # Modify based on stats (assuming the quest has a primary relevant stat)
            relevant_stat = {
                QuestType.treasure: self.trickyness,
                QuestType.combat: self.combat,
                QuestType.delivery: self.navigation,
                QuestType.rescue: self.trickyness,
                QuestType.smuggling: self.trickyness,
                QuestType.fetch: self.navigation,
                QuestType.exploration: self.navigation,
                QuestType.escort: self.combat,
                QuestType.survival: max(self.navigation, self.combat),
                QuestType.theft: self.trickyness,
            }.get(self.current_quest.qtype, 0)

            # Each stat point gives a compouding 0.1 bonus to odds
            diff = max(0, relevant_stat - self.current_quest.difficulty)
            roulette.apply_modifier(True, diff * 0.1, False)
            p = roulette.get_probabilities()[True]
            self.captains_log.append(
                f"Rolled quest success with probability {round(p * 100, 1)}% (odds ="
                f" {p / (1 - p)})."
            )

            return roulette.roll()

    def __repr__(self):
        template = "| N {n} - C {c} - T {t} | {name}, a {trait} {flavor}\n|\t{desc}"
        return template.format(
            n=self.navigation,
            c=self.combat,
            t=self.trickyness,
            name=self.name,
            trait=self.trait,
            flavor=self.flavor,
            desc=self.description,
        )
