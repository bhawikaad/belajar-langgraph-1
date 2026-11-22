from langchain_core.language_models import BaseChatModel

from config.llm import get_llm
from graph.state import ArticleState
from prompts.article_prompts import IMAGE_PROMPT_PROMPT


class ImagePromptAgent:
    """Agent yang membuat prompt gambar (cover artikel) dari isi artikel."""

    def __init__(self):
        # Import BaseChatModel di atas membuat type hint ini valid.
        self.llm: BaseChatModel = get_llm()

    def run(self, state: ArticleState) -> ArticleState:
        # Agent ini hanya membaca dua field dari state.
        topic = state["topic"]
        article = state["article"]

        # Template prompt ada di prompts/article_prompts.py. Prompt gambar
        # sengaja dalam bahasa Inggris karena sebagian besar model image
        # generation paling baik dengan bahasa Inggris.
        prompt = IMAGE_PROMPT_PROMPT.format(topic=topic, article=article)

        response = self.llm.invoke(prompt)

        # Kembalikan hanya field yang berubah (partial update);
        # LangGraph yang menggabungkannya ke state.
        return {"image_prompt": response.content}
