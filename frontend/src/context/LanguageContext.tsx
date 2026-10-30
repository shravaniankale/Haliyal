import React from 'react';
import { useSettings, Language, RegionalDialect, VoiceGender } from './SettingsContext';

export type { Language, RegionalDialect, VoiceGender };

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};

export const useLanguage = () => {
  const settings = useSettings();
  return {
    language: settings.language,
    setLanguage: settings.setLanguage,
    toggleLanguage: settings.toggleLanguage,
    regionalDialect: settings.regionalDialect,
    setRegionalDialect: settings.setRegionalDialect,
    voiceGender: settings.voiceGender,
    setVoiceGender: settings.setVoiceGender,
    speechSpeed: settings.speechSpeed,
    setSpeechSpeed: settings.setSpeechSpeed,
    autoVoiceResponse: settings.autoVoiceResponse,
    setAutoVoiceResponse: settings.setAutoVoiceResponse,
    voiceInputEnabled: settings.voiceInputEnabled,
    setVoiceInputEnabled: settings.setVoiceInputEnabled,
    voiceAssistantEnabled: settings.voiceAssistantEnabled,
    setVoiceAssistantEnabled: settings.setVoiceAssistantEnabled,
    t: settings.t,
  };
};
