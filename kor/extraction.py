import abc
from typing import Dict, List, Callable, Any, cast


from langchain.schema import BaseLanguageModel

from kor import nodes
from kor.parsing import parse_llm_output
from kor.prompts import (
    STANDARD_EXTRACTION_TEMPLATE,
    ExtractionPromptValue,
    PromptGenerator,
    JSON_ENCODING,
)


class Extractor(abc.ABC):  # pylint: disable=too-few-public-methods
    def __init__(
        self,
        model: BaseLanguageModel,
        prompt_generator: PromptGenerator = JSON_ENCODING,
        parser: Callable[[str], Dict[str, Any]] = parse_llm_output,
    ) -> None:
        """Initialize an extractor with a model and a prompt generator."""
        self.model = model
        self.prompt_generator = prompt_generator
        self.parser = parser

    def __call__(self, user_input: str, node: nodes.AbstractInput) -> Any:
        """Invoke the extractor with a user input and a schema node."""
        prompt = ExtractionPromptValue(
            template=self.prompt_generator, user_input=user_input, node=node
        )
        model_output = self.model.generate_prompt([prompt])
        text = cast(str, model_output.generations[0][0].text)
        return self.prompt_generator.parser()(text)
