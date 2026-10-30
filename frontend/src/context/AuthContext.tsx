import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, FarmerProfile } from '../types';
import { api } from '../services/api';
import { useSettings } from './SettingsContext';

interface AuthContextType {
  user: User | null;
  profile: FarmerProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (mobile: string, pass: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  profile: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  refreshProfile: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('krishi_mitra_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { syncFromProfile } = useSettings();

  const fetchUserData = async () => {
    try {
      if (!localStorage.getItem('krishi_mitra_token')) {
        setUser(null);
        setProfile(null);
        setIsLoading(false);
        return;
      }
      const meData = await api.getMe();
      setUser(meData.user);
      const prof = await api.getFarmerProfile();
      setProfile(prof);
      // Synchronize centralized settings with database preferences
      syncFromProfile(prof);
    } catch (err) {
      console.warn('Session expired or not logged in');
      localStorage.removeItem('krishi_mitra_token');
      setUser(null);
      setProfile(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUserData();
  }, [token]);

  const login = async (mobile: string, pass: string) => {
    const res = await api.login({ mobile, password: pass });
    localStorage.setItem('krishi_mitra_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    if (res.regional_speech) {
      localStorage.setItem('krishi_mitra_dialect', res.regional_speech);
    }
    await fetchUserData();
  };

  const register = async (data: any) => {
    const res = await api.register(data);
    localStorage.setItem('krishi_mitra_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    if (res.regional_speech) {
      localStorage.setItem('krishi_mitra_dialect', res.regional_speech);
    }
    await fetchUserData();
  };

  const logout = () => {
    localStorage.removeItem('krishi_mitra_token');
    setToken(null);
    setUser(null);
    setProfile(null);
  };

  const refreshProfile = async () => {
    await fetchUserData();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
