from langgraph.graph import StateGraph, START, END

from graph.router import route_after_evaluation, route_after_human_review
from graph.state import ArticleState
from graph.nodes import (
    orchestrator_node,
    generator_node,
    evaluator_node,
    human_review_node,
    image_prompt_node,
    save_node,
)


def create_workflow(checkpointer=None):
    """
    Bangun dan compile graph.

    checkpointer (opsional): objek yang menyimpan snapshot state setelah
    setiap node selesai. Tanpa checkpointer graph tidak punya "ingatan"
    antar run; dengan checkpointer kita bisa melihat riwayat state, dan
    nanti melanjutkan run yang terhenti atau menyisipkan human-in-the-loop.
    """
    # StateGraph = graph yang berbagi satu state (ArticleState) antar node.
    workflow = StateGraph(ArticleState)

    # Daftarkan node: nama (string) -> fungsi node.
    # Nama inilah yang dipakai saat membuat edge dan di router.
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("generator", generator_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("image_prompt", image_prompt_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("save", save_node)

    # Edge biasa: urutan tetap, tanpa percabangan.
    workflow.add_edge(START, "orchestrator")
    workflow.add_edge("orchestrator", "generator")
    workflow.add_edge("generator", "evaluator")

    # Conditional edge: setelah "evaluator", fungsi route_after_evaluation
    # dipanggil dengan state terbaru dan mengembalikan sebuah string.
    # Dictionary di bawah memetakan string itu ke node tujuan.
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "approved": "image_prompt",  # artikel diterima -> buat prompt gambar
            "rejected": "generator",  # loop revisi: kembali ke node sebelumnya
            "max_revisions": END,  # jatah revisi habis -> berhenti tanpa menyimpan
        },
    )

    # Setelah prompt gambar dibuat, manusia memeriksa dulu (graph berhenti
    # di node ini sampai ada Command(resume=...); butuh checkpointer).
    workflow.add_edge("image_prompt", "human_review")
    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "approved": "save",
            "rejected": END,  # ditolak manusia -> berhenti tanpa menyimpan
        },
    )

    workflow.add_edge("save", END)

    # compile() mengubah definisi graph menjadi objek yang bisa di-invoke().
    # Checkpointer dipasang di sini; None berarti tanpa penyimpanan state.
    return workflow.compile(checkpointer=checkpointer)
