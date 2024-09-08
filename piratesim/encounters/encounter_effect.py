from abc import ABC, abstractmethod


class EncounterEffect(ABC):
    @abstractmethod
    def resolve(self, pirate) -> str:
        raise NotImplementedError()
