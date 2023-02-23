"""Parse LLM Response."""

from typing import Sequence


def parse_llm_response(response: str, allowed_options: Sequence[str]) -> str | None:
    """Parse llm response."""
    no_whitespace = response.strip()
    if no_whitespace.startswith("<") and no_whitespace.endswith(">"):
        option = no_whitespace[1:-1]
        if option in allowed_options:
            return option
    return None
