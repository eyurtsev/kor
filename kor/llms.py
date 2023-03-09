"""Provide standard interface on tops of LLMs."""
import abc
import dataclasses
import json
import logging
import os

import openai

logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True)
class CompletionModel(abc.ABC):
    """Abstract completion model interface."""

    def __call__(self, prompt: str) -> str:
        """Call the model."""
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class ChatCompletionModel(abc.ABC):
    """Abstract chat completion model interface."""

    def __call__(self, messages: list[dict[str, str]]) -> str:
        """Call the model."""
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class OpenAICompletion(CompletionModel):
    """Wrapper around OpenAI Completion endpoint."""

    model: str = "text-davinci-001"
    verbose: bool = False
    temperature: float = 0
    max_tokens: int = 1000
    frequency_penalty: float = 0
    presence_penalty: float = 0
    top_p: float = 1.0

    def __post_init__(self) -> None:
        """Initialize the LLM model."""
        openai.api_key = os.environ["OPENAI_API_KEY"]

    def __call__(self, prompt: str) -> str:
        """Invoke the LLM with the given prompt."""
        if self.verbose:
            print(prompt)
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
            print(response)
            logger.debug(json.dumps(response))
        text = response["choices"][0]["text"]
        print(text)
        return text


@dataclasses.dataclass(kw_only=True)
class OpenAIChatCompletion(ChatCompletionModel):
    """Wrapper around OpenAI Chat Completion endpoint."""

    model: str = "gpt-3.5-turbo"
    verbose: bool = False
    temperature: float = 0
    max_tokens: int = 1000
    frequency_penalty: float = 0
    presence_penalty: float = 0
    top_p: float = 1.0

    def __post_init__(self) -> None:
        """Initialize the LLM model."""
        openai.api_key = os.environ["OPENAI_API_KEY"]

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
