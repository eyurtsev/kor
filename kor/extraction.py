import abc
from typing import Dict, List

from langchain.schema import BaseLanguageModel

from kor import nodes
from kor.prompts import (
    STANDARD_EXTRACTION_TEMPLATE,
    ExtractionPromptValue,
    PromptGenerator,
)


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
