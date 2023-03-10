"""Code to dynamically generate appropriate LLM prompts."""
import abc
import dataclasses
from typing import Union, Literal, Callable, List, Tuple

from kor.examples import generate_examples
from kor.nodes import AbstractInput
from kor.type_descriptors import (
    generate_typescript_description,
    generate_bullet_point_description,
)

PROMPT_FORMAT = Union[Literal["openai-chat"], Literal["string"]]


@dataclasses.dataclass(frozen=True, kw_only=True)
class PromptGenerator(abc.ABC):
    """Define abstract interface for a prompt."""

    @abc.abstractmethod
    def format_as_string(self, user_input: str, node: AbstractInput) -> str:
        """Format as a prompt to a standard LLM."""
        raise NotImplementedError()

    @abc.abstractmethod
    def format_as_chat(
        self, user_input: str, node: AbstractInput
    ) -> list[dict[str, str]]:
        """Format as a prompt to a chat model."""
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExtractionTemplate(PromptGenerator):
    """Prompt generator for extraction purposes."""

    prefix: str
    type_descriptor: str
    suffix: str
    example_generator: Callable[
        [AbstractInput], List[Tuple[str, str]]
    ] = generate_examples

    def __post_init__(self) -> None:
        """Validate the template."""
        if self.prefix.endswith("\n"):
            raise ValueError("Please do not end the prefix with new lines.")

        if self.suffix.endswith("\n"):
            raise ValueError("Please do not end the suffix with new lines.")

    def replace(self, **kwargs) -> "ExtractionTemplate":
        """Bind to replace function for convenience."""
        return dataclasses.replace(self, **kwargs)

    def generate_instruction_segment(self, node: AbstractInput) -> str:
        """Generate the instruction segment of the extraction."""
        if self.type_descriptor == "TypeScript":
            type_description = generate_typescript_description(node)
        elif self.type_descriptor == "BulletPoint":
            type_description = generate_bullet_point_description(node)
        else:
            raise NotImplementedError()
        return f"{self.prefix}\n\n{type_description}\n\n{self.suffix}"

    def format_as_string(self, user_input: str, node: AbstractInput) -> str:
        """Format the template for a `standard` LLM model."""
        instruction_segment = self.generate_instruction_segment(node)
        examples = self.example_generator(node)
        input_output_block = []

        for in_example, output in examples:
            input_output_block.extend(
                [
                    f"Input: {in_example}",
                    f"Output: {output}",
                ]
            )

        input_output_block.append(f"Input: {user_input}\nOutput:")
        input_output_block = "\n".join(input_output_block)
        return f"{instruction_segment}\n\n{input_output_block}"

    def format_as_chat(
        self, user_input: str, form: AbstractInput
    ) -> list[dict[str, str]]:
        """Format the template for a `chat` LLM model."""
        instruction_segment = self.generate_instruction_segment(form)

        messages = [
            {
                "role": "system",
                "content": instruction_segment,
            }
        ]

        for example_input, example_output in self.example_generator(form):
            messages.extend(
                [
                    {"role": "user", "content": example_input},
                    {
                        "role": "assistant",
                        "content": f"{example_output}",
                    },
                ]
            )

        messages.append({"role": "user", "content": user_input})
        return messages


STANDARD_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=(
        "Your goal is to extract structured information from the user's input that matches "
        "the form described below. "
        "When extracting information please make sure it matches the type information exactly. Do "
        "not add any attributes that do not appear in the schema shown below."
    ),
    type_descriptor="TypeScript",
    suffix=(
        "For Union types the output must EXACTLY match one of the members "
        "of the Union type.\n\n"
        "Please enclose the extracted information in HTML style tags with the tag name "
        "corresponding to the corresponding component ID. Use angle style brackets for the "
        "tags ('>' and '<'). "
        "Only output tags when you're confident about the information that was extracted "
        "from the user's query. If you can extract several pieces of relevant information "
        "from the query, then include all of them. If the type is an array, please "
        "repeat the corresponding tag name multiple times once for each relevant extraction. "
    ),
)


BULLET_POINT_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=(
        "Your goal is to extract structured information from the user's input that matches "
        "the form described below. "
        "When extracting information please make sure it matches the type information exactly. "
    ),
    type_descriptor="BulletPoint",
    suffix=(
        "Your task is to parse the user input and determine to what values the user is attempting "
        "to set each component of the form.\n"
        "When the type of the input is a Selection, only output one of the options specified in "
        "the square brackets as arguments to the Selection type of this input. "
        "Please enclose the extracted information in HTML style tags with the tag name "
        "corresponding to the corresponding component ID. Use angle style brackets for the "
        "tags ('>' and '<'). "
        "Only output tags when you're confident about the information that was extracted "
        "from the user's query. If you can extract several pieces of relevant information "
        "from the query include use a comma to separate the tags."
    ),
)
