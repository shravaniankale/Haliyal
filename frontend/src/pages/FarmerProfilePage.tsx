import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User as UserIcon,
  Phone,
  MapPin,
  Sprout,
  Mic,
  Save,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';

export const FarmerProfilePage: React.FC = () => {
  const { user, profile, refreshProfile, isAuthenticated } = useAuth();
  const { setRegionalDialect } = useLanguage();
  const navigate = useNavigate();

  const [districts, setDistricts] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [district, setDistrict] = useState('Belagavi');
  const [taluk, setTaluk] = useState('Belagavi');
  const [village, setVillage] = useState('');
  const [landAcres, setLandAcres] = useState<string>('3.0');
  const [landOwnership, setLandOwnership] = useState('Own');
  const [irrigationType, setIrrigationType] = useState('Rainfed');
  const [farmerCategory, setFarmerCategory] = useState('Small & Marginal');
  const [selectedSpeech, setSelectedSpeech] = useState('North Karnataka');
  const [selectedCrops, setSelectedCrops] = useState<string[]>(['Paddy']);

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const allCrops = ['Paddy', 'Ragi', 'Jowar', 'Maize', 'Cotton', 'Groundnut', 'Tur', 'Sugarcane'];

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated]);

  useEffect(() => {
    async function loadDistricts() {
      try {
        const d = await api.getDistricts();
        setDistricts(d);
      } catch (e) {}
    }
    loadDistricts();
  }, []);

  useEffect(() => {
    if (profile) {
      setName(profile.name || user?.name || '');
      setDistrict(profile.district || 'Belagavi');
      setTaluk(profile.taluk || 'Belagavi');
      setVillage(profile.village || '');
      setLandAcres(profile.land_acres ? String(profile.land_acres) : '');
      setLandOwnership(profile.land_ownership || 'Own');
      setIrrigationType(profile.irrigation_type || 'Rainfed');
      setFarmerCategory(profile.farmer_category || 'Small & Marginal');
      setSelectedSpeech(profile.regional_speech_preference || 'North Karnataka');
      setSelectedCrops(profile.crops_grown || ['Paddy']);
    }
  }, [profile, user]);

  const toggleCrop = (c: string) => {
    if (selectedCrops.includes(c)) {
      setSelectedCrops(selectedCrops.filter((x) => x !== c));
    } else {
      setSelectedCrops([...selectedCrops, c]);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);

    try {
      const acresVal = landAcres ? parseFloat(landAcres) : undefined;
      await api.updateFarmerProfile({
        name,
        district,
        taluk,
        village,
        land_acres: isNaN(acresVal as any) ? undefined : acresVal,
        land_ownership: landOwnership,
        irrigation_type: irrigationType,
        farmer_category: farmerCategory,
        regional_speech_preference: selectedSpeech,
        crops_grown: selectedCrops,
      });

      setRegionalDialect(selectedSpeech as any);
      await refreshProfile();
      setSuccessMsg('ಪ್ರೊಫೈಲ್ ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ (Profile updated successfully)!');
      setTimeout(() => setSuccessMsg(null), 3500);
    } catch (err: any) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const currentDistObj = districts.find((d) => d.name === district);
  const talukList = currentDistObj ? currentDistObj.taluks : [district];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <UserIcon className="w-4 h-4 text-[#2F7650]" />
          <span>Farmer Profile Management</span>
        </div>
        <h1 className="text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ರೈತರ ಪ್ರೊಫೈಲ್ & ವಿವರಗಳು (My Profile)
        </h1>
        <p className="text-xs sm:text-sm text-[#69766D] dark:text-[#9BB0A4]">
          Manage your agricultural profile, landholding, cultivated crops, and preferred regional Kannada speech style
        </p>
      </div>

      {successMsg && (
        <div className="p-4 rounded-2xl bg-green-50 dark:bg-green-950/40 border border-green-200 dark:border-green-800 flex items-center gap-2.5 text-xs font-bold text-green-800 dark:text-green-300">
          <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Profile Form Card */}
      <form onSubmit={handleSave} className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 sm:p-10 shadow-sm space-y-8">
        
        {/* Section 1: Basic Info */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada border-b border-[#E2E8DF] dark:border-[#1E382B] pb-2">
            ಮೂಲ ವಿವರಗಳು (Basic Credentials)
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಹೆಸರು (Full Name)
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ನೋಂದಾಯಿತ ಮೊಬೈಲ್ (Mobile)
              </label>
              <input
                type="text"
                disabled
                value={user?.mobile || ''}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-gray-100 dark:bg-gray-800 text-[#69766D] cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Regional Dialect & Location */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada border-b border-[#E2E8DF] dark:border-[#1E382B] pb-2 flex items-center gap-2">
            <Mic className="w-4 h-4 text-[#D8AA48]" />
            <span>ಸ್ಥಳ & ಕನ್ನಡ ಆಡುಭಾಷೆ ಶೈಲಿ (Location & Speech Style)</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಜಿಲ್ಲೆ (District)
              </label>
              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              >
                {districts.map((d) => (
                  <option key={d.name} value={d.name}>
                    {d.name_kn} ({d.name})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ತಾಲೂಕು (Taluk)
              </label>
              <select
                value={taluk}
                onChange={(e) => setTaluk(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              >
                {talukList.map((t: string) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಗ್ರಾಮ (Village)
              </label>
              <input
                type="text"
                value={village}
                onChange={(e) => setVillage(e.target.value)}
                placeholder="Village name"
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ಕನ್ನಡ ಧ್ವನಿ ಶೈಲಿ (Regional Kannada Speech Dialect)
            </label>
            <select
              value={selectedSpeech}
              onChange={(e) => setSelectedSpeech(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#174C36] dark:text-[#75A96A] font-bold"
            >
              <option value="North Karnataka">ಉತ್ತರ ಕರ್ನಾಟಕ (ಧಾರವಾಡ, ಬೆಳಗಾವಿ, ವಿಜಯಪುರ, ಕಲಬುರಗಿ ಶೈಲಿ)</option>
              <option value="South Karnataka">ದಕ್ಷಿಣ ಕರ್ನಾಟಕ (ಮೈಸೂರು, ಮಂಡ್ಯ, ಹಾಸನ, ಬೆಂಗಳೂರು ಶೈಲಿ)</option>
              <option value="Standard Kannada">ಶಿಷ್ಟ ಕನ್ನಡ (ಸರ್ಕಾರಿ ಅಧಿಕೃತ ಭಾಷಾ ಶೈಲಿ)</option>
            </select>
          </div>
        </div>

        {/* Section 3: Landholding Details */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada border-b border-[#E2E8DF] dark:border-[#1E382B] pb-2">
            ಕೃಷಿ ಭೂಮಿ ವಿವರಗಳು (Landholding Circumstances)
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (Acres)
              </label>
              <input
                type="number"
                step="0.1"
                value={landAcres}
                onChange={(e) => setLandAcres(e.target.value)}
                placeholder="e.g. 3.0"
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಮಾಲೀಕತ್ವ (Ownership)
              </label>
              <select
                value={landOwnership}
                onChange={(e) => setLandOwnership(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              >
                <option value="Own">ಸ್ವಂತ ಭೂಮಿ (Own Title)</option>
                <option value="Tenant">ಗೇಣಿ ಭೂಮಿ (Tenant / Leased)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ನೀರಾವರಿ (Irrigation)
              </label>
              <select
                value={irrigationType}
                onChange={(e) => setIrrigationType(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              >
                <option value="Rainfed">ಖುಷ್ಕಿ / ಮಳೆ ಆಶ್ರಿತ (Rainfed)</option>
                <option value="Borewell">ಕೊಳವೆಬಾವಿ (Borewell)</option>
                <option value="Canal">ಕಾಲುವೆ ನೀರಾವರಿ (Canal)</option>
                <option value="Drip">ಹನಿ ನೀರಾವರಿ (Drip)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ರೈತರ ವರ್ಗ (Category)
              </label>
              <select
                value={farmerCategory}
                onChange={(e) => setFarmerCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              >
                <option value="Small & Marginal">ಸಣ್ಣ & ಅತಿ ಸಣ್ಣ (Small & Marginal)</option>
                <option value="General">ಸಾಮಾನ್ಯ ವರ್ಗ (General)</option>
                <option value="SC/ST">ಪರಿಶಿಷ್ಟ ಜಾತಿ / ಪಂಗಡ (SC/ST)</option>
                <option value="Women">ಮಹಿಳಾ ರೈತರು (Women)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 4: Cultivated Crops Selection */}
        <div className="space-y-3">
          <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
            ನೀವು ಬೆಳೆಯುವ ಪ್ರಮುಖ ಬೆಳೆಗಳು (Cultivated Crops):
          </label>
          <div className="flex flex-wrap gap-2">
            {allCrops.map((c) => {
              const isSelected = selectedCrops.includes(c);
              return (
                <button
                  type="button"
                  key={c}
                  onClick={() => toggleCrop(c)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold border transition-colors ${
                    isSelected
                      ? 'bg-[#174C36] text-white border-[#174C36]'
                      : 'bg-[#F7F9F5] dark:bg-[#0B1711] border-[#E2E8DF] dark:border-[#1E382B] text-[#69766D]'
                  }`}
                >
                  {c} {isSelected && '✓'}
                </button>
              );
            })}
          </div>
        </div>

        {/* Submit Save Button */}
        <div className="pt-4 border-t border-[#E2E8DF] dark:border-[#1E382B] flex items-center justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white text-xs sm:text-sm font-bold shadow-md transition-colors flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'ಉಳಿಸಲಾಗುತ್ತಿದೆ...' : 'ಪ್ರೊಫೈಲ್ ಉಳಿಸಿ (Save Profile)'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
