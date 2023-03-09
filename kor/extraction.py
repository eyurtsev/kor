from typing import Callable, Mapping, Sequence

from kor import nodes, prompts
from kor.parsing import parse_llm_output


def extract(
    user_input: str,
    node: nodes.AbstractInput,
    model: Callable[[str], str] | Callable[[Sequence[Mapping[str, str]]], str],
    prompt_generator: prompts.PromptGenerator = prompts.STANDARD_EXTRACTION_TEMPLATE,
    prompt_format: prompts.PROMPT_FORMAT = "string",
) -> dict[str, list[str]]:
    """Extract information from the user input using the given form."""
    if prompt_format == "string":
        chat_prompt = prompt_generator.format_as_string(user_input, node)
    elif prompt_format == "openai-chat":
        chat_prompt = prompt_generator.format_as_chat(user_input, node)
    else:
        raise NotImplementedError(f"Unknown prompt format {prompt_format}")
    model_output = model(chat_prompt)
    return parse_llm_output(model_output)
