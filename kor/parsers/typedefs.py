import abc
from typing import Sequence, Tuple, List


class Encoder(abc.ABC):
    @abc.abstractmethod
    def encode(self, examples: Sequence[Tuple[str, str]]) -> str:
        """Encode the examples."""

    @abc.abstractmethod
    def decode(self, text: str) -> List[Tuple[str, str]]:
        """Decode the examples."""
        
    @abc.abstractmethod
    def format_instruction_segment(self) -> str:
        """Format instruction segment."""
        raise NotImplementedError()
