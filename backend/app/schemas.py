from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str
    username: Optional[str] = None
    email: Optional[str] = None
    mobile: str
    password: str
    district: str
    taluk: str
    village: Optional[str] = None
    preferred_language: Optional[str] = "kn"
    preferred_speech_style: Optional[str] = None  # North Karnataka, South Karnataka, Standard Kannada
    regional_speech_preference: Optional[str] = None
    land_acres: Optional[float] = None
    land_ownership: Optional[str] = "Own"
    farmer_category: Optional[str] = "Small & Marginal"
    irrigation_type: Optional[str] = "Rainfed"
    primary_crop: Optional[str] = None
    crops_grown: Optional[List[str]] = None
    crops: Optional[List[str]] = None

class UserLogin(BaseModel):
    mobile: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    username: Optional[str] = None
    email: Optional[str] = None
    mobile: str
    role: str
    theme_preference: Optional[str] = "light"
    voice_gender_preference: Optional[str] = "female"
    voice_assistant_enabled: Optional[bool] = True
    auto_voice_response: Optional[bool] = True
    voice_input_enabled: Optional[bool] = True
    speech_speed: Optional[float] = 1.0
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    regional_speech: str
    district: str

# --- Profile Schemas ---
class FarmerProfileUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None
    preferred_language: Optional[str] = None
    regional_speech_preference: Optional[str] = None
    land_acres: Optional[float] = None
    land_unit: Optional[str] = "acres"
    land_ownership: Optional[str] = None
    irrigation_type: Optional[str] = None
    farmer_category: Optional[str] = None
    primary_crop: Optional[str] = None
    secondary_crops: Optional[List[str]] = None
    crops_grown: Optional[List[str]] = None
    confirmed_fields: Optional[str] = None
    missing_fields: Optional[str] = None
    conversation_state: Optional[str] = None
    consent_for_audio_storage: Optional[str] = None
    agricultural_season: Optional[str] = None
    soil_type: Optional[str] = None
    sowing_date: Optional[str] = None
    crop_stage: Optional[str] = None
    theme_preference: Optional[str] = "light"
    voice_gender_preference: Optional[str] = "female"
    voice_assistant_enabled: Optional[bool] = None
    auto_voice_response: Optional[bool] = None
    voice_input_enabled: Optional[bool] = None
    speech_speed: Optional[float] = None

class FarmerProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    username: Optional[str] = None
    email: Optional[str] = None
    mobile: str
    district: str
    taluk: str
    village: Optional[str] = None
    preferred_language: str
    regional_speech_preference: str
    land_acres: Optional[float] = None
    land_unit: Optional[str] = "acres"
    land_ownership: str
    irrigation_type: str
    farmer_category: str
    primary_crop: Optional[str] = None
    secondary_crops: Optional[List[str]] = []
    crops_grown: List[str]
    confirmed_fields: Optional[str] = None
    missing_fields: Optional[str] = None
    conversation_state: Optional[str] = None
    consent_for_audio_storage: Optional[str] = None
    agricultural_season: Optional[str] = None
    soil_type: Optional[str] = None
    sowing_date: Optional[str] = None
    crop_stage: Optional[str] = None
    theme_preference: Optional[str] = "light"
    voice_gender_preference: Optional[str] = "female"
    voice_assistant_enabled: bool = True
    auto_voice_response: bool = True
    voice_input_enabled: bool = True
    speech_speed: float = 1.0
    account_created_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# --- Scheme Schemas ---
class SchemeBase(BaseModel):
    scheme_id: str
    scheme_name: str
    scheme_name_kn: str
    scheme_type: str
    department: str
    department_kn: str
    description: str
    description_kn: str
    eligibility_conditions: str
    eligible_farmer_categories: List[str]
    eligible_crops: List[str]
    land_requirements: Optional[str] = None
    max_land_acres: Optional[float] = None
    min_land_acres: Optional[float] = None
    required_ownership: Optional[str] = None
    benefit_details: str
    benefit_details_kn: str
    required_documents: List[str]
    application_steps: List[str]
    official_url: str
    source_url: Optional[str] = None
    verification_date: str
    verification_status: str
    active_status: bool = True
    image_url: Optional[str] = None

    # Extended CSV columns
    scheme_code: Optional[str] = None
    eligibility_rule_json: Optional[str] = None
    record_type: Optional[str] = "real_scheme"
    rag_document_id: Optional[str] = None
    benefit_amount: Optional[float] = None
    benefit_frequency: Optional[str] = None
    benefit_type: Optional[str] = None
    exclusion_conditions: Optional[str] = None
    source_document_title: Optional[str] = None
    source_published_date: Optional[str] = None
    source_last_verified: Optional[str] = None

class SchemeCreate(SchemeBase):
    pass

class SchemeUpdate(BaseModel):
    scheme_name: Optional[str] = None
    scheme_name_kn: Optional[str] = None
    scheme_type: Optional[str] = None
    department: Optional[str] = None
    department_kn: Optional[str] = None
    description: Optional[str] = None
    description_kn: Optional[str] = None
    eligibility_conditions: Optional[str] = None
    eligible_farmer_categories: Optional[List[str]] = None
    eligible_crops: Optional[List[str]] = None
    land_requirements: Optional[str] = None
    max_land_acres: Optional[float] = None
    min_land_acres: Optional[float] = None
    required_ownership: Optional[str] = None
    benefit_details: Optional[str] = None
    benefit_details_kn: Optional[str] = None
    required_documents: Optional[List[str]] = None
    application_steps: Optional[List[str]] = None
    official_url: Optional[str] = None
    source_url: Optional[str] = None
    verification_date: Optional[str] = None
    verification_status: Optional[str] = None
    active_status: Optional[bool] = None
    image_url: Optional[str] = None

class SchemeResponse(SchemeBase):
    id: int
    created_at: Optional[datetime] = None
    is_saved: bool = False

    class Config:
        from_attributes = True

# --- Eligibility Schemas ---
class EligibilityCheckRequest(BaseModel):
    district: str
    crop: str
    land_acres: Optional[float] = None
    land_ownership: Optional[str] = "Own"
    season: Optional[str] = "Kharif"
    irrigation_type: Optional[str] = "Rainfed"
    farmer_category: Optional[str] = "Small & Marginal"

class EligibilityItemResult(BaseModel):
    scheme_id: str
    scheme_name: str
    scheme_name_kn: str
    scheme_type: str
    department: str
    status: str  # "PASS", "FAIL", "UNKNOWN"
    explanation: str
    explanation_kn: str
    matched_conditions: List[str]
    failing_conditions: List[str]
    missing_information: List[str]
    required_documents: List[str]
    benefit_details: str
    benefit_details_kn: str
    official_url: str
    verification_status: str

class EligibilityResponse(BaseModel):
    total_evaluated: int
    eligible_count: int
    results: List[EligibilityItemResult]

# --- Chat & Voice Schemas ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default-session"
    user_id: Optional[int] = None
    language: Optional[str] = "kn"
    regional_preference: Optional[str] = None
    voice_gender: Optional[str] = None
    speech_speed: Optional[float] = None
    auto_voice_response: Optional[bool] = True

class ChatResponse(BaseModel):
    reply: str
    reply_kn: str
    audio_url: Optional[str] = None
    intent: Optional[str] = "general_query"
    topic: Optional[str] = "General Agriculture"
    detected_entities: Dict[str, Any] = {}
    recommended_schemes: List[Dict[str, Any]] = []
    rag_citations: Optional[List[Dict[str, Any]]] = []
    rag_confidence: Optional[float] = None
    rag_mode: Optional[str] = None
    is_agriculture_related: bool = True
    session_details: Optional[Dict[str, Any]] = None
    current_stage: Optional[str] = None
    confirmed_details: Optional[Dict[str, Any]] = None
    missing_details: Optional[List[str]] = None
    profile_updated: Optional[bool] = True

# --- Conversation & History Schemas ---
class ChatMessageItem(BaseModel):
    id: int
    conversation_id: int
    sender: str
    text: str
    text_kn: Optional[str] = None
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    topic: Optional[str] = None
    intent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationListItem(BaseModel):
    id: int
    session_id: str
    title: str
    topic: str
    selected_language: str
    selected_voice: str
    message_count: int
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    id: int
    session_id: str
    title: str
    topic: str
    selected_language: str
    selected_voice: str
    current_stage: str
    confirmed_details: Dict[str, Any]
    missing_details: List[str]
    messages: List[ChatMessageItem]
    created_at: datetime
    updated_at: datetime

class NewConversationRequest(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = "General Agriculture"
    language: Optional[str] = "kn"
    voice_gender: Optional[str] = "female"

class AnalysisHistoryItem(BaseModel):
    id: int
    conversation_id: Optional[int] = None
    topic: str
    crop_information: Optional[str] = None
    season_information: Optional[str] = None
    weather_used: Optional[str] = None
    recommendations: Optional[str] = None
    eligibility_results: Optional[str] = None
    source_references: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- RAG Specific Schemas ---
class RAGQueryRequest(BaseModel):
    query: str
    language: Optional[str] = "kn"
    top_k: Optional[int] = 3

class RAGCitation(BaseModel):
    doc_name: str
    page_number: int
    scheme_name: str
    scheme_code: Optional[str] = None
    similarity_score: float
    excerpt: str

class RAGQueryResponse(BaseModel):
    query: str
    available: bool
    answer_en: str
    answer_kn: str
    citations: List[RAGCitation]
    confidence: float
    generation_mode: str
    gemini_api_used: bool

class RAGIngestResponse(BaseModel):
    status: str
    collection_name: str
    total_chunks: int
    indexed_documents: Optional[List[str]] = []
    persist_directory: str
    reindexed: bool

class RAGStatusResponse(BaseModel):
    status: str
    collection_name: str
    total_chunks: int
    total_documents: int
    documents: List[str]
    persist_directory: str
    embedding_model: str
    gemini_api_configured: bool

class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "kn"
    regional_preference: Optional[str] = "Standard Kannada"
    voice_gender: Optional[str] = "female"
    speech_speed: Optional[float] = 1.0

class STTResponse(BaseModel):
    transcript: str
    language: str
    confidence: float
    normalized_transcript: Optional[str] = None

# --- Loan Schemas ---
class LoanCalcRequest(BaseModel):
    amount: float
    interest_rate: float
    tenure_months: int

class LoanCalcResponse(BaseModel):
    monthly_emi: float
    total_interest: float
    total_payment: float
    principal: float

# --- Market & Weather ---
class MarketPriceItem(BaseModel):
    crop: str
    crop_kn: str
    market: str
    district: str
    min_price: float
    max_price: float
    modal_price: float
    unit: str = "₹ / Quintal"
    date: str
    is_historical: bool = False

class WeatherData(BaseModel):
    district: str
    district_kn: str
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    condition: str
    condition_kn: str
    last_updated: str
    is_live: bool

# --- CSV Dataset Schemas ---
class RegionalVocabularyResponse(BaseModel):
    id: int
    term_id: str
    local_term: str
    standard_kannada_term: str
    english_meaning: Optional[str] = None
    concept_id: Optional[str] = None
    concept_category: Optional[str] = None
    district_or_region: Optional[str] = None
    alternative_spellings: Optional[str] = None
    example_sentence: Optional[str] = None
    verified_by: Optional[str] = None
    verification_status: str = "verified"
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class VocabularyNormalizeRequest(BaseModel):
    text: str
    region: Optional[str] = None

class VocabularyNormalizeResponse(BaseModel):
    original_text: str
    normalized_text: str
    detected_local_terms: List[Dict[str, Any]] = []
    applied_concepts: List[str] = []

class SpeechMetadataResponse(BaseModel):
    id: int
    audio_id: str
    audio_file_path_or_uri: str
    transcript_verbatim: str
    transcript_standard_kannada: Optional[str] = None
    english_translation: Optional[str] = None
    district_or_region: Optional[str] = None
    taluk_optional: Optional[str] = None
    speaker_pseudonymous_id: Optional[str] = None
    speech_language: str = "kn"
    code_mixed_languages: Optional[str] = None
    concept_labels: Optional[str] = None
    audio_duration_seconds: Optional[float] = None
    audio_quality: str = "high"
    consent_status: str = "consented"
    consent_record_reference: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_status: str = "approved"
    dataset_split: str = "test"
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class SpeechEvaluationRequest(BaseModel):
    audio_id: Optional[str] = None
    hypothesis_transcript: str
    reference_transcript: Optional[str] = None

class SpeechEvaluationResponse(BaseModel):
    reference: str
    hypothesis: str
    word_error_rate: float
    character_error_rate: float
    accuracy_percentage: float
    is_acceptable: bool

class FarmerSessionResponse(BaseModel):
    id: int
    farmer_session_id: str
    user_id_pseudonymous: Optional[str] = None
    district: str
    taluk: Optional[str] = None
    village_optional: Optional[str] = None
    regional_language_preference: Optional[str] = None
    preferred_language: str = "kn"
    speech_style_mode: str = "district_auto"
    crops_grown: Optional[str] = None
    land_area: Optional[float] = None
    land_area_unit: str = "acre"
    land_ownership: Optional[str] = None
    agricultural_season: Optional[str] = None
    irrigation_type: Optional[str] = None
    assistance_required: Optional[str] = None
    farmer_category_optional: Optional[str] = None
    soil_type_optional: Optional[str] = None
    confirmed_fields: Optional[str] = None
    missing_fields: Optional[str] = None
    conversation_state: str = "collecting_information"
    consent_for_audio_storage: str = "not_collected"
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FarmerSessionCreateUpdate(BaseModel):
    district: Optional[str] = None
    taluk: Optional[str] = None
    village_optional: Optional[str] = None
    regional_language_preference: Optional[str] = None
    preferred_language: Optional[str] = "kn"
    crops_grown: Optional[str] = None
    land_area: Optional[float] = None
    land_area_unit: Optional[str] = "acre"
    land_ownership: Optional[str] = None
    agricultural_season: Optional[str] = None
    irrigation_type: Optional[str] = None
    assistance_required: Optional[str] = None
    farmer_category_optional: Optional[str] = None
    soil_type_optional: Optional[str] = None
    confirmed_fields: Optional[str] = None
    missing_fields: Optional[str] = None
    conversation_state: Optional[str] = None
    consent_for_audio_storage: Optional[str] = None
    notes: Optional[str] = None

class DatasetDictionaryResponse(BaseModel):
    id: int
    file_name: str
    purpose: str
    key_fields: str
    important_note: str

    class Config:
        from_attributes = True
