import os
import csv
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..config import DATA_DIR
from ..models import (
    Scheme,
    RegionalVocabulary,
    SpeechMetadata,
    FarmerSession,
    DatasetDictionary
)

logger = logging.getLogger(__name__)

# Known Kannada translations for standard government schemes
SCHEME_KANNADA_MAPPINGS = {
    "PM-KISAN": {
        "kn_name": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (ಪಿಎಂ-ಕಿಸಾನ್)",
        "kn_dept": "ಕೃಷಿ ಮತ್ತು ರೈತರ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯ, ಭಾರತ ಸರ್ಕಾರ",
        "kn_desc": "ಭಾರತದ ಎಲ್ಲಾ ಕೃಷಿ ಭೂಮಿ ಹೊಂದಿರುವ ಅರ್ಹ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವಾರ್ಷಿಕ ₹6,000 ಆರ್ಥಿಕ ನೆರವನ್ನು ₹2,000 ರ ಮೂರು ಕಂತುಗಳಲ್ಲಿ ನೇರವಾಗಿ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಜಮೆ ಮಾಡುವ ಪ್ರಮುಖ ಕೇಂದ್ರ ಪುರಸ್ಕೃತ ಯೋಜನೆ.",
        "kn_benefit": "ವರ್ಷಕ್ಕೆ ₹6,000 ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ತಲಾ ₹2,000 ರಂತೆ 3 ಕಂತುಗಳಲ್ಲಿ ನೇರ ನಗದು ವರ್ಗಾವಣೆ (DBT) ಮೂಲಕ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ನೀಡಲಾಗುತ್ತದೆ."
    },
    "Pradhan Mantri Fasal Bima Yojana (PMFBY)": {
        "kn_name": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (ಪಿಎಂಎಫ್‌ಬಿವೈ)",
        "kn_dept": "ಕೃಷಿ ಇಲಾಖೆ, ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಮತ್ತು ಕೇಂದ್ರ ಕೃಷಿ ಸಚಿವಾಲಯ",
        "kn_desc": "ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳು (ಬರ, ಪ್ರವಾಹ, ಕೀಟಬಾಧೆ, ಅಕಾಲಿಕ ಮಳೆ) ಉಂಟಾದಾಗ ಬೆಳೆ ನಷ್ಟ ಪರಿಹಾರ ಒದಗಿಸುವ ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ ಯೋಜನೆ.",
        "kn_benefit": "ಬೆಳೆ ಬಿತ್ತನೆ ವಿಫಲತೆ, ಬರಗಾಲ, ಅಕಾಲಿಕ ಮಳೆ ಹಾಗೂ ಕಟಾವಿನ ನಂತರದ ನಷ್ಟಕ್ಕೆ ಪೂರ್ಣ ಬೆಳೆ ವಿಮೆ ಪರಿಹಾರ ಧನ ದೊರೆಯುತ್ತದೆ."
    },
    "Demonstration Micro-Irrigation Support": {
        "kn_name": "[ಮಾದರಿ ಯೋಜನೆ] ಸೂಕ್ಷ್ಮ ನೀರಾವರಿ ಸಹಾಯಧನ",
        "kn_dept": "ಕೃಷಿ ಇಲಾಖೆ (ಪ್ರಾಯೋಗಿಕ / ಡೆಮೊ)",
        "kn_desc": "ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿ ಪದ್ಧತಿ ಅಳವಡಿಕೆಗೆ ಸಣ್ಣ ಮತ್ತು ಅತಿ ಸಣ್ಣ ರೈತರಿಗೆ ಒದಗಿಸುವ ಮಾದರಿ ಡೆಮೊ ಸಹಾಯಧನ.",
        "kn_benefit": "ಪ್ರಾಯೋಗಿಕ ಡೆಮೊ ಸಹಾಯಧನ ₹25,000 ವರೆಗೆ (ಪರೀಕ್ಷಾರ್ಥ ದಾಖಲೆ)."
    },
    "Demonstration Agricultural Equipment Assistance": {
        "kn_name": "[ಮಾದರಿ ಯೋಜನೆ] ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ನೆರವು",
        "kn_dept": "ಕೃಷಿ ಇಲಾಖೆ (ಪ್ರಾಯೋಗಿಕ / ಡೆಮೊ)",
        "kn_desc": "ಟ್ರ್ಯಾಕ್ಟರ್, ಟಿಲ್ಲರ್ ಮತ್ತು ಆಧುನಿಕ ಕೃಷಿ ಉಪಕರಣ ಖರೀದಿಗೆ ಸಣ್ಣ ಮತ್ತು ಮಹಿಳಾ ರೈತರಿಗೆ ನೀಡುವ ಮಾದರಿ ಸಹಾಯಧನ.",
        "kn_benefit": "ಪ್ರಾಯೋಗಿಕ ಯಂತ್ರೋಪಕರಣ ಸಬ್ಸಿಡಿ ₹40,000 ವರೆಗೆ (ಪರೀಕ್ಷಾರ್ಥ ದಾಖಲೆ)."
    },
    "Demonstration Soil Improvement Support": {
        "kn_name": "[ಮಾದರಿ ಯೋಜನೆ] ಮಣ್ಣು ಸುಧಾರಣೆ ಸಹಾಯಧನ",
        "kn_dept": "ಕೃಷಿ ಇಲಾಖೆ (ಪ್ರಾಯೋಗಿಕ / ಡೆಮೊ)",
        "kn_desc": "ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಸುಧಾರಣೆ ಮತ್ತು ಸಾವಯವ ಕೃಷಿ ಪ್ರೋತ್ಸಾಹಕ್ಕಾಗಿ ಪರೀಕ್ಷಾರ್ಥ ನೆರವು.",
        "kn_benefit": "ವಾರ್ಷಿಕ ₹5,000 ಮಣ್ಣು ಸಂರಕ್ಷಣಾ ಕೂಪನ್ (ಪರೀಕ್ಷಾರ್ಥ ದಾಖಲೆ)."
    }
}

class CSVIntegrationService:
    """
    Robust CSV ingestion engine for Krishi Mitra datasets.
    Handles data validation, type conversion, safe defaults,
    deduplication, and preserves existing database records.
    """

    @classmethod
    def load_government_schemes(cls, db: Session) -> Dict[str, int]:
        """Loads and integrates government_schemes.csv."""
        fpath = os.path.join(DATA_DIR, "government_schemes.csv")
        stats = {"inserted": 0, "updated": 0, "preserved": 0, "errors": 0}
        if not os.path.exists(fpath):
            logger.warning(f"File not found: {fpath}")
            return stats

        with open(fpath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    scheme_id = row.get("scheme_id", "").strip()
                    scheme_name = row.get("scheme_name", "").strip()
                    if not scheme_id or not scheme_name:
                        continue

                    # Safely parse numeric bounds
                    min_land = None
                    if row.get("min_land_area") and row["min_land_area"].strip():
                        try:
                            min_land = float(row["min_land_area"].strip())
                        except ValueError:
                            pass

                    max_land = None
                    if row.get("max_land_area") and row["max_land_area"].strip():
                        try:
                            max_land = float(row["max_land_area"].strip())
                        except ValueError:
                            pass

                    benefit_amt = None
                    if row.get("benefit_amount") and row["benefit_amount"].strip():
                        try:
                            benefit_amt = float(row["benefit_amount"].strip())
                        except ValueError:
                            pass

                    # Parse eligibility rules JSON if present
                    rule_json_str = row.get("eligibility_rule_json", "").strip()
                    rule_crops = ["All"]
                    rule_categories = ["All"]
                    if rule_json_str:
                        try:
                            rule_obj = json.loads(rule_json_str)
                            if "eligible_crops" in rule_obj and isinstance(rule_obj["eligible_crops"], list):
                                rule_crops = rule_obj["eligible_crops"]
                            if "eligible_farmer_categories" in rule_obj and isinstance(rule_obj["eligible_farmer_categories"], list):
                                rule_categories = rule_obj["eligible_farmer_categories"]
                            if "min_land_acres" in rule_obj and min_land is None:
                                min_land = float(rule_obj["min_land_acres"])
                            if "max_land_acres" in rule_obj and max_land is None:
                                max_land = float(rule_obj["max_land_acres"])
                        except Exception:
                            pass

                    # If crops not from JSON rule, parse semicolon string
                    if rule_crops == ["All"] and row.get("eligible_crops"):
                        c_raw = row["eligible_crops"].strip()
                        if c_raw and "not crop-specific" not in c_raw.lower() and c_raw.lower() != "all":
                            rule_crops = [c.strip() for c in c_raw.split(";") if c.strip()]

                    if rule_categories == ["All"] and row.get("farmer_category"):
                        cat_raw = row["farmer_category"].strip()
                        if cat_raw and cat_raw.lower() != "all":
                            rule_categories = [c.strip() for c in cat_raw.split(";") if c.strip()]

                    # Documents and steps lists
                    docs_list = []
                    if row.get("required_documents"):
                        docs_list = [d.strip() for d in row["required_documents"].split(";") if d.strip()]

                    steps_list = []
                    if row.get("application_steps"):
                        steps_list = [s.strip() for s in row["application_steps"].split(". ") if s.strip()]

                    # Distinguish synthetic demo from verified schemes
                    verif_status = row.get("verification_status", "Verified").strip()
                    rec_type = row.get("record_type", "real_scheme").strip()
                    is_demo = (verif_status == "Synthetic Demo") or (rec_type == "synthetic_demo") or ("demo" in scheme_id.lower())

                    if is_demo:
                        verif_status = "Synthetic Demo"
                        scheme_type = "Synthetic Demonstration"
                    else:
                        verif_status = "Verified"
                        scheme_type = row.get("scheme_level", "Central").strip()

                    # Translations
                    kn_map = SCHEME_KANNADA_MAPPINGS.get(scheme_name, {})
                    scheme_name_kn = kn_map.get("kn_name", scheme_name)
                    dept_kn = kn_map.get("kn_dept", row.get("department", "ಕೃಷಿ ಇಲಾಖೆ"))
                    desc_kn = kn_map.get("kn_desc", row.get("description", ""))
                    benefit_kn = kn_map.get("kn_benefit", f"{row.get('benefit_type', '')} {row.get('benefit_amount', '')} {row.get('benefit_frequency', '')}".strip())

                    # Check for existing record to avoid duplicate
                    # Matching by scheme_id, scheme_code, or exact scheme_name
                    existing = db.query(Scheme).filter(
                        (Scheme.scheme_id == scheme_id) |
                        (Scheme.scheme_code == scheme_id) |
                        (Scheme.scheme_name == scheme_name) |
                        (Scheme.scheme_id == "PM-KISAN" if scheme_id == "SCM001" else False) |
                        (Scheme.scheme_id == "PMFBY" if scheme_id == "SCM002" else False) |
                        (Scheme.scheme_id == "DEMO-IRRIG-01" if scheme_id == "DEMO001" else False) |
                        (Scheme.scheme_id == "DEMO-EQUIP-02" if scheme_id == "DEMO002" else False) |
                        (Scheme.scheme_id == "DEMO-SOIL-03" if scheme_id == "DEMO003" else False)
                    ).first()

                    if existing:
                        # Update with CSV metadata while preserving existing database primary key and active flags
                        existing.scheme_code = scheme_id
                        existing.eligibility_rule_json = rule_json_str or existing.eligibility_rule_json
                        existing.record_type = rec_type
                        existing.rag_document_id = row.get("rag_document_id") or existing.rag_document_id
                        existing.benefit_amount = benefit_amt or existing.benefit_amount
                        existing.benefit_frequency = row.get("benefit_frequency") or existing.benefit_frequency
                        existing.benefit_type = row.get("benefit_type") or existing.benefit_type
                        existing.exclusion_conditions = row.get("exclusion_conditions") or existing.exclusion_conditions
                        existing.source_document_title = row.get("source_document_title") or existing.source_document_title
                        existing.source_published_date = row.get("source_published_date") or existing.source_published_date
                        existing.source_last_verified = row.get("source_last_verified") or existing.source_last_verified
                        stats["updated"] += 1
                    else:
                        # Create new scheme record
                        new_scheme = Scheme(
                            scheme_id=scheme_id,
                            scheme_code=scheme_id,
                            scheme_name=scheme_name,
                            scheme_name_kn=scheme_name_kn,
                            scheme_type=scheme_type,
                            department=row.get("department", "Ministry of Agriculture"),
                            department_kn=dept_kn,
                            description=row.get("description", ""),
                            description_kn=desc_kn,
                            eligibility_conditions=rule_json_str or json.dumps({"description": row.get("description", "")}),
                            eligible_farmer_categories=json.dumps(rule_categories),
                            eligible_crops=json.dumps(rule_crops),
                            land_requirements=f"{min_land or 0.1} - {max_land or 'any'} acres ({row.get('land_ownership_rule', 'Any')})",
                            max_land_acres=max_land,
                            min_land_acres=min_land or 0.1,
                            required_ownership=row.get("land_ownership_rule", "Any"),
                            benefit_details=f"{row.get('benefit_type', '')} ₹{row.get('benefit_amount', '')} {row.get('benefit_frequency', '')}".strip(),
                            benefit_details_kn=benefit_kn,
                            required_documents=json.dumps(docs_list),
                            application_steps=json.dumps(steps_list),
                            official_url=row.get("official_url", "https://karnataka.gov.in"),
                            source_url=row.get("official_url", ""),
                            verification_date=row.get("source_last_verified", "2026-10-25"),
                            verification_status=verif_status,
                            active_status=True,
                            eligibility_rule_json=rule_json_str,
                            record_type=rec_type,
                            rag_document_id=row.get("rag_document_id"),
                            benefit_amount=benefit_amt,
                            benefit_frequency=row.get("benefit_frequency"),
                            benefit_type=row.get("benefit_type"),
                            exclusion_conditions=row.get("exclusion_conditions"),
                            source_document_title=row.get("source_document_title"),
                            source_published_date=row.get("source_published_date"),
                            source_last_verified=row.get("source_last_verified")
                        )
                        db.add(new_scheme)
                        stats["inserted"] += 1
                except Exception as e:
                    logger.error(f"Error parsing scheme row {row}: {e}")
                    stats["errors"] += 1

            db.commit()
        return stats

    @classmethod
    def load_regional_kannada_vocabulary(cls, db: Session) -> Dict[str, int]:
        """Loads and normalizes regional_kannada_vocabulary.csv."""
        fpath = os.path.join(DATA_DIR, "regional_kannada_vocabulary.csv")
        stats = {"inserted": 0, "skipped_empty": 0, "existing": 0, "errors": 0}
        if not os.path.exists(fpath):
            logger.warning(f"File not found: {fpath}")
            return stats

        with open(fpath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    term_id = row.get("term_id", "").strip()
                    local_term = row.get("local_term", "").strip()
                    standard_term = row.get("standard_kannada_term", "").strip()

                    # Safe handling for empty placeholder rows
                    if not term_id or not local_term or not standard_term:
                        stats["skipped_empty"] += 1
                        continue

                    existing = db.query(RegionalVocabulary).filter(RegionalVocabulary.term_id == term_id).first()
                    if existing:
                        # Update attributes if needed
                        existing.local_term = local_term
                        existing.standard_kannada_term = standard_term
                        existing.english_meaning = row.get("english_meaning")
                        existing.concept_id = row.get("concept_id")
                        existing.concept_category = row.get("concept_category")
                        existing.district_or_region = row.get("district_or_region")
                        existing.alternative_spellings = row.get("alternative_spellings")
                        existing.example_sentence = row.get("example_sentence")
                        existing.verified_by = row.get("verified_by")
                        existing.verification_status = row.get("verification_status", "verified")
                        existing.notes = row.get("notes")
                        stats["existing"] += 1
                    else:
                        vocab = RegionalVocabulary(
                            term_id=term_id,
                            local_term=local_term,
                            standard_kannada_term=standard_term,
                            english_meaning=row.get("english_meaning", ""),
                            concept_id=row.get("concept_id", ""),
                            concept_category=row.get("concept_category", ""),
                            district_or_region=row.get("district_or_region", "North Karnataka"),
                            alternative_spellings=row.get("alternative_spellings", ""),
                            example_sentence=row.get("example_sentence", ""),
                            verified_by=row.get("verified_by", "Regional Linguistic Panel"),
                            verification_status=row.get("verification_status", "verified"),
                            notes=row.get("notes", "")
                        )
                        db.add(vocab)
                        stats["inserted"] += 1
                except Exception as e:
                    logger.error(f"Error parsing vocabulary row {row}: {e}")
                    stats["errors"] += 1

            db.commit()
        return stats

    @classmethod
    def load_kannada_speech_metadata(cls, db: Session) -> Dict[str, int]:
        """Loads kannada_speech_metadata.csv index (audio metadata only)."""
        fpath = os.path.join(DATA_DIR, "kannada_speech_metadata.csv")
        stats = {"inserted": 0, "existing": 0, "errors": 0}
        if not os.path.exists(fpath):
            logger.warning(f"File not found: {fpath}")
            return stats

        with open(fpath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    audio_id = row.get("audio_id", "").strip()
                    audio_uri = row.get("audio_file_path_or_uri", "").strip()
                    verbatim = row.get("transcript_verbatim", "").strip()

                    if not audio_id or not verbatim:
                        continue

                    duration = None
                    if row.get("audio_duration_seconds"):
                        try:
                            duration = float(row["audio_duration_seconds"].strip())
                        except ValueError:
                            pass

                    existing = db.query(SpeechMetadata).filter(SpeechMetadata.audio_id == audio_id).first()
                    if existing:
                        stats["existing"] += 1
                    else:
                        meta = SpeechMetadata(
                            audio_id=audio_id,
                            audio_file_path_or_uri=audio_uri,
                            transcript_verbatim=verbatim,
                            transcript_standard_kannada=row.get("transcript_standard_kannada", ""),
                            english_translation=row.get("english_translation", ""),
                            district_or_region=row.get("district_or_region", ""),
                            taluk_optional=row.get("taluk_optional", ""),
                            speaker_pseudonymous_id=row.get("speaker_pseudonymous_id", ""),
                            speech_language=row.get("speech_language", "kn"),
                            code_mixed_languages=row.get("code_mixed_languages", "None"),
                            concept_labels=row.get("concept_labels", ""),
                            audio_duration_seconds=duration,
                            audio_quality=row.get("audio_quality", "high"),
                            consent_status=row.get("consent_status", "consented"),
                            consent_record_reference=row.get("consent_record_reference", ""),
                            reviewed_by=row.get("reviewed_by", ""),
                            review_status=row.get("review_status", "approved"),
                            dataset_split=row.get("dataset_split", "test"),
                            notes=row.get("notes", "")
                        )
                        db.add(meta)
                        stats["inserted"] += 1
                except Exception as e:
                    logger.error(f"Error parsing speech metadata row {row}: {e}")
                    stats["errors"] += 1

            db.commit()
        return stats

    @classmethod
    def load_farmer_session_profiles(cls, db: Session) -> Dict[str, int]:
        """Loads and syncs farmer_session_profile.csv records."""
        fpath = os.path.join(DATA_DIR, "farmer_session_profile.csv")
        stats = {"inserted": 0, "existing": 0, "errors": 0}
        if not os.path.exists(fpath):
            logger.warning(f"File not found: {fpath}")
            return stats

        with open(fpath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    session_id = row.get("farmer_session_id", "").strip()
                    district = row.get("district", "").strip()
                    if not session_id or not district:
                        continue

                    land_area = None
                    if row.get("land_area") and row["land_area"].strip():
                        try:
                            land_area = float(row["land_area"].strip())
                        except ValueError:
                            pass

                    existing = db.query(FarmerSession).filter(FarmerSession.farmer_session_id == session_id).first()
                    if existing:
                        stats["existing"] += 1
                    else:
                        sess = FarmerSession(
                            farmer_session_id=session_id,
                            user_id_pseudonymous=row.get("user_id_pseudonymous", ""),
                            district=district,
                            taluk=row.get("taluk", ""),
                            village_optional=row.get("village_optional", ""),
                            regional_language_preference=row.get("regional_language_preference", ""),
                            preferred_language=row.get("preferred_language", "kn"),
                            speech_style_mode=row.get("speech_style_mode", "district_auto"),
                            crops_grown=row.get("crops_grown", ""),
                            land_area=land_area,
                            land_area_unit=row.get("land_area_unit", "acre"),
                            land_ownership=row.get("land_ownership", ""),
                            agricultural_season=row.get("agricultural_season", ""),
                            irrigation_type=row.get("irrigation_type", ""),
                            assistance_required=row.get("assistance_required", ""),
                            farmer_category_optional=row.get("farmer_category_optional", ""),
                            soil_type_optional=row.get("soil_type_optional", ""),
                            confirmed_fields=row.get("confirmed_fields", ""),
                            missing_fields=row.get("missing_fields", ""),
                            conversation_state=row.get("conversation_state", "collecting_information"),
                            consent_for_audio_storage=row.get("consent_for_audio_storage", "not_collected"),
                            notes=row.get("notes", "")
                        )
                        db.add(sess)
                        stats["inserted"] += 1
                except Exception as e:
                    logger.error(f"Error parsing session row {row}: {e}")
                    stats["errors"] += 1

            db.commit()
        return stats

    @classmethod
    def load_dataset_data_dictionary(cls, db: Session) -> Dict[str, int]:
        """Loads dataset_data_dictionary.csv for documentation catalog."""
        fpath = os.path.join(DATA_DIR, "dataset_data_dictionary.csv")
        stats = {"inserted": 0, "existing": 0, "errors": 0}
        if not os.path.exists(fpath):
            logger.warning(f"File not found: {fpath}")
            return stats

        with open(fpath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    file_name = row.get("file_name", "").strip()
                    purpose = row.get("purpose", "").strip()
                    if not file_name or not purpose:
                        continue

                    existing = db.query(DatasetDictionary).filter(DatasetDictionary.file_name == file_name).first()
                    if existing:
                        existing.purpose = purpose
                        existing.key_fields = row.get("key_fields", "")
                        existing.important_note = row.get("important_note", "")
                        stats["existing"] += 1
                    else:
                        dict_entry = DatasetDictionary(
                            file_name=file_name,
                            purpose=purpose,
                            key_fields=row.get("key_fields", ""),
                            important_note=row.get("important_note", "")
                        )
                        db.add(dict_entry)
                        stats["inserted"] += 1
                except Exception as e:
                    logger.error(f"Error parsing data dictionary row {row}: {e}")
                    stats["errors"] += 1

            db.commit()
        return stats

    @classmethod
    def load_all_csv_datasets(cls, db: Session) -> Dict[str, Any]:
        """Runs full integration of all 5 CSV datasets."""
        results = {
            "government_schemes": cls.load_government_schemes(db),
            "regional_kannada_vocabulary": cls.load_regional_kannada_vocabulary(db),
            "kannada_speech_metadata": cls.load_kannada_speech_metadata(db),
            "farmer_session_profile": cls.load_farmer_session_profiles(db),
            "dataset_data_dictionary": cls.load_dataset_data_dictionary(db)
        }
        logger.info(f"CSV Integration completed: {results}")
        return results

