from piratesim.encounters.encounter_effect import EncounterEffect


class MoraleEffect(EncounterEffect):
    def __init__(self, morale_value) -> None:
        self.morale_value = morale_value

    def resolve(self, pirate):
        effect_log = []
        if self.morale_value > 0:
            effect_log.append(f"The crew's morale increased by {self.morale_value}!")
        elif self.morale_value < 0:
            effect_log.append(f"The crew's morale decreased by {self.morale_value}!")

        pirate.morale += self.morale_value

        return effect_log
