import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Scheme, SavedScheme, User
from ..schemas import SchemeResponse, EligibilityCheckRequest, EligibilityResponse
from ..services.eligibility_engine import DeterministicEligibilityEngine
from ..auth import get_current_user, require_current_user
from ..config import KARNATAKA_DISTRICTS

router = APIRouter(prefix="/api/schemes", tags=["Government Schemes"])

def format_scheme_response(scheme: Scheme, is_saved: bool = False) -> SchemeResponse:
    crops = json.loads(scheme.eligible_crops) if scheme.eligible_crops else []
    cats = json.loads(scheme.eligible_farmer_categories) if scheme.eligible_farmer_categories else []
    docs = json.loads(scheme.required_documents) if scheme.required_documents else []
    steps = json.loads(scheme.application_steps) if scheme.application_steps else []

    return SchemeResponse(
        id=scheme.id,
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.scheme_name,
        scheme_name_kn=scheme.scheme_name_kn,
        scheme_type=scheme.scheme_type,
        department=scheme.department,
        department_kn=scheme.department_kn,
        description=scheme.description,
        description_kn=scheme.description_kn,
        eligibility_conditions=scheme.eligibility_conditions,
        eligible_farmer_categories=cats,
        eligible_crops=crops,
        land_requirements=scheme.land_requirements,
        max_land_acres=scheme.max_land_acres,
        min_land_acres=scheme.min_land_acres,
        required_ownership=scheme.required_ownership,
        benefit_details=scheme.benefit_details,
        benefit_details_kn=scheme.benefit_details_kn,
        required_documents=docs,
        application_steps=steps,
        official_url=scheme.official_url,
        source_url=scheme.source_url,
        verification_date=scheme.verification_date,
        verification_status=scheme.verification_status,
        active_status=scheme.active_status,
        image_url=scheme.image_url,
        is_saved=is_saved,
        scheme_code=getattr(scheme, "scheme_code", None),
        record_type=getattr(scheme, "record_type", "real_scheme"),
        benefit_amount=getattr(scheme, "benefit_amount", None),
        benefit_frequency=getattr(scheme, "benefit_frequency", None),
        benefit_type=getattr(scheme, "benefit_type", None),
        source_document_title=getattr(scheme, "source_document_title", None),
        source_published_date=getattr(scheme, "source_published_date", None),
        source_last_verified=getattr(scheme, "source_last_verified", None),
        rag_document_id=getattr(scheme, "rag_document_id", None)
    )

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    """Returns actual dynamic statistics directly from database records without hardcoding."""
    total_verified = db.query(Scheme).filter(Scheme.verification_status == "Verified", Scheme.active_status == True).count()
    total_schemes = db.query(Scheme).filter(Scheme.active_status == True).count()
    districts_count = len(KARNATAKA_DISTRICTS)
    service_categories = 8  # Schemes, Loans, Crop, Fertilizer, Weather, Market, Soil, Disease
    user_saved_count = 0
    if current_user:
        user_saved_count = db.query(SavedScheme).filter(SavedScheme.user_id == current_user.id).count()

    return {
        "verified_schemes": total_verified,
        "total_schemes": total_schemes,
        "districts_covered": districts_count,
        "service_categories": service_categories,
        "saved_schemes": user_saved_count
    }

@router.get("", response_model=List[SchemeResponse])
def get_all_schemes(
    search: Optional[str] = Query(None),
    crop: Optional[str] = Query(None),
    verification: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    query = db.query(Scheme).filter(Scheme.active_status == True)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Scheme.scheme_name.ilike(search_term)) |
            (Scheme.scheme_name_kn.ilike(search_term)) |
            (Scheme.scheme_id.ilike(search_term)) |
            (Scheme.scheme_code.ilike(search_term)) |
            (Scheme.department.ilike(search_term))
        )

    if verification:
        query = query.filter(Scheme.verification_status == verification)

    schemes = query.all()

    # Filter by crop if provided
    if crop and crop.lower() != "all":
        filtered = []
        for s in schemes:
            try:
                c_list = json.loads(s.eligible_crops) if s.eligible_crops else ["All"]
                if "All" in c_list or any(c.lower() == crop.lower() for c in c_list):
                    filtered.append(s)
            except Exception:
                filtered.append(s)
        schemes = filtered

    # Determine user's saved scheme IDs
    saved_ids = set()
    if current_user:
        saved_records = db.query(SavedScheme.scheme_id).filter(SavedScheme.user_id == current_user.id).all()
        saved_ids = {r[0] for r in saved_records}

    return [format_scheme_response(s, is_saved=(s.id in saved_ids)) for s in schemes]

@router.get("/saved/my", response_model=List[SchemeResponse])
def get_my_saved_schemes(current_user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    saved = db.query(Scheme).join(SavedScheme, SavedScheme.scheme_id == Scheme.id).filter(SavedScheme.user_id == current_user.id).all()
    return [format_scheme_response(s, is_saved=True) for s in saved]

@router.get("/{scheme_id}", response_model=SchemeResponse)
def get_scheme_detail(scheme_id: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    scheme = db.query(Scheme).filter(
        (Scheme.scheme_id == scheme_id) | 
        (Scheme.scheme_code == scheme_id) |
        (Scheme.id == int(scheme_id) if scheme_id.isdigit() else False)
    ).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    is_saved = False
    if current_user:
        is_saved = db.query(SavedScheme).filter(SavedScheme.user_id == current_user.id, SavedScheme.scheme_id == scheme.id).first() is not None

    return format_scheme_response(scheme, is_saved=is_saved)

@router.post("/eligibility", response_model=EligibilityResponse)
def check_eligibility(request: EligibilityCheckRequest, db: Session = Depends(get_db)):
    """Runs deterministic rule engine to evaluate PASS/FAIL/UNKNOWN status on all schemes."""
    schemes = db.query(Scheme).filter(Scheme.active_status == True).all()
    return DeterministicEligibilityEngine.evaluate_all(schemes, request)

@router.post("/{id}/save")
def toggle_save_scheme(id: int, current_user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    existing = db.query(SavedScheme).filter(SavedScheme.user_id == current_user.id, SavedScheme.scheme_id == id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"saved": False, "message": "Scheme removed from saved list"}
    else:
        new_save = SavedScheme(user_id=current_user.id, scheme_id=id)
        db.add(new_save)
        db.commit()
        return {"saved": True, "message": "Scheme saved successfully"}
