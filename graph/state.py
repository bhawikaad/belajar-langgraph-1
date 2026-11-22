"""
Shared State untuk workflow Article Blog Creation.

State ini menjadi media pertukaran data antar node LangGraph.
Setiap node membaca dan/atau memperbarui field yang relevan
sesuai tanggung jawabnya.
"""

from typing import TypedDict
from typing_extensions import NotRequired


class ArticleState(TypedDict):
    """Shared state untuk seluruh workflow."""

    # Input dari user
    topic: str

    # Hasil Orchestrator
    outline: NotRequired[str]

    # Draft artikel dari Generator
    article: NotRequired[str]

    # Masukan dari Evaluator
    feedback: NotRequired[str]

    # Status persetujuan artikel
    approved: NotRequired[bool]

    # Keputusan manusia (human-in-the-loop) sebelum artikel disimpan
    human_approved: NotRequired[bool]

    # Jumlah revisi yang sudah dilakukan Generator setelah artikel ditolak.
    # Dipakai Router untuk membatasi loop (0 = masih draft pertama).
    revision_count: NotRequired[int]

    # Prompt untuk image generation
    image_prompt: NotRequired[str]

    # Lokasi file gambar yang dihasilkan
    image_path: NotRequired[str]

    # Lokasi file markdown yang disimpan
    output_path: NotRequired[str]