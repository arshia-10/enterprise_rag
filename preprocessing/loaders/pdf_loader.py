from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


DOCUMENTS_DIR = Path("documents")


def load_all_pdfs():

    all_documents = []

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files.\n")

    for pdf_file in pdf_files:

        print(f"Loading: {pdf_file.name}")

        loader = PyPDFLoader(str(pdf_file))

        documents = loader.load()

        print(f"Pages loaded: {len(documents)}")

        all_documents.extend(documents)

    return all_documents


if __name__ == "__main__":

    documents = load_all_pdfs()

    print("\n" + "=" * 60)
    print(f"TOTAL PAGES LOADED: {len(documents)}")
    print("=" * 60)

    for document in documents[:3]:

        print("\nSOURCE:")
        print(document.metadata.get("source"))

        print("\nPAGE:")
        print(document.metadata.get("page"))

        print("\nTEXT:")
        print(document.page_content[:500])

        print("\n" + "-" * 60)