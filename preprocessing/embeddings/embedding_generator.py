from sentence_transformers import SentenceTransformer

from preprocessing.chunkers.text_chunker import create_chunks


# Local embedding model
MODEL_NAME = "all-MiniLM-L6-v2"
def load_embedding_model():
    """
    Load the Sentence Transformer embedding model.
    """

    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded successfully.")

    return model


def generate_embeddings(chunks, model):
    """
    Generate embeddings for document chunks.

    Args:
        chunks: List of LangChain Document objects.
        model: SentenceTransformer model.

    Returns:
        Embeddings as a NumPy array.
    """

    texts = [chunk.page_content for chunk in chunks]

    print(f"\nGenerating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return embeddings


if __name__ == "__main__":

    print("=" * 60)
    print("EMBEDDING GENERATION")
    print("=" * 60)

    # Step 1: Load and chunk documents
    chunks = create_chunks()

    # Step 2: Load embedding model
    model = load_embedding_model()

    # Step 3: Generate embeddings
    embeddings = generate_embeddings(chunks, model)

    # Step 4: Verify embeddings
    print("\n" + "=" * 60)
    print("EMBEDDING RESULTS")
    print("=" * 60)

    print("Number of chunks:", len(chunks))
    print("Embedding shape:", embeddings.shape)
    print("Embedding dimension:", embeddings.shape[1])

    print("\nFirst embedding:")
    print(embeddings[0])

    print("\nEmbedding generation completed successfully.")