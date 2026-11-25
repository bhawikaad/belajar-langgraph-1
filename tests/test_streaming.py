"""
Mencoba stream_mode="updates" dengan agent palsu (tanpa panggilan LLM).
Evaluator palsu menolak sekali lalu menerima, agar loop revisi terlihat di stream.
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
        revision = state.get("revision_count", 0)
        # Revisi pertama (ada feedback) menaikkan revision_count, seperti agent asli.
        if state.get("feedback"):
            return {"article": "artikel revisi", "revision_count": revision + 1}
        return {"article": "artikel awal"}


class FakeEvaluator:
    def __init__(self):
        self.calls = 0

    def run(self, state):
        self.calls += 1
        return {"feedback": f"feedback {self.calls}", "approved": self.calls >= 2}


class FakeImagePrompt:
    def run(self, state):
        return {"image_prompt": "prompt gambar palsu"}


def main():
    evaluator = FakeEvaluator()
    nodes.OrchestratorAgent = FakeOrchestrator
    nodes.GeneratorAgent = FakeGenerator
    nodes.EvaluatorAgent = lambda: evaluator
    nodes.ImagePromptAgent = FakeImagePrompt

    with tempfile.TemporaryDirectory() as tmp:
        nodes.save_article = lambda topic, article, **extra: save_article(topic, article, Path(tmp), **extra)

        workflow = create_workflow(checkpointer=InMemorySaver())
        config = {"configurable": {"thread_id": "tes-stream"}}

        order = []

        def consume(graph_input):
            for update in workflow.stream(graph_input, config, stream_mode="updates"):
                for node_name, changes in update.items():
                    order.append(node_name)
                    print(f"[{node_name}] mengubah: {sorted(changes)}")

        consume({"topic": "Tes Streaming"})
        # Berhenti di human_review (muncul sebagai "__interrupt__"); lanjutkan.
        consume(Command(resume=True))

        expected = [
            "orchestrator", "generator", "evaluator",
            "generator", "evaluator", "image_prompt",
            "__interrupt__", "human_review", "save",
        ]
        assert order == expected, order
        print("OK, urutan node:", " -> ".join(order))


if __name__ == "__main__":
    main()
