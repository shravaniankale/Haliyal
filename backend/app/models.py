import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=True, index=True)
    email = Column(String(100), nullable=True, index=True)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="farmer")  # "farmer" or "admin"
    theme_preference = Column(String(20), default="light")
    voice_gender_preference = Column(String(20), default="female")
    voice_assistant_enabled = Column(Boolean, default=True)
    auto_voice_response = Column(Boolean, default=True)
    voice_input_enabled = Column(Boolean, default=True)
    speech_speed = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_schemes = relationship("SavedScheme", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    email = Column(String(100), nullable=True)
    district = Column(String(100), nullable=False)
    taluk = Column(String(100), nullable=False)
    village = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="kn")  # "kn" or "en"
    regional_speech_preference = Column(String(50), default="Standard Kannada")  # "North Karnataka", "South Karnataka", "Standard Kannada"
    land_acres = Column(Float, nullable=True)
    land_ownership = Column(String(50), default="Own")  # "Own" or "Tenant"
    irrigation_type = Column(String(50), default="Rainfed")  # "Rainfed", "Borewell", "Canal", "Drip"
    farmer_category = Column(String(50), default="Small & Marginal")  # "Small & Marginal", "Medium", "Large"
    crops_grown = Column(Text, default="[]")  # JSON string of crop names
    
    # Extended fields aligning with farmer_session_profile.csv
    confirmed_fields = Column(Text, nullable=True)
    missing_fields = Column(Text, nullable=True)
    conversation_state = Column(String(50), default="collecting_information")
    consent_for_audio_storage = Column(String(50), default="not_collected")
    agricultural_season = Column(String(50), nullable=True)
    soil_type = Column(String(100), nullable=True)
    theme_preference = Column(String(20), default="light")
    voice_gender_preference = Column(String(20), default="female")
    voice_assistant_enabled = Column(Boolean, default=True)
    auto_voice_response = Column(Boolean, default=True)
    voice_input_enabled = Column(Boolean, default=True)
    speech_speed = Column(Float, default=1.0)
    primary_crop = Column(String(100), nullable=True)
    secondary_crops = Column(Text, default="[]")
    land_unit = Column(String(20), default="acres")
    sowing_date = Column(String(50), nullable=True)
    crop_stage = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "PM-KISAN", "PMFBY", "DEMO-IRRIG-01"
    scheme_name = Column(String(200), nullable=False)
    scheme_name_kn = Column(String(200), nullable=False)
    scheme_type = Column(String(50), default="Central")  # "Central", "Karnataka State", "Synthetic Demonstration"
    scheme_category = Column(String(100), default="General Agriculture")  # "Income Support", "Crop Insurance", "Agricultural Credit", etc.
    department = Column(String(150), nullable=False)
    department_kn = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    description_kn = Column(Text, nullable=False)
    
    # Eligibility criteria
    eligibility_conditions = Column(Text, nullable=False)  # JSON structure with rules
    eligible_farmer_categories = Column(Text, default='["All"]')  # JSON list
    eligible_crops = Column(Text, default='["All"]')  # JSON list
    land_requirements = Column(String(255), nullable=True)
    max_land_acres = Column(Float, nullable=True)
    min_land_acres = Column(Float, nullable=True)
    required_ownership = Column(String(50), nullable=True)  # "Own", "Tenant", "Any"
    location_restrictions = Column(String(255), default="All Karnataka")  # "All Karnataka", "Rainfed Dryland Zones", etc.
    application_period = Column(String(150), default="Open Throughout Year")  # e.g., "Kharif Season (June-August)", etc.
    current_status = Column(String(50), default="Active")  # "Active", "Inactive", "Suspended", "Verification Required"
    
    # Benefits & Documents
    benefit_details = Column(Text, nullable=False)
    benefit_details_kn = Column(Text, nullable=False)
    required_documents = Column(Text, default='[]')  # JSON list
    application_steps = Column(Text, default='[]')  # JSON list
    
    # Verification & Official Sources
    official_url = Column(String(300), nullable=False)
    source_url = Column(String(300), nullable=True)
    verification_date = Column(String(50), nullable=False)
    verification_status = Column(String(50), default="Verified")  # "Verified" or "Synthetic Demo"
    active_status = Column(Boolean, default=True)
    image_url = Column(String(300), nullable=True)

    # Extended CSV integration fields (government_schemes.csv)
    scheme_code = Column(String(50), nullable=True, index=True)  # e.g., "SCM001", "DEMO001"
    eligibility_rule_json = Column(Text, nullable=True)
    record_type = Column(String(50), default="real_scheme")  # "real_scheme", "synthetic_demo"
    rag_document_id = Column(String(100), nullable=True)
    benefit_amount = Column(Float, nullable=True)
    benefit_frequency = Column(String(100), nullable=True)
    benefit_type = Column(String(100), nullable=True)
    exclusion_conditions = Column(Text, nullable=True)
    source_document_title = Column(String(255), nullable=True)
    source_published_date = Column(String(50), nullable=True)
    source_last_verified = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    saved_by = relationship("SavedScheme", back_populates="scheme", cascade="all, delete-orphan")


class SavedScheme(Base):
    __tablename__ = "saved_schemes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="saved_schemes")
    scheme = relationship("Scheme", back_populates="saved_by")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    title = Column(String(200), default="ಕೃಷಿ ಸಂವಾದ")
    topic = Column(String(100), default="General Agriculture")
    selected_language = Column(String(10), default="kn")
    selected_voice = Column(String(20), default="female")
    current_stage = Column(String(50), default="idle")
    confirmed_details = Column(Text, default="{}")
    missing_details = Column(Text, default="[]")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    analyses = relationship("AnalysisHistory", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # "farmer" or "assistant"
    text = Column(Text, nullable=False)
    text_kn = Column(Text, nullable=True)
    audio_url = Column(String(300), nullable=True)
    transcript = Column(Text, nullable=True)  # Exact recognized speech transcript
    topic = Column(String(100), nullable=True)
    intent = Column(String(50), nullable=True)
    detected_entities = Column(Text, default='{}')  # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class AnalysisHistory(Base):
    """
    Stores historical analysis records for authenticated farmers
    (Schemes evaluated, insurance checks, fertilizer recommendations, crop guidance).
    """
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True, index=True)
    topic = Column(String(100), nullable=False)
    crop_information = Column(String(100), nullable=True)
    season_information = Column(String(100), nullable=True)
    weather_used = Column(Text, nullable=True)  # JSON string
    recommendations = Column(Text, nullable=True)  # JSON string
    eligibility_results = Column(Text, nullable=True)  # JSON string
    source_references = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    conversation = relationship("Conversation", back_populates="analyses")


class AdminAudit(Base):
    __tablename__ = "admin_audits"

    id = Column(Integer, primary_key=True, index=True)
    admin_mobile = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


# --- 5 CSV DATASET INTEGRATION MODELS ---

class RegionalVocabulary(Base):
    __tablename__ = "regional_vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(String(50), unique=True, index=True, nullable=False)
    local_term = Column(String(100), index=True, nullable=False)
    standard_kannada_term = Column(String(100), index=True, nullable=False)
    english_meaning = Column(String(255), nullable=True)
    concept_id = Column(String(100), index=True, nullable=True)
    concept_category = Column(String(50), nullable=True)
    district_or_region = Column(String(100), nullable=True)
    alternative_spellings = Column(Text, nullable=True)
    example_sentence = Column(Text, nullable=True)
    verified_by = Column(String(100), nullable=True)
    verification_status = Column(String(50), default="verified")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SpeechMetadata(Base):
    __tablename__ = "speech_metadata"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(String(50), unique=True, index=True, nullable=False)
    audio_file_path_or_uri = Column(String(255), nullable=False)
    transcript_verbatim = Column(Text, nullable=False)
    transcript_standard_kannada = Column(Text, nullable=True)
    english_translation = Column(Text, nullable=True)
    district_or_region = Column(String(100), index=True, nullable=True)
    taluk_optional = Column(String(100), nullable=True)
    speaker_pseudonymous_id = Column(String(100), nullable=True)
    speech_language = Column(String(20), default="kn")
    code_mixed_languages = Column(String(50), nullable=True)
    concept_labels = Column(Text, nullable=True)
    audio_duration_seconds = Column(Float, nullable=True)
    audio_quality = Column(String(50), default="high")
    consent_status = Column(String(50), default="consented")
    consent_record_reference = Column(String(100), nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    review_status = Column(String(50), default="approved")
    dataset_split = Column(String(50), default="test")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class FarmerSession(Base):
    __tablename__ = "farmer_sessions"

    id = Column(Integer, primary_key=True, index=True)
    farmer_session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id_pseudonymous = Column(String(100), nullable=True)
    district = Column(String(100), nullable=False)
    taluk = Column(String(100), nullable=True)
    village_optional = Column(String(100), nullable=True)
    regional_language_preference = Column(String(100), nullable=True)
    preferred_language = Column(String(20), default="kn")
    speech_style_mode = Column(String(50), default="district_auto")
    crops_grown = Column(Text, nullable=True)
    land_area = Column(Float, nullable=True)
    land_area_unit = Column(String(20), default="acre")
    land_ownership = Column(String(50), nullable=True)
    agricultural_season = Column(String(50), nullable=True)
    irrigation_type = Column(String(50), nullable=True)
    assistance_required = Column(Text, nullable=True)
    farmer_category_optional = Column(String(100), nullable=True)
    soil_type_optional = Column(String(100), nullable=True)
    confirmed_fields = Column(Text, nullable=True)
    missing_fields = Column(Text, nullable=True)
    conversation_state = Column(String(50), default="collecting_information")
    consent_for_audio_storage = Column(String(50), default="not_collected")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class DatasetDictionary(Base):
    __tablename__ = "dataset_dictionary"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(100), unique=True, index=True, nullable=False)
    purpose = Column(Text, nullable=False)
    key_fields = Column(Text, nullable=False)
    important_note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
