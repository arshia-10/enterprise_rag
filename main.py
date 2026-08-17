from pathlib import Path

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from generation.generator import Generator
from app.services.document_service import DocumentService

from app.security.document_registry import (
    get_documents_for_role,
    register_document
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="Secure RAG-based Enterprise Knowledge Assistant",
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# INITIALIZE RAG COMPONENTS
# ============================================================

generator = Generator(
    top_k=3
)

document_service = DocumentService()


# ============================================================
# REQUEST SCHEMA
# ============================================================

class QuestionRequest(BaseModel):

    question: str

    role: str = "employee"


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "Enterprise Knowledge Assistant"
    }


# ============================================================
# LIST DOCUMENTS FOR ROLE
# ============================================================

@app.get("/documents")
def list_documents(
    role: str = "employee"
):

    # --------------------------------------------------------
    # Normalize role
    # --------------------------------------------------------

    role = role.strip().lower()

    # --------------------------------------------------------
    # Validate role
    # --------------------------------------------------------

    allowed_roles = {
        "employee",
        "manager",
        "hr",
        "admin"
    }

    if role not in allowed_roles:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid role. Allowed roles: "
                "employee, manager, hr, admin."
            )
        )

    # --------------------------------------------------------
    # Get authorized documents
    # --------------------------------------------------------

    try:

        documents = get_documents_for_role(
            role
        )

        return {
            "role": role,
            "documents": documents,
            "count": len(documents)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    # --------------------------------------------------------
    # Clean inputs
    # --------------------------------------------------------

    question = request.question.strip()

    role = request.role.strip().lower()

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------------------------
    # Validate role
    # --------------------------------------------------------

    allowed_roles = {
        "employee",
        "manager",
        "hr",
        "admin"
    }

    if role not in allowed_roles:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid role. Allowed roles: "
                "employee, manager, hr, admin."
            )
        )

    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    try:

        result = generator.generate_answer(
            question,
            user_role=role
        )

        return {
            "question": question,
            "role": role,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    # --------------------------------------------------------
    # Validate PDF
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # --------------------------------------------------------
    # Create upload directory
    # --------------------------------------------------------

    upload_dir = Path(
        "documents/uploads"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Create file path
    # --------------------------------------------------------

    file_path = (
        upload_dir / file.filename
    )

    try:

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        contents = await file.read()

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(contents)

        print(
            f"\nUploaded file: "
            f"{file.filename}"
        )

        # ----------------------------------------------------
        # Process PDF
        # ----------------------------------------------------

        result = (
            document_service
            .process_uploaded_pdf(
                file_path
            )
        )

        # ----------------------------------------------------
        # Register document for authorization
        # ----------------------------------------------------

        register_document(
            filename=file.filename,
            classification="internal",
            allowed_roles=[
                "employee",
                "manager",
                "admin"
            ]
        )

        # ----------------------------------------------------
        # Refresh retriever
        # ----------------------------------------------------

        generator.retriever.refresh()

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {

            "message": (
                "Document uploaded and "
                "indexed successfully."
            ),

            "filename": file.filename,

            "classification": "internal",

            "chunks_added": result[
                "chunks_added"
            ],

            "total_vectors": result[
                "total_vectors"
            ]

        }

    except Exception as e:

        # ----------------------------------------------------
        # Delete file if processing fails
        # ----------------------------------------------------

        if file_path.exists():

            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )