from graph.state import ArticleState
from agents.orchestrator import OrchestratorAgent
from agents.generator import GeneratorAgent
from agents.evaluator import EvaluatorAgent
from langgraph.types import interrupt

from agents.image_prompt import ImagePromptAgent
from services.storage import save_article


def generator_node(state: ArticleState) -> ArticleState:
    """
    LangGraph node untuk menghasilkan draft artikel.
    """

    agent = GeneratorAgent()
    return agent.run(state)


def orchestrator_node(state: ArticleState) -> ArticleState:
    """
    LangGraph node untuk menghasilkan outline artikel.
    """
    
    agent = OrchestratorAgent()
    return agent.run(state)


def evaluator_node(state: ArticleState) -> ArticleState:
    """
    LangGraph node untuk evaluasi output draft artikel.
    """
    
    evaluator = EvaluatorAgent()
    return evaluator.run(state)


def image_prompt_node(state: ArticleState) -> ArticleState:
    """
    LangGraph node untuk membuat prompt gambar cover dari artikel
    yang sudah disetujui.
    """

    agent = ImagePromptAgent()
    return agent.run(state)


def human_review_node(state: ArticleState) -> ArticleState:
    """
    LangGraph node untuk meminta persetujuan manusia sebelum artikel disimpan.

    interrupt() menghentikan graph di sini dan mengirim payload ke pemanggil.
    Graph baru lanjut ketika pemanggil memanggil invoke/stream dengan
    Command(resume=...); nilai resume itu menjadi hasil kembalian interrupt().

    PENTING: saat dilanjutkan, node ini dijalankan ULANG dari baris pertama.
    Karena itu jangan taruh efek samping (tulis file, kirim request, dsb.)
    sebelum interrupt().
    """

    decision = interrupt(
        {
            "pesan": "Setujui artikel ini untuk disimpan?",
            "article": state["article"],
            "image_prompt": state.get("image_prompt", ""),
        }
    )

    # decision = nilai yang dikirim lewat Command(resume=...), di sini True/False.
    return {"human_approved": bool(decision)}


def save_node(state: ArticleState) -> ArticleState:
    """
    LangGraph node untuk menyimpan artikel yang disetujui ke folder output/.

    Node ini tidak memakai LLM, jadi tidak perlu class Agent: cukup
    fungsi biasa yang membaca state, memanggil service, dan
    mengembalikan field yang berubah (output_path).
    """

    path = save_article(state["topic"], state["article"])

    # Return hanya field yang berubah; LangGraph menggabungkannya ke state.
    return {"output_path": path}
