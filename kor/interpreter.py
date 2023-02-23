import dataclasses
import os
from typing import Mapping, Any, Callable, Dict, Sequence, Tuple, Self

import openai

from kor import inputs
from .inputs import Form, Input, Option
from .llm_utils import parse_llm_response


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
class Intent:
    pass


@dataclasses.dataclass(frozen=True)
class Update(Intent):
    location_id: str
    information: Mapping[str, Any]


@dataclasses.dataclass(frozen=True)
class GoBack(Intent):
    pass


@dataclasses.dataclass(frozen=True)
class Message:
    content: str
    success: bool


@dataclasses.dataclass(frozen=True)
class UpdateIntent(Intent):
    location_id: str
    information: Mapping[str, Any]


@dataclasses.dataclass(frozen=True)
class NoOpIntent(Intent):
    pass


@dataclasses.dataclass(frozen=True)
class Confirm(Intent):
    pass


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
    id_to_input: Mapping[str, Input]

    def resolve(self, id: str) -> Input:
        """Resolve the input tree."""
        return self.id_to_input[id]


def create_input_tree(input: Input) -> InputTree:
    """Create an input tree."""
    id_stack = [input]
    id_to_input = {}
    if not isinstance(input, (inputs.Option, inputs.Selection, inputs.Form)):
        raise AssertionError("not supported")
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
    def __init__(self, input: Input) -> None:
        self.input_tree = create_input_tree(input)
        self.state = State(location_id=input.id, information={})
        self.past_states = []

    def current_element(self) -> Input:
        return self.input_tree.resolve(self.state.location_id)

    @property
    def allowed_transitions(self):
        """Get information about the allowed options from given state."""
        current_element = self.input_tree.resolve(self.state.location_id)
        if isinstance(current_element, inputs.Selection):
            return current_element.allowed_transitions()
        else:
            return []

    def update(self, intent: Intent) -> Tuple[State, Message]:
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
        self.llm = LLM()

    def generate_state_message(self) -> Message:
        current_state = self.automaton.state
        element = self.automaton.input_tree.resolve(current_state.location_id)
        # We need something to compare required/option vs. known information
        if isinstance(element, inputs.Selection):
            valid_options = ", ".join(sorted(element.allowed_transitions()))

            input_summary = (
                f"You're currently updating element with ID: {element.id}.\n"
                f"Description: {element.description}\n"
                f"Valid options: {valid_options}\n"
            )
        elif isinstance(element, inputs.Form):
            input_summary = "You  are editing a form. TODO(EUGENE): Add stuff"
        else:
            raise AssertionError()

        return Message(success=True, content=f"Hello! {input_summary}")

    def interact(self, user_input: str) -> Message:
        """Interact with a user."""
        current_state = self.automaton.state
        element = self.automaton.current_element()
        prompt = inputs.generate_prompt_for_input(user_input, element)
        allowed_transitions = self.automaton.allowed_transitions
        selected_option = self.llm.call(prompt, allowed_transitions)

        if selected_option:
            intent = UpdateIntent(
                current_state.location_id,
                information={current_state.location_id: selected_option},
            )
        else:
            intent = NoOpIntent()
        new_state, message = self.automaton.update(intent)
        return message


class LLM:
    def __init__(self) -> None:
        openai.api_key = os.environ["OPENAI_API_KEY"]

    def call(self, prompt: str, allowed_options: Sequence[str]) -> str | None:
        """Invoke the LLM with the given prompt."""
        print("here is the prompt: ")
        print(prompt)
        print("-" * 80)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        print(response)
        text = response["choices"][0]["text"]
        choice = parse_llm_response(text, allowed_options=allowed_options)
        return choice


def run_interpreter(element: Input):
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


if __name__ == "__main__":
    selection = inputs.Selection(
        id="do",
        description="select what you want to do",
        options=[
            Option(
                id="eat",
                description="Specify that you want to eat",
                examples=["I'm hungry", "I want to eat"],
            ),
            Option(
                id="drink",
                description="Specify that you want to drink",
                examples=["I'm thirsty", "I want to drink"],
            ),
            Option(
                id="sleep",
                description="Specify that you want to sleep",
                examples=["I'm tired", "I want to go to bed"],
            ),
        ],
        examples=[],
    )

    selection2 = inputs.Selection(
        id="watch",
        description="select which movie you want to watch",
        options=[
            Option(
                id="bond",
                description="James Bond 007",
                examples=["watch james bond", "spy movie"],
            ),
            Option(
                id="leo",
                description="toddler movie about a dumptruck",
                examples=["dumptruck movie", "a movie for kids"],
            ),
            Option(
                id="alien",
                description="horror movie about aliens in space",
                examples=["something scary", "i want to watch a scary movie"],
            ),
        ],
        examples=[],
    )

    selection3 = inputs.Selection(
        id="sex",
        description="what's your sex",
        options=[
            Option(
                id="male",
                description="male",
                examples=[],
            ),
            Option(
                id="female",
                description="female",
                examples=[],
            ),
            Option(
                id="other",
                description="other",
                examples=[],
            ),
        ],
        examples=[],
    )
    form = inputs.Form(
        id="stuff",
        description="form to specify what to do and what to watch",
        elements=[selection, selection2, selection3],
        examples=[],
    )
    run_interpreter(form)
