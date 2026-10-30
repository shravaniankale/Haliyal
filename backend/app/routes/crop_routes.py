from fastapi import APIRouter, HTTPException
from ..seed_data import KARNATAKA_CROPS

router = APIRouter(prefix="/api/crops", tags=["Crop Guidance"])

@router.get("")
def list_crops():
    """Returns verified agricultural guidance for all major Karnataka crops."""
    return KARNATAKA_CROPS

@router.get("/{crop_id}")
def get_crop_details(crop_id: str):
    crop_id_clean = crop_id.strip().lower()
    for c in KARNATAKA_CROPS:
        if c["crop_id"].lower() == crop_id_clean:
            return c
    raise HTTPException(status_code=404, detail="Crop not found in Karnataka database")
