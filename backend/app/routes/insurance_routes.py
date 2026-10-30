from fastapi import APIRouter, Query
from typing import Optional
from ..services.insurance_service import CropInsuranceService

router = APIRouter(prefix="/api/insurance", tags=["Crop Insurance Intelligence"])

@router.get("/status")
def get_crop_insurance_status(
    district: str = Query("Belagavi"),
    taluk: Optional[str] = Query(None),
    crop: Optional[str] = Query("Paddy"),
    season: Optional[str] = Query(None),
    land_acres: Optional[float] = Query(1.0)
):
    """
    Evaluates PMFBY & Karnataka Samrakshane crop insurance parameters,
    notified crop status, premium rates, and the 72-hour claim reporting window.
    """
    return CropInsuranceService.evaluate_insurance(
        district=district,
        taluk=taluk,
        crop=crop,
        season=season,
        land_acres=land_acres
    )

