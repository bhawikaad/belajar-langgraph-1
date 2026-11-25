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

    # decision = nilai yang dikirim lewat Command(resume=...). Bentuk yang
    # didukung: dict {"approved": bool, "note": str} (dipakai main.py),
    # atau cukup True/False.
    if isinstance(decision, dict):
        approved = bool(decision.get("approved"))
        note = (decision.get("note") or "").strip()
    else:
        approved, note = bool(decision), ""

    if approved:
        return {"human_approved": True}

    # Ditolak manusia: artikel harus ditulis ulang. Generator memakai field
    # `feedback` saat merevisi, jadi catatan manusia diletakkan di sana
    # (menimpa feedback evaluator). Instruksi ini masuk ke prompt, maka
    # ditulis dalam bahasa Inggris.
    default_note = (
        "The reviewer rejected this draft without specific notes. "
        "Rewrite it with clearer structure, stronger content, and better readability."
    )

    return {
        "human_approved": False,
        "feedback": note or default_note,
        # Reset agar loop evaluator <-> generator mendapat jatah revisi baru
        # (kalau tidak, revisi karena penolakan manusia ikut menghabiskan
        # MAX_REVISIONS dan evaluator bisa langsung berhenti).
        "revision_count": 0,
    }


def save_node(state: ArticleState) -> ArticleState:
    """
    LangGraph node untuk menyimpan artikel yang disetujui ke folder output/.

    Node ini tidak memakai LLM, jadi tidak perlu class Agent: cukup
    fungsi biasa yang membaca state, memanggil service, dan
    mengembalikan field yang berubah (output_path).
    """

    # outline dan image_prompt dikirim sebagai catatan di awal file;
    # .get() karena field ini NotRequired di state.
    path = save_article(
        state["topic"],
        state["article"],
        outline=state.get("outline"),
        image_prompt=state.get("image_prompt"),
    )

    # Return hanya field yang berubah; LangGraph menggabungkannya ke state.
    return {"output_path": path}
