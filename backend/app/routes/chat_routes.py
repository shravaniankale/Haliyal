import json
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Conversation, ChatMessage, User, Scheme, FarmerProfile
from ..schemas import ChatRequest, ChatResponse
from ..services.agricultural_agent import AgriculturalConversationalAgent
from ..services.kannada_speech import KannadaSpeechService
from ..auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["AI Agricultural Chatbot"])

@router.post("", response_model=ChatResponse)
def handle_chat_message(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session_id = data.session_id or "default-session"
    user_id = current_user.id if current_user else data.user_id

    # Find or create conversation
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if not conv:
        conv = Conversation(session_id=session_id, user_id=user_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Load history
    history_records = db.query(ChatMessage).filter(ChatMessage.conversation_id == conv.id).order_by(ChatMessage.created_at.asc()).all()
    history = [{"sender": m.sender, "text": m.text, "intent": m.intent} for m in history_records[-10:]]

    # Load farmer profile
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
            "district": p.district,
            "taluk": p.taluk,
            "land_acres": p.land_acres,
            "land_ownership": p.land_ownership,
            "irrigation_type": p.irrigation_type,
            "farmer_category": p.farmer_category,
            "crops": crops_list,
            "regional_speech_preference": p.regional_speech_preference
        }

    # Fetch active schemes
    all_schemes = db.query(Scheme).filter(Scheme.active_status == True).all()

    # Generate response
    preferred_region = data.regional_preference or (farmer_profile_dict.get("regional_speech_preference") if farmer_profile_dict else "Standard Kannada")

    reply_en, reply_kn, recommended_schemes, entities = AgriculturalConversationalAgent.generate_response(
        user_message=data.message,
        conversation_history=history,
        farmer_profile=farmer_profile_dict,
        all_schemes=all_schemes,
        regional_style=preferred_region
    )

    # Synthesize Kannada audio
    audio_url, _ = KannadaSpeechService.synthesize_kannada_speech(reply_kn, regional_style=preferred_region)

    # Save user message
    user_msg_record = ChatMessage(
        conversation_id=conv.id,
        sender="farmer",
        text=data.message,
        text_kn=data.message,
        intent=entities.get("intent", "query"),
        detected_entities=json.dumps(entities)
    )
    db.add(user_msg_record)

    # Save assistant message
    bot_msg_record = ChatMessage(
        conversation_id=conv.id,
        sender="assistant",
        text=reply_en,
        text_kn=reply_kn,
        audio_url=audio_url,
        intent=entities.get("intent", "response"),
        detected_entities=json.dumps(entities)
    )
    db.add(bot_msg_record)
    db.commit()

    return ChatResponse(
        reply=reply_en,
        reply_kn=reply_kn,
        audio_url=audio_url,
        intent=entities.get("intent", "crop_advisory"),
        detected_entities=entities,
        recommended_schemes=recommended_schemes
    )

@router.get("/history")
def get_chat_history(session_id: str = Query("default-session"), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if not conv:
        return []

    messages = db.query(ChatMessage).filter(ChatMessage.conversation_id == conv.id).order_by(ChatMessage.created_at.asc()).all()
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "text": m.text,
            "text_kn": m.text_kn,
            "audio_url": m.audio_url,
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
