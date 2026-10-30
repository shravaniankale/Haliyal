from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, FarmerProfile
from ..schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from ..auth import hash_password, verify_password, create_access_token, require_current_user
from ..config import get_region_for_district

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    # Check if mobile already registered
    existing = db.query(User).filter(User.mobile == data.mobile.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered. Please login instead."
        )

    # Determine regional classification from district
    auto_region = get_region_for_district(data.district)
    selected_speech = data.preferred_speech_style if data.preferred_speech_style else auto_region

    clean_name = data.name.strip()
    username = data.username.strip() if data.username and data.username.strip() else clean_name.lower().replace(" ", "_")
    email = data.email.strip() if data.email and data.email.strip() else None

    # Create User
    new_user = User(
        name=clean_name,
        username=username,
        email=email,
        mobile=data.mobile.strip(),
        password_hash=hash_password(data.password),
        role="farmer",
        theme_preference="light",
        voice_gender_preference="female",
        auto_voice_response=True,
        voice_input_enabled=True,
        speech_speed=1.0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create associated Farmer Profile
    profile = FarmerProfile(
        user_id=new_user.id,
        email=email,
        district=data.district.strip(),
        taluk=data.taluk.strip(),
        village=data.village.strip() if data.village else None,
        preferred_language=data.preferred_language or "kn",
        regional_speech_preference=selected_speech,
        land_ownership="Own",
        irrigation_type="Rainfed",
        farmer_category="Small & Marginal",
        crops_grown="[]",
        auto_voice_response=True,
        voice_input_enabled=True,
        speech_speed=1.0
    )
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": new_user.id, "role": new_user.role})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
        regional_speech=selected_speech,
        district=data.district.strip()
    )

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == data.mobile.strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password."
        )

    token = create_access_token({"sub": user.id, "role": user.role})
    profile = user.profile
    regional_speech = profile.regional_speech_preference if profile else "Standard Kannada"
    district = profile.district if profile else "Belagavi"

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        regional_speech=regional_speech,
        district=district
    )

@router.get("/me")
def get_me(current_user: User = Depends(require_current_user)):
    profile = current_user.profile
    return {
        "user": UserResponse.model_validate(current_user),
        "district": profile.district if profile else "Belagavi",
        "taluk": profile.taluk if profile else "",
        "regional_speech_preference": profile.regional_speech_preference if profile else "Standard Kannada",
        "preferred_language": profile.preferred_language if profile else "kn",
        "theme_preference": getattr(current_user, "theme_preference", "light") or "light",
        "voice_gender_preference": getattr(current_user, "voice_gender_preference", "female") or "female",
        "auto_voice_response": getattr(current_user, "auto_voice_response", True),
        "voice_input_enabled": getattr(current_user, "voice_input_enabled", True),
        "speech_speed": getattr(current_user, "speech_speed", 1.0) or 1.0
    }
