"""
Mencoba human-in-the-loop (interrupt + Command(resume)) dengan agent palsu,
tanpa panggilan LLM dan tanpa input() dari terminal.

Alur yang diuji:
- manusia setuju       -> artikel disimpan
- manusia menolak      -> artikel ditulis ulang (kembali ke generator), lalu
                          graph menunggu persetujuan lagi
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
        # Seperti agent asli: ada feedback + draft lama = mode revisi.
        if state.get("feedback") and state.get("article"):
            return {
                "article": "artikel revisi: " + state["feedback"],
                "revision_count": state.get("revision_count", 0) + 1,
            }
        return {"article": "artikel palsu"}


class FakeEvaluator:
    def run(self, state):
        return {"feedback": "bagus", "approved": True}


class FakeImagePrompt:
    def run(self, state):
        return {"image_prompt": "prompt gambar palsu"}


def start(thread_id: str):
    """Jalankan graph sampai berhenti di human_review; kembalikan (workflow, config)."""
    workflow = create_workflow(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": thread_id}}

    workflow.invoke({"topic": "Tes Human Review"}, config)

    snapshot = workflow.get_state(config)
    assert snapshot.next == ("human_review",), snapshot.next
    assert "output_path" not in snapshot.values  # belum disimpan
    return workflow, config


def main():
    nodes.OrchestratorAgent = FakeOrchestrator
    nodes.GeneratorAgent = FakeGenerator
    nodes.EvaluatorAgent = FakeEvaluator
    nodes.ImagePromptAgent = FakeImagePrompt

    with tempfile.TemporaryDirectory() as tmp:
        # **extra meneruskan keyword apa pun dari save_node (outline, image_prompt, ...)
        # ke fungsi asli, tapi menyimpan ke folder sementara.
        nodes.save_article = lambda topic, article, **extra: save_article(
            topic, article, Path(tmp), **extra
        )

        print("Kasus 1: manusia setuju")
        workflow, config = start("setuju")
        final = workflow.invoke(Command(resume={"approved": True}), config)
        assert final["human_approved"] is True
        content = Path(final["output_path"]).read_text(encoding="utf-8")
        assert "**Topik:** Tes Human Review" in content
        assert "outline palsu" in content
        assert "### Prompt Gambar" in content
        assert "prompt gambar palsu" in content
        assert content.rstrip().endswith("artikel palsu")
        print("  tersimpan:", Path(final["output_path"]).name)

        print("Kasus 2: manusia menolak dengan catatan, lalu setuju")
        workflow, config = start("tolak-catatan")
        workflow.invoke(
            Command(resume={"approved": False, "note": "perbaiki intro"}), config
        )

        # Setelah ditolak: generator menulis ulang, evaluator + image_prompt
        # berjalan lagi, lalu graph berhenti di human_review LAGI.
        snapshot = workflow.get_state(config)
        assert snapshot.next == ("human_review",), snapshot.next
        assert snapshot.values["article"] == "artikel revisi: perbaiki intro"
        assert snapshot.values["revision_count"] == 1  # direset 0 lalu +1 oleh generator
        assert "output_path" not in snapshot.values  # belum disimpan
        print("  ditulis ulang:", snapshot.values["article"])

        final = workflow.invoke(Command(resume={"approved": True}), config)
        content = Path(final["output_path"]).read_text(encoding="utf-8")
        assert content.rstrip().endswith("artikel revisi: perbaiki intro")
        print("  setelah setuju, tersimpan versi revisi")

        print("Kasus 3: menolak tanpa catatan memakai catatan bawaan")
        workflow, config = start("tolak-tanpa-catatan")
        workflow.invoke(Command(resume={"approved": False, "note": "  "}), config)
        article = workflow.get_state(config).values["article"]
        assert "rejected this draft" in article, article
        print("  ditulis ulang dengan catatan bawaan")

        print("Kasus 4: format lama (bool) tetap didukung")
        workflow, config = start("bool")
        workflow.invoke(Command(resume=False), config)
        assert workflow.get_state(config).next == ("human_review",)
        final = workflow.invoke(Command(resume=True), config)
        assert Path(final["output_path"]).exists()
        print("  False menolak, True menyetujui")

    print("OK")


if __name__ == "__main__":
    main()
