import json
from pathlib import Path

from generation.generator import Generator


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = Path(
    "evaluation/evaluation_dataset.json"
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():
    """
    Load evaluation questions and expected answers.
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
    Convert a complete document path into
    filename only.
    """

    return Path(source).name.lower()


# ============================================================
# GET RETRIEVED SOURCES
# ============================================================

def get_retrieved_sources(result):
    """
    Extract unique source filenames from
    generator results.
    """

    sources = []

    seen = set()

    for source_info in result.get(
        "sources",
        []
    ):

        source = source_info.get(
            "source",
            ""
        )

        source = normalize_source(
            source
        )

        if not source:
            continue

        if source in seen:
            continue

        seen.add(source)

        sources.append(source)

    return sources


# ============================================================
# CHECK SOURCE
# ============================================================

def check_source(
    retrieved_sources,
    expected_source
):
    """
    Check whether the expected source
    was retrieved.
    """

    if expected_source is None:

        return len(
            retrieved_sources
        ) == 0

    expected_source = (
        expected_source.lower()
    )

    return (
        expected_source
        in retrieved_sources
    )


# ============================================================
# SIMPLE KEYWORD OVERLAP
# ============================================================

def calculate_keyword_overlap(
    answer,
    expected_answer
):
    """
    Calculate a simple word-overlap score.

    This is NOT a semantic evaluation.
    It is only a basic supporting metric.
    """

    if not answer or not expected_answer:

        return 0.0

    answer_words = set(
        answer.lower()
        .replace(".", " ")
        .replace(",", " ")
        .replace(":", " ")
        .split()
    )

    expected_words = set(
        expected_answer.lower()
        .replace(".", " ")
        .replace(",", " ")
        .replace(":", " ")
        .split()
    )

    # Remove very short/common words
    answer_words = {
        word
        for word in answer_words
        if len(word) > 3
    }

    expected_words = {
        word
        for word in expected_words
        if len(word) > 3
    }

    if not expected_words:

        return 0.0

    overlap = (
        answer_words
        & expected_words
    )

    return (
        len(overlap)
        / len(expected_words)
    )


# ============================================================
# GENERATION EVALUATION
# ============================================================

def evaluate_generation():

    print("=" * 70)
    print("RAG ANSWER-LEVEL EVALUATION")
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
    # Initialize generator
    # --------------------------------------------------------

    print(
        "\nInitializing RAG generator..."
    )

    generator = Generator(
        top_k=3
    )

    print(
        "Generator initialized."
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    answerable_questions = 0

    source_hits = 0

    no_answer_correct = 0

    keyword_scores = []

    # ========================================================
    # EVALUATE EACH QUESTION
    # ========================================================

    for index, item in enumerate(
        dataset,
        start=1
    ):

        question = item["question"]

        expected_source = (
            item["expected_source"]
        )

        expected_answer = (
            item.get(
                "expected_answer"
            )
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
        # Generate answer
        # ----------------------------------------------------

        try:

            result = generator.generate_answer(
                question
            )

        except Exception as e:

            print(
                f"Generation failed: {e}"
            )

            continue

        # ----------------------------------------------------
        # Extract answer
        # ----------------------------------------------------

        answer = result.get(
            "answer",
            ""
        )

        print(
            "\nGenerated answer:"
        )

        print(
            answer
        )

        # ----------------------------------------------------
        # Retrieved sources
        # ----------------------------------------------------

        retrieved_sources = (
            get_retrieved_sources(
                result
            )
        )

        print(
            "\nRetrieved sources:"
        )

        print(
            retrieved_sources
        )

        # ====================================================
        # NO-ANSWER CASE
        # ====================================================

        if expected_source is None:

            no_answer_message = (
                "could not find"
                in answer.lower()
                or
                "cannot find"
                in answer.lower()
                or
                "not found"
                in answer.lower()
            )

            if (
                not retrieved_sources
                and no_answer_message
            ):

                no_answer_correct += 1

                print(
                    "No-answer behavior: PASS"
                )

            else:

                print(
                    "No-answer behavior: REVIEW"
                )

            continue

        # ====================================================
        # NORMAL ANSWER
        # ====================================================

        answerable_questions += 1

        # ----------------------------------------------------
        # Source grounding check
        # ----------------------------------------------------

        source_found = check_source(
            retrieved_sources,
            expected_source
        )

        if source_found:

            source_hits += 1

            print(
                "Expected source retrieved: YES"
            )

        else:

            print(
                "Expected source retrieved: NO"
            )

        # ----------------------------------------------------
        # Keyword overlap
        # ----------------------------------------------------

        if expected_answer:

            overlap = (
                calculate_keyword_overlap(
                    answer,
                    expected_answer
                )
            )

            keyword_scores.append(
                overlap
            )

            print(
                f"Keyword overlap: "
                f"{overlap:.3f}"
            )

    # ========================================================
    # FINAL METRICS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL ANSWER EVALUATION RESULTS"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Source grounding rate
    # --------------------------------------------------------

    if answerable_questions > 0:

        source_grounding_rate = (
            source_hits
            / answerable_questions
        )

    else:

        source_grounding_rate = 0.0

    # --------------------------------------------------------
    # Average keyword overlap
    # --------------------------------------------------------

    if keyword_scores:

        average_keyword_overlap = (
            sum(keyword_scores)
            / len(keyword_scores)
        )

    else:

        average_keyword_overlap = 0.0

    # --------------------------------------------------------
    # No-answer accuracy
    # --------------------------------------------------------

    no_answer_questions = sum(
        1
        for item in dataset
        if item["expected_source"] is None
    )

    if no_answer_questions > 0:

        no_answer_accuracy = (
            no_answer_correct
            / no_answer_questions
        )

    else:

        no_answer_accuracy = 0.0

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print(
        f"\nAnswerable questions: "
        f"{answerable_questions}"
    )

    print(
        f"Source grounding rate: "
        f"{source_grounding_rate:.3f}"
    )

    print(
        f"Average keyword overlap: "
        f"{average_keyword_overlap:.3f}"
    )

    print(
        f"No-answer accuracy: "
        f"{no_answer_accuracy:.3f}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "ANSWER EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluate_generation()