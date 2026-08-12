from sentence_transformers import SentenceTransformer
from vector_store.faiss_store import FAISSVectorStore
# Same embedding model used when creating the FAISS index
MODEL_NAME = "all-MiniLM-L6-v2"
# Existing FAISS files

INDEX_PATH = "vector_store/faiss_index.bin"
METADATA_PATH = "vector_store/metadata.pkl"

class Retriever:

    def __init__(self, top_k=5):
        """
        Initialize the retriever.

        Args:
            top_k: Number of relevant chunks to retrieve.
        """

        self.top_k = top_k

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        print("Embedding model loaded.")

        # Load existing FAISS index
        print("Loading FAISS vector store...")

        self.vector_store = FAISSVectorStore(
            dimension=384
        )

        self.vector_store.load(
            INDEX_PATH,
            METADATA_PATH
        )

        print("FAISS vector store loaded.")
        print(
            f"Total vectors: "
            f"{self.vector_store.index.ntotal}"
        )

    def retrieve(self, query):
        """
        Retrieve the most relevant document chunks.

        Args:
            query: User's question.

        Returns:
            List of relevant document chunks.
        """

        # Convert user question into embedding
        query_embedding = self.model.encode(
            query,
            convert_to_numpy=True
        )

        # Search FAISS
        results = self.vector_store.search(
            query_embedding,
            k=self.top_k
        )

        return results


if __name__ == "__main__":

    print("=" * 60)
    print("RETRIEVAL TEST")
    print("=" * 60)

    retriever = Retriever(top_k=3)

    query = "What is the company's leave policy?"

    print(f"\nQuery: {query}")

    results = retriever.retrieve(query)

    print("\n" + "=" * 60)
    print("RETRIEVED RESULTS")
    print("=" * 60)

    for i, result in enumerate(results, start=1):

        document = result["document"]
        distance = result["distance"]

        print(f"\n--- Result {i} ---")
        print(f"Distance: {distance}")

        print("\nContent:")
        print(document.page_content)

        print("\nMetadata:")
        print(document.metadata)