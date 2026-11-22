from langchain_openai import ChatOpenAI

from config.settings import settings


def get_llm() -> ChatOpenAI:
    """
    Create and return the configured LLM instance.
    """

    return ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )