import ollama

from retrieval.retriever import Retriever


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "llama3.2"

# Minimum Cross-Encoder score required before
# sending context to the LLM.
GENERATION_RELEVANCE_THRESHOLD = 2.0

# Exact refusal used by the application.
REFUSAL_MESSAGE = (
    "I could not find this information in the authorized documents."
)


# ============================================================
# GENERATOR
# ============================================================

class Generator:

    def __init__(
        self,
        top_k=3
    ):
        """
        Initialize the RAG generator.
        """

        print(
            "Initializing RAG generator..."
        )

        self.retriever = Retriever(
            top_k=top_k
        )

        print(
            "RAG generator initialized successfully."
        )

    # ========================================================
    # CHECK RELEVANCE
    # ========================================================

    def has_relevant_context(
        self,
        retrieved_results
    ):
        """
        Check whether at least one retrieved chunk
        has a sufficiently strong Cross-Encoder score.
        """

        if not retrieved_results:
            return False

        for result in retrieved_results:

            score = result.get(
                "cross_encoder_score"
            )

            if score is None:
                continue

            if score >= GENERATION_RELEVANCE_THRESHOLD:
                return True

        return False

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    def build_context(
        self,
        retrieved_results
    ):
        """
        Build a clean context string from the
        authorized retrieved documents.
        """

        context_parts = []

        for i, result in enumerate(
            retrieved_results,
            start=1
        ):

            document = result["document"]

            source = document.metadata.get(
                "source",
                "Unknown"
            )

            page = document.metadata.get(
                "page_label",
                "Unknown"
            )

            text = document.page_content.strip()

            context_parts.append(
                f"""
CONTEXT {i}

Source: {source}
Page: {page}

{text}

END CONTEXT {i}
"""
            )

        return "\n".join(
            context_parts
        )

    # ========================================================
    # CREATE PROMPT
    # ========================================================

    def create_prompt(
        self,
        query,
        context
    ):
        """
        Create a grounded generation prompt.
        """

        prompt = f"""
You are an Enterprise Knowledge Assistant.

Answer the user's question ONLY from the document
context provided below.

STRICT RULES:

1. Use only the information in the context.

2. Do not use outside knowledge.

3. Do not invent facts.

4. Do not guess.

5. Do not infer information that is not supported
   by the context.

6. If the context contains relevant information,
   summarize that information clearly.

7. If multiple pieces of information answer the
   question, combine them into one concise answer.

8. The context has already been filtered according
   to the user's authorization.

9. Never reveal information that is not present
   in the context.

10. If the context genuinely does not contain
    information needed to answer the question,
    respond exactly:

I could not find this information in the authorized documents.

IMPORTANT:

For example, if the context contains:

- salary information
- performance review records
- employee personal records

and the user asks about confidential HR information,
those items ARE the answer and should be summarized.

Do not reject an answer merely because the question
uses different wording from the document.

============================================================
AUTHORIZED CONTEXT
============================================================

{context}

============================================================
END CONTEXT
============================================================

USER QUESTION:

{query}

============================================================
ANSWER
============================================================
"""

        return prompt

    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    def generate_answer(
        self,
        query,
        user_role="employee"
    ):
        """
        Retrieve authorized documents and generate
        a grounded answer.
        """

        print(
            "\nRetrieving relevant documents..."
        )

        # ----------------------------------------------------
        # STEP 1 — RETRIEVAL + AUTHORIZATION
        # ----------------------------------------------------

        retrieved_results = (
            self.retriever.retrieve(
                query,
                user_role=user_role
            )
        )

        # ----------------------------------------------------
        # STEP 2 — NO AUTHORIZED DOCUMENTS
        # ----------------------------------------------------

        if not retrieved_results:

            print(
                "No authorized documents found."
            )

            return {
                "answer": REFUSAL_MESSAGE,
                "sources": []
            }

        # ----------------------------------------------------
        # STEP 3 — SHOW AUTHORIZED CONTEXT
        # ----------------------------------------------------

        print(
            "\n" + "=" * 60
        )

        print(
            "AUTHORIZED CONTEXT"
        )

        print(
            "=" * 60
        )

        for i, result in enumerate(
            retrieved_results,
            start=1
        ):

            document = result["document"]

            print(
                f"\nContext {i}"
            )

            print(
                f"Source: "
                f"{document.metadata.get('source', 'Unknown')}"
            )

            print(
                f"Page: "
                f"{document.metadata.get('page_label', 'Unknown')}"
            )

            print(
                f"Similarity: "
                f"{result.get('similarity')}"
            )

            print(
                f"Cross-Encoder Score: "
                f"{result.get('cross_encoder_score')}"
            )

            print(
                "Text:"
            )

            print(
                document.page_content
            )

        # ----------------------------------------------------
        # STEP 4 — RELEVANCE GUARD
        # ----------------------------------------------------

        if not self.has_relevant_context(
            retrieved_results
        ):

            print(
                "\nNo sufficiently relevant authorized "
                "context found."
            )

            return {
                "answer": REFUSAL_MESSAGE,
                "sources": []
            }

        # ----------------------------------------------------
        # STEP 5 — BUILD CONTEXT
        # ----------------------------------------------------

        context = self.build_context(
            retrieved_results
        )

        # ----------------------------------------------------
        # STEP 6 — CREATE PROMPT
        # ----------------------------------------------------

        prompt = self.create_prompt(
            query,
            context
        )

        # ----------------------------------------------------
        # STEP 7 — GENERATE ANSWER
        # ----------------------------------------------------

        print(
            "\nGenerating answer using Llama 3.2..."
        )

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0
            }
        )

        answer = (
            response["message"]["content"]
            .strip()
        )

        # ----------------------------------------------------
        # STEP 8 — BASIC OUTPUT SAFETY
        # ----------------------------------------------------

        # If the model produces an empty response,
        # use the controlled fallback.

        if not answer:

            answer = REFUSAL_MESSAGE

        # ----------------------------------------------------
        # STEP 9 — SOURCES
        # ----------------------------------------------------

        sources = []

        for result in retrieved_results:

            document = result["document"]

            sources.append(
                {
                    "source": document.metadata.get(
                        "source",
                        "Unknown"
                    ),

                    "page": document.metadata.get(
                        "page_label",
                        "Unknown"
                    ),

                    "similarity": result.get(
                        "similarity"
                    ),

                    "cross_encoder_score": result.get(
                        "cross_encoder_score"
                    )
                }
            )

        # ----------------------------------------------------
        # STEP 10 — RETURN
        # ----------------------------------------------------

        return {
            "answer": answer,
            "sources": sources
        }


# ============================================================
# SECURITY TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "SECURE ENTERPRISE RAG GENERATION TEST"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Initialize
    # --------------------------------------------------------

    generator = Generator(
        top_k=3
    )

    # ========================================================
    # TEST 1 — EMPLOYEE
    # ========================================================

    employee_query = (
        "What is the confidential HR information?"
    )

    print(
        "\n" + "#" * 60
    )

    print(
        "TEST 1: EMPLOYEE ACCESS"
    )

    print(
        "#" * 60
    )

    print(
        f"\nQuestion: {employee_query}"
    )

    print(
        "User role: employee"
    )

    employee_result = generator.generate_answer(
        employee_query,
        user_role="employee"
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "EMPLOYEE FINAL ANSWER"
    )

    print(
        "=" * 60
    )

    print(
        employee_result["answer"]
    )

    print(
        "\nEmployee Sources:"
    )

    if not employee_result["sources"]:

        print(
            "No authorized sources found."
        )

    else:

        for source in employee_result["sources"]:

            print(
                f"- {source['source']} "
                f"(Page {source['page']})"
            )

    # ========================================================
    # TEST 2 — HR
    # ========================================================

    hr_query = (
        "What confidential information is contained "
        "in the HR records?"
    )

    print(
        "\n" + "#" * 60
    )

    print(
        "TEST 2: HR ACCESS"
    )

    print(
        "#" * 60
    )

    print(
        f"\nQuestion: {hr_query}"
    )

    print(
        "User role: hr"
    )

    hr_result = generator.generate_answer(
        hr_query,
        user_role="hr"
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "HR FINAL ANSWER"
    )

    print(
        "=" * 60
    )

    print(
        hr_result["answer"]
    )

    print(
        "\nHR Sources:"
    )

    if not hr_result["sources"]:

        print(
            "No authorized sources found."
        )

    else:

        for source in hr_result["sources"]:

            print(
                f"- {source['source']} "
                f"(Page {source['page']})"
            )

    # ========================================================
    # SECURITY SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "SECURITY TEST SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        "\nEmployee Answer:"
    )

    print(
        employee_result["answer"]
    )

    print(
        "\nHR Answer:"
    )

    print(
        hr_result["answer"]
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "GENERATION SECURITY TEST COMPLETE"
    )

    print(
        "=" * 60
    )