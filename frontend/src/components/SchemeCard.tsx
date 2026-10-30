import React from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  Bookmark,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import { Scheme } from '../types';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

interface SchemeCardProps {
  scheme: Scheme;
  onBookmarkToggled?: () => void;
}

export const SchemeCard: React.FC<SchemeCardProps> = ({ scheme, onBookmarkToggled }) => {
  const { language } = useLanguage();
  const { isAuthenticated } = useAuth();
  const [isSaved, setIsSaved] = React.useState(!!scheme.is_saved);
  const [saving, setSaving] = React.useState(false);

  const isDemo = scheme.verification_status === 'Synthetic Demo';

  const handleToggleSave = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('ಯೋಜನೆ ಉಳಿಸಲು ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಆಗಿ (Please login to bookmark schemes)');
      return;
    }
    setSaving(true);
    try {
      const res = await api.toggleSaveScheme(scheme.id);
      setIsSaved(res.saved);
      if (onBookmarkToggled) onBookmarkToggled();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className={`group bg-white dark:bg-[#11221A] rounded-2xl border transition-all duration-300 flex flex-col overflow-hidden shadow-sm hover:shadow-xl ${
        isDemo
          ? 'border-amber-300 dark:border-amber-700/60'
          : 'border-[#E2E8DF] dark:border-[#1E382B] hover:border-[#2F7650]'
      }`}
    >
      {/* Top Banner & Image */}
      <div className="relative h-48 w-full overflow-hidden bg-gray-100 dark:bg-gray-800">
        <img
          src={
            scheme.image_url ||
            'https://images.unsplash.com/photo-1592982537447-6f2a6a0c5c1c?auto=format&fit=crop&w=800&q=80'
          }
          alt={scheme.scheme_name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>

        {/* Verification Status Badge */}
        <div className="absolute top-3 left-3 z-10">
          {isDemo ? (
            <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-full bg-amber-500/90 text-white backdrop-blur-md shadow-md border border-amber-300">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Synthetic Demo Record</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-full bg-[#174C36]/90 text-white backdrop-blur-md shadow-md border border-[#75A96A]/50">
              <ShieldCheck className="w-3.5 h-3.5 text-[#D8AA48]" />
              <span>Verified Official Scheme</span>
            </span>
          )}
        </div>

        {/* Bookmark Button */}
        <button
          onClick={handleToggleSave}
          disabled={saving}
          className="absolute top-3 right-3 z-10 p-2 rounded-full bg-white/80 dark:bg-[#123B2B]/80 text-[#174C36] dark:text-[#E5BE5F] hover:scale-110 transition-transform shadow backdrop-blur-sm"
          title={isSaved ? 'Remove from saved' : 'Save scheme'}
        >
          <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current text-[#D8AA48]' : ''}`} />
        </button>

        {/* Scheme Department (Overlay bottom-left) */}
        <div className="absolute bottom-3 left-3 right-3 z-10 text-white">
          <p className="text-xs font-semibold text-[#D8AA48] tracking-wide uppercase truncate">
            {language === 'kn' ? scheme.department_kn : scheme.department}
          </p>
        </div>
      </div>

      {/* Card Content Body */}
      <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
        <div>
          {/* Scheme Name */}
          <h3 className="font-bold text-lg text-[#19251E] dark:text-[#EDF3EF] group-hover:text-[#174C36] dark:group-hover:text-[#75A96A] transition-colors leading-snug">
            {scheme.scheme_name_kn}
          </h3>
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] font-medium mt-0.5">
            {scheme.scheme_name}
          </p>

          {/* Description */}
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] line-clamp-2 mt-2.5 leading-relaxed">
            {language === 'kn' ? scheme.description_kn : scheme.description}
          </p>

          {/* Benefit Highlight Box */}
          <div className="mt-4 p-3 rounded-xl bg-[#EAF3E9]/80 dark:bg-[#152E22]/60 border border-[#75A96A]/30 text-xs">
            <span className="font-bold text-[#174C36] dark:text-[#92C987] block mb-0.5 font-kannada">
              {language === 'kn' ? 'ಪ್ರಮುಖ ಸೌಲಭ್ಯ / ಪ್ರಯೋಜನ:' : 'Key Benefit:'}
            </span>
            <p className="text-[#19251E] dark:text-[#EDF3EF] font-medium line-clamp-2">
              {language === 'kn' ? scheme.benefit_details_kn : scheme.benefit_details}
            </p>
          </div>

          {/* Eligibility Tags */}
          <div className="mt-3 flex flex-wrap gap-1.5">
            {scheme.land_requirements && (
              <span className="text-[11px] px-2 py-0.5 rounded-md bg-[#F7F9F5] dark:bg-[#0B1711] text-[#2F7650] dark:text-[#92C987] border border-[#E2E8DF] dark:border-[#1E382B]">
                {scheme.land_requirements}
              </span>
            )}
            {scheme.eligible_crops && scheme.eligible_crops.length > 0 && (
              <span className="text-[11px] px-2 py-0.5 rounded-md bg-[#F7F9F5] dark:bg-[#0B1711] text-[#69766D] dark:text-[#9BB0A4] border border-[#E2E8DF] dark:border-[#1E382B]">
                ಬೆಳೆಗಳು: {scheme.eligible_crops.slice(0, 3).join(', ')}
              </span>
            )}
          </div>
        </div>

        {/* Card Footer Actions */}
        <div className="pt-3 border-t border-[#E2E8DF] dark:border-[#1E382B] flex items-center justify-between gap-2">
          <Link
            to={`/schemes/${scheme.scheme_id}`}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-[#174C36] dark:text-[#75A96A] hover:underline"
          >
            <span>{language === 'kn' ? 'ವಿವರಗಳನ್ನು ನೋಡಿ' : 'View Details'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>

          <a
            href={scheme.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] hover:bg-[#EAF3E9] dark:hover:bg-[#152E22] border border-[#E2E8DF] dark:border-[#1E382B] transition-colors"
          >
            <span>{language === 'kn' ? 'ಅಧಿಕೃತ ಪೋರ್ಟಲ್' : 'Official Portal'}</span>
            <ExternalLink className="w-3 h-3 text-[#2F7650]" />
          </a>
        </div>
      </div>
    </div>
  );
};
