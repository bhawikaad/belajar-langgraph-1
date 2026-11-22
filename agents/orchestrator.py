from config.llm import get_llm
from graph.state import ArticleState
from prompts.article_prompts import ORCHESTRATOR_PROMPT


class OrchestratorAgent:
    """Agent yang membuat outline artikel berdasarkan topic."""

    def __init__(self):
        self.llm: BaseChatModel = get_llm()

    def run(self, state: ArticleState) -> ArticleState:
        topic = state["topic"]

        # Template prompt ada di prompts/article_prompts.py;
        # format() mengisi placeholder {topic}.
        prompt = ORCHESTRATOR_PROMPT.format(topic=topic)

        response = self.llm.invoke(prompt)

        return {
            "outline": response.content
        }