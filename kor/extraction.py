from typing import Callable

from kor import elements, prompts
from kor.llm_utils import parse_llm_output


def extract(
    user_input: str, form: elements.Form, model: Callable[[str], str]
) -> dict[str, list[str]]:
    """Extract information from the user input using the given form."""
    prompt = prompts.generate_prompt_for_form(user_input, form)
    model_output = model(prompt)
    return parse_llm_output(model_output)


def chat_extract(
    user_input: str, form: elements.Form, model: Callable[[dict], str]
) -> dict[str, list[str]]:
    """Extract information from the user input using the given form."""
    chat_prompt = prompts.generate_chat_prompt_for_form(user_input, form)
    model_output = model(chat_prompt)
    return parse_llm_output(model_output)
