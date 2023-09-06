from typing import Any, List, Optional

from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain.chat_models.base import BaseChatModel
from langchain.schema import AIMessage, BaseMessage, ChatGeneration, ChatResult

from kor._pydantic import PYDANTIC_MAJOR_VERSION

if PYDANTIC_MAJOR_VERSION == 1:
    from pydantic import Extra  # type: ignore[assignment]
else:
    from pydantic.v1 import Extra  # type: ignore[assignment,no-redef]


class ToyChatModel(BaseChatModel):
    response: str

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Top Level call"""
        message = AIMessage(content=self.response)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async version of _generate."""
        message = AIMessage(content=self.response)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        """Return the type of llm this is."""
        return "toy_chat_model"
