import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, FarmerProfile
from ..schemas import FarmerProfileUpdate, FarmerProfileResponse
from ..auth import require_current_user
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
            district="Belagavi",
            taluk="Belagavi",
            preferred_language="kn",
            regional_speech_preference="North Karnataka",
            crops_grown="[]"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    crops_list = []
    try:
        crops_list = json.loads(profile.crops_grown) if profile.crops_grown else []
    except Exception:
        crops_list = []

    return FarmerProfileResponse(
        id=profile.id,
        user_id=current_user.id,
        name=current_user.name,
        mobile=current_user.mobile,
        district=profile.district,
        taluk=profile.taluk,
        village=profile.village,
        preferred_language=profile.preferred_language,
        regional_speech_preference=profile.regional_speech_preference,
        land_acres=profile.land_acres,
        land_ownership=profile.land_ownership,
        irrigation_type=profile.irrigation_type,
        farmer_category=profile.farmer_category,
        crops_grown=crops_list,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.put("/profile", response_model=FarmerProfileResponse)
def update_farmer_profile(data: FarmerProfileUpdate, current_user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")

    if data.name:
        current_user.name = data.name.strip()
    if data.district:
        profile.district = data.district.strip()
        # If user changed district and didn't explicitly override regional speech, auto update
        if not data.regional_speech_preference:
            profile.regional_speech_preference = get_region_for_district(data.district)
    if data.taluk:
        profile.taluk = data.taluk.strip()
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

    db.commit()
    db.refresh(profile)
    db.refresh(current_user)

    crops_list = []
    try:
        crops_list = json.loads(profile.crops_grown) if profile.crops_grown else []
    except Exception:
        crops_list = []

    return FarmerProfileResponse(
        id=profile.id,
        user_id=current_user.id,
        name=current_user.name,
        mobile=current_user.mobile,
        district=profile.district,
        taluk=profile.taluk,
        village=profile.village,
        preferred_language=profile.preferred_language,
        regional_speech_preference=profile.regional_speech_preference,
        land_acres=profile.land_acres,
        land_ownership=profile.land_ownership,
        irrigation_type=profile.irrigation_type,
        farmer_category=profile.farmer_category,
        crops_grown=crops_list,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )
