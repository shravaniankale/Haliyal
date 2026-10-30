import uuid
import json
import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Conversation, ChatMessage, User, Scheme, FarmerProfile, FarmerSession, AnalysisHistory
from ..schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessageItem,
    ConversationListItem,
    ConversationDetailResponse,
    NewConversationRequest,
    AnalysisHistoryItem
)
from ..services.agricultural_agent import AgriculturalConversationalAgent
from ..services.kannada_speech import KannadaSpeechService
from ..services.vocabulary_service import KannadaVocabularyService
from ..auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["AI Agricultural Chatbot"])


@router.post("", response_model=ChatResponse)
def handle_chat_message(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session_id = data.session_id or f"sess_{uuid.uuid4().hex[:12]}"
    user_id = current_user.id if current_user else data.user_id

    # 1. Find or create conversation
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if not conv:
        initial_title = data.message.strip()[:40] if data.message else "ಕೃಷಿ ಸಂವಾದ"
        conv = Conversation(
            session_id=session_id,
            user_id=user_id,
            title=initial_title,
            selected_language=data.language or "kn",
            selected_voice=data.voice_gender or "female"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    elif user_id and not conv.user_id:
        conv.user_id = user_id
        db.commit()

    # 2. Load conversation history
    history_records = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conv.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history = [{"sender": m.sender, "text": m.text, "intent": m.intent} for m in history_records[-10:]]

    # Load confirmed details from conversation
    confirmed_dict = {}
    if conv.confirmed_details:
        try:
            confirmed_dict = json.loads(conv.confirmed_details)
        except Exception:
            confirmed_dict = {}

    current_stage = conv.current_stage or "COLLECT_DISTRICT"

    # 3. Load farmer profile for personalized recommendations
    farmer_profile_dict = None
    if current_user and current_user.profile:
        p = current_user.profile
        crops_list = []
        try:
            crops_list = json.loads(p.crops_grown) if p.crops_grown else []
        except Exception:
            crops_list = []

        farmer_profile_dict = {
            "name": current_user.name,
            "username": getattr(current_user, "username", None) or current_user.name,
            "district": p.district,
            "taluk": p.taluk,
            "village": getattr(p, "village", None),
            "land_acres": p.land_acres,
            "land_ownership": p.land_ownership,
            "irrigation": p.irrigation_type,
            "farmer_category": p.farmer_category,
            "primary_crop": getattr(p, "primary_crop", None) or (crops_list[0] if crops_list else None),
            "crop": getattr(p, "primary_crop", None) or (crops_list[0] if crops_list else None),
            "crops": crops_list,
            "soil_type": getattr(p, "soil_type", None),
            "crop_stage": getattr(p, "crop_stage", None),
            "season": getattr(p, "agricultural_season", None),
            "regional_speech_preference": p.regional_speech_preference,
            "voice_gender_preference": getattr(p, "voice_gender_preference", "female"),
            "speech_speed": getattr(current_user, "speech_speed", 1.0)
        }

    # 4. Fetch active schemes
    all_schemes = db.query(Scheme).filter(Scheme.active_status == True).all()

    # 5. Determine regional preferences
    preferred_region = (
        data.regional_preference
        or (farmer_profile_dict.get("regional_speech_preference") if farmer_profile_dict else "Standard Kannada")
        or "Standard Kannada"
    )

    # 6. Generate AI response using State Machine
    (
        reply_en,
        reply_kn,
        next_stage,
        updated_details,
        recommended_schemes,
        rag_citations,
        rag_confidence,
        rag_mode,
        is_agri,
        topic
    ) = AgriculturalConversationalAgent.process_turn(
        user_message=data.message,
        current_stage=current_stage,
        confirmed_details=confirmed_dict,
        farmer_profile=farmer_profile_dict,
        all_schemes=all_schemes,
        regional_style=preferred_region
    )

    entities = updated_details

    # 7. Synthesize Neural Audio
    voice_gender = (
        getattr(data, "voice_gender", None)
        or (farmer_profile_dict.get("voice_gender_preference") if farmer_profile_dict else "female")
        or "female"
    )
    pref_lang = getattr(data, "language", "kn") or "kn"
    spoken_text = reply_kn if pref_lang == "kn" else reply_en

    # Speed resolution
    speed = getattr(data, "speech_speed", None) or (farmer_profile_dict.get("speech_speed") if farmer_profile_dict else 1.0) or 1.0

    # Auto voice response preference check
    auto_voice = True
    if data.auto_voice_response is not None:
        auto_voice = data.auto_voice_response
    elif current_user and getattr(current_user, "auto_voice_response", None) is not None:
        auto_voice = current_user.auto_voice_response

    audio_url = None
    if auto_voice:
        audio_url, _ = KannadaSpeechService.synthesize_kannada_speech(
            text=spoken_text,
            regional_style=preferred_region,
            voice_gender=voice_gender,
            language=pref_lang,
            speech_speed=speed
        )

    # 8. Save user message
    user_msg_record = ChatMessage(
        conversation_id=conv.id,
        sender="farmer",
        text=data.message,
        text_kn=data.message,
        transcript=getattr(data, "transcript", None) or data.message,
        topic=topic,
        intent=entities.get("intent", "query"),
        detected_entities=json.dumps(entities)
    )
    db.add(user_msg_record)

    # 9. Save assistant message
    bot_msg_record = ChatMessage(
        conversation_id=conv.id,
        sender="assistant",
        text=reply_en,
        text_kn=reply_kn,
        audio_url=audio_url,
        topic=topic,
        intent=entities.get("intent", "response"),
        detected_entities=json.dumps(entities)
    )
    db.add(bot_msg_record)

    # 10. Update Conversation title, stage, and metadata
    if conv.title == "ಕೃಷಿ ಸಂವಾದ" and data.message:
        conv.title = data.message.strip()[:35]
    conv.topic = topic
    conv.current_stage = next_stage
    conv.confirmed_details = json.dumps(updated_details)
    conv.selected_language = pref_lang
    conv.selected_voice = voice_gender
    conv.updated_at = datetime.datetime.utcnow()

    # Sync confirmed details to user's FarmerProfile
    if current_user and current_user.profile:
        prof = current_user.profile
        if updated_details.get("district"): prof.district = updated_details["district"]
        if updated_details.get("taluk"): prof.taluk = updated_details["taluk"]
        if updated_details.get("village") is not None: prof.village = updated_details["village"]
        if updated_details.get("land_acres") is not None: prof.land_acres = updated_details["land_acres"]
        if updated_details.get("land_ownership"): prof.land_ownership = updated_details["land_ownership"]
        if updated_details.get("farmer_category"): prof.farmer_category = updated_details["farmer_category"]
        if updated_details.get("primary_crop"):
            prof.primary_crop = updated_details["primary_crop"]
            if updated_details.get("crops"):
                prof.crops_grown = json.dumps(updated_details["crops"])
        if updated_details.get("irrigation"): prof.irrigation_type = updated_details["irrigation"]
        if updated_details.get("soil_type"): prof.soil_type = updated_details["soil_type"]
        if updated_details.get("crop_stage"): prof.crop_stage = updated_details["crop_stage"]
        if updated_details.get("season"): prof.agricultural_season = updated_details["season"]
        if next_stage in ["IDENTIFY_REQUIREMENT", "FOLLOW_UP"]:
            prof.confirmed_fields = "district, taluk, land_acres, land_ownership, farmer_category, primary_crop, irrigation_type, soil_type"

    # 11. Record AnalysisHistory if meaningful agricultural analysis occurred
    if is_agri and user_id and (recommended_schemes or updated_details.get("crop") or topic in ["Crop Insurance", "Fertilizer Guidance", "Government Schemes", "Crop Guidance", "Weather Information", "Agricultural Loans"]):
        try:
            analysis = AnalysisHistory(
                user_id=user_id,
                conversation_id=conv.id,
                topic=topic,
                crop_information=updated_details.get("crop") or updated_details.get("primary_crop"),
                season_information=updated_details.get("season"),
                weather_used=json.dumps({"district": updated_details.get("district", "Belagavi")}),
                recommendations=json.dumps(recommended_schemes if recommended_schemes else [{"summary_en": reply_en[:200], "summary_kn": reply_kn[:200]}]),
                eligibility_results=json.dumps({"evaluated_schemes": len(recommended_schemes)}),
                source_references=json.dumps([c.get("doc_title") for c in rag_citations if isinstance(c, dict) and "doc_title" in c] if rag_citations else ["Krishi Mitra Official Rules"])
            )
            db.add(analysis)
        except Exception as e:
            pass

    # 12. Sync with FarmerSession
    try:
        sess_profile = db.query(FarmerSession).filter(FarmerSession.farmer_session_id == session_id).first()
        req_fields = ["district", "crop", "land_acres", "land_ownership"]
        conv_state = "schemes_recommended" if len(recommended_schemes) > 0 else "collecting_information"

        if not sess_profile:
            confirmed = [k for k in req_fields if k in updated_details and updated_details[k] is not None]
            missing = [k for k in req_fields if k not in confirmed]
            sess_profile = FarmerSession(
                farmer_session_id=session_id,
                user_id_pseudonymous=f"USER_{user_id}" if user_id else None,
                district=updated_details.get("district", "Belagavi"),
                crops_grown=updated_details.get("crop", ""),
                land_area=updated_details.get("land_acres"),
                land_ownership=updated_details.get("land_ownership"),
                agricultural_season=updated_details.get("season"),
                irrigation_type=updated_details.get("irrigation"),
                confirmed_fields=", ".join(confirmed) if confirmed else "none",
                missing_fields=", ".join(missing) if missing else "none",
                conversation_state=conv_state,
                consent_for_audio_storage="consented" if audio_url else "not_collected"
            )
            db.add(sess_profile)
        else:
            if updated_details.get("district"):
                sess_profile.district = updated_details["district"]
            if updated_details.get("crop"):
                sess_profile.crops_grown = updated_details["crop"]
            if updated_details.get("land_acres") is not None:
                sess_profile.land_area = updated_details["land_acres"]
            if updated_details.get("land_ownership"):
                sess_profile.land_ownership = updated_details["land_ownership"]
            if updated_details.get("season"):
                sess_profile.agricultural_season = updated_details["season"]
            if updated_details.get("irrigation"):
                sess_profile.irrigation_type = updated_details["irrigation"]

            current_confirmed = []
            if sess_profile.district:
                current_confirmed.append("district")
            if sess_profile.crops_grown:
                current_confirmed.append("crop")
            if sess_profile.land_area is not None:
                current_confirmed.append("land_acres")
            if sess_profile.land_ownership:
                current_confirmed.append("land_ownership")
            current_missing = [k for k in req_fields if k not in current_confirmed]

            sess_profile.confirmed_fields = ", ".join(current_confirmed) if current_confirmed else "none"
            sess_profile.missing_fields = ", ".join(current_missing) if current_missing else "none"
            sess_profile.conversation_state = conv_state
    except Exception:
        pass

    db.commit()

    return ChatResponse(
        reply=reply_en,
        reply_kn=reply_kn,
        audio_url=audio_url,
        intent=updated_details.get("intent", "crop_advisory"),
        topic=topic,
        detected_entities=updated_details,
        recommended_schemes=recommended_schemes,
        rag_citations=rag_citations,
        rag_confidence=rag_confidence,
        rag_mode=rag_mode,
        is_agriculture_related=is_agri,
        session_details=updated_details,
        current_stage=next_stage,
        confirmed_details=updated_details
    )


# --- CONVERSATION HISTORY MANAGEMENT ENDPOINTS ---

@router.get("/conversations", response_model=List[ConversationListItem])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """List all previous conversations for the authenticated farmer."""
    if not current_user:
        return []

    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id, Conversation.is_active == True)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    results = []
    for c in convs:
        msg_count = db.query(ChatMessage).filter(ChatMessage.conversation_id == c.id).count()
        last_msg = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == c.id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        last_text = last_msg.text_kn or last_msg.text if last_msg else None

        results.append(
            ConversationListItem(
                id=c.id,
                session_id=c.session_id,
                title=c.title or "ಕೃಷಿ ಸಂವಾದ",
                topic=c.topic or "General Agriculture",
                selected_language=c.selected_language or "kn",
                selected_voice=c.selected_voice or "female",
                message_count=msg_count,
                last_message=last_text[:60] if last_text else None,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
        )
    return results


@router.get("/conversations/{conv_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    conv_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Retrieve full messages and details of a specific conversation thread."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user and conv.user_id and conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conv.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    confirmed_dict = {}
    try:
        confirmed_dict = json.loads(conv.confirmed_details) if conv.confirmed_details else {}
    except Exception:
        pass

    missing_list = []
    try:
        missing_list = json.loads(conv.missing_details) if conv.missing_details else []
    except Exception:
        pass

    msg_items = [
        ChatMessageItem(
            id=m.id,
            conversation_id=m.conversation_id,
            sender=m.sender,
            text=m.text,
            text_kn=m.text_kn,
            audio_url=m.audio_url,
            transcript=m.transcript,
            topic=m.topic,
            intent=m.intent,
            created_at=m.created_at
        )
        for m in messages
    ]

    return ConversationDetailResponse(
        id=conv.id,
        session_id=conv.session_id,
        title=conv.title or "ಕೃಷಿ ಸಂವಾದ",
        topic=conv.topic or "General Agriculture",
        selected_language=conv.selected_language or "kn",
        selected_voice=conv.selected_voice or "female",
        current_stage=conv.current_stage or "idle",
        confirmed_details=confirmed_dict,
        missing_details=missing_list,
        messages=msg_items,
        created_at=conv.created_at,
        updated_at=conv.updated_at
    )


@router.post("/conversations/new", response_model=ConversationDetailResponse)
def start_new_conversation(
    req: NewConversationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Starts a fresh conversation thread with a personalized greeting addressing
    the user's actual username or name without interrogating the farmer immediately.
    """
    new_session_id = f"sess_{uuid.uuid4().hex[:12]}"
    user_id = current_user.id if current_user else None

    # Resolve greeting name
    farmer_name = "ರೈತ ಮಿತ್ರ"
    farmer_name_en = "Farmer"
    if current_user:
        name_val = getattr(current_user, "username", None) or current_user.name
        if name_val and name_val.strip():
            farmer_name = name_val.strip()
            farmer_name_en = name_val.strip()

    title = req.title or "ಹೊಸ ಕೃಷಿ ಸಂವಾದ"
    lang = req.language or "kn"
    voice_gender = req.voice_gender or "female"

    conv = Conversation(
        session_id=new_session_id,
        user_id=user_id,
        title=title,
        topic=req.topic or "General Agriculture",
        selected_language=lang,
        selected_voice=voice_gender,
        current_stage="idle"
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    # Determine regional preference
    reg_style = "Standard Kannada"
    if current_user and current_user.profile and current_user.profile.regional_speech_preference:
        reg_style = current_user.profile.regional_speech_preference

    # Retrieve saved profile and check if already confirmed
    saved_details = {}
    is_profile_confirmed = False
    if current_user and current_user.profile:
        p = current_user.profile
        crops_list = []
        try:
            crops_list = json.loads(p.crops_grown) if p.crops_grown else []
        except Exception:
            crops_list = []
        if p.district and p.district.strip(): saved_details["district"] = p.district.strip()
        if p.taluk and p.taluk.strip(): saved_details["taluk"] = p.taluk.strip()
        if p.village: saved_details["village"] = p.village
        if p.land_acres is not None: saved_details["land_acres"] = p.land_acres
        if p.land_ownership: saved_details["land_ownership"] = p.land_ownership
        if p.farmer_category: saved_details["farmer_category"] = p.farmer_category
        p_crop = getattr(p, "primary_crop", None) or (crops_list[0] if crops_list else None)
        if p_crop:
            saved_details["primary_crop"] = p_crop
            saved_details["crop"] = p_crop
        if p.irrigation_type: saved_details["irrigation"] = p.irrigation_type
        if p.soil_type: saved_details["soil_type"] = p.soil_type
        if getattr(p, "crop_stage", None): saved_details["crop_stage"] = p.crop_stage
        if getattr(p, "agricultural_season", None): saved_details["season"] = p.agricultural_season

        # Check if already confirmed
        if p.confirmed_fields and "district" in p.confirmed_fields and "crop" in p.confirmed_fields:
            is_profile_confirmed = True

    if is_profile_confirmed:
        current_stage = "IDENTIFY_REQUIREMENT"
        greeting_kn = (
            f"ನಮಸ್ಕಾರ {farmer_name} ಅವರೇ! ಕೃಷಿ ಮಿತ್ರಕ್ಕೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಉಳಿಸಿದ ಕೃಷಿ ಪ್ರೊಫೈಲ್ ({saved_details.get('district')} ಜಿಲ್ಲೆ, {saved_details.get('land_acres')} ಎಕರೆ, {saved_details.get('crop')} ಬೆಳೆ) ಪರಿಶೀಲಿಸಲಾಗಿದೆ.\n\n"
            f"ಈಗ ನಿಮಗೆ ಯಾವ ಕೃಷಿ ವಿಷಯದಲ್ಲಿ ಸಹಾಯ ಬೇಕು?\n\n"
            f"೧. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು (Government Schemes)\n"
            f"೨. ಬೆಳೆ ವಿಮೆ (Crop Insurance)\n"
            f"೩. ಗೊಬ್ಬರದ ಸಲಹೆ (Fertilizer Recommendations)\n"
            f"೪. ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ (Crop Guidance)\n"
            f"೫. ನೀರಾವರಿ ಸಲಹೆ (Irrigation Guidance)\n"
            f"೬. ಹವಾಮಾನ ಮಾಹಿತಿ (Weather Information)\n"
            f"೭. ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ (Pest & Disease Management)\n"
            f"೮. ಕೃಷಿ ಸಾಲಗಳು (Agricultural Loans)\n"
            f"೯. ಮಾರುಕಟ್ಟೆ ದರ (Market Prices)\n"
            f"೧೦. ಸಮಗ್ರ ಕೃಷಿ ನೆರವು (Complete Assistance)\n\n"
            f"ನೀವು ನೇರವಾಗಿ ಮಾತನಾಡಿ ಆಯ್ಕೆ ಮಾಡಬಹುದು."
        )
        greeting_en = (
            f"Hello {farmer_name_en}! Welcome to Krishi Mitra. Your verified farm profile ({saved_details.get('district')}, {saved_details.get('land_acres')} acres, {saved_details.get('crop')}) is loaded.\n\n"
            f"What agricultural assistance do you need today?\n"
            f"1. Government schemes\n2. Crop insurance\n3. Fertilizer recommendations\n4. Crop guidance\n5. Irrigation guidance\n6. Weather information\n7. Pest & disease management\n8. Agricultural loans\n9. Market prices\n10. Complete agricultural assistance\n\nYou can speak naturally or choose an option."
        )
    else:
        # Strip unconfirmed defaults so the state machine asks each question sequentially
        confirmed_set = set([f.strip() for f in p.confirmed_fields.split(",")]) if (current_user and current_user.profile and current_user.profile.confirmed_fields) else set()
        for k in ["land_ownership", "farmer_category", "primary_crop", "crop", "irrigation", "soil_type", "crop_stage", "season"]:
            if k not in confirmed_set:
                saved_details.pop(k, None)

        missing_stage = AgriculturalConversationalAgent.get_first_missing_stage(saved_details)
        current_stage = missing_stage
        q_kn, q_en = AgriculturalConversationalAgent.get_question_for_stage(missing_stage, saved_details, reg_style)

        greeting_kn = (
            f"ನಮಸ್ಕಾರ {farmer_name} ಅವರೇ! ಕೃಷಿ ಮಿತ್ರಕ್ಕೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಮಾಹಿತಿಯನ್ನು ತಿಳಿದುಕೊಳ್ಳಲು ಕೆಲವು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೇನೆ. ಈ ಮಾಹಿತಿಯು ನಿಮಗೆ ಸೂಕ್ತವಾದ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಬೆಳೆ ವಿಮೆ ಮತ್ತು ಕೃಷಿ ಸಲಹೆಗಳನ್ನು ಶಿಫಾರಸು ಮಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.\n\n"
            f"{q_kn}"
        )
        greeting_en = (
            f"Hello {farmer_name_en}! Welcome to Krishi Mitra. I will ask a few questions to understand your agricultural information. These details will help provide suitable agricultural recommendations.\n\n"
            f"{q_en}"
        )

    greeting_kn = KannadaVocabularyService.adapt_to_dialect(greeting_kn, reg_style)

    conv.current_stage = current_stage
    conv.confirmed_details = json.dumps(saved_details)
    db.commit()

    # Speech synthesis for the opening greeting
    auto_voice = getattr(current_user, "auto_voice_response", True) if current_user else True
    speed = getattr(current_user, "speech_speed", 1.0) if current_user else 1.0
    spoken_text = greeting_kn if lang == "kn" else greeting_en
    audio_url = None
    if auto_voice:
        audio_url, _ = KannadaSpeechService.synthesize_kannada_speech(
            text=spoken_text,
            regional_style=reg_style,
            voice_gender=voice_gender,
            language=lang,
            speech_speed=speed
        )

    initial_msg = ChatMessage(
        conversation_id=conv.id,
        sender="assistant",
        text=greeting_en,
        text_kn=greeting_kn,
        audio_url=audio_url,
        topic="Greeting",
        intent="greeting"
    )
    db.add(initial_msg)
    db.commit()
    db.refresh(initial_msg)

    return ConversationDetailResponse(
        id=conv.id,
        session_id=conv.session_id,
        title=conv.title,
        topic=conv.topic,
        selected_language=conv.selected_language,
        selected_voice=conv.selected_voice,
        current_stage=conv.current_stage,
        confirmed_details=saved_details,
        missing_details=[],
        messages=[
            ChatMessageItem(
                id=initial_msg.id,
                conversation_id=initial_msg.conversation_id,
                sender=initial_msg.sender,
                text=initial_msg.text,
                text_kn=initial_msg.text_kn,
                audio_url=initial_msg.audio_url,
                transcript=None,
                topic=initial_msg.topic,
                intent=initial_msg.intent,
                created_at=initial_msg.created_at
            )
        ],
        created_at=conv.created_at,
        updated_at=conv.updated_at
    )


@router.delete("/conversations/{conv_id}")
def delete_conversation(
    conv_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Deletes a single conversation thread and its associated messages."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user and conv.user_id and conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Cascade deletes chat_messages and analysis_history linked
    db.delete(conv)
    db.commit()
    return {"status": "deleted", "id": conv_id}


@router.delete("/conversations")
def delete_all_conversations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Deletes all conversation history for the current farmer with confirmation."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_convs = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    count = len(user_convs)
    for c in user_convs:
        db.delete(c)
    db.commit()
    return {"status": "all_deleted", "deleted_count": count}


@router.get("/analyses", response_model=List[AnalysisHistoryItem])
def get_user_analyses(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Retrieves saved analysis history (recommendations, eligibility, insurance) for the farmer."""
    if not current_user:
        return []

    records = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.user_id == current_user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .limit(20)
        .all()
    )

    return [
        AnalysisHistoryItem(
            id=r.id,
            conversation_id=r.conversation_id,
            topic=r.topic,
            crop_information=r.crop_information,
            season_information=r.season_information,
            weather_used=r.weather_used,
            recommendations=r.recommendations,
            eligibility_results=r.eligibility_results,
            source_references=r.source_references,
            created_at=r.created_at
        )
        for r in records
    ]


# --- LEGACY / BACKWARD COMPATIBLE HISTORY ENDPOINTS ---

@router.get("/history")
def get_chat_history(session_id: str = Query("default-session"), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if not conv:
        return []

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conv.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "text": m.text,
            "text_kn": m.text_kn,
            "audio_url": m.audio_url,
            "transcript": m.transcript,
            "topic": m.topic,
            "intent": m.intent,
            "created_at": m.created_at
        }
        for m in messages
    ]


@router.post("/clear")
def clear_chat_history(session_id: str = Query("default-session"), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if conv:
        db.query(ChatMessage).filter(ChatMessage.conversation_id == conv.id).delete()
        db.commit()
    return {"status": "cleared", "session_id": session_id}
