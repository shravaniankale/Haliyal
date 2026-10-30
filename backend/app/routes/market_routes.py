from typing import Optional, List
from fastapi import APIRouter, Query
from ..seed_data import KARNATAKA_APMC_PRICES
from ..schemas import MarketPriceItem

router = APIRouter(prefix="/api/market-prices", tags=["Market Prices"])

@router.get("", response_model=List[MarketPriceItem])
def get_market_prices(
    crop: Optional[str] = Query(None),
    district: Optional[str] = Query(None)
):
    """
    Returns authentic Karnataka APMC mandi commodity prices.
    Includes modal price, min/max range, market name, and historical status.
    """
    results = KARNATAKA_APMC_PRICES

    if crop and crop.lower() != "all":
        results = [r for r in results if crop.lower() in r["crop"].lower() or crop in r["crop_kn"]]

    if district and district.lower() != "all":
        results = [r for r in results if district.lower() in r["district"].lower()]

    return results
