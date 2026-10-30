from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    DatasetDictionary,
    Scheme,
    RegionalVocabulary,
    SpeechMetadata,
    FarmerSession
)
from ..schemas import DatasetDictionaryResponse

router = APIRouter(prefix="/api/datasets", tags=["CSV Datasets & Data Dictionary"])

@router.get("/dictionary", response_model=List[DatasetDictionaryResponse])
def get_all_dataset_dictionaries(db: Session = Depends(get_db)):
    """
    Returns documentation catalog from dataset_data_dictionary.csv.
    Explains the purpose, key fields, and validation rules for each dataset.
    """
    return db.query(DatasetDictionary).all()

@router.get("/dictionary/{file_name}", response_model=DatasetDictionaryResponse)
def get_dataset_dictionary_by_file(file_name: str, db: Session = Depends(get_db)):
    """
    Retrieves documentation for a specific CSV dataset file.
    """
    entry = db.query(DatasetDictionary).filter(
        (DatasetDictionary.file_name == file_name) |
        (DatasetDictionary.file_name.ilike(f"%{file_name}%"))
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Documentation for '{file_name}' not found")
    return entry

@router.get("/summary")
def get_datasets_integration_summary(db: Session = Depends(get_db)):
    """
    Returns high-level status and record counts across all five integrated CSV datasets.
    """
    schemes_count = db.query(Scheme).count()
    verified_schemes = db.query(Scheme).filter(Scheme.verification_status == "Verified").count()
    demo_schemes = db.query(Scheme).filter(Scheme.verification_status == "Synthetic Demo").count()
    vocab_count = db.query(RegionalVocabulary).count()
    speech_count = db.query(SpeechMetadata).count()
    consented_speech = db.query(SpeechMetadata).filter(SpeechMetadata.consent_status == "consented").count()
    sessions_count = db.query(FarmerSession).count()
    dictionary_count = db.query(DatasetDictionary).count()

    return {
        "datasets_integrated": 5,
        "status": "All CSV datasets successfully integrated",
        "datasets": {
            "government_schemes.csv": {
                "total_records": schemes_count,
                "verified_official": verified_schemes,
                "synthetic_demo": demo_schemes,
                "purpose": "Structured catalogue for scheme discovery and rule-based deterministic eligibility checks",
                "integration": "Connected to scheme discovery and rule eligibility engine"
            },
            "regional_kannada_vocabulary.csv": {
                "total_records": vocab_count,
                "purpose": "Map regional expressions and local agricultural terms to standard concepts",
                "integration": "Connected to conversational AI entity extraction and normalization"
            },
            "kannada_speech_metadata.csv": {
                "total_records": speech_count,
                "consented_records": consented_speech,
                "purpose": "Metadata index for consented audio and transcription evaluation/training",
                "integration": "Connected to speech evaluation WER/CER benchmarks and dataset stats"
            },
            "farmer_session_profile.csv": {
                "total_records": sessions_count,
                "purpose": "Example schema for conversation-time farmer information",
                "integration": "Connected to farmer session persistence and missing-information tracking"
            },
            "dataset_data_dictionary.csv": {
                "total_records": dictionary_count,
                "purpose": "Authoritative dictionary defining purpose and field semantics across all files",
                "integration": "Exposed via /api/datasets/dictionary API"
            }
        }
    }

