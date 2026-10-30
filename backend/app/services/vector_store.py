import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..config import CHROMA_PERSIST_DIR, SCHEME_DOCS_DIR, GEMINI_API_KEY
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

COLLECTION_NAME = "krishi_scheme_documents"

class VectorStoreService:
    """
    Manages persistent ChromaDB vector storage and semantic retrieval
    for official Karnataka government scheme documents.
    """
    _client = None
    _collection = None
    _embedding_function = None

    @classmethod
    def get_client(cls):
        """Initializes persistent ChromaDB client."""
        if cls._client is None:
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
            cls._client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        return cls._client

    @classmethod
    def get_embedding_function(cls):
        """
        Returns embedding function. Uses local ONNX all-MiniLM-L6-v2 by default
        for high-speed local inference without API dependencies.
        """
        if cls._embedding_function is None:
            cls._embedding_function = embedding_functions.DefaultEmbeddingFunction()
        return cls._embedding_function

    @classmethod
    def get_collection(cls):
        """Returns or creates the Chroma collection with persistent embeddings."""
        if cls._collection is None:
            client = cls.get_client()
            emb_fn = cls.get_embedding_function()
            cls._collection = client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=emb_fn,
                metadata={"hnsw:space": "cosine"}
            )
        return cls._collection

    @classmethod
    def index_all_documents(cls, force_reload: bool = False) -> Dict[str, Any]:
        """
        Extracts, chunks, embeds, and stores all official scheme PDF documents in ChromaDB.
        If already indexed and not force_reload, returns existing stats.
        """
        collection = cls.get_collection()
        current_count = collection.count()

        if current_count > 0 and not force_reload:
            logger.info(f"Vector store already contains {current_count} chunks. Skipping re-index.")
            return {
                "status": "already_indexed",
                "collection_name": COLLECTION_NAME,
                "total_chunks": current_count,
                "persist_directory": CHROMA_PERSIST_DIR,
                "reindexed": False
            }

        if force_reload and current_count > 0:
            logger.info(f"Clearing {current_count} existing chunks for fresh reload...")
            client = cls.get_client()
            client.delete_collection(name=COLLECTION_NAME)
            cls._collection = None
            collection = cls.get_collection()

        logger.info(f"Indexing PDF documents from: {SCHEME_DOCS_DIR}")
        chunks = PDFProcessor.process_all_documents(SCHEME_DOCS_DIR)

        if not chunks:
            logger.warning("No PDF document chunks found to index!")
            return {
                "status": "empty",
                "collection_name": COLLECTION_NAME,
                "total_chunks": 0,
                "persist_directory": CHROMA_PERSIST_DIR,
                "reindexed": False
            }

        # Prepare batch vectors
        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "doc_name": c["doc_name"],
                "page_number": int(c["page_number"]),
                "chunk_index": int(c["chunk_index"]),
                "scheme_code": c["scheme_code"],
                "scheme_id": c["scheme_id"],
                "scheme_name": c["scheme_name"],
                "category": c["category"],
                "char_count": int(c["char_count"])
            }
            for c in chunks
        ]

        # Add to ChromaDB in batches of 50 to avoid memory spikes
        batch_size = 50
        total = len(chunks)
        for i in range(0, total, batch_size):
            batch_end = min(i + batch_size, total)
            collection.add(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )

        logger.info(f"Successfully indexed {collection.count()} chunks into ChromaDB.")
        return {
            "status": "success",
            "collection_name": COLLECTION_NAME,
            "total_chunks": collection.count(),
            "indexed_documents": list(set(c["doc_name"] for c in chunks)),
            "persist_directory": CHROMA_PERSIST_DIR,
            "reindexed": True
        }

    @classmethod
    def similarity_search(
        cls,
        query: str,
        n_results: int = 4,
        scheme_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic vector search against scheme documents.
        Returns ranked chunks with exact page references and cosine similarity scores.
        """
        collection = cls.get_collection()
        if collection.count() == 0:
            # Auto-ingest if empty
            cls.index_all_documents()

        where_clause = None
        if scheme_id:
            where_clause = {"scheme_id": scheme_id}

        try:
            results = collection.query(
                query_texts=[query],
                n_results=min(n_results, max(1, collection.count())),
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logger.error(f"Error during semantic vector query: {e}")
            return []

        hits = []
        if results and "documents" in results and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else []
            dists = results["distances"][0] if "distances" in results else []
            ids = results["ids"][0] if "ids" in results else []

            for i in range(len(docs)):
                dist = float(dists[i]) if i < len(dists) and dists[i] is not None else 1.0
                # Cosine distance to similarity score in [0.0, 1.0]
                similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                meta = metas[i] if i < len(metas) else {}

                hits.append({
                    "chunk_id": ids[i] if i < len(ids) else f"chunk_{i}",
                    "doc_name": meta.get("doc_name", "official_scheme_doc.pdf"),
                    "page_number": meta.get("page_number", 1),
                    "chunk_index": meta.get("chunk_index", 0),
                    "scheme_code": meta.get("scheme_code", "SCM"),
                    "scheme_id": meta.get("scheme_id", "SCHEME"),
                    "scheme_name": meta.get("scheme_name", "Government Scheme"),
                    "category": meta.get("category", "Agriculture"),
                    "text": docs[i],
                    "distance": dist,
                    "similarity_score": round(similarity, 4)
                })

        return hits

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Returns vector database status and configuration."""
        client = cls.get_client()
        collection = cls.get_collection()
        total_chunks = collection.count()

        unique_docs = set()
        if total_chunks > 0:
            try:
                all_metas = collection.get(include=["metadatas"])["metadatas"]
                for m in all_metas:
                    if m and "doc_name" in m:
                        unique_docs.add(m["doc_name"])
            except Exception:
                pass

        return {
            "status": "ready" if total_chunks > 0 else "empty",
            "collection_name": COLLECTION_NAME,
            "total_chunks": total_chunks,
            "total_documents": len(unique_docs),
            "documents": sorted(list(unique_docs)),
            "persist_directory": CHROMA_PERSIST_DIR,
            "embedding_model": "all-MiniLM-L6-v2 (local ONNX, zero-network latency)",
            "gemini_api_configured": bool(GEMINI_API_KEY)
        }

