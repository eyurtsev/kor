"""Define public interface for llm wrapping package."""
from .openai import OpenAIChatCompletion, OpenAICompletion
from .typedefs import ChatCompletionModel, CompletionModel

__all__ = [
    "OpenAIChatCompletion",
    "OpenAICompletion",
    "CompletionModel",
    "ChatCompletionModel",
]
