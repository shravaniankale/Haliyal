from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/fertilizer", tags=["Fertilizer Guidance"])

class FertilizerRequest(BaseModel):
    crop: str
    soil_type: str  # "Red Loamy", "Black Cotton", "Sandy Loam", "Alluvial", "Laterite"
    growth_stage: str  # "Basal / Sowing", "Vegetative / Tillering", "Flowering / Panicle", "Maturity"

FERTILIZER_DATABASE = {
    "paddy": {
        "npk_ratio": "100:50:50 kg N:P2O5:K2O per hectare (approx 40:20:20 kg/acre)",
        "basal": "Apply 50% Nitrogen + 100% Phosphorus + 50% Potash at the time of final puddling/transplanting.",
        "top_dressing": "Apply 25% Nitrogen at tillering (20-25 days after transplanting) and remaining 25% Nitrogen + 50% Potash at panicle initiation.",
        "zinc_notice": "In case of Zinc deficiency (Khaira disease), apply 10 kg Zinc Sulphate per acre mixed with sand. Do not mix with DAP directly.",
        "organic_alternatives": [
            "Well decomposed Farm Yard Manure (FYM): 4 to 5 tonnes/acre 3 weeks before transplanting.",
            "Green manuring with Sunnhemp or Dhaincha (incorporate 45 days after sowing).",
            "Jeevamrutha application: 200 litres per acre through irrigation water every 15 days."
        ]
    },
    "ragi": {
        "npk_ratio": "50:40:25 kg N:P2O5:K2O per hectare (approx 20:16:10 kg/acre)",
        "basal": "Apply entire Phosphorus and Potash and 50% Nitrogen during land preparation / sowing.",
        "top_dressing": "Top-dress remaining 50% Nitrogen 3 to 4 weeks after sowing following weeding, with adequate soil moisture.",
        "zinc_notice": "Apply 5 kg Borax and 10 kg Zinc Sulphate per acre in deficient red soils of Karnataka.",
        "organic_alternatives": [
            "FYM or compost: 3 to 4 tonnes per acre applied during pre-monsoon ploughing.",
            "Vermicompost: 1 tonne per acre.",
            "Neem cake: 100 kg per acre to deter root grubs."
        ]
    },
    "jowar": {
        "npk_ratio": "60:30:30 kg N:P2O5:K2O per hectare (approx 24:12:12 kg/acre)",
        "basal": "Apply 50% Nitrogen and full dose of Phosphorus and Potassium in seed furrow at 5 cm depth.",
        "top_dressing": "Top dress remaining 50% Nitrogen 30 days after sowing after weeding.",
        "zinc_notice": "In black soils, Iron and Zinc chlorosis can occur; spray 0.5% FeSO4 or ZnSO4 if interveinal yellowing is observed.",
        "organic_alternatives": [
            "FYM: 2.5 tonnes per acre.",
            "Biofertilizers: Azospirillum and PSB seed treatment (200g per 10kg seeds)."
        ]
    },
    "maize": {
        "npk_ratio": "150:75:40 kg N:P2O5:K2O per hectare (approx 60:30:16 kg/acre)",
        "basal": "Apply 1/3rd Nitrogen, full Phosphorus and full Potash at sowing.",
        "top_dressing": "Apply 1/3rd Nitrogen at knee-high stage (30-35 days) and remaining 1/3rd Nitrogen at tasseling stage.",
        "zinc_notice": "Zinc deficiency causes 'white bud' in maize; apply 10 kg Zinc Sulphate per acre basal.",
        "organic_alternatives": [
            "FYM: 4 tonnes per acre.",
            "Enriched compost with Trichoderma."
        ]
    },
    "cotton": {
        "npk_ratio": "120:60:60 kg N:P2O5:K2O per hectare for irrigated Bt Cotton",
        "basal": "Apply 25% Nitrogen, full Phosphorus and 50% Potash as basal dose.",
        "top_dressing": "Apply Nitrogen and remaining Potash in 3 equal splits at squaring, flowering, and boll formation.",
        "zinc_notice": "Foliar spray of 1% Magnesium Sulphate + 0.5% Zinc Sulphate prevents leaf reddening.",
        "organic_alternatives": [
            "Castor or Neem cake: 200 kg/acre.",
            "Vermicompost: 1.5 tonnes/acre."
        ]
    },
    "groundnut": {
        "npk_ratio": "25:50:25 kg N:P2O5:K2O per hectare (approx 10:20:10 kg/acre)",
        "basal": "Apply full N, P, and K at the time of sowing.",
        "top_dressing": "Apply Gypsum @ 200 kg/acre at 40-45 days after sowing (flowering/pegging stage) to supply Calcium and Sulphur for pod filling.",
        "zinc_notice": "Gypsum application is critical for healthy pod shell formation and oil content.",
        "organic_alternatives": [
            "Rhizobium culture and PSB seed treatment.",
            "FYM: 3 tonnes per acre."
        ]
    },
    "tur": {
        "npk_ratio": "25:50:25 kg N:P2O5:K2O per hectare (approx 10:20:10 kg/acre)",
        "basal": "Apply full dose as basal application 5 cm below seed level.",
        "top_dressing": "Spray 2% Urea or 19:19:19 soluble fertilizer during flowering and pod development to enhance pod setting.",
        "zinc_notice": "Sulphur is critical for pulses; use SSP (Single Super Phosphate) as P source.",
        "organic_alternatives": [
            "Rhizobium leguminosarum seed inoculation.",
            "Vermicompost: 1 tonne/acre."
        ]
    },
    "sugarcane": {
        "npk_ratio": "250:100:125 kg N:P2O5:K2O per hectare",
        "basal": "Apply 10% N, full P, and 20% K at planting.",
        "top_dressing": "Remaining N and K in 3 splits at 45, 90, and final earthing up at 120-150 days.",
        "zinc_notice": "Ferrous sulphate spray if iron deficiency chlorosis is seen in calcareous soils.",
        "organic_alternatives": [
            "Pressmud cake / Filter cake from sugar mills: 5 tonnes/acre.",
            "Trash mulching between cane rows."
        ]
    }
}

@router.post("/recommend")
def get_fertilizer_guidance(data: FertilizerRequest):
    crop_key = data.crop.strip().lower()
    crop_info = FERTILIZER_DATABASE.get(crop_key, FERTILIZER_DATABASE["paddy"])

    return {
        "crop": data.crop,
        "soil_type": data.soil_type,
        "growth_stage": data.growth_stage,
        "recommended_npk": crop_info["npk_ratio"],
        "basal_guidance": crop_info["basal"],
        "top_dressing_guidance": crop_info["top_dressing"],
        "micronutrient_advisory": crop_info["zinc_notice"],
        "organic_alternatives": crop_info["organic_alternatives"],
        "safety_instructions": [
            "Always apply fertilizers when soil has adequate moisture; never broadcast urea on bone-dry soil.",
            "Incorporate phosphatic fertilizers deep in the root zone (5 cm below seed level) as Phosphorus is immobile in soil.",
            "Wear protective gloves and footwear during fertilizer application and wash hands thoroughly.",
            "Store chemical fertilizers in dry, ventilated storage away from livestock feed and children."
        ],
        "soil_test_advisory": "IMPORTANT: Standard recommendations are indicative. Exact customized dosage depends on your field's Soil Health Card (SHC). Please get your soil tested at your nearest Taluk Raitha Samparka Kendra or Krishi Vigyan Kendra (KVK)."
    }
