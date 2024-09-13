class Artifact:
    def __init__(
        self,
        name,
        description,
        navigation_modifier,
        combat_modifier,
        trickyness_modifier,
        **kwargs
    ) -> None:
        self.name = name
        self.description = description
        self.navigation_modifier = navigation_modifier
        self.combat_modifier = combat_modifier
        self.trickyness_modifier = trickyness_modifier

        increased = []
        decreased = []
        for mod_name, mod in zip(
            ["NAVIGATION", "COMBAT", "TRICKYNESS"],
            [navigation_modifier, combat_modifier, trickyness_modifier],
        ):
            if mod > 0:
                increased.append(f"{mod_name} by {abs(mod)}")
            if mod < 0:
                decreased.append(f"{mod_name} by {abs(mod)}")

        self.description = description.strip() + "\n\t"
        if increased:
            self.description += f'Increases {", ".join(increased)}. '
        if decreased:
            self.description += f'Reduces {", ".join(decreased)}. '

    def on_equip(self, pirate):
        pirate.navigation = pirate.navigation + self.navigation_modifier
        pirate.combat = pirate.combat + self.combat_modifier
        pirate.trickyness = pirate.trickyness + self.trickyness_modifier

    def unequip(self, pirate):
        pirate.navigation = pirate.navigation - self.navigation_modifier
        pirate.combat = pirate.combat - self.combat_modifier
        pirate.trickyness = pirate.trickyness - self.trickyness_modifier
