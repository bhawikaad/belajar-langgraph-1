from agents.evaluator import EvaluatorAgent


def main():
    state = {
        "topic": "Artificial Intelligence",
        "article": """
Artificial Intelligence is changing the way people work.
It can help automate repetitive tasks and assist humans
in analyzing large amounts of information.
"""
    }

    evaluator = EvaluatorAgent()

    result = evaluator.run(state)

    print("=== Evaluator Result ===")
    print(result)


if __name__ == "__main__":
    main()