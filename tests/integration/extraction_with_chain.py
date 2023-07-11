from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field

from kor.adapters import from_pydantic
from kor.extraction import create_extraction_chain


def test_pydantic() -> None:
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=2000)

    class Person(BaseModel):
        first_name: str = Field(
            description="The first name of a person.",
        )

    schema, v = from_pydantic(
        Person,
        description="Personal information",
        examples=[
            (
                "Alice and Bob are friends",
                {"first_name": "Alice"},
            )
        ],
        many=True,
    )

    chain = create_extraction_chain(llm, schema)
    result = chain.run("My name is Bobby. My brother's name Joe.")  # type: ignore
    data = result["data"]  # type: ignore

    assert "person" in data  # type: ignore
    assert len(data["person"]) == 2  # type: ignore
