from enum import Enum, auto

import numpy as np


class QuestType(Enum):
    treasure = auto()
    combat = auto()
    delivery = auto()
    rescue = auto()
    smuggling = auto()
    fetch = auto()
    exploration = auto()
    escort = auto()
    survival = auto()
    theft = auto()
    idle = auto()


class Quest:
    def __init__(
        self, name: str, qtype: QuestType, difficulty: int, reward: int
    ) -> None:
        self.name = name
        self.qtype = qtype
        self.difficulty = difficulty
        self.reward = reward
        self._bounty = 0
        self.progress = self.difficulty

    @classmethod
    def from_dict(cls, template_dict):
        difficulty = np.random.randint(
            template_dict["difficulty_min"], template_dict["difficulty_max"] + 1
        )
        min_reward = template_dict["reward_min"] // 10
        max_reward = template_dict["reward_max"] // 10 + 1

        reward = np.random.randint(min_reward, max_reward) * 10

        return cls(
            name=template_dict["name"],
            qtype=QuestType[template_dict["type"]],
            difficulty=difficulty,
            reward=reward,
        )

    @property
    def bounty(self):
        return self._bounty

    @property
    def bounty_ratio(self) -> int:
        return int(100 * self.bounty / self.reward)

    @bounty.setter
    def bounty(self, value):
        if value is not None:
            assert isinstance(value, int), "bounty must be an integer!"
            assert int(value) >= 0 and int(value) <= self.reward
            self._bounty = int(value)

    def __repr__(self) -> str:
        return (
            f"D {self.difficulty} - R {self.reward}\t[{self.qtype.name}]\t| {self.name}"
        )
