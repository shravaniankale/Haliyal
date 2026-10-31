# -*- coding: utf-8 -*-
import json
from sqlalchemy.orm import Session
from .models import Scheme, User, FarmerProfile

# Verified & Demonstration Schemes Dataset (Comprehensive 26-Scheme Repository)
INITIAL_SCHEMES = [
    # REAL VERIFIED SCHEME 1
    {
        "scheme_id": "PM-KISAN",
        "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "scheme_name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (ಪಿಎಂ-ಕಿಸಾನ್)",
        "scheme_type": "Central Sector Scheme",
        "scheme_category": "Income Support",
        "department": "Ministry of Agriculture & Farmers Welfare, GoI",
        "department_kn": "ಕೃಷಿ ಮತ್ತು ರೈತರ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯ, ಭಾರತ ಸರ್ಕಾರ",
        "description": "Income support scheme providing ₹6,000 per year to all landholding farmer families across the country in three equal four-monthly installments of ₹2,000 directly into bank accounts via DBT.",
        "description_kn": "ಭಾರತದ ಎಲ್ಲಾ ಕೃಷಿ ಭೂಮಿ ಹೊಂದಿರುವ ಅರ್ಹ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವಾರ್ಷಿಕ ₹6,000 ಆರ್ಥಿಕ ನೆರವನ್ನು ₹2,000 ರ ಮೂರು ಕಂತುಗಳಲ್ಲಿ ನೇರವಾಗಿ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಜಮೆ ಮಾಡುವ ಪ್ರಮುಖ ಕೇಂದ್ರ ಪುರಸ್ಕೃತ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "landholding": "Cultivable landholder family with land title (RTC/Pahani) in their name",
            "exclusions": "Institutional landholders, constitutional post holders, serving/retired government employees, income tax payers"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Ownership of cultivable landholding with legal title in Karnataka (RTC registered)",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka & All India",
        "benefit_details": "₹6,000 per year transferred in three equal installments of ₹2,000 each via Direct Benefit Transfer (DBT).",
        "benefit_details_kn": "ವರ್ಷಕ್ಕೆ ₹6,000 ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ತಲಾ ₹2,000 ರಂತೆ 3 ಕಂತುಗಳಲ್ಲಿ ನೇರ ನಗದು ವರ್ಗಾವಣೆ (DBT) ಮೂಲಕ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ನೀಡಲಾಗುತ್ತದೆ.",
        "required_documents": json.dumps(["Aadhaar Card linked with Bank Account", "Land Ownership Record (RTC/Pahani)", "Bank Passbook with IFSC", "Active Mobile Number"]),
        "application_steps": json.dumps([
            "1. Visit the official PM-KISAN portal (pmkisan.gov.in) or nearest Karnataka Grama One / Raitha Samparka Kendra.",
            "2. Enter Aadhaar number and verify with OTP.",
            "3. Select State: Karnataka, District, Taluk, Village, and enter Land Survey Number / RTC details.",
            "4. Upload land records and submit for Village Nodal Officer / Taluk Tahsildar e-verification."
        ]),
        "application_period": "Open Throughout Year (continuous DBT quarterly)",
        "official_url": "https://pmkisan.gov.in",
        "source_url": "https://pmkisan.gov.in/Documents/OperationalGuidelines.pdf",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=800&q=80"
    },

    # REAL VERIFIED SCHEME 2
    {
        "scheme_id": "PMFBY",
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "scheme_name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (ಪಿಎಂಎಫ್‌ಬಿವೈ)",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Crop Insurance",
        "department": "Department of Agriculture, GoK & Ministry of Agriculture, GoI",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಮತ್ತು ಕೇಂದ್ರ ಕೃಷಿ ಸಚಿವಾಲಯ",
        "description": "Comprehensive risk insurance covering yield losses due to non-preventable natural risks (drought, flood, pests, unseasonal rains) for notified crops in notified Karnataka areas.",
        "description_kn": "ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳು (ಬರ, ಪ್ರವಾಹ, ಕೀಟಬಾಧೆ, ಅಕಾಲಿಕ ಮಳೆ) ಉಂಟಾದಾಗ ಬೆಳೆ ನಷ್ಟ ಪರಿಹಾರ ಒದಗಿಸುವ ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ ಯೋಜನೆ. ರೈತರು ಅತ್ಯಂತ ಕಡಿಮೆ ಪ್ರೀಮಿಯಂ ಪಾವತಿಸಬೇಕಾಗುತ್ತದೆ.",
        "eligibility_conditions": json.dumps({
            "notified_crops": "Paddy, Ragi, Jowar, Maize, Groundnut, Cotton, Tur, Sugarcane",
            "premium_rate": "Kharif food crops & oilseeds: 2.0%, Rabi crops: 1.5%, Commercial/Horticulture crops: 5.0%"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers"]),
        "eligible_crops": json.dumps(["Paddy", "Ragi", "Jowar", "Maize", "Cotton", "Groundnut", "Tur", "Soybean", "Sugarcane"]),
        "land_requirements": "Cultivating insurable notified crop in notified gram panchayat / hobli (Own or Tenant)",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Notified Gram Panchayats",
        "benefit_details": "Comprehensive financial insurance compensation for localized calamities, prevented sowing, mid-season adversity, and post-harvest crop losses.",
        "benefit_details_kn": "ಬೆಳೆ ಬಿತ್ತನೆ ವಿಫಲತೆ, ಬರಗಾಲ, ಅಕಾಲಿಕ ಮಳೆ ಹಾಗೂ ಕಟಾವಿನ ನಂತರದ ನಷ್ಟಕ್ಕೆ ಪೂರ್ಣ ಬೆಳೆ ವಿಮೆ ಪರಿಹಾರ ಧನ ದೊರೆಯುತ್ತದೆ.",
        "required_documents": json.dumps(["Pahani (RTC) or Crop Sowing Certificate", "Aadhaar Card", "Bank Account Details", "Crop Declaration / Sowing Certificate"]),
        "application_steps": json.dumps([
            "1. Check notified crop for your hobli on Karnataka Samrakshane Portal (samrakshane.karnataka.gov.in).",
            "2. Pay minimal farmer premium (2% for Kharif, 1.5% for Rabi) before seasonal cut-off date.",
            "3. Obtain insurance proposal receipt with acknowledgment number.",
            "4. In case of localized calamity, report within 72 hours via Crop Insurance App or helpline 1800-180-1551."
        ]),
        "application_period": "Kharif: May 15 to July 31 / Rabi: Sept 15 to Dec 15",
        "official_url": "https://samrakshane.karnataka.gov.in",
        "source_url": "https://pmfby.gov.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80"
    },

    # REAL VERIFIED SCHEME 3
    {
        "scheme_id": "KRISHI-BHAGYA",
        "scheme_name": "Karnataka Krishi Bhagya Scheme",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Irrigation & Water",
        "department": "Department of Agriculture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "State initiative to secure sustainable farming in dryland and rainfed agro-climatic zones of Karnataka through in-situ rainwater harvesting (Krishi Honda / Farm Ponds), polythene lining, diesel/solar pump sets, and micro-irrigation systems.",
        "description_kn": "ಕರ್ನಾಟಕದ ಮಳೆ ಆಶ್ರಿತ ಒಣಭೂಮಿ ಪ್ರದೇಶಗಳಲ್ಲಿ ನೀರು ಸಂರಕ್ಷಣೆಗಾಗಿ ಕೃಷಿ ಹೊಂಡ ನಿರ್ಮಾಣ, ಪಾಲಿಥೀನ್ ಹೊದಿಕೆ, ಡೀಸೆಲ್/ಸೌರ ಪಂಪ್‌ಸೆಟ್ ಮತ್ತು ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿ ಅಳವಡಿಕೆಗೆ ಶೇ. 80 ರಿಂದ 90 ರವರೆಗೆ ಸಹಾಯಧನ ನೀಡುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "target_districts": "Rainfed dryland areas of Karnataka (North Karnataka and dry belts of South Karnataka)",
            "subsidy_rate": "80% subsidy for General category; 90% subsidy for SC/ST farmers"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "SC/ST", "General"]),
        "eligible_crops": json.dumps(["All", "Ragi", "Jowar", "Paddy", "Maize", "Cotton", "Groundnut", "Tur"]),
        "land_requirements": "Minimum 1 acre of dryland/rainfed agricultural land with clear title",
        "max_land_acres": 5.0,
        "min_land_acres": 1.0,
        "required_ownership": "Own",
        "location_restrictions": "Rainfed dryland areas of Karnataka (North Karnataka and dry belts of South Karnataka)",
        "benefit_details": "80% to 90% direct subsidy for construction of farm pond (Krishi Honda), tarpaulin lining, diesel/solar pump, and micro-irrigation kit.",
        "benefit_details_kn": "ಕೃಷಿ ಹೊಂಡ ನಿರ್ಮಾಣ ಮತ್ತು ಲೈನಿಂಗ್ ವೆಚ್ಚಕ್ಕೆ ಶೇ. 80-90 ರಷ್ಟು ಸರ್ಕಾರಿ ಸಹಾಯಧನ.",
        "required_documents": json.dumps(["Current RTC (Pahani)", "Aadhaar Card", "Caste Certificate (if SC/ST)", "Bank Passbook Copy", "Passport size photograph"]),
        "application_steps": json.dumps([
            "1. Apply through Seva Sindhu or K-Kisan online portal or visit Assistant Director of Agriculture (ADA) office.",
            "2. Submit RTC showing rainfed category and land measurement sketch.",
            "3. Field inspection by agricultural officer for GPS tagging.",
            "4. Post-construction verification and DBT release into beneficiary account."
        ]),
        "application_period": "Annual Budgetary Window (June to November)",
        "official_url": "https://raitamitra.karnataka.gov.in",
        "source_url": "https://raitamitra.karnataka.gov.in/info-2/Krishi+Bhagya/en",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&w=800&q=80"
    },

    # SYNTHETIC DEMONSTRATION RECORD 1
    {
        "scheme_id": "DEMO-IRRIG-01",
        "scheme_name": "[DEMO RECORD] Demo Micro-Irrigation Support",
        "scheme_name_kn": "[ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆ] ಡೆಮೊ ಹನಿ ನೀರಾವರಿ ಪ್ರೋತ್ಸಾಹ ಯೋಜನೆ",
        "scheme_type": "Synthetic Demonstration Record",
        "scheme_category": "Irrigation & Water",
        "department": "Fictional Demonstration Dept (Hackathon Sandbox)",
        "department_kn": "ಪ್ರಾಯೋಗಿಕ ಪರೀಕ್ಷಾ ವಿಭಾಗ (ಹ್ಯಾಕಥಾನ್ ಡೆಮೊ)",
        "description": "NOTICE: This is a synthetic test record provided for system testing and technical rule evaluation demonstration only. It does not represent an actual government benefit.",
        "description_kn": "ಸೂಚನೆ: ಇದು ಕೇವಲ ಸಿಸ್ಟಮ್ ಪರೀಕ್ಷೆ ಮತ್ತು ನಿಯಮ ಮೌಲ್ಯಮಾಪನಕ್ಕಾಗಿ ಬಳಸಲಾದ ಕಾಲ್ಪನಿಕ ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆಯಾಗಿದೆ. ಇದು ನಿಜವಾದ ಸರ್ಕಾರಿ ಯೋಜನೆಯಲ್ಲ.",
        "eligibility_conditions": json.dumps({
            "test_flag": "Synthetic test record",
            "purpose": "Demonstrates strict max land cut-off and irrigation filter"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Test condition: Exactly <= 2.5 acres",
        "max_land_acres": 2.5,
        "min_land_acres": 0.5,
        "required_ownership": "Own",
        "location_restrictions": "Karnataka (demo only)",
        "benefit_details": "Synthetic simulation benefit for sandbox testing only.",
        "benefit_details_kn": "ಕೇವಲ ಪರೀಕ್ಷಾರ್ಥ ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ಪ್ರಯೋಜನ.",
        "required_documents": json.dumps(["Demo Sample RTC", "Demo ID"]),
        "application_steps": json.dumps(["1. This is a synthetic sandbox test record; no application required."]),
        "application_period": "Synthetic sandbox test quota",
        "official_url": "https://krishimitra.karnataka.gov.in/demo-terms",
        "source_url": "https://krishimitra.karnataka.gov.in/demo-dataset",
        "verification_date": "2026-10-01",
        "verification_status": "Synthetic Demo",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?auto=format&fit=crop&w=800&q=80"
    },

    # SYNTHETIC DEMONSTRATION RECORD 2
    {
        "scheme_id": "DEMO-EQUIP-02",
        "scheme_name": "[DEMO RECORD] Demo Agricultural Equipment Assistance",
        "scheme_name_kn": "[ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆ] ಡೆಮೊ ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ನೆರವು",
        "scheme_type": "Synthetic Demonstration Record",
        "scheme_category": "Farm Mechanization",
        "department": "Fictional Demonstration Dept (Hackathon Sandbox)",
        "department_kn": "ಪ್ರಾಯೋಗಿಕ ಪರೀಕ್ಷಾ ವಿಭಾಗ (ಹ್ಯಾಕಥಾನ್ ಡೆಮೊ)",
        "description": "NOTICE: Fictional benchmark record generated for testing deterministic equipment qualification filters.",
        "description_kn": "ಸೂಚನೆ: ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳ ನಿಯಮ ಪರಿಶೀಲನೆಯನ್ನು ಪರೀಕ್ಷಿಸಲು ಮಾತ್ರ ರಚಿಸಲಾದ ಕಾಲ್ಪನಿಕ ದಾಖಲೆ.",
        "eligibility_conditions": json.dumps({
            "test_flag": "Synthetic test record",
            "purpose": "Validates equipment subsidy engine"
        }),
        "eligible_farmer_categories": json.dumps(["General", "Small and Marginal"]),
        "eligible_crops": json.dumps(["Paddy", "Sugarcane"]),
        "land_requirements": "Test condition: Minimum 2 acres",
        "max_land_acres": 10.0,
        "min_land_acres": 2.0,
        "required_ownership": "Own",
        "location_restrictions": "Karnataka (demo only)",
        "benefit_details": "Simulated 50% power-tiller test subsidy for validation.",
        "benefit_details_kn": "ಪರೀಕ್ಷಾರ್ಥ ಡೆಮೊ ಸಹಾಯಧನ ವಿವರ.",
        "required_documents": json.dumps(["Demo Machinery Quotation", "Demo RTC"]),
        "application_steps": json.dumps(["1. Fictional record for automated test suite execution."]),
        "application_period": "Synthetic sandbox test quota",
        "official_url": "https://krishimitra.karnataka.gov.in/demo-terms",
        "source_url": "https://krishimitra.karnataka.gov.in/demo-dataset",
        "verification_date": "2026-10-01",
        "verification_status": "Synthetic Demo",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1595838728639-4458f27fb636?auto=format&fit=crop&w=800&q=80"
    },

    # SYNTHETIC DEMONSTRATION RECORD 3
    {
        "scheme_id": "DEMO-SOIL-03",
        "scheme_name": "[DEMO RECORD] Demo Soil Improvement Support",
        "scheme_name_kn": "[ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆ] ಡೆಮೊ ಮಣ್ಣು ಸುಧಾರಣೆ ಸಹಾಯ ಯೋಜನೆ",
        "scheme_type": "Synthetic Demonstration Record",
        "scheme_category": "Soil Health & Fertilizers",
        "department": "Fictional Demonstration Dept (Hackathon Sandbox)",
        "department_kn": "ಪ್ರಾಯೋಗಿಕ ಪರೀಕ್ಷಾ ವಿಭಾಗ (ಹ್ಯಾಕಥಾನ್ ಡೆಮೊ)",
        "description": "NOTICE: Fictional benchmark record created strictly for testing soil amendment recommendations.",
        "description_kn": "ಸೂಚನೆ: ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳ ಶಿಫಾರಸು ಪರೀಕ್ಷೆಗಾಗಿ ಮಾತ್ರ ಇರುವ ಕಾಲ್ಪನಿಕ ದಾಖಲೆ.",
        "eligibility_conditions": json.dumps({
            "test_flag": "Synthetic test record",
            "purpose": "Verifies soil testing rule conditions"
        }),
        "eligible_farmer_categories": json.dumps(["All"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Cultivable land with recent soil test",
        "max_land_acres": 20.0,
        "min_land_acres": 0.5,
        "required_ownership": "Any",
        "location_restrictions": "Karnataka (demo only)",
        "benefit_details": "Synthetic micronutrient kit demonstration.",
        "benefit_details_kn": "ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ಮಣ್ಣು ಸುಧಾರಕ ಕಿಟ್.",
        "required_documents": json.dumps(["Demo Soil Health Card"]),
        "application_steps": json.dumps(["1. Test case scenario only."]),
        "application_period": "Synthetic sandbox test quota",
        "official_url": "https://krishimitra.karnataka.gov.in/demo-terms",
        "source_url": "https://krishimitra.karnataka.gov.in/demo-dataset",
        "verification_date": "2026-10-01",
        "verification_status": "Synthetic Demo",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 7: KCC-MISS
    {
        "scheme_id": "KCC-MISS",
        "scheme_name": "Modified Interest Subvention Scheme via Kisan Credit Card (KCC)",
        "scheme_name_kn": "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (ಕೆಸಿಸಿ) ಬಡ್ಡಿ ರಿಯಾಯಿತಿ ಯೋಜನೆ",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Credit & Loans",
        "department": "Ministry of Agriculture & Farmers Welfare, GoI / NABARD",
        "department_kn": "ಕೇಂದ್ರ ಕೃಷಿ ಸಚಿವಾಲಯ ಹಾಗೂ ನಬಾರ್ಡ್ (NABARD)",
        "description": "Provides short-term production credit up to ₹3,00,000 for crop cultivation and post-harvest expenses at 7% p.a., reduced to effectively 4% p.a. on prompt repayment through 3% interest subvention.",
        "description_kn": "ಬೀಜ, ಗೊಬ್ಬರ, ಕೀಟನಾಶಕ ಮತ್ತು ಕಟಾವಿನ ವೆಚ್ಚಕ್ಕಾಗಿ ₹3 ಲಕ್ಷದವರೆಗೆ ಶೇ. 7% ಬಡ್ಡಿದರದಲ್ಲಿ ಅಲ್ಪಾವಧಿ ಬೆಳೆ ಸಾಲ ಒದಗಿಸುವ ಯೋಜನೆ. ಸಕಾಲದಲ್ಲಿ ಸಾಲ ಮರುಪಾವತಿಸಿದರೆ ಶೇ. 3% ಬಡ್ಡಿ ರಿಯಾಯಿತಿ ದೊರೆತು ಪರಿಣಾಮಕಾರಿಯಾಗಿ ಕೇವಲ 4% ಬಡ್ಡಿ ಅನ್ವಯಿಸುತ್ತದೆ.",
        "eligibility_conditions": json.dumps({
            "farmer_types": "All cultivators: owner cultivators, tenant farmers, oral lessees, sharecroppers, and SHGs/JLGs",
            "collateral_free": "Collateral-free limit up to ₹1,60,000 (extended to ₹3,00,000 for tie-up arrangements)"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Agricultural cultivation on valid landholding (Own title RTC or registered lease / JLG agreement)",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "Short-term crop credit up to ₹3,00,000 at 4% effective interest rate with 3% prompt repayment incentive. No collateral required up to ₹1.6 Lakh.",
        "benefit_details_kn": "₹3 ಲಕ್ಷದವರೆಗೆ ಕೇವಲ 4% ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರದಲ್ಲಿ ಬೆಳೆ ಸಾಲ. ₹1.6 ಲಕ್ಷದವರೆಗೆ ಯಾವುದೇ ಆಸ್ತಿ ಅಡಮಾನವಿಲ್ಲದೆ ಸಾಲ ಸೌಲಭ್ಯ.",
        "required_documents": json.dumps(["Filled KCC application form", "RTC / Pahani or Cultivation / Lease agreement", "Aadhaar Card", "Bank Passbook with photo"]),
        "application_steps": json.dumps([
            "1. Approach nearest Commercial Bank, Grameena Bank, or Primary Agricultural Cooperative Society (PACS).",
            "2. Submit KCC application with RTC/Pahani or tenant cultivation proof.",
            "3. Bank processes and issues RuPay Kisan Credit Card within 14 working days."
        ]),
        "application_period": "Open Throughout Year",
        "official_url": "https://pmkisan.gov.in",
        "source_url": "https://www.nabard.org/content1.aspx?id=594&catid=23&mid=530",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 8: SHC-SCHEME
    {
        "scheme_id": "SHC-SCHEME",
        "scheme_name": "Soil Health Card Scheme & Nutrient Management",
        "scheme_name_kn": "ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ (ಸಾಯಿಲ್ ಹೆಲ್ತ್ ಕಾರ್ಡ್) ಯೋಜನೆ",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Soil Health & Fertilizers",
        "department": "Department of Agriculture, GoK & MoA&FW, GoI",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಮತ್ತು ಕೇಂದ್ರ ಕೃಷಿ ಸಚಿವಾಲಯ",
        "description": "Provides customized soil health cards assessing 12 critical chemical and physical parameters (macro-nutrients N, P, K; secondary nutrient S; micro-nutrients Zn, Fe, Cu, Mn, Bo; and pH, EC, OC) with dosage recommendations for balanced fertilizer use.",
        "description_kn": "ಜಮೀನಿನ ಮಣ್ಣಿನ 12 ಪೋಷಕಾಂಶಗಳ ಮಟ್ಟವನ್ನು (ಸಾರಜನಕ, ರಂಜಕ, ಪೊಟ್ಯಾಷ್, ಲಘು ಪೋಷಕಾಂಶಗಳು ಮತ್ತು ಪಿಹೆಚ್ ಮೌಲ್ಯ) ಉಚಿತವಾಗಿ ಪರೀಕ್ಷಿಸಿ, ಬೆಳೆವಾರು ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರ ಬಳಕೆಗೆ ಶಿಫಾರಸು ಪತ್ರ ನೀಡುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "testing_cycle": "Soil tested once every 3 years for all agricultural plots in Karnataka",
            "cost": "100% Free laboratory analysis and advisory"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "General", "SC/ST", "Women", "Tenant Farmers"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Any agricultural plot in Karnataka",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "Free scientific soil testing, printed Soil Health Card with 12 parameters, and 20-30% reduction in chemical fertilizer cost through balanced dosage advice.",
        "benefit_details_kn": "ಉಚಿತ ಮಣ್ಣು ಪರೀಕ್ಷೆ, ಸಮಗ್ರ ಪೋಷಕಾಂಶಗಳ ವರದಿ ಹಾಗೂ ರಸಗೊಬ್ಬರದ ವೆಚ್ಚದಲ್ಲಿ ೨೦-೩೦% ಉಳಿತಾಯಕ್ಕೆ ವೈಜ್ಞಾನಿಕ ಮಾರ್ಗದರ್ಶನ.",
        "required_documents": json.dumps(["Soil Sample with Plot Survey Number", "Aadhaar Card", "RTC / Pahani copy"]),
        "application_steps": json.dumps([
            "1. Collect 'V' shaped composite soil sample before sowing from your plot.",
            "2. Submit soil sample to Raitha Samparka Kendra (RSK) or District Soil Testing Lab.",
            "3. Download printed Soil Health Card online at soilhealth.dac.gov.in."
        ]),
        "application_period": "Pre-sowing (April-May for Kharif, Sept-Oct for Rabi)",
        "official_url": "https://soilhealth.dac.gov.in",
        "source_url": "https://soilhealth.dac.gov.in/home",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 9: PMKSY-PDMC
    {
        "scheme_id": "PMKSY-PDMC",
        "scheme_name": "PM Krishi Sinchayee Yojana - Per Drop More Crop (Micro-Irrigation)",
        "scheme_name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕೃಷಿ ಸಿಂಚಾಯಿ ಯೋಜನೆ - ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿ (ಪಿಡಿಕೆಎಂಸಿ)",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Irrigation & Water",
        "department": "Department of Agriculture & Horticulture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಮತ್ತು ತೋಟಗಾರಿಕೆ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Promotes water-use efficiency through financial assistance for Drip and Sprinkler irrigation systems: 55% subsidy for Small & Marginal Farmers, 45% for other farmers, enhanced up to 90% in Karnataka for SC/ST cultivators.",
        "description_kn": "ಜಮೀನಿನಲ್ಲಿ ನೀರಿನ ಸದ್ಬಳಕೆ ಮತ್ತು ಇಳುವರಿ ಹೆಚ್ಚಿಸಲು ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿ ಘಟಕಗಳ ಅಳವಡಿಕೆಗೆ ಸಣ್ಣ ಮತ್ತು ಅತಿ ಸಣ್ಣ ರೈತರಿಗೆ 55% ಮತ್ತು ಇತರ ರೈತರಿಗೆ 45% ಸಹಾಯಧನ. ಕರ್ನಾಟಕದಲ್ಲಿ ಎಸ್‌ಸಿ/ಎಸ್‌ಟಿ ರೈತರಿಗೆ ಶೇ. 90 ರವರೆಗೆ ಗರಿಷ್ಠ ಸಬ್ಸಿಡಿ.",
        "eligibility_conditions": json.dumps({
            "water_source": "Assured water source (borewell, open well, farm pond, or canal) required",
            "subsidy_scale": "55% for Small/Marginal (< 5 acres), 45% for General (> 5 acres), up to 90% for SC/ST under Karnataka top-up"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All", "Sugarcane", "Cotton", "Maize", "Arecanut", "Banana", "Vegetables", "Paddy"]),
        "land_requirements": "Ownership of agricultural land with assured water source",
        "max_land_acres": 12.5,
        "min_land_acres": 0.5,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "Direct capital subsidy for Drip & Sprinkler equipment (up to 55%-90% of unit cost) saving 40-50% water and improving crop yield.",
        "benefit_details_kn": "ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿ ಪದ್ಧತಿಗಳಿಗೆ ಶೇ. 55 ರಿಂದ 90 ರಷ್ಟು ನೇರ ಸಬ್ಸಿಡಿ. ಶೇ. 40-50 ನೀರು ಉಳಿತಾಯ.",
        "required_documents": json.dumps(["Current RTC / Pahani", "Aadhaar Card", "Bank Passbook", "Water & Electricity Availability Certificate", "Caste Certificate (if SC/ST)"]),
        "application_steps": json.dumps([
            "1. Register on Karnataka Seva Sindhu or K-Kisan portal.",
            "2. Select empanelled micro-irrigation manufacturer and submit farm sketch.",
            "3. Pre-installation inspection by Assistant Director of Agriculture/Horticulture.",
            "4. Field installation and GPS verification, followed by direct subsidy release."
        ]),
        "application_period": "Open Throughout Year",
        "official_url": "https://pmksy.gov.in",
        "source_url": "https://horticulturedir.karnataka.gov.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 10: PM-KUSUM-B
    {
        "scheme_id": "PM-KUSUM-B",
        "scheme_name": "PM-KUSUM Component-B: Standalone Solar Agriculture Pumps",
        "scheme_name_kn": "ಪಿಎಂ-ಕುಸುಮ್ ಯೋಜನೆ - ಸೋಲಾರ್ ಕೃಷಿ ಪಂಪ್‌ಸೆಟ್ ಸಹಾಯಧನ",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Irrigation & Water",
        "department": "Ministry of New & Renewable Energy, GoI / KREDL Karnataka",
        "department_kn": "ನವೀಕರಿಸಬಹುದಾದ ಇಂಧನ ಸಚಿವಾಲಯ ಹಾಗೂ ಕೆ.ಆರ್.ಇ.ಡಿ.ಎಲ್ ಕರ್ನಾಟಕ",
        "description": "Subsidizes installation of standalone off-grid solar-powered agriculture pumps (3 HP to 7.5 HP). 60% total subsidy (30% Central + 30% Karnataka KREDL subsidy), with farmer contributing only 40% (or bank loan).",
        "description_kn": "ವಿದ್ಯುತ್ ಸಂಪರ್ಕವಿಲ್ಲದ ಜಮೀನುಗಳಿಗೆ 3 ಹೆಚ್‌ಪಿ ಯಿಂದ 7.5 ಹೆಚ್‌ಪಿ ಸಾಮರ್ಥ್ಯದ ಸೌರಶಕ್ತಿ ಕೃಷಿ ಪಂಪ್‌ಸೆಟ್‌ಗಳನ್ನು ಅಳವಡಿಸಲು ಒಟ್ಟು 60% ಸಹಾಯಧನ (30% ಕೇಂದ್ರ + 30% ಕರ್ನಾಟಕ ಸರ್ಕಾರ). ರೈತರು ಕೇವಲ 40% ಪಾಲು ಭರಿಸಬೇಕು.",
        "eligibility_conditions": json.dumps({
            "grid_condition": "Priority for non-electrified farmlands or diesel pump replacement",
            "borewell": "Borewell or open well with adequate yield required"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Ownership of agricultural land with borewell/open well without regular electric connection",
        "max_land_acres": None,
        "min_land_acres": 1.0,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "60% direct subsidy for 3 HP, 5 HP, or 7.5 HP standalone solar pump sets. Guaranteed uninterrupted daytime irrigation without electricity bills.",
        "benefit_details_kn": "ಸೌರ ಪಂಪ್‌ಸೆಟ್ ಖರೀದಿಗೆ ಶೇ. 60 ರಷ್ಟು ಭಾರಿ ಸಬ್ಸಿಡಿ. ಹಗಲು ವೇಳೆಯಲ್ಲಿ ವಿದ್ಯುತ್ ಬಿಲ್ ಇಲ್ಲದೆ ನಿರಂತರ ನೀರಾವರಿ ಸೌಲಭ್ಯ.",
        "required_documents": json.dumps(["RTC (Pahani)", "Aadhaar Card", "Bank Account Details", "Borewell / Water Source Certificate", "Electricity Board (ESCOM) No-connection certificate"]),
        "application_steps": json.dumps([
            "1. Apply online via KREDL solar pump portal (kredlinfo.in).",
            "2. Submit land RTC, water source proof, and ESCOM non-electrification certificate.",
            "3. Pay 40% beneficiary share online upon document verification.",
            "4. Empanelled solar vendor installs pump within 90 days with 5-year comprehensive maintenance."
        ]),
        "application_period": "Annual Quota Allocation Window (July to December)",
        "official_url": "https://pmkusum.mnre.gov.in",
        "source_url": "https://kredlinfo.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 11: SMAM-MECH
    {
        "scheme_id": "SMAM-MECH",
        "scheme_name": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "scheme_name_kn": "ಕೃಷಿ ಯಾಂತ್ರೀಕರಣ ಉಪ-ಯೋಜನೆ (ಎಸ್‌ಎಂಎಎಂ)",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Farm Mechanization",
        "department": "Department of Agriculture, GoK & MoA&FW, GoI",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಮತ್ತು ಕೇಂದ್ರ ಕೃಷಿ ಸಚಿವಾಲಯ",
        "description": "Subsidizes farm machinery and implements (tractors, power tillers, rotavators, multi-crop seed drills, weeders, harvesters) with 40%-50% financial assistance, and promotes Custom Hiring Centres (CHC) with up to 40% capital grant.",
        "description_kn": "ಕೃಷಿ ಕೆಲಸಗಳ ಯಾಂತ್ರೀಕರಣಕ್ಕಾಗಿ ಟ್ರ್ಯಾಕ್ಟರ್, ಪವರ್ ಟಿಲ್ಲರ್, ರೋಟಾವೇಟರ್, ಕಳೆ ಕೀಳುವ ಯಂತ್ರ ಮುಂತಾದ ಉಪಕರಣಗಳ ಖರೀದಿಗೆ ಶೇ. 40 ರಿಂದ 50 ರಷ್ಟು ಸಹಾಯಧನ ಹಾಗೂ ಬಾಡಿಗೆ ಆಧಾರಿತ ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ಕೇಂದ್ರಗಳಿಗೆ (CHC) ಅನುದಾನ.",
        "eligibility_conditions": json.dumps({
            "subsidy_rate": "50% for SC/ST/Small & Marginal/Women farmers; 40% for other general farmers",
            "frequency": "One major implement per farmer every 5 years"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All", "Paddy", "Sugarcane", "Cotton", "Maize", "Ragi"]),
        "land_requirements": "Minimum 1 acre of agricultural land (RTC required for equipment allocation)",
        "max_land_acres": None,
        "min_land_acres": 1.0,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "40% to 50% capital subsidy on authorized agricultural machinery (up to ₹1,25,000 for power tillers and ₹2,00,000 for tractors).",
        "benefit_details_kn": "ಅಧಿಕೃತ ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳಿಗೆ ಶೇ. 40 ರಿಂದ 50 ರಷ್ಟು (ಪವರ್ ಟಿಲ್ಲರ್‌ಗೆ ₹1.25 ಲಕ್ಷದವರೆಗೆ) ನೇರ ಸಹಾಯಧನ.",
        "required_documents": json.dumps(["RTC (Pahani)", "Aadhaar Card", "Bank Passbook", "Caste Certificate (for SC/ST)", "Dealer Quotation for Machinery"]),
        "application_steps": json.dumps([
            "1. Register on Direct Benefit Transfer in Agriculture Mechanization portal (agrimachinery.nic.in).",
            "2. Select equipment, make/model, and authorized dealer in Karnataka.",
            "3. Departmental approval and verification by Taluk Assistant Director of Agriculture.",
            "4. Physical inspection and subsidy crediting via Aadhaar-linked DBT."
        ]),
        "application_period": "Kharif Season Portal Opening (May to October)",
        "official_url": "https://agrimachinery.nic.in",
        "source_url": "https://raitamitra.karnataka.gov.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1595838728639-4458f27fb636?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 12: AIF-INFRA
    {
        "scheme_id": "AIF-INFRA",
        "scheme_name": "Agriculture Infrastructure Fund (AIF)",
        "scheme_name_kn": "ಕೃಷಿ ಮೂಲಸೌಕರ್ಯ ನಿಧಿ (ಎಐಎಫ್) ಯೋಜನೆ",
        "scheme_type": "Central Sector Scheme",
        "scheme_category": "Post-Harvest & Marketing",
        "department": "Ministry of Agriculture & Farmers Welfare, GoI",
        "department_kn": "ಕೃಷಿ ಮತ್ತು ರೈತರ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯ, ಭಾರತ ಸರ್ಕಾರ",
        "description": "Medium-to-long term debt financing for post-harvest management infrastructure and community farming assets (warehouses, cold storage, silos, sorting/grading units, drying yards) with 3% per annum interest subvention up to ₹2 Crore for up to 7 years.",
        "description_kn": "ಕಟಾವಿನ ನಂತರದ ಬೆಳೆ ಸಂರಕ್ಷಣೆಗಾಗಿ ಗೋದಾಮು, ಕೋಲ್ಡ್ ಸ್ಟೋರೇಜ್, ಗ್ರೇಡಿಂಗ್ ಘಟಕ ಮತ್ತು ಕಣಗಳನ್ನು ನಿರ್ಮಿಸಲು ₹2 ಕೋಟಿ ವರೆಗಿನ ಸಾಲಕ್ಕೆ ವಾರ್ಷಿಕ 3% ಬಡ್ಡಿ ರಿಯಾಯಿತಿ ಮತ್ತು ಸಿಜಿಟಿಎಂಎಸ್‌ಇ ಸಾಲ ಖಾತರಿ ನೀಡುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "eligible_entities": "Primary Agricultural Credit Societies, FPOs, individual farmers, Agri-entrepreneurs, SHGs",
            "subvention": "3% per annum interest subvention on loans up to ₹2 Crore for a maximum period of 7 years"
        }),
        "eligible_farmer_categories": json.dumps(["All", "General", "Small and Marginal", "Tenant Farmers"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Land suitable for post-harvest agro-processing / storage infrastructure (owned or long-term lease)",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "3% per annum interest subvention on bank term loans up to ₹2 Crore for 7 years plus CGTMSE credit guarantee fee coverage.",
        "benefit_details_kn": "₹2 ಕೋಟಿಯವರೆಗಿನ ಸಾಲಕ್ಕೆ ವಾರ್ಷಿಕ 3% ಬಡ್ಡಿ ಸಬ್ಸಿಡಿ ಮತ್ತು ಕ್ರೆಡಿಟ್ ಗ್ಯಾರಂಟಿ ಕವರೇಜ್.",
        "required_documents": json.dumps(["Detailed Project Report (DPR)", "Land records / Lease deed", "KYC & PAN documents", "Bank in-principle sanction letter"]),
        "application_steps": json.dumps([
            "1. Register on AIF portal (agriinfra.dac.gov.in).",
            "2. Upload DPR, project cost estimate, and land title/lease document.",
            "3. Ministry evaluates and sanctions within 60 days, followed by participating bank loan disbursement."
        ]),
        "application_period": "Open Throughout Year (Until 2032-33)",
        "official_url": "https://agriinfra.dac.gov.in",
        "source_url": "https://agriinfra.dac.gov.in/Home/AboutUs",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 13: MIDH-HORTI
    {
        "scheme_id": "MIDH-HORTI",
        "scheme_name": "Mission for Integrated Development of Horticulture (MIDH)",
        "scheme_name_kn": "ಸಮಗ್ರ ತೋಟಗಾರಿಕೆ ಅಭಿವೃದ್ಧಿ ಮಿಷನ್ (ಎಂಐಡಿಹೆಚ್)",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Horticulture Development",
        "department": "Department of Horticulture, Government of Karnataka",
        "department_kn": "ತೋಟಗಾರಿಕೆ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Comprehensive horticulture development covering new orchard establishment (mango, arecanut, banana, pepper, citrus, pomegranate), rejuvenation of senile plantations, protected cultivation, and post-harvest pack houses with 40%-50% capital subsidy.",
        "description_kn": "ಹೊಸ ತೋಟಗಾರಿಕೆ ಬೆಳೆಗಳಾದ ಅಡಿಕೆ, ಮಾವು, ಬಾಳೆ, ಕಾಳುಮೆಣಸು, ದಾಳಿಂಬೆ ನಾಟಿ ಮಾಡಲು ಹಾಗೂ ತೋಟ ನವೀಕರಣ, ನೆರಳು ಪರದೆ ಮತ್ತು ಪ್ಯಾಕ್ ಹೌಸ್ ನಿರ್ಮಾಣಕ್ಕೆ ಶೇ. 40 ರಿಂದ 50 ರಷ್ಟು ಸಹಾಯಧನ ನೀಡುವ ಪ್ರಮುಖ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "crops": "Fruits, vegetables, spices (pepper), plantation crops (arecanut, cashew)",
            "subsidy_rate": "40% to 50% of cost norm specified by National Horticulture Mission"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["Arecanut", "Banana", "Pepper", "Mango", "Vegetables", "Flowers", "Spices", "Pomegranate"]),
        "land_requirements": "Minimum 0.5 acre for new plantation or protected cultivation",
        "max_land_acres": 10.0,
        "min_land_acres": 0.5,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts (special focus on Coastal, Malnad and Southern Dry Belts)",
        "benefit_details": "40% to 50% capital subsidy for high-yielding planting material, drip linkage, shade net houses, and pack-house infrastructure.",
        "benefit_details_kn": "ಹೊಸ ತೋಟ ನಿರ್ಮಾಣ ಹಾಗೂ ನೆರಳು ಪರದೆ ಘಟಕಗಳಿಗೆ ಶೇ. 40 ರಿಂದ 50 ರಷ್ಟು ಸಹಾಯಧನ.",
        "required_documents": json.dumps(["RTC (Pahani) with horticulture crop entry", "Aadhaar Card", "Bank Passbook", "Soil and Water testing report"]),
        "application_steps": json.dumps([
            "1. Apply at Senior Assistant Director of Horticulture (SADH) Taluk office or online via Seva Sindhu.",
            "2. Submit farm location sketch and proposed plantation project details.",
            "3. Field inspection by Horticulture Officer and planting material issuance.",
            "4. Subsidy released directly to bank account upon plantation survival verification."
        ]),
        "application_period": "Pre-Monsoon & Kharif (May to September)",
        "official_url": "https://midh.gov.in",
        "source_url": "https://horticulturedir.karnataka.gov.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 14: NMNF-BPKP
    {
        "scheme_id": "NMNF-BPKP",
        "scheme_name": "National Mission on Natural Farming (NMNF / BPKP)",
        "scheme_name_kn": "ರಾಷ್ಟ್ರೀಯ ನೈಸರ್ಗಿಕ ಕೃಷಿ ಮಿಷನ್ (ಭಾರತೀಯ ಪ್ರಾಕೃತಿಕ ಕೃಷಿ ಪದ್ಧತಿ)",
        "scheme_type": "Central Sector Scheme",
        "scheme_category": "Organic & Natural Farming",
        "department": "Ministry of Agriculture & Farmers Welfare, GoI & GoK",
        "department_kn": "ಕೃಷಿ ಸಚಿವಾಲಯ, ಭಾರತ ಸರ್ಕಾರ ಹಾಗೂ ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ",
        "description": "Financial assistance of ₹15,000 per hectare for 3 years to adopt natural chemical-free farming, setup on-farm bio-input preparation units (Jeevamrutha, Beejamrutha, Ghanajeevamrutha), farmer cluster training, and free PGS-India green certification.",
        "description_kn": "ರಾಸಾಯನಿಕ ಮುಕ್ತ ನೈಸರ್ಗಿಕ ಕೃಷಿ ಅಳವಡಿಕೆಗೆ ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ 3 ವರ್ಷಗಳವರೆಗೆ ₹15,000 ಪ್ರೋತ್ಸಾಹಧನ. ಜೀವಾಮೃತ, ಬೀಜಾಮೃತ ಘಟಕಗಳ ಸ್ಥಾಪನೆ, ಕ್ಲಸ್ಟರ್ ತರಬೇತಿ ಹಾಗೂ ಉಚಿತ ಪಿಜಿಎಸ್-ಇಂಡಿಯಾ ನೈಸರ್ಗಿಕ ಕೃಷಿ ಪ್ರಮಾಣಪತ್ರ ನೀಡುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "farming_method": "Complete avoidance of synthetic fertilizers, chemical insecticides and weedicides",
            "indigenous_cows": "Encouragement for desi cow maintenance for bio-inputs"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All", "Paddy", "Ragi", "Jowar", "Pulses", "Millets", "Vegetables", "Arecanut", "Banana"]),
        "land_requirements": "Agricultural cultivable land (minimum 0.5 acre)",
        "max_land_acres": None,
        "min_land_acres": 0.5,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts (Cluster-based selection across Gram Panchayats)",
        "benefit_details": "₹15,000/ha incentive over 3 years, free organic certification, and support for on-farm Jeevamrutha preparation units.",
        "benefit_details_kn": "ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ₹15,000 ಪ್ರೋತ್ಸಾಹಧನ, ಉಚಿತ ನೈಸರ್ಗಿಕ ಕೃಷಿ ಪ್ರಮಾಣೀಕರಣ ಹಾಗೂ ಜೀವಾಮೃತ ಘಟಕ ಸ್ಥಾಪನೆಗೆ ನೆರವು.",
        "required_documents": json.dumps(["RTC (Pahani)", "Aadhaar Card", "Bank Passbook", "Natural Farming Cluster Farmer Declaration"]),
        "application_steps": json.dumps([
            "1. Join designated Natural Farming Cluster via Raitha Samparka Kendra (RSK).",
            "2. Complete on-field master trainer demonstration on Beejamrutha and Jeevamrutha.",
            "3. Register on PGS-India portal for organic traceability.",
            "4. Incentive credited via DBT in annual phases upon cluster peer review."
        ]),
        "application_period": "Kharif and Rabi Pre-sowing (May-June / Sept-Oct)",
        "official_url": "https://naturalfarming.dac.gov.in",
        "source_url": "https://naturalfarming.dac.gov.in/guidelines",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1500651230702-0e2d8a49d4ad?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 15: ENAM-TRADE
    {
        "scheme_id": "ENAM-TRADE",
        "scheme_name": "National Agriculture Market (e-NAM) Electronic Trading Platform",
        "scheme_name_kn": "ರಾಷ್ಟ್ರೀಯ ಕೃಷಿ ಮಾರುಕಟ್ಟೆ (ಇ-ನಾಮ್) ವಿದ್ಯುನ್ಮಾನ ವ್ಯಾಪಾರ ವೇದಿಕೆ",
        "scheme_type": "Central Sector Scheme",
        "scheme_category": "Post-Harvest & Marketing",
        "department": "Small Farmers Agribusiness Consortium (SFAC) & Karnataka APMC",
        "department_kn": "ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಇಲಾಖೆ ಹಾಗೂ ಎಸ್‌ಎಫ್‌ಎಸಿ (SFAC)",
        "description": "Pan-India electronic trading portal integrating 1,361 mandis across 23 states. Provides online transparent bidding, quality assaying laboratories, electronic weighing, online payments directly into farmers' bank accounts without commission deduction.",
        "description_kn": "ಕರ್ನಾಟಕ ಹಾಗೂ ದೇಶದ ೧,೩೬೧ ಎಪಿಎಂಸಿ ಮಂಡಿಗಳನ್ನು ಸಂಪರ್ಕಿಸುವ ಆನ್‌ಲೈನ್ ಹರಾಜು ವೇದಿಕೆ. ಗುಣಮಟ್ಟ ಪರೀಕ್ಷೆ, ನಿಖರ ವಿದ್ಯುನ್ಮಾನ ತೂಕ ಹಾಗೂ ನೇರವಾಗಿ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ದಲ್ಲಾಳಿ ಕಮಿಷನ್ ರಹಿತ ಪಾವತಿ ಒದಗಿಸುವ ವ್ಯವಸ್ಥೆ.",
        "eligibility_conditions": json.dumps({
            "produce": "Agricultural and horticultural commodities brought to connected Karnataka APMC mandis",
            "cost": "Zero registration fee for farmers"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All", "Paddy", "Ragi", "Jowar", "Maize", "Cotton", "Groundnut", "Tur", "Arecanut"]),
        "land_requirements": "Any farmer marketing agricultural produce in Karnataka",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts (Connected APMC Markets)",
        "benefit_details": "Real-time transparent online auctioning, higher commodity realization by 10-15%, zero middleman exploitation, and same-day electronic payments.",
        "benefit_details_kn": "ಪಾರದರ್ಶಕ ಆನ್‌ಲೈನ್ ಹರಾಜು, ಶೇ. 10-15 ರಷ್ಟು ಉತ್ತಮ ಬೆಲೆ ಹಾಗೂ ಅದೇ ದಿನ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ನೇರ ಹಣ ಜಮೆ.",
        "required_documents": json.dumps(["Aadhaar Card", "Bank Passbook with IFSC", "APMC Gate Entry Pass / Sowing Record"]),
        "application_steps": json.dumps([
            "1. Bring farm produce to e-NAM integrated APMC market yard gate.",
            "2. Generate e-Gate Pass and submit sample for electronic assaying assay.",
            "3. Live bidding takes place online across national buyers.",
            "4. Farmer accepts winning bid, weighing completed, and payment transferred via DBT."
        ]),
        "application_period": "Open Throughout Year on Mandi Trading Days",
        "official_url": "https://enam.gov.in",
        "source_url": "https://enam.gov.in/web",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 16: NFSM-SEEDS
    {
        "scheme_id": "NFSM-SEEDS",
        "scheme_name": "National Food Security Mission: Certified Seed Distribution & Mini-kits",
        "scheme_name_kn": "ರಾಷ್ಟ್ರೀಯ ಆಹಾರ ಭದ್ರತಾ ಮಿಷನ್ - ಪ್ರಮಾಣಿತ ಬಿತ್ತನೆ ಬೀಜ ಮತ್ತು ಮಿನಿಕಿಟ್ ವಿತರಣೆ",
        "scheme_type": "Centrally Sponsored Scheme",
        "scheme_category": "Seeds & Crop Production",
        "department": "Department of Agriculture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Subsidizes high-yielding and climate-resilient certified seeds of pulses (tur, gram, moong, urad) and coarse cereals (ragi, jowar, bajra, maize) with 50% subsidy on seed cost and free pulse seed mini-kits for small and marginal farmers.",
        "description_kn": "ಸುಧಾರಿತ ಮತ್ತು ಅಧಿಕ ಇಳುವರಿ ನೀಡುವ ದ್ವಿದಳ ಧಾನ್ಯಗಳು (ತೊಗರಿ, ಕಡಲೆ, ಹೆಸರು) ಮತ್ತು ಸಿರಿಧಾನ್ಯಗಳ (ರಾಗಿ, ಜೋಳ) ಪ್ರಮಾಣಿತ ಬಿತ್ತನೆ ಬೀಜಗಳ ಮೇಲೆ ಶೇ. 50 ರಷ್ಟು ಸಹಾಯಧನ ಮತ್ತು ಸಣ್ಣ ರೈತರಿಗೆ ಉಚಿತ ಬೀಜ ಮಿನಿಕಿಟ್ ನೀಡುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "eligible_seeds": "Certified breeder/foundation seeds distributed through Raitha Samparka Kendras (RSK)",
            "subsidy": "Up to 50% of seed purchase price or maximum ₹50/kg for certified pulses"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "SC/ST", "Women", "General", "Tenant Farmers"]),
        "eligible_crops": json.dumps(["Tur", "Ragi", "Jowar", "Maize", "Groundnut", "Paddy", "Pulses", "Soybean"]),
        "land_requirements": "Cultivation of field crops in Karnataka (RTC or sowing declaration required)",
        "max_land_acres": 5.0,
        "min_land_acres": 0.5,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "50% direct subsidy on certified seed bags purchased at Raitha Samparka Kendras and free 4 kg pulse seed mini-kits.",
        "benefit_details_kn": "ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರಗಳಲ್ಲಿ ಪ್ರಮಾಣಿತ ಬಿತ್ತನೆ ಬೀಜಗಳ ಮೇಲೆ ಶೇ. 50 ರಿಯಾಯಿತಿ ಮತ್ತು ಉಚಿತ ಬೀಜ ಮಿನಿಕಿಟ್ ವಿತರಣೆ.",
        "required_documents": json.dumps(["RTC (Pahani) or Tenant Sowing Certificate", "Aadhaar Card", "Farmer ID (FID / Fruits ID)"]),
        "application_steps": json.dumps([
            "1. Visit nearest Raitha Samparka Kendra (RSK) during pre-sowing window.",
            "2. Provide FID (FRUITS ID) or Aadhaar number for biometric POS authentication.",
            "3. Collect subsidized certified seed bags with official cash receipt."
        ]),
        "application_period": "Kharif (May-July) and Rabi (Sept-Nov)",
        "official_url": "https://nfsm.gov.in",
        "source_url": "https://raitamitra.karnataka.gov.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 17: FPO-PRODUCE
    {
        "scheme_id": "FPO-PRODUCE",
        "scheme_name": "Formation & Promotion of 10,000 Farmer Producer Organizations (FPOs)",
        "scheme_name_kn": "ರೈತ ಉತ್ಪಾದಕ ಸಂಸ್ಥೆಗಳ (ಎಫ್‌ಪಿಒ) ರಚನೆ ಮತ್ತು ಉತ್ತೇಜನ ಯೋಜನೆ",
        "scheme_type": "Central Sector Scheme",
        "scheme_category": "Post-Harvest & Marketing",
        "department": "NABARD / SFAC / NCDC & GoK",
        "department_kn": "ನಬಾರ್ಡ್ ಮತ್ತು ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ",
        "description": "Promotes farmer collectives into registered FPOs to achieve economies of scale. Provides equity grant up to ₹15 Lakh per FPO matching farmer member contribution, management support of ₹18 Lakh for 3 years, and Credit Guarantee up to ₹2 Crore.",
        "description_kn": "ಸಣ್ಣ ಮತ್ತು ಅತಿ ಸಣ್ಣ ರೈತರನ್ನು ಒಗ್ಗೂಡಿಸಿ ರೈತ ಉತ್ಪಾದಕ ಸಂಸ್ಥೆಗಳನ್ನು (FPO) ರಚಿಸಲು ಪ್ರತಿ ಸಂಸ್ಥೆಗೆ ₹15 ಲಕ್ಷದವರೆಗೆ ಮ್ಯಾಚಿಂಗ್ ಇಕ್ವಿಟಿ ಅನುದಾನ ಹಾಗೂ ₹18 ಲಕ್ಷ ನಿರ್ವಹಣಾ ನೆರವು ಒದಗಿಸುವ ಮಹತ್ವದ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "minimum_members": "Minimum 300 farmer members in plains, 100 members in hilly/Ghat areas",
            "focus": "Small, marginal and women farmer inclusion"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "Tenant Farmers", "Women", "General", "SC/ST"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Practicing cultivators in Karnataka",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "Matching equity grant up to ₹15,00,000 per FPO, direct bulk purchase of inputs at 15-20% discount, and collective bargaining for output marketing.",
        "benefit_details_kn": "ಪ್ರತಿ ಎಫ್‌ಪಿಒಗೆ ₹15 ಲಕ್ಷದವರೆಗೆ ಇಕ್ವಿಟಿ ಅನುದಾನ, ಕಡಿಮೆ ಬೆಲೆಗೆ ಸಗಟು ಗೊಬ್ಬರ-ಔಷಧಿ ಖರೀದಿ ಮತ್ತು ಉತ್ಪನ್ನಗಳಿಗೆ ಉತ್ತಮ ಬೆಲೆ.",
        "required_documents": json.dumps(["Aadhaar Card", "RTC / Land record", "FPO Shareholder Membership Form", "Bank Account Details"]),
        "application_steps": json.dumps([
            "1. Enroll as member shareholder in local Taluk FPO through Raitha Samparka Kendra or CBBO.",
            "2. Contribute one-time nominal share capital (₹1,000 - ₹2,000).",
            "3. Access institutional inputs, rental machinery, and collective aggregation facilities."
        ]),
        "application_period": "Open Throughout Year",
        "official_url": "https://sfacindia.com",
        "source_url": "https://www.nabard.org/content1.aspx?id=594&catid=23&mid=530",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 18: RAITHA-SIRI
    {
        "scheme_id": "RAITHA-SIRI",
        "scheme_name": "Karnataka Raitha Siri Scheme for Millets Promotion",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ರೈತ ಸಿರಿ ಸಿರಿಧಾನ್ಯ ಪ್ರೋತ್ಸಾಹಧನ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Millet Crop Incentives",
        "department": "Department of Agriculture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Special state financial incentive of ₹10,000 per hectare (up to a maximum of 2 hectares = ₹20,000) directly transferred into farmers' bank accounts via DBT for cultivating designated millets (Ragi, Jowar, Bajra, Foxtail millet, Little millet, Kodo millet).",
        "description_kn": "ಕರ್ನಾಟಕದ ರೈತರು ಸಿರಿಧಾನ್ಯಗಳನ್ನು (ರಾಗಿ, ಜೋಳ, ಸಜ್ಜೆ, ನವಣೆ, ಸಾಮೆ, ಹಾರಕ, ಕೊರಲೆ) ಬೆಳೆಯಲು ಉತ್ತೇಜಿಸಲು ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ₹10,000 (ಗರಿಷ್ಠ 2 ಹೆಕ್ಟೇರ್‌ಗೆ ₹20,000) ನೇರ ನಗದು ಪ್ರೋತ್ಸಾಹಧನ ನೀಡುವ ಜನಪ್ರಿಯ ರಾಜ್ಯ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "eligible_crops": "Ragi, Jowar, Bajra, Foxtail millet (Navane), Little millet (Same), Kodo millet (Haraka), Proso millet (Baragu), Barnyard millet (Oodalu)",
            "rate": "₹10,000 per hectare up to maximum 2 hectares (₹20,000 maximum per farmer)"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["Ragi", "Jowar", "Millets", "Bajra"]),
        "land_requirements": "Cultivation of notified millets in Karnataka on minimum 0.5 acre to maximum 2 hectares",
        "max_land_acres": 5.0,
        "min_land_acres": 0.5,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts (rainfed millet zones in North & South Karnataka)",
        "benefit_details": "Direct Cash Transfer (DBT) of ₹10,000 per hectare (up to ₹20,000 for 2 hectares) credited directly to farmer's Aadhaar-linked bank account.",
        "benefit_details_kn": "ಪ್ರತಿ ಹೆಕ್ಟೇರ್ ಸಿರಿಧಾನ್ಯ ಬೆಳೆಗೆ ₹10,000 ನೇರ ನಗದು ಸಹಾಯಧನ (ಡಿಬಿಟಿ ಮೂಲಕ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಜಮೆ).",
        "required_documents": json.dumps(["Current RTC (Pahani) with Millet Crop Survey Entry", "Aadhaar Card", "FRUITS ID (FID)", "Bank Passbook"]),
        "application_steps": json.dumps([
            "1. Ensure millet crop is officially recorded in Digital Crop Survey (Bele Samikshe) during Kharif season.",
            "2. Register application at nearest Raitha Samparka Kendra or via K-Kisan / Fruits portal.",
            "3. Village Nodal Officer verifies crop standing.",
            "4. Incentive credited via DBT into Aadhaar-seeded bank account."
        ]),
        "application_period": "Kharif Season (Crop survey entry July to October)",
        "official_url": "https://raitamitra.karnataka.gov.in",
        "source_url": "https://raitamitra.karnataka.gov.in/info-2/Raitha+Siri/kn",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 19: KA-AGRI-MECH
    {
        "scheme_id": "KA-AGRI-MECH",
        "scheme_name": "Karnataka Farm Mechanization Assistance Scheme (Raita Shakti / Agri-Mech)",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ಪ್ರೋತ್ಸಾಹ ಯೋಜನೆ (ರೈತ ಶಕ್ತಿ)",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Farm Mechanization",
        "department": "Department of Agriculture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "State scheme providing 50% to 90% capital subsidy for purchase of small farm machineries (power weeders, paddy transplanters, knapsack/power sprayers, chaff cutters, seed-cum-fertilizer drills, diesel engines) with preferential funding for SC/ST and women farmers.",
        "description_kn": "ಸಣ್ಣ ಕೃಷಿ ಯಂತ್ರಗಳಾದ ಪವರ್ ವೀಡರ್, ಭತ್ತ ನಾಟಿ ಯಂತ್ರ, ಔಷಧಿ ಸಿಂಪಡಿಸುವ ಪವರ್ ಸ್ಪ್ರೇಯರ್, ಹುಲ್ಲು ಕತ್ತರಿಸುವ ಯಂತ್ರ ಮುಂತಾದವುಗಳ ಖರೀದಿಗೆ ಶೇ. 50 ರಿಂದ 90 ರಷ್ಟು ರಾಜ್ಯ ಸರ್ಕಾರಿ ಸಹಾಯಧನ.",
        "eligibility_conditions": json.dumps({
            "subsidy": "90% for SC/ST small farmers; 50% for General small/marginal farmers",
            "land": "Registered landholder in Karnataka"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "SC/ST", "Women", "General"]),
        "eligible_crops": json.dumps(["All", "Paddy", "Sugarcane", "Arecanut", "Maize", "Cotton"]),
        "land_requirements": "Registered agricultural land with clear title",
        "max_land_acres": 5.0,
        "min_land_acres": 0.5,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "50% to 90% direct subsidy on approved agricultural implements reducing manual labor dependency and cultivation costs.",
        "benefit_details_kn": "ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳಿಗೆ ಶೇ. 50 ರಿಂದ 90 ರಷ್ಟು ನೇರ ಸಬ್ಸಿಡಿ.",
        "required_documents": json.dumps(["RTC (Pahani)", "Aadhaar Card", "Bank Passbook", "Caste Certificate (if SC/ST)", "FRUITS ID"]),
        "application_steps": json.dumps([
            "1. Apply via Karnataka Seva Sindhu or K-Kisan portal.",
            "2. Submit quotation from authorized agricultural machinery dealer.",
            "3. Verification and allotment order by Taluk Assistant Director of Agriculture.",
            "4. Machine delivered and verified via GPS photo, subsidy released to dealer/farmer."
        ]),
        "application_period": "Annual Budgetary Window (May to November)",
        "official_url": "https://raitamitra.karnataka.gov.in",
        "source_url": "https://raitamitra.karnataka.gov.in/info-2/Farm+Mechanization/en",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1595838728639-4458f27fb636?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 20: KA-MICRO-IRRIG
    {
        "scheme_id": "KA-MICRO-IRRIG",
        "scheme_name": "Karnataka Micro-Irrigation Promotion Scheme (Top-Up)",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ರಾಜ್ಯ ಸೂಕ್ಷ್ಮ ನೀರಾವರಿ ಪ್ರೋತ್ಸಾಹ ಯೋಜನೆ (ಟಾಪ್-ಅಪ್)",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Irrigation & Water",
        "department": "Department of Agriculture & Horticulture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಮತ್ತು ತೋಟಗಾರಿಕೆ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "State top-up scheme enhancing central PMKSY micro-irrigation subsidies to 90% for SC/ST farmers and 75% for General category farmers (up to 5 acres) for installing Drip and Sprinkler irrigation units.",
        "description_kn": "ಕೇಂದ್ರದ ಪಿಎಂಕೆಎಸ್‌ವೈ ಸಹಾಯಧನಕ್ಕೆ ರಾಜ್ಯ ಸರ್ಕಾರದಿಂದ ಹೆಚ್ಚುವರಿ ಟಾಪ್-ಅಪ್ ಸಬ್ಸಿಡಿ ಸೇರಿಸಿ ಎಸ್‌ಸಿ/ಎಸ್‌ಟಿ ರೈತರಿಗೆ ಶೇ. 90 ಮತ್ತು ಸಾಮಾನ್ಯ ರೈತರಿಗೆ ಶೇ. 75 ರವರೆಗೆ ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿ ಸೌಲಭ್ಯ ಒದಗಿಸುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "rate": "90% total subsidy for SC/ST; 75% total subsidy for General farmers up to 5 acres",
            "water_source": "Functional borewell, open well, or farm pond required"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "SC/ST", "General", "Women"]),
        "eligible_crops": json.dumps(["All", "Sugarcane", "Arecanut", "Banana", "Vegetables", "Paddy", "Cotton", "Maize"]),
        "land_requirements": "Own agricultural land with verified irrigation source",
        "max_land_acres": 5.0,
        "min_land_acres": 0.5,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "Up to 90% total combined subsidy for complete Drip/Sprinkler kit including filters, lateral pipes, and drippers.",
        "benefit_details_kn": "ಹನಿ ನೀರಾವರಿ ಘಟಕಕ್ಕೆ ಶೇ. 75 ರಿಂದ 90 ರಷ್ಟು ಭಾರಿ ಸಹಾಯಧನ.",
        "required_documents": json.dumps(["Current RTC (Pahani)", "Aadhaar Card", "Electricity / Water source bill or certificate", "Bank Passbook", "Caste Certificate"]),
        "application_steps": json.dumps([
            "1. Submit online application on Karnataka Seva Sindhu / K-Kisan.",
            "2. Empanelled vendor surveys the field and prepares technical layout.",
            "3. Department approves subsidy sanction.",
            "4. Vendor installs system, GPS-tagged inspection conducted, subsidy released."
        ]),
        "application_period": "Open Throughout Year",
        "official_url": "https://horticulturedir.karnataka.gov.in",
        "source_url": "https://horticulturedir.karnataka.gov.in/info-2/Micro+Irrigation/en",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 21: KA-HORTI-POLY
    {
        "scheme_id": "KA-HORTI-POLY",
        "scheme_name": "Karnataka Polyhouse & Protected Horticulture Cultivation Scheme",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಪಾಲಿಹೌಸ್ ಹಾಗೂ ಸಂರಕ್ಷಿತ ತೋಟಗಾರಿಕೆ ಬೆಳೆ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Horticulture Development",
        "department": "Department of Horticulture, Government of Karnataka",
        "department_kn": "ತೋಟಗಾರಿಕೆ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Provides 50% capital subsidy for construction of naturally ventilated polyhouses and shade net structures (up to 4,000 sq.m) for high-value off-season vegetable, flower, and exotic crop cultivation.",
        "description_kn": "ಅಧಿಕ ಮೌಲ್ಯದ ತರಕಾರಿ, ಹೂವು ಹಾಗೂ ವಿಲಕ್ಷಣ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯಲು ನೈಸರ್ಗಿಕ ಗಾಳಿ-ಬೆಳಕಿನ ಪಾಲಿಹೌಸ್ ಮತ್ತು ನೆರಳು ಪರದೆ (ಶೇಡ್ ನೆಟ್) ನಿರ್ಮಾಣಕ್ಕೆ ಶೇ. 50 ರಷ್ಟು ಸಹಾಯಧನ ನೀಡುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "unit_size": "Minimum 500 sq. meters to maximum 4,000 sq. meters per beneficiary",
            "subsidy": "50% of cost norm specified by State Horticulture Mission"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["Vegetables", "Flowers", "Capsicum", "Tomato", "Cucumber", "Banana", "Orchids"]),
        "land_requirements": "Ownership of agricultural land with assured round-the-year quality water",
        "max_land_acres": None,
        "min_land_acres": 0.25,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts (peri-urban and high-value zones)",
        "benefit_details": "50% capital construction subsidy (up to ₹450-₹500 per sq. meter) for polyhouse structure and micro-fogger irrigation.",
        "benefit_details_kn": "ಪಾಲಿಹೌಸ್ ನಿರ್ಮಾಣ ವೆಚ್ಚಕ್ಕೆ ಶೇ. 50 ರಷ್ಟು (ಪ್ರತಿ ಚದರ ಮೀಟರ್‌ಗೆ ₹೪೫೦-₹೫೦೦ ವರೆಗೆ) ಸಹಾಯಧನ.",
        "required_documents": json.dumps(["RTC (Pahani)", "Aadhaar Card", "Bank Passbook", "Water Quality Test Report", "Polyhouse Technical Drawing"]),
        "application_steps": json.dumps([
            "1. Apply at District Senior Assistant Director of Horticulture (SADH) office or Seva Sindhu.",
            "2. Submit quotation and structural drawings from authorized fabrication agency.",
            "3. Department issues administrative sanction.",
            "4. Post-construction inspection and subsidy credit via DBT."
        ]),
        "application_period": "Annual Quota Allocation (June to December)",
        "official_url": "https://horticulturedir.karnataka.gov.in",
        "source_url": "https://horticulturedir.karnataka.gov.in/info-2/Protected+Cultivation/en",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 22: KA-SAVAYAVA
    {
        "scheme_id": "KA-SAVAYAVA",
        "scheme_name": "Karnataka Savayava Bhagya & Organic Village Mission",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಸಾವಯವ ಭಾಗ್ಯ ಹಾಗೂ ಸಾವಯವ ಗ್ರಾಮ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Organic & Natural Farming",
        "department": "Department of Agriculture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Promotes chemical-free organic farming in designated village clusters of 100 hectares. Provides assistance for vermicompost pits, bio-digesters, organic bio-fertilizer kits, and third-party certified organic export facilitation with ₹10,000/ha state support.",
        "description_kn": "೧೦೦ ಹೆಕ್ಟೇರ್ ವಿಸ್ತೀರ್ಣದ ಗ್ರಾಮ ಕ್ಲಸ್ಟರ್‌ಗಳಲ್ಲಿ ಸಾವಯವ ಕೃಷಿಯನ್ನು ಉತ್ತೇಜಿಸುವ ಯೋಜನೆ. ಎರೆಹುಳು ಗೊಬ್ಬರ ತೊಟ್ಟಿ, ಜೈವಿಕ ಅನಿಲ, ಜೈವಿಕ ಗೊಬ್ಬರ ಕಿಟ್‌ಗಳು ಮತ್ತು ಸಾವಯವ ಪ್ರಮಾಣೀಕರಣಕ್ಕೆ ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ₹10,000 ವರೆಗೆ ಸಹಾಯಧನ.",
        "eligibility_conditions": json.dumps({
            "cluster": "Selection within recognized Savayava Grama Panchayat clusters in Karnataka",
            "commitment": "Adoption of certified organic farming practices"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All", "Paddy", "Ragi", "Jowar", "Pulses", "Sugarcane", "Arecanut", "Banana", "Pepper"]),
        "land_requirements": "Agricultural land participating in organic cluster",
        "max_land_acres": None,
        "min_land_acres": 0.5,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "₹10,000/ha assistance for organic inputs, subsidized vermicompost beds, free NPOP organic certification, and premium market linkage.",
        "benefit_details_kn": "ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ₹10,000 ಸಹಾಯ, ಎರೆಹುಳು ಗೊಬ್ಬರ ಘಟಕ ನಿರ್ಮಾಣ ನೆರವು ಮತ್ತು ಸಾವಯವ ಉತ್ಪನ್ನಗಳಿಗೆ ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ.",
        "required_documents": json.dumps(["RTC (Pahani)", "Aadhaar Card", "Bank Passbook", "Organic Farming Agreement"]),
        "application_steps": json.dumps([
            "1. Register with Taluk Organic Farming Federation / Raitha Samparka Kendra.",
            "2. Join local village organic farmer group.",
            "3. Setup vermicompost pit and use approved bio-fertilizers.",
            "4. Incentive credited via DBT upon third-party organic inspection."
        ]),
        "application_period": "Pre-Monsoon (May to August)",
        "official_url": "https://raitamitra.karnataka.gov.in",
        "source_url": "https://raitamitra.karnataka.gov.in/info-2/Savayava+Bhagya/kn",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1500651230702-0e2d8a49d4ad?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 23: KA-DISASTER-RELIEF
    {
        "scheme_id": "KA-DISASTER-RELIEF",
        "scheme_name": "Karnataka Parihara: SDRF / NDRF Calamity Crop Loss Relief",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಪರಿಹಾರ - ಎಸ್‌ಡಿಆರ್‌ಎಫ್/ಎನ್‌ಡಿಆರ್‌ಎಫ್ ಬೆಳೆ ಹಾನಿ ಪರಿಹಾರ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Disaster & Calamity Relief",
        "department": "Revenue & Agriculture Department, Government of Karnataka",
        "department_kn": "ಕಂದಾಯ ಮತ್ತು ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Direct financial relief for farmers experiencing crop loss of 33% or more due to natural disasters (floods, heavy rain, drought, hailstorms). Compensation rates: ₹8,500/ha for rainfed crops, ₹17,000/ha for irrigated crops, and ₹22,500/ha for perennial/horticultural crops.",
        "description_kn": "ಪ್ರವಾಹ, ಅತಿಯಾದ ಮಳೆ ಅಥವಾ ಬರಗಾಲದಿಂದ ಶೇ. 33 ಕ್ಕಿಂತ ಹೆಚ್ಚು ಬೆಳೆ ಹಾನಿಯಾದಾಗ ರಾಜ್ಯ ಸರ್ಕಾರದ ಪರಿಹಾರ ಪೋರ್ಟಲ್ ಮೂಲಕ ನೇರ ನಗದು ಪರಿಹಾರ. ಮಳೆಯಾಶ್ರಿತ ಬೆಳೆಗೆ ಹೆಕ್ಟೇರ್‌ಗೆ ₹8,500, ನೀರಾವರಿ ಬೆಳೆಗೆ ₹17,000 ಹಾಗೂ ತೋಟಗಾರಿಕೆ ಬೆಳೆಗೆ ₹22,500 ಪರಿಹಾರ.",
        "eligibility_conditions": json.dumps({
            "loss_threshold": "Crop damage of 33% and above assessed by joint survey team (Revenue, Agriculture, Panchayat)",
            "rate": "Rainfed: ₹8,500/ha; Irrigated: ₹17,000/ha; Perennial: ₹22,500/ha"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All", "Paddy", "Arecanut", "Banana", "Pepper", "Sugarcane", "Cotton", "Maize", "Ragi", "Jowar"]),
        "land_requirements": "Land affected by declared natural calamity in Karnataka",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts (Calamity-Notified Hoblis/Taluks)",
        "benefit_details": "Direct cash compensation into Aadhaar-seeded bank account (up to ₹22,500 per hectare for perennial crops and ₹17,000/ha for irrigated crops) within 30 days of survey.",
        "benefit_details_kn": "ಬೆಳೆ ಹಾನಿಗೆ ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ₹೮,೫೦೦ ರಿಂದ ₹೨೨,೫೦೦ ವರೆಗೆ ನೇರ ಪರಿಹಾರ ಧನ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಜಮೆ.",
        "required_documents": json.dumps(["Current RTC (Pahani) or Joint Cultivation Certificate", "Aadhaar Card", "Bank Account Details", "Joint Damage Survey Report (Parihara ID)"]),
        "application_steps": json.dumps([
            "1. Village Accountant (VA) and Agriculture Officer conduct joint GPS damage survey.",
            "2. Survey details and photo uploaded to Karnataka Parihara Portal (parihara.karnataka.gov.in).",
            "3. Farmer verifies survey entry using Aadhaar number on Parihara portal.",
            "4. Funds disbursed automatically through Aadhaar Payment Bridge (APB)."
        ]),
        "application_period": "Post-calamity notification window (active within 30 days of disaster)",
        "official_url": "https://parihara.karnataka.gov.in",
        "source_url": "https://parihara.karnataka.gov.in/service92",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1547683905-f686c993aae5?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 24: KA-PASHU-BHAGYA
    {
        "scheme_id": "KA-PASHU-BHAGYA",
        "scheme_name": "Karnataka Pashu Bhagya Scheme for Integrated Animal Husbandry",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಪಶು ಭಾಗ್ಯ ಸಮಗ್ರ ಪಶುಪಾಲನಾ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Livestock & Integrated Farming",
        "department": "Department of Animal Husbandry and Veterinary Services, GoK",
        "department_kn": "ಪಶುಪಾಲನಾ ಮತ್ತು ಪಶುವೈದ್ಯಕೀಯ ಸೇವಾ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Subsidizes establishment of small dairy units (2 cows/buffaloes), sheep/goat rearing (10+1), poultry, or piggery units with 50% subsidy for General farmers and 70% subsidy for SC/ST farmers, with short-term livestock credit up to ₹1.2 Lakh at zero/low interest.",
        "description_kn": "ರೈತರ ಪೂರಕ ಆದಾಯಕ್ಕಾಗಿ ಹೈನುಗಾರಿಕೆ (2 ಹಸು/ಎಮ್ಮೆ), ಕುರಿ-ಮೇಕೆ ಸಾಕಾಣಿಕೆ (10+1) ಅಥವಾ ಕೋಳಿ ಸಾಕಾಣಿಕೆ ಘಟಕಗಳಿಗೆ ಸಾಮಾನ್ಯ ವರ್ಗಕ್ಕೆ ಶೇ. 50 ಮತ್ತು ಎಸ್‌ಸಿ/ಎಸ್‌ಟಿ ವರ್ಗಕ್ಕೆ ಶೇ. 70 ರಷ್ಟು ಭಾರಿ ಸಹಾಯಧನ ನೀಡುವ ಯೋಜನೆ.",
        "eligibility_conditions": json.dumps({
            "subsidy": "50% for General; 70% for SC/ST beneficiaries",
            "scope": "Dairy, sheep/goat, poultry, or piggery units"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All", "Fodder"]),
        "land_requirements": "Land suitable for cattle shelter or fodder cultivation (minimum 0.25 acre)",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "50% to 70% subsidy on purchase of dairy animals and animal housing, plus low-interest credit via cooperative banks.",
        "benefit_details_kn": "ಹಸು/ಎಮ್ಮೆ, ಕುರಿ-ಮೇಕೆ ಸಾಕಾಣಿಕೆ ಘಟಕಗಳಿಗೆ ಶೇ. 50 ರಿಂದ 70 ರಷ್ಟು ಸರ್ಕಾರಿ ಸಹಾಯಧನ.",
        "required_documents": json.dumps(["RTC (Pahani) or Resident Certificate", "Aadhaar Card", "Bank Passbook", "Caste Certificate (if SC/ST)", "Veterinary Officer Health Certificate"]),
        "application_steps": json.dumps([
            "1. Apply via Taluk Assistant Director of Veterinary Services or Seva Sindhu.",
            "2. Verification of fodder availability and shed location by local Veterinary Officer.",
            "3. Animal purchase through official cattle purchase committee (Shandy).",
            "4. Subsidy directly credited into beneficiary bank account."
        ]),
        "application_period": "Annual Budgetary Window (June to November)",
        "official_url": "https://ahvs.karnataka.gov.in",
        "source_url": "https://ahvs.karnataka.gov.in/info-2/Pashu+Bhagya/en",
        "verification_date": "2026-10-25",
        "verification_status": "Verified",
        "current_status": "Active",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 25: KA-CM-KISAN (Verification Required)
    {
        "scheme_id": "KA-CM-KISAN",
        "scheme_name": "Karnataka Chief Minister Raitha Siri / CM-Kisan Top-Up Scheme",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಮುಖ್ಯಮಂತ್ರಿ ರೈತ ಸಿರಿ / ಸಿಎಂ-ಕಿಸಾನ್ ಹೆಚ್ಚುವರಿ ನೆರವು ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Income Support",
        "department": "Department of Agriculture, Government of Karnataka",
        "department_kn": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "State supplemental top-up scheme providing additional annual financial assistance to PM-KISAN eligible landholding farmers in Karnataka. NOTE: State budgetary allocation and disbursement schedule for the current financial cycle is currently under official cabinet review.",
        "description_kn": "ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆಯಡಿ ಅರ್ಹರಾಗಿರುವ ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ರಾಜ್ಯ ಸರ್ಕಾರದಿಂದ ಹೆಚ್ಚುವರಿ ಆರ್ಥಿಕ ನೆರವು ಒದಗಿಸುವ ಯೋಜನೆ. ಗಮನಿಸಿ: ಪ್ರಸ್ತುತ ಆರ್ಥಿಕ ವರ್ಷದ ರಾಜ್ಯ ಸರ್ಕಾರದ ಅನುದಾನ ಮತ್ತು ಪಾವತಿ ವೇಳಾಪಟ್ಟಿಯು ಸಚಿವ ಸಂಪುಟದ ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ (ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ).",
        "eligibility_conditions": json.dumps({
            "base_requirement": "Active beneficiary of PM-KISAN in Karnataka",
            "verification_notice": "Subject to ongoing State Cabinet budget re-allocation guidelines"
        }),
        "eligible_farmer_categories": json.dumps(["Small and Marginal", "General", "SC/ST", "Women"]),
        "eligible_crops": json.dumps(["All"]),
        "land_requirements": "Own agricultural land with registered RTC title",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Own",
        "location_restrictions": "All Karnataka Districts",
        "benefit_details": "State top-up financial assistance (Status: Subject to current cabinet budgetary notification and verification).",
        "benefit_details_kn": "ರಾಜ್ಯ ಸರ್ಕಾರದ ಹೆಚ್ಚುವರಿ ಸಹಾಯಧನ (ಸ್ಥಿತಿ: ಸಚಿವ ಸಂಪುಟದ ಮರುಪರಿಶೀಲನೆಗೆ ಒಳಪಟ್ಟಿದೆ).",
        "required_documents": json.dumps(["Aadhaar Card", "RTC (Pahani)", "PM-KISAN Registration ID", "Bank Passbook"]),
        "application_steps": json.dumps([
            "1. Active registration in PM-KISAN portal.",
            "2. Automatic linkage through Karnataka FRUITS database.",
            "3. Awaiting formal notification of current disbursement cycle."
        ]),
        "application_period": "State Review Pending / Verification Required",
        "official_url": "https://raitamitra.karnataka.gov.in",
        "source_url": "https://raitamitra.karnataka.gov.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verification Required",
        "current_status": "Verification Required",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=800&q=80"
    },

    # VERIFIED SCHEME 26: KA-PUNYAKOTI (Verification Required)
    {
        "scheme_id": "KA-PUNYAKOTI",
        "scheme_name": "Karnataka Punyakoti Dattu & Cattle Insurance Subsidy Scheme",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಪುಣ್ಯಕೋಟಿ ದತ್ತು ಹಾಗೂ ಜಾನುವಾರು ವಿಮೆ ಸಹಾಯಧನ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
        "scheme_category": "Livestock & Integrated Farming",
        "department": "Department of Animal Husbandry and Veterinary Services, GoK",
        "department_kn": "ಪಶುಪಾಲನಾ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ",
        "description": "Subsidizes indigenous cattle adoption and provides premium subsidies for rural cattle insurance. NOTE: Gram Panchayat quota allocation and taluk-level beneficiary targets are currently undergoing quarterly verification with local veterinary offices.",
        "description_kn": "ಗ್ರಾಮೀಣ ಜಾನುವಾರುಗಳಿಗೆ ವಿಮಾ ಪ್ರೀಮಿಯಂ ಸಹಾಯಧನ ಮತ್ತು ಪುಣ್ಯಕೋಟಿ ದತ್ತು ಯೋಜನೆ. ಗಮನಿಸಿ: ಪ್ರಸ್ತುತ ತ್ರೈಮಾಸಿಕದ ಗ್ರಾಮ ಪಂಚಾಯತಿ ಕೋಟಾ ಮತ್ತು ಫಲಾನುಭವಿಗಳ ಪಟ್ಟಿಯು ಪಶುವೈದ್ಯಕೀಯ ಇಲಾಖೆಯಲ್ಲಿ ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ (ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ).",
        "eligibility_conditions": json.dumps({
            "cattle": "Indigenous and cross-breed cattle tagged under INAPH",
            "verification_notice": "Local veterinary officer quota availability verification required"
        }),
        "eligible_farmer_categories": json.dumps(["All", "Small and Marginal", "Tenant Farmers", "General", "SC/ST"]),
        "eligible_crops": json.dumps(["All", "Fodder"]),
        "land_requirements": "Cattle rearer in Karnataka",
        "max_land_acres": None,
        "min_land_acres": 0.1,
        "required_ownership": "Any",
        "location_restrictions": "All Karnataka Districts (Quota subject to local Gram Panchayat)",
        "benefit_details": "Subsidized cattle insurance premium coverage and indigenous breed maintenance support.",
        "benefit_details_kn": "ಜಾನುವಾರು ವಿಮಾ ಪ್ರೀಮಿಯಂ ಸಹಾಯಧನ (ಸ್ಥಳೀಯ ಪಶುವೈದ್ಯರ ಕೋಟಾ ಪರಿಶೀಲನೆಗೆ ಒಳಪಟ್ಟಿದೆ).",
        "required_documents": json.dumps(["INAPH Ear Tag Number", "Aadhaar Card", "Veterinary Certificate", "Bank Passbook"]),
        "application_steps": json.dumps([
            "1. Contact local Gram Panchayat Veterinary Dispensary.",
            "2. Submit cattle ear-tag number and health record.",
            "3. Verification against current quarter taluk quota."
        ]),
        "application_period": "Quarterly Allocation Window / Verification Required",
        "official_url": "https://punyakoti.karnataka.gov.in",
        "source_url": "https://ahvs.karnataka.gov.in",
        "verification_date": "2026-10-25",
        "verification_status": "Verification Required",
        "current_status": "Verification Required",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=800&q=80"
    }
]

# Verified Agricultural Loans Dataset
AGRICULTURAL_LOANS = [
    {
        "loan_id": "KCC",
        "name": "Kisan Credit Card (KCC) Crop Loan",
        "name_kn": "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (ಕೆಸಿಸಿ) ಬೆಳೆ ಸಾಲ",
        "purpose": "Timely short-term credit for cultivating seasonal crops, purchase of seeds, fertilizers, pesticides, and post-harvest maintenance expenses.",
        "purpose_kn": "ಕೃಷಿ ವೆಚ್ಚಗಳಾದ ಬೀಜ, ಗೊಬ್ಬರ, ಕೀಟನಾಶಕಗಳ ಖರೀದಿ ಹಾಗೂ ಬೆಳೆ ಕಟಾವಿನ ವೆಚ್ಚಗಳಿಗಾಗಿ ರಿಯಾಯಿತಿ ದರದ ಅಲ್ಪಾವಧಿ ಸಾಲ.",
        "interest_rate": "7.0% p.a. (Effectively 4.0% p.a. with prompt repayment subvention up to ₹3 Lakh)",
        "max_amount": "₹3,00,000 without collateral up to ₹1.6 Lakh",
        "eligibility": "All farmers, individual/joint cultivators, tenant farmers, sharecroppers, and Self Help Groups (SHGs) cultivating Karnataka agricultural land.",
        "required_documents": [
            "Duly filled application form",
            "RTC (Pahani) / Land ownership or cultivation agreement",
            "Aadhaar Card / Voter ID",
            "Bank passbook copy and passport photos"
        ],
        "official_source": "Reserve Bank of India / NABARD KCC Guidelines (nabard.org)"
    },
    {
        "loan_id": "TRACTOR-EQUIP",
        "name": "Farm Mechanization & Tractor Loan",
        "name_kn": "ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ಹಾಗೂ ಟ್ರ್ಯಾಕ್ಟರ್ ಸಾಲ",
        "purpose": "Medium-to-long term financing for purchase of new tractors, rotavators, power tillers, and harvesters.",
        "purpose_kn": "ಹೊಸ ಟ್ರ್ಯಾಕ್ಟರ್, ಟಿಲ್ಲರ್ ಹಾಗೂ ಕೊಯ್ಲು ಯಂತ್ರಗಳ ಖರೀದಿಗೆ ದೀರ್ಘಾವಧಿ ಕಂತಿನ ಸಾಲ.",
        "interest_rate": "8.5% to 10.5% p.a. with State Government mechanization subsidy back-ended credit",
        "max_amount": "Up to 85% - 90% of on-road quotation value",
        "eligibility": "Farmers holding minimum 3 to 5 acres of irrigated/cultivable land with clear title and repayment capability.",
        "required_documents": [
            "Land title deeds (Pahani & Mutation)",
            "Authorized tractor/implement dealer quotation",
            "KYC documents (Aadhaar, PAN)",
            "No-dues certificate from nearby financial institutions"
        ],
        "official_source": "State Bank of India / Canara Bank Agri Credit (canarabank.com)"
    },
    {
        "loan_id": "IRRIGATION-SOLAR",
        "name": "Solar Agri Pump Loan (PM-KUSUM Linkage)",
        "name_kn": "ಸೌರ ಕೃಷಿ ಪಂಪ್ ಸಾಲ (ಪಿಎಂ-ಕುಸುಮ್ ಯೋಜನೆ)",
        "purpose": "Installation of 3HP to 7.5HP standalone solar photovoltaic water pumping systems for off-grid irrigation.",
        "purpose_kn": "ವಿದ್ಯುತ್ ರಹಿತ ಕೃಷಿ ಭೂಮಿಗೆ ಸೋಲಾರ್ ಪಂಪ್‌ಸೆಟ್ ಅಳವಡಿಕೆಗೆ ಸಾಲ ಮತ್ತು ಕೇಂದ್ರ/ರಾಜ್ಯ ಸರ್ಕಾರದ ಶೇ. 60 ರಷ್ಟು ಸಹಾಯಧನ.",
        "interest_rate": "7.5% to 9.0% p.a. (Farmer contributes only 10% equity; 60% is Government subsidy, 30% bank loan)",
        "max_amount": "Up to ₹2,50,000 for farmer share financing",
        "eligibility": "Farmers with agriculture land having an existing borewell or water source with no grid electric connection.",
        "required_documents": [
            "RTC (Pahani) showing agricultural land",
            "KREDL Solar Pump Allotment / In-principle subsidy sanction",
            "Aadhaar and PAN card",
            "Bank statement for past 6 months"
        ],
        "official_source": "Karnataka Renewable Energy Development Ltd (kredlinfo.in) / NABARD"
    },
    {
        "loan_id": "DAIRY-PASHU",
        "name": "Dairy & Livestock Development Loan (Pashu Bhagya)",
        "name_kn": "ಹೈನುಗಾರಿಕೆ ಹಾಗೂ ಜಾನುವಾರು ಸಾಲ (ಪಶು ಭಾಗ್ಯ ಯೋಜನೆ)",
        "purpose": "Purchase of milch animals (cows/buffaloes), construction of cattle sheds, and purchase of dairy equipment.",
        "purpose_kn": "ಹಾಲು ನೀಡುವ ಹಸು/ಎಮ್ಮೆಗಳ ಖರೀದಿ, ಕೊಟ್ಟಿಗೆ ನಿರ್ಮಾಣ ಮತ್ತು ಹಾಲು ಕರೆಯುವ ಯಂತ್ರಗಳ ಖರೀದಿಗೆ ರಿಯಾಯಿತಿ ಸಾಲ.",
        "interest_rate": "0% interest up to ₹50,000 via Primary Dairy Cooperative Societies; 4% to 7% for higher amounts",
        "max_amount": "₹1,20,000 to ₹3,00,000 with 50% to 70% state subsidy",
        "eligibility": "Small and marginal farmers, agricultural laborers, and women SHG members with green fodder availability.",
        "required_documents": [
            "Dairy Cooperative Society (KMF/Nandini) membership passbook",
            "Aadhaar Card and residence certificate",
            "Veterinary health certificate of cattle",
            "Savings bank account details"
        ],
        "official_source": "Karnataka Milk Federation (KMF) & Animal Husbandry Dept (ahvs.karnataka.gov.in)"
    }
]

# Verified Karnataka Crops Knowledge Base
KARNATAKA_CROPS = [
    {
        "crop_id": "paddy",
        "name": "Paddy (Rice)",
        "name_kn": "ಭತ್ತ",
        "scientific_name": "Oryza sativa",
        "soil": "Clayey loam, alluvial, and heavy black clay soils with high water-retention capacity.",
        "soil_kn": "ಗೋಡು ಮಣ್ಣು, ಜೇಡಿ ಮಿಶ್ರಿತ ಕಪ್ಪು ಮಣ್ಣು ಹಾಗೂ ಕರಾವಳಿಯ ಮೆಕ್ಕಲು ಮಣ್ಣು.",
        "climate": "Hot and humid climate; temperature 22°C - 35°C.",
        "sowing_season": "Kharif (June - July) and Rabi/Summer (November - December).",
        "varieties": ["JGL 1798", "BPT 5204 (Sona Masuri)", "IR-64", "Intan", "Gangavathi Sona", "Tellahamsa", "MO-4 (Bhadra)", "KPR-1"],
        "growth_stages": ["Seedling / Nursery (20-25 days)", "Tillering (30-50 days)", "Panicle Initiation (50-70 days)", "Flowering & Grain Filling (70-100 days)", "Maturity (110-135 days)"],
        "water_requirement": "1,200 - 1,500 mm; maintain 2-5 cm standing water during tillering.",
        "harvesting": "Harvest when 80-85% of grains in the panicle turn golden yellow.",
        "pests": "Stem borer, leaf folder, blast disease, brown planthopper (BPH)."
    },
    {
        "crop_id": "ragi",
        "name": "Finger Millet (Ragi)",
        "name_kn": "ರಾಗಿ",
        "scientific_name": "Eleusine coracana",
        "soil": "Red sandy loam, laterite, and moderately fertile well-drained soils of Southern Karnataka.",
        "soil_kn": "ಕೆಂಪು ಜೇಡಿ ಮಣ್ಣು ಮತ್ತು ಗೋಡು ಮಣ್ಣು (ದಕ್ಷಿಣ ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಆಹಾರ ಬೆಳೆ).",
        "climate": "Drought-tolerant crop, thrives at temperatures of 20°C - 32°C.",
        "sowing_season": "Kharif: Punarvasu/Pushya rains (July - August).",
        "varieties": ["ML-365", "GPU-28", "GPU-48", "Indaf-8", "KMR-301", "KMR-630", "MR-1"],
        "growth_stages": ["Germination & Tillering (15-35 days)", "Stem elongation (35-55 days)", "Earhead emergence (55-75 days)", "Grain hardening (75-105 days)", "Maturity (110-125 days)"],
        "water_requirement": "350 - 500 mm; highly resilient dryland crop.",
        "harvesting": "Harvest when earheads turn brown and grains harden; thresh after drying.",
        "pests": "Blast disease (leaf and neck blast), armyworm, shoot fly."
    },
    {
        "crop_id": "jowar",
        "name": "Sorghum (Jowar / Great Millet)",
        "name_kn": "ಜೋಳ",
        "scientific_name": "Sorghum bicolor",
        "soil": "Deep black cotton soils (Regur) and medium black soils with high moisture capacity.",
        "soil_kn": "ಆಳವಾದ ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು ಮತ್ತು ಎರೆ ಮಣ್ಣು (ಉತ್ತರ ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಬೆಳೆ).",
        "climate": "Warm and semi-arid climate, optimal temperature 26°C - 34°C.",
        "sowing_season": "Kharif (June - July) and Rabi (September - October).",
        "varieties": ["Maldandi (M 35-1)", "CSV 216R", "CSV 29R", "DSV 4", "BJV 44", "SPV 2217"],
        "growth_stages": ["Seedling (1-20 days)", "Vegetative & Booting (20-60 days)", "Flowering (60-75 days)", "Grain filling (75-95 days)", "Physiological maturity (105-120 days)"],
        "water_requirement": "400 - 550 mm; excellent drought recovery capability.",
        "harvesting": "Cut earheads when grains are hard and dry (below 14% moisture).",
        "pests": "Sorghum shoot fly, stem borer, grain mold, charcoal rot."
    },
    {
        "crop_id": "maize",
        "name": "Maize (Corn)",
        "name_kn": "ಮೆಕ್ಕೆಜೋಳ",
        "scientific_name": "Zea mays",
        "soil": "Well-drained fertile loams and red loams rich in organic matter; sensitive to waterlogging.",
        "soil_kn": "ಉತ್ತಮ ಬಸಿದು ಹೋಗುವ ಫಲವತ್ತಾದ ಕೆಂಪು ಗೋಡು ಮಣ್ಣು.",
        "climate": "Warm weather crop, optimum temperature 21°C - 30°C.",
        "sowing_season": "Kharif (June-July) and Rabi (October-November).",
        "varieties": ["CP 818", "NK 6240", "DKC 9108", "Hema (NAH-1137)", "Nithyashree", "Pioneer 3396"],
        "growth_stages": ["Knee-high (25-35 days)", "Tasseling (50-60 days)", "Silking (60-70 days)", "Dough stage (75-90 days)", "Maturity (100-115 days)"],
        "water_requirement": "500 - 650 mm; critical stages are tasseling and silking.",
        "harvesting": "Harvest when outer cob husks turn dry paper-white and kernel moisture drops below 20%.",
        "pests": "Fall Armyworm (FAW - Spodoptera frugiperda), stem borer, turcicum leaf blight."
    },
    {
        "crop_id": "cotton",
        "name": "Cotton (Kapas)",
        "name_kn": "ಹತ್ತಿ",
        "scientific_name": "Gossypium hirsutum",
        "soil": "Deep black soils of Northern Karnataka (Belagavi, Dharwad, Haveri, Ballari, Raichur).",
        "soil_kn": "ಉತ್ತರ ಕರ್ನಾಟಕದ ಆಳವಾದ ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು.",
        "climate": "Warm and sunny climate with minimum 180-200 frost-free days.",
        "sowing_season": "Kharif (June - July).",
        "varieties": ["Bt Cotton hybrids (Bollgard II)", "DHH-11", "Sahana", "RAHS-14", "DCH-32"],
        "growth_stages": ["Square formation (35-50 days)", "Flowering (55-80 days)", "Boll development (80-125 days)", "Boll bursting & Picking (130-170 days)"],
        "water_requirement": "700 - 1,000 mm; well-distributed rainfall followed by bright sunshine.",
        "harvesting": "Hand-pick clean, fully opened fluffy white bolls in morning hours.",
        "pests": "Pink bollworm (PBW), American bollworm, whitefly, thrips, leaf blight."
    },
    {
        "crop_id": "groundnut",
        "name": "Groundnut (Peanut)",
        "name_kn": "ಕಡಲೆಕಾಯಿ (ಶೇಂಗಾ)",
        "scientific_name": "Arachis hypogaea",
        "soil": "Light sandy loam and red loose sandy soils ensuring easy peg penetration.",
        "soil_kn": "ಸಡಿಲವಾದ ಕೆಂಪು ಮರಳು ಮಣ್ಣು (ಕಾಯಿ ಕಟ್ಟಲು ಸುಲಭವಾಗುವ ಮಣ್ಣು).",
        "climate": "Warm semi-arid climate, temperature 24°C - 32°C.",
        "sowing_season": "Kharif (June-July) and Summer (January-February with irrigation).",
        "varieties": ["TMV-2", "JL-24", "GPBD-4", "KDG-128", "Kadiri Lepakshi (K-1812)"],
        "growth_stages": ["Pegging (30-45 days)", "Pod formation (45-75 days)", "Pod maturity (75-105 days)"],
        "water_requirement": "450 - 600 mm; critical stage is flowering and peg formation.",
        "harvesting": "Pull out plants when inner pod shell shows dark brown/black veins.",
        "pests": "Tikka leaf spot, collar rot, leaf miner."
    },
    {
        "crop_id": "tur",
        "name": "Pigeon Pea (Tur / Red Gram)",
        "name_kn": "ತೊಗರಿ",
        "scientific_name": "Cajanus cajan",
        "soil": "Deep black loams and fertile red soils of Kalaburagi / Bidar (Tur Bowl of Karnataka).",
        "soil_kn": "ಆಳವಾದ ಕಪ್ಪು ಮಣ್ಣು (ಕಲಬುರಗಿ ಮತ್ತು ಬೀದರ್ ಜಿಲ್ಲೆಯ ಪ್ರಸಿದ್ಧ ಬೆಳೆ).",
        "climate": "Warm weather, optimal temperature 25°C - 35°C during vegetative growth.",
        "sowing_season": "Kharif (June - July).",
        "varieties": ["GRG-811", "TS-3R", "BSMR-736", "Maruti (ICP-8863)"],
        "growth_stages": ["Branching (30-60 days)", "Podding (90-130 days)", "Pod filling & Maturity (140-180 days)"],
        "water_requirement": "500 - 650 mm; deep taproot extracts subsoil water.",
        "harvesting": "Harvest when 80% of pods turn dry brown; thresh using pulse thresher.",
        "pests": "Helicoverpa armigera (Pod borer), sterility mosaic disease."
    },
    {
        "crop_id": "sugarcane",
        "name": "Sugarcane",
        "name_kn": "ಕಬ್ಬು",
        "scientific_name": "Saccharum officinarum",
        "soil": "Deep fertile alluvial and well-drained loamy black soils of Krishna & Cauvery river basins.",
        "soil_kn": "ಕೃಷ್ಣಾ ಹಾಗೂ ಕಾವೇರಿ ಕಣಿವೆಯ ಫಲವತ್ತಾದ ಗೋಡು ಮಣ್ಣು.",
        "climate": "Tropical hot and sunny climate with high humidity.",
        "sowing_season": "Eksali (July-August) and Pre-seasonal (October-November).",
        "varieties": ["Co 86032", "CoM 0265", "Co 62175", "Co 09004"],
        "growth_stages": ["Germination (1-35 days)", "Tillering (35-100 days)", "Grand Growth (100-270 days)", "Ripening & Maturity (270-360 days)"],
        "water_requirement": "1,500 - 2,200 mm; drip irrigation saves 40% water.",
        "harvesting": "Cut close to ground level when brix reading reaches 18-20%.",
        "pests": "Early shoot borer, top shoot borer, red rot disease."
    }
]

# Verified APMC Mandi Market Prices (Karnataka Mandis)
KARNATAKA_APMC_PRICES = [
    {"crop": "Paddy (Sona Masuri)", "crop_kn": "ಭತ್ತ (ಸೋನಾ ಮಸೂರಿ)", "market": "Raichur APMC", "district": "Raichur", "min_price": 2450.0, "max_price": 2850.0, "modal_price": 2680.0, "date": "2026-10-29", "is_historical": False},
    {"crop": "Ragi", "crop_kn": "ರಾಗಿ", "market": "Mysore APMC", "district": "Mysuru", "min_price": 3800.0, "max_price": 4250.0, "modal_price": 4050.0, "date": "2026-10-29", "is_historical": False},
    {"crop": "Jowar (Maldandi)", "crop_kn": "ಜೋಳ (ಮಾಲ್ದಂಡಿ)", "market": "Bijapur APMC", "district": "Vijayapura", "min_price": 3900.0, "max_price": 4500.0, "modal_price": 4200.0, "date": "2026-10-29", "is_historical": False},
    {"crop": "Tur (Red Gram)", "crop_kn": "ತೊಗರಿ", "market": "Gulbarga APMC", "district": "Kalaburagi", "min_price": 9400.0, "max_price": 10500.0, "modal_price": 10100.0, "date": "2026-10-29", "is_historical": False},
    {"crop": "Maize", "crop_kn": "ಮೆಕ್ಕೆಜೋಳ", "market": "Davanagere APMC", "district": "Davanagere", "min_price": 2100.0, "max_price": 2380.0, "modal_price": 2260.0, "date": "2026-10-29", "is_historical": False},
    {"crop": "Cotton", "crop_kn": "ಹತ್ತಿ", "market": "Hubli APMC", "district": "Dharwad", "min_price": 6800.0, "max_price": 7600.0, "modal_price": 7250.0, "date": "2026-10-29", "is_historical": False},
    {"crop": "Groundnut", "crop_kn": "ಕಡಲೆಕಾಯಿ", "market": "Challakere APMC", "district": "Chitradurga", "min_price": 5800.0, "max_price": 6600.0, "modal_price": 6300.0, "date": "2026-10-29", "is_historical": False},
    {"crop": "Sugarcane (FRP)", "crop_kn": "ಕಬ್ಬು (ಎಫ್‌ಆರ್‌ಪಿ ದರ)", "market": "Belgaum Mandi", "district": "Belagavi", "min_price": 315.0, "max_price": 340.0, "modal_price": 325.0, "unit": "₹ / Quintal", "date": "2026-10-29", "is_historical": False}
]

def seed_database_if_empty(db: Session):
    """
    Populates initial verified government schemes and demo records if table is empty or missing schemes.
    Preserves existing records while inserting newly cataloged schemes and updating metadata.
    """
    existing_schemes = {s.scheme_id: s for s in db.query(Scheme).all()}
    added_or_updated = False
    for s in INITIAL_SCHEMES:
        sid = s["scheme_id"]
        if sid not in existing_schemes:
            scheme_obj = Scheme(**s)
            db.add(scheme_obj)
            added_or_updated = True
        else:
            obj = existing_schemes[sid]
            for k, v in s.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
            added_or_updated = True
    if added_or_updated:
        db.commit()
