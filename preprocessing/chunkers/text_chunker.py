from pathlib import Path
from preprocessing.loaders.pdf_loader import (
    load_all_pdfs,
    load_pdf
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)
def split_documents(documents):
    """
    Split loaded documents into smaller chunks.

    Args:
        documents: List of LangChain Document objects.
    Returns:
        List of chunked Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    chunks = text_splitter.split_documents(
        documents
    )
    return chunks
def create_chunks():
    """
    Create chunks from all existing documents.

    Used when building the initial FAISS index.
    """

    print("\nLoading documents...")

    documents = load_all_pdfs()

    print(
        f"\nTotal pages loaded: "
        f"{len(documents)}"
    )

    print("\nCreating chunks...")

    chunks = split_documents(documents)

    print(
        f"Total chunks created: "
        f"{len(chunks)}"
    )

    return chunks


def create_chunks_from_pdf(pdf_path):
    """
    Load and chunk a single PDF.

    Used for dynamic document uploads.
    """

    print(
        f"\nProcessing uploaded PDF: "
        f"{pdf_path}"
    )

    documents = load_pdf(pdf_path)

    print(
        f"Pages loaded: {len(documents)}"
    )

    chunks = split_documents(documents)

    print(
        f"Chunks created: {len(chunks)}"
    )

    return chunks


if __name__ == "__main__":

    chunks = create_chunks()

    print("\n" + "=" * 60)
    print("CHUNKING COMPLETE")
    print("=" * 60)

    sample_count = min(
        3,
        len(chunks)
    )

    for i, chunk in enumerate(
        chunks[:sample_count]
    ):

        print(
            f"\nCHUNK {i + 1}"
        )
        print(
            "Characters:",
            len(chunk.page_content)
        )
        print(
            "Source:",
            chunk.metadata.get("source")
        )

        print(
            "Page:",
            chunk.metadata.get("page")
        )

        print("\nContent:")

        print(
            chunk.page_content[:500]
        )

        print("-" * 60)