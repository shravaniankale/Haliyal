import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Send,
  Volume2,
  VolumeX,
  Square,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  Loader2,
  UserCheck,
  Edit2,
  Trash2,
  MessageSquare,
  PlusCircle,
  History,
  X,
  Check,
  ShieldAlert,
  Sprout,
  Sliders,
  Power
} from 'lucide-react';
import { useSettings, RegionalDialect, VoiceGender } from '../context/SettingsContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { ChatMessage, ConversationItem, ConversationDetail } from '../types';

type ConversationState = 'idle' | 'listening' | 'processing' | 'speaking' | 'interrupted' | 'error';

export const VoiceAssistantPage: React.FC = () => {
  const {
    language,
    regionalDialect,
    setRegionalDialect,
    voiceGender,
    setVoiceGender,
    speechSpeed,
    autoVoiceResponse,
    setAutoVoiceResponse,
    voiceInputEnabled,
    voiceAssistantEnabled,
    setVoiceAssistantEnabled
  } = useSettings();
  const { user, profile } = useAuth();

  // Assistant states
  const [convState, setConvState] = useState<ConversationState>('idle');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [speechTranscriptPreview, setSpeechTranscriptPreview] = useState<string | null>(null);
  const [isEditingTranscript, setIsEditingTranscript] = useState(false);
  const [isMuted, setIsMuted] = useState(!autoVoiceResponse);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Active Session & Conversation ID
  const [sessionId, setSessionId] = useState<string>(() => 'sess_' + Math.random().toString(36).substring(2, 10));
  const [activeConvId, setActiveConvId] = useState<number | null>(null);
  const [activeTopic, setActiveTopic] = useState<string>('General Agriculture');

  // Conversation History Drawer
  const [isHistoryDrawerOpen, setIsHistoryDrawerOpen] = useState(false);
  const [conversationsList, setConversationsList] = useState<ConversationItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showDeleteAllModal, setShowDeleteAllModal] = useState(false);

  // Audio state management (strictly 1 active instance)
  const [playingMessageId, setPlayingMessageId] = useState<number | string | null>(null);
  const [isAudioPaused, setIsAudioPaused] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Speech Recognition
  const recognitionRef = useRef<any>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Conversational Workflow State Machine Stage & Confirmed Details
  const [currentStage, setCurrentStage] = useState<string>('STAGE_COLLECT_DISTRICT');
  const [confirmedDetails, setConfirmedDetails] = useState<Record<string, any>>({});

  // Dynamic Contextual Prompts by Stage
  const getContextualPrompts = () => {
    const key = currentStage.startsWith('STAGE_') ? currentStage : `STAGE_${currentStage}`;
    switch (key) {
      case 'STAGE_COLLECT_DISTRICT':
        return [
          { kn: 'ಬೆಳಗಾವಿ', en: 'Belagavi', category: 'ಜಿಲ್ಲೆ' },
          { kn: 'ಧಾರವಾಡ', en: 'Dharwad', category: 'ಜಿಲ್ಲೆ' },
          { kn: 'ಬಾಗಲಕೋಟೆ', en: 'Bagalkote', category: 'ಜಿಲ್ಲೆ' },
          { kn: 'ವಿಜಯಪುರ', en: 'Vijayapura', category: 'ಜಿಲ್ಲೆ' },
          { kn: 'ಉತ್ತರ ಕನ್ನಡ', en: 'Uttara Kannada', category: 'ಜಿಲ್ಲೆ' },
          { kn: 'ಬಳ್ಳಾರಿ', en: 'Ballari', category: 'ಜಿಲ್ಲೆ' },
          { kn: 'ಶಿವಮೊಗ್ಗ', en: 'Shivamogga', category: 'ಜಿಲ್ಲೆ' }
        ];
      case 'STAGE_COLLECT_TALUKA':
        return [
          { kn: 'ಬೈಲಹೊಂಗಲ', en: 'Bailhongal', category: 'ತಾಲೂಕು' },
          { kn: 'ಗೋಕಾಕ', en: 'Gokak', category: 'ತಾಲೂಕು' },
          { kn: 'ಚಿಕ್ಕೋಡಿ', en: 'Chikkodi', category: 'ತಾಲೂಕು' },
          { kn: 'ಹುಬ್ಬಳ್ಳಿ', en: 'Hubballi', category: 'ತಾಲೂಕು' },
          { kn: 'ಹಳಿಯಾಳ', en: 'Haliyal', category: 'ತಾಲೂಕು' },
          { kn: 'ಬೆಳಗಾವಿ', en: 'Belagavi', category: 'ತಾಲೂಕು' }
        ];
      case 'STAGE_COLLECT_VILLAGE':
        return [
          { kn: 'ಖಾನಾಪುರ', en: 'Khanapur', category: 'ಗ್ರಾಮ' },
          { kn: 'ಬೆಳಗುಂದಿ', en: 'Belagundi', category: 'ಗ್ರಾಮ' },
          { kn: 'ಗ್ರಾಮ ಇಲ್ಲ, ಮುಂದೆ ಸಾಗಿ', en: 'Skip village, continue', category: 'ಮುಂದುವರಿ' }
        ];
      case 'STAGE_COLLECT_LAND_SIZE':
        return [
          { kn: '೩ ಎಕರೆ', en: '3 acres', category: 'ವಿಸ್ತೀರ್ಣ' },
          { kn: '೨.೫ ಎಕರೆ', en: '2.5 acres', category: 'ವಿಸ್ತೀರ್ಣ' },
          { kn: '೫ ಎಕರೆ', en: '5 acres', category: 'ವಿಸ್ತೀರ್ಣ' },
          { kn: '೧೦ ಗುಂಟೆ', en: '10 guntas', category: 'ವಿಸ್ತೀರ್ಣ' },
          { kn: '೧ ಹೆಕ್ಟೇರ್', en: '1 hectare', category: 'ವಿಸ್ತೀರ್ಣ' }
        ];
      case 'STAGE_COLLECT_OWNERSHIP':
        return [
          { kn: 'ನನ್ನ ಸ್ವಂತ ಜಮೀನು', en: 'Own land', category: 'ಮಾಲೀಕತ್ವ' },
          { kn: 'ಗುತ್ತಿಗೆಗೆ ಪಡೆದ ಜಮೀನು', en: 'Leased / Tenant land', category: 'ಮಾಲೀಕತ್ವ' },
          { kn: 'ಪಾಲುದಾರಿಕೆ ಜಮೀನು', en: 'Shared land', category: 'ಮಾಲೀಕತ್ವ' }
        ];
      case 'STAGE_COLLECT_FARMER_CATEGORY':
        return [
          { kn: 'ಸಣ್ಣ ರೈತರು (Small Farmer)', en: 'Small farmer (2.5-5 acres)', category: 'ವರ್ಗ' },
          { kn: 'ಅತಿ ಸಣ್ಣ ರೈತರು (Marginal Farmer)', en: 'Marginal farmer (up to 2.5 acres)', category: 'ವರ್ಗ' },
          { kn: 'ಸಾಮಾನ್ಯ ವರ್ಗದ ರೈತರು', en: 'General category', category: 'ವರ್ಗ' },
          { kn: 'SC / ST ರೈತರು', en: 'SC / ST farmer', category: 'ವರ್ಗ' }
        ];
      case 'STAGE_COLLECT_CROPS':
        return [
          { kn: 'ಭತ್ತ', en: 'Paddy', category: 'ಬೆಳೆ' },
          { kn: 'ಶೇಂಗಾ', en: 'Groundnut', category: 'ಬೆಳೆ' },
          { kn: 'ಕಬ್ಬು', en: 'Sugarcane', category: 'ಬೆಳೆ' },
          { kn: 'ಮೆಕ್ಕೆಜೋಳ', en: 'Maize', category: 'ಬೆಳೆ' },
          { kn: 'ಹತ್ತಿ', en: 'Cotton', category: 'ಬೆಳೆ' },
          { kn: 'ಸೂರ್ಯಕಾಂತಿ', en: 'Sunflower', category: 'ಬೆಳೆ' }
        ];
      case 'STAGE_COLLECT_OTHER_CROPS':
        return [
          { kn: 'ಶೇಂಗಾ ಮತ್ತು ಉದ್ದು', en: 'Groundnut and Black gram', category: 'ಇತರ ಬೆಳೆ' },
          { kn: 'ಕಡಲೆ ಮತ್ತು ತೊಗರಿ', en: 'Gram and Red gram', category: 'ಇತರ ಬೆಳೆ' },
          { kn: 'ಇಲ್ಲ, ಬೇರೆ ಬೆಳೆಗಳಿಲ್ಲ', en: 'No other crops', category: 'ಮುಂದುವರಿ' }
        ];
      case 'STAGE_COLLECT_IRRIGATION':
        return [
          { kn: 'ಬೋರ್‌ವೆಲ್ ನೀರಾವರಿ', en: 'Borewell irrigation', category: 'ನೀರಾವರಿ' },
          { kn: 'ಕಾಲುವೆ ನೀರಾವರಿ', en: 'Canal irrigation', category: 'ನೀರಾವರಿ' },
          { kn: 'ಮಳೆ ಆಶ್ರಿತ ಜಮೀನು', en: 'Rainfed', category: 'ನೀರಾವರಿ' },
          { kn: 'ಹನಿ ನೀರಾವರಿ (Drip)', en: 'Drip irrigation', category: 'ನೀರಾವರಿ' },
          { kn: 'ತುಂತುರು ನೀರಾವರಿ (Sprinkler)', en: 'Sprinkler irrigation', category: 'ನೀರಾವರಿ' }
        ];
      case 'STAGE_COLLECT_SOIL':
        return [
          { kn: 'ಕಪ್ಪು ಮಣ್ಣು (ಏರಿ ಮಣ್ಣು)', en: 'Black soil', category: 'ಮಣ್ಣು' },
          { kn: 'ಕೆಂಪು ಮಣ್ಣು (ಮಸಾರಿ ಮಣ್ಣು)', en: 'Red soil', category: 'ಮಣ್ಣು' },
          { kn: 'ಮರಳು ಮಣ್ಣು', en: 'Sandy soil', category: 'ಮಣ್ಣು' },
          { kn: 'ಗೊತ್ತಿಲ್ಲ, ಮುಂದೆ ಸಾಗಿ', en: 'Not sure, skip soil', category: 'ಮುಂದುವರಿ' }
        ];
      case 'STAGE_COLLECT_SEASON_AND_CROP_STAGE':
        return [
          { kn: 'ಜೂನ್‌ನಲ್ಲಿ ಬಿತ್ತನೆ, ಬೆಳವಣಿಗೆ ಹಂತ', en: 'Sown in June, vegetative stage', category: 'ಹಂತ' },
          { kn: 'ಜುಲೈ ೧೫ ಬಿತ್ತನೆ, ಹೂವಾಡುವ ಹಂತ', en: 'July 15 sowing, flowering stage', category: 'ಹಂತ' },
          { kn: 'ಖಾರಿಫ್ ಹಂಗಾಮು, ಕಟಾವಿನ ಹಂತ', en: 'Kharif season, maturity/harvest', category: 'ಹಂಗಾಮು' }
        ];
      case 'STAGE_CONFIRM_PROFILE':
        return [
          { kn: 'ಹೌದು, ಎಲ್ಲ ವಿವರ ಸರಿಯಾಗಿದೆ', en: 'Yes, all details are correct', category: 'ದೃಢೀಕರಣ' },
          { kn: 'ಇಲ್ಲ, ವಿವರ ಬದಲಾಯಿಸಬೇಕು', en: 'No, change details', category: 'ತಿದ್ದುಪಡಿ' }
        ];
      case 'STAGE_COLLECT_CORRECTION':
        return [
          { kn: 'ನನ್ನ ಜಮೀನು ೫ ಎಕರೆ ಇದೆ', en: 'My land is 5 acres', category: 'ತಿದ್ದುಪಡಿ' },
          { kn: 'ನನ್ನ ಬೆಳೆ ಕಬ್ಬು', en: 'My crop is Sugarcane', category: 'ತಿದ್ದುಪಡಿ' },
          { kn: 'ಬೋರ್‌ವೆಲ್ ನೀರಾವರಿ ಇದೆ', en: 'I have borewell irrigation', category: 'ತಿದ್ದುಪಡಿ' }
        ];
      case 'STAGE_IDENTIFY_REQUIREMENT':
      case 'STAGE_FOLLOW_UP':
      default:
        return [
          { kn: 'ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗುತ್ತವೆ?', en: 'Which government schemes are available for me?', category: 'ಸರ್ಕಾರಿ ಯೋಜನೆ' },
          { kn: 'ಬೆಳೆ ವಿಮೆ (PMFBY) ನೋಂದಣಿ ಕೊನೆಯ ದಿನಾಂಕ ಯಾವಾಗ?', en: 'What is the deadline for PMFBY crop insurance?', category: 'ಬೆಳೆ ವಿಮೆ' },
          { kn: 'ಭತ್ತದ ಬೆಳೆಗೆ ಯೂರಿಯಾ ಮತ್ತು ಡಿಎಪಿ ಗೊಬ್ಬರ ಎಷ್ಟು ಹಾಕಬೇಕು?', en: 'What is the recommended fertilizer for paddy?', category: 'ಗೊಬ್ಬರದ ಸಲಹೆ' },
          { kn: 'ಭತ್ತ ಮತ್ತು ಶೇಂಗಾ ಬೆಳೆಗೆ ಸಮಗ್ರ ಮಾರ್ಗದರ್ಶನ ನೀಡಿ', en: 'Give comprehensive crop guidance for paddy and groundnut', category: 'ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ' },
          { kn: 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಸಾಲದ ನಿಯಮಗಳು ಮತ್ತು ಬಡ್ಡಿ ದರ ಎಷ್ಟು?', en: 'What are the rules and interest rate for KCC crop loan?', category: 'ಕೃಷಿ ಸಾಲ' },
          { kn: 'ಈ ವಾರ ಮಳೆಯ ಮುನ್ಸೂಚನೆ ಮತ್ತು ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆ ಸಮಯ ಹೇಗಿದೆ?', en: 'What is the rain forecast and spraying window this week?', category: 'ಹವಾಮಾನ' },
          { kn: 'ಬೆಳಗಾವಿ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಇಂದಿನ ಶೇಂಗಾ ದರ ಎಷ್ಟು?', en: 'What is the current mandi price for groundnut?', category: 'ಮಾರುಕಟ್ಟೆ ದರ' },
          { kn: 'ನನ್ನ ಜಮೀನಿಗೆ ಸಮಗ್ರ ಕೃಷಿ ನೆರವು ನೀಡಿ', en: 'Provide complete agricultural advisory', category: 'ಸಮಗ್ರ ನೆರವು' }
        ];
    }
  };

  const getStageBadgeLabel = (stage: string) => {
    const key = stage.startsWith('STAGE_') ? stage : `STAGE_${stage}`;
    const map: Record<string, { kn: string; en: string }> = {
      STAGE_COLLECT_DISTRICT: { kn: 'ಹಂತ ೧: ಜಿಲ್ಲೆ', en: 'Step 1: District' },
      STAGE_COLLECT_TALUKA: { kn: 'ಹಂತ ೨: ತಾಲೂಕು', en: 'Step 2: Taluka' },
      STAGE_COLLECT_VILLAGE: { kn: 'ಹಂತ ೩: ಗ್ರಾಮ', en: 'Step 3: Village' },
      STAGE_COLLECT_LAND_SIZE: { kn: 'ಹಂತ ೪: ಜಮೀನು ವಿಸ್ತೀರ್ಣ', en: 'Step 4: Land Size' },
      STAGE_COLLECT_OWNERSHIP: { kn: 'ಹಂತ ೫: ಮಾಲೀಕತ್ವ', en: 'Step 5: Ownership' },
      STAGE_COLLECT_FARMER_CATEGORY: { kn: 'ಹಂತ ೬: ರೈತ ವರ್ಗ', en: 'Step 6: Category' },
      STAGE_COLLECT_CROPS: { kn: 'ಹಂತ ೭: ಮುಖ್ಯ ಬೆಳೆ', en: 'Step 7: Primary Crop' },
      STAGE_COLLECT_OTHER_CROPS: { kn: 'ಹಂತ ೮: ಇತರ ಬೆಳೆಗಳು', en: 'Step 8: Other Crops' },
      STAGE_COLLECT_IRRIGATION: { kn: 'ಹಂತ ೯: ನೀರಾವರಿ', en: 'Step 9: Irrigation' },
      STAGE_COLLECT_SOIL: { kn: 'ಹಂತ ೧೦: ಮಣ್ಣಿನ ವಿಧ', en: 'Step 10: Soil' },
      STAGE_COLLECT_SEASON_AND_CROP_STAGE: { kn: 'ಹಂತ ೧೧: ಬಿತ್ತನೆ & ಹಂತ', en: 'Step 11: Sowing & Stage' },
      STAGE_CONFIRM_PROFILE: { kn: 'ಪ್ರೊಫೈಲ್ ದೃಢೀಕರಣ', en: 'Profile Confirmation' },
      STAGE_COLLECT_CORRECTION: { kn: 'ವಿವರ ತಿದ್ದುಪಡಿ', en: 'Profile Correction' },
      STAGE_IDENTIFY_REQUIREMENT: { kn: 'ಕೃಷಿ ಅಗತ್ಯತೆ ಆಯ್ಕೆ', en: 'Choose Topic' },
      STAGE_FOLLOW_UP: { kn: 'ಕೃಷಿ ಸಮಾಲೋಚನೆ', en: 'Advisory Active' }
    };
    return map[stage] || { kn: 'ಕೃಷಿ ಸಂವಾದ', en: 'Active' };
  };

  // Farmer greeting name resolution
  const farmerUsername = user?.username || user?.name || profile?.name || 'ರೈತ ಮಿತ್ರ';

  // 1. Initialize First Greeting & Natural Voice Conversation on Mount
  const hasInitializedRef = useRef(false);
  useEffect(() => {
    if (hasInitializedRef.current) return;
    hasInitializedRef.current = true;

    const initConversation = async () => {
      try {
        const newConv = await api.startNewConversation({
          language: language,
          voice_gender: voiceGender
        });
        setSessionId(newConv.session_id);
        setActiveConvId(newConv.id);
        setActiveTopic(newConv.topic || 'General Agriculture');
        if (newConv.current_stage) {
          setCurrentStage(newConv.current_stage);
        }
        setConfirmedDetails(newConv.confirmed_details || {});
        if (newConv.messages && newConv.messages.length > 0) {
          setMessages(newConv.messages);
          const firstMsg = newConv.messages[0];
          if (firstMsg.audio_url && autoVoiceResponse && !isMuted) {
            playAudio(firstMsg.audio_url, firstMsg.id || 1);
          }
        }
      } catch (err) {
        // Fallback local greeting matching exact prompt specification
        const greetingKn =
          regionalDialect === 'North Karnataka'
            ? `ನಮಸ್ಕಾರ್ರೀ ${farmerUsername} ಅವರೇ! ಕೃಷಿ ಮಿತ್ರಕ್ಕೆ ಸ್ವಾಗತ ನೋಡ್ರೀ. ನಿಮ್ಮ ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಮಾಹಿತಿಯನ್ನು ತಿಳಿದುಕೊಳ್ಳಲು ಕೆಲವು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೇನೆ.\n\nನೀವು ಯಾವ ಜಿಲ್ಲೆಯ ರೈತರು?`
            : `ನಮಸ್ಕಾರ ${farmerUsername} ಅವರೇ! ಕೃಷಿ ಮಿತ್ರಕ್ಕೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಮಾಹಿತಿಯನ್ನು ತಿಳಿದುಕೊಳ್ಳಲು ಕೆಲವು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೇನೆ.\n\nನೀವು ಯಾವ ಜಿಲ್ಲೆಯ ರೈತರು?`;

        const greetingEn = `Hello ${farmerUsername}! Welcome to Krishi Mitra. I will ask a few questions to understand your agricultural details.\n\nWhich district of Karnataka are you farming in?`;

        setMessages([
          {
            id: 1,
            sender: 'assistant',
            text: greetingEn,
            text_kn: greetingKn,
            topic: 'Farmer Information Collection',
            created_at: new Date().toISOString()
          }
        ]);
        setCurrentStage('STAGE_COLLECT_DISTRICT');
      }
    };

    initConversation();
  }, [farmerUsername, regionalDialect, voiceGender, language]);

  // 2. Initialize Web Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = language === 'en' ? 'en-IN' : 'kn-IN';

      recognition.onstart = () => {
        setConvState('listening');
        setErrorMessage(null);
        setInterimTranscript('');
      };

      recognition.onresult = (event: any) => {
        let interim = '';
        let final = '';

        for (let i = 0; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (interim) {
          setInterimTranscript(interim);
        }

        if (final && final.trim()) {
          setInterimTranscript('');
          // Set preview for farmer review before sending
          setSpeechTranscriptPreview(final.trim());
          setConvState('idle');
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech Recognition notice:', event.error);
        if (event.error === 'not-allowed') {
          setErrorMessage(language === 'kn' ? 'ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ.' : 'Microphone permission denied.');
        } else if (event.error !== 'no-speech') {
          setErrorMessage(
            language === 'kn'
              ? 'ಧ್ವನಿ ಗ್ರಹಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಮಾತನಾಡಿ ಅಥವಾ ಕೆಳಗೆ ಟೈಪ್ ಮಾಡಿ.'
              : 'Could not capture speech. Please try speaking again or type below.'
          );
        }
        setConvState('idle');
      };

      recognition.onend = () => {
        setConvState((prev) => (prev === 'listening' ? 'idle' : prev));
      };

      recognitionRef.current = recognition;
    }
  }, [language]);

  // 3. Scroll to bottom
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, convState]);

  // 4. Load Conversation History list on drawer open
  const loadConversations = async () => {
    setHistoryLoading(true);
    try {
      const convs = await api.getConversations();
      setConversationsList(convs);
    } catch (err) {
      console.warn('Error loading conversations', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (isHistoryDrawerOpen) {
      loadConversations();
    }
  }, [isHistoryDrawerOpen]);

  // 5. Clean up audio on unmount
  useEffect(() => {
    return () => {
      stopAudio();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
    };
  }, []);

  // Strict Single Audio Controller
  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setPlayingMessageId(null);
    setIsAudioPaused(false);
    if (convState === 'speaking') {
      setConvState('idle');
    }
  };

  const playAudio = (url: string, messageId: number | string) => {
    if (isMuted || !url) {
      stopAudio();
      return;
    }

    // Stop currently running audio instance
    stopAudio();

    try {
      const audio = new Audio(url);
      audio.playbackRate = speechSpeed || 1.0;
      audioRef.current = audio;
      setPlayingMessageId(messageId);
      setIsAudioPaused(false);
      setConvState('speaking');

      audio.onended = () => {
        stopAudio();
      };

      audio.onerror = () => {
        stopAudio();
      };

      audio.play().catch((err) => {
        console.warn('Audio play prevented:', err);
        stopAudio();
      });
    } catch (e) {
      stopAudio();
    }
  };

  const pauseResumeAudio = () => {
    if (!audioRef.current) return;

    if (isAudioPaused) {
      audioRef.current.play();
      setIsAudioPaused(false);
      setConvState('speaking');
    } else {
      audioRef.current.pause();
      setIsAudioPaused(true);
      setConvState('idle');
    }
  };

  // Toggle Mic
  const toggleListening = () => {
    if (!voiceInputEnabled) {
      setErrorMessage(
        language === 'kn'
          ? 'ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಅನ್ನು ಪ್ರೊಫೈಲ್ ಸೆಟ್ಟಿಂಗ್ಸ್‌ನಲ್ಲಿ ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ.'
          : 'Voice input is disabled in settings. Enable it from Profile Settings.'
      );
      return;
    }

    if (convState === 'speaking') {
      stopAudio();
      return;
    }

    if (convState === 'listening') {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      setConvState('idle');
      return;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.lang = language === 'en' ? 'en-IN' : 'kn-IN';
        recognitionRef.current.start();
        setConvState('listening');
      } catch (err) {
        console.warn('Recognition start error:', err);
        setConvState('idle');
      }
    } else {
      setErrorMessage(
        language === 'kn'
          ? 'ಬ್ರೌಸರ್‌ನಲ್ಲಿ Web Speech ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೆಳಗೆ ಟೈಪ್ ಮಾಡಿ.'
          : 'Web Speech API not supported in this browser. Please type below.'
      );
    }
  };

  // Send message to AI
  const handleSend = async (textToSend: string, transcriptText?: string) => {
    if (!textToSend.trim()) return;

    stopAudio();

    const userMsg: ChatMessage = {
      id: Date.now(),
      sender: 'farmer',
      text: textToSend,
      text_kn: textToSend,
      transcript: transcriptText || textToSend,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setInterimTranscript('');
    setSpeechTranscriptPreview(null);
    setIsEditingTranscript(false);
    setConvState('processing');
    setErrorMessage(null);

    try {
      const res = await api.sendChatMessage({
        message: textToSend,
        session_id: sessionId,
        language: language,
        regional_preference: regionalDialect,
        voice_gender: voiceGender,
        speech_speed: speechSpeed,
        auto_voice_response: autoVoiceResponse,
        transcript: transcriptText
      });

      if (res.topic) {
        setActiveTopic(res.topic);
      }
      if (res.current_stage) {
        setCurrentStage(res.current_stage);
      }

      const botMsgId = Date.now() + 1;
      const botMsg: ChatMessage = {
        id: botMsgId,
        sender: 'assistant',
        text: res.reply,
        text_kn: res.reply_kn,
        audio_url: res.audio_url,
        topic: res.topic,
        intent: res.intent,
        created_at: new Date().toISOString()
      };

      setMessages((prev) => [...prev, botMsg]);

      if (res.confirmed_details) {
        setConfirmedDetails((prev) => ({ ...prev, ...res.confirmed_details }));
      } else if (res.session_details) {
        setConfirmedDetails((prev) => ({ ...prev, ...res.session_details }));
      }

      if (res.audio_url && !isMuted && autoVoiceResponse) {
        playAudio(res.audio_url, botMsgId);
      } else {
        setConvState('idle');
      }
    } catch (err: any) {
      console.error(err);
      setErrorMessage(
        language === 'kn'
          ? 'AI ಸಂವಹನದಲ್ಲಿ ತೊಂದರೆ ಉಂಟಾಗಿದೆ. ದಯವಿಟ್ಟು ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.'
          : 'Error communicating with agricultural AI assistant.'
      );
      setConvState('error');
      setTimeout(() => setConvState('idle'), 2500);
    }
  };

  // Start New Conversation
  const handleStartNewConversation = async () => {
    stopAudio();
    try {
      const newConv = await api.startNewConversation({
        language: language,
        voice_gender: voiceGender
      });
      setSessionId(newConv.session_id);
      setActiveConvId(newConv.id);
      setActiveTopic(newConv.topic || 'General Agriculture');
      if (newConv.current_stage) {
        setCurrentStage(newConv.current_stage);
      }
      setConfirmedDetails(newConv.confirmed_details || {});
      setMessages(newConv.messages || []);
      setIsHistoryDrawerOpen(false);
      loadConversations();
      if (newConv.messages && newConv.messages.length > 0) {
        const firstMsg = newConv.messages[0];
        if (firstMsg.audio_url && autoVoiceResponse && !isMuted) {
          playAudio(firstMsg.audio_url, firstMsg.id || 1);
        }
      }
    } catch (err) {
      // Fallback local reset
      const newSess = 'sess_' + Math.random().toString(36).substring(2, 10);
      setSessionId(newSess);
      setActiveConvId(null);
      const greetingKn =
        regionalDialect === 'North Karnataka'
          ? `ನಮಸ್ಕಾರ್ರೀ ${farmerUsername} ಅವರೇ! ಕೃಷಿ ಮಿತ್ರಕ್ಕೆ ಸ್ವಾಗತ ನೋಡ್ರೀ. ನಿಮ್ಮ ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಮಾಹಿತಿಯನ್ನು ತಿಳಿದುಕೊಳ್ಳಲು ಕೆಲವು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೇನೆ.\n\nನೀವು ಯಾವ ಜಿಲ್ಲೆಯ ರೈತರು?`
          : `ನಮಸ್ಕಾರ ${farmerUsername} ಅವರೇ! ಕೃಷಿ ಮಿತ್ರಕ್ಕೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಮಾಹಿತಿಯನ್ನು ತಿಳಿದುಕೊಳ್ಳಲು ಕೆಲವು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೇನೆ.\n\nನೀವು ಯಾವ ಜಿಲ್ಲೆಯ ರೈತರು?`;
      const greetingEn = `Hello ${farmerUsername}! Welcome to Krishi Mitra. I will ask a few questions to understand your agricultural information.\n\nWhich district are you farming in?`;
      setMessages([
        {
          id: Date.now(),
          sender: 'assistant',
          text: greetingEn,
          text_kn: greetingKn,
          topic: 'Farmer Information Collection',
          created_at: new Date().toISOString()
        }
      ]);
      setCurrentStage('STAGE_COLLECT_DISTRICT');
      setIsHistoryDrawerOpen(false);
    }
  };

  // Switch to an existing conversation
  const handleSelectConversation = async (conv: ConversationItem) => {
    stopAudio();
    try {
      const detail = await api.getConversationDetail(conv.id);
      setSessionId(detail.session_id);
      setActiveConvId(detail.id);
      setActiveTopic(detail.topic);
      if (detail.current_stage) {
        setCurrentStage(detail.current_stage);
      }
      setConfirmedDetails(detail.confirmed_details || {});
      setMessages(detail.messages || []);
      setIsHistoryDrawerOpen(false);
    } catch (err) {
      console.error('Failed to load conversation detail', err);
    }
  };

  // Delete a single conversation
  const handleDeleteConversation = async (convId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(convId);
      setConversationsList((prev) => prev.filter((c) => c.id !== convId));
      if (activeConvId === convId) {
        handleStartNewConversation();
      }
    } catch (err) {
      console.error('Failed to delete conversation', err);
    }
  };

  // Delete all conversations
  const handleDeleteAllConversations = async () => {
    try {
      await api.deleteAllConversations();
      setConversationsList([]);
      setShowDeleteAllModal(false);
      handleStartNewConversation();
    } catch (err) {
      console.error('Failed to delete all conversations', err);
    }
  };

  // Confirmed details badges (reused from saved profile + current session)
  const effectiveDetails = {
    district: confirmedDetails.district || profile?.district,
    taluk: confirmedDetails.taluk || profile?.taluk,
    village: confirmedDetails.village || profile?.village,
    crop: confirmedDetails.crop || confirmedDetails.primary_crop || profile?.primary_crop || (profile?.crops_grown && profile.crops_grown[0]),
    other_crops: confirmedDetails.other_crops || confirmedDetails.crops || profile?.secondary_crops,
    land: confirmedDetails.land_acres || profile?.land_acres,
    ownership: confirmedDetails.land_ownership || profile?.land_ownership,
    category: confirmedDetails.farmer_category || profile?.farmer_category,
    irrigation: confirmedDetails.irrigation || profile?.irrigation_type,
    soil: confirmedDetails.soil_type || profile?.soil_type,
    stage: confirmedDetails.crop_stage || profile?.crop_stage
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Alert if Voice Assistant is Disabled in Settings */}
      {!voiceAssistantEnabled && (
        <div className="bg-amber-50 dark:bg-amber-950/50 border border-amber-300 dark:border-amber-800 p-4 rounded-2xl flex items-center justify-between gap-3 text-amber-900 dark:text-amber-200">
          <div className="flex items-center gap-2.5">
            <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
            <span className="text-xs sm:text-sm font-medium font-kannada">
              {language === 'kn'
                ? 'ಧ್ವನಿ AI ಸಹಾಯಕರನ್ನು ಪ್ರೊಫೈಲ್ ಸೆಟ್ಟಿಂಗ್ಸ್‌ನಲ್ಲಿ ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ.'
                : 'Voice Assistant is currently disabled in your settings.'}
            </span>
          </div>
          <button
            type="button"
            onClick={() => setVoiceAssistantEnabled(true)}
            className="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0"
          >
            <Power className="w-3.5 h-3.5" />
            <span>{language === 'kn' ? 'ಸಕ್ರಿಯಗೊಳಿಸಿ (Enable)' : 'Enable Voice'}</span>
          </button>
        </div>
      )}

      {/* Top Banner & Control Bar */}
      <div className="bg-white dark:bg-slate-900 p-5 sm:p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4 transition-colors">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-700 to-green-600 flex items-center justify-center text-white shadow-md">
            <Mic className="w-6 h-6 text-amber-300" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white font-kannada">
                {language === 'kn' ? 'ಕೃಷಿ ಮಿತ್ರ AI ಧ್ವನಿ ಸಂವಾದ' : 'Krishi Mitra AI Voice Assistant'}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 text-xs font-bold">
                {activeTopic}
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 text-xs font-bold font-kannada">
                {language === 'kn' ? getStageBadgeLabel(currentStage).kn : getStageBadgeLabel(currentStage).en}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
              {language === 'kn'
                ? `ಸ್ವಾಗತ ${farmerUsername} ಅವರೇ! ನೈಸರ್ಗಿಕ ಧ್ವನಿ ಸಂಭಾಷಣೆಯೊಂದಿಗೆ ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ.`
                : `Welcome ${farmerUsername}! Real-time spoken Kannada AI with genuine neural voices.`}
            </p>
          </div>
        </div>

        {/* Action Buttons: History Drawer, New Thread, Audio Toggle */}
        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
          {/* Conversation History Drawer Button */}
          <button
            onClick={() => setIsHistoryDrawerOpen(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold transition"
          >
            <History className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>{language === 'kn' ? 'ಸಂವಾದ ಇತಿಹಾಸ' : 'History'}</span>
          </button>

          {/* Start New Conversation Button */}
          <button
            onClick={handleStartNewConversation}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold transition shadow-sm"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{language === 'kn' ? 'ಹೊಸ ಸಂವಾದ' : 'New Chat'}</span>
          </button>

          {/* Mute / Unmute Button */}
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:text-emerald-600 bg-slate-50 dark:bg-slate-800 transition"
            title={isMuted ? 'Unmute Audio' : 'Mute Audio'}
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-rose-500" /> : <Volume2 className="w-4 h-4 text-emerald-600" />}
          </button>
        </div>
      </div>

      {/* Main Grid: Left Orb & Smart Context | Right Messages & Input */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT COLUMN: Orb & Intelligent Farmer Context (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Animated Spoken Orb Card */}
          <div className="bg-gradient-to-b from-white to-slate-50 dark:from-slate-900 dark:to-slate-950 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm text-center flex flex-col items-center justify-between min-h-[420px] transition-colors">
            <div className="space-y-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-amber-500">
                {language === 'kn' ? 'ನೈಸರ್ಗಿಕ ಧ್ವನಿ ಸಂವಾದ' : 'Natural Two-Way Speech'}
              </span>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white font-kannada">
                {convState === 'listening'
                  ? language === 'kn'
                    ? 'ಧ್ವನಿ ಗ್ರಹಿಸಲಾಗುತ್ತಿದೆ (Listening...)'
                    : 'Listening to your voice...'
                  : convState === 'speaking'
                  ? language === 'kn'
                    ? 'ಉತ್ತರಿಸುತ್ತಿದೆ (Speaking...)'
                    : 'Speaking in Neural Voice...'
                  : convState === 'processing'
                  ? language === 'kn'
                    ? 'ಮಾಹಿತಿ ವಿಶ್ಲೇಷಣೆ (Processing...)'
                    : 'Analyzing agricultural request...'
                  : language === 'kn'
                  ? 'ಮಾತನಾಡಲು ಮೈಕ್ ಒತ್ತಿರಿ (Tap to Speak)'
                  : 'Tap the Microphone to Speak'}
              </h2>
            </div>

            {/* Glowing Center Orb */}
            <div className="relative my-8">
              {convState === 'listening' && (
                <div className="absolute inset-0 -m-8 rounded-full bg-rose-500/25 animate-ping"></div>
              )}
              {convState === 'speaking' && (
                <div className="absolute inset-0 -m-6 rounded-full bg-amber-500/25 animate-pulse"></div>
              )}

              <button
                type="button"
                onClick={toggleListening}
                className={`w-36 h-36 rounded-full flex flex-col items-center justify-center transition-all duration-300 shadow-2xl relative z-10 ${
                  convState === 'listening'
                    ? 'bg-rose-600 text-white shadow-rose-500/50 scale-105'
                    : convState === 'speaking'
                    ? 'bg-gradient-to-tr from-emerald-700 via-green-600 to-amber-500 text-white shadow-amber-500/40'
                    : convState === 'processing'
                    ? 'bg-blue-600 text-white animate-pulse'
                    : 'bg-gradient-to-tr from-emerald-700 to-green-600 text-white hover:scale-105'
                }`}
              >
                {convState === 'listening' ? (
                  <>
                    <MicOff className="w-10 h-10 animate-pulse" />
                    <span className="text-[11px] font-bold mt-1 font-kannada">
                      {language === 'kn' ? 'ನಿಲ್ಲಿಸಿ' : 'Stop'}
                    </span>
                  </>
                ) : convState === 'speaking' ? (
                  <>
                    <Volume2 className="w-10 h-10 text-amber-200 animate-bounce" />
                    <span className="text-[11px] font-bold mt-1 font-kannada">
                      {language === 'kn' ? 'ನಿಲ್ಲಿಸಿ' : 'Pause'}
                    </span>
                  </>
                ) : (
                  <>
                    <Mic className="w-10 h-10 text-amber-300" />
                    <span className="text-xs font-bold mt-1 font-kannada">
                      {language === 'kn' ? 'ಮಾತನಾಡಿ' : 'Speak'}
                    </span>
                  </>
                )}
              </button>
            </div>

            {/* Speech Interim Feedback / Active Audio Controls */}
            <div className="space-y-3 w-full">
              {interimTranscript && (
                <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 text-xs font-kannada text-amber-900 dark:text-amber-200 animate-pulse text-left">
                  <span className="font-bold">
                    {language === 'kn' ? 'ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿರುವುದು: ' : 'Capturing speech: '}
                  </span>
                  "{interimTranscript}"
                </div>
              )}

              {/* Editable Speech Preview Box (Requirement: edit/correct speech before sending) */}
              {speechTranscriptPreview && (
                <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 text-left space-y-3 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5 font-kannada">
                      <Edit2 className="w-3.5 h-3.5" />
                      {language === 'kn' ? 'ಧ್ವನಿ ಪಠ್ಯ ಪೂರ್ವವೀಕ್ಷಣೆ (ಸರಿಪಡಿಸಿ / ಕಳುಹಿಸಿ)' : 'Speech Transcript Review'}
                    </span>
                    <button
                      onClick={() => setSpeechTranscriptPreview(null)}
                      className="text-slate-400 hover:text-slate-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <textarea
                    rows={2}
                    value={speechTranscriptPreview}
                    onChange={(e) => setSpeechTranscriptPreview(e.target.value)}
                    className="w-full p-2.5 bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-700 rounded-xl text-xs sm:text-sm text-slate-800 dark:text-slate-100 font-kannada focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />

                  <div className="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => setSpeechTranscriptPreview(null)}
                      className="px-3 py-1.5 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg"
                    >
                      {language === 'kn' ? 'ರದ್ದು' : 'Discard'}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSend(speechTranscriptPreview, speechTranscriptPreview)}
                      className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm"
                    >
                      <Send className="w-3 h-3" />
                      <span>{language === 'kn' ? 'ಕಳುಹಿಸಿ (Send)' : 'Send to AI'}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Stop / Interrupt audio button when assistant is speaking */}
              {convState === 'speaking' && (
                <button
                  type="button"
                  onClick={stopAudio}
                  className="w-full py-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-300 dark:border-rose-800 font-bold text-xs flex items-center justify-center gap-1.5 transition"
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                  <span>
                    {language === 'kn'
                      ? 'ಧ್ವನಿ ನಿಲ್ಲಿಸಿ (Stop Audio & Interrupt)'
                      : 'Stop Audio & Speak'}
                  </span>
                </button>
              )}

              {errorMessage && (
                <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-xs text-rose-700 dark:text-rose-300 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Speech style indicator */}
              <div className="p-3 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-xs text-emerald-800 dark:text-emerald-300 font-medium font-kannada text-left border border-emerald-200 dark:border-emerald-900">
                <span className="font-bold">
                  {language === 'kn' ? 'ಸಕ್ರಿಯ ಧ್ವನಿ ಶೈಲಿ: ' : 'Active Voice & Style: '}
                </span>
                {regionalDialect} ({voiceGender === 'male' ? 'Gagan/Prabhat' : 'Sapna/Neerja'} • {speechSpeed}x)
              </div>
            </div>
          </div>

          {/* Intelligent Agricultural Context (Non-Interrogative Badges) */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-3 transition-colors">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Sprout className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 font-kannada">
                  {language === 'kn' ? 'ದೃಢೀಕೃತ ಕೃಷಿ ಹಿನ್ನೆಲೆ (Confirmed Context)' : 'Active Farm Context'}
                </h3>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold">
                {language === 'kn' ? 'ಸ್ವಯಂ ಜೋಡಣೆ' : 'Auto Reused'}
              </span>
            </div>

            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              {language === 'kn'
                ? 'AI ಸಹಾಯಕ ನಿಮ್ಮ ಉಳಿಸಿದ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಸಂವಾದದ ವಿವರಗಳನ್ನು ಪುನರಾವರ್ತನೆಯಿಲ್ಲದೆ ಬಳಸುತ್ತದೆ.'
                : 'The AI reuses known profile details without repeatedly asking you questions.'}
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs font-kannada">
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{language === 'kn' ? 'ಜಿಲ್ಲೆ / ತಾಲೂಕು' : 'District/Taluk'}</span>
                  {effectiveDetails.district && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                </div>
                <div className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">
                  {effectiveDetails.district ? `${effectiveDetails.district}${effectiveDetails.taluk ? `, ${effectiveDetails.taluk}` : ''}` : (language === 'kn' ? 'ಬಾಕಿ ಇದೆ...' : 'Pending...')}
                </div>
              </div>

              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{language === 'kn' ? 'ಮುಖ್ಯ ಬೆಳೆ' : 'Primary Crop'}</span>
                  {effectiveDetails.crop && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                </div>
                <div className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">
                  {effectiveDetails.crop || (language === 'kn' ? 'ಬಾಕಿ ಇದೆ...' : 'Pending...')}
                </div>
              </div>

              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{language === 'kn' ? 'ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ' : 'Land Size'}</span>
                  {effectiveDetails.land && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                </div>
                <div className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">
                  {effectiveDetails.land ? `${effectiveDetails.land} ಎಕರೆ` : (language === 'kn' ? 'ಬಾಕಿ ಇದೆ...' : 'Pending...')}
                </div>
              </div>

              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{language === 'kn' ? 'ಮಾಲೀಕತ್ವ' : 'Ownership'}</span>
                  {effectiveDetails.ownership && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                </div>
                <div className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">
                  {effectiveDetails.ownership || (language === 'kn' ? 'ಸ್ವಂತ / ಗುತ್ತಿಗೆ' : 'Pending')}
                </div>
              </div>

              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{language === 'kn' ? 'ರೈತ ವರ್ಗ' : 'Category'}</span>
                  {effectiveDetails.category && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                </div>
                <div className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">
                  {effectiveDetails.category || (language === 'kn' ? 'ಸ್ವಯಂ ವರ್ಗೀಕರಣ' : 'Auto')}
                </div>
              </div>

              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{language === 'kn' ? 'ನೀರಾವರಿ & ಮಣ್ಣು' : 'Irrigation & Soil'}</span>
                  {(effectiveDetails.irrigation || effectiveDetails.soil) && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                </div>
                <div className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">
                  {effectiveDetails.irrigation || 'ಬೋರ್‌ವೆಲ್'}{effectiveDetails.soil ? ` • ${effectiveDetails.soil}` : ''}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Conversation Transcript & Unified Input (7 cols) */}
        <div className="lg:col-span-7 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col h-[700px] overflow-hidden transition-colors">
          {/* Header */}
          <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs font-bold text-slate-600 dark:text-slate-400">
            <span className="font-kannada uppercase tracking-wide">
              {language === 'kn' ? 'ಧ್ವನಿ ಸಂವಾದ ಇತಿಹಾಸ (Conversation Transcript)' : 'Conversation Transcript'}
            </span>
            <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800">
              {messages.length} {language === 'kn' ? 'ಸಂದೇಶಗಳು' : 'messages'}
            </span>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-slate-50 dark:bg-slate-950/60">
            {messages.map((msg, index) => {
              const isBot = msg.sender === 'assistant';
              const isCurrentlyPlaying = playingMessageId === (msg.id || index);

              return (
                <div key={msg.id || index} className={`flex ${isBot ? 'justify-start' : 'justify-end'}`}>
                  <div
                    className={`max-w-[85%] rounded-3xl p-4 text-xs sm:text-sm leading-relaxed shadow-sm transition ${
                      isBot
                        ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-800 rounded-tl-sm'
                        : 'bg-emerald-700 text-white rounded-tr-sm'
                    }`}
                  >
                    {/* Kannada primary text */}
                    {msg.text_kn && (
                      <p className="font-kannada font-medium text-sm leading-relaxed mb-1.5 whitespace-pre-line">
                        {msg.text_kn}
                      </p>
                    )}

                    {/* English subtitle */}
                    {msg.text && msg.text !== msg.text_kn && (
                      <p className="text-xs text-slate-500 dark:text-slate-400 pt-1.5 border-t border-slate-200 dark:border-slate-800 whitespace-pre-line">
                        {msg.text}
                      </p>
                    )}

                    {/* Bot Spoken Audio Controls (Play / Pause / Stop / Replay) */}
                    {isBot && msg.audio_url && (
                      <div className="mt-3 pt-2 border-t border-slate-200 dark:border-slate-800 flex items-center gap-3">
                        {isCurrentlyPlaying ? (
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={pauseResumeAudio}
                              className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-200 rounded-lg text-xs font-bold"
                            >
                              {isAudioPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
                              <span>{isAudioPaused ? (language === 'kn' ? 'ಮುಂದುವರಿಸಿ' : 'Resume') : (language === 'kn' ? 'ವಿರಾಮ' : 'Pause')}</span>
                            </button>

                            <button
                              type="button"
                              onClick={stopAudio}
                              className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300 rounded-lg text-xs font-bold"
                            >
                              <Square className="w-3 h-3 fill-current" />
                              <span>{language === 'kn' ? 'ನಿಲ್ಲಿಸಿ' : 'Stop'}</span>
                            </button>
                          </div>
                        ) : (
                          <button
                            type="button"
                            onClick={() => playAudio(msg.audio_url!, msg.id || index)}
                            className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-400 hover:underline"
                          >
                            <Volume2 className="w-3.5 h-3.5" />
                            <span>
                              {language === 'kn' ? 'ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ (Listen Audio)' : 'Play Audio'}
                            </span>
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {convState === 'processing' && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-slate-900 rounded-2xl p-3.5 text-xs border border-slate-200 dark:border-slate-800 flex items-center gap-2.5 shadow-sm">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-ping"></div>
                  <span className="font-kannada text-slate-600 dark:text-slate-300">
                    {language === 'kn'
                      ? 'ಕೃಷಿ ಮಾಹಿತಿ ಮತ್ತು ಅಧಿಕೃತ ನಿಯಮಗಳನ್ನು ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...'
                      : 'Consulting official agricultural rules & generating guidance...'}
                  </span>
                </div>
              </div>
            )}

            <div ref={scrollRef} />
          </div>

          {/* Quick Questions Strip */}
          <div className="px-4 py-2.5 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center gap-2 overflow-x-auto scrollbar-none">
            <span className="text-[10px] font-bold uppercase text-slate-500 shrink-0 font-kannada">
              {language === 'kn' ? 'ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು:' : 'Quick Prompts:'}
            </span>
            {getContextualPrompts().map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(language === 'kn' ? q.kn : q.en)}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 whitespace-nowrap hover:bg-emerald-600 hover:text-white transition font-kannada"
              >
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-200/70 dark:bg-emerald-900/80 text-emerald-900 dark:text-emerald-100">
                  {q.category}
                </span>
                <span>{language === 'kn' ? q.kn : q.en}</span>
              </button>
            ))}
          </div>

          {/* Unified Input Bar */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend(inputText);
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                placeholder={
                  language === 'kn'
                    ? 'ಕನ್ನಡದಲ್ಲಿ ಪ್ರಶ್ನೆ ಬರೆಯಿರಿ ಅಥವಾ ಎಡಗಡೆಯ ಮೈಕ್ ಬಳಸಿ ಮಾತನಾಡಿ...'
                    : 'Type your agriculture question or tap the mic on the left...'
                }
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="flex-1 px-4 py-3 text-xs sm:text-sm rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 font-kannada"
              />

              <button
                type="submit"
                disabled={!inputText.trim() || convState === 'processing'}
                className="px-5 py-3 rounded-2xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs sm:text-sm shadow transition disabled:opacity-40"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* =========================================================================
          CONVERSATION HISTORY DRAWER (Requirement 4)
      ========================================================================= */}
      {isHistoryDrawerOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
            onClick={() => setIsHistoryDrawerOpen(false)}
          />

          <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
            <div className="w-screen max-w-md bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col">
              {/* Drawer Header */}
              <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <History className="w-5 h-5 text-emerald-600" />
                  <h3 className="font-bold text-slate-900 dark:text-white font-kannada">
                    {language === 'kn' ? 'ಸಂವಾದ ಇತಿಹಾಸ (Conversations)' : 'Conversation History'}
                  </h3>
                </div>

                <button
                  type="button"
                  onClick={() => setIsHistoryDrawerOpen(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Drawer Actions */}
              <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
                <button
                  type="button"
                  onClick={handleStartNewConversation}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>{language === 'kn' ? 'ಹೊಸ ಸಂವಾದ' : 'New Chat'}</span>
                </button>

                {conversationsList.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowDeleteAllModal(true)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-50 dark:bg-rose-950 text-rose-700 dark:text-rose-300 rounded-xl text-xs font-semibold hover:bg-rose-100"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>{language === 'kn' ? 'ಎಲ್ಲವನ್ನೂ ಅಳಿಸಿ' : 'Clear All'}</span>
                  </button>
                )}
              </div>

              {/* Conversations List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {historyLoading ? (
                  <div className="py-12 text-center text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                    <span className="text-xs">{language === 'kn' ? 'ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...' : 'Loading history...'}</span>
                  </div>
                ) : conversationsList.length === 0 ? (
                  <div className="py-12 text-center text-slate-400">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-40" />
                    <p className="text-xs">
                      {language === 'kn'
                        ? 'ಇನ್ನೂ ಯಾವುದೇ ಹಿಂದಿನ ಸಂವಾದಗಳು ಲಭ್ಯವಿಲ್ಲ.'
                        : 'No previous conversations found.'}
                    </p>
                  </div>
                ) : (
                  conversationsList.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => handleSelectConversation(conv)}
                      className={`p-3.5 rounded-2xl border transition cursor-pointer text-left ${
                        activeConvId === conv.id
                          ? 'border-emerald-600 bg-emerald-50/80 dark:bg-emerald-950/40 ring-1 ring-emerald-500/20'
                          : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate font-kannada">
                            {conv.title}
                          </h4>
                          <span className="inline-block mt-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                            {conv.topic}
                          </span>
                        </div>

                        <button
                          type="button"
                          onClick={(e) => handleDeleteConversation(conv.id, e)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition"
                          title="Delete Conversation"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {conv.last_message && (
                        <p className="text-xs text-slate-500 dark:text-slate-400 truncate mt-2 font-kannada">
                          {conv.last_message}
                        </p>
                      )}

                      <div className="text-[10px] text-slate-400 mt-2">
                        {new Date(conv.updated_at).toLocaleString(language === 'kn' ? 'kn-IN' : 'en-IN', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete All Conversations Confirmation Modal */}
      {showDeleteAllModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-950 text-rose-600 mx-auto flex items-center justify-center">
              <Trash2 className="w-6 h-6" />
            </div>

            <h3 className="text-lg font-bold text-slate-900 dark:text-white font-kannada">
              {language === 'kn' ? 'ಎಲ್ಲಾ ಸಂವಾದಗಳನ್ನು ಅಳಿಸುವುದೇ?' : 'Delete All Conversations?'}
            </h3>

            <p className="text-xs text-slate-500 dark:text-slate-400">
              {language === 'kn'
                ? 'ನಿಮ್ಮ ಎಲ್ಲಾ ಹಿಂದಿನ ಸಂವಾದ ಇತಿಹಾಸವನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸಲಾಗುತ್ತದೆ.'
                : 'This will permanently remove all your conversation history.'}
            </p>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowDeleteAllModal(false)}
                className="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold text-xs rounded-xl"
              >
                {language === 'kn' ? 'ರದ್ದುಮಾಡಿ' : 'Cancel'}
              </button>

              <button
                type="button"
                onClick={handleDeleteAllConversations}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs rounded-xl shadow"
              >
                {language === 'kn' ? 'ಹೌದು, ಅಳಿಸಿ' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
