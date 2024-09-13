import random

from piratesim.quests.quest import Quest, QuestType
from piratesim.quests import load_quest_bank
from piratesim.quests.quest_factory import QuestFactory
from piratesim.quests.effects import NewQuestEffect, RegionDiscoveredEffect, RetryQuestEffect
from piratesim.encounters.encounter_manager import EncounterManager
from piratesim.pirate import Pirate, load_pirate_bank
from piratesim.common.utils import clear_terminal
from piratesim.world_map import WorldMap

class SingleRun:
    def __init__(
        self,
        selected_pirates,
        n_quests,
        gold,
        unlocked_pirates,
        seed,
        random_encounter_chance,
        debug=False,
    ) -> None:
        self.n_quests = n_quests
        self.quest_bank = load_quest_bank()
        self.pirate_bank = load_pirate_bank()
        self.turn = 0
        self.turn_log = {}
        self._debug = debug
        self._seed = seed
        self.world_map = WorldMap()

        self.gold = gold

        self.notoriety = 0
        self.max_notoriety = 30

        self.available_quests: list[Quest] = []
        self.pinned_quests: list[Quest] = []
        self.pinned_quests_expiration: dict[Quest, int] = {}
        self.pirates: list[Pirate] = selected_pirates
        self.unlocked_pirates: list[Pirate] = unlocked_pirates

        self.encounter_manager = EncounterManager()
        self.random_encounter_chance = random_encounter_chance

    def print_state(self):
        print()
        print("-- 🗒️🖋️ PIRATE's LOG --")
        for pirate in self.pirates:
            print(f"{pirate.name}")
            [print(f"\t{line}") for line in pirate.captains_log[-3:]]
        print()

        if (self.turn - 1) in self.turn_log:
            print(f"-- ❕ TURN {self.turn - 1} EVENTS --")
            [print(line) for line in self.turn_log[self.turn - 1]]
            print()

        print("-- 🏠 Pirates at the Tavern --")
        for pirate in self.pirates:
            if not pirate.on_a_quest:
                print(pirate)
        print()

        print("-- 🧭 Pirates at Sea --")
        for pirate in self.pirates:
            if pirate.on_a_quest:
                print(pirate)
        print()

        print("-- 📌 Pinned quests --")
        if len(self.pinned_quests):
            for quest in self.pinned_quests:
                print(
                    f"> {quest} | Expires in"
                    f" {self.pinned_quests_expiration[quest]} turn(s)"
                )
        else:
            print("> EMPTY BOARD")
        print()

        print("-- Available quests --")
        for i, quest in enumerate(["Next turn"] + self.available_quests):
            print(f"{i}) {quest}")
        print()
        print(
            f"-- 🔄 TURN {self.turn} | 💰 GOLD {self.gold}  | 🌱 SEED {self._seed} --"
            "\n-- ⚠️  NOTORIETY"
            f" [{'/' * self.notoriety}{'_' * (self.max_notoriety - self.notoriety)}] --"  # noqa: E501
        )

    @property
    def quests_in_game(self):
        quests = []
        for pirate in self.pirates:
            if pirate.current_quest:
                quests.append(pirate.current_quest)

        quests.extend(self.available_quests)

        quests.extend(self.pinned_quests)

        return quests

    def randomize_quests(self, n_quests):
        quests = []
        for region in self.world_map.get_all_regions():
            if not region.discovered:
                quest_name = f'Explore the region {region.distance} leagues to the {region.direction}'
                if quest_name not in [q.name for q in self.quests_in_game]:
                    quest = QuestFactory().from_dict({
                        'name': quest_name,
                        'type': 'exploration',
                        'difficulty_min': 1,
                        'difficulty_max': 2,
                        'reward_min': 0,
                        'reward_max': 100,
                        'success_notoriety': 0,
                        'failure_notoriety': 0,
                        'expiration': 10,
                        'next_in_chain': -1,
                        'retry': 1,
                    }, parent_region=region)
                    
                    quests.append(quest)
        
        return quests

    def select_quests(self):
        while True:
            clear_terminal()
            self.print_state()

            if not self.available_quests:
                input('\n> No available quests, press enter to continue... <')
                return

            quest = self._handle_quest_selected()
            if quest:
                quest = self._handle_bounty(quest)

                self.pin_quest(quest)
            else:
                self.print_state()
                return

    def pin_quest(self, quest):
        self.available_quests.remove(quest)
        self.pinned_quests.append(quest)
        quest.on_pinned()
        # TODO Quests that don't expire or rethink this logic
        self.pinned_quests_expiration[quest] = (
            quest.expiration if quest.expiration else quest.difficulty
        )

    def _handle_quest_selected(self):
        ans = input("🗺️   Select a quest: ")
        try:
            ans = int(ans)
            assert ans >= 0 and ans <= len(self.available_quests)
        except:
            print("⚠️   Invalid option!")
            return self._handle_quest_selected()

        return self.available_quests[ans - 1] if ans > 0 else None

    def _handle_bounty(self, quest: Quest):
        ans = input("💰   What will be the pirate's cut? ")
        try:
            ans = int(ans)
            quest.bounty = ans
        except ValueError as e:
            print(f"⚠️   Invalid option! ({e})")
            return self._handle_bounty(quest)
        except AssertionError as e:
            print(f"⚠️   Invalid option! ({e})")
            return self._handle_bounty(quest)

        return quest

    def _check_game_over(self):
        if self.notoriety >= self.max_notoriety:
            return (
                True,
                "Your deeds travelled far and wide... Right in the Navy's ears!",
            )

        if self.gold < 0:
            return True, "Empty coffers!"

        if not self.pirates:
            return True, "Your crew is all gone!"

        return False, None

    def _update_pinned_quests(self):
        for quest in self.pinned_quests:
            turns_to_expire = self.pinned_quests_expiration[quest]
            if turns_to_expire > 1:
                self.pinned_quests_expiration[quest] = turns_to_expire - 1
            else:
                self.pinned_quests_expiration.pop(quest)
                self.pinned_quests.remove(quest)

    def next_turn(self):
        self.turn += 1

        self._update_pinned_quests()

        self.available_quests += self.randomize_quests(self.n_quests)
        self.select_quests()
        self.turn_log[self.turn] = []

        for pirate in self.pirates:
            if pirate.current_quest is None:
                selected_quest = pirate.select_quest(self.pinned_quests)
                pirate.assign_quest(selected_quest)

                for effect in selected_quest.all_effects:
                    effect.on_selected(pirate)

                if selected_quest.qtype is QuestType.idle:
                    self.turn_log[self.turn].append(
                        f"💤 {pirate.name} decided to {selected_quest.name} for"
                        f" {selected_quest.difficulty} turns"
                    )
                else:
                    self.pinned_quests.remove(selected_quest)
                    self.pinned_quests_expiration.pop(selected_quest)
                    self.turn_log[self.turn].append(
                        f"🚢 {pirate.name} embarked on a voyage!"
                        f" {selected_quest.name} [{selected_quest.qtype.name}]"
                    )
            else:
                quest_result = pirate.progress_quest()

                if quest_result is not None:
                    # Quest is complete
                    success, quest_effects = quest_result
                    self.turn_log[self.turn].append(
                        f'{"✅" if success else "❌"} '
                        f' {pirate.name} {"succeeded" if success else "failed"} the'
                        f" quest {pirate.current_quest.name}"
                    )

                    pirate.current_quest = None

                    for effect in quest_effects:
                        self.turn_log[self.turn].extend(
                            [f"\t{s}" for s in effect.resolve(self)]
                        )

                else:
                    # Quest is in progress
                    self.turn_log[self.turn].append(
                        f"🕓 {pirate.name} is working on {pirate.current_quest.name}"
                        f" [{pirate.current_quest.progress} turn(s) remaining]"
                    )

                    if random.random() < self.random_encounter_chance and pirate.current_quest.qtype != QuestType['idle']:
                        encounter = EncounterManager().create_encounter()
                        encounter_log = encounter.trigger(pirate)
                        self.turn_log[self.turn].extend(encounter_log)

        game_over = self._check_game_over()
        return game_over

    def run(self):
        while True:
            game_over, reason = self.next_turn()
            if game_over:
                clear_terminal()
                print("TURN LOG:\n\n")

                for key in self.turn_log:
                    print(f"-- TURN {key} --")
                    for line in self.turn_log[key]:
                        print(line)
                        print()

                print("\n\n     >------ GAME OVER ------<\n")
                print("\t", reason)
                input("\n\n> Press enter to continue...")
                return self
