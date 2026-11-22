from agents.generator import GeneratorAgent


def main():
    state = {
        "topic": "Pengenalan LangGraph",
        "outline": """
# Pendahuluan
# Apa itu LangGraph
# Kelebihan LangGraph
# Kesimpulan
"""
    }

    agent = GeneratorAgent()
    result = agent.run(state)

    print("=" * 80)
    print(result["article"])
    print("=" * 80)


if __name__ == "__main__":
    main()