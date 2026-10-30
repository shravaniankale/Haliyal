import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  Bookmark,
  CheckCircle2,
  FileText,
  Clock,
  Landmark,
  ArrowLeft,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { Scheme } from '../types';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';

export const SchemeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { language } = useLanguage();
  const { isAuthenticated } = useAuth();

  const [scheme, setScheme] = useState<Scheme | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadScheme() {
      if (!id) return;
      setLoading(true);
      try {
        const data = await api.getSchemeDetail(id);
        setScheme(data);
        setIsSaved(!!data.is_saved);
      } catch (err) {
        console.error('Failed to load scheme:', err);
      } finally {
        setLoading(false);
      }
    }
    loadScheme();
  }, [id]);

  const handleToggleSave = async () => {
    if (!scheme) return;
    if (!isAuthenticated) {
      alert('ಯೋಜನೆ ಉಳಿಸಲು ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಆಗಿ (Please login to bookmark schemes)');
      return;
    }
    setSaving(true);
    try {
      const res = await api.toggleSaveScheme(scheme.id);
      setIsSaved(res.saved);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="w-12 h-12 rounded-full border-4 border-[#174C36] border-t-transparent animate-spin mx-auto"></div>
        <p className="mt-4 text-xs font-semibold text-[#69766D] dark:text-[#9BB0A4]">
          ಯೋಜನೆಯ ವಿವರಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...
        </p>
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4">
        <h2 className="text-xl font-bold text-red-600">ಯೋಜನೆ ಕಂಡುಬಂದಿಲ್ಲ (Scheme Not Found)</h2>
        <Link
          to="/schemes"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#174C36] text-white text-xs font-bold"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>ಎಲ್ಲಾ ಯೋಜನೆಗಳಿಗೆ ಹಿಂತಿರುಗಿ</span>
        </Link>
      </div>
    );
  }

  const isDemo = scheme.verification_status === 'Synthetic Demo';

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-xs text-[#69766D] dark:text-[#9BB0A4]">
        <Link to="/schemes" className="hover:underline flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>ಯೋಜನೆಗಳು (Schemes)</span>
        </Link>
        <ChevronRight className="w-3 h-3" />
        <span className="font-semibold text-[#19251E] dark:text-[#EDF3EF] truncate max-w-xs">
          {scheme.scheme_id}
        </span>
      </div>

      {/* Main Header Card */}
      <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 sm:p-8 shadow-sm space-y-6">
        
        {/* Top Badges & Actions */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
            {isDemo ? (
              <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-300">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Synthetic Demonstration Record (Test Only)</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] border border-[#75A96A]/40">
                <ShieldCheck className="w-4 h-4 text-[#D8AA48]" />
                <span>Verified Official Government Scheme</span>
              </span>
            )}
            <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#F7F9F5] dark:bg-[#0B1711] text-[#69766D] dark:text-[#9BB0A4] border border-[#E2E8DF] dark:border-[#1E382B]">
              {scheme.scheme_type}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleToggleSave}
              disabled={saving}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold border transition-colors ${
                isSaved
                  ? 'bg-[#EAF3E9] text-[#174C36] border-[#75A96A]'
                  : 'border-[#E2E8DF] dark:border-[#1E382B] text-[#69766D] hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current text-[#D8AA48]' : ''}`} />
              <span>{isSaved ? 'Saved' : 'Save Scheme'}</span>
            </button>

            <a
              href={scheme.official_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white text-xs font-bold shadow-sm transition-colors"
            >
              <span>ಅಧಿಕೃತ ಪೋರ್ಟಲ್ (Apply)</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Title & Department */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-tight">
            {scheme.scheme_name_kn}
          </h1>
          <p className="text-base font-semibold text-[#69766D] dark:text-[#9BB0A4] mt-1">
            {scheme.scheme_name}
          </p>
          <div className="flex items-center gap-2 text-xs font-medium text-[#2F7650] dark:text-[#75A96A] mt-2">
            <Landmark className="w-4 h-4 shrink-0" />
            <span>{scheme.department_kn} ({scheme.department})</span>
          </div>
        </div>

        {/* Synthetic Demo Warning Notice */}
        {isDemo && (
          <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 flex items-start gap-3 text-xs text-amber-900 dark:text-amber-200">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold">ಕಾಲ್ಪನಿಕ ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆಯ ಸೂಚನೆ (Fictional Demo Record Notice)</p>
              <p className="leading-relaxed">
                ಇದು ಕೇವಲ ಹ್ಯಾಕಥಾನ್ ನಿಯಮ ಮೌಲ್ಯಮಾಪನ ಮತ್ತು ಅಲ್ಗಾರಿದಮ್ ಪರೀಕ್ಷೆಗಾಗಿ ರಚಿಸಲಾದ ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ದಾಖಲೆಯಾಗಿದೆ. ಇದು ನಿಜವಾದ ಸರ್ಕಾರಿ ಯೋಜನೆಯಲ್ಲ ಹಾಗೂ ಯಾವುದೇ ನೈಜ ಸಹಾಯಧನವನ್ನು ಪ್ರತಿನಿಧಿಸುವುದಿಲ್ಲ.
              </p>
            </div>
          </div>
        )}

        {/* Benefit Highlight Card */}
        <div className="p-5 rounded-2xl bg-gradient-to-br from-[#EAF3E9] to-[#F7F9F5] dark:from-[#152E22] dark:to-[#11221A] border-2 border-[#75A96A]/40 space-y-2">
          <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wide text-[#174C36] dark:text-[#92C987]">
            <Sparkles className="w-4 h-4 text-[#D8AA48]" />
            <span>ಯೋಜನೆಯ ಸೌಲಭ್ಯ & ಪ್ರಯೋಜನ (Benefit Details)</span>
          </div>
          <p className="text-sm sm:text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-relaxed">
            {scheme.benefit_details_kn}
          </p>
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
            {scheme.benefit_details}
          </p>
        </div>
      </div>

      {/* Grid: Description & Eligibility Rules */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Full Description & Steps */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* Detailed Description */}
          <div className="bg-white dark:bg-[#11221A] p-6 rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm space-y-3">
            <h2 className="text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
              ಯೋಜನೆಯ ಸಂಪೂರ್ಣ ವಿವರಣೆ (Description)
            </h2>
            <p className="text-xs sm:text-sm text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-relaxed">
              {scheme.description_kn}
            </p>
            <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] leading-relaxed pt-2 border-t border-[#E2E8DF] dark:border-[#1E382B]">
              {scheme.description}
            </p>
          </div>

          {/* Application Steps */}
          <div className="bg-white dark:bg-[#11221A] p-6 rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm space-y-4">
            <h2 className="text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#2F7650]" />
              <span>ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಹಂತಗಳು (Step-by-Step Application)</span>
            </h2>
            <div className="space-y-3">
              {scheme.application_steps.map((step, idx) => (
                <div key={idx} className="flex items-start gap-3 text-xs sm:text-sm">
                  <span className="w-6 h-6 rounded-full bg-[#174C36] text-white flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <p className="text-[#19251E] dark:text-[#EDF3EF] font-medium leading-relaxed">
                    {step}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Transparent Eligibility Breakdown & Documents */}
        <div className="lg:col-span-5 space-y-8">
          
          {/* Eligibility Criteria Matrix */}
          <div className="bg-white dark:bg-[#11221A] p-6 rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm space-y-4">
            <h2 className="text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#2F7650]" />
              <span>ಅರ್ಹತೆಯ ನಿಯಮಗಳು (Eligibility Criteria)</span>
            </h2>

            <div className="space-y-3 text-xs divide-y divide-[#E2E8DF] dark:divide-[#1E382B]">
              
              <div className="pt-2">
                <span className="font-semibold text-[#69766D] dark:text-[#9BB0A4] block">ಅರ್ಹ ರೈತರ ವರ್ಗ (Farmer Category):</span>
                <span className="font-bold text-[#19251E] dark:text-[#EDF3EF] mt-0.5 block">
                  {scheme.eligible_farmer_categories.join(', ')}
                </span>
              </div>

              <div className="pt-2">
                <span className="font-semibold text-[#69766D] dark:text-[#9BB0A4] block">ಕೃಷಿ ಭೂಮಿಯ ಮಿತಿ (Land Limits):</span>
                <span className="font-bold text-[#19251E] dark:text-[#EDF3EF] mt-0.5 block">
                  {scheme.land_requirements || (scheme.max_land_acres ? `ಗರಿಷ್ಠ ${scheme.max_land_acres} ಎಕರೆ` : 'ಯಾವುದೇ ಗರಿಷ್ಠ ಮಿತಿಯಿಲ್ಲ')}
                </span>
              </div>

              <div className="pt-2">
                <span className="font-semibold text-[#69766D] dark:text-[#9BB0A4] block">ಭೂ ಮಾಲೀಕತ್ವದ ಷರತ್ತು (Ownership):</span>
                <span className="font-bold text-[#19251E] dark:text-[#EDF3EF] mt-0.5 block">
                  {scheme.required_ownership === 'Own' ? 'ಸ್ವಂತ ಜಮೀನು (RTC ಪಹಣಿ ಕಡ್ಡಾಯ)' : 'ಸ್ವಂತ ಅಥವಾ ಗೇಣಿ ಜಮೀನು (Tenant allowed)'}
                </span>
              </div>

              <div className="pt-2">
                <span className="font-semibold text-[#69766D] dark:text-[#9BB0A4] block">ಒಳಪಡುವ ಬೆಳೆಗಳು (Eligible Crops):</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {scheme.eligible_crops.map((c) => (
                    <span key={c} className="px-2 py-0.5 rounded bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] text-[11px] font-semibold">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-3">
              <Link
                to="/eligibility-checker"
                className="w-full py-2.5 rounded-xl bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] hover:bg-[#75A96A] hover:text-white transition-colors text-xs font-bold flex items-center justify-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#D8AA48]" />
                <span>ನನ್ನ ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ (Check My Status)</span>
              </Link>
            </div>
          </div>

          {/* Required Documents Checklist */}
          <div className="bg-white dark:bg-[#11221A] p-6 rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm space-y-4">
            <h2 className="text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#D8AA48]" />
              <span>ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳು (Required Documents)</span>
            </h2>

            <ul className="space-y-2 text-xs">
              {scheme.required_documents.map((doc, idx) => (
                <li key={idx} className="flex items-center gap-2 text-[#19251E] dark:text-[#EDF3EF]">
                  <CheckCircle2 className="w-4 h-4 text-[#2F7650] shrink-0" />
                  <span className="font-medium">{doc}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Verification Audit Stamp */}
          <div className="p-4 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] text-xs text-[#69766D] dark:text-[#9BB0A4] space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-[#19251E] dark:text-[#EDF3EF]">
              <Clock className="w-3.5 h-3.5 text-[#2F7650]" />
              <span>ಪರಿಶೀಲನೆ ದಿನಾಂಕ: {scheme.verification_date}</span>
            </div>
            {scheme.source_url && (
              <a
                href={scheme.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#174C36] dark:text-[#75A96A] hover:underline flex items-center gap-1 text-[11px] pt-1"
              >
                <span>ಅಧಿಕೃತ ಮಾರ್ಗಸೂಚಿ ಮೂಲ ಲಿಂಕ್ (Official Guidelines Source)</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
