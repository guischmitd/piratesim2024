import random

from piratesim.single_run import SingleRun
from piratesim.artifact import Artifact
from piratesim.common.assets import get_asset
from piratesim.common.random import get_seed
from piratesim.common.utils import clear_terminal
from piratesim.pirate import load_pirate_bank


class Game:
    def __init__(
        self,
        max_pirates_per_run=2,
        n_quests=2,
        starting_gold=500,
        seed=None,
        random_encounter_chance=1.0,
        debug=True,
    ) -> None:
        self.runs = []
        self.max_pirates_per_run = max_pirates_per_run
        self.random_encounter_chance = random_encounter_chance
        self.n_quests = n_quests
        self.gold = starting_gold

        self.pirate_bank = load_pirate_bank()

        self._debug = debug
        self._seed = seed if seed else get_seed()
        random.seed(self._seed)

        # Starting pirates
        self.pirates = [p for p in self.pirate_bank if p.level == 0]

        # Starting artifacts
        self.artifacts = [
            Artifact(
                name=row['name'],
                description=row['description'],
                navigation_modifier=row['navigation_modifier'],
                combat_modifier=row['combat_modifier'],
                trickyness_modifier=row['trickyness_modifier'],
                )
            for _, row in get_asset("artifacts/artifacts.csv").iterrows()
        ]

    def launch_run(self, selected_pirates):
        run = SingleRun(
            selected_pirates,
            gold=self.gold,
            n_quests=self.n_quests,
            unlocked_pirates=self.pirates,
            random_encounter_chance=self.random_encounter_chance,
            seed=self._seed,
            debug=self._debug,
        )
        self.runs.append(run)
        run.run()

        self.gold = run.gold
        for pirate in run.pirates:
            if pirate.artifact:
                self.artifacts.append(pirate.artifact)
                pirate.unequip_artifact()

            if pirate not in self.pirates:
                self.pirates.append(pirate)

    def main_menu(self):
        selected_pirates = []
        while True:
            clear_terminal()
            print(
                f"-- 🔄 RUNS {len(self.runs)} | 💰 GOLD {self.gold}  | 🌱 SEED"
                f" {self._seed} --"
            )

            print("-- YOUR PIRATES --")
            print("0) Next")
            for i, pirate in enumerate(self.pirates):
                print(
                    f'{i + 1}) [{"x" if pirate in selected_pirates else " "}]', pirate
                )

            ans = self._handle_pirate_selection()

            if ans != 0:
                selected_pirate = self.pirates[ans - 1]
                if selected_pirate in selected_pirates:
                    selected_pirates.remove(selected_pirate)
                else:
                    selected_pirates.append(selected_pirate)

            elif self._validate_pirate_selection(selected_pirates):
                self._handle_artifact_equipping(selected_pirates)
                self.launch_run(selected_pirates)
                selected_pirates = []

    def _handle_artifact_equipping(self, selected_pirates):
        for pirate in selected_pirates:
            clear_terminal()

            print("-- SELECTED PIRATES --")
            [print(pirate) for pirate in selected_pirates]

            print("\n-- YOUR ARTIFACTS --")
            print("0) None")
            for i, artifact in enumerate(self.artifacts):
                print(f'{i + 1}) "{artifact.name}" {artifact.description}')

            ans = self._handle_artifact_selection(pirate)

            if ans != 0:
                art = self.artifacts[ans - 1]
                pirate.equip_artifact(art)
                self.artifacts.remove(art)

    def _handle_artifact_selection(self, pirate):
        ans = input(f"\n⚙️  Select an artifact for {pirate.name}: ")

        try:
            ans = int(ans)
        except:
            print("> Invalid option!")
            return self._handle_artifact_selection(pirate)

        if ans not in range(len(self.artifacts) + 1):
            print("> Invalid option!")
            return self._handle_artifact_selection(pirate)

        return ans

    def _validate_pirate_selection(self, selected_pirates):
        if len(selected_pirates) == 0:
            print("> You must select at least 1 pirate!")
            input("Press Enter to continue...")
            return False

        elif len(selected_pirates) > self.max_pirates_per_run:
            print(f"> Only {self.max_pirates_per_run} pirates allowed!")
            input("Press Enter to continue...")
            return False

        return True

    def _handle_pirate_selection(self):
        ans = input(f"\n📢  Select up to {self.max_pirates_per_run} pirates: ")
        try:
            ans = int(ans)
        except:
            print("> Invalid pirate selection option!")
            return self._handle_pirate_selection()

        if ans not in list(range(len(self.pirates) + 1)):
            print("> Invalid pirate selection option!")
            return self._handle_pirate_selection()

        return ans

    def run(self):
        while True:
            self.main_menu()