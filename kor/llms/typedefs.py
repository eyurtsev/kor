"""Provide standard interface on tops of LLMs."""
import abc
import dataclasses


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
