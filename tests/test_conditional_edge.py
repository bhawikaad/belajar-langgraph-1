from langgraph.graph import StateGraph, START, END

from graph.state import ArticleState
from graph.router import route_after_evaluation


def approved_node(state: ArticleState):
    print("→ Approved path")
    return {}


def rejected_node(state: ArticleState):
    print("→ Rejected path")
    return {}


def create_test_graph():
    graph = StateGraph(ArticleState)

    graph.add_node("approved", approved_node)
    graph.add_node("rejected", rejected_node)

    graph.add_conditional_edges(
        START,
        route_after_evaluation,
        {
            "approved": "approved",
            "rejected": "rejected",
        },
    )

    graph.add_edge("approved", END)
    graph.add_edge("rejected", END)

    return graph.compile()


def main():
    graph = create_test_graph()

    print("Test approved=True")
    graph.invoke({
        "topic": "LangGraph",
        "approved": True,
    })

    print()

    print("Test approved=False")
    graph.invoke({
        "topic": "LangGraph",
        "approved": False,
    })


if __name__ == "__main__":
    main()