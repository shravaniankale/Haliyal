import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, ArrowLeft, ArrowRight, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { Scheme } from '../types';
import { SchemeCard } from '../components/SchemeCard';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export const SavedSchemesPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [savedSchemes, setSavedSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);

  const loadSaved = async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await api.getMySavedSchemes();
      setSavedSchemes(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSaved();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-4">
        <Bookmark className="w-12 h-12 text-[#69766D] mx-auto" />
        <h2 className="text-xl font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ಉಳಿಸಿದ ಯೋಜನೆಗಳನ್ನು ನೋಡಲು ಲಾಗಿನ್ ಆಗಿ
        </h2>
        <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
          Please login to your farmer account to view and manage your bookmarked government schemes.
        </p>
        <Link
          to="/login"
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#174C36] text-white text-xs font-bold shadow"
        >
          <span>ಲಾಗಿನ್ ಆಗಿ (Login)</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <Bookmark className="w-4 h-4 text-[#2F7650]" />
          <span>Farmer Bookmarks</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ನನ್ನ ಉಳಿಸಿದ ಯೋಜನೆಗಳು (My Saved Schemes)
        </h1>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4]">
          Quick access to your bookmarked welfare programs and subsidy schemes
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2].map((n) => (
            <div key={n} className="h-80 rounded-2xl bg-white dark:bg-[#11221A] animate-pulse border"></div>
          ))}
        </div>
      ) : savedSchemes.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] space-y-4">
          <Bookmark className="w-12 h-12 text-[#69766D] mx-auto opacity-50" />
          <h3 className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
            ನೀವು ಇನ್ನೂ ಯಾವುದೇ ಯೋಜನೆಗಳನ್ನು ಉಳಿಸಿಲ್ಲ
          </h3>
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
            Explore government schemes and click the bookmark button to save them here for quick application.
          </p>
          <Link
            to="/schemes"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#174C36] text-white text-xs font-bold"
          >
            <span>ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ (Explore Schemes)</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedSchemes.map((scheme) => (
            <SchemeCard key={scheme.scheme_id} scheme={scheme} onBookmarkToggled={loadSaved} />
          ))}
        </div>
      )}
    </div>
  );
};
