from typing import Callable, Mapping, Sequence

from kor import elements, prompts
from kor.llm_utils import parse_llm_output


def extract(
    user_input: str,
    form: elements.Form,
    model: Callable[[str], str] | Callable[[Sequence[Mapping[str, str]]], str],
    prompt_generator: prompts.PromptGenerator = prompts.STANDARD_EXTRACTION_TEMPLATE,
    prompt_format: prompts.PROMPT_FORMAT = "string",
) -> dict[str, list[str]]:
    """Extract information from the user input using the given form."""
    if prompt_format == "string":
        chat_prompt = prompt_generator.format_chat(user_input, form)
    elif prompt_format == "chat":
        chat_prompt = prompt_generator.format_chat(user_input, form)
    else:
        raise NotImplementedError(f"Unknown prompt format {prompt_format}")
    model_output = model(chat_prompt)
    return parse_llm_output(model_output)
