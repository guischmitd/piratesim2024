import random

from piratesim.common.assets import get_asset
from piratesim.common.utils import clear_terminal
from piratesim.common.random import get_seed
from piratesim.pirate import Pirate
from piratesim.quests.quest import Quest, QuestType
from piratesim.quests.quest_factory import QuestFactory


def load_pirate_bank() -> list[Pirate]:
    pirates = []
    for _, row in get_asset("pirates/pirates.csv").iterrows():
        pirates.append(Pirate.from_dict(row.to_dict()))
    return pirates


def load_quest_bank():
    return get_asset("quests/quests.csv").set_index("quest_id")


class Game:
    def __init__(self, max_pirates_per_run=2, n_quests=2, starting_gold=500, seed=None, debug=True) -> None:
        self.runs = []
        self.max_pirates_per_run=max_pirates_per_run
        self.n_quests = n_quests
        self.gold = starting_gold

        self.pirate_bank = load_pirate_bank()

        self._debug = debug
        self._seed = seed if seed else get_seed()
        random.seed(self._seed)

        # Starting pirates
        self.pirates = [p for p in self.pirate_bank if p.level == 0]


    def launch_run(self,
                   selected_pirates
        ):
        run = SingleRun(
            selected_pirates,
            gold = self.gold,
            n_quests=self.n_quests,
            unlocked_pirates=self.pirates,
            seed=self._seed,
            debug=self._debug
        )
        self.runs.append(run)
        run.run()

        self.gold = run.gold
        for pirate in run.pirates:
            if pirate not in self.pirates:
                self.pirates.append(pirate)

    def main_menu(self):
        selected_pirates = []
        while True:
            clear_terminal()
            print(
                f"-- 🔄 RUNS {len(self.runs)} | 💰 GOLD {self.gold}  | 🌱 SEED {self._seed} --")
            
            print("-- YOUR PIRATES --")
            print('0) Start run')
            for i, pirate in enumerate(self.pirates):
                print(f'{i+1}) [{"x" if pirate in selected_pirates else " "}]',
                    pirate)
                
            ans = input(f'\n📢  Select up to {self.max_pirates_per_run} pirates: ')
            try:
                ans = int(ans)
            except:
                continue
            
            if ans not in list(range(len(self.pirates) + 1)):
                continue
            
            if ans == 0:
                if len(selected_pirates) == 0:
                    print('> You must select at least 1 pirate!')
                    continue
                elif len(selected_pirates) > self.max_pirates_per_run:
                    print(f'> Only {self.max_pirates_per_run} pirates allowed!')
                    continue
                else:
                    self.launch_run(selected_pirates)
            
            selected_pirate = self.pirates[ans - 1]
            if selected_pirate in selected_pirates:
                selected_pirates.remove(selected_pirate)
            else:
                selected_pirates.append(selected_pirate)
            

    def run(self):
        while True:
            self.main_menu()


class SingleRun:
    def __init__(
        self, selected_pirates, n_quests, gold, unlocked_pirates, seed, debug=False
    ) -> None:
        self.n_quests = n_quests
        self.quest_bank = load_quest_bank()
        self.pirate_bank = load_pirate_bank()
        self.turn = 0
        self.turn_log = {}
        self._debug = debug
        self._seed = seed

        self.gold = gold

        self.notoriety = 0
        self.max_notoriety = 30

        self.available_quests: list[Quest] = []
        self.pinned_quests: list[Quest] = []
        self.pinned_quests_expiration: dict[Quest, int] = {}
        self.pirates: list[Pirate] = selected_pirates
        self.unlocked_pirates: list[Pirate] = unlocked_pirates

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
    def quests_in_progress(self):
        quests_in_progress = []
        for pirate in self.pirates:
            if pirate.current_quest:
                quests_in_progress.append(pirate.current_quest)
        
        return quests_in_progress

    def randomize_quests(self, n_quests):
        quests = []
        for _, row in self.quest_bank.iterrows():
            if (row["is_chain_root"]) and row["name"] not in [
                q.name for q in self.available_quests + self.quests_in_progress
            ]:
                quests.append(QuestFactory().from_dict(row.to_dict()))

        return random.sample(quests, k=min(len(quests), n_quests))

    def select_quests(self):
        while True:
            clear_terminal()
            self.print_state()

            if not self.available_quests:
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
            # TODO allow bounty bigger than reward
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
            return True
        if self.gold < 0:
            return True
        
        return False

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
                    self.turn_log[self.turn].append(
                        f"🕓 {pirate.name} is working on a quest"
                        f" [{pirate.current_quest.progress} turn(s) remaining]"
                    )

        game_over = self._check_game_over()
        return game_over

    def run(self):
        while True:
            game_over = self.next_turn()
            if game_over:
                print("\n\n >-- GAME OVER --<")
                for key in self.turn_log:
                    print(f"-- TURN {key} --")
                    for line in self.turn_log[key]:
                        print(line)
                
                return self
