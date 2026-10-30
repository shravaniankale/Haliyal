import React, { useState } from 'react';
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
  ShieldCheck,
  ChevronDown
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const { language, toggleLanguage, regionalDialect, setRegionalDialect, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dialectDropdownOpen, setDialectDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/schemes?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
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
                ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ
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

          {/* Right Controls: Search, Dialect, Lang, Theme, Profile */}
          <div className="hidden sm:flex items-center gap-2 lg:gap-3">
            
            {/* Quick Scheme Search */}
            <form onSubmit={handleSearchSubmit} className="relative hidden xl:block w-48">
              <input
                type="text"
                placeholder={language === 'kn' ? 'ಯೋಜನೆ ಹುಡುಕಿ...' : 'Search scheme...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-full border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:ring-1 focus:ring-[#2F7650]"
              />
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-[#69766D]" />
            </form>

            {/* Regional Dialect Selector Dropdown */}
            <div className="relative">
              <button
                onClick={() => setDialectDropdownOpen(!dialectDropdownOpen)}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] border border-[#75A96A]/30 hover:border-[#75A96A] transition-colors"
                title="Kannada Regional Dialect"
              >
                <Mic className="w-3.5 h-3.5 text-[#D8AA48]" />
                <span className="hidden md:inline font-kannada">
                  {regionalDialect === 'North Karnataka' ? 'ಉತ್ತರ ಕರ್ನಾಟಕ' : regionalDialect === 'South Karnataka' ? 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ' : 'ಶಿಷ್ಟ ಕನ್ನಡ'}
                </span>
                <ChevronDown className="w-3 h-3" />
              </button>

              {dialectDropdownOpen && (
                <div className="absolute right-0 mt-2 w-52 rounded-xl bg-white dark:bg-[#11221A] border border-[#E2E8DF] dark:border-[#1E382B] shadow-xl py-2 z-50">
                  <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#69766D] dark:text-[#9BB0A4]">
                    ಪ್ರಾದೇಶಿಕ ಕನ್ನಡ ಶೈಲಿ
                  </div>
                  <button
                    onClick={() => {
                      setRegionalDialect('North Karnataka');
                      setDialectDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between font-kannada ${
                      regionalDialect === 'North Karnataka'
                        ? 'bg-[#EAF3E9] dark:bg-[#152E22] font-bold text-[#174C36] dark:text-[#92C987]'
                        : 'text-[#19251E] dark:text-[#EDF3EF] hover:bg-gray-50 dark:hover:bg-[#152E22]/50'
                    }`}
                  >
                    <span>ಉತ್ತರ ಕರ್ನಾಟಕ (ಧಾರವಾಡ/ಬೆಳಗಾವಿ)</span>
                    {regionalDialect === 'North Karnataka' && <span className="text-[#D8AA48]">✓</span>}
                  </button>
                  <button
                    onClick={() => {
                      setRegionalDialect('South Karnataka');
                      setDialectDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between font-kannada ${
                      regionalDialect === 'South Karnataka'
                        ? 'bg-[#EAF3E9] dark:bg-[#152E22] font-bold text-[#174C36] dark:text-[#92C987]'
                        : 'text-[#19251E] dark:text-[#EDF3EF] hover:bg-gray-50 dark:hover:bg-[#152E22]/50'
                    }`}
                  >
                    <span>ದಕ್ಷಿಣ ಕರ್ನಾಟಕ (ಮೈಸೂರು/ಮಂಡ್ಯ)</span>
                    {regionalDialect === 'South Karnataka' && <span className="text-[#D8AA48]">✓</span>}
                  </button>
                  <button
                    onClick={() => {
                      setRegionalDialect('Standard Kannada');
                      setDialectDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between font-kannada ${
                      regionalDialect === 'Standard Kannada'
                        ? 'bg-[#EAF3E9] dark:bg-[#152E22] font-bold text-[#174C36] dark:text-[#92C987]'
                        : 'text-[#19251E] dark:text-[#EDF3EF] hover:bg-gray-50 dark:hover:bg-[#152E22]/50'
                    }`}
                  >
                    <span>ಶಿಷ್ಟ ಕನ್ನಡ (ಸರ್ಕಾರಿ ಅಧಿಕೃತ)</span>
                    {regionalDialect === 'Standard Kannada' && <span className="text-[#D8AA48]">✓</span>}
                  </button>
                </div>
              )}
            </div>

            {/* Language Switch Button */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold border border-[#E2E8DF] dark:border-[#1E382B] text-[#19251E] dark:text-[#EDF3EF] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22] transition-colors"
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

            {/* User Profile / Login */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2">
                <Link
                  to="/profile"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#174C36] text-white hover:bg-[#123B2B] transition-colors shadow-sm"
                >
                  <UserIcon className="w-3.5 h-3.5 text-[#D8AA48]" />
                  <span>{user?.name.split(' ')[0]}</span>
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

          {/* Mobile Hamburger Menu Button */}
          <div className="flex lg:hidden items-center gap-2">
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
        <div className="lg:hidden border-t border-[#E2E8DF] dark:border-[#1E382B] bg-white dark:bg-[#11221A] px-4 pt-3 pb-6 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2.5 rounded-lg text-sm font-medium text-[#19251E] dark:text-[#EDF3EF] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22]"
            >
              {link.label}
            </Link>
          ))}
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
