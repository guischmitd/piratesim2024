from piratesim.common.random import RouletteSelector
from piratesim.common.utils import clear_terminal
from piratesim.encounters.encounter_effect import EncounterEffect


class Encouter:
    def __init__(
        self,
        title: str,
        description: str,
        options: list[str],
        success_odds: list[float],
        success_texts: list[str],
        failure_texts: list[str],
        success_effects: list[list[EncounterEffect]],
        failure_effects: list[list[EncounterEffect]],
    ) -> None:
        self.title = title
        self.description = description
        self.options = options

        self.success_odds = success_odds
        self.success_effects = success_effects
        self.failure_effects = failure_effects

        self.success_texts = success_texts
        self.failure_texts = failure_texts

    def trigger(self, quest_taker):
        description = self.description.format(name=quest_taker.name)

        clear_terminal()
        print(f" --- ⁉️ {self.title.upper()} ⁉️ --- ")
        print(description + "\n")

        for i, option in enumerate(self.options):
            print(f"{i + 1}) {option}")

        ans = self._handle_option_selection()

        roulette = RouletteSelector(items=[True, False])
        roulette.set_chance(True, self.success_odds[ans])
        success = roulette.roll()

        encounter_log = ["\t" + description]
        if success:
            encounter_log.append(
                "\t" + self.success_texts[ans].format(name=quest_taker.name)
            )
            for effect in self.success_effects[ans]:
                encounter_log.extend(["\t\t" + s for s in effect.resolve(quest_taker)])
        else:
            encounter_log.append(
                "\t" + self.failure_texts[ans].format(name=quest_taker.name)
            )
            for effect in self.failure_effects[ans]:
                encounter_log.extend(["\t\t" + s for s in effect.resolve(quest_taker)])

        return encounter_log

    def _handle_option_selection(self):
        ans = input("\n❓  Select a course of action: ")
        try:
            ans = int(ans)
        except:
            print("> Invalid option!")
            return self._handle_option_selection

        if ans not in range(1, len(self.options) + 1):
            print("> Invalid option!")
            return self._handle_option_selection

        return ans - 1
