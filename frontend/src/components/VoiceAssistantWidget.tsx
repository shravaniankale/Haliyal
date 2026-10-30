import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Mic,
  MicOff,
  Send,
  X,
  Volume2,
  VolumeX,
  Maximize2,
  Sparkles,
  RotateCcw,
  Square,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { ChatMessage } from '../types';

type ConversationState = 'idle' | 'listening' | 'processing' | 'speaking' | 'interrupted' | 'error';

export const VoiceAssistantWidget: React.FC = () => {
  const { language, regionalDialect } = useLanguage();
  const { user, profile } = useAuth();
  const navigate = useNavigate();

  const [isOpen, setIsOpen] = useState(false);
  const [convState, setConvState] = useState<ConversationState>('idle');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isAudioMuted, setIsAudioMuted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [sessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 9));

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Initialize Web Speech Recognition for Kannada
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      // Configure Kannada (kn-IN)
      recognition.lang = 'kn-IN';

      recognition.onstart = () => {
        setConvState('listening');
        setErrorMessage(null);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript && transcript.trim()) {
          handleSendMessage(transcript.trim());
        } else {
          setConvState('idle');
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        if (event.error === 'not-allowed') {
          setErrorMessage('ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ (Microphone permission denied).');
        } else if (event.error !== 'no-speech') {
          setErrorMessage('ಧ್ವನಿ ಗ್ರಹಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ, ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಮಾತನಾಡಿ.');
        }
        setConvState('idle');
      };

      recognition.onend = () => {
        // If it wasn't transitioned to processing, set back to idle
        setConvState((prev) => (prev === 'listening' ? 'idle' : prev));
      };

      recognitionRef.current = recognition;
    }

    // Initial greeting
    const greetingTextKn =
      regionalDialect === 'North Karnataka'
        ? 'ನಮಸ್ಕಾರ್ರೀ ಅಪ್ಪಾ, ನಮ್ದು ಕೃಷಿ ಮಿತ್ರ AI ಸಹಾಯಕ ನೋಡ್ರೀ. ನಿಮ್ಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆ ಅಥವಾ ಬೆಳೆ ಮಾಹಿತಿ ಬೇಕ್ರಿ? ಮೈಕ್ ಬಟನ್ ಒತ್ತಿ ಕನ್ನಡದಲ್ಲೇ ಕೇಳ್ರಿ!'
        : 'ನಮಸ್ಕಾರ, ಕೃಷಿ ಮಿತ್ರ AI ಸಹಾಯಕ್ಕೆ ಸ್ವಾಗತ. ನಿಮಗೆ ಯಾವ ಯೋಜನೆ ಅಥವಾ ಕೃಷಿ ಮಾಹಿತಿ ಬೇಕು? ಮೈಕ್ ಒತ್ತಿ ಮಾತನಾಡಿ.';

    setMessages([
      {
        sender: 'assistant',
        text: 'Welcome to Krishi Mitra AI! How can I assist you with schemes, loans, or crop guidance? Speak in Kannada or type below.',
        text_kn: greetingTextKn,
      },
    ]);
  }, [regionalDialect]);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, convState]);

  // Clean up audio on unmount
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

  // Play audio automatically
  const playKannadaAudio = (audioUrl: string) => {
    if (isAudioMuted || !audioUrl) {
      setConvState('idle');
      return;
    }

    // Stop existing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    setConvState('speaking');

    audio.onended = () => {
      setConvState('idle');
    };

    audio.onerror = (e) => {
      console.warn('Audio playback error:', e);
      setConvState('idle');
    };

    audio.play().catch((err) => {
      console.warn('Auto-play blocked or failed:', err);
      setConvState('idle');
    });
  };

  // Interrupt speaking
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

  // Toggle voice listening
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
        console.warn('Recognition start failed:', err);
        setConvState('idle');
      }
    } else {
      setErrorMessage('ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ Web Speech ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಟೈಪ್ ಮಾಡಿ.');
    }
  };

  // Send message to AI backend
  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim()) return;

    // Stop speaking if running
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
      const response = await api.sendChatMessage({
        message: textToSend,
        session_id: sessionId,
        language: language,
        regional_preference: regionalDialect,
      });

      const botMsg: ChatMessage = {
        sender: 'assistant',
        text: response.reply,
        text_kn: response.reply_kn,
        audio_url: response.audio_url,
        intent: response.intent,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMsg]);

      // Automatic Two-Way Audio Playback
      if (response.audio_url && !isAudioMuted) {
        playKannadaAudio(response.audio_url);
      } else {
        setConvState('idle');
      }
    } catch (err: any) {
      console.error('Chat error:', err);
      setErrorMessage('AI ಸಹಾಯಕರ ಸಂಪರ್ಕದಲ್ಲಿ ತೊಂದರೆಯಾಗಿದೆ. ದಯವಿಟ್ಟು ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.');
      setConvState('error');
      setTimeout(() => setConvState('idle'), 2500);
    }
  };

  return (
    <>
      {/* Floating Action Trigger Button (Bottom Right) */}
      {!isOpen && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3">
          {/* Pulsing Helper Tooltip */}
          <div className="hidden sm:flex items-center gap-2 bg-[#174C36] text-white text-xs px-3.5 py-2 rounded-full shadow-lg border border-[#75A96A]/40 animate-bounce">
            <Sparkles className="w-3.5 h-3.5 text-[#D8AA48]" />
            <span className="font-kannada font-medium">ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ</span>
          </div>

          <button
            onClick={() => setIsOpen(true)}
            className="w-16 h-16 rounded-full bg-gradient-to-tr from-[#174C36] via-[#2F7650] to-[#75A96A] text-white flex items-center justify-center shadow-2xl hover:scale-110 transition-transform relative group border-2 border-[#D8AA48]"
            title="Open Krishi Mitra AI Assistant"
          >
            <Mic className="w-7 h-7 text-[#D8AA48] animate-pulse" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-[#D8AA48] rounded-full border-2 border-white animate-ping"></span>
          </button>
        </div>
      )}

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-[95vw] sm:w-[440px] h-[640px] max-h-[90vh] bg-white dark:bg-[#11221A] rounded-2xl shadow-2xl border border-[#E2E8DF] dark:border-[#1E382B] flex flex-col overflow-hidden transition-all duration-300">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-[#174C36] via-[#123B2B] to-[#2F7650] text-white p-4 flex items-center justify-between shadow-md">
            <div className="flex items-center gap-3">
              {/* Animated Glowing Orb Status */}
              <div
                onClick={handleInterrupt}
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all cursor-pointer ${
                  convState === 'listening'
                    ? 'bg-red-500 animate-listening-ring shadow-lg shadow-red-500/50'
                    : convState === 'speaking'
                    ? 'bg-[#D8AA48] animate-orb shadow-lg shadow-[#D8AA48]/50'
                    : convState === 'processing'
                    ? 'bg-blue-400 animate-spin'
                    : 'bg-[#2F7650]'
                }`}
                title={convState === 'speaking' ? 'Click to interrupt' : 'AI Voice Orb'}
              >
                {convState === 'listening' ? (
                  <Mic className="w-5 h-5 text-white animate-pulse" />
                ) : convState === 'speaking' ? (
                  <Volume2 className="w-5 h-5 text-[#123B2B]" />
                ) : (
                  <Sparkles className="w-5 h-5 text-[#D8AA48]" />
                )}
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-sm tracking-wide">KRISHI MITRA AI</h3>
                  <span className="text-[10px] bg-[#D8AA48] text-[#123B2B] font-bold px-1.5 py-0.2 rounded">
                    ಕನ್ನಡ AI
                  </span>
                </div>
                <p className="text-[11px] text-[#EAF3E9]/80 font-kannada">
                  {convState === 'listening'
                    ? 'ಧ್ವನಿ ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದೆ... (Listening)'
                    : convState === 'speaking'
                    ? 'ಉತ್ತರಿಸುತ್ತಿದೆ... (Speaking)'
                    : convState === 'processing'
                    ? 'ಯೋಚಿಸುತ್ತಿದೆ... (Processing)'
                    : `${regionalDialect === 'North Karnataka' ? 'ಉತ್ತರ ಕರ್ನಾಟಕ' : 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ'} ಶೈಲಿ`}
                </p>
              </div>
            </div>

            {/* Header Action Controls */}
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setIsAudioMuted(!isAudioMuted)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-white/90"
                title={isAudioMuted ? 'Unmute Audio' : 'Mute Audio'}
              >
                {isAudioMuted ? <VolumeX className="w-4 h-4 text-red-300" /> : <Volume2 className="w-4 h-4" />}
              </button>

              <button
                onClick={() => {
                  setIsOpen(false);
                  navigate('/voice-assistant');
                }}
                className="p-1.5 rounded-lg hover:bg-white/10 text-white/90"
                title="Open Fullscreen Voice Assistant"
              >
                <Maximize2 className="w-4 h-4" />
              </button>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-white/90"
                title="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Conversation State Banner */}
          {convState === 'speaking' && (
            <div className="bg-[#D8AA48]/15 dark:bg-[#D8AA48]/10 px-4 py-2 border-b border-[#D8AA48]/30 flex items-center justify-between text-xs text-[#174C36] dark:text-[#E5BE5F]">
              <div className="flex items-center gap-2">
                <span className="flex gap-0.5 items-end h-3">
                  <span className="w-1 bg-[#D8AA48] voice-bar h-3"></span>
                  <span className="w-1 bg-[#D8AA48] voice-bar h-2 animation-delay-200"></span>
                  <span className="w-1 bg-[#D8AA48] voice-bar h-3.5 animation-delay-400"></span>
                </span>
                <span className="font-semibold font-kannada">ಕನ್ನಡದಲ್ಲಿ ಧ್ವನಿ ಮೂಡುತ್ತಿದೆ...</span>
              </div>
              <button
                onClick={handleInterrupt}
                className="flex items-center gap-1 text-[11px] font-bold bg-white dark:bg-[#11221A] px-2 py-0.5 rounded border border-[#D8AA48] text-red-600 hover:bg-red-50"
              >
                <Square className="w-3 h-3 fill-current" />
                <span>ನಿಲ್ಲಿಸಿ (Interrupt)</span>
              </button>
            </div>
          )}

          {/* Error Banner */}
          {errorMessage && (
            <div className="bg-red-50 dark:bg-red-950/40 px-3 py-2 border-b border-red-200 dark:border-red-800 flex items-center gap-2 text-xs text-red-700 dark:text-red-300">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span className="font-kannada">{errorMessage}</span>
            </div>
          )}

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-[#F7F9F5] dark:bg-[#0B1711]">
            {messages.map((msg, index) => {
              const isAssistant = msg.sender === 'assistant';
              return (
                <div
                  key={index}
                  className={`flex ${isAssistant ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-3.5 text-xs sm:text-sm leading-relaxed shadow-sm ${
                      isAssistant
                        ? 'bg-white dark:bg-[#11221A] text-[#19251E] dark:text-[#EDF3EF] border border-[#E2E8DF] dark:border-[#1E382B] rounded-tl-sm'
                        : 'bg-[#174C36] text-white rounded-tr-sm'
                    }`}
                  >
                    {/* Kannada text */}
                    {msg.text_kn && (
                      <p className="font-kannada font-medium text-sm leading-relaxed mb-1.5">
                        {msg.text_kn}
                      </p>
                    )}
                    {/* English translation */}
                    {language === 'en' && msg.text !== msg.text_kn && (
                      <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] pt-1 border-t border-[#E2E8DF] dark:border-[#1E382B]">
                        {msg.text}
                      </p>
                    )}

                    {/* Audio replay button */}
                    {msg.audio_url && isAssistant && (
                      <button
                        onClick={() => playKannadaAudio(msg.audio_url!)}
                        className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-[#2F7650] dark:text-[#75A96A] hover:underline"
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>ಮತ್ತೊಮ್ಮೆ ಕೇಳಿ (Replay)</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Processing Indicator */}
            {convState === 'processing' && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-[#11221A] rounded-2xl p-3 text-xs border border-[#E2E8DF] dark:border-[#1E382B] flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-[#174C36] animate-ping"></div>
                  <span className="font-kannada text-[#69766D] dark:text-[#9BB0A4]">
                    ಕೃಷಿ ಮಾಹಿತಿ ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Bottom Voice & Text Input Bar */}
          <div className="p-3 bg-white dark:bg-[#11221A] border-t border-[#E2E8DF] dark:border-[#1E382B]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage(inputText);
              }}
              className="flex items-center gap-2"
            >
              {/* Large Microphone Button */}
              <button
                type="button"
                onClick={toggleListening}
                className={`p-3 rounded-full transition-all shrink-0 ${
                  convState === 'listening'
                    ? 'bg-red-600 text-white animate-pulse shadow-lg shadow-red-500/50 scale-105'
                    : convState === 'speaking'
                    ? 'bg-[#D8AA48] text-[#123B2B] hover:scale-105'
                    : 'bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] hover:bg-[#75A96A] hover:text-white'
                }`}
                title={convState === 'listening' ? 'Stop listening' : 'Speak in Kannada'}
              >
                {convState === 'listening' ? (
                  <MicOff className="w-5 h-5 text-white" />
                ) : convState === 'speaking' ? (
                  <Square className="w-5 h-5 fill-current" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </button>

              {/* Text Input */}
              <input
                type="text"
                placeholder="ಕನ್ನಡದಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಮಾತನಾಡಿ..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="flex-1 px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:ring-1 focus:ring-[#2F7650] font-kannada"
              />

              {/* Send Button */}
              <button
                type="submit"
                disabled={!inputText.trim() || convState === 'processing'}
                className="p-2.5 rounded-xl bg-[#174C36] text-white hover:bg-[#123B2B] disabled:opacity-40 transition-colors shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>

            {/* Micro dialect indicator footer */}
            <div className="flex items-center justify-between text-[10px] text-[#69766D] dark:text-[#9BB0A4] pt-2 px-1">
              <span className="font-kannada">
                ಧ್ವನಿ ಶೈಲಿ: <span className="font-semibold text-[#174C36] dark:text-[#75A96A]">{regionalDialect}</span>
              </span>
              <span>Kannada Neural Voice Active</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
