from pathlib import Path

import pandas as pd
import numpy as np

from piratesim.pirate import Pirate
from piratesim.quest import Quest 


class Game:
    def __init__(self, n_quests=3, n_pirates=5, level=1) -> None:
        self.n_quests = n_quests
        self.quest_bank = self._init_quests()
        self.pirate_bank = self._init_pirates()
        self.turn = 0

        self.gold = 1000

        self.available_quests : list[Quest] = self.randomize_quests(n_quests)
        self.pinned_quests : list[Quest] = []
        self.pirates : list[Pirate] = np.random.choice(self.pirate_bank, n_pirates, replace=False)

    @staticmethod
    def _init_quests():
        quests = []
        for _, row in pd.read_csv(Path(__file__).parent / 'assets' / 'quests' / 'quests.csv').iterrows():
            quests.append(Quest.from_dict(row.to_dict()))
        return quests
    
    @staticmethod
    def _init_pirates():
        pirates = []
        for _, row in pd.read_csv(Path(__file__).parent / 'assets' / 'pirates' / 'pirates.csv').iterrows():
            pirates.append(Pirate.from_dict(row.to_dict()))
        return pirates
    
    def randomize_quests(self, n_quests):
        return list(np.random.choice(self.quest_bank, n_quests, replace=False))
    
    def select_quests(self):
        while len(self.available_quests):
            print('-- Pinned quests --')
            for quest in self.pinned_quests:
                print(f'> {quest}')
            print()

            print('-- Available quests --')
            for i, quest in enumerate(self.available_quests):
                print(f'{i + 1}) {quest}')
            print()


            quest = self._handle_quest_selected()
            quest = self._handle_bounty(quest)

            self.available_quests.remove(quest)
            self.pinned_quests.append(quest)

            ans = input('Next turn? ')
            if ans.lower() in ['y', 'yes']:
                return
        
    def _handle_quest_selected(self): 
        ans = input('🗺️   Select a quest: ')
        try:
            ans = int(ans)
            assert ans > 0 and ans <= len(self.available_quests)
        except:
            print('⚠️   Invalid option!')
            return self._handle_quest_selected()
        return self.available_quests[ans - 1]
    
    def _handle_bounty(self, quest: Quest):
        ans = input("💰   What will be the pirate's cut? ")
        try:
            ans = int(ans)
            quest.bounty = ans
        except ValueError as e:
            print(f'⚠️   Invalid option! ({e})')
            return self._handle_bounty(quest)
        except AssertionError as e:
            print(f'⚠️   Invalid option! ({e})')
            return self._handle_bounty(quest)
        
        return quest

    def next_turn(self):
        self.turn += 1

        self.randomize_quests(self.n_quests)
        self.select_quests()
        # np.random.shuffle(self.pirates)
        for pirate in self.pirates:
            if pirate.current_quest is None:
                selected_quest = pirate.select_quest(self.available_quests)
                self.available_quests.remove(selected_quest)
                print(f'> {pirate.name} selected {selected_quest}')
            else:
                success = pirate.progress_quest()
                if success is not None:
                    self.gold -= pirate.current_quest.bounty
                    pirate.gold += pirate.current_quest.bounty
                    if success:
                        self.gold += pirate.current_quest.reward

                    pirate.current_quest = None

    def run(self):
        while True:
            self.next_turn()