import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, ShieldCheck, AlertTriangle, Sparkles, Layers, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { Scheme } from '../types';
import { SchemeCard } from '../components/SchemeCard';
import { useLanguage } from '../context/LanguageContext';

export const SchemesPage: React.FC = () => {
  const { language } = useLanguage();
  const [searchParams, setSearchParams] = useSearchParams();

  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [selectedCrop, setSelectedCrop] = useState(searchParams.get('crop') || 'All');
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || 'All');
  const [selectedVerification, setSelectedVerification] = useState(searchParams.get('verification') || 'All');
  const [selectedStatus, setSelectedStatus] = useState(searchParams.get('status') || 'All');

  const cropsList = ['All', 'Paddy', 'Ragi', 'Jowar', 'Maize', 'Cotton', 'Groundnut', 'Tur', 'Sugarcane', 'Arecanut', 'Banana', 'Pepper'];

  const categoriesList = [
    { id: 'All', name: 'All Categories', name_kn: 'ಎಲ್ಲಾ ವಿಭಾಗಗಳು' },
    { id: 'Income Support', name: 'Income Support', name_kn: 'ಆದಾಯ ನೆರವು (PM-Kisan)' },
    { id: 'Crop Insurance', name: 'Crop Insurance', name_kn: 'ಬೆಳೆ ವಿಮೆ (PMFBY / Samrakshane)' },
    { id: 'Irrigation & Water', name: 'Irrigation & Water', name_kn: 'ನೀರಾವರಿ & ಕೃಷಿ ಹೊಂಡ (Krishi Bhagya / PMKSY)' },
    { id: 'Farm Mechanization', name: 'Farm Mechanization', name_kn: 'ಕೃಷಿ ಯಾಂತ್ರೀಕರಣ (SMAM / Raita Shakti)' },
    { id: 'Soil Health & Fertilizers', name: 'Soil Health', name_kn: 'ಮಣ್ಣು ಆರೋಗ್ಯ & ರಸಗೊಬ್ಬರ (SHC)' },
    { id: 'Credit & Loans', name: 'Credit & Loans', name_kn: 'ಬೆಳೆ ಸಾಲ (KCC / MISS)' },
    { id: 'Horticulture Development', name: 'Horticulture', name_kn: 'ತೋಟಗಾರಿಕೆ ಅಭಿವೃದ್ಧಿ (MIDH / Polyhouse)' },
    { id: 'Organic & Natural Farming', name: 'Organic Farming', name_kn: 'ಸಾವಯವ & ನೈಸರ್ಗಿಕ ಕೃಷಿ (NMNF / Savayava)' },
    { id: 'Post-Harvest & Marketing', name: 'Marketing & Infra', name_kn: 'ಮಾರುಕಟ್ಟೆ & ಗೋದಾಮು (e-NAM / AIF / FPO)' },
    { id: 'Disaster & Calamity Relief', name: 'Disaster Relief', name_kn: 'ಬೆಳೆ ಹಾನಿ ಪರಿಹಾರ (Parihara / SDRF)' },
    { id: 'Livestock & Integrated Farming', name: 'Livestock', name_kn: 'ಪಶುಪಾಲನೆ (Pashu Bhagya)' },
    { id: 'Millet Crop Incentives', name: 'Millets', name_kn: 'ಸಿರಿಧಾನ್ಯ ಪ್ರೋತ್ಸಾಹಧನ (Raitha Siri)' },
  ];

  useEffect(() => {
    loadSchemes();
  }, [searchParams]);

  const loadSchemes = async () => {
    setLoading(true);
    try {
      const s = searchParams.get('search') || undefined;
      const c = searchParams.get('crop') || undefined;
      const cat = searchParams.get('category') || undefined;
      const v = searchParams.get('verification') || undefined;
      const st = searchParams.get('status') || undefined;

      const data = await api.getSchemes({
        search: s,
        crop: c === 'All' ? undefined : c,
        category: cat === 'All' ? undefined : cat,
        verification: v === 'All' ? undefined : v,
        status: st === 'All' ? undefined : st,
      });
      setSchemes(data);
    } catch (err) {
      console.error('Failed to load schemes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const params: Record<string, string> = {};
    if (search.trim()) params.search = search.trim();
    if (selectedCrop !== 'All') params.crop = selectedCrop;
    if (selectedCategory !== 'All') params.category = selectedCategory;
    if (selectedVerification !== 'All') params.verification = selectedVerification;
    if (selectedStatus !== 'All') params.status = selectedStatus;
    setSearchParams(params);
  };

  const clearFilters = () => {
    setSearch('');
    setSelectedCrop('All');
    setSelectedCategory('All');
    setSelectedVerification('All');
    setSelectedStatus('All');
    setSearchParams({});
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Title & Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <ShieldCheck className="w-4 h-4 text-[#2F7650]" />
          <span>Comprehensive Central & Karnataka Agricultural Scheme Repository</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
            ಸರ್ಕಾರಿ ಕೃಷಿ ಯೋಜನೆಗಳು (Government Agricultural Schemes)
          </h1>
          <span className="px-3.5 py-1.5 rounded-full bg-[#174C36] text-white text-xs font-bold shrink-0 self-start sm:self-auto shadow-sm">
            {schemes.length} ಯೋಜನೆಗಳು ಲಭ್ಯವಿದೆ ({schemes.length} Schemes)
          </span>
        </div>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] max-w-4xl leading-relaxed">
          {language === 'kn'
            ? 'ಕರ್ನಾಟಕದ ರೈತರಿಗಾಗಿ ಕೇಂದ್ರ ಹಾಗೂ ರಾಜ್ಯ ಸರ್ಕಾರಗಳು ಜಾರಿಗೆ ತಂದಿರುವ ಕೃಷಿ, ನೀರಾವರಿ, ಬೆಳೆ ವಿಮೆ, ರಸಗೊಬ್ಬರ, ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ಮತ್ತು ಪರಿಹಾರ ಯೋಜನೆಗಳ ಸಮಗ್ರ ಅಧಿಕೃತ ದಾಖಲೆಗಳು.'
            : 'Explore complete verified agricultural assistance, subsidies, crop insurance, mechanization, micro-irrigation, and calamity relief schemes available for Karnataka farmers.'}
        </p>
      </div>

      {/* Quick Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {categoriesList.map((cat) => {
          const isActive = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => {
                setSelectedCategory(cat.id);
                const params: Record<string, string> = {};
                if (search.trim()) params.search = search.trim();
                if (selectedCrop !== 'All') params.crop = selectedCrop;
                if (cat.id !== 'All') params.category = cat.id;
                if (selectedVerification !== 'All') params.verification = selectedVerification;
                if (selectedStatus !== 'All') params.status = selectedStatus;
                setSearchParams(params);
              }}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ${
                isActive
                  ? 'bg-[#174C36] text-white border-[#174C36] shadow-md'
                  : 'bg-white dark:bg-[#11221A] text-[#19251E] dark:text-[#EDF3EF] border-[#E2E8DF] dark:border-[#1E382B] hover:border-[#2F7650]'
              }`}
            >
              {language === 'kn' ? cat.name_kn : cat.name}
            </button>
          );
        })}
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white dark:bg-[#11221A] p-4 sm:p-6 rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm space-y-4">
        <form onSubmit={handleApplyFilters} className="grid grid-cols-1 sm:grid-cols-12 gap-3 sm:gap-4">
          
          {/* Keyword Search */}
          <div className="sm:col-span-4 relative">
            <input
              type="text"
              placeholder="ಯೋಜನೆ ಹೆಸರು ಅಥವಾ ಇಲಾಖೆ ಹುಡುಕಿ..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650] font-kannada"
            />
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-[#69766D]" />
          </div>

          {/* Crop Filter */}
          <div className="sm:col-span-3">
            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="w-full px-3 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              {cropsList.map((c) => (
                <option key={c} value={c}>
                  {c === 'All' ? 'ಎಲ್ಲಾ ಬೆಳೆಗಳು (All Crops)' : c}
                </option>
              ))}
            </select>
          </div>

          {/* Verification Status Filter */}
          <div className="sm:col-span-3">
            <select
              value={selectedVerification}
              onChange={(e) => setSelectedVerification(e.target.value)}
              className="w-full px-3 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="All">ಎಲ್ಲಾ ಯೋಜನೆಗಳು (All Records)</option>
              <option value="Verified">Verified Official Schemes</option>
              <option value="Verification Required">Verification Required (State Review)</option>
              <option value="Synthetic Demo">Synthetic Demo Benchmarks</option>
            </select>
          </div>

          {/* Filter & Reset Buttons */}
          <div className="sm:col-span-2 flex items-center gap-2">
            <button
              type="submit"
              className="flex-1 py-2.5 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white text-xs sm:text-sm font-bold shadow-sm transition-colors"
            >
              ಹುಡುಕಿ
            </button>
            <button
              type="button"
              onClick={clearFilters}
              className="px-3 py-2.5 rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] text-xs text-[#69766D] hover:bg-gray-100 dark:hover:bg-gray-800"
              title="Reset Filters"
            >
              Reset
            </button>
          </div>
        </form>

        {/* Quick Crop Badges */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E2E8DF] dark:border-[#1E382B] text-xs text-[#69766D]">
          <span className="font-semibold text-[#19251E] dark:text-[#EDF3EF]">ತ್ವರಿತ ಬೆಳೆಗಳು:</span>
          {cropsList.slice(1, 8).map((c) => (
            <button
              key={c}
              onClick={() => {
                setSelectedCrop(c);
                const params: Record<string, string> = {};
                if (search.trim()) params.search = search.trim();
                params.crop = c;
                if (selectedCategory !== 'All') params.category = selectedCategory;
                if (selectedVerification !== 'All') params.verification = selectedVerification;
                setSearchParams(params);
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors ${
                selectedCrop === c
                  ? 'bg-[#174C36] text-white border-[#174C36]'
                  : 'bg-[#F7F9F5] dark:bg-[#0B1711] border-[#E2E8DF] dark:border-[#1E382B] hover:border-[#2F7650]'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Schemes Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              className="h-96 rounded-2xl bg-white dark:bg-[#11221A] animate-pulse border border-[#E2E8DF] dark:border-[#1E382B]"
            ></div>
          ))}
        </div>
      ) : schemes.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] space-y-3">
          <p className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
            ಯಾವುದೇ ಯೋಜನೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ
          </p>
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
            No schemes found matching the specified filters. Try clearing filters.
          </p>
          <button
            onClick={clearFilters}
            className="px-4 py-2 rounded-xl bg-[#174C36] text-white text-xs font-bold"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemes.map((scheme) => (
            <SchemeCard key={scheme.scheme_id} scheme={scheme} onBookmarkToggled={loadSchemes} />
          ))}
        </div>
      )}
    </div>
  );
};
