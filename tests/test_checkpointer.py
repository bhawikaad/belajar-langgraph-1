"""
Mencoba checkpointer dengan agent palsu (tanpa panggilan LLM),
sehingga cepat dan tidak butuh API key yang aktif.
"""

import tempfile
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

import graph.nodes as nodes
from graph.workflow import create_workflow
from services.storage import save_article


class FakeOrchestrator:
    def run(self, state):
        return {"outline": "outline palsu"}


class FakeGenerator:
    def run(self, state):
        return {"article": "artikel palsu"}


class FakeEvaluator:
    def run(self, state):
        return {"feedback": "bagus", "approved": True}


class FakeImagePrompt:
    def run(self, state):
        return {"image_prompt": "prompt gambar palsu"}


def main():
    # Ganti agent asli dengan palsu. graph.nodes memanggil nama-nama ini
    # saat node dijalankan, jadi patch di modul nodes sudah cukup.
    nodes.OrchestratorAgent = FakeOrchestrator
    nodes.GeneratorAgent = FakeGenerator
    nodes.EvaluatorAgent = FakeEvaluator
    nodes.ImagePromptAgent = FakeImagePrompt

    # Simpan file ke folder sementara supaya output/ asli tidak terisi.
    with tempfile.TemporaryDirectory() as tmp:
        nodes.save_article = lambda topic, article: save_article(topic, article, Path(tmp))

        workflow = create_workflow(checkpointer=InMemorySaver())
        config = {"configurable": {"thread_id": "tes-1"}}

        workflow.invoke({"topic": "Tes Checkpointer"}, config)
        # Graph berhenti di human_review; lanjutkan dengan persetujuan.
        workflow.invoke(Command(resume=True), config)

        # Snapshot terbaru = state akhir. get_state() membacanya dari checkpointer.
        final = workflow.get_state(config)
        print("State akhir tersimpan:", sorted(final.values))
        print("Node berikutnya (kosong = selesai):", final.next)

        print("\nRiwayat checkpoint (terlama -> terbaru):")
        for snapshot in reversed(list(workflow.get_state_history(config))):
            print(f"  step {snapshot.metadata['step']}: next={snapshot.next}")


if __name__ == "__main__":
    main()
