from abc import ABC, abstractmethod

class Chain(ABC):

    @abstractmethod
    def run(self, query: str):
        ''' run the chain '''