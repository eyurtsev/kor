"""***WIP EXPERIMENTAL*** code for a parsing interpreter."""
import abc
import dataclasses
from typing import Mapping, Any, Tuple, Self

from kor import elements
from kor.elements import AbstractInput
from kor.extraction import extract
from kor.llm_utils import LLMOpenAI


# @dataclasses.dataclass(frozen=True)
# hooks for state transitions / input interpretation
# @dataclasses.dataclass(frozen=True)
# class Action:
#     """Intended action."""
#
#     name: str
#     prompt: str
#     parameters: Mapping[str, Any]
#
# class FormFillingState:
#     input: Form
#     requires_confirmation: bool
#     parameters: Dict[str, Any]
#     on_success: Callable
#     on_cancel: Callable


@dataclasses.dataclass(frozen=True)
class Intent(abc.ABC):
    """Abstract intent type from which all intents should be derived."""


@dataclasses.dataclass(frozen=True)
class UpdateIntent(Intent):
    location_id: str
    information: Mapping[str, Any]


@dataclasses.dataclass(frozen=True)
class NoOpIntent(Intent):
    pass


@dataclasses.dataclass(frozen=True)
class Message:
    content: str
    success: bool


@dataclasses.dataclass(frozen=True)
class State:
    location_id: str  # Working on id
    information: Mapping[str, dict]

    def update(self, new_information: Mapping[str, dict]) -> Self:
        """Update the state."""
        updated_information = dict(self.information)
        updated_information.update(**new_information)
        return dataclasses.replace(self, information=updated_information)


@dataclasses.dataclass(frozen=True)
class InputTree:
    id_to_input: Mapping[str, AbstractInput]

    def resolve(self, id: str) -> AbstractInput:
        """Resolve the input tree."""
        return self.id_to_input[id]


def create_input_tree(input: AbstractInput) -> InputTree:
    """Create an input tree."""
    id_stack = [input]
    id_to_input = {}

    if not isinstance(input, (elements.Option, elements.Selection, elements.Form)):
        raise AssertionError(f"Type {type(input)} is not supported.")

    while id_stack:
        input = id_stack.pop(0)
        id_to_input.update({input.id: input})

        # match input:
        #     case Option:
        #         print("hello")
        #     # case Selection:
        #     #     for option in input.options:
        #
    return InputTree(id_to_input=id_to_input)


class Automaton:
    def __init__(self, input: AbstractInput) -> None:
        self.input_tree = create_input_tree(input)
        self.state = State(location_id=input.id, information={})
        self.past_states = []

    def current_element(self) -> AbstractInput:
        """Get the state associated with the current element."""
        return self.input_tree.resolve(self.state.location_id)

    @property
    def allowed_transitions(self):
        """Get information about the allowed options from given state."""
        current_element = self.input_tree.resolve(self.state.location_id)
        if isinstance(current_element, elements.Selection):
            return current_element.option_ids()
        else:
            return []

    def update(self, intent: Intent) -> Tuple[State, Message]:
        """Update the state based on the intent."""
        if isinstance(intent, UpdateIntent):
            new_state = self.state.update(intent.information)
            self.past_states.append(self.state)
            self.state = new_state
            message = Message(
                content=f"OK! Updated. The new state is: {self.state.information}.",
                success=True,
            )
            return new_state, message
        elif isinstance(intent, NoOpIntent):
            return self.state, Message(
                content="Sorry I didn't catch that.", success=False
            )
        else:
            raise NotImplemented(type(intent))


class Interpreter:
    def __init__(self, automaton: Automaton) -> None:
        """Existing bot interpreter."""
        self.automaton = automaton
        self.llm = LLMOpenAI()

    def generate_state_message(self) -> Message:
        current_state = self.automaton.state
        element = self.automaton.input_tree.resolve(current_state.location_id)
        # We need something to compare required/option vs. known information
        if isinstance(element, elements.Selection):
            valid_options = ", ".join(sorted(element.option_ids))

            input_summary = (
                f"You're currently updating element with ID: {element.id}.\n"
                f"Description: {element.description}\n"
                f"Valid options: {valid_options}\n"
            )
        elif isinstance(element, elements.Form):
            input_summary = "You  are editing a form. TODO(EUGENE): Add stuff"
        else:
            raise AssertionError()

        return Message(success=True, content=f"Hello! {input_summary}")

    def interact(self, user_input: str) -> Message:
        """Interact with a user."""
        current_state = self.automaton.state
        element = self.automaton.current_element()
        if not isinstance(element, elements.Form):
            raise NotImplementedError()
        parsed_data = extract(user_input, element, self.llm)

        if parsed_data:
            intent = UpdateIntent(
                current_state.location_id,
                information={current_state.location_id: parsed_data},
            )
        else:
            intent = NoOpIntent()
        new_state, message = self.automaton.update(intent)
        return message


def run_interpreter(element: AbstractInput) -> None:
    """Run the interpreter."""
    automaton = Automaton(element)
    interpreter = Interpreter(automaton)
    message = interpreter.generate_state_message()
    print(message.content)

    while True:
        user_input = input()
        if user_input == "q":
            print("OK! Goodbye!")
            break
        message = interpreter.interact(user_input)
        print(message.content)
