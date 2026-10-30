from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SpeechMetadata
from ..schemas import (
    TTSRequest,
    STTResponse,
    SpeechMetadataResponse,
    SpeechEvaluationRequest,
    SpeechEvaluationResponse
)
from ..services.kannada_speech import KannadaSpeechService
from ..services.speech_eval_service import SpeechEvaluationService

router = APIRouter(prefix="/api/speech", tags=["Kannada Speech Technology"])

@router.get("/voices")
def list_voices():
    """
    Returns available neural voices (Sapna, Gagan, Neerja, Prabhat)
    with gender, language, description, and preview text.
    """
    return KannadaSpeechService.get_voice_catalog()

@router.post("/preview")
def preview_voice(voice_id: str = Query("kn_female")):
    """
    Generates preview speech for a specific neural voice.
    """
    catalog = {v["voice_id"]: v for v in KannadaSpeechService.get_voice_catalog()}
    voice_info = catalog.get(voice_id, catalog["kn_female"])
    audio_url, status = KannadaSpeechService.synthesize_kannada_speech(
        text=voice_info["preview_text"],
        voice_gender=voice_info["gender"],
        language=voice_info["language"]
    )
    return {
        "voice_id": voice_id,
        "name": voice_info["name"],
        "gender": voice_info["gender"],
        "language": voice_info["language"],
        "preview_text": voice_info["preview_text"],
        "audio_url": audio_url,
        "message": status
    }

@router.post("/synthesize")
def synthesize_speech(data: TTSRequest):
    """
    Synthesizes Kannada/English text into authentic neural audio.
    Supports Male / Female voice selection (Gagan, Sapna, Prabhat, Neerja).
    """
    if not data.text or not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    gender = getattr(data, "voice_gender", "female") or "female"
    lang = getattr(data, "language", "kn") or "kn"
    speed = getattr(data, "speech_speed", 1.0) or 1.0

    audio_url, status_msg = KannadaSpeechService.synthesize_kannada_speech(
        text=data.text,
        regional_style=data.regional_preference or "Standard Kannada",
        voice_gender=gender,
        language=lang,
        speech_speed=speed
    )

    if not audio_url:
        return {
            "success": False,
            "audio_url": None,
            "message": status_msg
        }

    return {
        "success": True,
        "audio_url": audio_url,
        "language": lang,
        "gender": gender,
        "regional_style": data.regional_preference or "Standard Kannada",
        "message": status_msg
    }

@router.post("/transcribe", response_model=STTResponse)
async def transcribe_speech(audio: UploadFile = File(...)):
    """
    Transcribes farmer's spoken audio into Kannada text.
    """
    try:
        content = await audio.read()
        transcript, confidence = KannadaSpeechService.transcribe_audio_file(content, audio.filename or "recording.wav")
        return STTResponse(
            transcript=transcript,
            language="kn",
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription error: {str(e)}")

# --- CSV SPEECH METADATA & EVALUATION ENDPOINTS ---

@router.get("/metadata", response_model=List[SpeechMetadataResponse])
def get_speech_metadata(
    district: Optional[str] = Query(None),
    split: Optional[str] = Query(None),
    consent: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lists speech dataset metadata from kannada_speech_metadata.csv.
    Explicitly provides index and consent records; audio is reference only.
    """
    query = db.query(SpeechMetadata)
    if district:
        query = query.filter(SpeechMetadata.district_or_region.ilike(f"%{district}%"))
    if split:
        query = query.filter(SpeechMetadata.dataset_split == split)
    if consent:
        query = query.filter(SpeechMetadata.consent_status.ilike(f"%{consent}%"))

    return query.all()

@router.get("/metadata/stats")
def get_speech_metadata_stats(db: Session = Depends(get_db)):
    """
    Returns statistical metrics, consent rate, and split distributions for speech dataset.
    """
    return SpeechEvaluationService.get_dataset_stats(db)

@router.post("/evaluate", response_model=SpeechEvaluationResponse)
def evaluate_transcription(data: SpeechEvaluationRequest, db: Session = Depends(get_db)):
    """
    Evaluates a transcription hypothesis against a reference transcript or audio_id record.
    Returns Word Error Rate (WER), Character Error Rate (CER), and Accuracy %.
    """
    result = SpeechEvaluationService.evaluate_audio_record(
        db=db,
        hypothesis_transcript=data.hypothesis_transcript,
        audio_id=data.audio_id,
        reference_transcript=data.reference_transcript
    )
    return SpeechEvaluationResponse(**result)

@router.get("/benchmark")
def run_speech_benchmarks(db: Session = Depends(get_db)):
    """
    Executes benchmark evaluation across consented evaluation split records in kannada_speech_metadata.csv.
    """
    return SpeechEvaluationService.run_benchmark_suite(db)
