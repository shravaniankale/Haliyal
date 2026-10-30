import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  HelpCircle,
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Filter
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { EligibilityResponse, EligibilityResultItem } from '../types';

export const EligibilityCheckerPage: React.FC = () => {
  const { profile } = useAuth();
  const { language } = useLanguage();

  const [districts, setDistricts] = useState<any[]>([]);
  const [district, setDistrict] = useState(profile?.district || 'Belagavi');
  const [crop, setCrop] = useState('Paddy');
  const [landAcres, setLandAcres] = useState<string>(profile?.land_acres ? String(profile.land_acres) : '3.0');
  const [landOwnership, setLandOwnership] = useState<string>('Own');
  const [season, setSeason] = useState('Kharif');
  const [irrigation, setIrrigation] = useState<string>('Rainfed');
  const [category, setCategory] = useState<string>('Small & Marginal');

  const [evalResult, setEvalResult] = useState<EligibilityResponse | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    async function loadDistricts() {
      try {
        const data = await api.getDistricts();
        setDistricts(data);
      } catch (e) {}
    }
    loadDistricts();
  }, []);

  // Update defaults if profile loads
  useEffect(() => {
    if (profile) {
      if (profile.district) setDistrict(profile.district);
      if (profile.land_acres) setLandAcres(String(profile.land_acres));
      if (profile.land_ownership) setLandOwnership(profile.land_ownership);
      if (profile.irrigation_type) setIrrigation(profile.irrigation_type);
      if (profile.farmer_category) setCategory(profile.farmer_category);
    }
  }, [profile]);

  const handleEvaluate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setEvaluating(true);

    try {
      const acresVal = landAcres ? parseFloat(landAcres) : undefined;
      const res = await api.checkEligibility({
        district,
        crop,
        land_acres: isNaN(acresVal as any) ? undefined : acresVal,
        land_ownership: landOwnership,
        season,
        irrigation_type: irrigation,
        farmer_category: category,
      });
      setEvalResult(res);
    } catch (err) {
      console.error('Eligibility check failed:', err);
    } finally {
      setEvaluating(false);
    }
  };

  // Run initial evaluation on load
  useEffect(() => {
    handleEvaluate();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <Sparkles className="w-4 h-4 text-[#2F7650]" />
          <span>Deterministic Eligibility Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ನನಗಾಗಿ ಸೂಕ್ತ ಯೋಜನೆಗಳು (Find Schemes for Me)
        </h1>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] max-w-3xl leading-relaxed">
          {language === 'kn'
            ? 'ನಿಮ್ಮ ಜಮೀನು, ಬೆಳೆ ಮತ್ತು ವರ್ಗದ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ. ಯಾವುದೇ ಊಹಾಪೋಹವಿಲ್ಲದೆ ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಮಾನದಂಡಗಳ ಆಧಾರದ ಮೇಲೆ ನಿಮ್ಮ ಅರ್ಹತೆಯನ್ನು ತಕ್ಷಣ ಪರಿಶೀಲಿಸಿ.'
            : 'Enter your landholding, crop, and location details to receive source-backed, transparent recommendations evaluated by our deterministic rule engine.'}
        </p>
      </div>

      {/* Input Form & Criteria Matrix */}
      <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 sm:p-8 shadow-sm space-y-6">
        <h2 className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
          <Filter className="w-5 h-5 text-[#2F7650]" />
          <span>ರೈತರ ವಿವರಗಳು (Farmer Circumstances)</span>
        </h2>

        <form onSubmit={handleEvaluate} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* District */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ಜಿಲ್ಲೆ (District)
            </label>
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              {districts.map((d) => (
                <option key={d.name} value={d.name}>
                  {d.name_kn} ({d.name})
                </option>
              ))}
            </select>
          </div>

          {/* Crop */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ಪ್ರಮುಖ ಬೆಳೆ (Primary Crop)
            </label>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="Paddy">ಭತ್ತ (Paddy)</option>
              <option value="Ragi">ರಾಗಿ (Ragi)</option>
              <option value="Jowar">ಜೋಳ (Jowar)</option>
              <option value="Maize">ಮೆಕ್ಕೆಜೋಳ (Maize)</option>
              <option value="Cotton">ಹತ್ತಿ (Cotton)</option>
              <option value="Groundnut">ಕಡಲೆಕಾಯಿ (Groundnut)</option>
              <option value="Tur">ತೊಗರಿ (Tur / Red Gram)</option>
              <option value="Sugarcane">ಕಬ್ಬು (Sugarcane)</option>
            </select>
          </div>

          {/* Land Area */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (Acres)
            </label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 3.0"
              value={landAcres}
              onChange={(e) => setLandAcres(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            />
          </div>

          {/* Land Ownership */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ಮಾಲೀಕತ್ವ (Land Ownership)
            </label>
            <select
              value={landOwnership}
              onChange={(e) => setLandOwnership(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="Own">ಸ್ವಂತ ಭೂಮಿ (Own Title Holder)</option>
              <option value="Tenant">ಗೇಣಿ ಭೂಮಿ (Tenant / Cultivator)</option>
              <option value="Leased">ಗುತ್ತಿಗೆ ಭೂಮಿ (Leased)</option>
              <option value="Shared">ಪಾಲುದಾರಿಕೆ (Shared)</option>
              <option value="Other">ಇತರೆ (Other)</option>
            </select>
          </div>

          {/* Season */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ಹಂಗಾಮು (Season)
            </label>
            <select
              value={season}
              onChange={(e) => setSeason(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="Kharif">ಮುಂಗಾರು (Kharif)</option>
              <option value="Rabi">ಹಿಂಗಾರು (Rabi)</option>
              <option value="Summer">ಬೇಸಿಗೆ (Summer)</option>
            </select>
          </div>

          {/* Irrigation */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ನೀರಾವರಿ ಮೂಲ (Irrigation)
            </label>
            <select
              value={irrigation}
              onChange={(e) => setIrrigation(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="Rainfed">ಮಳೆ ಆಶ್ರಿತ / ಖುಷ್ಕಿ (Rainfed)</option>
              <option value="Borewell">ಕೊಳವೆಬಾವಿ (Borewell)</option>
              <option value="Canal">ಕಾಲುವೆ ನೀರಾವರಿ (Canal)</option>
              <option value="Drip">ಹನಿ ನೀರಾವರಿ (Drip)</option>
              <option value="Sprinkler">ತುಂತುರು ನೀರಾವರಿ (Sprinkler)</option>
            </select>
          </div>

          {/* Farmer Category */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ರೈತರ ವರ್ಗ (Farmer Category)
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="Small & Marginal">ಸಣ್ಣ & ಅತಿ ಸಣ್ಣ ರೈತರು (Small & Marginal &lt;= 5 ac)</option>
              <option value="General">ಸಾಮಾನ್ಯ ವರ್ಗ (General)</option>
              <option value="SC/ST">ಪರಿಶಿಷ್ಟ ಜಾತಿ / ಪಂಗಡ (SC/ST)</option>
              <option value="Women">ಮಹಿಳಾ ರೈತರು (Women Farmers)</option>
              <option value="Not sure">ಖಚಿತವಿಲ್ಲ (Not sure)</option>
            </select>
          </div>

          {/* Submit Button */}
          <div className="flex items-end">
            <button
              type="submit"
              disabled={evaluating}
              className="w-full py-2.5 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white text-xs sm:text-sm font-bold shadow-md transition-colors flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-[#D8AA48]" />
              <span>{evaluating ? 'ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...' : 'ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Results Section */}
      {evalResult && (
        <div className="space-y-6">
          
          {/* Summary Banner */}
          <div className="flex flex-wrap items-center justify-between p-4 rounded-2xl bg-[#EAF3E9] dark:bg-[#152E22] border border-[#75A96A]/40 text-xs text-[#174C36] dark:text-[#92C987] font-semibold gap-3">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-[#2F7650]" />
              <span className="font-kannada text-sm">
                ಒಟ್ಟು {evalResult.total_evaluated} ಯೋಜನೆಗಳನ್ನು ಪರಿಶೀಲಿಸಲಾಗಿದೆ. {evalResult.eligible_count} ಯೋಜನೆಗಳಲ್ಲಿ ನೀವು ಸಂಭಾವ್ಯ ಅರ್ಹರಾಗಿದ್ದೀರಿ.
              </span>
            </div>
            <span className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">
              Evaluation timestamp: {new Date().toLocaleTimeString()}
            </span>
          </div>

          {/* Cards Breakdown: PASS, UNKNOWN, FAIL */}
          <div className="space-y-4">
            {evalResult.results.map((item) => {
              const isPass = item.status === 'PASS';
              const isUnknown = item.status === 'UNKNOWN';
              const isFail = item.status === 'FAIL';

              return (
                <div
                  key={item.scheme_id}
                  className={`p-6 rounded-3xl border transition-all bg-white dark:bg-[#11221A] shadow-sm ${
                    isPass
                      ? 'border-green-300 dark:border-green-800/80 bg-gradient-to-r from-green-50/20 to-transparent'
                      : isUnknown
                      ? 'border-amber-300 dark:border-amber-800/80 bg-gradient-to-r from-amber-50/20 to-transparent'
                      : 'border-red-200 dark:border-red-900/60 bg-gradient-to-r from-red-50/10 to-transparent opacity-90'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    
                    {/* Status Badge & Name */}
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        {isPass && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-green-100 dark:bg-green-950 text-green-800 dark:text-green-300 border border-green-300">
                            <CheckCircle className="w-3.5 h-3.5" />
                            <span>ಅರ್ಹತೆ ಇದೆ (PASS)</span>
                          </span>
                        )}
                        {isUnknown && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300">
                            <HelpCircle className="w-3.5 h-3.5" />
                            <span>ಮಾಹಿತಿ ಅಪೂರ್ಣ (UNKNOWN)</span>
                          </span>
                        )}
                        {isFail && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300 border border-red-200">
                            <XCircle className="w-3.5 h-3.5" />
                            <span>ಅರ್ಹತೆ ಹೊಂದಿಲ್ಲ (FAIL)</span>
                          </span>
                        )}
                        <span className="text-xs text-[#69766D] dark:text-[#9BB0A4] font-semibold">
                          {item.scheme_id} • {item.department}
                        </span>
                      </div>

                      <h3 className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                        {item.scheme_name_kn}
                      </h3>
                      <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                        {item.scheme_name}
                      </p>
                    </div>

                    {/* Action Link */}
                    <div className="shrink-0 flex items-center gap-2">
                      <a
                        href={item.official_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-3.5 py-2 rounded-xl text-xs font-bold bg-[#174C36] hover:bg-[#123B2B] text-white shadow transition-colors"
                      >
                        <span>ಅಧಿಕೃತ ಅರ್ಜಿ (Apply)</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>

                  {/* Explanation Paragraph */}
                  <div className="mt-4 p-3.5 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] text-xs leading-relaxed space-y-1">
                    <p className="font-kannada font-bold text-[#19251E] dark:text-[#EDF3EF]">
                      {item.explanation_kn}
                    </p>
                    <p className="text-[#69766D] dark:text-[#9BB0A4]">
                      {item.explanation}
                    </p>
                  </div>

                  {/* Criteria Checklist Breakdown */}
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    {/* Matched rules */}
                    {item.matched_conditions.length > 0 && (
                      <div className="space-y-1">
                        <span className="font-bold text-green-700 dark:text-green-400 block">
                          ✓ ಹೊಂದಾಣಿಕೆಯಾದ ಮಾನದಂಡಗಳು (Passed Criteria):
                        </span>
                        <ul className="space-y-1 text-[#19251E] dark:text-[#EDF3EF]">
                          {item.matched_conditions.map((m, idx) => (
                            <li key={idx} className="flex items-start gap-1.5">
                              <span className="text-green-600 font-bold">•</span>
                              <span>{m}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Failing or missing rules */}
                    {(item.failing_conditions.length > 0 || item.missing_information.length > 0) && (
                      <div className="space-y-1">
                        {item.failing_conditions.length > 0 && (
                          <>
                            <span className="font-bold text-red-600 dark:text-red-400 block">
                              ✕ ಅನರ್ಹತೆಯ ಕಾರಣಗಳು (Failing Criteria):
                            </span>
                            <ul className="space-y-1 text-red-700 dark:text-red-300">
                              {item.failing_conditions.map((f, idx) => (
                                <li key={idx} className="flex items-start gap-1.5">
                                  <span>•</span>
                                  <span>{f}</span>
                                </li>
                              ))}
                            </ul>
                          </>
                        )}

                        {item.missing_information.length > 0 && (
                          <>
                            <span className="font-bold text-amber-700 dark:text-amber-400 block">
                              ? ಅಗತ್ಯವಿರುವ ಅಪೂರ್ಣ ವಿವರಗಳು (Missing Info):
                            </span>
                            <ul className="space-y-1 text-amber-800 dark:text-amber-300">
                              {item.missing_information.map((miss, idx) => (
                                <li key={idx} className="flex items-start gap-1.5">
                                  <span>•</span>
                                  <span>{miss}</span>
                                </li>
                              ))}
                            </ul>
                          </>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Required Documents Checklist */}
                  {item.required_documents.length > 0 && isPass && (
                    <div className="mt-3 pt-3 border-t border-[#E2E8DF] dark:border-[#1E382B] text-xs flex flex-wrap items-center gap-2 text-[#69766D] dark:text-[#9BB0A4]">
                      <span className="font-bold text-[#19251E] dark:text-[#EDF3EF]">ಕಡ್ಡಾಯ ದಾಖಲೆಗಳು:</span>
                      {item.required_documents.map((doc, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] font-medium text-[11px]">
                          {doc}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Legal / Evaluation Disclaimer */}
          <div className="p-4 rounded-2xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-[11px] text-[#69766D] dark:text-[#9BB0A4] leading-relaxed">
            <strong className="text-[#19251E] dark:text-[#EDF3EF]">ಕಾನೂನು ಸೂಚನೆ (Disclaimer): </strong>
            ಈ ಅರ್ಹತಾ ಪರಿಶೀಲನೆಯು ರೈತರು ಒದಗಿಸಿದ ವಿವರಗಳ ಆಧಾರದ ಮೇಲೆ ಮಾಡಿದ ತಾಂತ್ರಿಕ ಶಿಫಾರಸಾಗಿದೆ. ಅಂತಿಮ ಅನುಮೋದನೆಯು ಸಂಬಂಧಪಟ್ಟ ಸರ್ಕಾರಿ ಇಲಾಖೆಗಳು ಹಾಗೂ ಗ್ರಾಮ ಮಟ್ಟದ ದಾಖಲೆಗಳ (RTC ಪಹಣಿ) ತಪಾಸಣೆಗೆ ಒಳಪಟ್ಟಿರುತ್ತದೆ.
          </div>
        </div>
      )}
    </div>
  );
};
