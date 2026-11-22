"""
Mencoba human-in-the-loop (interrupt + Command(resume)) dengan agent palsu,
tanpa panggilan LLM dan tanpa input() dari terminal.
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


def run_case(human_answer: bool, tmp: str):
    workflow = create_workflow(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": f"tes-{human_answer}"}}

    # Tahap 1: jalan sampai berhenti di human_review.
    workflow.invoke({"topic": "Tes Human Review"}, config)
    snapshot = workflow.get_state(config)
    assert snapshot.next == ("human_review",), snapshot.next
    assert "output_path" not in snapshot.values  # belum disimpan
    payload = snapshot.tasks[0].interrupts[0].value
    print(f"  berhenti di {snapshot.next}, payload: {sorted(payload)}")

    # Tahap 2: manusia menjawab, graph dilanjutkan.
    final = workflow.invoke(Command(resume=human_answer), config)
    return final


def main():
    nodes.OrchestratorAgent = FakeOrchestrator
    nodes.GeneratorAgent = FakeGenerator
    nodes.EvaluatorAgent = FakeEvaluator
    nodes.ImagePromptAgent = FakeImagePrompt

    with tempfile.TemporaryDirectory() as tmp:
        nodes.save_article = lambda topic, article: save_article(topic, article, Path(tmp))

        print("Kasus: manusia setuju")
        final = run_case(True, tmp)
        assert final["human_approved"] is True
        assert Path(final["output_path"]).exists()
        print("  tersimpan:", Path(final["output_path"]).name)

        print("Kasus: manusia menolak")
        final = run_case(False, tmp)
        assert final["human_approved"] is False
        assert "output_path" not in final
        print("  tidak tersimpan")

    print("OK")


if __name__ == "__main__":
    main()
