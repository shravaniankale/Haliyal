import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sprout, Phone, Lock, User, MapPin, Mic, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const { setRegionalDialect } = useLanguage();
  const navigate = useNavigate();

  const [districts, setDistricts] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('Belagavi');
  const [selectedTaluk, setSelectedTaluk] = useState('Belagavi');
  const [village, setVillage] = useState('');
  const [preferredLang, setPreferredLang] = useState<'kn' | 'en'>('kn');
  const [detectedRegion, setDetectedRegion] = useState('North Karnataka');
  const [selectedSpeechStyle, setSelectedSpeechStyle] = useState('North Karnataka');
  
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch verified Karnataka districts & taluks
  useEffect(() => {
    async function loadDistricts() {
      try {
        const data = await api.getDistricts();
        setDistricts(data);
        if (data.length > 0) {
          const belagavi = data.find((d: any) => d.name === 'Belagavi') || data[0];
          setSelectedDistrict(belagavi.name);
          setDetectedRegion(belagavi.region);
          setSelectedSpeechStyle(belagavi.region);
          if (belagavi.taluks && belagavi.taluks.length > 0) {
            setSelectedTaluk(belagavi.taluks[0]);
          }
        }
      } catch (err) {
        console.error('Failed to load districts:', err);
      }
    }
    loadDistricts();
  }, []);

  // Update region classification and taluk list when district changes
  const handleDistrictChange = (distName: string) => {
    setSelectedDistrict(distName);
    const dist = districts.find((d) => d.name === distName);
    if (dist) {
      setDetectedRegion(dist.region);
      setSelectedSpeechStyle(dist.region);
      if (dist.taluks && dist.taluks.length > 0) {
        setSelectedTaluk(dist.taluks[0]);
      }
    }
  };

  const currentDistrictObj = districts.find((d) => d.name === selectedDistrict);
  const availableTaluks = currentDistrictObj ? currentDistrictObj.taluks : [selectedDistrict];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !mobile.trim() || !password.trim()) {
      setError('ದಯವಿಟ್ಟು ಎಲ್ಲಾ ಅಗತ್ಯ ಕ್ಷೇತ್ರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ.');
      return;
    }
    if (mobile.trim().length !== 10) {
      setError('ಮೊಬೈಲ್ ಸಂಖ್ಯೆ 10 ಅಂಕಿಗಳಾಗಿರಬೇಕು.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await register({
        name: name.trim(),
        mobile: mobile.trim(),
        password: password,
        district: selectedDistrict,
        taluk: selectedTaluk,
        village: village.trim() || null,
        preferred_language: preferredLang,
        preferred_speech_style: selectedSpeechStyle,
      });

      setRegionalDialect(selectedSpeechStyle as any);
      navigate('/voice-assistant');
    } catch (err: any) {
      setError(err.message || 'ನೋಂದಣಿ ವಿಫಲವಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-xl bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-xl p-8 sm:p-10">
        
        {/* Header */}
        <div className="text-center space-y-2 mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#174C36] to-[#2F7650] flex items-center justify-center text-white mx-auto shadow-md">
            <Sprout className="w-8 h-8 text-[#D8AA48]" />
          </div>
          <h2 className="text-2xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] tracking-tight">
            ರೈತರ ನೋಂದಣಿ (Farmer Registration)
          </h2>
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
            Register to receive personalized government scheme guidance and regional Kannada voice AI
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 flex items-center gap-2 text-xs text-red-700 dark:text-red-300">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="font-kannada">{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
          
          {/* Farmer Full Name */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
              ರೈತರ ಪೂರ್ಣ ಹೆಸರು (Farmer Full Name) *
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="ಉದಾ. ಬಸವರಾಜ್ ಪಾಟೀಲ್ / Basavaraj Patil"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
              />
              <User className="w-4 h-4 absolute left-3.5 top-3 text-[#69766D]" />
            </div>
          </div>

          {/* Mobile & Password Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಮೊಬೈಲ್ ಸಂಖ್ಯೆ (Mobile Number) *
              </label>
              <div className="relative">
                <input
                  type="tel"
                  placeholder="10-digit Mobile"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  maxLength={10}
                  required
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
                />
                <Phone className="w-4 h-4 absolute left-3.5 top-3 text-[#69766D]" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಪಾಸ್‌ವರ್ಡ್ (Password) *
              </label>
              <div className="relative">
                <input
                  type="password"
                  placeholder="Create secure password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
                />
                <Lock className="w-4 h-4 absolute left-3.5 top-3 text-[#69766D]" />
              </div>
            </div>
          </div>

          {/* District Selection (Crucial - Auto configures North/South Region) */}
          <div className="p-4 rounded-2xl bg-[#EAF3E9]/60 dark:bg-[#152E22]/40 border border-[#75A96A]/30 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#174C36] dark:text-[#92C987] font-kannada flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-[#D8AA48]" />
                <span>ಕರ್ನಾಟಕ ಜಿಲ್ಲೆ (District) *</span>
              </label>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#174C36] text-white">
                {detectedRegion}
              </span>
            </div>

            <select
              value={selectedDistrict}
              onChange={(e) => handleDistrictChange(e.target.value)}
              className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-white dark:bg-[#11221A] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
            >
              {districts.map((d) => (
                <option key={d.name} value={d.name}>
                  {d.name_kn} ({d.name}) — {d.region}
                </option>
              ))}
            </select>

            {/* Configured regional classification info */}
            <div className="flex items-start gap-2 text-xs text-[#2F7650] dark:text-[#92C987]">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-[#D8AA48] mt-0.5" />
              <span>
                {selectedDistrict} ಜಿಲ್ಲೆಗೆ <strong className="font-bold">{detectedRegion}</strong> ಪ್ರಾದೇಶಿಕ ಭಾಷಾ ಶೈಲಿಯನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಸಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ.
              </span>
            </div>
          </div>

          {/* Taluk and Village */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ತಾಲೂಕು (Taluk) *
              </label>
              <select
                value={selectedTaluk}
                onChange={(e) => setSelectedTaluk(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
              >
                {availableTaluks.map((t: string) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಗ್ರಾಮ (Village - Optional)
              </label>
              <input
                type="text"
                placeholder="Village name"
                value={village}
                onChange={(e) => setVillage(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
              />
            </div>
          </div>

          {/* Speech Preference & Language Customization */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada">
                ಪ್ರಾಥಮಿಕ ಭಾಷೆ (Language)
              </label>
              <select
                value={preferredLang}
                onChange={(e) => setPreferredLang(e.target.value as any)}
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              >
                <option value="kn">ಕನ್ನಡ (Kannada - Recommended)</option>
                <option value="en">English</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1 font-kannada flex items-center gap-1">
                <Mic className="w-3.5 h-3.5 text-[#D8AA48]" />
                <span>ಕನ್ನಡ ಧ್ವನಿ ಶೈಲಿ (Speech Dialect)</span>
              </label>
              <select
                value={selectedSpeechStyle}
                onChange={(e) => setSelectedSpeechStyle(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              >
                <option value="North Karnataka">ಉತ್ತರ ಕರ್ನಾಟಕ (ಧಾರವಾಡ/ಬೆಳಗಾವಿ)</option>
                <option value="South Karnataka">ದಕ್ಷಿಣ ಕರ್ನಾಟಕ (ಮೈಸೂರು/ಮಂಡ್ಯ)</option>
                <option value="Standard Kannada">ಶಿಷ್ಟ ಕನ್ನಡ (ಸರ್ಕಾರಿ ಅಧಿಕೃತ)</option>
              </select>
            </div>
          </div>

          {/* Privacy Note */}
          <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4] leading-relaxed pt-1">
            ಗಮನಿಸಿ: ನಿಮ್ಮ ಆಧಾರ್ ಸಂಖ್ಯೆ ಅಥವಾ ಬ್ಯಾಂಕ್ ಪಾಸ್‌ವರ್ಡ್ ಅನ್ನು ಇಲ್ಲಿ ಸಂಗ್ರಹಿಸುವುದಿಲ್ಲ. ಕೃಷಿ ಮಾಹಿತಿ ಮತ್ತು ಯೋಜನೆಗಳ ಪರಿಶೀಲನೆಗಾಗಿ ಮಾತ್ರ ಈ ವಿವರಗಳು ಬಳಕೆಯಾಗುತ್ತವೆ.
          </p>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white font-bold text-sm shadow-md transition-colors disabled:opacity-50 mt-2"
          >
            {loading ? 'ನೋಂದಾಯಿಸಲಾಗುತ್ತಿದೆ...' : 'ನೋಂದಣಿ ಪೂರ್ಣಗೊಳಿಸಿ (Complete Registration)'}
          </button>
        </form>

        {/* Login Link */}
        <div className="mt-8 text-center text-xs text-[#69766D] dark:text-[#9BB0A4]">
          <span>ಈಗಾಗಲೇ ಖಾತೆ ಹೊಂದಿದ್ದೀರಾ? </span>
          <Link
            to="/login"
            className="font-bold text-[#174C36] dark:text-[#75A96A] hover:underline"
          >
            ಲಾಗಿನ್ ಆಗಿ (Login here)
          </Link>
        </div>
      </div>
    </div>
  );
};
