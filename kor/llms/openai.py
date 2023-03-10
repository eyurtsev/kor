import dataclasses
import json
import logging
import os

from .typedefs import CompletionModel, ChatCompletionModel

try:
    import openai
except ImportError:
    openai = None


logger = logging.getLogger(__name__)


def _set_openai_api_key_if_needed() -> None:
    """Set the openai api key if needed."""
    if not openai:
        raise ImportError("Missing `openai` dependency.")

    if not openai.api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            if "OPENAI_API_KEY" not in os.environ:
                raise ValueError(
                    "Please include OPENAI_API_KEY in the environment or set the openai.api_key."
                )
        openai.api_key = api_key


@dataclasses.dataclass(kw_only=True, frozen=True)
class OpenAICompletion(CompletionModel):
    """Wrapper around OpenAI Completion endpoint."""

    model: str
    verbose: bool = False
    temperature: float = 0
    max_tokens: int = 2000
    frequency_penalty: float = 0
    presence_penalty: float = 0
    top_p: float = 1.0

    def __post_init__(self) -> None:
        """Set credentials if needed."""
        _set_openai_api_key_if_needed()

    def __call__(self, prompt: str) -> str:
        """Invoke the LLM with the given prompt."""
        if self.verbose:
            logger.debug(prompt)
        response = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        if self.verbose:
            logger.debug(json.dumps(response))
        text = response["choices"][0]["text"]
        return text


@dataclasses.dataclass(kw_only=True, frozen=True)
class OpenAIChatCompletion(ChatCompletionModel):
    """Wrapper around OpenAI Chat Completion endpoint."""

    model: str
    verbose: bool = False
    temperature: float = 0
    max_tokens: int = 1000
    frequency_penalty: float = 0
    presence_penalty: float = 0
    top_p: float = 1.0

    def __post_init__(self) -> None:
        """Set credentials if needed."""
        _set_openai_api_key_if_needed()

    def __call__(self, messages: list[dict[str, str]]) -> str:
        """Invoke the LLM with the given prompt."""
        if self.verbose:
            for message in messages:
                logger.debug(json.dumps(message))
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        if self.verbose:
            logger.debug(json.dumps(response))
        text = response["choices"][0]["message"]["content"]
        return text
