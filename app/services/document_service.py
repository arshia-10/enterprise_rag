from pathlib import Path

from preprocessing.chunkers.text_chunker import (
    create_chunks_from_pdf
)

from preprocessing.embeddings.embedding_generator import (
    load_embedding_model,
    generate_embeddings
)

from vector_store.faiss_store import FAISSVectorStore


# --------------------------------------------------
# Paths
# --------------------------------------------------

INDEX_PATH = "vector_store/faiss_index.bin"
METADATA_PATH = "vector_store/metadata.pkl"

UPLOAD_DIR = Path("documents/uploads")


class DocumentService:

    def __init__(self):
        """
        Initialize the document processing service.
        """

        print("Initializing Document Service...")

        # Create upload directory if it doesn't exist
        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        # Load embedding model ONCE
        print("Loading embedding model...")

        self.embedding_model = load_embedding_model()

        print("Document Service initialized.")

    def process_uploaded_pdf(self, pdf_path):
        """
        Process a newly uploaded PDF and add it
        to the existing FAISS vector store.

        Pipeline:

        PDF
        ↓
        Load
        ↓
        Chunk
        ↓
        Embeddings
        ↓
        FAISS
        ↓
        Save updated index
        """

        pdf_path = Path(pdf_path)

        print("\n" + "=" * 60)
        print("PROCESSING UPLOADED DOCUMENT")
        print("=" * 60)

        # ------------------------------------------
        # Step 1: Load and chunk PDF
        # ------------------------------------------

        print("\n[1/4] Loading and chunking PDF...")

        chunks = create_chunks_from_pdf(
            pdf_path
        )

        if not chunks:
            raise ValueError(
                "No text chunks were created "
                "from the uploaded PDF."
            )

        print(
            f"Chunks created: {len(chunks)}"
        )

        # ------------------------------------------
        # Step 2: Generate embeddings
        # ------------------------------------------

        print(
            "\n[2/4] Generating embeddings..."
        )

        embeddings = generate_embeddings(
            chunks,
            self.embedding_model
        )

        print(
            f"Embedding shape: "
            f"{embeddings.shape}"
        )

        # ------------------------------------------
        # Step 3: Load existing FAISS index
        # ------------------------------------------

        print(
            "\n[3/4] Loading existing FAISS index..."
        )

        vector_store = FAISSVectorStore(
            dimension=embeddings.shape[1]
        )

        vector_store.load(
            INDEX_PATH,
            METADATA_PATH
        )

        existing_vectors = (
            vector_store.index.ntotal
        )

        print(
            f"Existing vectors: "
            f"{existing_vectors}"
        )

        # ------------------------------------------
        # Step 4: Add new embeddings
        # ------------------------------------------

        print(
            "\n[4/4] Adding new vectors to FAISS..."
        )

        vector_store.add_embeddings(
            embeddings=embeddings,
            documents=chunks
        )

        vector_store.save(
            index_path=INDEX_PATH,
            metadata_path=METADATA_PATH
        )

        total_vectors = (
            vector_store.index.ntotal
        )

        print("\n" + "=" * 60)
        print("DOCUMENT ADDED SUCCESSFULLY")
        print("=" * 60)

        print(
            f"New chunks added: "
            f"{len(chunks)}"
        )

        print(
            f"Previous vectors: "
            f"{existing_vectors}"
        )

        print(
            f"Total vectors now: "
            f"{total_vectors}"
        )

        return {
            "filename": pdf_path.name,
            "chunks_added": len(chunks),
            "total_vectors": total_vectors
        }
if __name__ == "__main__":

    service = DocumentService()

    result = service.process_uploaded_pdf(
        "documents/uploads/enterprise_remote_work_policy.pdf"
    )

    print("\nRESULT:")
    print(result)