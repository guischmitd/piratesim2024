import random

from piratesim.common.os import clear_terminal, get_asset
from piratesim.common.random import get_seed
from piratesim.pirate import Pirate
from piratesim.quests.quest import Quest, QuestType
from piratesim.quests.quest_factory import QuestFactory

class Game:
    def __init__(self, n_quests=3, n_pirates=5, gold=1000, seed=None, debug=True) -> None:
        self.n_quests = n_quests
        self.quest_bank = self._load_quest_bank()
        self.pirate_bank = self._init_pirates()
        self.turn = 0
        self.turn_log = {}
        self._debug = debug
        self._seed = seed if seed else get_seed()
        random.seed(self._seed)

        self.gold = gold

        self.available_quests: list[Quest] = self.randomize_quests(n_quests)
        self.pinned_quests: list[Quest] = []
        self.pinned_quests_expiration: dict[Quest, int] = {}
        self.pirates: list[Pirate] = random.sample(self.pirate_bank, n_pirates)
    
    @staticmethod
    def _load_quest_bank():
        return get_asset("quests/quests.csv")

    @staticmethod
    def _init_pirates():
        pirates = []
        for _, row in get_asset("pirates/pirates.csv").iterrows():
            pirates.append(Pirate.from_dict(row.to_dict()))
        return pirates

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
            f"-- 🔄 TURN {self.turn} | 💰 GOLD {self.gold} | 🌱 SEED {self._seed:06d} --"
        )

    def randomize_quests(self, n_quests):
        quests = []
        for _, row in get_asset("quests/quests.csv").iterrows():
            quests.append(QuestFactory.from_dict(row.to_dict()))
    
        return random.sample(quests, k=n_quests)

    def select_quests(self):
        while True:
            clear_terminal()
            self.print_state()

            if not self.available_quests:
                return

            quest = self._handle_quest_selected()
            if quest:
                quest = self._handle_bounty(quest)

                self.available_quests.remove(quest)
                self.pinned_quests.append(quest)
                self.pinned_quests_expiration[quest] = quest.difficulty
            else:
                self.print_state()
                return

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

    def next_turn(self):
        self.turn += 1

        for quest in self.pinned_quests:
            turns_to_expire = self.pinned_quests_expiration[quest]
            if turns_to_expire > 1:
                self.pinned_quests_expiration[quest] = turns_to_expire - 1
            else:
                self.pinned_quests_expiration.pop(quest)
                self.pinned_quests.remove(quest)

        self.available_quests = self.randomize_quests(self.n_quests)
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
                quest_effects = pirate.progress_quest()

                if quest_effects is not None:
                    self.turn_log[self.turn].append(
                        f'✅ {pirate.name} completed the quest {pirate.current_quest.name}'
                    )

                    # TODO bounty effect
                    self.gold -= pirate.current_quest.bounty
                    pirate.gold += pirate.current_quest.bounty

                    if pirate.current_quest.bounty != 0:
                        self.turn_log[self.turn].append(
                            f'\tYou paid {pirate.current_quest.bounty} for their troubles'
                        )

                    pirate.current_quest = None
                    
                    for effect in quest_effects:
                        self.turn_log[self.turn].extend([f'\t{s}' for s in effect.resolve(self)])

                else:
                    self.turn_log[self.turn].append(
                        f"🕓 {pirate.name} is working on a quest"
                        f" [{pirate.current_quest.progress} turn(s) remaining]"
                    )

    def run(self):
        while True:
            self.next_turn()
