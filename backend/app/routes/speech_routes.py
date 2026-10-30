from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..schemas import TTSRequest, STTResponse
from ..services.kannada_speech import KannadaSpeechService

router = APIRouter(prefix="/api/speech", tags=["Kannada Speech Technology"])

@router.post("/synthesize")
def synthesize_speech(data: TTSRequest):
    """
    Synthesizes Kannada text into authentic neural audio using gTTS (lang='kn').
    Returns public streaming URL.
    """
    if not data.text or not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    audio_url, status_msg = KannadaSpeechService.synthesize_kannada_speech(
        text=data.text,
        regional_style=data.regional_preference or "Standard Kannada"
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
        "language": "kn",
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
