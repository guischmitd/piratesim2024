import random

from piratesim.common.assets import get_asset
from piratesim.encounters.effects import MoraleEffect
from piratesim.encounters.encounter import Encouter


class EncounterManager:
    def __init__(self) -> None:
        self.encounter_bank = get_asset("encounters/encounters.csv")
        self.option_columns = sorted(
            [
                c
                for c in self.encounter_bank.columns
                if c.startswith("option_") and "success" not in c and "failure" not in c
            ]
        )

        self.odds_columns = sorted(
            [c for c in self.encounter_bank.columns if c.endswith("success_odds")]
        )

        self.success_text_columns = sorted(
            [c for c in self.encounter_bank.columns if c.endswith("success_text")]
        )

        self.failure_text_columns = sorted(
            [c for c in self.encounter_bank.columns if c.endswith("failure_text")]
        )

    def create_encounter(self):
        """Creates a random encounter"""
        random_index = random.randint(0, len(self.encounter_bank) - 1)
        encounter_data = self.encounter_bank.iloc[random_index]

        options = encounter_data[self.option_columns].dropna().tolist()
        odds = encounter_data[self.odds_columns].dropna().tolist()
        success_texts = encounter_data[self.success_text_columns].dropna().tolist()
        failure_texts = encounter_data[self.failure_text_columns].dropna().tolist()

        return Encouter(
            title=encounter_data["title"],
            description=encounter_data["description"],
            options=options,
            success_odds=odds,
            success_texts=success_texts,
            failure_texts=failure_texts,
            success_effects=[[MoraleEffect(5)]] * len(options),
            failure_effects=[[MoraleEffect(-5)]] * len(options),
        )
