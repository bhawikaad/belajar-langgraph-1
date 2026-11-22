from graph.state import ArticleState

# Batas revisi agar loop generator <-> evaluator tidak berjalan tanpa akhir.
MAX_REVISIONS = 2


def route_after_human_review(state: ArticleState) -> str:
    """
    Menentukan node berikutnya setelah keputusan manusia.

    - "approved" : disetujui manusia -> simpan
    - "rejected" : ditolak manusia -> selesai tanpa menyimpan
    """
    if state["human_approved"]:
        return "approved"

    return "rejected"


def route_after_evaluation(state: ArticleState) -> str:
    """
    Menentukan node berikutnya setelah evaluasi.

    - "approved"       : artikel diterima -> selesai
    - "rejected"       : artikel ditolak, masih ada jatah revisi -> kembali ke generator
    - "max_revisions"  : artikel ditolak tapi jatah revisi habis -> selesai
    """
    if state["approved"]:
        return "approved"

    if state.get("revision_count", 0) >= MAX_REVISIONS:
        return "max_revisions"

    return "rejected"
