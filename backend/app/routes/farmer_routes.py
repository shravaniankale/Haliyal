import json
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, FarmerProfile, FarmerSession
from ..schemas import (
    FarmerProfileUpdate,
    FarmerProfileResponse,
    FarmerSessionResponse,
    FarmerSessionCreateUpdate
)
from ..auth import require_current_user, get_current_user
from ..config import KARNATAKA_DISTRICTS, get_region_for_district
from ..services.district_service import DISTRICT_TALUKS

router = APIRouter(prefix="/api/farmer", tags=["Farmer Profile"])

@router.get("/districts")
def list_districts():
    """Returns all 31 Karnataka districts with regional classifications and taluks."""
    results = []
    for dist, data in KARNATAKA_DISTRICTS.items():
        results.append({
            "name": dist,
            "name_kn": data["kn"],
            "region": data["region"],
            "taluks": DISTRICT_TALUKS.get(dist, [dist])
        })
    return results

@router.get("/profile", response_model=FarmerProfileResponse)
def get_farmer_profile(current_user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    profile = current_user.profile
    if not profile:
        profile = FarmerProfile(
            user_id=current_user.id,
            email=current_user.email,
            district="Belagavi",
            taluk="Belagavi",
            preferred_language="kn",
            regional_speech_preference="North Karnataka",
            crops_grown="[]",
            conversation_state="collecting_information",
            consent_for_audio_storage="not_collected",
            auto_voice_response=getattr(current_user, "auto_voice_response", True),
            voice_input_enabled=getattr(current_user, "voice_input_enabled", True),
            speech_speed=getattr(current_user, "speech_speed", 1.0) or 1.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    crops_list = []
    try:
        crops_list = json.loads(profile.crops_grown) if profile.crops_grown else []
    except Exception:
        crops_list = []

    sec_crops = []
    try:
        sec_crops = json.loads(profile.secondary_crops) if getattr(profile, "secondary_crops", None) else []
    except Exception:
        sec_crops = []

    uname = getattr(current_user, "username", None) or current_user.name.lower().replace(" ", "_")
    email_val = getattr(current_user, "email", None) or getattr(profile, "email", None)

    return FarmerProfileResponse(
        id=profile.id,
        user_id=current_user.id,
        name=current_user.name,
        username=uname,
        email=email_val,
        mobile=current_user.mobile,
        district=profile.district,
        taluk=profile.taluk,
        village=profile.village,
        preferred_language=profile.preferred_language or "kn",
        regional_speech_preference=profile.regional_speech_preference or "North Karnataka",
        land_acres=profile.land_acres,
        land_unit=getattr(profile, "land_unit", "acres") or "acres",
        land_ownership=profile.land_ownership or "Own",
        irrigation_type=profile.irrigation_type or "Rainfed",
        farmer_category=profile.farmer_category or "Small & Marginal",
        primary_crop=getattr(profile, "primary_crop", None) or (crops_list[0] if crops_list else None),
        secondary_crops=sec_crops,
        crops_grown=crops_list,
        confirmed_fields=profile.confirmed_fields,
        missing_fields=profile.missing_fields,
        conversation_state=profile.conversation_state,
        consent_for_audio_storage=profile.consent_for_audio_storage,
        agricultural_season=profile.agricultural_season,
        soil_type=profile.soil_type,
        sowing_date=getattr(profile, "sowing_date", None),
        crop_stage=getattr(profile, "crop_stage", None),
        theme_preference=getattr(current_user, "theme_preference", "light") or "light",
        voice_gender_preference=getattr(current_user, "voice_gender_preference", "female") or "female",
        voice_assistant_enabled=getattr(current_user, "voice_assistant_enabled", True),
        auto_voice_response=getattr(current_user, "auto_voice_response", True),
        voice_input_enabled=getattr(current_user, "voice_input_enabled", True),
        speech_speed=getattr(current_user, "speech_speed", 1.0) or 1.0,
        account_created_at=current_user.created_at,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.put("/profile", response_model=FarmerProfileResponse)
def update_farmer_profile(data: FarmerProfileUpdate, current_user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")

    # Validation
    if data.name is not None:
        clean_name = data.name.strip()
        if not clean_name:
            raise HTTPException(status_code=400, detail="Name cannot be empty.")
        current_user.name = clean_name

    if data.username is not None:
        clean_uname = data.username.strip().lower()
        if clean_uname:
            if not re.match(r"^[a-zA-Z0-9_\.]{3,30}$", clean_uname):
                raise HTTPException(status_code=400, detail="Username must be 3-30 characters with alphanumeric, underscore, or dot.")
            # Check if taken by another user
            existing_uname = db.query(User).filter(User.username == clean_uname, User.id != current_user.id).first()
            if existing_uname:
                raise HTTPException(status_code=400, detail="Username is already taken by another farmer.")
            current_user.username = clean_uname

    if data.email is not None:
        clean_email = data.email.strip()
        if clean_email:
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean_email):
                raise HTTPException(status_code=400, detail="Invalid email address format.")
            current_user.email = clean_email
            profile.email = clean_email
        else:
            current_user.email = None
            profile.email = None

    if data.district is not None:
        clean_dist = data.district.strip()
        profile.district = clean_dist
        if clean_dist and not data.regional_speech_preference:
            profile.regional_speech_preference = get_region_for_district(clean_dist)

    if data.taluk is not None:
        clean_taluk = data.taluk.strip()
        profile.taluk = clean_taluk
    if data.village is not None:
        profile.village = data.village.strip()
    if data.preferred_language:
        profile.preferred_language = data.preferred_language
    if data.regional_speech_preference:
        profile.regional_speech_preference = data.regional_speech_preference
    if data.land_acres is not None:
        profile.land_acres = data.land_acres
    if data.land_ownership:
        profile.land_ownership = data.land_ownership
    if data.irrigation_type:
        profile.irrigation_type = data.irrigation_type
    if data.farmer_category:
        profile.farmer_category = data.farmer_category
    if data.crops_grown is not None:
        profile.crops_grown = json.dumps(data.crops_grown)
    if data.primary_crop is not None:
        clean_pc = data.primary_crop.strip()
        profile.primary_crop = clean_pc if clean_pc else None
    if data.secondary_crops is not None:
        profile.secondary_crops = json.dumps(data.secondary_crops)
    if data.confirmed_fields is not None:
        profile.confirmed_fields = data.confirmed_fields
    if data.missing_fields is not None:
        profile.missing_fields = data.missing_fields
    if data.conversation_state:
        profile.conversation_state = data.conversation_state
    if data.consent_for_audio_storage:
        profile.consent_for_audio_storage = data.consent_for_audio_storage
    if data.agricultural_season:
        profile.agricultural_season = data.agricultural_season
    if data.soil_type:
        profile.soil_type = data.soil_type
    if data.sowing_date:
        profile.sowing_date = data.sowing_date
    if data.crop_stage:
        profile.crop_stage = data.crop_stage

    # Website Settings
    if data.theme_preference:
        profile.theme_preference = data.theme_preference
        current_user.theme_preference = data.theme_preference
    if data.voice_gender_preference:
        profile.voice_gender_preference = data.voice_gender_preference
        current_user.voice_gender_preference = data.voice_gender_preference
    if data.voice_assistant_enabled is not None:
        profile.voice_assistant_enabled = data.voice_assistant_enabled
        current_user.voice_assistant_enabled = data.voice_assistant_enabled
    if data.auto_voice_response is not None:
        profile.auto_voice_response = data.auto_voice_response
        current_user.auto_voice_response = data.auto_voice_response
    if data.voice_input_enabled is not None:
        profile.voice_input_enabled = data.voice_input_enabled
        current_user.voice_input_enabled = data.voice_input_enabled
    if data.speech_speed is not None:
        profile.speech_speed = data.speech_speed
        current_user.speech_speed = data.speech_speed

    if data.primary_crop:
        profile.primary_crop = data.primary_crop
    if data.secondary_crops is not None:
        profile.secondary_crops = json.dumps(data.secondary_crops)
    if data.land_unit:
        profile.land_unit = data.land_unit

    db.commit()
    db.refresh(profile)
    db.refresh(current_user)

    crops_list = []
    try:
        crops_list = json.loads(profile.crops_grown) if profile.crops_grown else []
    except Exception:
        crops_list = []

    sec_crops = []
    try:
        sec_crops = json.loads(profile.secondary_crops) if getattr(profile, "secondary_crops", None) else []
    except Exception:
        sec_crops = []

    uname = getattr(current_user, "username", None) or current_user.name.lower().replace(" ", "_")
    email_val = getattr(current_user, "email", None) or getattr(profile, "email", None)

    return FarmerProfileResponse(
        id=profile.id,
        user_id=current_user.id,
        name=current_user.name,
        username=uname,
        email=email_val,
        mobile=current_user.mobile,
        district=profile.district,
        taluk=profile.taluk,
        village=profile.village,
        preferred_language=profile.preferred_language or "kn",
        regional_speech_preference=profile.regional_speech_preference or "North Karnataka",
        land_acres=profile.land_acres,
        land_unit=getattr(profile, "land_unit", "acres") or "acres",
        land_ownership=profile.land_ownership or "Own",
        irrigation_type=profile.irrigation_type or "Rainfed",
        farmer_category=profile.farmer_category or "Small & Marginal",
        primary_crop=getattr(profile, "primary_crop", None) or (crops_list[0] if crops_list else None),
        secondary_crops=sec_crops,
        crops_grown=crops_list,
        confirmed_fields=profile.confirmed_fields,
        missing_fields=profile.missing_fields,
        conversation_state=profile.conversation_state,
        consent_for_audio_storage=profile.consent_for_audio_storage,
        agricultural_season=profile.agricultural_season,
        soil_type=profile.soil_type,
        sowing_date=getattr(profile, "sowing_date", None),
        crop_stage=getattr(profile, "crop_stage", None),
        theme_preference=getattr(current_user, "theme_preference", "light") or "light",
        voice_gender_preference=getattr(current_user, "voice_gender_preference", "female") or "female",
        voice_assistant_enabled=getattr(current_user, "voice_assistant_enabled", True),
        auto_voice_response=getattr(current_user, "auto_voice_response", True),
        voice_input_enabled=getattr(current_user, "voice_input_enabled", True),
        speech_speed=getattr(current_user, "speech_speed", 1.0) or 1.0,
        account_created_at=current_user.created_at,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.delete("/profile")
def delete_farmer_profile(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes the farmer's saved profile and conversation records upon user self-determination.
    """
    profile = current_user.profile
    if profile:
        db.delete(profile)
    
    # Also clear conversation records for this user
    user_convs = db.query(FarmerSession).filter(
        FarmerSession.user_id_pseudonymous == f"USER_{current_user.id}"
    ).all()
    for s in user_convs:
        db.delete(s)
    
    db.commit()
    return {
        "status": "success",
        "message": "Farmer profile and conversation records successfully deleted upon user request."
    }
