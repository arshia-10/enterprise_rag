from pathlib import Path

from sentence_transformers import SentenceTransformer, CrossEncoder

from vector_store.faiss_store import FAISSVectorStore

from app.security.authorization import (
    filter_authorized_results
)


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

RERANKER_MODEL_NAME = (
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

INDEX_PATH = "vector_store/faiss_index.bin"
METADATA_PATH = "vector_store/metadata.pkl"


# ============================================================
# RETRIEVER
# ============================================================

class Retriever:

    def __init__(
        self,
        top_k=5,
        similarity_threshold=0.45,
        candidate_multiplier=3,
        mmr_lambda=0.7,
        rerank_top_n=3
    ):
        """
        Optimized enterprise RAG retriever.

        Pipeline:

        Query
          ↓
        Embedding
          ↓
        FAISS
          ↓
        Similarity filtering
          ↓
        Authorization
          ↓
        MMR
          ↓
        Cross-Encoder reranking
          ↓
        Final chunks
        """

        self.top_k = top_k

        self.similarity_threshold = (
            similarity_threshold
        )

        self.candidate_multiplier = (
            candidate_multiplier
        )

        self.mmr_lambda = mmr_lambda

        self.rerank_top_n = rerank_top_n

        # ----------------------------------------------------
        # Embedding model
        # ----------------------------------------------------

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

        print("Embedding model loaded.")

        # ----------------------------------------------------
        # Cross-Encoder
        # ----------------------------------------------------

        print(
            "Loading Cross-Encoder reranker..."
        )

        self.reranker = CrossEncoder(
            RERANKER_MODEL_NAME
        )

        print(
            "Cross-Encoder reranker loaded."
        )

        # ----------------------------------------------------
        # FAISS
        # ----------------------------------------------------

        print(
            "Loading FAISS vector store..."
        )

        self.vector_store = FAISSVectorStore(
            dimension=384
        )

        self.vector_store.load(
            INDEX_PATH,
            METADATA_PATH
        )

        print(
            "Retriever initialized successfully."
        )

        print(
            f"Total vectors available: "
            f"{self.vector_store.index.ntotal}"
        )

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(self):
        """
        Reload the latest FAISS index and metadata.
        """

        print(
            "\nRefreshing FAISS vector store..."
        )

        self.vector_store = FAISSVectorStore(
            dimension=384
        )

        self.vector_store.load(
            INDEX_PATH,
            METADATA_PATH
        )

        print(
            "Retriever refreshed successfully."
        )

        print(
            f"Total vectors available: "
            f"{self.vector_store.index.ntotal}"
        )

    # ========================================================
    # MMR
    # ========================================================

    def _mmr(
        self,
        results,
        top_k
    ):
        """
        Maximal Marginal Relevance.

        Balances:
        - relevance to query
        - diversity between chunks
        """

        if not results:

            return []

        if len(results) <= top_k:

            return results

        selected = []

        remaining = list(results)

        # ----------------------------------------------------
        # Select first most relevant result
        # ----------------------------------------------------

        first = max(
            remaining,
            key=lambda x: x["similarity"]
        )

        selected.append(first)

        remaining.remove(first)

        # ----------------------------------------------------
        # Select remaining chunks
        # ----------------------------------------------------

        while (
            remaining
            and len(selected) < top_k
        ):

            best_result = None

            best_score = float("-inf")

            for candidate in remaining:

                relevance = (
                    candidate["similarity"]
                )

                # ------------------------------------------------
                # Approximate text similarity for diversity
                # ------------------------------------------------

                candidate_words = set(
                    candidate["document"]
                    .page_content
                    .lower()
                    .split()
                )

                max_similarity = 0.0

                for selected_result in selected:

                    selected_words = set(
                        selected_result["document"]
                        .page_content
                        .lower()
                        .split()
                    )

                    if (
                        not candidate_words
                        or not selected_words
                    ):

                        text_similarity = 0.0

                    else:

                        intersection = (
                            candidate_words
                            & selected_words
                        )

                        union = (
                            candidate_words
                            | selected_words
                        )

                        text_similarity = (
                            len(intersection)
                            / len(union)
                        )

                    max_similarity = max(
                        max_similarity,
                        text_similarity
                    )

                # ------------------------------------------------
                # MMR score
                # ------------------------------------------------

                mmr_score = (
                    self.mmr_lambda
                    * relevance
                    - (
                        1 - self.mmr_lambda
                    )
                    * max_similarity
                )

                if mmr_score > best_score:

                    best_score = mmr_score

                    best_result = candidate

                    best_result[
                        "mmr_score"
                    ] = mmr_score

            if best_result is None:

                break

            selected.append(
                best_result
            )

            remaining.remove(
                best_result
            )

        return selected

    # ========================================================
    # RETRIEVE
    # ========================================================

    def retrieve(
        self,
        query,
        user_role="employee"
    ):
        """
        Retrieve authorized and relevant
        document chunks.

        Args:
            query:
                User question.

            user_role:
                Current user's role.

        Returns:
            List of authorized ranked chunks.
        """

        print(
            f"\nRetrieving for role: "
            f"{user_role}"
        )

        # ----------------------------------------------------
        # STEP 1: Query embedding
        # ----------------------------------------------------

        query_embedding = self.model.encode(
            query,
            convert_to_numpy=True
        )

        # ----------------------------------------------------
        # STEP 2: FAISS candidate retrieval
        # ----------------------------------------------------

        candidate_k = (
            self.top_k
            * self.candidate_multiplier
        )

        print(
            f"Retrieving "
            f"{candidate_k} candidate chunks..."
        )

        results = self.vector_store.search(
            query_embedding,
            k=candidate_k,
            similarity_threshold=(
                self.similarity_threshold
            )
        )

        print(
            f"Candidates after similarity "
            f"filtering: {len(results)}"
        )

        # ----------------------------------------------------
        # STEP 3: AUTHORIZATION FILTER
        # ----------------------------------------------------

        authorized_results = (
            filter_authorized_results(
                results,
                user_role
            )
        )

        print(
            f"Candidates after authorization: "
            f"{len(authorized_results)}"
        )

        # ----------------------------------------------------
        # STEP 4: Remove duplicate chunks
        # ----------------------------------------------------

        unique_results = []

        seen_texts = set()

        for result in authorized_results:

            document = result["document"]

            text = (
                document
                .page_content
                .strip()
            )

            if text in seen_texts:

                continue

            seen_texts.add(text)

            unique_results.append(
                result
            )

        print(
            f"Candidates after duplicate "
            f"removal: {len(unique_results)}"
        )

        # ----------------------------------------------------
        # STEP 5: MMR
        # ----------------------------------------------------

        mmr_results = self._mmr(
            unique_results,
            self.top_k
        )

        print(
            f"Final chunks selected by MMR: "
            f"{len(mmr_results)}"
        )

        # ----------------------------------------------------
        # STEP 6: CROSS-ENCODER
        # ----------------------------------------------------

        if not mmr_results:

            print(
                "No authorized relevant "
                "documents found."
            )

            return []

        print(
            "Running Cross-Encoder reranking..."
        )

        pairs = []

        for result in mmr_results:

            document = result["document"]

            pairs.append(
                (
                    query,
                    document.page_content
                )
            )

        scores = self.reranker.predict(
            pairs
        )

        # ----------------------------------------------------
        # Attach Cross-Encoder scores
        # ----------------------------------------------------

        for result, score in zip(
            mmr_results,
            scores
        ):

            result[
                "cross_encoder_score"
            ] = float(score)

        # ----------------------------------------------------
        # Sort by Cross-Encoder score
        # ----------------------------------------------------

        reranked_results = sorted(
            mmr_results,
            key=lambda x: x[
                "cross_encoder_score"
            ],
            reverse=True
        )

        # ----------------------------------------------------
        # Final top N
        # ----------------------------------------------------

        reranked_results = (
            reranked_results[
                :self.rerank_top_n
            ]
        )

        print(
            f"Final chunks after "
            f"Cross-Encoder: "
            f"{len(reranked_results)}"
        )

        return reranked_results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SECURE OPTIMIZED RETRIEVER TEST")
    print("=" * 60)

    retriever = Retriever(
        top_k=3,
        similarity_threshold=0.45,
        candidate_multiplier=3,
        mmr_lambda=0.7,
        rerank_top_n=3
    )

    # --------------------------------------------------------
    # Test query
    # --------------------------------------------------------

    query = (
        "What are the access control rules?"
    )

    # --------------------------------------------------------
    # Test as employee
    # --------------------------------------------------------

    user_role = "employee"

    print(
        f"\nQuery: {query}"
    )

    print(
        f"User role: {user_role}"
    )

    results = retriever.retrieve(
        query,
        user_role=user_role
    )

    print(
        f"\nFinal relevant chunks: "
        f"{len(results)}"
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "FINAL SECURE RETRIEVED RESULTS"
    )

    print(
        "=" * 60
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        document = result["document"]

        print(
            f"\nResult {i}"
        )

        print(
            f"FAISS Similarity: "
            f"{result['similarity']:.4f}"
        )

        print(
            f"Cross-Encoder Score: "
            f"{result['cross_encoder_score']:.4f}"
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
            f"Text: "
            f"{document.page_content[:300]}..."
        )

    print(
        "\n" + "=" * 60
    )

    print(
        "SECURE RETRIEVER TEST COMPLETE"
    )

    print(
        "=" * 60
    )