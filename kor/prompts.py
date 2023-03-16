"""Code to dynamically generate appropriate LLM prompts."""
from __future__ import annotations

import abc
import dataclasses
from typing import Any, Callable, List, Literal, Tuple, Union
import json
from json import JSONDecodeError


from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    PromptValue,
    SystemMessage,
)
from pydantic import Extra

from kor.examples import generate_examples
from kor.nodes import AbstractInput
from kor.type_descriptors import (
    generate_bullet_point_description,
    generate_typescript_description,
)
from kor.parsing import parse_llm_output

PromptFormat = Union[Literal["openai-chat"], Literal["string"]]


@dataclasses.dataclass(frozen=True)
class PromptGenerator(abc.ABC):
    """Define abstract interface for a prompt."""

    @abc.abstractmethod
    def format_as_string(self, user_input: str, node: AbstractInput) -> str:
        """Format as a prompt to a standard LLM."""
        raise NotImplementedError()

    @abc.abstractmethod
    def format_as_chat(self, user_input: str, node: AbstractInput) -> List[BaseMessage]:
        """Format as a prompt to a chat model."""
        raise NotImplementedError()

    def parser(self) -> Callable[[str], Any]:
        raise NotImplementedError()


def load_json_or_dict(s: str):
    try:
        return json.loads(s)
    except JSONDecodeError:
        return {}


@dataclasses.dataclass(frozen=True)
class ExtractionTemplate(PromptGenerator):
    """Prompt generator for extraction purposes."""

    prefix: str
    type_descriptor: str
    suffix: str
    encoding: str
    example_generator: Callable[
        [AbstractInput], List[Tuple[str, str]]
    ] = generate_examples

    def __post_init__(self) -> None:
        """Validate the template."""
        if self.prefix.endswith("\n"):
            raise ValueError("Please do not end the prefix with new lines.")

        if self.suffix.endswith("\n"):
            raise ValueError("Please do not end the suffix with new lines.")

    def replace(self, **kwargs: Any) -> "ExtractionTemplate":
        """Bind to replace function for convenience."""
        return dataclasses.replace(self, **kwargs)

    def parser(self):
        if self.encoding == "JSON":
            return load_json_or_dict
        elif self.encoding == "XML":
            return parse_llm_output
        else:
            raise NotImplementedError()

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
        formatted_examples: List[str] = []

        for in_example, output in examples:
            formatted_examples.extend(
                [
                    f"Input: {in_example}",
                    f"Output: {output}",
                ]
            )

        formatted_examples.append(f"Input: {user_input}\nOutput:")
        input_output_block = "\n".join(formatted_examples)
        return f"{instruction_segment}\n\n{input_output_block}"

    def format_as_chat(self, user_input: str, node: AbstractInput) -> List[BaseMessage]:
        """Format the template for a `chat` LLM model."""
        instruction_segment = self.generate_instruction_segment(node)

        messages: List[BaseMessage] = [SystemMessage(content=instruction_segment)]

        for example_input, example_output in self.example_generator(
            node, encoding=self.encoding
        ):
            messages.extend(
                [
                    HumanMessage(content=example_input),
                    AIMessage(content=example_output),
                ]
            )

        messages.append(HumanMessage(content=user_input))
        return messages


class ExtractionPromptValue(PromptValue):
    """Integration with langchain prompt format."""

    template: ExtractionTemplate
    user_input: str
    node: AbstractInput

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def to_string(self) -> str:
        """Format the template to a string."""
        return self.template.format_as_string(self.user_input, self.node)

    def to_messages(self) -> List[BaseMessage]:
        """Format the template to chat messages."""
        return self.template.format_as_chat(self.user_input, self.node)


PREFIX = (
    "Your goal is to extract structured information from a given segment of text. "
    "The extracted information must exactly match the schema provided below. If the attribute or "
    "object does not appear in the schema do not add it."
)


STANDARD_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=PREFIX,
    type_descriptor="TypeScript",
    suffix=(
        "For Union types the output must EXACTLY match one of the members of the Union"
        " type.\n\nPlease enclose the extracted information in HTML style tags with the"
        " tag name corresponding to the corresponding component ID. Use angle style"
        " brackets for the tags ('>' and '<'). Only output tags when you're confident"
        " about the information that was extracted from the user's query. If you can"
        " extract several pieces of relevant information from the query, then include"
        " all of them. If the type is an array, please repeat the corresponding tag"
        " name multiple times once for each relevant extraction. Do NOT output anything"
        " except for the extracted information. Only output information inside the HTML"
        " style tags. Do not include any notes or any clarifications. "
    ),
    encoding="XML",
)


BULLET_POINT_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=PREFIX,
    type_descriptor="BulletPoint",
    suffix=(
        "Your task is to parse the user input and determine to what values the user is"
        " attempting to set each component of the form.\nWhen the type of the input is"
        " a Selection, only output one of the options specified in the square brackets"
        " as arguments to the Selection type of this input. Please enclose the"
        " extracted information in HTML style tags with the tag name corresponding to"
        " the corresponding component ID. Use angle style brackets for the tags ('>'"
        " and '<'). Only output tags when you're confident about the information that"
        " was extracted from the user's query. If you can extract several pieces of"
        " relevant information from the query include use a comma to separate the tags."
        " Do NOT output anything except for the extracted information. Only output"
        " information inside the HTML style tags. Do not include any notes or any"
        " clarifications. "
    ),
    encoding="XML",
)


JSON_ENCODING = ExtractionTemplate(
    prefix=(
        "Your goal is to extract structured information from the user's input that"
        " matches the form described below. When extracting information please make"
        " sure it matches the type information exactly. "
    ),
    type_descriptor="TypeScript",
    suffix=(
        "Please output your results in a JSON format that matches the type information "
        "provided above. Do not NOT explain your results, do NOT provide clarifications. "
        "If no relevant information can be extracted from the segment of text, please output "
        "an empty object encoded in JSON format, and nothing else."
    ),
    encoding="JSON",
)
