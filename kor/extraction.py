import abc
from typing import Dict, List, Any

from pydantic import Extra

from kor import nodes
from kor.encoders import Encoder
from kor.nodes import AbstractInput
from kor.prompts import (
    STANDARD_EXTRACTION_TEMPLATE,
    ExtractionPromptValue,
    PromptGenerator,
)
from langchain import BasePromptTemplate
from langchain.output_parsers import BaseOutputParser
from langchain.schema import BaseLanguageModel, PromptValue


class ExtractionPromptTemplate(BasePromptTemplate):
    node: AbstractInput

    def format_prompt(self, user_input: str, **kwargs: Any) -> PromptValue:
        """Format the prompt."""
        return ExtractionPromptValue(
            template=STANDARD_EXTRACTION_TEMPLATE, user_input=user_input, node=self.node
        )

    def format(self, **kwargs: Any) -> str:
        raise NotImplementedError()

    @property
    def _prompt_type(self) -> str:
        """Prompt type."""
        return "ExtractionPromptTemplate"


class KorEncoder(BaseOutputParser):
    """A langchain parser """
    encoder: Encoder

    @property
    def _type(self) -> str:
        return 'KOREn'

    def parse(self, text: str):
        return self.encoder.decode(text)

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True


class Extractor(abc.ABC):  # pylint: disable=too-few-public-methods
    def __init__(
        self,
        model: BaseLanguageModel,
        prompt_generator: PromptGenerator = STANDARD_EXTRACTION_TEMPLATE,
    ) -> None:
        """Initialize an extractor with a model and a prompt generator."""
        self.model = model
        self.prompt_generator = prompt_generator

    def __call__(
        self, user_input: str, node: nodes.AbstractInput
    ) -> Dict[str, List[str]]:
        """Invoke the extractor with a user input and a schema node."""
        prompt = ExtractionPromptValue(
            template=self.prompt_generator, user_input=user_input, node=node
        )
        model_output = self.model.generate_prompt([prompt])
        text = model_output.generations[0][0].text
        encoder = self.prompt_generator._generate_encoder(node)
        return encoder.decode(text)
