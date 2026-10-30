import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'kn' | 'en';
type RegionalDialect = 'North Karnataka' | 'South Karnataka' | 'Standard Kannada';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  regionalDialect: RegionalDialect;
  setRegionalDialect: (dialect: RegionalDialect) => void;
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
    kn: 'ಕನ್ನಡ ಧ್ವನಿ ಸಂವಾದದ ಮೂಲಕ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಕೃಷಿ ಸಾಲಗಳು, ಮತ್ತು ನಿಖರ ಬೆಳೆ ಮಾಹಿತಿಯನ್ನು ಸುಲಭವಾಗಿ ಪಡೆಯಿರಿ.',
    en: 'Discover government schemes, agricultural loans and farming guidance through intelligent Kannada voice assistance.'
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
};

const LanguageContext = createContext<LanguageContextType>({
  language: 'kn',
  setLanguage: () => {},
  toggleLanguage: () => {},
  regionalDialect: 'North Karnataka',
  setRegionalDialect: () => {},
  t: (key: string) => key,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('krishi_mitra_lang');
    return (saved as Language) || 'kn';
  });

  const [regionalDialect, setRegionalDialectState] = useState<RegionalDialect>(() => {
    const saved = localStorage.getItem('krishi_mitra_dialect');
    return (saved as RegionalDialect) || 'North Karnataka';
  });

  const setLanguage = (lang: Language) => {
    localStorage.setItem('krishi_mitra_lang', lang);
    setLanguageState(lang);
  };

  const toggleLanguage = () => {
    const next = language === 'kn' ? 'en' : 'kn';
    setLanguage(next);
  };

  const setRegionalDialect = (dialect: RegionalDialect) => {
    localStorage.setItem('krishi_mitra_dialect', dialect);
    setRegionalDialectState(dialect);
  };

  const t = (key: string): string => {
    if (TRANSLATIONS[key]) {
      return TRANSLATIONS[key][language] || TRANSLATIONS[key]['en'] || key;
    }
    return key;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        toggleLanguage,
        regionalDialect,
        setRegionalDialect,
        t,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
