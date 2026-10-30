import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="farmer")  # "farmer" or "admin"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_schemes = relationship("SavedScheme", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # "farmer" or "assistant"
    text = Column(Text, nullable=False)
    text_kn = Column(Text, nullable=True)
    audio_url = Column(String(300), nullable=True)
    intent = Column(String(50), nullable=True)
    detected_entities = Column(Text, default='{}')  # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class AdminAudit(Base):
    __tablename__ = "admin_audits"

    id = Column(Integer, primary_key=True, index=True)
    admin_mobile = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
