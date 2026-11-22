from models.evaluation import EvaluationResult


def main():
    result = EvaluationResult(
        score=8,
        feedback="Artikel cukup baik.",
        approved=True,
    )

    print("=== Valid Result ===")
    print(result)
    print(type(result))
    print(result.score)
    print(result.feedback)
    print(result.approved)


if __name__ == "__main__":
    main()