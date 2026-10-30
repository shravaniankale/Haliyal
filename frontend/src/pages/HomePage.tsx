import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Mic,
  Search,
  ArrowRight,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Sprout,
  Landmark,
  BookOpen,
  FlaskConical,
  CloudSun,
  TrendingUp,
  Activity,
  Bug,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  Calendar,
  Clock,
  Droplets,
  Wind,
  Sun,
  AlertTriangle,
  UserCheck,
  FileText,
  ExternalLink,
  Volume2
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import {
  Scheme,
  WeatherData,
  AgriculturalSeasonData,
  CropInsuranceStatus,
  MarketPrice
} from '../types';
import { SchemeCard } from '../components/SchemeCard';

export const HomePage: React.FC = () => {
  const { language, regionalDialect, voiceGender, t } = useLanguage();
  const { user, profile, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Data states
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [stats, setStats] = useState({
    verified_schemes: 3,
    districts_covered: 31,
    service_categories: 8,
    saved_schemes: 0,
  });
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [seasonData, setSeasonData] = useState<AgriculturalSeasonData | null>(null);
  const [insuranceData, setInsuranceData] = useState<CropInsuranceStatus | null>(null);
  const [marketPrices, setMarketPrices] = useState<MarketPrice[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  const activeDistrict = profile?.district || 'Belagavi';
  const activeTaluk = profile?.taluk || 'Belagavi';
  const activeCrop = profile?.primary_crop || (profile?.crops_grown && profile.crops_grown[0]) || 'Paddy';
  const activeLand = profile?.land_acres || 3.0;

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [
          schemesData,
          statsData,
          weatherData,
          seasonInfo,
          insuranceInfo,
          pricesData
        ] = await Promise.all([
          api.getSchemes().catch(() => []),
          api.getSchemeStats().catch(() => ({ verified_schemes: 3, districts_covered: 31, service_categories: 8, saved_schemes: 0 })),
          api.getWeather(activeDistrict, activeTaluk).catch(() => null),
          api.getAgriculturalSeason({ district: activeDistrict, crop: activeCrop }).catch(() => null),
          api.getCropInsuranceStatus({ district: activeDistrict, taluk: activeTaluk, crop: activeCrop, land_acres: activeLand }).catch(() => null),
          api.getMarketPrices(activeCrop, activeDistrict).catch(() => [])
        ]);

        setSchemes(schemesData);
        setStats(statsData);
        if (weatherData) setWeather(weatherData);
        if (seasonInfo) setSeasonData(seasonInfo);
        if (insuranceInfo) setInsuranceData(insuranceInfo);
        setMarketPrices(pricesData.slice(0, 4));
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, [activeDistrict, activeTaluk, activeCrop, activeLand]);

  // Automatic carousel rotation
  useEffect(() => {
    if (schemes.length === 0) return;
    const interval = setInterval(() => {
      setCarouselIndex((prev) => (prev + 1) % schemes.length);
    }, 6000);
    return () => clearInterval(interval);
  }, [schemes]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/schemes?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="space-y-12 sm:space-y-16 pb-16">
      
      {/* 1. HERO SECTION & AI VOICE TRIGGER (Section 9) */}
      <section className="relative overflow-hidden pt-6 sm:pt-12 pb-10 bg-gradient-to-b from-[#EAF3E9]/50 via-transparent to-transparent dark:from-[#11221A]/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            <div className="lg:col-span-7 space-y-5">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#EAF3E9] dark:bg-[#152E22] border border-[#75A96A]/40 text-[#174C36] dark:text-[#92C987] text-xs font-bold shadow-sm">
                <Sparkles className="w-4 h-4 text-[#D8AA48]" />
                <span>AI Agriculture Assistant for Karnataka Farmers • AI 2.0</span>
              </div>

              <div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[#19251E] dark:text-[#EDF3EF] leading-tight">
                  Your Smart Agriculture Assistant
                </h1>
                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#174C36] dark:text-[#75A96A] font-kannada mt-1.5">
                  ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಧ್ವನಿ ಕೃಷಿ ಸಹಾಯಕ
                </h2>
              </div>

              <p className="text-sm sm:text-base text-[#69766D] dark:text-[#9BB0A4] leading-relaxed max-w-2xl">
                {language === 'kn'
                  ? 'ಕನ್ನಡದಲ್ಲೇ ಮಾತನಾಡಿ ಸರ್ಕಾರಿ ಸಬ್ಸಿಡಿ, ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಸಾಲ, ಬೆಳೆ ವಿಮೆ ಮತ್ತು ಹವಾಮಾನ ಸಲಹೆ ಪಡೆಯಿರಿ.'
                  : 'Speak naturally in North Karnataka, South Karnataka, or Standard Kannada for verified government schemes, crop insurance, and personalized farming guidance.'}
              </p>

              {/* Search Bar */}
              <form onSubmit={handleSearchSubmit} className="relative max-w-xl">
                <input
                  type="text"
                  placeholder="ಯೋಜನೆ ಹೆಸರು, ಬೆಳೆ (ಉದಾ. ಭತ್ತ, ಜೋಳ) ಅಥವಾ ಸಬ್ಸಿಡಿ ಹುಡುಕಿ..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-11 pr-24 py-3 text-xs sm:text-sm rounded-2xl border-2 border-[#E2E8DF] dark:border-[#1E382B] bg-white dark:bg-[#11221A] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650] shadow-sm font-kannada"
                />
                <Search className="w-4 h-4 absolute left-4 top-3.5 text-[#69766D]" />
                <button
                  type="submit"
                  className="absolute right-1.5 top-1.5 bottom-1.5 px-4 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white text-xs font-bold transition-colors shadow"
                >
                  ಹುಡುಕಿ
                </button>
              </form>

              {/* Hero Voice CTAs */}
              <div className="flex flex-wrap items-center gap-3 pt-1">
                <Link
                  to="/voice-assistant"
                  className="px-5 py-3 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white font-bold text-xs sm:text-sm shadow-md hover:shadow-lg transition-all flex items-center gap-2 group"
                >
                  <Mic className="w-4 h-4 text-[#D8AA48] animate-pulse" />
                  <span>ಧ್ವನಿ ಮೂಲಕ ಮಾತನಾಡಿ (Talk to AI)</span>
                </Link>

                <Link
                  to="/schemes"
                  className="px-5 py-3 rounded-xl bg-white dark:bg-[#11221A] border border-[#174C36] dark:border-[#75A96A] text-[#174C36] dark:text-[#92C987] font-bold text-xs sm:text-sm hover:bg-[#EAF3E9] dark:hover:bg-[#152E22] transition-colors flex items-center gap-2 shadow-sm"
                >
                  <Landmark className="w-4 h-4 text-[#D8AA48]" />
                  <span>ಯೋಜನೆಗಳು (Schemes)</span>
                </Link>
              </div>

              {/* Active Voice Pill */}
              <div className="flex items-center gap-2 text-xs text-[#69766D] dark:text-[#9BB0A4]">
                <CheckCircle className="w-4 h-4 text-[#2F7650]" />
                <span className="font-kannada">
                  ಸಕ್ರಿಯ ಧ್ವನಿ: <strong className="text-[#174C36] dark:text-[#75A96A]">{voiceGender === 'male' ? 'Gagan (ಪುರುಷ)' : 'Sapna (ಮಹಿಳೆ)'}</strong> • ಶೈಲಿ: <strong className="text-[#174C36] dark:text-[#75A96A]">{regionalDialect}</strong>
                </span>
              </div>
            </div>

            {/* Right Column: Hero Visual with Real Farmer */}
            <div className="lg:col-span-5 relative">
              <div className="relative rounded-3xl overflow-hidden shadow-xl border-4 border-white dark:border-[#1E382B]">
                <img
                  src="https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=900&q=80"
                  alt="Karnataka Farmer in lush agricultural field"
                  className="w-full h-[380px] object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>

                <div className="absolute bottom-4 left-4 right-4 p-3.5 rounded-2xl bg-white/95 dark:bg-[#11221A]/95 backdrop-blur-md border border-[#E2E8DF] dark:border-[#1E382B] shadow-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-9 h-9 rounded-full bg-[#174C36] flex items-center justify-center text-white">
                        <Mic className="w-4 h-4 text-[#D8AA48]" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                          "ನನಗೆ ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಯ ಬೆಳೆ ಸಾಲ ಮತ್ತು ಸಬ್ಸಿಡಿ ತಿಳಿಸಿ"
                        </p>
                        <p className="text-[10px] text-[#2F7650] dark:text-[#92C987] font-semibold">
                          ಕನ್ನಡ ನೈಜ ನರಮಂಡಲ ಧ್ವನಿ ಸಕ್ರಿಯ
                        </p>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] text-[10px] font-bold">
                      Neural TTS
                    </span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 2. SECTION 1: FARMER PROFILE SUMMARY CARD */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-5 sm:p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#EAF3E9] dark:bg-[#152E22] flex items-center justify-center text-[#174C36] dark:text-[#75A96A]">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-base text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                  {isAuthenticated ? `ರೈತ ಪ್ರೊಫೈಲ್ ಸಾರಾಂಶ (${profile?.name || user?.name || 'ರೈತ ಮಿತ್ರ'})` : 'ಕೃಷಿ ಪ್ರೊಫೈಲ್ ಸಾರಾಂಶ (Farmer Agricultural Profile)'}
                </h3>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                  {isAuthenticated ? 'ಖಚಿತಪಡಿಸಿದ ವಿವರಗಳ ಆಧಾರದ ಮೇಲೆ ವೈಯಕ್ತಿಕಗೊಳಿಸಿದ ಯೋಜನೆಗಳು ಮತ್ತು ಬೆಳೆ ಸಲಹೆ' : 'ಲಾಗಿನ್ ಮಾಡಿ ಅಥವಾ AI ಸಂವಾದದ ಮೂಲಕ ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಉಳಿಸಿ'}
                </p>
              </div>
            </div>

            <Link
              to="/profile"
              className="text-xs font-bold text-[#174C36] dark:text-[#75A96A] hover:underline flex items-center gap-1"
            >
              <span>ಪ್ರೊಫೈಲ್ ಸಂಪಾದಿಸಿ (Edit Profile)</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="p-3 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B]">
              <span className="text-[10px] uppercase font-bold text-[#69766D] dark:text-[#9BB0A4]">ಜಿಲ್ಲೆ & ತಾಲೂಕು</span>
              <p className="font-bold text-xs sm:text-sm text-[#174C36] dark:text-[#75A96A] font-kannada mt-0.5">
                {activeDistrict}, {activeTaluk}
              </p>
            </div>

            <div className="p-3 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B]">
              <span className="text-[10px] uppercase font-bold text-[#69766D] dark:text-[#9BB0A4]">ಮುಖ್ಯ ಬೆಳೆ</span>
              <p className="font-bold text-xs sm:text-sm text-[#174C36] dark:text-[#75A96A] font-kannada mt-0.5">
                {activeCrop}
              </p>
            </div>

            <div className="p-3 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B]">
              <span className="text-[10px] uppercase font-bold text-[#69766D] dark:text-[#9BB0A4]">ಜಮೀನು ವಿಸ್ತೀರ್ಣ</span>
              <p className="font-bold text-xs sm:text-sm text-[#174C36] dark:text-[#75A96A] font-kannada mt-0.5">
                {activeLand} {profile?.land_unit || 'ಎಕರೆ'}
              </p>
            </div>

            <div className="p-3 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B]">
              <span className="text-[10px] uppercase font-bold text-[#69766D] dark:text-[#9BB0A4]">ನೀರಾವರಿ & ಮಾಲೀಕತ್ವ</span>
              <p className="font-bold text-xs sm:text-sm text-[#174C36] dark:text-[#75A96A] font-kannada mt-0.5">
                {profile?.irrigation_type || 'Rainfed'} • {profile?.land_ownership || 'Own'}
              </p>
            </div>

            <div className="p-3 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B]">
              <span className="text-[10px] uppercase font-bold text-[#69766D] dark:text-[#9BB0A4]">ರೈತ ವರ್ಗ</span>
              <p className="font-bold text-xs sm:text-sm text-[#174C36] dark:text-[#75A96A] font-kannada mt-0.5">
                {profile?.farmer_category || 'Small & Marginal'}
              </p>
            </div>

            <div className="p-3 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B]">
              <span className="text-[10px] uppercase font-bold text-[#69766D] dark:text-[#9BB0A4]">ಆಯ್ಕೆಯ ಧ್ವನಿ & ಶೈಲಿ</span>
              <p className="font-bold text-xs text-[#174C36] dark:text-[#75A96A] font-kannada mt-0.5 truncate">
                {voiceGender === 'male' ? 'Gagan (ಪುರುಷ)' : 'Sapna (ಮಹಿಳೆ)'} • {regionalDialect.split(' ')[0]}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. SECTION 2: LIVE WEATHER INTELLIGENCE & 5-DAY AGRONOMIC FORECAST */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-5 sm:p-6 shadow-sm space-y-5">
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-amber-50 dark:bg-amber-950/40 flex items-center justify-center text-amber-600">
                <CloudSun className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-base text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                    {weather?.location_display || activeDistrict} ಲೈವ್ ಹವಾಮಾನ ಮತ್ತು ಕೃಷಿ ಮುನ್ಸೂಚನೆ
                  </h3>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1 ${
                    weather?.is_live
                      ? 'bg-green-100 text-green-800 dark:bg-green-950/50 dark:text-green-300'
                      : 'bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300'
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${weather?.is_live ? 'bg-green-600 animate-pulse' : 'bg-amber-600'}`}></span>
                    <span>{weather?.is_live ? 'Live Data (Open-Meteo)' : 'Cached Offline'}</span>
                  </span>
                </div>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                  High-resolution numerical weather prediction for agricultural operations
                </p>
              </div>
            </div>

            <div className="text-right text-xs text-[#69766D] dark:text-[#9BB0A4]">
              <span>ನವೀಕರಣ: </span>
              <span className="font-semibold">{weather?.last_updated || 'Just now'}</span>
            </div>
          </div>

          {/* Current Conditions & Key Agronomic Alerts */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            
            {/* Current Metrics (4 cols) */}
            <div className="md:col-span-4 p-4 rounded-2xl bg-gradient-to-br from-[#EAF3E9]/60 to-[#F7F9F5] dark:from-[#152E22]/40 dark:to-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-3xl font-extrabold text-[#174C36] dark:text-[#75A96A]">
                    {weather?.temperature || 28}°C
                  </span>
                  <p className="text-xs font-semibold text-[#19251E] dark:text-[#EDF3EF] font-kannada mt-0.5">
                    {weather?.condition_kn || 'ಸ್ವಚ್ಛ ಆಕಾಶ'} ({weather?.condition || 'Clear'})
                  </p>
                </div>
                <span className="text-4xl">{weather?.icon || '🌤️'}</span>
              </div>

              <div className="grid grid-cols-3 gap-2 pt-4 border-t border-[#E2E8DF] dark:border-[#1E382B] text-center">
                <div>
                  <div className="flex items-center justify-center gap-1 text-[#69766D] text-[10px]">
                    <Droplets className="w-3 h-3 text-blue-500" />
                    <span>ಆರ್ದ್ರತೆ</span>
                  </div>
                  <span className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">{weather?.humidity || 65}%</span>
                </div>

                <div>
                  <div className="flex items-center justify-center gap-1 text-[#69766D] text-[10px]">
                    <Wind className="w-3 h-3 text-teal-500" />
                    <span>ಗಾಳಿ</span>
                  </div>
                  <span className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">{weather?.wind_speed || 12} km/h</span>
                </div>

                <div>
                  <div className="flex items-center justify-center gap-1 text-[#69766D] text-[10px]">
                    <CloudSun className="w-3 h-3 text-amber-500" />
                    <span>ಮಳೆ ಪ್ರಮಾಣ</span>
                  </div>
                  <span className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">{weather?.precipitation || 0} mm</span>
                </div>
              </div>
            </div>

            {/* Agronomic Spraying & Irrigation Feasibility (8 cols) */}
            <div className="md:col-span-8 grid grid-cols-1 sm:grid-cols-2 gap-3">
              
              {/* Spraying window */}
              <div className="p-3.5 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#174C36] dark:text-[#75A96A] font-kannada">
                    ಕೀಟನಾಶಕ ಸಿಂಪಡಣಾ ಮುನ್ಸೂಚನೆ (Spraying Window)
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300">
                    ಅನುಕೂಲಕರ
                  </span>
                </div>
                <p className="text-xs text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-relaxed">
                  {weather?.spraying_advisory_kn || 'ಇಂದು ಪೋಷಕಾಂಶ ಮತ್ತು ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆಗೆ ಸೂಕ್ತ ವಾತಾವರಣವಿದೆ.'}
                </p>
                <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">
                  {weather?.spraying_advisory_en || 'Safe spraying window with moderate wind.'}
                </p>
              </div>

              {/* Irrigation advice */}
              <div className="p-3.5 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#174C36] dark:text-[#75A96A] font-kannada">
                    ನೀರಾವರಿ ಸಲಹೆ (Irrigation Advisory)
                  </span>
                  <Droplets className="w-3.5 h-3.5 text-blue-500" />
                </div>
                <p className="text-xs text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-relaxed">
                  {weather?.irrigation_advisory_kn || 'ಮಳೆಯ ಸಾಧ್ಯತೆ ಕಡಿಮೆ ಇರುವುದರಿಂದ ಸಂಜೆ ವೇಳೆಗೆ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಿ.'}
                </p>
                <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">
                  {weather?.irrigation_advisory_en || 'Low precipitation expected. Provide light evening irrigation.'}
                </p>
              </div>

              {/* Weather Alerts if any */}
              {weather?.alerts && weather.alerts.length > 0 && (
                <div className="sm:col-span-2 p-3 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-center gap-2 text-xs font-semibold text-amber-900 dark:text-amber-200 font-kannada">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>{weather.alerts[0]}</span>
                </div>
              )}

            </div>
          </div>

          {/* 5-Day Forecast Row */}
          {weather?.forecast_5_days && weather.forecast_5_days.length > 0 && (
            <div className="pt-2 border-t border-[#E2E8DF] dark:border-[#1E382B]">
              <span className="text-xs font-bold uppercase tracking-wider text-[#69766D] dark:text-[#9BB0A4] block mb-2 font-kannada">
                ಮುಂದಿನ ೫ ದಿನಗಳ ಕೃಷಿ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ (5-Day Forecast):
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {weather.forecast_5_days.map((day, idx) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] text-center">
                    <p className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">{day.day_name}</p>
                    <span className="text-2xl my-1 block">{day.icon}</span>
                    <p className="text-xs font-extrabold text-[#174C36] dark:text-[#75A96A]">{day.temp_max}° / {day.temp_min}°</p>
                    <p className="text-[10px] text-blue-600 font-semibold mt-0.5">ಮಳೆ: {day.rain_probability}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </section>

      {/* 4. SECTION 3: CURRENT AGRICULTURAL SEASON & KARNATAKA CROP CALENDAR */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-5 sm:p-6 shadow-sm space-y-4">
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#EAF3E9] dark:bg-[#152E22] flex items-center justify-center text-[#174C36] dark:text-[#75A96A]">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-base text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                    ಪ್ರಸ್ತುತ ಕೃಷಿ ಋತುಮಾನ ಮತ್ತು ಬೆಳೆ ಕ್ಯಾಲೆಂಡರ್ ({seasonData?.current_season_kn || 'ಮುಂಗಾರು-ಹಿಂಗಾರು ಸಂಕ್ರಮಣ'})
                  </h3>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#75A96A]">
                    {seasonData?.timezone || 'Asia/Kolkata'}
                  </span>
                </div>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                  {seasonData?.current_date ? `ಇಂದಿನ ದಿನಾಂಕ: ${seasonData.current_date} • ${seasonData.season_phase}` : 'Dynamic Karnataka Crop Calendar'}
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Kharif */}
            <div className="p-3.5 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                  ಖಾರೀಫ್ / ಮುಂಗಾರು (Kharif)
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-bold">
                  ಕೊಯ್ಲು ಹಂತ (Harvesting)
                </span>
              </div>
              <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">ಜೂನ್ - ಅಕ್ಟೋಬರ್ (June - October)</p>
              <p className="text-xs font-semibold text-[#174C36] dark:text-[#75A96A] font-kannada pt-1">
                ಭತ್ತ, ಮೆಕ್ಕೆಜೋಳ, ಹತ್ತಿ, ಶೇಂಗಾ ಕೊಯ್ಲು ಮತ್ತು ದಾಸ್ತಾನು ಸಿದ್ಧತೆ.
              </p>
            </div>

            {/* Rabi */}
            <div className="p-3.5 rounded-2xl bg-[#EAF3E9]/50 dark:bg-[#152E22]/30 border border-[#75A96A]/40 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-[#174C36] dark:text-[#92C987] font-kannada">
                  ರಬಿ / ಹಿಂಗಾರು (Rabi)
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300 font-bold">
                  ಪ್ರಸ್ತುತ ಬಿತ್ತನೆ (Sowing Window)
                </span>
              </div>
              <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">ಅಕ್ಟೋಬರ್ - ಮಾರ್ಚ್ (October - March)</p>
              <p className="text-xs font-semibold text-[#174C36] dark:text-[#75A96A] font-kannada pt-1">
                ಹಿಂಗಾರು ಜೋಳ, ಕಡಲೆ, ಗೋಧಿ ಹಾಗೂ ಎಣ್ಣೆಕಾಳುಗಳ ಬಿತ್ತನೆಗೆ ಅತ್ಯಂತ ಸೂಕ್ತ ಸಮಯ.
              </p>
            </div>

            {/* Summer */}
            <div className="p-3.5 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                  ಬೇಸಿಗೆ / ಗರಿಷ್ಟ (Summer)
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 font-bold">
                  ಯೋಜನೆ (Upcoming)
                </span>
              </div>
              <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">ಜನವರಿ - ಮೇ (January - May)</p>
              <p className="text-xs font-semibold text-[#174C36] dark:text-[#75A96A] font-kannada pt-1">
                ನೀರಾವರಿ ಸೌಲಭ್ಯವಿರುವ ಪ್ರದೇಶಗಳಲ್ಲಿ ತರಕಾರಿ ಹಾಗೂ ಕಲ್ಲಂಗಡಿ ಬೆಳೆಗಳು.
              </p>
            </div>
          </div>

          {/* Extension Advisory Bulletin */}
          <div className="p-3.5 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] flex items-start gap-3">
            <Sprout className="w-5 h-5 text-[#2F7650] shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-relaxed">
                {seasonData?.advisory_bulletin_kn || 'ಮುಂಗಾರು ಬೆಳೆಗಳ ಕೊಯ್ಲು ಮುಗಿದ ನಂತರ ತಕ್ಷಣವೇ ಹಿಂಗಾರು ಬಿತ್ತನೆಗೆ ಮಣ್ಣಿನ ತೇವಾಂಶ ಸಂರಕ್ಷಣೆ ಮಾಡಿ.'}
              </p>
              <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">
                {seasonData?.advisory_bulletin || 'Conserve residual soil moisture immediately after Kharif harvest for successful Rabi sowing.'}
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* 5. SECTION 4: GOVERNMENT SCHEME RECOMMENDATIONS (RAG Grounded) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-6 gap-3">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
              <ShieldCheck className="w-4 h-4 text-[#2F7650]" />
              <span>Official Database & RAG Citations</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] mt-1 font-kannada">
              ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಕೃಷಿ ಯೋಜನೆಗಳು (Government Schemes)
            </h2>
            <p className="text-xs sm:text-sm text-[#69766D] dark:text-[#9BB0A4]">
              Verified Central and Karnataka State schemes with deterministic eligibility rules & document citations
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCarouselIndex((prev) => (prev - 1 + schemes.length) % schemes.length)}
              className="p-2 rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22]"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCarouselIndex((prev) => (prev + 1) % schemes.length)}
              className="p-2 rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22]"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <Link
              to="/schemes"
              className="ml-2 text-xs font-bold text-[#174C36] dark:text-[#75A96A] hover:underline flex items-center gap-1"
            >
              <span>ಎಲ್ಲಾ ಯೋಜನೆಗಳು ({schemes.length})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Scheme Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemes.slice(0, 3).map((scheme) => (
            <SchemeCard key={scheme.scheme_id} scheme={scheme} />
          ))}
        </div>
      </section>

      {/* 6. SECTION 5: CROP INSURANCE INTELLIGENCE (PMFBY & Samrakshane) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-5 sm:p-6 shadow-sm space-y-4">
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-blue-50 dark:bg-blue-950/40 flex items-center justify-center text-blue-600">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-base text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                    ಬೆಳೆ ವಿಮೆ ಮಾರ್ಗದರ್ಶನ (PMFBY & ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್)
                  </h3>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
                    Notified Crop Status
                  </span>
                </div>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                  Official Karnataka Samrakshane crop insurance verification and claim rules
                </p>
              </div>
            </div>

            <a
              href="https://samrakshane.karnataka.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-bold text-blue-600 hover:underline flex items-center gap-1"
            >
              <span>ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್ ತೆರೆಯಿರಿ</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* Status Card */}
            <div className="p-4 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-2">
              <span className="text-[10px] uppercase font-bold text-[#69766D]">ಅಧಿಸೂಚಿತ ಬೆಳೆ ವಿವರ (Notified Status)</span>
              <p className="font-bold text-sm text-[#174C36] dark:text-[#75A96A] font-kannada">
                {activeCrop} ಬೆಳೆ {activeDistrict} ಜಿಲ್ಲೆಗೆ ಅಧಿಸೂಚಿತವಾಗಿದೆ.
              </p>
              <div className="text-xs space-y-1 text-[#69766D] dark:text-[#9BB0A4]">
                <p>ರೈತರ ಪ್ರೀಮಿಯಂ ದರ: <strong className="text-[#19251E] dark:text-[#EDF3EF]">{insuranceData?.farmer_premium_rate || '2.0%'}</strong></p>
                <p>ಅಂದಾಜು ಪ್ರೀಮಿಯಂ ಮೊತ್ತ: <strong className="text-[#19251E] dark:text-[#EDF3EF]">{insuranceData?.farmer_premium_amount_approx || '₹600 - ₹900 / acre'}</strong></p>
              </div>
            </div>

            {/* 72-Hour Calamity Rule (Crucial Requirement) */}
            <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-amber-900 dark:text-amber-200 font-kannada">
                  ೭೨ ಗಂಟೆಗಳ ನಷ್ಟ ಮಾಹಿತಿ ನಿಯಮ (72-Hour Rule)
                </span>
                <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-red-600 text-white">ಕಡ್ಡಾಯ</span>
              </div>
              <p className="text-xs text-amber-900 dark:text-amber-200 font-kannada leading-relaxed">
                ಆಲಿಕಲ್ಲು ಮಳೆ, ಪ್ರವಾಹ ಅಥವಾ ಭೂಕುಸಿತದಿಂದ ಬೆಳೆ ಹಾನಿಯಾದರೆ <strong>೭೨ ಗಂಟೆಗಳ ಒಳಗಾಗಿ</strong> ಸಂರಕ್ಷಣೆ ಸಹಾಯವಾಣಿ ಅಥವಾ ಬ್ಯಾಂಕ್‌ಗೆ ಮಾಹಿತಿ ನೀಡುವುದು ಕಡ್ಡಾಯ.
              </p>
              <p className="text-[11px] text-amber-800 dark:text-amber-300 font-bold">
                ಸಹಾಯವಾಣಿ (Toll-Free Helpline): 1800-425-3553
              </p>
            </div>

            {/* Documents Checklist */}
            <div className="p-4 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-2">
              <span className="text-[10px] uppercase font-bold text-[#69766D]">ಅರ್ಜಿಗೆ ಬೇಕಾದ ದಾಖಲೆಗಳು (Documents)</span>
              <ul className="text-xs space-y-1 font-kannada text-[#19251E] dark:text-[#EDF3EF]">
                <li>✓ ಪಹಣಿ / ಆರ್‌ಟಿಸಿ (RTC Extract)</li>
                <li>✓ ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್ ಮತ್ತು ಆಧಾರ್ ಕಾರ್ಡ್</li>
                <li>✓ ಗ್ರಾಮ ಆಡಳಿತಾಧಿಕಾರಿ ನೀಡಿದ ಬಿತ್ತನೆ ದೃಢೀಕರಣ</li>
              </ul>
            </div>

          </div>
        </div>
      </section>

      {/* 7. SECTION 6 & 7: PERSONALIZED CROP & FERTILIZER GUIDANCE */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Crop Guidance Card */}
          <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-5 sm:p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E8DF] dark:border-[#1E382B] pb-3">
              <div className="flex items-center gap-2.5">
                <Sprout className="w-5 h-5 text-[#2F7650]" />
                <h3 className="font-bold text-base text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                  {activeCrop} ಬೆಳೆ ಸಮಗ್ರ ಮಾರ್ಗದರ್ಶನ (Crop Advisory)
                </h3>
              </div>
              <Link to="/crops" className="text-xs font-bold text-[#174C36] dark:text-[#75A96A] hover:underline">
                ವಿವರ ನೋಡಿ
              </Link>
            </div>

            <div className="space-y-2 text-xs leading-relaxed font-kannada text-[#19251E] dark:text-[#EDF3EF]">
              <p>• <strong>ಬೆಳವಣಿಗೆ ಹಂತ:</strong> ಕೊಯ್ಲು ಮತ್ತು ತೆನೆ ತುಂಬುವ ಹಂತ (Grain Filling / Harvesting)</p>
              <p>• <strong>ನೀರಾವರಿ ನಿಯಂತ್ರಣ:</strong> ಕೊಯ್ಲಿಗೆ ೧೦-೧೫ ದಿನ ಮುಂಚಿತವಾಗಿ ಗದ್ದೆಯಿಂದ ನೀರನ್ನು ಹೊರಹಾಕಿ.</p>
              <p>• <strong>ಕೀಟ ನಿರ್ವಹಣೆ:</strong> ಕಂದು ಜಿಗಿ ಹುಳು (BPH) ಹತೋಟಿಗೆ ಗದ್ದೆಯಲ್ಲಿ ಗಾಳಿಯಾಡುವಂತೆ ಸಾಲು ತೆರೆಯಿರಿ.</p>
            </div>
          </div>

          {/* Fertilizer Guidance Card */}
          <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-5 sm:p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E8DF] dark:border-[#1E382B] pb-3">
              <div className="flex items-center gap-2.5">
                <FlaskConical className="w-5 h-5 text-[#2F7650]" />
                <h3 className="font-bold text-base text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                  ವೈಜ್ಞಾನಿಕ ರಸಗೊಬ್ಬರ & ಪೋಷಕಾಂಶ ಸಲಹೆ
                </h3>
              </div>
              <Link to="/fertilizer" className="text-xs font-bold text-[#174C36] dark:text-[#75A96A] hover:underline">
                ಲೆಕ್ಕಾಚಾರ
              </Link>
            </div>

            <div className="space-y-2 text-xs leading-relaxed font-kannada text-[#19251E] dark:text-[#EDF3EF]">
              <p>• <strong>ಶಿಫಾರಸು ಎನ್‌ಪಿಕೆ ಅನುಪಾತ:</strong> ೧೦೦:೫೦:೫೦ ಕಿ.ಗ್ರಾಂ/ಹೆಕ್ಟೇರ್ (NPK Split)</p>
              <p>• <strong>ಪೋಷಕಾಂಶ ನಿರ್ವಹಣೆ:</strong> ಸಾರಜನಕವನ್ನು ಒಂದೇ ಬಾರಿ ಹಾಕದೆ ೩ ಹಂತಗಳಲ್ಲಿ ವಿಭಜಿಸಿ ಹಾಕಿರಿ.</p>
              <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4] italic">
                * ಗಮನಿಸಿ: ನಿಖರ ಗೊಬ್ಬರ ಪ್ರಮಾಣಕ್ಕೆ ನಿಮ್ಮ ಸಮೀಪದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರದಲ್ಲಿ ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮಾಡಿಸಿಕೊಳ್ಳಿ (Soil Health Card).
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* 8. SECTION 8: APMC MANDI MARKET COMMODITY PRICES */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-5 sm:p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-[#E2E8DF] dark:border-[#1E382B] pb-3">
            <div className="flex items-center gap-2.5">
              <Activity className="w-5 h-5 text-[#2F7650]" />
              <div>
                <h3 className="font-bold text-base text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                  ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಮಂಡಿ ಧಾರಣೆ (APMC Market Prices)
                </h3>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                  Official modal rates recorded across Karnataka agricultural markets
                </p>
              </div>
            </div>
            <Link to="/weather-market" className="text-xs font-bold text-[#174C36] dark:text-[#75A96A] hover:underline">
              ಎಲ್ಲಾ ಮಾರುಕಟ್ಟೆಗಳು ({marketPrices.length}+)
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {marketPrices.map((m, idx) => (
              <div key={idx} className="p-3 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-[#174C36] dark:text-[#75A96A] font-kannada">{m.crop_kn || m.crop}</span>
                  <span className="text-[10px] text-[#69766D]">{m.market}</span>
                </div>
                <p className="text-lg font-extrabold text-[#19251E] dark:text-[#EDF3EF]">
                  ₹{m.modal_price} <span className="text-xs font-normal text-[#69766D]">/ {m.unit || 'ಕ್ವಿಂಟಾಲ್'}</span>
                </p>
                <p className="text-[10px] text-[#69766D]">ಕನಿಷ್ಠ: ₹{m.min_price} • ಗರಿಷ್ಠ: ₹{m.max_price}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
};
