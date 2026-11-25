from config.llm import get_llm
from config.settings import settings
from graph.state import ArticleState
from prompts.article_prompts import GENERATOR_PROMPT, GENERATOR_REVISION_PROMPT


class GeneratorAgent:
    """Agent untuk menghasilkan artikel."""

    def __init__(self):
        self.llm: BaseChatModel = get_llm()

    def run(self, state: ArticleState) -> ArticleState:
        topic = state["topic"]
        outline = state["outline"]

        # Jika sudah ada feedback, berarti ini revisi dari artikel yang ditolak.
        feedback = state.get("feedback")
        previous_article = state.get("article")
        is_revision = bool(feedback and previous_article)

        # Template prompt ada di prompts/article_prompts.py. {language} =
        # bahasa artikel dari settings (instruksi prompt tetap bahasa Inggris).
        prompt = GENERATOR_PROMPT.format(
            topic=topic,
            outline=outline,
            language=settings.output_language,
        )

        # Saat revisi, tambahkan instruksi perbaikan di akhir prompt dasar.
        if is_revision:
            prompt += GENERATOR_REVISION_PROMPT.format(
                previous_article=previous_article,
                feedback=feedback,
            )

        response = self.llm.invoke(prompt)

        update = {"article": response.content}

        # Node hanya mengembalikan field yang berubah; LangGraph yang
        # menggabungkannya ke state.
        if is_revision:
            update["revision_count"] = state.get("revision_count", 0) + 1

        return update