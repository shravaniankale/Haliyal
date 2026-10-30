import React, { useState, useEffect } from 'react';
import {
  FlaskConical,
  Sprout,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Leaf,
  Layers,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';

export const FertilizerGuidancePage: React.FC = () => {
  const { language } = useLanguage();

  const [crop, setCrop] = useState('Paddy');
  const [soilType, setSoilType] = useState('Red Loamy');
  const [growthStage, setGrowthStage] = useState('Basal / Sowing');
  const [guidance, setGuidance] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchGuidance = async () => {
    setLoading(true);
    try {
      const data = await api.getFertilizerGuidance({
        crop,
        soil_type: soilType,
        growth_stage: growthStage,
      });
      setGuidance(data);
    } catch (err) {
      console.error('Failed to load fertilizer guidance:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGuidance();
  }, [crop, soilType, growthStage]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <FlaskConical className="w-4 h-4 text-[#2F7650]" />
          <span>Balanced Crop Nutrition Management</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ರಸಗೊಬ್ಬರ & ಪೋಷಕಾಂಶ ಮಾರ್ಗದರ್ಶನ (Fertilizer Guidance)
        </h1>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] max-w-3xl leading-relaxed">
          {language === 'kn'
            ? 'ಬೆಳೆ, ಮಣ್ಣಿನ ವಿಧ ಹಾಗೂ ಬೆಳವಣಿಗೆಯ ಹಂತಕ್ಕೆ ತಕ್ಕಂತೆ ವೈಜ್ಞಾನಿಕ NPK ಗೊಬ್ಬರ ಬಳಕೆ, ಲಘು ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ ನಿವಾರಣೆ ಮತ್ತು ಸಾವಯವ ಪರ್ಯಾಯಗಳ ಮಾಹಿತಿ.'
            : 'Scientific NPK dosage, micronutrient deficiency management, and organic alternatives tailored to crop stage and Karnataka soil types.'}
        </p>
      </div>

      {/* Selectors Bar */}
      <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          
          {/* Crop Selector */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1.5 font-kannada">
              ಬೆಳೆ (Select Crop)
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
              <option value="Tur">ತೊಗರಿ (Tur)</option>
              <option value="Sugarcane">ಕಬ್ಬು (Sugarcane)</option>
            </select>
          </div>

          {/* Soil Type Selector */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1.5 font-kannada">
              ಮಣ್ಣಿನ ವಿಧ (Soil Type)
            </label>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="Red Loamy">ಕೆಂಪು ಗೋಡು ಮಣ್ಣು (Red Loamy)</option>
              <option value="Black Cotton">ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು (Black Cotton / Regur)</option>
              <option value="Sandy Loam">ಮರಳು ಮಿಶ್ರಿತ ಗೋಡು (Sandy Loam)</option>
              <option value="Alluvial">ಮೆಕ್ಕಲು ಮಣ್ಣು (Alluvial)</option>
              <option value="Laterite">ಜಂಬಿಟ್ಟಿಗೆ ಮಣ್ಣು (Laterite)</option>
            </select>
          </div>

          {/* Growth Stage Selector */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1.5 font-kannada">
              ಬೆಳೆಯ ಹಂತ (Growth Stage)
            </label>
            <select
              value={growthStage}
              onChange={(e) => setGrowthStage(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              <option value="Basal / Sowing">ಬಿತ್ತನೆ ಪೂರ್ವ / ಪ್ರಾರಂಭಿಕ (Basal / Sowing)</option>
              <option value="Vegetative / Tillering">ಬೆಳವಣಿಗೆ / ಕವಲೊಡೆಯುವ ಹಂತ (Vegetative)</option>
              <option value="Flowering / Panicle">ಹೂವಾಡುವ / ತೆನೆ ಬರುವ ಹಂತ (Flowering)</option>
              <option value="Maturity">ಕಾಳು ಕಟ್ಟುವ ಹಂತ (Maturity)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Guidance Content */}
      {guidance && (
        <div className="space-y-8">
          
          {/* NPK Ratio Highlight Box */}
          <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-[#174C36] via-[#123B2B] to-[#2F7650] text-white shadow-xl space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
              ಪ್ರಮಾಣಿತ N:P:K ಪೋಷಕಾಂಶ ಅನುಪಾತ (Recommended Dosage)
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              {guidance.recommended_npk}
            </h2>
            <p className="text-xs text-[#EAF3E9]/80 font-kannada leading-relaxed">
              *ಸೂಚನೆ: ಸಾರಜನಕ (N), ರಂಜಕ (P2O5), ಮತ್ತು ಪೊಟ್ಯಾಷ್ (K2O) ಸರಿಯಾದ ಪ್ರಮಾಣದಲ್ಲಿ ಬಳಸುವುದರಿಂದ ಇಳುವರಿ ಶೇ. 25-30 ರಷ್ಟು ಹೆಚ್ಚುತ್ತದೆ.
            </p>
          </div>

          {/* Application Breakdown Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Basal Application */}
            <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-[#174C36] dark:text-[#92C987]">
                <Layers className="w-4 h-4 text-[#D8AA48]" />
                <span>ಆರಂಭಿಕ ಗೊಬ್ಬರ ಬಳಕೆ (Basal Application)</span>
              </div>
              <p className="text-sm font-semibold text-[#19251E] dark:text-[#EDF3EF] leading-relaxed">
                {guidance.basal_guidance}
              </p>
            </div>

            {/* Top Dressing */}
            <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-[#2F7650] dark:text-[#75A96A]">
                <Sprout className="w-4 h-4 text-[#D8AA48]" />
                <span>ಮೇಲುಗೊಬ್ಬರ ಬಳಕೆ (Top Dressing Guidance)</span>
              </div>
              <p className="text-sm font-semibold text-[#19251E] dark:text-[#EDF3EF] leading-relaxed">
                {guidance.top_dressing_guidance}
              </p>
            </div>
          </div>

          {/* Micronutrient Advisory & Organic Alternatives */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Micronutrients */}
            <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-amber-700 dark:text-amber-400">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <span>ಲಘು ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ (Micronutrients)</span>
              </div>
              <p className="text-xs sm:text-sm text-[#19251E] dark:text-[#EDF3EF] leading-relaxed">
                {guidance.micronutrient_advisory}
              </p>
            </div>

            {/* Organic Alternatives */}
            <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-green-700 dark:text-green-400">
                <Leaf className="w-4 h-4 text-green-600" />
                <span>ಸಾವಯವ ಪರ್ಯಾಯಗಳು (Organic Alternatives)</span>
              </div>
              <ul className="space-y-2 text-xs text-[#19251E] dark:text-[#EDF3EF]">
                {guidance.organic_alternatives.map((org: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[#2F7650] shrink-0 mt-0.5" />
                    <span>{org}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Safe Application Protocols */}
          <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-[#2F7650]" />
              <span>ಸುರಕ್ಷಿತ ಬಳಕೆ ನಿಯಮಗಳು (Safe Application Guidelines)</span>
            </h3>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-[#69766D] dark:text-[#9BB0A4]">
              {guidance.safety_instructions.map((inst: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-[#174C36] dark:text-[#75A96A] font-bold">•</span>
                  <span>{inst}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Mandatory Soil Test Disclaimer */}
          <div className="p-5 rounded-2xl bg-[#EAF3E9]/80 dark:bg-[#152E22]/60 border border-[#75A96A]/40 flex items-start gap-3 text-xs text-[#174C36] dark:text-[#92C987] leading-relaxed">
            <Sparkles className="w-5 h-5 text-[#D8AA48] shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">ಮಣ್ಣು ಪರೀಕ್ಷೆ ಕಡ್ಡಾಯ ಸಲಹೆ (Soil Health Card Advisory):</p>
              <p className="mt-1">{guidance.soil_test_advisory}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
