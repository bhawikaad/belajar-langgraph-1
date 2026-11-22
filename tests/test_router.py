from graph.router import route_after_evaluation


def main():
    approved_state = {
        "topic": "Artificial Intelligence",
        "approved": True,
    }

    rejected_state = {
        "topic": "Artificial Intelligence",
        "approved": False,
    }

    maxed_state = {
        "topic": "Artificial Intelligence",
        "approved": False,
        "revision_count": 2,
    }

    print("Approved:", route_after_evaluation(approved_state))  # approved
    print("Rejected:", route_after_evaluation(rejected_state))  # rejected
    print("Max revisions:", route_after_evaluation(maxed_state))  # max_revisions


if __name__ == "__main__":
    main()