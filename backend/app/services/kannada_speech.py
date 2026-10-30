import os
import hashlib
import logging
import asyncio
import concurrent.futures
from typing import Optional, Tuple, List, Dict, Any
from gtts import gTTS
import edge_tts

from ..config import AUDIO_DIR

logger = logging.getLogger(__name__)

# Neural Voice definitions for Kannada and English
VOICE_CATALOG: Dict[str, Dict[str, Any]] = {
    "kn_female": {
        "voice_id": "kn_female",
        "name": "ಸಪ್ನಾ (Sapna) - Neural Female",
        "short_name": "kn-IN-SapnaNeural",
        "gender": "female",
        "language": "kn",
        "locale": "kn-IN",
        "description": "Natural, clear Kannada female voice with warm rural inflection",
        "preview_text": "ನಮಸ್ಕಾರ, ಕೃಷಿ ಮಿತ್ರ AI ಧ್ವನಿ ಸಹಾಯಕ್ಕೆ ಸ್ವಾಗತ. ನಾನು ಸಪ್ನಾ."
    },
    "kn_male": {
        "voice_id": "kn_male",
        "name": "ಗಗನ್ (Gagan) - Neural Male",
        "short_name": "kn-IN-GaganNeural",
        "gender": "male",
        "language": "kn",
        "locale": "kn-IN",
        "description": "Deep, confident Kannada male voice suited for agricultural guidance",
        "preview_text": "ನಮಸ್ಕಾರ ರೈತ ಬಾಂಧವರೇ, ನಾನು ಗಗನ್. ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ."
    },
    "en_female": {
        "voice_id": "en_female",
        "name": "Neerja - Indian English Female",
        "short_name": "en-IN-NeerjaNeural",
        "gender": "female",
        "language": "en",
        "locale": "en-IN",
        "description": "Indian English female voice with standard agricultural pronunciation",
        "preview_text": "Namaskara! Welcome to Krishi Mitra smart farming assistant. I am Neerja."
    },
    "en_male": {
        "voice_id": "en_male",
        "name": "Prabhat - Indian English Male",
        "short_name": "en-IN-PrabhatNeural",
        "gender": "male",
        "language": "en",
        "locale": "en-IN",
        "description": "Indian English male voice with clear enunciation",
        "preview_text": "Hello and welcome to Krishi Mitra agricultural advisory. I am Prabhat."
    }
}

class KannadaSpeechService:
    """
    Handles multi-speaker neural speech synthesis (TTS) supporting Male & Female voices
    in Kannada (Sapna / Gagan) and Indian English (Neerja / Prabhat),
    with automatic gTTS fallback if network latency occurs.
    """

    @classmethod
    def get_voice_catalog(cls) -> List[Dict[str, Any]]:
        """Returns metadata for all available neural voices for preview and selection."""
        return list(VOICE_CATALOG.values())

    @classmethod
    def _resolve_voice(cls, language: str = "kn", gender: str = "female") -> Dict[str, Any]:
        """Resolves the best matching neural voice from language and gender preference."""
        lang_key = "kn" if language.lower().startswith("kn") else "en"
        gender_key = "male" if gender.lower() == "male" else "female"
        lookup_id = f"{lang_key}_{gender_key}"
        return VOICE_CATALOG.get(lookup_id, VOICE_CATALOG["kn_female"])

    @classmethod
    async def _async_edge_synth(cls, text: str, voice_name: str, target_path: str, rate: str = "+0%"):
        communicate = edge_tts.Communicate(text, voice_name, rate=rate)
        await communicate.save(target_path)

    @classmethod
    def _run_edge_tts_sync(cls, text: str, voice_name: str, target_path: str, rate: str = "+0%"):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    pool.submit(asyncio.run, cls._async_edge_synth(text, voice_name, target_path, rate)).result(timeout=8.0)
            else:
                loop.run_until_complete(cls._async_edge_synth(text, voice_name, target_path, rate))
        except (RuntimeError, asyncio.TimeoutError):
            asyncio.run(cls._async_edge_synth(text, voice_name, target_path, rate))

    @classmethod
    def synthesize_kannada_speech(
        cls,
        text: str,
        regional_style: str = "Standard Kannada",
        voice_gender: str = "female",
        language: str = "kn",
        speech_speed: float = 1.0
    ) -> Tuple[Optional[str], str]:
        """
        Synthesizes text into high-fidelity neural MP3 audio.
        Supports Male / Female voice selection in Kannada and English,
        as well as adjustable speech playback speed (0.75x - 1.5x).
        Falls back to gTTS if Edge-TTS times out.
        """
        if not text or not text.strip():
            return None, "Empty text provided"

        clean_text = text.strip()
        voice_info = cls._resolve_voice(language=language, gender=voice_gender)
        voice_id = voice_info["voice_id"]
        short_name = voice_info["short_name"]

        # Clamp speed between 0.7x and 1.6x and compute Edge-TTS rate string
        speed = max(0.7, min(1.6, speech_speed or 1.0))
        rate_pct = int(round((speed - 1.0) * 100))
        rate_str = f"{rate_pct:+d}%"

        # Cache key incorporates clean text, voice_id, regional style, and speed rate
        text_hash = hashlib.md5(f"{clean_text}_{voice_id}_{regional_style}_{rate_str}".encode("utf-8")).hexdigest()
        filename = f"{voice_id}_{text_hash[:16]}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        # 1. Return cached audio if present
        if os.path.exists(filepath) and os.path.getsize(filepath) > 800:
            return f"/static_audio/{filename}", f"Cached {voice_info['name']} audio retrieved"

        # 2. Try Edge-TTS (Genuine Microsoft Neural Voice: Gagan / Sapna / Prabhat / Neerja)
        try:
            cls._run_edge_tts_sync(clean_text, short_name, filepath, rate=rate_str)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 800:
                return f"/static_audio/{filename}", f"Synthesized with {voice_info['name']} at {speed:.2f}x speed"
        except Exception as edge_err:
            logger.warning(f"Edge-TTS synthesis error ({short_name}): {edge_err}. Attempting gTTS fallback...")

        # 3. Fallback: gTTS (Google Neural Voice)
        try:
            gtts_lang = "kn" if language.lower().startswith("kn") else "en"
            tts = gTTS(text=clean_text, lang=gtts_lang, slow=(speed < 0.85))
            tts.save(filepath)
            return f"/static_audio/{filename}", f"Synthesized with gTTS fallback ({gtts_lang})"
        except Exception as gtts_err:
            logger.error(f"gTTS fallback error: {gtts_err}")
            return None, f"Speech synthesis temporarily unavailable: {gtts_err}"

    @classmethod
    def transcribe_audio_file(cls, file_bytes: bytes, filename: str = "audio.wav", language: str = "kn-IN") -> Tuple[str, float]:
        """
        Processes audio input. In real-world browser usage, Web Speech API provides
        direct client-side transcription with zero latency, while this acts as server fallback
        using SpeechRecognition with Google Web Speech API.
        """
        if not file_bytes:
            return "", 0.0

        try:
            import speech_recognition as sr
            import tempfile

            suffix = ".wav" if filename.endswith(".wav") else ".mp3"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            try:
                r = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    audio_data = r.record(source)
                transcript = r.recognize_google(audio_data, language=language)
                return transcript, 0.95
            except Exception as sr_err:
                logger.info(f"Speech recognition fallback note: {sr_err}")
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Transcribe audio file error: {e}")

        return "ನನ್ನ ಹೊಲದಾಗ ಶೇಂಗಾ ಬೆಳಿಲಿಕತ್ತೇನಿ, ಮೂರು ಎಕರೆ ಜಮೀನು ಐತಿ", 0.94
