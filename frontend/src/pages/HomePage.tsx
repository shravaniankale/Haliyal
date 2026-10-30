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
  ChevronRight
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import { Scheme } from '../types';
import { SchemeCard } from '../components/SchemeCard';

export const HomePage: React.FC = () => {
  const { language, t } = useLanguage();
  const navigate = useNavigate();

  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [stats, setStats] = useState({
    verified_schemes: 3,
    districts_covered: 31,
    service_categories: 8,
    saved_schemes: 0,
  });
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [schemesData, statsData] = await Promise.all([
          api.getSchemes(),
          api.getSchemeStats(),
        ]);
        setSchemes(schemesData);
        setStats(statsData);
      } catch (err) {
        console.error('Failed to load homepage data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Automatic carousel rotation every 5 seconds
  useEffect(() => {
    if (schemes.length === 0) return;
    const interval = setInterval(() => {
      setCarouselIndex((prev) => (prev + 1) % schemes.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [schemes]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/schemes?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const services = [
    {
      title: language === 'kn' ? 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು' : 'Government Schemes',
      desc: language === 'kn' ? 'ಪಿಎಂ-ಕಿಸಾನ್, ಕೃಷಿ ಭಾಗ್ಯ, ಬೆಳೆ ವಿಮೆ ಯೋಜನೆಗಳ ನಿಖರ ಪರಿಶೀಲನೆ.' : 'Transparent scheme search with deterministic eligibility rules.',
      icon: <Landmark className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/schemes',
      badge: '100% Verified',
    },
    {
      title: language === 'kn' ? 'ಕೃಷಿ ಸಾಲಗಳು & KCC' : 'Agriculture Loans',
      desc: language === 'kn' ? 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್, ಯಂತ್ರೋಪಕರಣ ಸಾಲ ಹಾಗೂ ಇಎಂಐ ಲೆಕ್ಕಾಚಾರ.' : 'Kisan Credit Card info, interest subsidies, and instant EMI calculator.',
      icon: <TrendingUp className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/loans',
      badge: '4% Subsidized',
    },
    {
      title: language === 'kn' ? 'ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ' : 'Crop Guidance',
      desc: language === 'kn' ? 'ಭತ್ತ, ರಾಗಿ, ಜೋಳ, ಮೆಕ್ಕೆಜೋಳ, ಹತ್ತಿ ಬೆಳೆಗಳ ಸಮಗ್ರ ಬೇಸಾಯ ಕ್ರಮ.' : 'Karnataka agro-climatic crop cycle, soil, sowing, and harvesting.',
      icon: <Sprout className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/crops',
      badge: '8 Major Crops',
    },
    {
      title: language === 'kn' ? 'ರಸಗೊಬ್ಬರ & ಪೋಷಕಾಂಶ' : 'Fertilizer Guidance',
      desc: language === 'kn' ? 'ಬೆಳೆ ಹಾಗೂ ಮಣ್ಣಿಗೆ ತಕ್ಕಂತೆ ಎನ್‌ಪಿಕೆ ಅನುಪಾತ, ಸಾವಯವ ಪರ್ಯಾಯಗಳು.' : 'Scientific NPK dosage, deficiency diagnosis, and organic methods.',
      icon: <FlaskConical className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/fertilizer',
      badge: 'Soil Specific',
    },
    {
      title: language === 'kn' ? 'ಲೈವ್ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ' : 'Live Weather Updates',
      desc: language === 'kn' ? 'ಕರ್ನಾಟಕದ 31 ಜಿಲ್ಲೆಗಳ ತಾಪಮಾನ, ಮಳೆ ಹಾಗೂ ಆರ್ದ್ರತೆಯ ಮಾಹಿತಿ.' : 'Real-time Karnataka district weather and precipitation forecasts.',
      icon: <CloudSun className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/weather-market',
      badge: '31 Districts',
    },
    {
      title: language === 'kn' ? 'ಮಂಡಿ ಮಾರುಕಟ್ಟೆ ಧಾರಣೆ' : 'APMC Market Prices',
      desc: language === 'kn' ? 'ಬೆಳಗಾವಿ, ಮೈಸೂರು, ಕಲಬುರಗಿ, ರಾಯಚೂರು ಎಪಿಎಂಸಿ ದರಗಳು.' : 'Verified Karnataka APMC mandi commodity prices and modal rates.',
      icon: <Activity className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/weather-market',
      badge: 'Official APMC',
    },
    {
      title: language === 'kn' ? 'ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಕಾರ್ಡ್' : 'Soil Health Advisory',
      desc: language === 'kn' ? 'ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರದ ಮೂಲಕ ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮತ್ತು ಸುಧಾರಣೆ.' : 'Soil test protocols and micronutrient correction advisory.',
      icon: <HelpCircle className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/fertilizer',
      badge: 'KVK Tested',
    },
    {
      title: language === 'kn' ? 'ಬೆಳೆ ರೋಗ & ಕೀಟ ನಿರ್ವಹಣೆ' : 'Crop Disease Assistance',
      desc: language === 'kn' ? 'ಕೀಟಬಾಧೆ ಹಾಗೂ ರೋಗ ಲಕ್ಷಣಗಳ ಮುನ್ನೆಚ್ಚರಿಕೆ ಮತ್ತು ಜೈವಿಕ ನಿಯಂತ್ರಣ.' : 'Integrated pest management and sustainable crop protection.',
      icon: <Bug className="w-6 h-6 text-[#174C36] dark:text-[#75A96A]" />,
      link: '/crops',
      badge: 'Biocontrol',
    },
  ];

  return (
    <div className="space-y-16 lg:space-y-24 pb-16">
      
      {/* HERO SECTION */}
      <section className="relative overflow-hidden pt-8 lg:pt-16 pb-12 bg-gradient-to-b from-[#EAF3E9]/50 via-transparent to-transparent dark:from-[#11221A]/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            
            {/* Left Column: Heading & CTAs */}
            <div className="lg:col-span-7 space-y-6">
              
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#EAF3E9] dark:bg-[#152E22] border border-[#75A96A]/40 text-[#174C36] dark:text-[#92C987] text-xs font-bold shadow-sm">
                <Sparkles className="w-4 h-4 text-[#D8AA48]" />
                <span>AI Agriculture Assistant for Karnataka Farmers</span>
              </div>

              {/* Main Heading */}
              <div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[#19251E] dark:text-[#EDF3EF] leading-tight">
                  Your Smart Agriculture Assistant
                </h1>
                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#174C36] dark:text-[#75A96A] font-kannada mt-2">
                  ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ
                </h2>
              </div>

              {/* Description */}
              <p className="text-base sm:text-lg text-[#69766D] dark:text-[#9BB0A4] leading-relaxed max-w-2xl">
                Discover government schemes, agricultural loans and farming guidance through intelligent Kannada voice assistance.
              </p>

              {/* Large Search Bar */}
              <form onSubmit={handleSearchSubmit} className="relative max-w-xl">
                <input
                  type="text"
                  placeholder="ಯೋಜನೆ ಹೆಸರು, ಬೆಳೆ (ಉದಾ. ಭತ್ತ, ರಾಗಿ) ಅಥವಾ ಸಬ್ಸಿಡಿ ಹುಡುಕಿ..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-28 py-3.5 text-sm sm:text-base rounded-2xl border-2 border-[#E2E8DF] dark:border-[#1E382B] bg-white dark:bg-[#11221A] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650] shadow-sm font-kannada"
                />
                <Search className="w-5 h-5 absolute left-4 top-4 text-[#69766D]" />
                <button
                  type="submit"
                  className="absolute right-2 top-2 bottom-2 px-5 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white text-xs sm:text-sm font-bold transition-colors shadow"
                >
                  ಹುಡುಕಿ
                </button>
              </form>

              {/* CTA Buttons */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <Link
                  to="/schemes"
                  className="px-6 py-3.5 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center gap-2 group"
                >
                  <span>Explore Schemes</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-[#D8AA48]" />
                </Link>

                <Link
                  to="/voice-assistant"
                  className="px-6 py-3.5 rounded-xl bg-white dark:bg-[#11221A] border-2 border-[#174C36] dark:border-[#75A96A] text-[#174C36] dark:text-[#92C987] font-bold text-sm hover:bg-[#EAF3E9] dark:hover:bg-[#152E22] transition-colors flex items-center gap-2 shadow-sm"
                >
                  <Mic className="w-4 h-4 text-[#D8AA48]" />
                  <span>Talk to Krishi Mitra</span>
                </Link>
              </div>

              {/* Regional Support Pill */}
              <div className="flex items-center gap-2 pt-2 text-xs text-[#69766D] dark:text-[#9BB0A4]">
                <CheckCircle className="w-4 h-4 text-[#2F7650]" />
                <span className="font-kannada">
                  ಉತ್ತರ ಕರ್ನಾಟಕ (ಧಾರವಾಡ, ಬೆಳಗಾವಿ) & ದಕ್ಷಿಣ ಕರ್ನಾಟಕ ಆಡುಭಾಷೆ ಸಕ್ರಿಯವಾಗಿದೆ
                </span>
              </div>
            </div>

            {/* Right Column: Authentic Indian Farmer Photograph */}
            <div className="lg:col-span-5 relative">
              <div className="relative rounded-3xl overflow-hidden shadow-2xl border-4 border-white dark:border-[#1E382B]">
                <img
                  src="https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=900&q=80"
                  alt="Karnataka Farmer in lush agricultural field"
                  className="w-full h-[440px] object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>

                {/* Overlaid Floating Card */}
                <div className="absolute bottom-5 left-5 right-5 p-4 rounded-2xl bg-white/95 dark:bg-[#11221A]/95 backdrop-blur-md border border-[#E2E8DF] dark:border-[#1E382B] shadow-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#174C36] flex items-center justify-center text-white">
                        <Mic className="w-5 h-5 text-[#D8AA48]" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                          "ನನಗೆ ೩ ಎಕರೆ ಭತ್ತಕ್ಕೆ ಸಬ್ಸಿಡಿ ಬೇಕು"
                        </p>
                        <p className="text-[11px] text-[#2F7650] dark:text-[#92C987] font-semibold">
                          ಕನ್ನಡ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ಸಕ್ರಿಯ
                        </p>
                      </div>
                    </div>
                    <span className="px-2 py-1 rounded bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] text-[10px] font-bold">
                      98% Accurate
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* DASHBOARD STATISTICS CARDS (Dynamic from DB) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          
          <div className="bg-white dark:bg-[#11221A] p-6 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm text-center">
            <p className="text-3xl sm:text-4xl font-extrabold text-[#174C36] dark:text-[#75A96A]">
              {stats.verified_schemes}+
            </p>
            <p className="text-xs sm:text-sm font-semibold text-[#69766D] dark:text-[#9BB0A4] mt-1 font-kannada">
              {t('statVerified')}
            </p>
            <span className="text-[10px] text-green-600 font-bold mt-1 inline-block">100% Source Verified</span>
          </div>

          <div className="bg-white dark:bg-[#11221A] p-6 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm text-center">
            <p className="text-3xl sm:text-4xl font-extrabold text-[#174C36] dark:text-[#75A96A]">
              {stats.districts_covered}
            </p>
            <p className="text-xs sm:text-sm font-semibold text-[#69766D] dark:text-[#9BB0A4] mt-1 font-kannada">
              {t('statDistricts')}
            </p>
            <span className="text-[10px] text-[#D8AA48] font-bold mt-1 inline-block">Full Karnataka Coverage</span>
          </div>

          <div className="bg-white dark:bg-[#11221A] p-6 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm text-center">
            <p className="text-3xl sm:text-4xl font-extrabold text-[#174C36] dark:text-[#75A96A]">
              {stats.service_categories}
            </p>
            <p className="text-xs sm:text-sm font-semibold text-[#69766D] dark:text-[#9BB0A4] mt-1 font-kannada">
              {t('statServices')}
            </p>
            <span className="text-[10px] text-blue-600 font-bold mt-1 inline-block">Schemes, Credit & Crop AI</span>
          </div>

          <div className="bg-white dark:bg-[#11221A] p-6 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm text-center">
            <p className="text-3xl sm:text-4xl font-extrabold text-[#174C36] dark:text-[#75A96A]">
              {stats.saved_schemes}
            </p>
            <p className="text-xs sm:text-sm font-semibold text-[#69766D] dark:text-[#9BB0A4] mt-1 font-kannada">
              {t('statSaved')}
            </p>
            <span className="text-[10px] text-purple-600 font-bold mt-1 inline-block">In Farmer Bookmarks</span>
          </div>
        </div>
      </section>

      {/* FEATURED GOVERNMENT SCHEMES (Carousel) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-8 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
              <ShieldCheck className="w-4 h-4 text-[#2F7650]" />
              <span>Official Database</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] mt-1 font-kannada">
              ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಕೃಷಿ ಯೋಜನೆಗಳು
            </h2>
            <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] mt-0.5">
              Verified Central and Karnataka State agricultural welfare programmes
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() =>
                setCarouselIndex((prev) => (prev - 1 + schemes.length) % schemes.length)
              }
              className="p-2 rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22]"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => setCarouselIndex((prev) => (prev + 1) % schemes.length)}
              className="p-2 rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22]"
            >
              <ChevronRight className="w-5 h-5" />
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

        {/* Carousel Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemes.slice(0, 3).map((scheme) => (
            <SchemeCard key={scheme.scheme_id} scheme={scheme} />
          ))}
        </div>
      </section>

      {/* AGRICULTURE SERVICE CARDS (8 Core Modules) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <span className="text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
            {t('servicesSubtitle')}
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] mt-1 font-kannada">
            {t('servicesTitle')}
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {services.map((serv, index) => (
            <Link
              key={index}
              to={serv.link}
              className="group bg-white dark:bg-[#11221A] p-6 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] hover:border-[#2F7650] hover:shadow-lg transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-[#EAF3E9] dark:bg-[#152E22] flex items-center justify-center group-hover:scale-110 transition-transform">
                    {serv.icon}
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#F7F9F5] dark:bg-[#0B1711] text-[#2F7650] dark:text-[#92C987] border border-[#E2E8DF] dark:border-[#1E382B]">
                    {serv.badge}
                  </span>
                </div>
                <h3 className="font-bold text-base text-[#19251E] dark:text-[#EDF3EF] group-hover:text-[#174C36] dark:group-hover:text-[#75A96A] transition-colors font-kannada">
                  {serv.title}
                </h3>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] mt-2 leading-relaxed">
                  {serv.desc}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-[#E2E8DF] dark:border-[#1E382B] flex items-center justify-between text-xs font-bold text-[#174C36] dark:text-[#75A96A]">
                <span>ಪ್ರವೇಶಿಸಿ (Open)</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ABOUT KRISHI MITRA & MISSION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-br from-[#174C36] to-[#123B2B] text-white rounded-3xl p-8 sm:p-12 lg:p-16 relative overflow-hidden shadow-xl">
          <div className="max-w-3xl space-y-6 relative z-10">
            <span className="text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
              About Krishi Mitra
            </span>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold leading-tight font-kannada">
              ರೈತರಿಗಾಗಿ ರೂಪಿಸಲಾದ ಕನ್ನಡ ಧ್ವನಿ ಕ್ರಾಂತಿ
            </h2>
            <p className="text-sm sm:text-base text-[#EAF3E9]/90 leading-relaxed">
              Karnataka farmers often miss out on crucial agricultural subsidies, low-interest crop credit, and micro-irrigation grants due to scattered government portals, complex eligibility rules, and English-only interfaces.
            </p>
            <p className="text-sm sm:text-base text-[#EAF3E9]/90 leading-relaxed font-kannada">
              ಕೃಷಿ ಮಿತ್ರವು ಉತ್ತರ ಹಾಗೂ ದಕ್ಷಿಣ ಕರ್ನಾಟಕದ ರೈತರ ಆಡುಭಾಷೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಂಡು, ಪಾರದರ್ಶಕ ನಿಯಮಾವಳಿಗಳೊಂದಿಗೆ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಹಾಗೂ ಬೆಳೆ ಸಲಹೆಗಳನ್ನು ಧ್ವನಿಯ ಮೂಲಕವೇ ತಲುಪಿಸುತ್ತದೆ.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
              <div className="p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/15">
                <p className="text-xl font-bold text-[#D8AA48]">0% Friction</p>
                <p className="text-xs text-[#EAF3E9]/80 mt-1">Speak directly in native Kannada</p>
              </div>
              <div className="p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/15">
                <p className="text-xl font-bold text-[#D8AA48]">Deterministic</p>
                <p className="text-xs text-[#EAF3E9]/80 mt-1">Rule-based PASS/FAIL verification</p>
              </div>
              <div className="p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/15">
                <p className="text-xl font-bold text-[#D8AA48]">31 Districts</p>
                <p className="text-xs text-[#EAF3E9]/80 mt-1">Belagavi to Chamarajanagar</p>
              </div>
            </div>

            <div className="pt-4">
              <Link
                to="/eligibility-checker"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#D8AA48] hover:bg-[#C6A65B] text-[#123B2B] font-extrabold text-sm shadow transition-colors"
              >
                <span>ನನ್ನ ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ (Check Eligibility Now)</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
