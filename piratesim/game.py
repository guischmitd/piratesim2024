import numpy as np

from piratesim.common import get_asset
from piratesim.pirate import Pirate
from piratesim.quest import Quest, QuestType


class Game:
    def __init__(self, n_quests=3, n_pirates=5, level=1) -> None:
        self.n_quests = n_quests
        self.quest_bank = self._init_quests()
        self.pirate_bank = self._init_pirates()
        self.turn = 0

        self.gold = 1000

        self.available_quests: list[Quest] = self.randomize_quests(n_quests)
        self.pinned_quests: list[Quest] = []
        self.pirates: list[Pirate] = np.random.choice(
            self.pirate_bank, n_pirates, replace=False
        )

    @staticmethod
    def _init_quests():
        quests = []
        for _, row in get_asset("quests/quests.csv").iterrows():
            quests.append(Quest.from_dict(row.to_dict()))
        return quests

    @staticmethod
    def _init_pirates():
        pirates = []
        for _, row in get_asset("pirates/pirates.csv").iterrows():
            pirates.append(Pirate.from_dict(row.to_dict()))
        return pirates

    def print_state(self):
        print()

        print("-- 🏠 Pirates at the Tavern --")
        for pirate in self.pirates:
            if not pirate.on_a_quest():
                print(pirate)
        print()

        print("-- 🧭 Pirates at Sea --")
        for pirate in self.pirates:
            if pirate.on_a_quest():
                print(pirate)
        print()

        print("-- 📌 Pinned quests --")
        if len(self.pinned_quests):
            for quest in self.pinned_quests:
                print(f"> {quest}")
        else:
            print("> EMPTY BOARD")
        print()

        print("-- Available quests --")
        for i, quest in enumerate(["Skip turn"] + self.available_quests):
            print(f"{i}) {quest}")
        print()
        print(f"-- 🔄 TURN {self.turn} | 💰 GOLD {self.gold}  --")

    def randomize_quests(self, n_quests):
        return list(np.random.choice(self.quest_bank, n_quests, replace=False))

    def select_quests(self):
        while True:
            self.print_state()

            if not self.available_quests:
                return

            quest = self._handle_quest_selected()
            if quest:
                quest = self._handle_bounty(quest)

                self.available_quests.remove(quest)
                self.pinned_quests.append(quest)
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

        self.available_quests = self.randomize_quests(self.n_quests)
        self.select_quests()
        print("\n-- 🗒️🖋️ TURN LOG --")
        for pirate in self.pirates:
            if pirate.current_quest is None:
                selected_quest = pirate.select_quest(self.pinned_quests)
                pirate.current_quest = selected_quest
                if selected_quest.qtype is QuestType.idle:
                    print(
                        f"💤 {pirate.name} decided to {selected_quest.name} for"
                        f" {selected_quest.difficulty} turns"
                    )
                else:
                    self.pinned_quests.remove(selected_quest)
                    print(
                        f"🚢 {pirate.name} embarked on a voyage!"
                        f" {selected_quest.name} [{selected_quest.qtype.name}]"
                    )
            else:
                success = pirate.progress_quest()

                # TODO QuestEffect abstract class
                if success is not None:
                    print(
                        f'{"🟢" if success else "🔴"} {pirate.name}'
                        f'{"SUCCEEDED" if success else "FAILED"} the'
                        f" quest {pirate.current_quest}"
                    )
                    self.gold -= pirate.current_quest.bounty
                    pirate.gold += pirate.current_quest.bounty
                    if success:
                        self.gold += pirate.current_quest.reward

                    pirate.current_quest = None
                else:
                    print(
                        f"🕓 {pirate.name} is working on a quest"
                        f" [{pirate.current_quest.progress} turn(s) remaining]"
                    )

    def run(self):
        while True:
            self.next_turn()
