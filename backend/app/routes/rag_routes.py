import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
import pypdf

from ..config import SCHEME_DOCS_DIR
from ..schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGIngestResponse,
    RAGStatusResponse
)
from ..services.rag_engine import RAGEngine
from ..services.vector_store import VectorStoreService
from ..services.pdf_processor import SCHEME_FILE_MAP

router = APIRouter(prefix="/api/rag", tags=["RAG Government Schemes Engine"])

@router.post("/query", response_model=RAGQueryResponse)
def query_rag_engine(data: RAGQueryRequest):
    """
    Semantic search and grounded answer generation from official government PDFs.
    Returns exact document citations (document name, page number, excerpt),
    bilingual answers (Kannada and English), and confidence scores.
    Strictly refuses to hallucinate if query is unavailable or out of domain.
    """
    if not data.query or not data.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    result = RAGEngine.answer_query(
        query=data.query.strip(),
        preferred_language=data.language or "kn",
        top_k=data.top_k or 3
    )

    return RAGQueryResponse(
        query=result["query"],
        available=result["available"],
        answer_en=result["answer_en"],
        answer_kn=result["answer_kn"],
        citations=result["citations"],
        confidence=result["confidence"],
        generation_mode=result["generation_mode"],
        gemini_api_used=result["gemini_api_used"]
    )

@router.post("/ingest", response_model=RAGIngestResponse)
def ingest_documents(force: bool = Query(False, description="Force re-indexing all documents")):
    """
    Extracts text, splits chunks, computes embeddings, and stores in ChromaDB.
    """
    result = VectorStoreService.index_all_documents(force_reload=force)
    return RAGIngestResponse(
        status=result["status"],
        collection_name=result["collection_name"],
        total_chunks=result["total_chunks"],
        indexed_documents=result.get("indexed_documents", []),
        persist_directory=result["persist_directory"],
        reindexed=result.get("reindexed", False)
    )

@router.get("/status", response_model=RAGStatusResponse)
def get_rag_status():
    """
    Returns ChromaDB vector store health, document statistics, and embedding configuration.
    """
    return VectorStoreService.get_status()

@router.get("/documents")
def list_available_documents():
    """
    Lists all official government scheme PDF documents stored in scheme_documents directory.
    """
    if not os.path.exists(SCHEME_DOCS_DIR):
        return []

    docs = []
    pdf_files = [f for f in os.listdir(SCHEME_DOCS_DIR) if f.lower().endswith(".pdf")]

    for f in sorted(pdf_files):
        fpath = os.path.join(SCHEME_DOCS_DIR, f)
        meta = SCHEME_FILE_MAP.get(f, {
            "scheme_code": "UNKNOWN",
            "scheme_id": f.replace(".pdf", ""),
            "scheme_name": f.replace(".pdf", "").replace("_", " "),
            "scheme_name_kn": "",
            "category": "Official Government Document"
        })

        page_count = 0
        file_size = os.path.getsize(fpath) if os.path.exists(fpath) else 0
        try:
            reader = pypdf.PdfReader(fpath)
            page_count = len(reader.pages)
        except Exception:
            page_count = 0

        docs.append({
            "filename": f,
            "scheme_code": meta.get("scheme_code"),
            "scheme_id": meta.get("scheme_id"),
            "scheme_name": meta.get("scheme_name"),
            "scheme_name_kn": meta.get("scheme_name_kn"),
            "category": meta.get("category"),
            "page_count": page_count,
            "file_size_bytes": file_size,
            "path": fpath
        })

    return docs

