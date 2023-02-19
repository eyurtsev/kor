import dataclasses
from typing import Mapping, Any, Callable, Dict, Tuple

from inputs import Form


@dataclasses.dataclass(frozen=True)
class Action:
    """Intended action."""

    name: str
    prompt: str
    parameters: Mapping[str, Any]

    def submit(self):
        """"""
        pass


@dataclasses.dataclass(frozen=True)
class FormFillingState:
    input: Form
    requires_confirmation: bool
    parameters: Dict[str, Any]
    on_success: Callable
    on_cancel: Callable


@dataclasses.dataclass(frozen=True)
class Transition:
    pass


@dataclasses.dataclass(frozen=True)
class GoBack(Transition):
    pass


@dataclasses.dataclass(frozen=True)
class Message:
    content: str
    success: bool


@dataclasses.dataclass(frozen=True)
class UpdateInformation(Transition):
    pass


@dataclasses.dataclass(frozen=True)
class Confirm(Transition):
    pass


class Automaton:
    def __init__(self, state) -> None:
        """State"""
        self.state = state
        self.past_states = []

    def update(self, transition: Transition) -> Tuple[Any, Message]:
        raise NotImplemented()
        # match transition:
        #     case GoBack:
        #         self.state.on_cancel()
        #     case UpdateInformation:
        #         pass
        #     case Confirm:
        #         pass


class Interpreter:
    def __init__(self, automaton: Automaton, model) -> None:
        """Existing bot interpreter."""
        self.automaton = automaton
        self.model = model

    def interact(self, user_input: str):
        current_state = self.automaton.state
        transition = self.model.interpret(current_state)
        new_state, message = self.automaton.update(transition)
        # Emit message
        print(message.content)


if __name__ == "__main__":
    pass
