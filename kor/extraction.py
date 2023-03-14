import abc
from typing import Any, Union

from kor import nodes, prompts
from kor.llms import ChatCompletionModel, CompletionModel
from kor.parsing import parse_llm_output


class Extractor(abc.ABC):  # pylint: disable=too-few-public-methods
    def __init__(
        self,
        model: Union[CompletionModel, ChatCompletionModel],
        prompt_generator: prompts.PromptGenerator = prompts.STANDARD_EXTRACTION_TEMPLATE,
    ) -> None:
        """Initialize an extractor with a model and a prompt generator."""
        self.model = model
        self.prompt_generator = prompt_generator

    def __call__(self, user_input: str, node: nodes.AbstractInput) -> Any:
        """Invoke the extractor with a user input and a schema node."""
        if isinstance(self.model, CompletionModel):
            prompt = self.prompt_generator.format_as_string(user_input, node)
        elif isinstance(self.model, ChatCompletionModel):
            prompt = self.prompt_generator.format_as_chat(user_input, node)
        else:
            raise NotImplementedError(
                f"Unsupported model interface for type {type(self.model)}."
            )
        model_output = self.model(prompt)
        return parse_llm_output(model_output)
