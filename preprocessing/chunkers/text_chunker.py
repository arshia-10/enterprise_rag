from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Directory containing the source PDF documents
DOCUMENTS_DIR = Path("documents")
def load_documents():
    """
    Load all PDF files from the documents directory.

    Returns:
        list: A list of LangChain Document objects.
    """
    all_documents = []

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:
        print(f"Loading: {pdf_file.name}")

        loader = PyPDFLoader(str(pdf_file))
        documents = loader.load()

        print(f"Pages loaded: {len(documents)}")

        all_documents.extend(documents)

    return all_documents


def split_documents(documents):
    """
    Split loaded documents into smaller chunks.

    Args:
        documents: List of LangChain Document objects.

    Returns:
        list: List of chunked Document objects.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks
def create_chunks():
    """
    Complete document chunking pipeline.

    Returns:
        list: Chunked documents.
    """
    print("\nLoading documents...")
    documents = load_documents()
    print(f"\nTotal pages loaded: {len(documents)}")
    print("\nCreating chunks...")
    chunks = split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")
    return chunks
if __name__ == "__main__":

    chunks = create_chunks()

    print("\n" + "=" * 60)
    print("CHUNKING COMPLETE")
    print("=" * 60)

    # Display a small sample for verification
    sample_count = min(3, len(chunks))

    for i, chunk in enumerate(chunks[:sample_count]):

        print(f"\nCHUNK {i + 1}")
        print("Characters:", len(chunk.page_content))
        print("Source:", chunk.metadata.get("source"))
        print("Page:", chunk.metadata.get("page"))

        print("\nContent:")
        print(chunk.page_content[:500])

        print("-" * 60)