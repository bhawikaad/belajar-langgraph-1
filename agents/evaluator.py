from config.llm import get_llm
from config.settings import settings
from graph.state import ArticleState
from models.evaluation import EvaluationResult
from prompts.article_prompts import EVALUATOR_PROMPT


class EvaluatorAgent:
    def __init__(self):
        self.llm = get_llm()
        self.structured_llm = self.llm.with_structured_output(
            EvaluationResult
        )

    def run(self, state: ArticleState) -> ArticleState:
        article = state["article"]

        # Template prompt ada di prompts/article_prompts.py. {language} =
        # bahasa feedback dari settings, supaya feedback yang nanti dipakai
        # generator saat revisi konsisten dengan bahasa artikel.
        prompt = EVALUATOR_PROMPT.format(
            article=article,
            language=settings.output_language,
        )

        result = self.structured_llm.invoke(prompt)

        return {
            "feedback": result.feedback,
            "approved": result.approved,
        }