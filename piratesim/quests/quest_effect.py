from abc import ABC, abstractmethod

class QuestEffect(ABC):
    @abstractmethod
    def resolve(self, game) -> str:
        raise NotImplementedError()

    def on_selected(self, *args):
        pass