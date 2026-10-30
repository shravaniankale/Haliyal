import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, ShieldCheck, AlertTriangle, Sparkles } from 'lucide-react';
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
  const [selectedVerification, setSelectedVerification] = useState(searchParams.get('verification') || 'All');

  const cropsList = ['All', 'Paddy', 'Ragi', 'Jowar', 'Maize', 'Cotton', 'Groundnut', 'Tur', 'Sugarcane'];

  useEffect(() => {
    loadSchemes();
  }, [searchParams]);

  const loadSchemes = async () => {
    setLoading(true);
    try {
      const s = searchParams.get('search') || undefined;
      const c = searchParams.get('crop') || undefined;
      const v = searchParams.get('verification') || undefined;

      const data = await api.getSchemes({
        search: s,
        crop: c === 'All' ? undefined : c,
        verification: v === 'All' ? undefined : v,
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
    if (selectedVerification !== 'All') params.verification = selectedVerification;
    setSearchParams(params);
  };

  const clearFilters = () => {
    setSearch('');
    setSelectedCrop('All');
    setSelectedVerification('All');
    setSearchParams({});
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Title & Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <ShieldCheck className="w-4 h-4 text-[#2F7650]" />
          <span>Government Welfare Scheme Repository</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ಸರ್ಕಾರಿ ಕೃಷಿ ಯೋಜನೆಗಳು (All Schemes)
        </h1>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] max-w-3xl leading-relaxed">
          {language === 'kn'
            ? 'ಕರ್ನಾಟಕದ ರೈತರಿಗಾಗಿ ಕೇಂದ್ರ ಹಾಗೂ ರಾಜ್ಯ ಸರ್ಕಾರಗಳು ಜಾರಿಗೆ ತಂದಿರುವ ಕೃಷಿ, ನೀರಾವರಿ, ಬೆಳೆ ವಿಮೆ ಮತ್ತು ಸಬ್ಸಿಡಿ ಯೋಜನೆಗಳ ಅಧಿಕೃತ ವಿವರಗಳು.'
            : 'Explore verified agricultural assistance, subsidies, crop insurance, and equipment support available for Karnataka farmers.'}
        </p>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white dark:bg-[#11221A] p-4 sm:p-6 rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm space-y-4">
        <form onSubmit={handleApplyFilters} className="grid grid-cols-1 sm:grid-cols-12 gap-3 sm:gap-4">
          
          {/* Keyword Search */}
          <div className="sm:col-span-5 relative">
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
          <div className="sm:col-span-2">
            <select
              value={selectedVerification}
              onChange={(e) => setSelectedVerification(e.target.value)}
              className="w-full px-3 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="All">ಎಲ್ಲಾ ಸ್ಥಿತಿ (All Status)</option>
              <option value="Verified">Verified Official</option>
              <option value="Synthetic Demo">Synthetic Demo</option>
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

        {/* Quick Filter Badges */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E2E8DF] dark:border-[#1E382B] text-xs text-[#69766D]">
          <span className="font-semibold text-[#19251E] dark:text-[#EDF3EF]">ತ್ವರಿತ ಬೆಳೆಗಳು:</span>
          {cropsList.slice(1, 6).map((c) => (
            <button
              key={c}
              onClick={() => {
                setSelectedCrop(c);
                setSearchParams({ crop: c });
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
          {[1, 2, 3].map((n) => (
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
