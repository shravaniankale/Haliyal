import json
from sqlalchemy.orm import Session
from .models import Scheme, User, FarmerProfile

# Verified & Demonstration Schemes Dataset
INITIAL_SCHEMES = [
    # REAL VERIFIED SCHEME 1
    {
        "scheme_id": "PM-KISAN",
        "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "scheme_name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (ಪಿಎಂ-ಕಿಸಾನ್)",
        "scheme_type": "Central Sector Scheme",
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
        "benefit_details": "₹6,000 per year transferred in three equal installments of ₹2,000 each via Direct Benefit Transfer (DBT).",
        "benefit_details_kn": "ವರ್ಷಕ್ಕೆ ₹6,000 ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ತಲಾ ₹2,000 ರಂತೆ 3 ಕಂತುಗಳಲ್ಲಿ ನೇರ ನಗದು ವರ್ಗಾವಣೆ (DBT) ಮೂಲಕ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ನೀಡಲಾಗುತ್ತದೆ.",
        "required_documents": json.dumps(["Aadhaar Card linked with Bank Account", "Land Ownership Record (RTC/Pahani)", "Bank Passbook with IFSC", "Active Mobile Number"]),
        "application_steps": json.dumps([
            "1. Visit the official PM-KISAN portal (pmkisan.gov.in) or nearest Karnataka Grama One / Raitha Samparka Kendra.",
            "2. Enter Aadhaar number and verify with OTP.",
            "3. Select State: Karnataka, District, Taluk, Village, and enter Land Survey Number / RTC details.",
            "4. Upload land records and submit for Village Nodal Officer / Taluk Tahsildar e-verification."
        ]),
        "official_url": "https://pmkisan.gov.in",
        "source_url": "https://pmkisan.gov.in/Documents/OperationalGuidelines.pdf",
        "verification_date": "2026-10-15",
        "verification_status": "Verified",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=800&q=80"
    },

    # REAL VERIFIED SCHEME 2
    {
        "scheme_id": "PMFBY",
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "scheme_name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (ಪಿಎಂಎಫ್‌ಬಿವೈ)",
        "scheme_type": "Centrally Sponsored Scheme",
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
        "benefit_details": "Comprehensive financial insurance compensation for localized calamities, prevented sowing, mid-season adversity, and post-harvest crop losses.",
        "benefit_details_kn": "ಬೆಳೆ ಬಿತ್ತನೆ ವಿಫಲತೆ, ಬರಗಾಲ, ಅಕಾಲಿಕ ಮಳೆ ಹಾಗೂ ಕಟಾವಿನ ನಂತರದ ನಷ್ಟಕ್ಕೆ ಪೂರ್ಣ ಬೆಳೆ ವಿಮೆ ಪರಿಹಾರ ಧನ ದೊರೆಯುತ್ತದೆ.",
        "required_documents": json.dumps(["Pahani (RTC) or Crop Sowing Certificate", "Aadhaar Card", "Bank Account Details", "Crop Declaration / Sowing Certificate"]),
        "application_steps": json.dumps([
            "1. Check notified crop for your hobli on Karnataka Samrakshane Portal (samrakshane.karnataka.gov.in).",
            "2. Pay minimal farmer premium (2% for Kharif) before seasonal cut-off date.",
            "3. Obtain insurance proposal receipt with acknowledgment number.",
            "4. In case of localized calamity, report within 72 hours via Crop Insurance App or helpline 1800-180-1551."
        ]),
        "official_url": "https://samrakshane.karnataka.gov.in",
        "source_url": "https://pmfby.gov.in",
        "verification_date": "2026-10-20",
        "verification_status": "Verified",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80"
    },

    # REAL VERIFIED SCHEME 3 (Karnataka Krishi Bhagya)
    {
        "scheme_id": "KRISHI-BHAGYA",
        "scheme_name": "Karnataka Krishi Bhagya Scheme",
        "scheme_name_kn": "ಕರ್ನಾಟಕ ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ",
        "scheme_type": "Karnataka State Government Scheme",
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
        "benefit_details": "80% to 90% direct subsidy for construction of farm pond (Krishi Honda), tarpaulin lining, diesel/solar pump, and micro-irrigation kit.",
        "benefit_details_kn": "ಕೃಷಿ ಹೊಂಡ ನಿರ್ಮಾಣ ಮತ್ತು ಲೈನಿಂಗ್ ವೆಚ್ಚಕ್ಕೆ ಶೇ. 80-90 ರಷ್ಟು ಸರ್ಕಾರಿ ಸಹಾಯಧನ.",
        "required_documents": json.dumps(["Current RTC (Pahani)", "Aadhaar Card", "Caste Certificate (if SC/ST)", "Bank Passbook Copy", "Passport size photograph"]),
        "application_steps": json.dumps([
            "1. Apply through Seva Sindhu or K-Kisan online portal or visit Assistant Director of Agriculture (ADA) office.",
            "2. Submit RTC showing rainfed category and land measurement sketch.",
            "3. Field inspection by agricultural officer for GPS tagging.",
            "4. Post-construction verification and DBT release into beneficiary account."
        ]),
        "official_url": "https://raitamitra.karnataka.gov.in",
        "source_url": "https://raitamitra.karnataka.gov.in/info-2/Krishi+Bhagya/en",
        "verification_date": "2026-10-18",
        "verification_status": "Verified",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&w=800&q=80"
    },

    # SYNTHETIC DEMONSTRATION RECORD 1
    {
        "scheme_id": "DEMO-IRRIG-01",
        "scheme_name": "[DEMO RECORD] Demo Micro-Irrigation Support",
        "scheme_name_kn": "[ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆ] ಡೆಮೊ ಹನಿ ನೀರಾವರಿ ಪ್ರೋತ್ಸಾಹ ಯೋಜನೆ",
        "scheme_type": "Synthetic Demonstration Record",
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
        "benefit_details": "Synthetic simulation benefit for sandbox testing only.",
        "benefit_details_kn": "ಕೇವಲ ಪರೀಕ್ಷಾರ್ಥ ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ಪ್ರಯೋಜನ.",
        "required_documents": json.dumps(["Demo Sample RTC", "Demo ID"]),
        "application_steps": json.dumps(["1. This is a synthetic sandbox test record; no application required."]),
        "official_url": "https://krishimitra.karnataka.gov.in/demo-terms",
        "source_url": "https://krishimitra.karnataka.gov.in/demo-dataset",
        "verification_date": "2026-10-01",
        "verification_status": "Synthetic Demo",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?auto=format&fit=crop&w=800&q=80"
    },

    # SYNTHETIC DEMONSTRATION RECORD 2
    {
        "scheme_id": "DEMO-EQUIP-02",
        "scheme_name": "[DEMO RECORD] Demo Agricultural Equipment Assistance",
        "scheme_name_kn": "[ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆ] ಡೆಮೊ ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ನೆರವು",
        "scheme_type": "Synthetic Demonstration Record",
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
        "benefit_details": "Simulated 50% power-tiller test subsidy for validation.",
        "benefit_details_kn": "ಪರೀಕ್ಷಾರ್ಥ ಡೆಮೊ ಸಹಾಯಧನ ವಿವರ.",
        "required_documents": json.dumps(["Demo Machinery Quotation", "Demo RTC"]),
        "application_steps": json.dumps(["1. Fictional record for automated test suite execution."]),
        "official_url": "https://krishimitra.karnataka.gov.in/demo-terms",
        "source_url": "https://krishimitra.karnataka.gov.in/demo-dataset",
        "verification_date": "2026-10-01",
        "verification_status": "Synthetic Demo",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1595838728639-4458f27fb636?auto=format&fit=crop&w=800&q=80"
    },

    # SYNTHETIC DEMONSTRATION RECORD 3
    {
        "scheme_id": "DEMO-SOIL-03",
        "scheme_name": "[DEMO RECORD] Demo Soil Improvement Support",
        "scheme_name_kn": "[ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆ] ಡೆಮೊ ಮಣ್ಣು ಸುಧಾರಣೆ ಸಹಾಯ ಯೋಜನೆ",
        "scheme_type": "Synthetic Demonstration Record",
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
        "benefit_details": "Synthetic micronutrient kit demonstration.",
        "benefit_details_kn": "ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ಮಣ್ಣು ಸುಧಾರಕ ಕಿಟ್.",
        "required_documents": json.dumps(["Demo Soil Health Card"]),
        "application_steps": json.dumps(["1. Test case scenario only."]),
        "official_url": "https://krishimitra.karnataka.gov.in/demo-terms",
        "source_url": "https://krishimitra.karnataka.gov.in/demo-dataset",
        "verification_date": "2026-10-01",
        "verification_status": "Synthetic Demo",
        "active_status": True,
        "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=800&q=80"
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
            "Borewell yield certificate / Water source proof",
            "RTC (Pahani)",
            "PM-KUSUM beneficiary registration ID from KREDL",
            "Aadhaar & Bank Details"
        ],
        "official_source": "Ministry of New and Renewable Energy (mnre.gov.in) & KREDL Karnataka"
    }
]

# Verified Karnataka Crops Database
KARNATAKA_CROPS = [
    {
        "crop_id": "paddy",
        "name": "Paddy (Rice)",
        "name_kn": "ಭತ್ತ",
        "scientific_name": "Oryza sativa",
        "soil": "Clayey loam, alluvial and deep fertile red loamy soils with high water retention capacity.",
        "soil_kn": "ಗೋಡು ಮಣ್ಣು, ಜೇಡಿ ಮಿಶ್ರಿತ ಕಪ್ಪು ಮಣ್ಣು ಹಾಗೂ ಕೆಂಪು ಗೋಡು ಮಣ್ಣು.",
        "climate": "Warm and humid climate, optimal temperature 22°C - 32°C with adequate rainfall or assured irrigation.",
        "sowing_season": "Kharif (June-July), Rabi/Summer (November-December in command areas).",
        "varieties": ["BPT 5204 (Sona Masuri)", "IR-64", "JGL 1798", "Gangavathi Sona", "RNR 15048 (Telangana Sona)"],
        "growth_stages": ["Nursery & Seedling (1-25 days)", "Tillering (25-50 days)", "Panicle Initiation & Flowering (50-80 days)", "Grain Filling & Maturity (80-120 days)"],
        "water_requirement": "1,200 - 1,400 mm throughout the cropping season; requires saturated field conditions during tillering.",
        "harvesting": "Harvest when 85-90% of panicles turn golden yellow and moisture content drops to 20-22%.",
        "pests": "Brown Plant Hopper (BPH), Stem Borer, Blast disease, Bacterial Leaf Blight."
    },
    {
        "crop_id": "ragi",
        "name": "Finger Millet (Ragi)",
        "name_kn": "ರಾಗಿ",
        "scientific_name": "Eleusine coracana",
        "soil": "Red loamy, sandy loam, and lateritic soils of South Karnataka. Tolerates low-fertility soils.",
        "soil_kn": "ಕೆಂಪು ಮರಳು ಗೋಡು ಮಣ್ಣು ಮತ್ತು ಜಂಬಿಟ್ಟಿಗೆ ಮಣ್ಣು. ದಕ್ಷಿಣ ಕರ್ನಾಟಕದ ಹವಾಗುಣಕ್ಕೆ ಅತ್ಯಂತ ಸೂಕ್ತ.",
        "climate": "Drought-resilient semi-arid climate, temperature 25°C - 34°C, rainfall 600 - 800 mm.",
        "sowing_season": "Kharif (July - August) with pre-monsoon showers.",
        "varieties": ["ML-365", "GPU-28", "GPU-48", "KMR-301", "Indaf-9"],
        "growth_stages": ["Germination & Seedling (1-20 days)", "Tillering & Vegetative (20-45 days)", "Heading & Flowering (45-70 days)", "Dough & Maturity (70-110 days)"],
        "water_requirement": "350 - 500 mm; highly resilient dryland crop, requires minimal supplemental irrigation.",
        "harvesting": "Cut earheads when grains become brown and hard; dry under sun for threshing.",
        "pests": "Ragi blast (Pyricularia grisea), stem borer, aphid infestations."
    },
    {
        "crop_id": "jowar",
        "name": "Sorghum (Jowar)",
        "name_kn": "ಜೋಳ",
        "scientific_name": "Sorghum bicolor",
        "soil": "Deep black soils (Regur) and medium deep clay loams of North Karnataka.",
        "soil_kn": "ಆಳವಾದ ಕಪ್ಪು ಮಣ್ಣು ಮತ್ತು ಮಧ್ಯಮ ಕಪ್ಪು ಮಣ್ಣು (ಉತ್ತರ ಕರ್ನಾಟಕದ ಬಯಲು ಸೀಮೆ).",
        "climate": "Warm and dry climate, temperature 26°C - 35°C, rainfall 450 - 650 mm.",
        "sowing_season": "Kharif (June - July) and Rabi (September - October in North Karnataka).",
        "varieties": ["M 35-1 (Maldandi)", "DSV-4", "CSH-14", "CSV-29R", "BJV-44"],
        "growth_stages": ["Emergence (1-10 days)", "Vegetative (10-40 days)", "Booting & Flowering (40-65 days)", "Grain Maturity (65-105 days)"],
        "water_requirement": "400 - 550 mm; excellent drought tolerance due to deep root system.",
        "harvesting": "Harvest when black layer develops at grain attachment point.",
        "pests": "Shoot fly (Atherigona soccata), stem borer, grain mold."
    },
    {
        "crop_id": "maize",
        "name": "Maize (Corn)",
        "name_kn": "ಮೆಕ್ಕೆಜೋಳ",
        "scientific_name": "Zea mays",
        "soil": "Well-drained deep loamy and red sandy loam soils with pH 6.0 to 7.5.",
        "soil_kn": "ಉತ್ತಮ ನೀರು ಬಸಿದು ಹೋಗುವ ಗೋಡು ಮಣ್ಣು ಮತ್ತು ಕೆಂಪು ಮರಳು ಗೋಡು ಮಣ್ಣು.",
        "climate": "Warm climate with abundant sunshine, 21°C - 30°C temperature.",
        "sowing_season": "Kharif (June - July) and Rabi (October - November).",
        "varieties": ["Deccan 103", "NAH-2049", "Pinnacle", "DKC 9108", "Bio 9681"],
        "growth_stages": ["Knee-high (15-30 days)", "Tasseling & Silking (45-60 days)", "Milking & Dough (60-85 days)", "Physiological Maturity (85-115 days)"],
        "water_requirement": "500 - 650 mm; critical water sensitive stages are tasseling and silking.",
        "harvesting": "Harvest when outer cob husks turn papery dry and brown.",
        "pests": "Fall Armyworm (Spodoptera frugiperda), stem borer."
    },
    {
        "crop_id": "cotton",
        "name": "Cotton",
        "name_kn": "ಹತ್ತಿ",
        "scientific_name": "Gossypium hirsutum",
        "soil": "Deep black cotton soils with excellent moisture storage in North Karnataka.",
        "soil_kn": "ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು (ಬೆಳಗಾವಿ, ಧಾರವಾಡ, ಬಳ್ಳಾರಿ, ಹಾವೇರಿ ಜಿಲ್ಲೆಗಳಲ್ಲಿ ವ್ಯಾಪಕ).",
        "climate": "Warm tropical climate, minimum 180 frost-free sunny days.",
        "sowing_season": "Kharif (May - June with early monsoon rains).",
        "varieties": ["Bt Cotton Hybrids (Bollgard II)", "DHH-11", "RCH-2"],
        "growth_stages": ["Squaring (35-50 days)", "Flowering & Boll formation (55-90 days)", "Boll bursting (100-150 days)"],
        "water_requirement": "700 - 900 mm; well distributed moisture essential during boll formation.",
        "harvesting": "Pick clean, fully opened bolls in dry sunny mornings without dry leaf trash.",
        "pests": "Pink Bollworm, whitefly, thrips, jassids."
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
    """Populates initial verified government schemes and demo records if table is empty."""
    count = db.query(Scheme).count()
    if count == 0:
        for s in INITIAL_SCHEMES:
            scheme_obj = Scheme(**s)
            db.add(scheme_obj)
        db.commit()
