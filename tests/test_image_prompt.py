from agents.image_prompt import ImagePromptAgent


def main():
    state = {
        "topic": "Artificial Intelligence",
        "article": """
# Artificial Intelligence di Tempat Kerja

Artificial Intelligence membantu mengotomatisasi tugas berulang
dan menganalisis data dalam jumlah besar.
""",
    }

    agent = ImagePromptAgent()

    result = agent.run(state)

    print("=== Image Prompt Result ===")
    print(result)


if __name__ == "__main__":
    main()
