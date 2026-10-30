import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { api } from '../services/api';

export type Theme = 'light' | 'dark';
export type Language = 'kn' | 'en';
export type RegionalDialect = 'North Karnataka' | 'South Karnataka' | 'Standard Kannada' | 'English';
export type VoiceGender = 'female' | 'male';

export interface AppSettings {
  theme: Theme;
  language: Language;
  regionalDialect: RegionalDialect;
  voiceGender: VoiceGender;
  voiceAssistantEnabled: boolean;
  autoVoiceResponse: boolean;
  voiceInputEnabled: boolean;
  speechSpeed: number;
}

export interface SettingsContextType extends AppSettings {
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  setRegionalDialect: (dialect: RegionalDialect) => void;
  setVoiceGender: (gender: VoiceGender) => void;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  setVoiceAssistantEnabled: (enabled: boolean) => void;
  setAutoVoiceResponse: (enabled: boolean) => void;
  setVoiceInputEnabled: (enabled: boolean) => void;
  setSpeechSpeed: (speed: number) => void;
  updateSettings: (partial: Partial<AppSettings>) => void;
  syncFromProfile: (profileData: any) => void;
  t: (key: string) => string;
}

const TRANSLATIONS: Record<string, { kn: string; en: string }> = {
  // Brand & Navigation
  brandName: { kn: 'ಕೃಷಿ ಮಿತ್ರ', en: 'Krishi Mitra' },
  tagline: { kn: 'ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ', en: 'Your Smart Agriculture Assistant' },
  navHome: { kn: 'ಮುಖಪುಟ', en: 'Home' },
  navSchemes: { kn: 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು', en: 'Government Schemes' },
  navEligibility: { kn: 'ಅರ್ಹತೆ ಪರಿಶೀಲನೆ', en: 'Find Schemes for Me' },
  navLoans: { kn: 'ಕೃಷಿ ಸಾಲಗಳು', en: 'Agriculture Loans' },
  navCrop: { kn: 'ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ', en: 'Crop Guidance' },
  navFertilizer: { kn: 'ಗೊಬ್ಬರ ಮಾಹಿತಿ', en: 'Fertilizer Guidance' },
  navWeatherMarket: { kn: 'ಹವಾಮಾನ & ಮಾರುಕಟ್ಟೆ', en: 'Weather & Prices' },
  navSaved: { kn: 'ಉಳಿಸಿದ ಯೋಜನೆಗಳು', en: 'Saved Schemes' },
  navProfile: { kn: 'ನನ್ನ ಪ್ರೊಫೈಲ್', en: 'Profile' },
  navAdmin: { kn: 'ಅಡ್ಮಿನ್ ಲಾಗಿನ್', en: 'Admin Panel' },
  navLogin: { kn: 'ಲಾಗಿನ್', en: 'Login' },
  navRegister: { kn: 'ನೋಂದಣಿ', en: 'Register' },
  navLogout: { kn: 'ನಿರ್ಗಮಿಸಿ', en: 'Logout' },

  // Hero Section
  heroBadge: { kn: 'ಕರ್ನಾಟಕ ರೈತರಿಗಾಗಿ AI ಕೃಷಿ ತಂತ್ರಜ್ಞಾನ', en: 'AI Agriculture Assistant for Karnataka Farmers' },
  heroMainTitle: { kn: 'ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ', en: 'Your Smart Agriculture Assistant' },
  heroSubtitle: {
    kn: 'ಕನ್ನಡ ಧ್ವನಿ ಸಂವಾದದ ಮೂಲಕ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಬೆಳೆ ವಿಮೆ, ಕೃಷಿ ಸಾಲಗಳು ಮತ್ತು ನಿಖರ ಬೆಳೆ ಮಾಹಿತಿಯನ್ನು ಸುಲಭವಾಗಿ ಪಡೆಯಿರಿ.',
    en: 'Discover government schemes, crop insurance, agricultural loans and farming guidance through intelligent Kannada voice assistance.'
  },
  btnExploreSchemes: { kn: 'ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ', en: 'Explore Schemes' },
  btnTalkAi: { kn: 'ಕೃಷಿ ಮಿತ್ರನೊಂದಿಗೆ ಮಾತನಾಡಿ', en: 'Talk to Krishi Mitra' },
  heroSearchPlaceholder: { kn: 'ಯೋಜನೆಗಳು, ಬೆಳೆ ಅಥವಾ ಸಬ್ಸಿಡಿಗಳನ್ನು ಹುಡುಕಿ...', en: 'Search schemes, crops, or subsidies...' },

  // Stats
  statVerified: { kn: 'ಪರಿಶೀಲಿಸಿದ ಯೋಜನೆಗಳು', en: 'Verified Schemes' },
  statDistricts: { kn: 'ಒಳಗೊಂಡ ಜಿಲ್ಲೆಗಳು', en: 'Districts Covered' },
  statServices: { kn: 'ಕೃಷಿ ಸೇವೆಗಳು', en: 'Agricultural Services' },
  statSaved: { kn: 'ಉಳಿಸಿದ ಯೋಜನೆಗಳು', en: 'Saved Schemes' },

  // Services
  servicesTitle: { kn: 'ನಮ್ಮ ಕೃಷಿ ಸೇವೆಗಳು', en: 'Our Agricultural Services' },
  servicesSubtitle: { kn: 'ರೈತರ ಸಬಲೀಕರಣಕ್ಕಾಗಿ ಆಧುನಿಕ ತಂತ್ರಜ್ಞಾನ', en: 'Empowering farmers with modern agricultural technology' },

  // Regional Speech Labels
  speechNorth: { kn: 'ಉತ್ತರ ಕರ್ನಾಟಕ ಧ್ವನಿ', en: 'North Karnataka Voice' },
  speechSouth: { kn: 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ ಧ್ವನಿ', en: 'South Karnataka Voice' },
  speechStandard: { kn: 'ಶಿಷ್ಟ ಕನ್ನಡ ಧ್ವನಿ', en: 'Standard Kannada Voice' },
  speechEnglish: { kn: 'ಇಂಡಿಯನ್ ಇಂಗ್ಲಿಷ್', en: 'Indian English' },

  // Voice Gender
  voiceFemale: { kn: 'ಮಹಿಳಾ ಧ್ವನಿ (ಸಪ್ನಾ)', en: 'Female Voice (Sapna)' },
  voiceMale: { kn: 'ಪುರುಷ ಧ್ವನಿ (ಗಗನ್)', en: 'Male Voice (Gagan)' },
  previewVoice: { kn: 'ಧ್ವನಿ ಕೇಳಿ', en: 'Preview Voice' },

  // Dashboard Section Titles
  sectionProfile: { kn: 'ನನ್ನ ಕೃಷಿ ವಿವರ (ರೈತ ಪ್ರೊಫೈಲ್)', en: 'My Farm Profile' },
  sectionWeather: { kn: 'ಹವಾಮಾನ ಬುಲೆಟಿನ್ & ಮುನ್ಸೂಚನೆ', en: 'Weather Bulletin & Forecast' },
  sectionSeason: { kn: 'ಪ್ರಸ್ತುತ ಕೃಷಿ ಋತು & ಕ್ಯಾಲೆಂಡರ್', en: 'Current Agricultural Season' },
  sectionSchemes: { kn: 'ನಿಮಗಾಗಿ ಶಿಫಾರಸು ಮಾಡಿದ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು', en: 'Recommended Government Schemes' },
  sectionInsurance: { kn: 'ಬೆಳೆ ವಿಮೆ (ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ - PMFBY)', en: 'Crop Insurance (Samrakshane PMFBY)' },
  sectionGuidance: { kn: 'ವೈಯಕ್ತಿಕ ಬೆಳೆ & ರೋಗ ಮಾರ್ಗದರ್ಶನ', en: 'Personalized Crop Guidance' },
  sectionFertilizer: { kn: 'ರಸಗೊಬ್ಬರ & ಪೋಷಕಾಂಶ ನಿರ್ವಹಣೆ', en: 'Fertilizer & Nutrient Advisory' },
  sectionMandi: { kn: 'ಕರ್ನಾಟಕ APMC ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು', en: 'Karnataka APMC Market Prices' },
  sectionVoiceAi: { kn: 'ಧ್ವನಿ-ಪ್ರಥಮ AI ಸಹಾಯಕ ಸಂವಾದ', en: 'Voice-First AI Assistant' },
};

const SettingsContext = createContext<SettingsContextType | null>(null);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 1. Initial State from LocalStorage
  const [theme, setThemeState] = useState<Theme>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_theme');
      if (saved === 'dark' || saved === 'light') return saved;
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    } catch {}
    return 'light';
  });

  const [regionalDialect, setRegionalDialectState] = useState<RegionalDialect>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_dialect');
      if (saved) return saved as RegionalDialect;
    } catch {}
    return 'North Karnataka';
  });

  const [language, setLanguageState] = useState<Language>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_lang');
      if (saved === 'kn' || saved === 'en') return saved;
      const dialect = localStorage.getItem('krishi_mitra_dialect');
      return dialect === 'English' ? 'en' : 'kn';
    } catch {}
    return 'kn';
  });

  const [voiceGender, setVoiceGenderState] = useState<VoiceGender>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_voice_gender');
      if (saved === 'male' || saved === 'female') return saved;
    } catch {}
    return 'female';
  });

  const [voiceAssistantEnabled, setVoiceAssistantEnabledState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_voice_enabled');
      return saved !== null ? saved === 'true' : true;
    } catch {}
    return true;
  });

  const [autoVoiceResponse, setAutoVoiceResponseState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_auto_voice');
      return saved !== null ? saved === 'true' : true;
    } catch {}
    return true;
  });

  const [voiceInputEnabled, setVoiceInputEnabledState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_voice_input');
      return saved !== null ? saved === 'true' : true;
    } catch {}
    return true;
  });

  const [speechSpeed, setSpeechSpeedState] = useState<number>(() => {
    try {
      const saved = localStorage.getItem('krishi_mitra_speech_speed');
      return saved ? parseFloat(saved) : 1.0;
    } catch {}
    return 1.0;
  });

  // Debounce ref for backend sync
  const syncTimeoutRef = useRef<any>(null);

  // Sync DOM with theme
  useEffect(() => {
    try {
      localStorage.setItem('krishi_mitra_theme', theme);
    } catch {}

    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.setAttribute('data-theme', 'light');
    }
  }, [theme]);

  // Backend persistence helper (safely fires in background when authenticated)
  const scheduleBackendSync = (updates: Record<string, any>) => {
    const token = localStorage.getItem('krishi_mitra_token');
    if (!token) return;

    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current);
    }

    syncTimeoutRef.current = setTimeout(async () => {
      try {
        await api.updateFarmerProfile(updates);
      } catch (err) {
        console.warn('Settings background synchronization notice:', err);
      }
    }, 400);
  };

  // Updaters
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    scheduleBackendSync({ theme_preference: newTheme });
  };

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
  };

  const setRegionalDialect = (newDialect: RegionalDialect) => {
    setRegionalDialectState(newDialect);
    try {
      localStorage.setItem('krishi_mitra_dialect', newDialect);
    } catch {}

    const newLang = newDialect === 'English' ? 'en' : 'kn';
    setLanguageState(newLang);
    try {
      localStorage.setItem('krishi_mitra_lang', newLang);
    } catch {}

    scheduleBackendSync({
      regional_speech_preference: newDialect,
      preferred_language: newLang
    });
  };

  const setVoiceGender = (newGender: VoiceGender) => {
    setVoiceGenderState(newGender);
    try {
      localStorage.setItem('krishi_mitra_voice_gender', newGender);
    } catch {}
    scheduleBackendSync({ voice_gender_preference: newGender });
  };

  const setLanguage = (newLang: Language) => {
    setLanguageState(newLang);
    try {
      localStorage.setItem('krishi_mitra_lang', newLang);
    } catch {}

    // If English selected, dialect becomes English; if Kannada, keep current or fallback to North/Standard
    if (newLang === 'en' && regionalDialect !== 'English') {
      setRegionalDialectState('English');
      try {
        localStorage.setItem('krishi_mitra_dialect', 'English');
      } catch {}
    } else if (newLang === 'kn' && regionalDialect === 'English') {
      setRegionalDialectState('North Karnataka');
      try {
        localStorage.setItem('krishi_mitra_dialect', 'North Karnataka');
      } catch {}
    }

    scheduleBackendSync({ preferred_language: newLang });
  };

  const toggleLanguage = () => {
    const next = language === 'kn' ? 'en' : 'kn';
    setLanguage(next);
  };

  const setVoiceAssistantEnabled = (enabled: boolean) => {
    setVoiceAssistantEnabledState(enabled);
    try {
      localStorage.setItem('krishi_mitra_voice_enabled', String(enabled));
    } catch {}
    scheduleBackendSync({ voice_assistant_enabled: enabled });
  };

  const setAutoVoiceResponse = (enabled: boolean) => {
    setAutoVoiceResponseState(enabled);
    try {
      localStorage.setItem('krishi_mitra_auto_voice', String(enabled));
    } catch {}
    scheduleBackendSync({ auto_voice_response: enabled });
  };

  const setVoiceInputEnabled = (enabled: boolean) => {
    setVoiceInputEnabledState(enabled);
    try {
      localStorage.setItem('krishi_mitra_voice_input', String(enabled));
    } catch {}
    scheduleBackendSync({ voice_input_enabled: enabled });
  };

  const setSpeechSpeed = (speed: number) => {
    setSpeechSpeedState(speed);
    try {
      localStorage.setItem('krishi_mitra_speech_speed', String(speed));
    } catch {}
    scheduleBackendSync({ speech_speed: speed });
  };

  const syncFromProfile = (profileData: any) => {
    if (!profileData) return;

    if (profileData.theme_preference) {
      setThemeState(profileData.theme_preference as Theme);
    }
    if (profileData.regional_speech_preference) {
      setRegionalDialectState(profileData.regional_speech_preference as RegionalDialect);
    }
    if (profileData.preferred_language) {
      setLanguageState(profileData.preferred_language as Language);
    }
    if (profileData.voice_gender_preference) {
      setVoiceGenderState(profileData.voice_gender_preference as VoiceGender);
    }
    if (profileData.voice_assistant_enabled !== undefined) {
      setVoiceAssistantEnabledState(profileData.voice_assistant_enabled);
    }
    if (profileData.auto_voice_response !== undefined) {
      setAutoVoiceResponseState(profileData.auto_voice_response);
    }
    if (profileData.voice_input_enabled !== undefined) {
      setVoiceInputEnabledState(profileData.voice_input_enabled);
    }
    if (profileData.speech_speed !== undefined) {
      setSpeechSpeedState(profileData.speech_speed);
    }
  };

  const updateSettings = async (partial: Partial<AppSettings>) => {
    if (partial.theme !== undefined) setTheme(partial.theme);
    if (partial.regionalDialect !== undefined) setRegionalDialect(partial.regionalDialect);
    if (partial.voiceGender !== undefined) setVoiceGender(partial.voiceGender);
    if (partial.language !== undefined) setLanguage(partial.language);
    if (partial.voiceAssistantEnabled !== undefined) setVoiceAssistantEnabled(partial.voiceAssistantEnabled);
    if (partial.autoVoiceResponse !== undefined) setAutoVoiceResponse(partial.autoVoiceResponse);
    if (partial.voiceInputEnabled !== undefined) setVoiceInputEnabled(partial.voiceInputEnabled);
    if (partial.speechSpeed !== undefined) setSpeechSpeed(partial.speechSpeed);
  };

  const t = (key: string): string => {
    if (TRANSLATIONS[key]) {
      return TRANSLATIONS[key][language] || TRANSLATIONS[key]['en'] || key;
    }
    return key;
  };

  return (
    <SettingsContext.Provider
      value={{
        theme,
        language,
        regionalDialect,
        voiceGender,
        voiceAssistantEnabled,
        autoVoiceResponse,
        voiceInputEnabled,
        speechSpeed,
        setTheme,
        toggleTheme,
        setRegionalDialect,
        setVoiceGender,
        setLanguage,
        toggleLanguage,
        setVoiceAssistantEnabled,
        setAutoVoiceResponse,
        setVoiceInputEnabled,
        setSpeechSpeed,
        updateSettings,
        syncFromProfile,
        t
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const ctx = useContext(SettingsContext);
  if (!ctx) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return ctx;
};
