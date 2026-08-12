from preprocessing.chunkers.text_chunker import create_chunks
from preprocessing.embeddings.embedding_generator import (
    load_embedding_model,
    generate_embeddings
)

from vector_store.faiss_store import FAISSVectorStore


# Paths where FAISS index and metadata will be saved
INDEX_PATH = "vector_store/faiss_index.bin"
METADATA_PATH = "vector_store/metadata.pkl"


def build_faiss_index():

    print("=" * 60)
    print("BUILDING FAISS VECTOR STORE")
    print("=" * 60)

    # --------------------------------------------------
    # Step 1: Load and chunk documents
    # --------------------------------------------------

    print("\n[1/4] Creating document chunks...")

    chunks = create_chunks()

    if not chunks:
        raise ValueError(
            "No document chunks were created. "
            "Please check your documents and chunking pipeline."
        )

    print(f"Number of chunks: {len(chunks)}")

    # --------------------------------------------------
    # Step 2: Load embedding model
    # --------------------------------------------------

    print("\n[2/4] Loading embedding model...")

    model = load_embedding_model()

    # --------------------------------------------------
    # Step 3: Generate embeddings
    # --------------------------------------------------

    print("\n[3/4] Generating embeddings...")

    embeddings = generate_embeddings(
        chunks,
        model
    )

    print("Embedding shape:", embeddings.shape)
    print("Embedding dimension:", embeddings.shape[1])

    # --------------------------------------------------
    # Step 4: Create FAISS vector store
    # --------------------------------------------------

    print("\n[4/4] Creating FAISS index...")

    dimension = embeddings.shape[1]

    vector_store = FAISSVectorStore(
        dimension=dimension
    )

    vector_store.add_embeddings(
        embeddings=embeddings,
        documents=chunks
    )

    # Save FAISS index and metadata
    vector_store.save(
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH
    )

    print("\n" + "=" * 60)
    print("FAISS VECTOR STORE CREATED SUCCESSFULLY")
    print("=" * 60)

    print("\nTotal vectors:", vector_store.index.ntotal)
    print("Vector dimension:", dimension)

    print("\nSaved files:")
    print(f"FAISS index: {INDEX_PATH}")
    print(f"Metadata:    {METADATA_PATH}")

    print("\nFAISS indexing completed successfully.")


if __name__ == "__main__":
    build_faiss_index()