import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Send,
  Volume2,
  VolumeX,
  Square,
  RotateCcw,
  Sparkles,
  AlertCircle,
  Languages,
  CheckCircle2,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { ChatMessage } from '../types';

type ConversationState = 'idle' | 'listening' | 'processing' | 'speaking' | 'interrupted' | 'error';

export const VoiceAssistantPage: React.FC = () => {
  const { language, regionalDialect, setRegionalDialect } = useLanguage();
  const { user, profile } = useAuth();

  const [convState, setConvState] = useState<ConversationState>('idle');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isMuted, setIsMuted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [sessionId] = useState(() => 'fs_sess_' + Math.random().toString(36).substring(2, 9));

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Suggested Quick Prompts in Kannada
  const quickPrompts = [
    { kn: 'ನನಗೆ ಭತ್ತಕ್ಕೆ ಸಿಗುವ ಯೋಜನೆಗಳ ಮಾಹಿತಿ ಕೊಡಿ', en: 'Tell me about paddy schemes' },
    { kn: 'ನನ್ನ ಬಳಿ ೩ ಎಕರೆ ಜಮೀನಿದೆ, ನನಗೆ ಸಬ್ಸಿಡಿ ಸಿಗುತ್ತದೆಯೇ?', en: 'I have 3 acres, do I qualify?' },
    { kn: 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಸಾಲ ಪಡೆಯುವುದು ಹೇಗೆ?', en: 'How to get KCC crop loan?' },
    { kn: 'ರಾಗಿ ಬೆಳೆಗೆ ಎನ್‌ಪಿಕೆ ಗೊಬ್ಬರ ಎಷ್ಟು ಹಾಕಬೇಕು?', en: 'Fertilizer dosage for ragi' },
  ];

  // Initialize Web Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'kn-IN';

      recognition.onstart = () => {
        setConvState('listening');
        setErrorMessage(null);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript && transcript.trim()) {
          handleSend(transcript.trim());
        } else {
          setConvState('idle');
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech Recognition error:', event.error);
        if (event.error === 'not-allowed') {
          setErrorMessage('ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ (Microphone permission denied).');
        } else if (event.error !== 'no-speech') {
          setErrorMessage('ಧ್ವನಿ ಗ್ರಹಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಮಾತನಾಡಿ.');
        }
        setConvState('idle');
      };

      recognition.onend = () => {
        setConvState((prev) => (prev === 'listening' ? 'idle' : prev));
      };

      recognitionRef.current = recognition;
    }

    const greetingKn =
      regionalDialect === 'North Karnataka'
        ? 'ನಮಸ್ಕಾರ್ರೀ ಅಪ್ಪಾ, ನಮ್ದು ಕೃಷಿ ಮಿತ್ರ AI ಧ್ವನಿ ಸಹಾಯಕ ನೋಡ್ರೀ. ನೀವು ಬೆಳೆ, ಜಮೀನು ಅಥವಾ ಸರ್ಕಾರದ ಸಬ್ಸಿಡಿ ಬಗ್ಗೆ ಕನ್ನಡದಲ್ಲೇ ಮಾತನಾಡಿ ಕೇಳ್ರಿ, ನಾನು ನೇರ ಧ್ವನಿಯಲ್ಲೇ ಉತ್ತರಿಸ್ತೇನಿ.'
        : 'ನಮಸ್ಕಾರ, ಕೃಷಿ ಮಿತ್ರ ಕನ್ನಡ ಧ್ವನಿ ಸಹಾಯಕಕ್ಕೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಮಾತನಾಡಿ ಕೇಳಿ, ನಾನು ನಿಮಗೆ ನೆರವಾಗುತ್ತೇನೆ.';

    setMessages([
      {
        sender: 'assistant',
        text: 'Welcome to Krishi Mitra Full-Screen Kannada AI Voice Assistant. Speak naturally in Kannada or type below.',
        text_kn: greetingKn,
      },
    ]);
  }, [regionalDialect]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, convState]);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
    };
  }, []);

  const playAudio = (url: string) => {
    if (isMuted || !url) {
      setConvState('idle');
      return;
    }

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const audio = new Audio(url);
    audioRef.current = audio;
    setConvState('speaking');

    audio.onended = () => {
      setConvState('idle');
    };

    audio.onerror = () => {
      setConvState('idle');
    };

    audio.play().catch((err) => {
      console.warn('Audio play prevented:', err);
      setConvState('idle');
    });
  };

  const handleInterrupt = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setConvState('interrupted');
    setTimeout(() => {
      setConvState('idle');
    }, 400);
  };

  const toggleListening = () => {
    if (convState === 'speaking') {
      handleInterrupt();
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
        recognitionRef.current.lang = 'kn-IN';
        recognitionRef.current.start();
        setConvState('listening');
      } catch (err) {
        console.warn('Recognition start error:', err);
        setConvState('idle');
      }
    } else {
      setErrorMessage('ಬ್ರೌಸರ್‌ನಲ್ಲಿ Web Speech ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೆಳಗೆ ಟೈಪ್ ಮಾಡಿ.');
    }
  };

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim()) return;

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const userMsg: ChatMessage = {
      sender: 'farmer',
      text: textToSend,
      text_kn: textToSend,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setConvState('processing');
    setErrorMessage(null);

    try {
      const res = await api.sendChatMessage({
        message: textToSend,
        session_id: sessionId,
        language: language,
        regional_preference: regionalDialect,
      });

      const botMsg: ChatMessage = {
        sender: 'assistant',
        text: res.reply,
        text_kn: res.reply_kn,
        audio_url: res.audio_url,
        intent: res.intent,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMsg]);

      if (res.audio_url && !isMuted) {
        playAudio(res.audio_url);
      } else {
        setConvState('idle');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage('AI ಸಂವಹನದಲ್ಲಿ ತೊಂದರೆ ಉಂಟಾಗಿದೆ. ದಯವಿಟ್ಟು ಪುನಃ ಮಾತನಾಡಿ.');
      setConvState('error');
      setTimeout(() => setConvState('idle'), 2000);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner & Dialect Selector */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white dark:bg-[#11221A] p-5 rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-[#174C36] flex items-center justify-center text-white">
            <Mic className="w-5 h-5 text-[#D8AA48]" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
              ಕೃಷಿ ಮಿತ್ರ AI ಧ್ವನಿ ಸಂವಾದ (Voice Assistant)
            </h1>
            <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
              Two-way real-time spoken Kannada conversational intelligence
            </p>
          </div>
        </div>

        {/* Dialect Switcher */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-[#69766D] dark:text-[#9BB0A4] font-kannada">
            ಪ್ರಾದೇಶಿಕ ಶೈಲಿ:
          </span>
          <select
            value={regionalDialect}
            onChange={(e) => setRegionalDialect(e.target.value as any)}
            className="px-3 py-1.5 text-xs font-bold rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#174C36] dark:text-[#75A96A] font-kannada"
          >
            <option value="North Karnataka">ಉತ್ತರ ಕರ್ನಾಟಕ (ಧಾರವಾಡ/ಬೆಳಗಾವಿ)</option>
            <option value="South Karnataka">ದಕ್ಷಿಣ ಕರ್ನಾಟಕ (ಮೈಸೂರು/ಮಂಡ್ಯ)</option>
            <option value="Standard Kannada">ಶಿಷ್ಟ ಕನ್ನಡ (ಸರ್ಕಾರಿ ಅಧಿಕೃತ)</option>
          </select>

          <button
            onClick={() => setIsMuted(!isMuted)}
            className="p-2 rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] text-[#69766D] hover:text-[#174C36]"
            title={isMuted ? 'Unmute Audio' : 'Mute Audio'}
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-red-500" /> : <Volume2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Main Interactive Screen */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Giant Glowing Voice Orb & Controller (5 cols) */}
        <div className="lg:col-span-5 bg-gradient-to-b from-white to-[#F7F9F5] dark:from-[#11221A] dark:to-[#0B1711] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-8 shadow-md text-center flex flex-col items-center justify-between min-h-[500px]">
          
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
              Voice Orb Status
            </span>
            <h2 className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
              {convState === 'listening'
                ? 'ಧ್ವನಿ ಗ್ರಹಿಸಲಾಗುತ್ತಿದೆ (Listening...)'
                : convState === 'speaking'
                ? 'ಉತ್ತರಿಸುತ್ತಿದೆ (Speaking in Kannada)'
                : convState === 'processing'
                ? 'ಮಾಹಿತಿ ವಿಶ್ಲೇಷಣೆ (Processing AI)'
                : 'ಮಾತನಾಡಲು ಮೈಕ್ ಒತ್ತಿರಿ (Tap to Speak)'}
            </h2>
          </div>

          {/* Central Animated Orb */}
          <div className="relative my-8">
            {/* Outer Pulsing Wave Rings */}
            {convState === 'listening' && (
              <div className="absolute inset-0 -m-8 rounded-full bg-red-500/20 animate-ping"></div>
            )}
            {convState === 'speaking' && (
              <div className="absolute inset-0 -m-6 rounded-full bg-[#D8AA48]/25 animate-pulse"></div>
            )}

            <button
              onClick={toggleListening}
              className={`w-36 h-36 rounded-full flex flex-col items-center justify-center transition-all duration-300 shadow-2xl relative z-10 ${
                convState === 'listening'
                  ? 'bg-red-600 text-white animate-listening-ring shadow-red-500/50 scale-105'
                  : convState === 'speaking'
                  ? 'bg-gradient-to-tr from-[#174C36] to-[#D8AA48] text-white animate-orb shadow-[#D8AA48]/50'
                  : convState === 'processing'
                  ? 'bg-blue-600 text-white animate-pulse'
                  : 'bg-gradient-to-tr from-[#174C36] to-[#2F7650] text-white hover:scale-105'
              }`}
            >
              {convState === 'listening' ? (
                <>
                  <MicOff className="w-10 h-10 animate-pulse" />
                  <span className="text-[11px] font-bold mt-1">ನಿಲ್ಲಿಸಿ</span>
                </>
              ) : convState === 'speaking' ? (
                <>
                  <Volume2 className="w-10 h-10 text-[#D8AA48] animate-bounce" />
                  <span className="text-[11px] font-bold mt-1">ನಿಲ್ಲಿಸಿ (Interrupt)</span>
                </>
              ) : (
                <>
                  <Mic className="w-10 h-10 text-[#D8AA48]" />
                  <span className="text-xs font-bold mt-1 font-kannada">ಮಾತನಾಡಿ</span>
                </>
              )}
            </button>
          </div>

          {/* Interrupt & Action Buttons */}
          <div className="space-y-3 w-full">
            {convState === 'speaking' && (
              <button
                onClick={handleInterrupt}
                className="w-full py-2.5 rounded-xl bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-300 font-bold text-xs flex items-center justify-center gap-1.5"
              >
                <Square className="w-3.5 h-3.5 fill-current" />
                <span>ಉತ್ತರ ನಿಲ್ಲಿಸಿ ಮತ್ತೊಂದು ಪ್ರಶ್ನೆ ಕೇಳಿ (Interrupt)</span>
              </button>
            )}

            <div className="p-3 rounded-2xl bg-[#EAF3E9]/60 dark:bg-[#152E22]/40 text-xs text-[#2F7650] dark:text-[#92C987] font-medium font-kannada">
              {regionalDialect === 'North Karnataka'
                ? 'ಉತ್ತರ ಕರ್ನಾಟಕ ಆಡುಭಾಷೆ: "ಐತಿ", "ಸಿಗತೈತಿ", "ನೋಡ್ರೀ" ಶೈಲಿಯ ಸಂವಾದ ಸಕ್ರಿಯವಾಗಿದೆ.'
                : 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ ಆಡುಭಾಷೆ: "ಇದೆ", "ಲಭ್ಯವಿದೆ", "ತಿಳಿಸಿ" ಶೈಲಿಯ ಸಂವಾದ ಸಕ್ರಿಯವಾಗಿದೆ.'}
            </div>
          </div>
        </div>

        {/* Right Column: Live Conversation Transcript & Input (7 cols) */}
        <div className="lg:col-span-7 bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm flex flex-col h-[600px] overflow-hidden">
          
          {/* Transcript Header */}
          <div className="p-4 border-b border-[#E2E8DF] dark:border-[#1E382B] flex items-center justify-between text-xs font-bold text-[#69766D] dark:text-[#9BB0A4]">
            <span className="font-kannada uppercase tracking-wide">ಸಂವಾದ ಇತಿಹಾಸ (Conversation Transcript)</span>
            <span>{messages.length} ಸಂದೇಶಗಳು</span>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-[#F7F9F5] dark:bg-[#0B1711]">
            {messages.map((msg, index) => {
              const isBot = msg.sender === 'assistant';
              return (
                <div key={index} className={`flex ${isBot ? 'justify-start' : 'justify-end'}`}>
                  <div
                    className={`max-w-[85%] rounded-3xl p-4 text-xs sm:text-sm leading-relaxed shadow-sm ${
                      isBot
                        ? 'bg-white dark:bg-[#11221A] text-[#19251E] dark:text-[#EDF3EF] border border-[#E2E8DF] dark:border-[#1E382B] rounded-tl-sm'
                        : 'bg-[#174C36] text-white rounded-tr-sm'
                    }`}
                  >
                    {msg.text_kn && (
                      <p className="font-kannada font-medium text-sm leading-relaxed mb-1.5">
                        {msg.text_kn}
                      </p>
                    )}
                    {msg.text !== msg.text_kn && (
                      <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] pt-1 border-t border-[#E2E8DF] dark:border-[#1E382B]">
                        {msg.text}
                      </p>
                    )}

                    {isBot && msg.audio_url && (
                      <button
                        onClick={() => playAudio(msg.audio_url!)}
                        className="mt-2 inline-flex items-center gap-1.5 text-xs font-bold text-[#2F7650] dark:text-[#75A96A] hover:underline"
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>ಮತ್ತೊಮ್ಮೆ ಧ್ವನಿಯಲ್ಲಿ ಕೇಳಿ (Replay)</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}

            {convState === 'processing' && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-[#11221A] rounded-2xl p-3 text-xs border border-[#E2E8DF] dark:border-[#1E382B] flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-[#174C36] animate-ping"></div>
                  <span className="font-kannada text-[#69766D]">ಕೃಷಿ ಮಾಹಿತಿ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...</span>
                </div>
              </div>
            )}

            <div ref={scrollRef} />
          </div>

          {/* Quick Questions Carousel */}
          <div className="px-4 py-2 border-t border-[#E2E8DF] dark:border-[#1E382B] bg-white dark:bg-[#11221A] flex items-center gap-2 overflow-x-auto scrollbar-none">
            <span className="text-[10px] font-bold uppercase text-[#69766D] shrink-0 font-kannada">
              ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು:
            </span>
            {quickPrompts.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q.kn)}
                className="px-3 py-1 rounded-full text-xs bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] border border-[#75A96A]/30 whitespace-nowrap hover:bg-[#75A96A] hover:text-white transition-colors font-kannada"
              >
                {q.kn}
              </button>
            ))}
          </div>

          {/* Input Bar */}
          <div className="p-4 border-t border-[#E2E8DF] dark:border-[#1E382B] bg-white dark:bg-[#11221A]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend(inputText);
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                placeholder="ಕನ್ನಡದಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಎಡಗಡೆಯ ಮೈಕ್ ಬಳಸಿ..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="flex-1 px-4 py-3 text-xs sm:text-sm rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650] font-kannada"
              />
              <button
                type="submit"
                disabled={!inputText.trim() || convState === 'processing'}
                className="px-5 py-3 rounded-2xl bg-[#174C36] hover:bg-[#123B2B] text-white font-bold text-xs sm:text-sm shadow transition-colors disabled:opacity-40"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
