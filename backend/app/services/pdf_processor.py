import os
import re
import logging
from typing import List, Dict, Any, Optional
import pypdf

logger = logging.getLogger(__name__)

# Map filenames to scheme codes and standardized names
SCHEME_FILE_MAP = {
    "PM_KISAN_Operational_Guidelines.pdf": {
        "scheme_code": "SCM001",
        "scheme_id": "PM-KISAN",
        "scheme_name": "Pradhan Mantri Kisan Samman Nidhi",
        "scheme_name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (ಪಿಎಂ-ಕಿಸಾನ್)",
        "category": "Income Support / DBT"
    },
    "PMFBY_Karnataka_Samrakshane_Crop_Insurance.pdf": {
        "scheme_code": "SCM002",
        "scheme_id": "PMFBY",
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana",
        "scheme_name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ)",
        "category": "Crop Insurance / Risk Protection"
    },
    "Karnataka_Krishi_Bhagya_Scheme_Dryland_Manual.pdf": {
        "scheme_code": "SCM003",
        "scheme_id": "KRISHI-BHAGYA",
        "scheme_name": "Karnataka Krishi Bhagya Scheme",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ",
        "category": "Dryland Irrigation / Farm Pond Subsidy"
    },
    "Kisan_Credit_Card_KCC_Crop_Loans_Handbook.pdf": {
        "scheme_code": "LN001",
        "scheme_id": "KCC",
        "scheme_name": "Kisan Credit Card Crop Loan Scheme",
        "scheme_name_kn": "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (ಕೆಸಿಸಿ) ಸಾಲ ಯೋಜನೆ",
        "category": "Agricultural Credit / Subsidized Loans"
    }
}

class PDFProcessor:
    """
    Extracts text page-by-page from official government PDF documents
    and creates semantically coherent, metadata-rich document chunks.
    """

    @staticmethod
    def extract_pages(pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts raw text page by page preserving page index.
        Returns: list of dicts with 'page_number' (1-indexed), 'text', 'char_count'.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        pages_data = []
        try:
            reader = pypdf.PdfReader(pdf_path)
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                # Normalize excessive whitespace but preserve paragraph breaks
                normalized_text = re.sub(r'[ \t]+', ' ', page_text).strip()
                pages_data.append({
                    "page_number": idx + 1,
                    "total_pages": total_pages,
                    "text": normalized_text,
                    "char_count": len(normalized_text)
                })
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            raise e

        return pages_data

    @staticmethod
    def chunk_page_text(
        text: str,
        page_number: int,
        doc_name: str,
        scheme_meta: Dict[str, Any],
        chunk_size: int = 650,
        chunk_overlap: int = 150
    ) -> List[Dict[str, Any]]:
        """
        Splits page text into overlapping chunks respecting sentence and section breaks.
        """
        if not text:
            return []

        chunks = []
        # Split text into natural paragraphs
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        current_chunk_text = ""
        chunk_idx = 0

        for para in paragraphs:
            if len(current_chunk_text) + len(para) < chunk_size:
                current_chunk_text += ("\n" + para if current_chunk_text else para)
            else:
                # If current chunk is non-empty, save it
                if current_chunk_text:
                    chunk_id = f"{doc_name}_p{page_number}_c{chunk_idx}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_name": doc_name,
                        "page_number": page_number,
                        "chunk_index": chunk_idx,
                        "scheme_code": scheme_meta.get("scheme_code", "UNKNOWN"),
                        "scheme_id": scheme_meta.get("scheme_id", "SCHEME"),
                        "scheme_name": scheme_meta.get("scheme_name", doc_name),
                        "scheme_name_kn": scheme_meta.get("scheme_name_kn", ""),
                        "category": scheme_meta.get("category", "Government Scheme"),
                        "text": current_chunk_text.strip(),
                        "char_count": len(current_chunk_text.strip())
                    })
                    chunk_idx += 1

                # If paragraph itself is longer than chunk_size, split by sentences
                if len(para) > chunk_size:
                    sentences = re.split(r'(?<=[.!?।])\s+', para)
                    sub_chunk = ""
                    for s in sentences:
                        if len(sub_chunk) + len(s) < chunk_size:
                            sub_chunk += (" " + s if sub_chunk else s)
                        else:
                            if sub_chunk:
                                chunk_id = f"{doc_name}_p{page_number}_c{chunk_idx}"
                                chunks.append({
                                    "chunk_id": chunk_id,
                                    "doc_name": doc_name,
                                    "page_number": page_number,
                                    "chunk_index": chunk_idx,
                                    "scheme_code": scheme_meta.get("scheme_code", "UNKNOWN"),
                                    "scheme_id": scheme_meta.get("scheme_id", "SCHEME"),
                                    "scheme_name": scheme_meta.get("scheme_name", doc_name),
                                    "scheme_name_kn": scheme_meta.get("scheme_name_kn", ""),
                                    "category": scheme_meta.get("category", "Government Scheme"),
                                    "text": sub_chunk.strip(),
                                    "char_count": len(sub_chunk.strip())
                                })
                                chunk_idx += 1
                            sub_chunk = s
                    current_chunk_text = sub_chunk
                else:
                    # Start new chunk with overlap from end of previous
                    if current_chunk_text:
                        overlap = current_chunk_text[-chunk_overlap:]
                        current_chunk_text = overlap + "\n" + para
                    else:
                        current_chunk_text = para

        # Flush any remaining text
        if current_chunk_text.strip():
            chunk_id = f"{doc_name}_p{page_number}_c{chunk_idx}"
            chunks.append({
                "chunk_id": chunk_id,
                "doc_name": doc_name,
                "page_number": page_number,
                "chunk_index": chunk_idx,
                "scheme_code": scheme_meta.get("scheme_code", "UNKNOWN"),
                "scheme_id": scheme_meta.get("scheme_id", "SCHEME"),
                "scheme_name": scheme_meta.get("scheme_name", doc_name),
                "scheme_name_kn": scheme_meta.get("scheme_name_kn", ""),
                "category": scheme_meta.get("category", "Government Scheme"),
                "text": current_chunk_text.strip(),
                "char_count": len(current_chunk_text.strip())
            })

        return chunks

    @classmethod
    def process_all_documents(cls, docs_dir: str) -> List[Dict[str, Any]]:
        """
        Reads all PDF files from directory, extracts pages, chunks them,
        and attaches metadata.
        """
        all_chunks = []
        if not os.path.exists(docs_dir):
            logger.warning(f"Documents directory does not exist: {docs_dir}")
            return all_chunks

        pdf_files = [f for f in os.listdir(docs_dir) if f.lower().endswith(".pdf")]
        logger.info(f"Processing {len(pdf_files)} PDF documents from {docs_dir}")

        for fname in sorted(pdf_files):
            file_path = os.path.join(docs_dir, fname)
            meta = SCHEME_FILE_MAP.get(fname, {
                "scheme_code": "DOC",
                "scheme_id": fname.replace(".pdf", ""),
                "scheme_name": fname.replace(".pdf", "").replace("_", " "),
                "scheme_name_kn": "",
                "category": "Official Scheme Document"
            })

            try:
                pages = cls.extract_pages(file_path)
                for page_info in pages:
                    page_chunks = cls.chunk_page_text(
                        text=page_info["text"],
                        page_number=page_info["page_number"],
                        doc_name=fname,
                        scheme_meta=meta
                    )
                    all_chunks.extend(page_chunks)
            except Exception as e:
                logger.error(f"Failed to process {fname}: {e}")

        logger.info(f"Generated {len(all_chunks)} total chunks across {len(pdf_files)} PDFs")
        return all_chunks

