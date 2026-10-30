import React, { useState, useEffect } from 'react';
import {
  Sprout,
  Sun,
  Droplets,
  Calendar,
  Layers,
  Bug,
  Award,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';
import { api } from '../services/api';
import { Crop } from '../types';
import { useLanguage } from '../context/LanguageContext';

export const CropGuidancePage: React.FC = () => {
  const { language } = useLanguage();
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<Crop | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCrops() {
      try {
        const data = await api.getCrops();
        setCrops(data);
        if (data.length > 0) {
          setSelectedCrop(data[0]);
        }
      } catch (err) {
        console.error('Failed to load crops:', err);
      } finally {
        setLoading(false);
      }
    }
    loadCrops();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <Sprout className="w-4 h-4 text-[#2F7650]" />
          <span>Karnataka Agro-Climatic Agronomy</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ಕರ್ನಾಟಕ ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ (Crop Guidance)
        </h1>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] max-w-3xl leading-relaxed">
          {language === 'kn'
            ? 'ಕರ್ನಾಟಕದ ಪ್ರಮುಖ ಆಹಾರ, ಎಣ್ಣೆಕಾಳು ಹಾಗೂ ವಾಣಿಜ್ಯ ಬೆಳೆಗಳ ಬಿತ್ತನೆ, ಸೂಕ್ತ ಮಣ್ಣು, ಹವಾಮಾನ, ನೀರಿನ ನಿರ್ವಹಣೆ ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣದ ಸಮಗ್ರ ಮಾಹಿತಿ.'
            : 'Scientific agronomic practices, high-yield varieties, pest management, and irrigation requirements for Karnataka crops.'}
        </p>
      </div>

      {/* Crop Selector Tabs */}
      <div className="flex overflow-x-auto pb-2 gap-2 scrollbar-thin">
        {crops.map((c) => {
          const isSelected = selectedCrop?.crop_id === c.crop_id;
          return (
            <button
              key={c.crop_id}
              onClick={() => setSelectedCrop(c)}
              className={`px-4 py-2.5 rounded-2xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all flex items-center gap-2 ${
                isSelected
                  ? 'bg-[#174C36] text-white shadow-md'
                  : 'bg-white dark:bg-[#11221A] text-[#19251E] dark:text-[#EDF3EF] border border-[#E2E8DF] dark:border-[#1E382B] hover:border-[#2F7650]'
              }`}
            >
              <span className="font-kannada">{c.name_kn}</span>
              <span className="text-[11px] opacity-80">({c.name.split(' ')[0]})</span>
            </button>
          );
        })}
      </div>

      {/* Selected Crop Details Display */}
      {selectedCrop && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Main Info Box (8 cols) */}
          <div className="lg:col-span-8 bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 sm:p-8 shadow-sm space-y-6">
            
            <div className="border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                    {selectedCrop.name_kn} ({selectedCrop.name})
                  </h2>
                  <p className="text-xs font-semibold italic text-[#69766D] dark:text-[#9BB0A4] mt-0.5">
                    Scientific Name: {selectedCrop.scientific_name}
                  </p>
                </div>
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987]">
                  UAS Bengaluru / Dharwad Certified
                </span>
              </div>
            </div>

            {/* Growth Stages Pipeline */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
                <Layers className="w-4 h-4 text-[#2F7650]" />
                <span>ಬೆಳವಣಿಗೆಯ ಹಂತಗಳು (Growth Stages Pipeline)</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {selectedCrop.growth_stages.map((stage, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] flex items-center gap-2.5 text-xs font-medium text-[#19251E] dark:text-[#EDF3EF]"
                  >
                    <span className="w-5 h-5 rounded-full bg-[#174C36] text-white flex items-center justify-center text-[10px] font-bold shrink-0">
                      {idx + 1}
                    </span>
                    <span>{stage}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Soil & Climate */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-4 rounded-2xl bg-[#EAF3E9]/50 dark:bg-[#152E22]/30 border border-[#75A96A]/30 space-y-1">
                <span className="text-xs font-bold text-[#174C36] dark:text-[#92C987] font-kannada flex items-center gap-1.5">
                  <Sun className="w-4 h-4 text-[#D8AA48]" />
                  <span>ಸೂಕ್ತ ಮಣ್ಣು (Suitable Soil):</span>
                </span>
                <p className="text-xs text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-relaxed">
                  {selectedCrop.soil_kn}
                </p>
                <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4]">{selectedCrop.soil}</p>
              </div>

              <div className="p-4 rounded-2xl bg-[#EAF3E9]/50 dark:bg-[#152E22]/30 border border-[#75A96A]/30 space-y-1">
                <span className="text-xs font-bold text-[#174C36] dark:text-[#92C987] font-kannada flex items-center gap-1.5">
                  <Droplets className="w-4 h-4 text-blue-500" />
                  <span>ಹವಾಮಾನ & ಮಳೆ (Climate):</span>
                </span>
                <p className="text-xs text-[#19251E] dark:text-[#EDF3EF] leading-relaxed">
                  {selectedCrop.climate}
                </p>
              </div>
            </div>

            {/* Irrigation & Harvesting */}
            <div className="space-y-4 pt-2">
              <div className="p-4 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
                <span className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-1.5">
                  <Droplets className="w-4 h-4 text-cyan-600" />
                  <span>ನೀರಿನ ಅವಶ್ಯಕತೆ (Water & Irrigation):</span>
                </span>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] leading-relaxed">
                  {selectedCrop.water_requirement}
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-[#F7F9F5] dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
                <span className="text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-[#D8AA48]" />
                  <span>ಕಟಾವು ವಿಧಾನ (Harvesting Guidelines):</span>
                </span>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] leading-relaxed">
                  {selectedCrop.harvesting}
                </p>
              </div>
            </div>
          </div>

          {/* Side Column: Varieties & Pest Management (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Recommended High-Yield Seed Varieties */}
            <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
                <Award className="w-4 h-4 text-[#D8AA48]" />
                <span>ಉನ್ನತ ಇಳುವರಿ ತಳಿಗಳು (Recommended Varieties)</span>
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedCrop.varieties.map((v) => (
                  <span
                    key={v}
                    className="px-3 py-1.5 rounded-xl bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] text-xs font-bold border border-[#75A96A]/30"
                  >
                    {v}
                  </span>
                ))}
              </div>
              <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4] pt-2 border-t border-[#E2E8DF] dark:border-[#1E382B]">
                ಲಭ್ಯತೆ: ಸ್ಥಳೀಯ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ (RSK) ಮತ್ತು ಕರ್ನಾಟಕ ರಾಜ್ಯ ಬೀಜ ನಿಗಮ (KSSC).
              </p>
            </div>

            {/* Common Pests and Diseases */}
            <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-red-200 dark:border-red-900/40 p-6 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-red-700 dark:text-red-400 font-kannada flex items-center gap-2">
                <Bug className="w-4 h-4 text-red-600" />
                <span>ಪ್ರಮುಖ ಕೀಟ & ರೋಗಗಳು (Pests & Diseases)</span>
              </h3>
              <p className="text-xs text-[#19251E] dark:text-[#EDF3EF] leading-relaxed font-medium">
                {selectedCrop.pests}
              </p>
              <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 text-[11px] text-red-800 dark:text-red-300 space-y-1">
                <span className="font-bold">ನಿರ್ವಹಣಾ ಸಲಹೆ: </span>
                <span>ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸುವ ಮುನ್ನ ಸಮಗ್ರ ಕೀಟ ನಿರ್ವಹಣೆ (IPM) ಹಾಗೂ ಜೈವಿಕ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳನ್ನು ಅನುಸರಿಸಿ.</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
