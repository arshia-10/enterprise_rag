from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


DOCUMENTS_DIR = Path("documents")


def load_pdf(pdf_path):
    """
    Load a single PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of LangChain Document objects.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are supported."
        )

    print(f"Loading PDF: {pdf_path}")

    loader = PyPDFLoader(str(pdf_path))

    documents = loader.load()

    print(
        f"Pages loaded from {pdf_path.name}: "
        f"{len(documents)}"
    )

    return documents


def load_all_pdfs():
    """
    Load all PDF files from the documents directory.

    Used for the initial knowledge base.
    """

    all_documents = []

    pdf_files = list(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    print(
        f"Found {len(pdf_files)} PDF files."
    )

    for pdf_file in pdf_files:

        documents = load_pdf(pdf_file)

        all_documents.extend(documents)

    return all_documents


if __name__ == "__main__":

    documents = load_all_pdfs()

    print("\n" + "=" * 60)
    print(
        f"TOTAL PAGES LOADED: {len(documents)}"
    )
    print("=" * 60)

    for document in documents[:3]:

        print("\nSOURCE:")
        print(
            document.metadata.get("source")
        )

        print("\nPAGE:")
        print(
            document.metadata.get("page")
        )

        print("\nTEXT:")
        print(
            document.page_content[:500]
        )

        print("\n" + "-" * 60)