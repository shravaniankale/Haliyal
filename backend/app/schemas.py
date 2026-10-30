from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str
    mobile: str
    password: str
    district: str
    taluk: str
    village: Optional[str] = None
    preferred_language: Optional[str] = "kn"
    preferred_speech_style: Optional[str] = None  # North Karnataka, South Karnataka, Standard Kannada

class UserLogin(BaseModel):
    mobile: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    mobile: str
    role: str
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
    district: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None
    preferred_language: Optional[str] = None
    regional_speech_preference: Optional[str] = None
    land_acres: Optional[float] = None
    land_ownership: Optional[str] = None
    irrigation_type: Optional[str] = None
    farmer_category: Optional[str] = None
    crops_grown: Optional[List[str]] = None

class FarmerProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    mobile: str
    district: str
    taluk: str
    village: Optional[str]
    preferred_language: str
    regional_speech_preference: str
    land_acres: Optional[float]
    land_ownership: str
    irrigation_type: str
    farmer_category: str
    crops_grown: List[str]
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

class SchemeCreate(SchemeBase):
    pass

class SchemeResponse(SchemeBase):
    id: int
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True

# --- Eligibility Schemas ---
class EligibilityCheckRequest(BaseModel):
    district: str
    crop: str
    land_acres: Optional[float] = None
    land_ownership: Optional[str] = "Own"  # "Own" or "Tenant"
    season: Optional[str] = "Kharif"      # "Kharif", "Rabi", "Summer"
    irrigation_type: Optional[str] = "Rainfed" # "Rainfed", "Borewell", "Canal", "Drip"
    farmer_category: Optional[str] = "Small & Marginal" # "Small & Marginal", "General", "SC/ST", "Women"

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
    regional_preference: Optional[str] = "North Karnataka"

class ChatResponse(BaseModel):
    reply: str
    reply_kn: str
    audio_url: Optional[str] = None
    intent: Optional[str] = "general_query"
    detected_entities: Dict[str, Any] = {}
    recommended_schemes: List[Dict[str, Any]] = []

class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "kn"
    regional_preference: Optional[str] = "Standard Kannada"

class STTResponse(BaseModel):
    transcript: str
    language: str
    confidence: float

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
