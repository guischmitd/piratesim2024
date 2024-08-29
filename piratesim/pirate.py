import random
from enum import Enum, auto

from piratesim.common.os import get_asset
from piratesim.common.random import RouletteSelector
from piratesim.quest import Quest, QuestType
from piratesim.trait import TraitFactory


class Trait(Enum):
    BOLD = auto()
    CAUTIOUS = auto()
    GREEDY = auto()
    LOYAL = auto()
    IMPULSIVE = auto()
    STRATEGIC = auto()
    SUPERSTITIOUS = auto()
    BRUTAL = auto()
    RESOURCEFUL = auto()
    COWARDLY = auto()
    TRICKY = auto()


class Pirate:
    def __init__(self, name, description, trait, navigation, combat, trickyness):
        self.name = name
        self.description = description
        self.trait = trait
        self.navigation = navigation
        self.combat = combat
        self.trickyness = trickyness
        self.gold = random.randint(5, 15) * 10
        self.flavor = random.choice(
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
            trait=TraitFactory.get_trait(pirate_dict["trait"]),
            navigation=pirate_dict["navigation"],
            combat=pirate_dict["combat"],
            trickyness=pirate_dict["trickyness"],
        )

    @property
    def bounty_ratio_threshold(self):
        thresh = 20  # Pirates expect at least a 20% cut
        return thresh + 10 if self.trait == Trait.GREEDY else thresh

    def select_idle_quest(self):
        self.idle_quest_bank = self.generate_idle_quests()
        return random.choice(self.idle_quest_bank)

    def select_quest(self, quests):
        """Selects a quest based on the pirate's traits."""
        if not quests:
            return self.select_idle_quest()

        quest_roulette = RouletteSelector()

        preferred_quests = []

        # Pirates require a minimum cut of the bounty
        for quest in quests:
            if quest.bounty_ratio > self.bounty_ratio_threshold:
                quest_roulette.append(quest)
            else:
                self.captains_log.append(
                    f'{self.name} thinks "{quest.name}" is not worth it for this'
                    " bounty."
                )

        # TODO TraitEffect abstract class
        if self.trait == Trait.BOLD:
            # Prefer higher difficulty quests
            preferred_quests = [q for q in set(quest_roulette) if q.difficulty_min >= 3]
            quest_roulette.extend(preferred_quests)
        elif self.trait == Trait.CAUTIOUS:
            # Prefer lower difficulty quests
            preferred_quests = [q for q in set(quest_roulette) if q.difficulty_max <= 3]
            quest_roulette.extend(preferred_quests)
        elif self.trait == Trait.GREEDY:
            # Prefer higher reward quests
            preferred_quests = [q for q in set(quest_roulette) if q.bounty >= 100]
            quest_roulette.extend(preferred_quests)
        elif self.trait == Trait.LOYAL:
            # Prefer rescue or escort missions
            preferred_quests = [
                q
                for q in set(quest_roulette)
                if q.qtype in {QuestType.rescue, QuestType.escort}
            ]
            quest_roulette.extend(preferred_quests)
        elif self.trait == Trait.IMPULSIVE:
            # Randomly select a quest
            selected_quest = random.choice(quests + [self.select_idle_quest()])
            self.captains_log.append(
                f"{self.name} thinks life's too short to spend it thinking! Let's go"
                f" '{selected_quest.name}'"
            )
            return selected_quest
        elif self.trait == Trait.STRATEGIC:
            # Prefer quests with clear objectives
            preferred_quests = [
                q
                for q in set(quest_roulette)
                if q.qtype in {QuestType.delivery, QuestType.exploration}
            ]
            quest_roulette.extend(preferred_quests * 2)  # 3 times as likely
        elif self.trait == Trait.SUPERSTITIOUS:
            # Avoid supernatural quests
            preferred_quests = [
                q for q in set(quest_roulette) if "cursed" not in q.name.lower()
            ]
            quest_roulette.extend(preferred_quests)
        elif self.trait == Trait.BRUTAL:
            # Prefer combat-heavy quests
            preferred_quests = [
                q for q in set(quest_roulette) if q.qtype == QuestType.combat
            ]
            quest_roulette.extend(preferred_quests * 2)  # 3 times as likely
        elif self.trait == Trait.RESOURCEFUL:
            # Prefer exploration or recovery quests
            preferred_quests = [
                q
                for q in set(quest_roulette)
                if q.qtype in {QuestType.exploration, QuestType.fetch}
            ]
            quest_roulette.extend(preferred_quests * 2)  # 3 times as likely
        elif self.trait == Trait.COWARDLY:
            # Prefer low-risk quests
            preferred_quests = [q for q in set(quest_roulette) if q.difficulty_max <= 2]
            quest_roulette.extend(preferred_quests * 2)
        elif self.trait == Trait.TRICKY:
            # Prefer quests with a lot of potential tricks and twists
            preferred_quests = [
                q
                for q in set(quest_roulette)
                if q.qtype in {QuestType.smuggling, QuestType.theft}
            ]
            quest_roulette.extend(preferred_quests * 2)  # 3 times as likely

        # If no preferred quests are found, select randomly
        selected_quest = (
            random.choice(quest_roulette)
            if quest_roulette
            else self.select_idle_quest()
        )

        if selected_quest.qtype == QuestType.idle:
            self.captains_log.append(
                f"{self.name} feels there's nothing worth pursuing in the board."
            )
        elif selected_quest in preferred_quests:
            self.captains_log.append(
                f'{self.name} will love to go "{selected_quest.name}"!'
            )
        elif selected_quest not in preferred_quests:
            self.captains_log.append(
                f"{self.name} would like to try something different and go"
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
            if self.navigation > 3:
                self.current_quest.progress = max(1, self.current_quest.progress - 2)
            else:
                self.current_quest.progress -= 1
            return None  # Continue

        else:
            # Time to roll for success!
            if self.current_quest.qtype is QuestType.idle:
                return True

            base_chance = 50  # Base success chance in percent

            # Modify chance based on traits
            if self.trait == Trait.BOLD:
                base_chance += 10 if self.current_quest.difficulty >= 3 else -10
            elif self.trait == Trait.CAUTIOUS:
                base_chance += 10 if self.current_quest.difficulty <= 3 else -10
            elif self.trait == Trait.GREEDY:
                base_chance += 5 if self.current_quest.reward >= 200 else -5
            elif self.trait == Trait.LOYAL:
                base_chance += (
                    15
                    if self.current_quest.qtype in {QuestType.rescue, QuestType.escort}
                    else -5
                )
            elif self.trait == Trait.IMPULSIVE:
                base_chance = random.randint(0, 100)
            elif self.trait == Trait.STRATEGIC:
                base_chance += (
                    10
                    if self.current_quest.qtype
                    in {QuestType.delivery, QuestType.exploration}
                    else 0
                )
            elif self.trait == Trait.SUPERSTITIOUS:
                base_chance -= 10 if "cursed" in self.current_quest.name.lower() else 5
            elif self.trait == Trait.BRUTAL:
                base_chance += (
                    20 if self.current_quest.qtype == QuestType.combat else -10
                )
            elif self.trait == Trait.RESOURCEFUL:
                base_chance += (
                    10
                    if self.current_quest.qtype
                    in {QuestType.exploration, QuestType.fetch}
                    else 0
                )
            elif self.trait == Trait.COWARDLY:
                base_chance += 20 if self.current_quest.difficulty <= 2 else -15
            elif self.trait == Trait.TRICKY:
                base_chance += (
                    15
                    if self.current_quest.qtype
                    in {QuestType.smuggling, QuestType.theft}
                    else 0
                )

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
            }.get(self.current_quest.qtype, 3)

            base_chance += relevant_stat * 5  # Each stat point gives a 5% bonus

            # Roll to determine success
            roll = random.randint(0, 100)
            return roll < base_chance

    def __repr__(self):
        template = "| N {n} - C {c} - T {t} | {name}, a {trait} {flavor}\n\t{desc}"
        return template.format(
            n=self.navigation,
            c=self.combat,
            t=self.trickyness,
            name=self.name,
            trait=self.trait.upper(),
            flavor=self.flavor,
            desc=self.description,
        )


if __name__ == "__main__":
    # Example quests list
    quests = [
        Quest.from_dict(
            {
                "name": "Plunder the Ghost Ship",
                "type": QuestType.treasure,
                "difficulty_min": 3,
                "difficulty_max": 5,
                "reward_min": 100,
                "reward_max": 300,
            }
        ),
        Quest.from_dict(
            {
                "name": "Hunt the Giant Squid",
                "type": QuestType.combat,
                "difficulty_min": 4,
                "difficulty_max": 5,
                "reward_min": 200,
                "reward_max": 400,
            }
        ),
        # Add more quests here
    ]

    # Example usage
    pirate = Pirate("Cpt Shaliber", Trait.TRICKY, 3, 2, 5)
    selected_quest = pirate.select_quest(quests)
    print(f"{pirate.name} selected the quest: {selected_quest['name']}")

    success = pirate.attempt_quest(selected_quest)
    print(f"Quest success: {'Yes' if success else 'No'}")
