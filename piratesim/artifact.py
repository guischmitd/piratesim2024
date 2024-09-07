class Artifact:
    def __init__(
        self, navigation_modifier, combat_modifier, trickyness_modifier
    ) -> None:
        self.navigation_modifier = navigation_modifier
        self.combat_modifier = combat_modifier
        self.trickyness_modifier = trickyness_modifier

    def on_equip(self, pirate):
        pirate.navigation = min(pirate.navigation + self.navigation_modifier, 5)
        pirate.combat = min(pirate.combat + self.combat_modifier, 5)
        pirate.trickyness = min(pirate.trickyness + self.trickyness_modifier, 5)
