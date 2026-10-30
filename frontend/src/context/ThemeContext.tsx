import React from 'react';
import { useSettings, Theme } from './SettingsContext';

export type { Theme };

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};

export const useTheme = () => {
  const { theme, toggleTheme, setTheme } = useSettings();
  return { theme, toggleTheme, setTheme };
};
