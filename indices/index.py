from abc import ABC, abstractmethod
from typing import List, Dict
from functions import Function

class FunctionIndex(ABC):
    @abstractmethod
    def put(self, function: Function) -> None:
        ''' add an function to the database '''

    @abstractmethod
    def get(self, name: str) -> Function:
        ''' get a function from the database '''

    @abstractmethod
    def retrieve(self, query: str, k: int = 1) -> List[Function]:
        ''' retrieve relevant function from the database '''