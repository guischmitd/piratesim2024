
import random
from typing import Optional

from piratesim.quests import load_quest_bank
from piratesim.quests.quest import Quest
from piratesim.quests.quest_factory import QuestFactory

ISLAND_NAMES = [
    "Blackwater", "Crimson", "Skullfang", "Serpent's", "Deadman's", "Lost Anchor", 
    "Pirate's", "Stormwatch", "Cursed", "Tortuga", "Golden Sands", "Mermaid's", 
    "Wraith's", "Devil's", "Sharktooth", "Cutlass", "Plunderer's", "Raven's", 
    "Thunder", "Shipwreck", "Bloodmoon", "Whispering", "Hurricane", "Marauder's", 
    "Siren's", "Fogbound", "Jagged Edge", "Rogue's", "Emerald", "Silver Skull"
]

ISLAND_TYPES = [
    "Isle", "Reef", "Atoll", "Quay", "Cove", "Cay", "Rest", "Bay", "Lagoon", 
    "Haven", "Reach", "Key", "Nest", "Shoals", "Point", "Hideaway", "Call", "Island"
]


class Region:
    def __init__(self, 
                 island_name: str,
                 direction: str,
                 available_quest: Optional[Quest],
                 distance: int = 3,
                 ) -> None:
        
        self.island_name = island_name
        self.direction = direction
        self.available_quest = available_quest
        self.distance = distance
        self.discovered = False

    def explore(self):
        self.discovered = True
        return self.available_quest
    
    def __repr__(self) -> str:
        return f"{self.island_name if self.discovered else '???'}, {self.distance} leagues to the {self.direction}"


class WorldMap:
    def __init__(self, quests_to_spawn = 4) -> None:
        self.directions = ['NORTH', 'SOUTH', 'EAST', 'WEST',
                    'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST']
        self.map = self._generate_map(quests_to_spawn)
    
    def get_region(self, direction):
        return self.map[direction]
    
    def get_all_regions(self):
        return [self.map[d] for d in self.directions]

    def _generate_map(self, quests_to_spawn):
        quest_bank = load_quest_bank()
        roots = quest_bank[quest_bank['is_chain_root'] == 1]
        
        selected_quests = [QuestFactory().from_dict(row.to_dict()) 
                        for _, row in roots.sample(quests_to_spawn).iterrows()]
        selected_directions = random.sample(self.directions, quests_to_spawn)

        dir_quest_dict = dict(zip(selected_directions, selected_quests))
        world_map = {}
        
        for direction in self.directions:
            island_name = f"{random.choice(ISLAND_NAMES)} {random.choice(ISLAND_TYPES)}"
            world_map[direction] = Region(
                island_name=island_name,
                available_quest=dir_quest_dict.get(direction, None),
                distance=random.randint(2, 5),
                direction=direction
            )

        return world_map