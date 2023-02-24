import abc
import dataclasses
import os
from typing import Mapping, Any, Tuple, Self

import openai

import kor.prompts
from kor import elements
from .elements import AbstractInput, Option
from .llm_utils import parse_llm_response


@dataclasses.dataclass(frozen=True)
class Action:
    """Intended action."""

    name: str
    prompt: str
    parameters: Mapping[str, Any]


# @dataclasses.dataclass(frozen=True)
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
        self.llm = LLM()

    def generate_state_message(self) -> Message:
        current_state = self.automaton.state
        element = self.automaton.input_tree.resolve(current_state.location_id)
        # We need something to compare required/option vs. known information
        if isinstance(element, elements.Selection):
            valid_options = ", ".join(sorted(element.option_ids()))

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
        prompt = kor.prompts.generate_prompt_for_input(user_input, element)
        # allowed_transitions = self.automaton.allowed_transitions
        parsed_data = self.llm.call(prompt)

        if parsed_data:
            intent = UpdateIntent(
                current_state.location_id,
                information={current_state.location_id: parsed_data},
            )
        else:
            intent = NoOpIntent()
        new_state, message = self.automaton.update(intent)
        return message


class LLM:
    def __init__(self) -> None:
        """Initialize the LLM model."""
        openai.api_key = os.environ["OPENAI_API_KEY"]

    def call(self, prompt: str) -> dict[str, list[str]]:
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
        parsed_information = parse_llm_response(text)
        return parsed_information


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


def get_test_form() -> elements.Form:
    """Get a test form."""
    selection = elements.Selection(
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

    selection2 = elements.Selection(
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

    selection3 = elements.Selection(
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
    movie_date = elements.DateInput(
        id="watch-when",
        description="When do you want to watch the movie",
        examples=[
            ("I want to watch the movie on 2022-01-03", "2022-01-03"),
            ("I want to watch a movie after dinner", "after dinner"),
        ],
    )

    dentist_date = elements.DateInput(
        id="dentist-when",
        description="When will you go to the dentist",
        examples=[
            ("I am going to the dentist on 2022-01-03", "2022-01-03"),
            ("I am going to the dentist after dinner", "after dinner"),
        ],
    )

    nationality_input = elements.TextInput(
        id="nationality",
        description="What is your nationality. Please only use standard nationalities.",
        examples=[
            ("I am an american", "American"),
            ("je suis french", "French"),
        ],
    )

    form = elements.Form(
        id="input-form",
        description="form to specify what to do and what to watch",
        elements=[
            selection,
            selection2,
            selection3,
            movie_date,
            dentist_date,
            nationality_input,
        ],
        examples=[],
    )
    return form


def get_test_form_2():
    company_name = elements.TextInput(
        id="company-name",
        description="what is the name of the company you want to find",
        examples=[
            ("Apple inc", "Apple inc"),
            ("largest 10 banks in the world", ""),
            ("microsoft and apple", "microsoft,apple"),
        ],
    )
    selection_block = elements.Selection(
        multiple=True,
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
    industry_name = elements.TextInput(
        id="industry-name",
        description="what is the name of the company's industry",
        examples=[
            ("companies in the steel manufacturing industry", "steel manufacturing"),
            ("large banks", "banking"),
            ("military companies", "defense"),
            ("chinese companies", ""),
        ],
    )

    geography_name = elements.TextInput(
        id="geography-name",
        description="where is the company based? Please use a single country name.",
        examples=[
            ("chinese companies", "china"),
            ("companies based in france", "france"),
            ("france, italy", ""),
        ],
    )

    foundation_date = elements.DateInput(
        id="foundation-date",
        description="Foundation date of the company",
        examples=[("companies founded in 2023", "2023")],
    )

    revenue = elements.Number(
        id="revenue",
        description="What is the revenue of the company?",  # Might want to model the currency
        examples=[("Revenue of $1,000,000", "$1,000,000"), ("No revenue", 0)],
    )

    employee_range = elements.NumericRange(
        id="employees",
        description="The number of employees reported potentially as a range. May include either a max, a min or both.",
        examples=[
            ("At least 100 employees", "(100, *)"),
            ("Less than twelve employees", "(*, 12)"),
            ("Fifty to sixty employees", "(50, 60)"),
        ],
    )

    sales_geography = elements.TextInput(
        id="geography-sales",
        description="where is the company doing sales? Please use a single country name.",
        examples=[
            ("companies with sales in france", "france"),
            ("companies that sell their products in germany", "germany"),
            ("france, italy", ""),
        ],
    )

    form = elements.Form(
        id="search-for-companies",
        description="Search for companies matching the following criteria.",
        elements=[
            company_name,
            selection_block,
            geography_name,
            foundation_date,
            industry_name,
            revenue,
            sales_geography,
            employee_range,
        ],
        examples=[],
    )
    return form


def main() -> None:
    form = get_test_form_2()
    run_interpreter(form)


if __name__ == "__main__":
    main()
