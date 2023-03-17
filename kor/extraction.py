from langchain.chains import LLMChain
from langchain.schema import BaseLanguageModel

from kor.encoders import Encoder
from kor.prompts import create_langchain_prompt

# PUBLIC API


def create_extraction_chain(llm: BaseLanguageModel, encoder: Encoder) -> LLMChain:
    """Creat an extraction chain."""
    return LLMChain(llm=llm, prompt=create_langchain_prompt(encoder))
