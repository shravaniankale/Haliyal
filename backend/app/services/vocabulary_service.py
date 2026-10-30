import os
import csv
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from ..config import DATA_DIR
from ..models import RegionalVocabulary

logger = logging.getLogger(__name__)

class KannadaVocabularyService:
    """
    Service for normalizing regional and dialect Kannada expressions into standard concepts.
    Powered by regional_kannada_vocabulary.csv.
    """

    _cache: Dict[str, Dict[str, Any]] = {}
    _concept_cache: Dict[str, List[Dict[str, Any]]] = {}
    _is_initialized: bool = False

    @classmethod
    def initialize_from_csv(cls):
        """Loads and indexes regional vocabulary from CSV."""
        fpath = os.path.join(DATA_DIR, "regional_kannada_vocabulary.csv")
        cls._cache.clear()
        cls._concept_cache.clear()

        if not os.path.exists(fpath):
            logger.warning(f"Vocabulary CSV not found: {fpath}")
            return

        with open(fpath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                local_term = row.get("local_term", "").strip()
                std_term = row.get("standard_kannada_term", "").strip()
                if not local_term or not std_term:
                    continue

                term_data = {
                    "term_id": row.get("term_id", "").strip(),
                    "local_term": local_term,
                    "standard_kannada_term": std_term,
                    "english_meaning": row.get("english_meaning", "").strip(),
                    "concept_id": row.get("concept_id", "").strip(),
                    "concept_category": row.get("concept_category", "").strip(),
                    "district_or_region": row.get("district_or_region", "").strip(),
                    "alternative_spellings": [s.strip() for s in row.get("alternative_spellings", "").split(";") if s.strip()],
                    "example_sentence": row.get("example_sentence", "").strip(),
                    "verification_status": row.get("verification_status", "verified")
                }

                # Index primary local term
                cls._cache[local_term] = term_data

                # Index alternative spellings
                for alt in term_data["alternative_spellings"]:
                    cls._cache[alt] = term_data

                # Index by concept
                cid = term_data["concept_id"]
                if cid:
                    if cid not in cls._concept_cache:
                        cls._concept_cache[cid] = []
                    cls._concept_cache[cid].append(term_data)

        cls._is_initialized = True
        logger.info(f"KannadaVocabularyService initialized with {len(cls._cache)} term mappings.")

    @classmethod
    def get_all_vocabulary(cls, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """Returns all verified vocabulary terms."""
        if not cls._is_initialized:
            cls.initialize_from_csv()

        if db:
            db_terms = db.query(RegionalVocabulary).all()
            if db_terms:
                return [{
                    "id": t.id,
                    "term_id": t.term_id,
                    "local_term": t.local_term,
                    "standard_kannada_term": t.standard_kannada_term,
                    "english_meaning": t.english_meaning,
                    "concept_id": t.concept_id,
                    "concept_category": t.concept_category,
                    "district_or_region": t.district_or_region,
                    "alternative_spellings": t.alternative_spellings,
                    "example_sentence": t.example_sentence,
                    "verification_status": t.verification_status,
                    "notes": t.notes
                } for t in db_terms]

        # Fallback to in-memory cache
        seen_ids = set()
        results = []
        for term_data in cls._cache.values():
            tid = term_data["term_id"]
            if tid not in seen_ids:
                seen_ids.add(tid)
                results.append(term_data)
        return results

    @classmethod
    def normalize_text(cls, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Normalizes regional dialect terms in farmer Kannada text into standard terms.
        Returns (normalized_text, list_of_detected_replacements).
        """
        if not text:
            return "", []

        if not cls._is_initialized:
            cls.initialize_from_csv()

        normalized = text
        detected = []

        # Sort terms by length descending to replace longer phrases first
        sorted_terms = sorted(cls._cache.keys(), key=lambda t: len(t), reverse=True)

        for term in sorted_terms:
            if term in normalized:
                term_info = cls._cache[term]
                std_term = term_info["standard_kannada_term"]
                if term != std_term:
                    normalized = normalized.replace(term, std_term)
                    detected.append({
                        "original_term": term,
                        "standard_term": std_term,
                        "concept_id": term_info["concept_id"],
                        "english_meaning": term_info["english_meaning"],
                        "region": term_info["district_or_region"]
                    })

        # Common North Karnataka phrase patterns
        nk_patterns = [
            (r'ಹೊಲದಾಗ\b', 'ಜಮೀನಿನಲ್ಲಿ'),
            (r'ಹೊಲದಾಗೆ\b', 'ಜಮೀನಿನಲ್ಲಿ'),
            (r'ಗದ್ದ್ಯಾಗ\b', 'ಗದ್ದೆಯಲ್ಲಿ'),
            (r'ಬೆಳಿಲಿಕತ್ತೇನಿ\b', 'ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ'),
            (r'ಬೆಳಿಲಿಕ್ಕೆತ್ತೀನಿ\b', 'ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ'),
            (r'ಮಾಡಲಿಕತ್ತೇನಿ\b', 'ಮಾಡುತ್ತಿದ್ದೇನೆ'),
            (r'ಹಾಕ್ಲಿಕತ್ತೇನಿ\b', 'ಹಾಕುತ್ತಿದ್ದೇನೆ'),
            (r'ಬಿತ್ತೇನಿ\b', 'ಬಿತ್ತಿದ್ದೇನೆ'),
            (r'ಮಾಡೇನಿ\b', 'ಮಾಡಿದ್ದೇನೆ'),
            (r'ಹಾಕೇನಿ\b', 'ಹಾಕಿದ್ದೇನೆ'),
            (r'ಜಮೀನ್ ಐತಿ\b', 'ಜಮೀನು ಇದೆ'),
            (r'ಹೊಲ ಐತಿ\b', 'ಜಮೀನು ಇದೆ'),
            (r'ಸಿಗತೈತಿ\b', 'ಸಿಗುತ್ತದೆ'),
            (r'ಆಗತೈತಿ\b', 'ಆಗುತ್ತದೆ'),
            (r'ಬರತೈತಿ\b', 'ಬರುತ್ತದೆ'),
            (r'ಹೇಳ್ರಿ\b', 'ಹೇಳಿ'),
            (r'ತಿಳಿಸ್ರಿ\b', 'ತಿಳಿಸಿ'),
            (r'ಕೊಡ್ರಿ\b', 'ನೀಡಿ'),
            (r'ಕೇಳ್ರಿ\b', 'ಕೇಳಿ'),
            (r'ನೋಡ್ರಿ\b', 'ನೋಡಿ'),
            (r'ನೋಡ್ರೀ\b', 'ನೋಡಿ'),
            (r'ಹೌದ್ರಿ\b', 'ಹೌದು'),
            (r'ಹೌದ್ರೀ\b', 'ಹೌದು'),
            (r'ಇಲ್ಲ್ರೀ\b', 'ಇಲ್ಲ'),
            (r'ಇಲ್ಲ್ರೀ\b', 'ಇಲ್ಲ'),
        ]
        for pat, repl in nk_patterns:
            if re.search(pat, normalized):
                normalized = re.sub(pat, repl, normalized)
                detected.append({
                    "original_term": pat.replace('\\b', ''),
                    "standard_term": repl,
                    "concept_id": "DIALECT_PATTERN",
                    "english_meaning": "North Karnataka grammatical variant",
                    "region": "North Karnataka"
                })

        return normalized, detected

    @classmethod
    def adapt_to_dialect(cls, text: str, regional_style: str = "Standard Kannada") -> str:
        """
        Adapts standard Kannada response into the selected regional dialect style
        using validated vocabulary from regional_kannada_vocabulary.csv.
        """
        if not text or regional_style in ["Standard Kannada", "English"]:
            return text

        adapted = text

        if regional_style == "North Karnataka":
            # Adapt verbs and endings respectfully to North Karnataka dialect
            replacements = [
                ("ಆಗುತ್ತದೆ", "ಆಗತೈತಿ"),
                ("ಆಗುತ್ತೆ", "ಆಗತೈತಿ ನೋಡ್ರೀ"),
                ("ಇದೆ.", "ಐತಿ ನೋಡ್ರೀ."),
                ("ಇದೆ\n", "ಐತಿ ನೋಡ್ರೀ\n"),
                ("ಇದೆ ", "ಐತಿ "),
                ("ಇವೆ.", "ಅವ್ ನೋಡ್ರೀ."),
                ("ಸಿಗುತ್ತದೆ.", "ಸಿಗತೈತಿ ನೋಡ್ರೀ."),
                ("ಸಿಗುತ್ತದೆ\n", "ಸಿಗತೈತಿ ನೋಡ್ರೀ\n"),
                ("ಸಿಗುತ್ತದೆ ", "ಸಿಗತೈತಿ "),
                ("ತಿಳಿಸಿ", "ತಿಳಿಸ್ರಿ ಹೇಳ್ರಿ"),
                ("ಹೇಳಿ", "ಹೇಳ್ರಿ"),
                ("ನೋಡಿ", "ನೋಡ್ರೀ"),
                ("ಹಾಕಿ", "ಹಾಕ್ರಿ"),
                ("ಕೇಳಿ", "ಕೇಳ್ರಿ"),
                ("ಸಲ್ಲಿಸಿ", "ಸಲ್ಲಿಸ್ರಿ"),
                ("ಮಾಡಿಕೊಳ್ಳಿ", "ಮಾಡಿಕೊಳ್ರಿ"),
                ("ಕಡಲೆಕಾಯಿ", "ಶೇಂಗಾ"),
                ("ಕಪ್ಪು ಮಣ್ಣು", "ಏರಿ ಮಣ್ಣು (ಕಪ್ಪು ಮಣ್ಣು)"),
                ("ಜಮೀನು", "ಹೊಲ"),
            ]
            for std, nk in replacements:
                adapted = adapted.replace(std, nk)

        elif regional_style == "South Karnataka":
            # Adapt expressions to Old Mysuru / South Karnataka style
            replacements = [
                ("ತಿಳಿಸಿರಿ", "ತಿಳಿಸಿ ಸ್ವಾಮಿ"),
                ("ತಿಳಿಸಿ", "ತಿಳಿಸಿ ಸ್ವಾಮಿ"),
                ("ಕೇಳಿ", "ಕೇಳಿ ಸ್ವಾಮಿ"),
                ("ಭೇಟಿ ನೀಡಿ", "ಭೇಟಿ ನೀಡಿ ಬನ್ನಿ"),
                ("ಆಗತೈತಿ", "ಆಗುತ್ತದೆ"),
                ("ನೀಡಲಾಗುತ್ತದೆ", "ಸಿಗುತ್ತದೆ"),
                ("ಅಗತ್ಯವಿದೆ", "ಬೇಕು"),
                ("ಶೇಂಗಾ", "ಕಡಲೆಕಾಯಿ"),
                ("ಹೊಲ", "ಜಮೀನು"),
                ("ಏರಿ ಮಣ್ಣು", "ಕೆಂಪು ಮಣ್ಣು"),
            ]
            for std, sk in replacements:
                adapted = adapted.replace(std, sk)

        return adapted

    @classmethod
    def get_standard_crop_name(cls, crop_token: str) -> Optional[str]:
        """Resolves dialect crop token to standard crop name."""
        if not cls._is_initialized:
            cls.initialize_from_csv()

        clean_token = crop_token.strip()
        if clean_token in cls._cache:
            info = cls._cache[clean_token]
            if info["concept_category"] == "crop":
                return info["standard_kannada_term"]
        return None

