import abc
from typing import Dict, Callable, Any, cast

from langchain.prompts import FewShotPromptTemplate
from langchain.schema import BaseLanguageModel

from kor import nodes
from kor.parsing import parse_llm_output
from kor.prompts import (
    ExtractionPromptValue, PromptGenerator, JSON_ENCODING,
)

# # Finally, we create the `FewShotPromptTemplate` object.
# few_shot_prompt = FewShotPromptTemplate(
#     # These are the examples we want to insert into the prompt.
#     examples=examples,
#     # This is how we want to format the examples when we insert them into the prompt.
#     example_prompt=example_prompt,
#     # The prefix is some text that goes before the examples in the prompt.
#     # Usually, this consists of intructions.
#     prefix="Give the antonym of every input.",
#     # The suffix is some text that goes after the examples in the prompt.
#     # Usually, this is where the user input will go
#     suffix="Word: {input}\nAntonym:",
#     # The input variables are the variables that the overall prompt expects.
#     input_variables=["input"],
#     # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
#     example_separator="\n",
# )
#

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
