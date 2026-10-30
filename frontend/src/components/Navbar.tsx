import React, { useState, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  Sprout,
  Search,
  Languages,
  Sun,
  Moon,
  User as UserIcon,
  Menu,
  X,
  Mic,
  Volume2,
  ChevronDown,
  Loader2
} from 'lucide-react';
import { useLanguage, RegionalDialect } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const { language, toggleLanguage, regionalDialect, setRegionalDialect, voiceGender, setVoiceGender, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dialectDropdownOpen, setDialectDropdownOpen] = useState(false);
  const [voiceDropdownOpen, setVoiceDropdownOpen] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/schemes?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  const handleVoicePreview = async (gender: 'female' | 'male', e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      setPreviewLoading(true);
      const voiceId = language === 'en'
        ? (gender === 'male' ? 'en_male' : 'en_female')
        : (gender === 'male' ? 'kn_male' : 'kn_female');
      
      const res = await api.previewVoice(voiceId);
      if (res.audio_url) {
        if (!audioRef.current) {
          audioRef.current = new Audio();
        }
        audioRef.current.src = res.audio_url;
        await audioRef.current.play();
      }
    } catch (err) {
      console.error('Failed to preview voice:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const navLinks = [
    { to: '/', label: t('navHome') },
    { to: '/schemes', label: t('navSchemes') },
    { to: '/eligibility-checker', label: t('navEligibility') },
    { to: '/loans', label: t('navLoans') },
    { to: '/crops', label: t('navCrop') },
    { to: '/fertilizer', label: t('navFertilizer') },
    { to: '/weather-market', label: t('navWeatherMarket') },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#FFFFFF]/95 dark:bg-[#11221A]/95 backdrop-blur-md border-b border-[#E2E8DF] dark:border-[#1E382B] transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Brand Logo & Title */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#174C36] to-[#2F7650] flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform">
              <Sprout className="w-7 h-7 text-[#D8AA48]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl sm:text-2xl tracking-tight text-[#174C36] dark:text-[#75A96A]">
                  KRISHI MITRA
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-[#EAF3E9] dark:bg-[#152E22] text-[#2F7650] dark:text-[#92C987] border border-[#75A96A]/30">
                  AI 2.0
                </span>
              </div>
              <p className="text-xs font-medium text-[#69766D] dark:text-[#9BB0A4] font-kannada">
                {language === 'kn' ? 'ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಧ್ವನಿ ಕೃಷಿ ಸಹಾಯಕ' : 'Your Smart Voice Agricultural Assistant'}
              </p>
            </div>
          </Link>

          {/* Center Navigation Links (Desktop) */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-[#174C36] text-white shadow-sm font-semibold'
                      : 'text-[#19251E] dark:text-[#EDF3EF] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22] hover:text-[#174C36] dark:hover:text-[#75A96A]'
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Right Controls: Search, Dialect, Voice Gender, Lang, Theme, Profile */}
          <div className="hidden sm:flex items-center gap-2 lg:gap-2.5">
            
            {/* Quick Scheme Search */}
            <form onSubmit={handleSearchSubmit} className="relative hidden 2xl:block w-40">
              <input
                type="text"
                placeholder={language === 'kn' ? 'ಯೋಜನೆ ಹುಡುಕಿ...' : 'Search scheme...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-full border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:ring-1 focus:ring-[#2F7650]"
              />
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-[#69766D]" />
            </form>

            {/* Regional Dialect Dropdown */}
            <div className="relative">
              <button
                onClick={() => {
                  setDialectDropdownOpen(!dialectDropdownOpen);
                  setVoiceDropdownOpen(false);
                }}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] border border-[#75A96A]/30 hover:border-[#75A96A] transition-colors"
                title="Dialect / Language Style"
              >
                <Mic className="w-3.5 h-3.5 text-[#D8AA48]" />
                <span className="font-kannada">
                  {regionalDialect === 'North Karnataka'
                    ? (language === 'kn' ? 'ಉತ್ತರ ಕರ್ನಾಟಕ' : 'North KN')
                    : regionalDialect === 'South Karnataka'
                    ? (language === 'kn' ? 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ' : 'South KN')
                    : regionalDialect === 'English'
                    ? 'English'
                    : (language === 'kn' ? 'ಶಿಷ್ಟ ಕನ್ನಡ' : 'Standard KN')}
                </span>
                <ChevronDown className="w-3 h-3" />
              </button>

              {dialectDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white dark:bg-[#11221A] border border-[#E2E8DF] dark:border-[#1E382B] shadow-xl py-2 z-50">
                  <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#69766D] dark:text-[#9BB0A4]">
                    {language === 'kn' ? 'ಪ್ರಾದೇಶಿಕ ಕನ್ನಡ ಶೈಲಿ' : 'Select Regional Dialect'}
                  </div>
                  {[
                    { key: 'North Karnataka', kn: 'ಉತ್ತರ ಕರ್ನಾಟಕ (ಧಾರವಾಡ/ಬೆಳಗಾವಿ)', en: 'North Karnataka (Belagavi/Dharwad)' },
                    { key: 'South Karnataka', kn: 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ (ಮೈಸೂರು/ಮಂಡ್ಯ)', en: 'South Karnataka (Mysuru/Mandya)' },
                    { key: 'Standard Kannada', kn: 'ಶಿಷ್ಟ ಕನ್ನಡ (ಸರ್ಕಾರಿ ಅಧಿಕೃತ)', en: 'Standard Kannada (Formal)' },
                    { key: 'English', kn: 'ಇಂಗ್ಲಿಷ್ (English)', en: 'English' }
                  ].map((d) => (
                    <button
                      key={d.key}
                      onClick={() => {
                        setRegionalDialect(d.key as RegionalDialect);
                        setDialectDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between font-kannada ${
                        regionalDialect === d.key
                          ? 'bg-[#EAF3E9] dark:bg-[#152E22] font-bold text-[#174C36] dark:text-[#92C987]'
                          : 'text-[#19251E] dark:text-[#EDF3EF] hover:bg-gray-50 dark:hover:bg-[#152E22]/50'
                      }`}
                    >
                      <span>{language === 'kn' ? d.kn : d.en}</span>
                      {regionalDialect === d.key && <span className="text-[#D8AA48]">✓</span>}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Voice Gender Selector with Preview */}
            <div className="relative">
              <button
                onClick={() => {
                  setVoiceDropdownOpen(!voiceDropdownOpen);
                  setDialectDropdownOpen(false);
                }}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] border border-[#E2E8DF] dark:border-[#1E382B] hover:border-[#75A96A] transition-colors"
                title="Voice Gender & Preview"
              >
                <Volume2 className="w-3.5 h-3.5 text-[#2F7650] dark:text-[#75A96A]" />
                <span>
                  {voiceGender === 'male'
                    ? (language === 'kn' ? 'ಪುರುಷ ಧ್ವನಿ' : 'Male Voice')
                    : (language === 'kn' ? 'ಮಹಿಳಾ ಧ್ವನಿ' : 'Female Voice')}
                </span>
                <ChevronDown className="w-3 h-3" />
              </button>

              {voiceDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 rounded-xl bg-white dark:bg-[#11221A] border border-[#E2E8DF] dark:border-[#1E382B] shadow-xl py-2 z-50">
                  <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#69766D] dark:text-[#9BB0A4]">
                    {language === 'kn' ? 'ಧ್ವನಿ ಆಯ್ಕೆ ಮತ್ತು ಪ್ರಿವ್ಯೂ' : 'Voice Selection & Preview'}
                  </div>
                  
                  {/* Female Voice Option */}
                  <div className={`px-3 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-[#152E22]/50 cursor-pointer ${voiceGender === 'female' ? 'bg-[#EAF3E9] dark:bg-[#152E22]' : ''}`}>
                    <div 
                      className="flex-1"
                      onClick={() => {
                        setVoiceGender('female');
                        setVoiceDropdownOpen(false);
                      }}
                    >
                      <div className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">
                        {language === 'kn' ? 'ಮಹಿಳಾ ಧ್ವನಿ (ಸ್ವಪ್ನ)' : 'Female Voice (Sapna/Neerja)'}
                      </div>
                      <div className="text-[10px] text-[#69766D] dark:text-[#9BB0A4]">
                        {language === 'kn' ? 'ಸ್ಪಷ್ಟ ಮತ್ತು ವಿನಮ್ರ ಕೃಷಿ ಸಲಹೆ' : 'Warm, clear neural tone'}
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleVoicePreview('female', e)}
                      disabled={previewLoading}
                      title="Preview Female Voice"
                      className="p-1.5 rounded-lg bg-[#174C36]/10 hover:bg-[#174C36]/20 text-[#174C36] dark:text-[#75A96A] transition-colors ml-2"
                    >
                      {previewLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Volume2 className="w-3.5 h-3.5" />}
                    </button>
                  </div>

                  {/* Male Voice Option */}
                  <div className={`px-3 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-[#152E22]/50 cursor-pointer ${voiceGender === 'male' ? 'bg-[#EAF3E9] dark:bg-[#152E22]' : ''}`}>
                    <div 
                      className="flex-1"
                      onClick={() => {
                        setVoiceGender('male');
                        setVoiceDropdownOpen(false);
                      }}
                    >
                      <div className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">
                        {language === 'kn' ? 'ಪುರುಷ ಧ್ವನಿ (ಗಗನ್)' : 'Male Voice (Gagan/Prabhat)'}
                      </div>
                      <div className="text-[10px] text-[#69766D] dark:text-[#9BB0A4]">
                        {language === 'kn' ? 'ಗಂಭೀರ ಅಧಿಕೃತ ಸಲಹೆ' : 'Deep, authoritative neural tone'}
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleVoicePreview('male', e)}
                      disabled={previewLoading}
                      title="Preview Male Voice"
                      className="p-1.5 rounded-lg bg-[#174C36]/10 hover:bg-[#174C36]/20 text-[#174C36] dark:text-[#75A96A] transition-colors ml-2"
                    >
                      {previewLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Volume2 className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Language Switch Button */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-bold border border-[#E2E8DF] dark:border-[#1E382B] text-[#19251E] dark:text-[#EDF3EF] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22] transition-colors"
              title="Change Language"
            >
              <Languages className="w-3.5 h-3.5 text-[#2F7650]" />
              <span>{language === 'kn' ? 'EN' : 'ಕನ್ನಡ'}</span>
            </button>

            {/* Light / Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg border border-[#E2E8DF] dark:border-[#1E382B] text-[#19251E] dark:text-[#EDF3EF] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22] transition-colors"
              title="Toggle Theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-[#D8AA48]" />
              ) : (
                <Moon className="w-4 h-4 text-[#2F7650]" />
              )}
            </button>

            {/* Talk to AI Button */}
            <Link
              to="/voice-assistant"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-[#174C36] hover:bg-[#123B2B] text-white shadow-sm transition-all"
              title="Talk to AI Agricultural Assistant"
            >
              <Mic className="w-3.5 h-3.5 text-[#D8AA48] animate-pulse" />
              <span>{language === 'kn' ? 'ಧ್ವನಿ AI' : 'Talk to AI'}</span>
            </Link>

            {/* User Profile / Login */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2">
                <Link
                  to="/profile"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#174C36] text-white hover:bg-[#123B2B] transition-colors shadow-sm"
                >
                  <UserIcon className="w-3.5 h-3.5 text-[#D8AA48]" />
                  <span>{user?.name?.split(' ')[0] || 'Farmer'}</span>
                </Link>
                <button
                  onClick={logout}
                  className="text-xs text-[#69766D] hover:text-red-600 px-2 py-1"
                >
                  {t('navLogout')}
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-3 py-1.5 text-xs font-semibold text-[#174C36] dark:text-[#75A96A] hover:underline"
                >
                  {t('navLogin')}
                </Link>
                <Link
                  to="/register"
                  className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-[#174C36] text-white hover:bg-[#123B2B] transition-colors shadow-sm"
                >
                  {t('navRegister')}
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Quick Controls & Hamburger Menu Button */}
          <div className="flex lg:hidden items-center gap-2">
            <button
              onClick={() => handleVoicePreview(voiceGender)}
              className="p-2 rounded-lg border border-[#E2E8DF] dark:border-[#1E382B] text-[#2F7650] dark:text-[#75A96A]"
              title="Voice Preview"
            >
              <Volume2 className="w-4 h-4" />
            </button>
            <button
              onClick={toggleLanguage}
              className="p-2 rounded-lg border border-[#E2E8DF] dark:border-[#1E382B] text-xs font-bold"
            >
              {language === 'kn' ? 'EN' : 'ಕನ್ನಡ'}
            </button>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg border border-[#E2E8DF] dark:border-[#1E382B]"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4 text-[#D8AA48]" /> : <Moon className="w-4 h-4 text-[#2F7650]" />}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-[#19251E] dark:text-[#EDF3EF]"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-[#E2E8DF] dark:border-[#1E382B] bg-white dark:bg-[#11221A] px-4 pt-3 pb-6 space-y-3">
          {/* Dialect selector in mobile */}
          <div>
            <label className="text-xs font-semibold text-[#69766D] dark:text-[#9BB0A4] block mb-1">
              {language === 'kn' ? 'ಪ್ರಾದೇಶಿಕ ಶೈಲಿ:' : 'Dialect:'}
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              {[
                { key: 'North Karnataka', label: 'ಉತ್ತರ ಕರ್ನಾಟಕ' },
                { key: 'South Karnataka', label: 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ' },
                { key: 'Standard Kannada', label: 'ಶಿಷ್ಟ ಕನ್ನಡ' },
                { key: 'English', label: 'English' }
              ].map((d) => (
                <button
                  key={d.key}
                  onClick={() => setRegionalDialect(d.key as RegionalDialect)}
                  className={`px-2 py-1.5 text-xs rounded-lg border ${
                    regionalDialect === d.key
                      ? 'bg-[#174C36] text-white border-[#174C36]'
                      : 'border-[#E2E8DF] dark:border-[#1E382B] text-[#19251E] dark:text-[#EDF3EF]'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Voice gender selector in mobile */}
          <div>
            <label className="text-xs font-semibold text-[#69766D] dark:text-[#9BB0A4] block mb-1">
              {language === 'kn' ? 'ಧ್ವನಿ ಲಿಂಗ:' : 'Voice Gender:'}
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              <button
                onClick={() => setVoiceGender('female')}
                className={`px-2 py-1.5 text-xs rounded-lg border ${
                  voiceGender === 'female'
                    ? 'bg-[#174C36] text-white border-[#174C36]'
                    : 'border-[#E2E8DF] dark:border-[#1E382B] text-[#19251E] dark:text-[#EDF3EF]'
                }`}
              >
                {language === 'kn' ? 'ಮಹಿಳಾ ಧ್ವನಿ (ಸ್ವಪ್ನ)' : 'Female (Sapna)'}
              </button>
              <button
                onClick={() => setVoiceGender('male')}
                className={`px-2 py-1.5 text-xs rounded-lg border ${
                  voiceGender === 'male'
                    ? 'bg-[#174C36] text-white border-[#174C36]'
                    : 'border-[#E2E8DF] dark:border-[#1E382B] text-[#19251E] dark:text-[#EDF3EF]'
                }`}
              >
                {language === 'kn' ? 'ಪುರುಷ ಧ್ವನಿ (ಗಗನ್)' : 'Male (Gagan)'}
              </button>
            </div>
          </div>

          {/* Mobile Talk to AI Button */}
          <Link
            to="/voice-assistant"
            onClick={() => setMobileMenuOpen(false)}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#174C36] text-white font-bold text-sm shadow-sm"
          >
            <Mic className="w-4 h-4 text-[#D8AA48] animate-pulse" />
            <span>{language === 'kn' ? 'ಧ್ವನಿ AI ಸಹಾಯಕ (Talk to AI)' : 'Talk to AI Assistant'}</span>
          </Link>

          {/* Nav Links */}
          <div className="pt-2 border-t border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm font-medium text-[#19251E] dark:text-[#EDF3EF] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22]"
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="pt-3 border-t border-[#E2E8DF] dark:border-[#1E382B]">
            {isAuthenticated ? (
              <div className="space-y-2">
                <Link
                  to="/profile"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 text-sm font-semibold text-[#174C36] dark:text-[#75A96A]"
                >
                  {t('navProfile')} ({user?.name})
                </Link>
                <button
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                  }}
                  className="block w-full text-left px-3 py-2 text-sm text-red-600 font-medium"
                >
                  {t('navLogout')}
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2 pt-1">
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-center py-2 text-sm font-semibold border border-[#174C36] rounded-lg text-[#174C36] dark:text-[#75A96A]"
                >
                  {t('navLogin')}
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-center py-2 text-sm font-semibold bg-[#174C36] text-white rounded-lg"
                >
                  {t('navRegister')}
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
