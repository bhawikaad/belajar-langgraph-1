"""
Membuktikan checkpoint SQLite tetap ada setelah koneksi ditutup,
memakai agent palsu (tanpa panggilan LLM).
"""

import tempfile
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
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
    nodes.OrchestratorAgent = FakeOrchestrator
    nodes.GeneratorAgent = FakeGenerator
    nodes.EvaluatorAgent = FakeEvaluator
    nodes.ImagePromptAgent = FakeImagePrompt

    with tempfile.TemporaryDirectory() as tmp:
        nodes.save_article = lambda topic, article, **extra: save_article(topic, article, Path(tmp), **extra)
        db_path = str(Path(tmp) / "tes.db")
        config = {"configurable": {"thread_id": "tes-sqlite"}}

        # Koneksi 1: jalankan workflow, lalu tutup koneksi (keluar dari `with`).
        with SqliteSaver.from_conn_string(db_path) as saver:
            workflow = create_workflow(checkpointer=saver)
            workflow.invoke({"topic": "Tes SQLite"}, config)
            # Graph berhenti di human_review; lanjutkan dengan persetujuan.
            workflow.invoke(Command(resume=True), config)
        print("Run selesai, koneksi 1 ditutup.")

        # Koneksi 2: buka database yang sama sebagai "proses baru".
        with SqliteSaver.from_conn_string(db_path) as saver:
            workflow = create_workflow(checkpointer=saver)
            snapshot = workflow.get_state(config)
            print("State terbaca dari disk:", sorted(snapshot.values))
            print("Jumlah checkpoint:", len(list(workflow.get_state_history(config))))
            assert snapshot.values["article"] == "artikel palsu"
            assert snapshot.next == ()

        print("OK")


if __name__ == "__main__":
    main()
