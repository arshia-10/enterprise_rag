import json
from pathlib import Path

from retrieval.retriever import Retriever


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = Path(
    "evaluation/evaluation_dataset.json"
)

TOP_K = 3


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():
    """
    Load evaluation questions from JSON.
    """

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# NORMALIZE SOURCE
# ============================================================

def normalize_source(source):
    """
    Convert complete document path into
    filename only.

    Example:

    documents\\it_security_policy.pdf

    becomes:

    it_security_policy.pdf
    """

    return Path(source).name.lower()


# ============================================================
# GET UNIQUE SOURCES
# ============================================================

def get_unique_sources(results):
    """
    Extract unique document sources.

    Multiple chunks from the same PDF are counted
    as one document.
    """

    unique_sources = []

    seen_sources = set()

    for result in results:

        document = result["document"]

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        source = normalize_source(
            source
        )

        if source in seen_sources:
            continue

        seen_sources.add(source)

        unique_sources.append(
            source
        )

    return unique_sources


# ============================================================
# RECIPROCAL RANK
# ============================================================

def reciprocal_rank(
    retrieved_sources,
    expected_source
):
    """
    Calculate Reciprocal Rank.

    Rank 1 -> 1.0
    Rank 2 -> 0.5
    Rank 3 -> 0.333

    Not found -> 0.0
    """

    if expected_source is None:

        return None

    expected_source = (
        expected_source.lower()
    )

    for rank, source in enumerate(
        retrieved_sources,
        start=1
    ):

        if source == expected_source:

            return 1.0 / rank

    return 0.0


# ============================================================
# EVALUATE RETRIEVAL
# ============================================================

def evaluate_retrieval():

    print("=" * 70)
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    dataset = load_dataset()

    print(
        f"\nEvaluation questions: "
        f"{len(dataset)}"
    )

    # --------------------------------------------------------
    # Initialize retriever
    # --------------------------------------------------------

    retriever = Retriever(
        top_k=TOP_K,
        similarity_threshold=0.45,
        candidate_multiplier=3,
        mmr_lambda=0.7,
        rerank_top_n=TOP_K
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    evaluated_questions = 0

    hit_count = 0

    precision_scores = []

    reciprocal_ranks = []

    # ========================================================
    # PROCESS EACH QUESTION
    # ========================================================

    for index, item in enumerate(
        dataset,
        start=1
    ):

        question = item["question"]

        expected_source = (
            item["expected_source"]
        )

        print(
            "\n" + "-" * 70
        )

        print(
            f"Question {index}: "
            f"{question}"
        )

        print(
            f"Expected source: "
            f"{expected_source}"
        )

        # ----------------------------------------------------
        # Retrieve chunks
        # ----------------------------------------------------

        results = retriever.retrieve(
            question
        )

        # ----------------------------------------------------
        # Convert chunks to unique documents
        # ----------------------------------------------------

        retrieved_sources = (
            get_unique_sources(
                results
            )
        )

        # Keep only top K unique documents
        retrieved_sources = (
            retrieved_sources[:TOP_K]
        )

        print(
            f"Retrieved unique sources: "
            f"{retrieved_sources}"
        )

        # ====================================================
        # NO-ANSWER QUESTION
        # ====================================================

        if expected_source is None:

            if not retrieved_sources:

                print(
                    "Result: PASS "
                    "(No relevant source found)"
                )

            else:

                print(
                    "Result: REVIEW "
                    "(Documents were retrieved)"
                )

            continue

        # ====================================================
        # NORMAL QUESTION
        # ====================================================

        evaluated_questions += 1

        expected_source = (
            expected_source.lower()
        )

        # ----------------------------------------------------
        # HIT
        # ----------------------------------------------------

        if expected_source in (
            retrieved_sources
        ):

            hit_count += 1

            print(
                "Hit: YES"
            )

        else:

            print(
                "Hit: NO"
            )

        # ----------------------------------------------------
        # PRECISION@K
        # ----------------------------------------------------

        if len(retrieved_sources) > 0:

            relevant_count = 0

            for source in retrieved_sources:

                if source == expected_source:

                    relevant_count += 1

            precision = (
                relevant_count
                / len(retrieved_sources)
            )

        else:

            precision = 0.0

        precision_scores.append(
            precision
        )

        # ----------------------------------------------------
        # RECIPROCAL RANK
        # ----------------------------------------------------

        rr = reciprocal_rank(
            retrieved_sources,
            expected_source
        )

        reciprocal_ranks.append(
            rr
        )

        # ----------------------------------------------------
        # Display metrics
        # ----------------------------------------------------

        print(
            f"Precision@{TOP_K}: "
            f"{precision:.3f}"
        )

        print(
            f"Reciprocal Rank: "
            f"{rr:.3f}"
        )

    # ========================================================
    # FINAL METRICS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL EVALUATION RESULTS"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if evaluated_questions == 0:

        print(
            "\nNo answerable questions "
            "were evaluated."
        )

        return

    # --------------------------------------------------------
    # Hit Rate
    # --------------------------------------------------------

    hit_rate = (
        hit_count
        / evaluated_questions
    )

    # --------------------------------------------------------
    # Mean Precision
    # --------------------------------------------------------

    mean_precision = (
        sum(precision_scores)
        / len(precision_scores)
    )

    # --------------------------------------------------------
    # Mean Reciprocal Rank
    # --------------------------------------------------------

    mrr = (
        sum(reciprocal_ranks)
        / len(reciprocal_ranks)
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print(
        f"\nQuestions evaluated: "
        f"{evaluated_questions}"
    )

    print(
        f"Hit Rate: "
        f"{hit_rate:.3f}"
    )

    print(
        f"Precision@{TOP_K}: "
        f"{mean_precision:.3f}"
    )

    print(
        f"MRR: "
        f"{mrr:.3f}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluate_retrieval()