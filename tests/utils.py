from typing import Any, List, Optional

from langchain.chat_models.base import BaseChatModel
from langchain.schema import AIMessage, BaseMessage, ChatGeneration, ChatResult
from pydantic import Extra


class ToyChatModel(BaseChatModel):
    response: str

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def _generate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None
    ) -> ChatResult:
        message = AIMessage(content=self.response)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    async def _agenerate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None
    ) -> Any:
        """Async version of _generate."""
        message = AIMessage(content=self.response)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
