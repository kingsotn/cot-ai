from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

class Function(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """name of this function"""

    @property
    @abstractmethod
    def description(self) -> str:
        """description for this function"""

    @abstractmethod
    def execute(self, input: str) -> str:
        """run this function"""

    def __str__(self) -> str:
        return self.name + ": " + self.description

