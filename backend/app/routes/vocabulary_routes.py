from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import RegionalVocabulary
from ..schemas import (
    RegionalVocabularyResponse,
    VocabularyNormalizeRequest,
    VocabularyNormalizeResponse
)
from ..services.vocabulary_service import KannadaVocabularyService

router = APIRouter(prefix="/api/vocabulary", tags=["Regional Kannada Vocabulary"])

@router.get("", response_model=List[RegionalVocabularyResponse])
def get_vocabulary(
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns verified regional Kannada vocabulary mappings from regional_kannada_vocabulary.csv.
    """
    query = db.query(RegionalVocabulary)
    if region:
        query = query.filter(RegionalVocabulary.district_or_region.ilike(f"%{region}%"))
    if category:
        query = query.filter(RegionalVocabulary.concept_category.ilike(f"%{category}%"))

    terms = query.all()
    if not terms:
        # Fallback to in-memory loader
        raw_list = KannadaVocabularyService.get_all_vocabulary(db=db)
        return raw_list

    return terms

@router.post("/normalize", response_model=VocabularyNormalizeResponse)
def normalize_kannada_text(data: VocabularyNormalizeRequest):
    """
    Normalizes local North/South Karnataka dialect terms into standard agricultural Kannada.
    """
    normalized_text, detected = KannadaVocabularyService.normalize_text(data.text)
    applied_concepts = list({d["concept_id"] for d in detected if d.get("concept_id")})

    return VocabularyNormalizeResponse(
        original_text=data.text,
        normalized_text=normalized_text,
        detected_local_terms=detected,
        applied_concepts=applied_concepts
    )

