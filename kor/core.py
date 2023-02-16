import openai
from typing import Mapping, Any
import dataclasses


class State:
    """Represent the current state of the automaton."""

    pass


@dataclasses.dataclass(frozen=True)
class Action:
    """Intended action."""

    name: str
    prompt: str
    parameters: Mapping[str, Any]

    def submit(self):
        """"""
        pass
    
    
class Interpreter:
    def __init__(self) -> None:
        """Existing bot interpreter."""
        self.state = None
        
    
    
   
if __name__ == "__main__" :
    pass