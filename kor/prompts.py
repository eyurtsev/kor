"""Code to dynamically generate appropriate LLM prompts."""
from __future__ import annotations

import abc
import dataclasses
from typing import Any, Callable, List, Literal, Tuple, Type, Union

from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    PromptValue,
    SystemMessage,
)
from pydantic import Extra

from kor.encoders import CSVEncoder, Encoder, XMLEncoder, JSONEncoder
from kor.encoders.encode import encode_examples
from kor.examples import generate_examples
from kor.nodes import AbstractInput, Object
from kor.type_descriptors import (
    generate_bullet_point_description,
    generate_typescript_description,
)

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


# TODO(Eugene): Figure out the best place to do this.
def _extract_top_level_fieldnames(node: AbstractInput) -> List[str]:
    """Temporary schema description for CSV extraction."""
    if isinstance(node, Object):
        return [attributes.id for attributes in node.attributes]
    else:
        return [node.id]


@dataclasses.dataclass(frozen=True)
class ExtractionTemplate(PromptGenerator):
    """Prompt generator for extraction purposes."""

    prefix: str
    type_descriptor: str
    encoder_class: Type[Encoder]
    example_generator: Callable[
        [AbstractInput], List[Tuple[str, str]]
    ] = generate_examples

    def __post_init__(self) -> None:
        """Validate the template."""
        if self.prefix.endswith("\n"):
            raise ValueError("Please do not end the prefix with new lines.")

    def replace(self, **kwargs: Any) -> "ExtractionTemplate":
        """Bind to replace function for convenience."""
        return dataclasses.replace(self, **kwargs)

    def _generate_encoder(self, node: AbstractInput) -> Encoder:
        """TODO(Eugene): This doesn't look good here."""
        if (
            self.encoder_class == CSVEncoder
        ):  # TODO(Eugene): Figure out how to best do this.
            fieldnames = _extract_top_level_fieldnames(node)
            encoder = self.encoder_class(fieldnames)
        else:
            encoder = self.encoder_class()
        return encoder

    def generate_encoded_examples(self, node: AbstractInput) -> List[Tuple[str, str]]:
        """Generate encoded examples."""
        encoder = self._generate_encoder(node)
        examples = self.example_generator(node)
        return encode_examples(examples, encoder)

    def generate_instruction_segment(self, node: AbstractInput) -> str:
        """Generate the instruction segment of the extraction."""
        if self.type_descriptor == "TypeScript":
            type_description = generate_typescript_description(node)
        elif self.type_descriptor == "BulletPoint":
            type_description = generate_bullet_point_description(node)
        else:
            raise NotImplementedError("Unsupported type descriptor")
        encoder = self._generate_encoder(node)
        instruction_segment = encoder.get_instruction_segment()
        return f"{self.prefix}\n\n{type_description}\n\n{instruction_segment}"

    def format_as_string(self, user_input: str, node: AbstractInput) -> str:
        """Format the template for a `standard` LLM model."""
        instruction_segment = self.generate_instruction_segment(node)
        encoded_examples = self.generate_encoded_examples(node)
        formatted_examples: List[str] = []

        for in_example, output in encoded_examples:
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
        encoded_examples = self.generate_encoded_examples(node)

        for example_input, example_output in encoded_examples:
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


STANDARD_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=(
        "Your goal is to extract structured information from the user's input that"
        " matches the form described below. When extracting information please make"
        " sure it matches the type information exactly. Do not add any attributes that"
        " do not appear in the schema shown below."
    ),
    type_descriptor="TypeScript",
    encoder_class=XMLEncoder,
)

JSON_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=(
        "Your goal is to extract structured information from the user's input that"
        " matches the form described below. When extracting information please make"
        " sure it matches the type information exactly. Do not add any attributes that"
        " do not appear in the schema shown below."
    ),
    type_descriptor="TypeScript",
    encoder_class=JSONEncoder,
)


BULLET_POINT_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=(
        "Your goal is to extract structured information from the user's input that"
        " matches the schema shown below. When extracting information please make"
        " sure it matches the type information exactly. "
    ),
    type_descriptor="BulletPoint",
    encoder_class=XMLEncoder,
)

CSV_EXTRACTION_TEMPLATE = ExtractionTemplate(
    prefix=(
        "Your goal is to extract structured information from the user's input that"
        " matches the form described below. When extracting information please make"
        " sure it matches the type information exactly. Do not add any attributes that"
        " do not appear in the schema shown below."
    ),
    type_descriptor="TypeScript",
    encoder_class=CSVEncoder,
)
