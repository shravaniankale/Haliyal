from fastapi import APIRouter, Query
from typing import Optional
from ..services.season_service import AgriculturalSeasonService

router = APIRouter(prefix="/api/season", tags=["Agricultural Season Intelligence"])

@router.get("")
def get_agricultural_season(
    district: Optional[str] = Query(None, description="Farmer district for regional calendar context"),
    crop: Optional[str] = Query(None, description="Primary crop cultivated"),
    crop_stage: Optional[str] = Query(None, description="Current growth stage if known")
):
    """
    Returns real-time Asia/Kolkata agricultural date, season (Kharif, Rabi, Summer),
    crop stage, insurance parameters, and Karnataka extension advisory.
    """
    return AgriculturalSeasonService.analyze_season(
        district=district,
        crop=crop,
        crop_stage=crop_stage
    )

