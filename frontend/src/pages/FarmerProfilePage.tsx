import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User as UserIcon,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Save,
  CheckCircle2,
  AlertCircle,
  Volume2,
  Sun,
  Moon,
  Mic,
  Sliders,
  LogOut,
  Sparkles,
  Play,
  Square,
  ShieldCheck,
  Sprout,
  Tractor,
  Compass,
  Check,
  Bot
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSettings, RegionalDialect, VoiceGender, Theme } from '../context/SettingsContext';
import { api } from '../services/api';

interface DistrictOption {
  name: string;
  name_kn: string;
  region: string;
  taluks: string[];
}

export const FarmerProfilePage: React.FC = () => {
  const { user, profile, refreshProfile, isAuthenticated, logout } = useAuth();
  const {
    theme,
    setTheme,
    language,
    regionalDialect,
    setRegionalDialect,
    voiceGender,
    setVoiceGender,
    voiceAssistantEnabled,
    setVoiceAssistantEnabled,
    autoVoiceResponse,
    setAutoVoiceResponse,
    voiceInputEnabled,
    setVoiceInputEnabled,
    speechSpeed,
    setSpeechSpeed,
    t
  } = useSettings();
  const navigate = useNavigate();

  // District/Taluk data
  const [districts, setDistricts] = useState<DistrictOption[]>([]);
  const [availableTaluks, setAvailableTaluks] = useState<string[]>([]);

  // Section A: Personal Details State
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('Belagavi');
  const [selectedTaluk, setSelectedTaluk] = useState('Belagavi');
  const [accountCreatedAt, setAccountCreatedAt] = useState<string>('');

  // Agricultural Details State (Synchronized with AI Voice Assistant)
  const [village, setVillage] = useState('');
  const [landAcres, setLandAcres] = useState('');
  const [landOwnership, setLandOwnership] = useState('Own');
  const [primaryCrop, setPrimaryCrop] = useState('Paddy');
  const [farmerCategory, setFarmerCategory] = useState('Small & Marginal');
  const [irrigationType, setIrrigationType] = useState('Rainfed');
  const [soilType, setSoilType] = useState('Red Soil');
  const [season, setSeason] = useState('Kharif');
  const [cropStage, setCropStage] = useState('Tillering / Flowering');

  // Audio Preview State
  const [isPlayingPreview, setIsPlayingPreview] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const audioPreviewRef = useRef<HTMLAudioElement | null>(null);

  // Feedback states
  const [personalSaving, setPersonalSaving] = useState(false);
  const [personalSuccess, setPersonalSuccess] = useState<string | null>(null);
  const [personalError, setPersonalError] = useState<string | null>(null);

  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null);

  // Section C: Logout Confirmation Modal
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  // Redirect if unauthenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Load districts
  useEffect(() => {
    async function fetchDistricts() {
      try {
        const d = await api.getDistricts();
        setDistricts(d);
      } catch (err) {
        console.error('Failed to load districts', err);
      }
    }
    fetchDistricts();
  }, []);

  // Sync personal details from profile & user
  useEffect(() => {
    if (user || profile) {
      setUsername(user?.username || (profile as any)?.username || '');
      setFullName(profile?.name || user?.name || '');
      setEmail(profile?.email || user?.email || '');
      setPhone(profile?.mobile || user?.mobile || '');

      const dist = profile?.district || 'Belagavi';
      setSelectedDistrict(dist);
      setSelectedTaluk(profile?.taluk || 'Belagavi');

      // Sync agricultural details
      setVillage(profile?.village || '');
      setLandAcres(profile?.land_acres !== undefined && profile?.land_acres !== null ? String(profile.land_acres) : '');
      setLandOwnership(profile?.land_ownership || 'Own');
      
      let pCrop = (profile as any)?.primary_crop;
      if (!pCrop && profile?.crops_grown) {
        try {
          const arr = typeof profile.crops_grown === 'string' ? JSON.parse(profile.crops_grown) : profile.crops_grown;
          if (Array.isArray(arr) && arr.length > 0) pCrop = arr[0];
        } catch (e) {}
      }
      setPrimaryCrop(pCrop || 'Paddy');
      setFarmerCategory(profile?.farmer_category || 'Small & Marginal');
      setIrrigationType(profile?.irrigation_type || 'Rainfed');
      setSoilType((profile as any)?.soil_type || 'Red Soil');
      setSeason((profile as any)?.agricultural_season || 'Kharif');
      setCropStage((profile as any)?.crop_stage || 'Tillering / Flowering');

      // Account creation date
      const createdDate = (profile as any)?.account_created_at || user?.created_at || profile?.created_at;
      if (createdDate) {
        try {
          const d = new Date(createdDate);
          setAccountCreatedAt(
            d.toLocaleDateString(language === 'kn' ? 'kn-IN' : 'en-IN', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })
          );
        } catch {
          setAccountCreatedAt(createdDate);
        }
      }
    }
  }, [user, profile]);

  // Update taluks when district changes
  useEffect(() => {
    const matched = districts.find((d) => d.name === selectedDistrict);
    if (matched && matched.taluks && matched.taluks.length > 0) {
      setAvailableTaluks(matched.taluks);
      if (!matched.taluks.includes(selectedTaluk)) {
        setSelectedTaluk(matched.taluks[0]);
      }
    } else {
      setAvailableTaluks([selectedDistrict]);
    }
  }, [selectedDistrict, districts]);

  // Clean up audio preview on unmount
  useEffect(() => {
    return () => {
      if (audioPreviewRef.current) {
        audioPreviewRef.current.pause();
        audioPreviewRef.current = null;
      }
    };
  }, []);

  // Validate personal details
  const validatePersonalDetails = (): string | null => {
    if (!fullName.trim()) {
      return language === 'kn' ? 'ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.' : 'Please enter your full name.';
    }
    if (username.trim()) {
      const uRegex = /^[a-zA-Z0-9_.]{3,30}$/;
      if (!uRegex.test(username.trim())) {
        return language === 'kn'
          ? 'ಬಳಕೆದಾರ ಹೆಸರು 3 ರಿಂದ 30 ಅಕ್ಷರಗಳನ್ನು ಹೊಂದಿರಬೇಕು (ಕೇವಲ ಅಕ್ಷರಗಳು, ಸಂಖ್ಯೆಗಳು, _ ಅಥವಾ .).'
          : 'Username must be 3-30 characters (alphanumeric, underscore, or dot).';
      }
    }
    if (email.trim()) {
      const eRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
      if (!eRegex.test(email.trim())) {
        return language === 'kn' ? 'ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಇಮೇಲ್ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿ.' : 'Please enter a valid email address.';
      }
    }
    return null;
  };

  // Save Personal Details
  const handleSavePersonal = async (e: React.FormEvent) => {
    e.preventDefault();
    setPersonalError(null);
    setPersonalSuccess(null);

    const validationError = validatePersonalDetails();
    if (validationError) {
      setPersonalError(validationError);
      return;
    }

    setPersonalSaving(true);
    try {
      const parsedAcres = landAcres.trim() ? parseFloat(landAcres) : undefined;
      await api.updateFarmerProfile({
        name: fullName.trim(),
        username: username.trim() || undefined,
        email: email.trim() || undefined,
        district: selectedDistrict,
        taluk: selectedTaluk,
        village: village.trim() || undefined,
        land_acres: parsedAcres,
        land_ownership: landOwnership,
        primary_crop: primaryCrop,
        crops_grown: primaryCrop ? [primaryCrop] : [],
        farmer_category: farmerCategory,
        irrigation_type: irrigationType,
        soil_type: soilType,
        agricultural_season: season,
        crop_stage: cropStage,
        confirmed_fields: "district, taluk, land_acres, crop, irrigation, ownership"
      });

      await refreshProfile();
      setPersonalSuccess(
        language === 'kn'
          ? 'ವೈಯಕ್ತಿಕ ವಿವರಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ!'
          : 'Personal details updated successfully!'
      );
      setTimeout(() => setPersonalSuccess(null), 4000);
    } catch (err: any) {
      setPersonalError(err.message || 'Failed to update personal details.');
    } finally {
      setPersonalSaving(false);
    }
  };

  // Preview Voice Action
  const handlePreviewVoice = async () => {
    if (isPlayingPreview && audioPreviewRef.current) {
      audioPreviewRef.current.pause();
      setIsPlayingPreview(false);
      return;
    }

    setPreviewLoading(true);
    try {
      const voiceId =
        regionalDialect === 'English'
          ? voiceGender === 'male'
            ? 'en_male'
            : 'en_female'
          : voiceGender === 'male'
          ? 'kn_male'
          : 'kn_female';

      const res = await api.previewVoice(voiceId);
      if (res && res.audio_url) {
        if (audioPreviewRef.current) {
          audioPreviewRef.current.pause();
        }
        const audio = new Audio(res.audio_url);
        audio.playbackRate = speechSpeed;
        audioPreviewRef.current = audio;
        audio.onended = () => setIsPlayingPreview(false);
        audio.onerror = () => setIsPlayingPreview(false);
        await audio.play();
        setIsPlayingPreview(true);
      }
    } catch (err) {
      console.warn('Voice preview playback error:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  // Explicit Settings Confirmation Action
  const handleConfirmSaveSettings = () => {
    setSettingsSuccess(
      language === 'kn'
        ? 'ವೆಬ್‌ಸೈಟ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ ಮತ್ತು ಅನ್ವಯಿಸಲಾಗಿದೆ!'
        : 'Website settings saved and synchronized successfully!'
    );
    setTimeout(() => setSettingsSuccess(null), 3500);
  };

  // Logout Handler
  const handleConfirmLogout = () => {
    if (audioPreviewRef.current) {
      audioPreviewRef.current.pause();
      audioPreviewRef.current = null;
    }
    setShowLogoutModal(false);
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8 px-4 sm:px-6 lg:px-8 transition-colors duration-200">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Primary Interface Mode Switcher (Voice Assistant <-> Manual Mode) */}
        <div className="flex items-center justify-center gap-3 p-1.5 bg-slate-200 dark:bg-slate-800/80 rounded-2xl max-w-md mx-auto shadow-inner">
          <button
            type="button"
            onClick={() => navigate('/voice-assistant')}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 transition"
          >
            <Mic className="w-4 h-4 text-emerald-600" />
            <span>{language === 'kn' ? 'ಧ್ವನಿ ಸಹಾಯಕ' : 'Voice Assistant'}</span>
          </button>
          <button
            type="button"
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold bg-emerald-600 text-white shadow-md transition"
          >
            <Sliders className="w-4 h-4" />
            <span>{language === 'kn' ? 'ಹಸ್ತಚಾಲಿತ ನಮೂನೆ' : 'Manual Mode'}</span>
          </button>
        </div>

        {/* Header Banner */}
        <div className="bg-gradient-to-r from-emerald-700 via-green-700 to-teal-800 rounded-2xl p-6 sm:p-8 text-white shadow-lg relative overflow-hidden">
          <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-semibold mb-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-300" />
                {language === 'kn' ? 'ದೃಢೀಕೃತ ರೈತ ಖಾತೆ' : 'Verified Farmer Account'}
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold font-kannada">
                {language === 'kn' ? 'ನನ್ನ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಸೆಟ್ಟಿಂಗ್ಸ್' : 'My Profile & Settings'}
              </h1>
              <p className="text-emerald-100 text-sm mt-1 max-w-xl">
                {language === 'kn'
                  ? 'ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ವಿವರಗಳು ಮತ್ತು ವೆಬ್‌ಸೈಟ್ ಆದ್ಯತೆಗಳನ್ನು ಇಲ್ಲಿ ನಿರ್ವಹಿಸಿ.'
                  : 'Manage your personal details, AI voice assistant, and application preferences.'}
              </p>
            </div>
            <div className="flex items-center gap-3 bg-white/10 backdrop-blur-md px-4 py-2.5 rounded-xl border border-white/20">
              <div className="w-10 h-10 rounded-full bg-emerald-500/40 flex items-center justify-center font-bold text-lg text-white">
                {(fullName || username || 'KM').charAt(0).toUpperCase()}
              </div>
              <div className="text-left">
                <div className="text-xs text-emerald-200">{language === 'kn' ? 'ಲಾಗಿನ್ ಆದವರು' : 'Logged in as'}</div>
                <div className="font-semibold text-sm truncate max-w-[160px]">{username || fullName || 'Farmer'}</div>
              </div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION 1: PERSONAL DETAILS
        ========================================================================= */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 sm:p-8 transition-colors">
          <div className="flex items-center justify-between pb-5 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 rounded-xl">
                <UserIcon className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white font-kannada">
                  {language === 'kn' ? '೧. ವೈಯಕ್ತಿಕ ವಿವರಗಳು (Personal Details)' : '1. Personal Details'}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {language === 'kn'
                    ? 'ನಿಮ್ಮ ಹೆಸರು, ಸಂಪರ್ಕ ಹಾಗೂ ವಿಳಾಸದ ವಿವರಗಳನ್ನು ಇಲ್ಲಿ ನವೀಕರಿಸಿ.'
                    : 'View and update your personal information, location, and account details.'}
                </p>
              </div>
            </div>
          </div>

          {/* Feedback messages */}
          {personalSuccess && (
            <div className="mt-4 p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 rounded-xl flex items-center gap-2.5 text-sm animate-fade-in">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <span>{personalSuccess}</span>
            </div>
          )}

          {personalError && (
            <div className="mt-4 p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800 text-rose-800 dark:text-rose-200 rounded-xl flex items-center gap-2.5 text-sm animate-fade-in">
              <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
              <span>{personalError}</span>
            </div>
          )}

          <form onSubmit={handleSavePersonal} className="mt-6 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Username */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಬಳಕೆದಾರ ಹೆಸರು (Username)' : 'Username'}
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 text-sm font-medium">
                    @
                  </span>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g. basavaraj_patil"
                    className="w-full pl-8 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                  />
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  {language === 'kn'
                    ? 'AI ಸಹಾಯಕ ನಿಮ್ಮನ್ನು ಈ ಹೆಸರಿನಿಂದ ಸಂಬೋಧಿಸುತ್ತದೆ.'
                    : 'The AI assistant greets you personally by this username.'}
                </p>
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಪೂರ್ಣ ಹೆಸರು (Full Name)' : 'Full Name'} *
                </label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Basavaraj Patil"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                  />
                </div>
              </div>

              {/* Email Address */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಇಮೇಲ್ ವಿಳಾಸ (Email Address)' : 'Email Address'}
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="farmer@example.com"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                  />
                </div>
              </div>

              {/* Phone Number (Verified, protected) */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ದೂರವಾಣಿ ಸಂಖ್ಯೆ (Phone Number)' : 'Phone Number'}
                </label>
                <div className="relative">
                  <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
                  <input
                    type="text"
                    readOnly
                    value={phone}
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-100 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 rounded-xl text-sm cursor-not-allowed"
                  />
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  {language === 'kn' ? 'ದೃಢೀಕರಿಸಿದ ನೋಂದಾಯಿತ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ.' : 'Verified registered mobile number.'}
                </p>
              </div>

              {/* District */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಜಿಲ್ಲೆ (District)' : 'District'} *
                </label>
                <div className="relative">
                  <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
                  <select
                    value={selectedDistrict}
                    onChange={(e) => setSelectedDistrict(e.target.value)}
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                  >
                    {districts.map((d) => (
                      <option key={d.name} value={d.name}>
                        {d.name} ({d.name_kn})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Taluk */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ತಾಲೂಕು (Taluka)' : 'Taluka'} *
                </label>
                <select
                  value={selectedTaluk}
                  onChange={(e) => setSelectedTaluk(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                >
                  {availableTaluks.map((tName) => (
                    <option key={tName} value={tName}>
                      {tName}
                    </option>
                  ))}
                </select>
              </div>

              {/* Village */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಗ್ರಾಮ (Village)' : 'Village'}
                </label>
                <input
                  type="text"
                  value={village}
                  onChange={(e) => setVillage(e.target.value)}
                  placeholder="e.g. Belagundi"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                />
              </div>

              {/* Land Size (Acres) */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (Land Size in Acres)' : 'Land Size (Acres)'} *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  max="1000"
                  value={landAcres}
                  onChange={(e) => setLandAcres(e.target.value)}
                  placeholder="e.g. 3.5"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                />
              </div>

              {/* Land Ownership */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಭೂ ಮಾಲೀಕತ್ವ (Land Ownership)' : 'Land Ownership'}
                </label>
                <select
                  value={landOwnership}
                  onChange={(e) => setLandOwnership(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                >
                  <option value="Own">{language === 'kn' ? 'ಸ್ವಂತ ಜಮೀನು (Owned)' : 'Owned'}</option>
                  <option value="Leased">{language === 'kn' ? 'ಗುತ್ತಿಗೆ / ಗೇಣಿ (Leased / Tenant)' : 'Leased / Tenant'}</option>
                  <option value="Shared">{language === 'kn' ? 'ಪಾಲುದಾರಿಕೆ (Shared)' : 'Shared'}</option>
                </select>
              </div>

              {/* Primary Crop */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಮುಖ್ಯ ಬೆಳೆ (Primary Crop)' : 'Primary Crop'} *
                </label>
                <select
                  value={primaryCrop}
                  onChange={(e) => setPrimaryCrop(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                >
                  <option value="Paddy">ಭತ್ತ (Paddy)</option>
                  <option value="Sugarcane">ಕಬ್ಬು (Sugarcane)</option>
                  <option value="Groundnut">ಶೇಂಗಾ (Groundnut)</option>
                  <option value="Maize">ಮೆಕ್ಕೆಜೋಳ (Maize)</option>
                  <option value="Cotton">ಹತ್ತಿ (Cotton)</option>
                  <option value="Tur">ತೊಗರಿ (Tur / Red Gram)</option>
                  <option value="Jowar">ಜೋಳ (Jowar / Sorghum)</option>
                  <option value="Ragi">ರಾಗಿ (Ragi / Finger Millet)</option>
                  <option value="Bengal Gram">ಕಡಲೆ (Bengal Gram / Chickpea)</option>
                  <option value="Sunflower">ಸೂರ್ಯಕಾಂತಿ (Sunflower)</option>
                  <option value="Wheat">ಗೋಧಿ (Wheat)</option>
                  <option value="Onion">ಈರುಳ್ಳಿ (Onion)</option>
                  <option value="Tomato">ಟೊಮೆಟೊ (Tomato)</option>
                </select>
              </div>

              {/* Farmer Category */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ರೈತ ವರ್ಗ (Farmer Category)' : 'Farmer Category'}
                </label>
                <select
                  value={farmerCategory}
                  onChange={(e) => setFarmerCategory(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                >
                  <option value="Small & Marginal">ಸಣ್ಣ ಮತ್ತು ಅತಿ ಸಣ್ಣ (Small & Marginal: &lt; 5 acres)</option>
                  <option value="Marginal farmer">ಅತಿ ಸಣ್ಣ ರೈತರು (Marginal: &lt; 2.5 acres)</option>
                  <option value="Small farmer">ಸಣ್ಣ ರೈತರು (Small: 2.5 - 5 acres)</option>
                  <option value="General">ಸಾಮಾನ್ಯ ವರ್ಗ (General Farmer)</option>
                  <option value="SC/ST">SC / ST ರೈತರು (SC / ST Category)</option>
                </select>
              </div>

              {/* Irrigation Type */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ನೀರಾವರಿ ಸೌಲಭ್ಯ (Irrigation Facility)' : 'Irrigation Facility'}
                </label>
                <select
                  value={irrigationType}
                  onChange={(e) => setIrrigationType(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                >
                  <option value="Rainfed">ಮಳೆಯಾಶ್ರಿತ / ಖುಷ್ಕಿ (Rainfed)</option>
                  <option value="Borewell">ಕೊಳವೆಬಾವಿ (Borewell)</option>
                  <option value="Canal">ಕಾಲುವೆ ನೀರಾವರಿ (Canal)</option>
                  <option value="Drip">ಹನಿ ನೀರಾವರಿ (Drip)</option>
                  <option value="Sprinkler">ತುಂತುರು ನೀರಾವರಿ (Sprinkler)</option>
                </select>
              </div>

              {/* Soil Type */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಮಣ್ಣಿನ ವಿಧ (Soil Type)' : 'Soil Type'}
                </label>
                <select
                  value={soilType}
                  onChange={(e) => setSoilType(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                >
                  <option value="Black Soil">ಕಪ್ಪು ಮಣ್ಣು / ಎರೆ ಮಣ್ಣು (Black Soil)</option>
                  <option value="Red Soil">ಕೆಂಪು ಮಣ್ಣು / ಮಸಾರಿ (Red Soil)</option>
                  <option value="Loamy Soil">ಗೋಡು ಮಣ್ಣು (Loamy Soil)</option>
                  <option value="Sandy Soil">ಮರಳು ಮಿಶ್ರಿತ ಮಣ್ಣು (Sandy Soil)</option>
                </select>
              </div>

              {/* Agricultural Season */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಕೃಷಿ ಹಂಗಾಮು (Crop Season)' : 'Crop Season'}
                </label>
                <select
                  value={season}
                  onChange={(e) => setSeason(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm transition"
                >
                  <option value="Kharif">ಮುಂಗಾರು ಹಂಗಾಮು (Kharif)</option>
                  <option value="Rabi">ಹಿಂಗಾರು ಹಂಗಾಮು (Rabi)</option>
                  <option value="Summer">ಬೇಸಿಗೆ ಹಂಗಾಮು (Summer)</option>
                </select>
              </div>

              {/* Account Creation Date */}
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  {language === 'kn' ? 'ಖಾತೆ ರಚನೆ ದಿನಾಂಕ (Account Created Date)' : 'Account Created Date'}
                </label>
                <div className="flex items-center gap-2.5 text-sm text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/50 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700">
                  <Calendar className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  <span>{accountCreatedAt || 'October 2026'}</span>
                </div>
              </div>
            </div>

            {/* Save Personal Details Button */}
            <div className="flex justify-end pt-3">
              <button
                type="submit"
                disabled={personalSaving}
                className="inline-flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-semibold shadow-sm hover:shadow transition disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                {personalSaving
                  ? language === 'kn'
                    ? 'ಉಳಿಸಲಾಗುತ್ತಿದೆ...'
                    : 'Saving...'
                  : language === 'kn'
                  ? 'ವೈಯಕ್ತಿಕ ವಿವರಗಳನ್ನು ಉಳಿಸಿ'
                  : 'Save Personal Details'}
              </button>
            </div>
          </form>
        </div>

        {/* =========================================================================
            SECTION 2: WEBSITE SETTINGS (Synchronized with Centralized SettingsContext)
        ========================================================================= */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 sm:p-8 transition-colors">
          <div className="flex items-center justify-between pb-5 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 rounded-xl">
                <Sliders className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white font-kannada">
                  {language === 'kn' ? '೨. ವೆಬ್‌ಸೈಟ್ ಸೆಟ್ಟಿಂಗ್ಸ್ (Website Settings)' : '2. Website Settings'}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {language === 'kn'
                    ? 'ಥೀಮ್, ಭಾಷೆ, ಧ್ವನಿ ಶೈಲಿ ಮತ್ತು AI ಸಹಾಯಕ ಸಂವಾದದ ಆದ್ಯತೆಗಳು (ಟೂಲ್‌ಬಾರ್‌ನೊಂದಿಗೆ ಸಿಂಕ್ರೊನೈಸ್ ಆಗಿದೆ).'
                    : 'Configure theme, regional dialect, neural voice, and AI voice assistant behavior (synchronized with toolbar).'}
                </p>
              </div>
            </div>
          </div>

          {/* Settings Feedback */}
          {settingsSuccess && (
            <div className="mt-4 p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 rounded-xl flex items-center gap-2.5 text-sm animate-fade-in">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <span>{settingsSuccess}</span>
            </div>
          )}

          <div className="mt-6 space-y-8">
            {/* SUB-SECTION 1: APPEARANCE (THEME) */}
            <div>
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-3">
                {language === 'kn' ? 'ಗೋಚರತೆ / ಥೀಮ್ (Appearance)' : 'Appearance & Theme'}
              </h3>
              <div className="grid grid-cols-2 gap-4 max-w-md">
                <button
                  type="button"
                  onClick={() => setTheme('light')}
                  className={`flex items-center justify-center gap-3 p-3.5 rounded-xl border text-sm font-medium transition ${
                    theme === 'light'
                      ? 'border-emerald-600 bg-emerald-50/80 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200 font-semibold ring-2 ring-emerald-500/20'
                      : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                  }`}
                >
                  <Sun className="w-5 h-5 text-amber-500" />
                  <span>{language === 'kn' ? 'ಲೈಟ್ ಮೋಡ್ (Light)' : 'Light Mode'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setTheme('dark')}
                  className={`flex items-center justify-center gap-3 p-3.5 rounded-xl border text-sm font-medium transition ${
                    theme === 'dark'
                      ? 'border-emerald-600 bg-emerald-50/80 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200 font-semibold ring-2 ring-emerald-500/20'
                      : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                  }`}
                >
                  <Moon className="w-5 h-5 text-indigo-400" />
                  <span>{language === 'kn' ? 'ಡಾರ್ಕ್ ಮೋಡ್ (Dark)' : 'Dark Mode'}</span>
                </button>
              </div>
            </div>

            {/* SUB-SECTION 2: LANGUAGE & REGIONAL DIALECT */}
            <div>
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-3">
                {language === 'kn' ? 'ಭಾಷೆ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಶೈಲಿ (Language & Dialect)' : 'Language & Dialect'}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  {
                    id: 'North Karnataka',
                    title: 'North Karnataka Kannada',
                    title_kn: 'ಉತ್ತರ ಕರ್ನಾಟಕ ಕನ್ನಡ',
                    desc: 'ಬೆಳಗಾವಿ, ಧಾರವಾಡ, ವಿಜಯಪುರ, ಬಾಗಲಕೋಟೆ ಶೈಲಿ ("ನೋಡ್ರೀ", "ಮಾಡ್ರೀ", "ಐತಿ")'
                  },
                  {
                    id: 'South Karnataka',
                    title: 'South Karnataka Kannada',
                    title_kn: 'ದಕ್ಷಿಣ ಕರ್ನಾಟಕ ಕನ್ನಡ',
                    desc: 'ಮೈಸೂರು, ಮಂಡ್ಯ, ಹಾಸನ, ಬೆಂಗಳೂರು ಶೈಲಿ'
                  },
                  {
                    id: 'Standard Kannada',
                    title: 'Standard Kannada',
                    title_kn: 'ಶಿಷ್ಟ ಕನ್ನಡ (ಪುಸ್ತಕ ಭಾಷೆ)',
                    desc: 'ಔಪಚಾರಿಕ ಶಿಷ್ಟ ಕನ್ನಡ ಭಾಷಾ ಶೈಲಿ'
                  },
                  {
                    id: 'English',
                    title: 'Indian English',
                    title_kn: 'ಇಂಡಿಯನ್ ಇಂಗ್ಲಿಷ್',
                    desc: 'Standard agricultural terminology in Indian English'
                  }
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setRegionalDialect(item.id as RegionalDialect)}
                    className={`flex flex-col text-left p-3.5 rounded-xl border transition ${
                      regionalDialect === item.id
                        ? 'border-emerald-600 bg-emerald-50/80 dark:bg-emerald-950/50 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20'
                        : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="font-semibold text-sm font-kannada">
                        {language === 'kn' ? item.title_kn : item.title}
                      </span>
                      {regionalDialect === item.id && <Check className="w-4 h-4 text-emerald-600" />}
                    </div>
                    <span className="text-xs text-slate-500 dark:text-slate-400 mt-1">{item.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* SUB-SECTION 3: VOICE PREFERENCE (MALE / FEMALE) + PREVIEW */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
                  {language === 'kn' ? 'ಧ್ವನಿ ಆಯ್ಕೆ (Neural Voice Preference)' : 'Voice Preference'}
                </h3>

                <button
                  type="button"
                  onClick={handlePreviewVoice}
                  disabled={previewLoading}
                  className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 rounded-lg text-xs font-semibold hover:bg-emerald-200 transition"
                >
                  {previewLoading ? (
                    <span>{language === 'kn' ? 'ಸಿದ್ಧಪಡಿಸಲಾಗುತ್ತಿದೆ...' : 'Loading voice...'}</span>
                  ) : isPlayingPreview ? (
                    <>
                      <Square className="w-3.5 h-3.5 fill-current" />
                      <span>{language === 'kn' ? 'ನಿಲ್ಲಿಸಿ' : 'Stop Preview'}</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-3.5 h-3.5" />
                      <span>{language === 'kn' ? 'ಧ್ವನಿ ಕೇಳಿ (Preview)' : 'Preview Voice'}</span>
                    </>
                  )}
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setVoiceGender('female')}
                  className={`flex items-center justify-between p-4 rounded-xl border text-left transition ${
                    voiceGender === 'female'
                      ? 'border-emerald-600 bg-emerald-50/80 dark:bg-emerald-950/50 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20'
                      : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                  }`}
                >
                  <div>
                    <div className="font-semibold text-sm">
                      {language === 'kn' ? 'ಮಹಿಳಾ ಧ್ವನಿ (ಸಪ್ನಾ - Sapna)' : 'Female Voice (Sapna / Neerja)'}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {language === 'kn'
                        ? 'ಸ್ವಾಭಾವಿಕ, ಮೃದುವಾದ ಗ್ರಾಮೀಣ ಶೈಲಿಯ ಧ್ವನಿ'
                        : 'Warm, natural female neural voice'}
                    </div>
                  </div>
                  {voiceGender === 'female' && <Check className="w-5 h-5 text-emerald-600" />}
                </button>

                <button
                  type="button"
                  onClick={() => setVoiceGender('male')}
                  className={`flex items-center justify-between p-4 rounded-xl border text-left transition ${
                    voiceGender === 'male'
                      ? 'border-emerald-600 bg-emerald-50/80 dark:bg-emerald-950/50 text-emerald-900 dark:text-emerald-200 ring-2 ring-emerald-500/20'
                      : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                  }`}
                >
                  <div>
                    <div className="font-semibold text-sm">
                      {language === 'kn' ? 'ಪುರುಷ ಧ್ವನಿ (ಗಗನ್ - Gagan)' : 'Male Voice (Gagan / Prabhat)'}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {language === 'kn'
                        ? 'ಗಂಭೀರ, ವಿಶ್ವಾಸಾರ್ಹ ಕೃಷಿ ಸಲಹಾ ಧ್ವನಿ'
                        : 'Deep, clear male neural voice'}
                    </div>
                  </div>
                  {voiceGender === 'male' && <Check className="w-5 h-5 text-emerald-600" />}
                </button>
              </div>
            </div>

            {/* SUB-SECTION 4: VOICE ASSISTANT CONTROLS */}
            <div className="pt-2 border-t border-slate-200 dark:border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-2">
                {language === 'kn' ? 'AI ಧ್ವನಿ ಸಹಾಯಕ ನಿಯಂತ್ರಣಗಳು (Voice Assistant Controls)' : 'Voice Assistant Controls'}
              </h3>

              {/* Master Voice Assistant Enabled Toggle */}
              <div className="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="pr-4">
                  <div className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                    <Bot className="w-4 h-4 text-emerald-600" />
                    <span>{language === 'kn' ? 'ಧ್ವನಿ ಸಹಾಯಕ ಸಕ್ರಿಯಗೊಳಿಸಿ (Voice Assistant)' : 'Enable Voice Assistant System'}</span>
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    {language === 'kn'
                      ? 'ವೆಬ್‌ಸೈಟ್‌ನಾದ್ಯಂತ AI ಧ್ವನಿ ಸಹಾಯಕವನ್ನು ಆನ್ ಅಥವಾ ಆಫ್ ಮಾಡಿ.'
                      : 'Master switch to enable or disable the AI voice assistant across the platform.'}
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
                  <input
                    type="checkbox"
                    checked={voiceAssistantEnabled}
                    onChange={(e) => setVoiceAssistantEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                </label>
              </div>

              {/* Automatic Voice Response Toggle */}
              <div className="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="pr-4">
                  <div className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    {language === 'kn' ? 'ಸ್ವಯಂಚಾಲಿತ ಧ್ವನಿ ಉತ್ತರಗಳು (Auto Voice Responses)' : 'Automatic Voice Responses'}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    {language === 'kn'
                      ? 'AI ಸಹಾಯಕ ಪ್ರತಿಯೊಂದು ಪ್ರಶ್ನೆ ಮತ್ತು ಉತ್ತರವನ್ನು ಧ್ವನಿಯ ಮೂಲಕ ಓದಿ ಹೇಳಬೇಕೆ?'
                      : 'Automatically speak greetings, follow-up questions, and results aloud.'}
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
                  <input
                    type="checkbox"
                    checked={autoVoiceResponse}
                    onChange={(e) => setAutoVoiceResponse(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                </label>
              </div>

              {/* Voice Input Toggle */}
              <div className="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="pr-4">
                  <div className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    {language === 'kn' ? 'ಧ್ವನಿ ಇನ್‌ಪುಟ್ (Voice Input / Mic)' : 'Enable Voice Input (Microphone)'}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    {language === 'kn'
                      ? 'ಕನ್ನಡ ಧ್ವನಿ ಸಂಭಾಷಣೆಯ ಮೈಕ್ರೋಫೋನ್ ಇನ್‌ಪುಟ್ ಸಕ್ರಿಯಗೊಳಿಸಿ.'
                      : 'Allow speaking questions using speech-to-text recognition.'}
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
                  <input
                    type="checkbox"
                    checked={voiceInputEnabled}
                    onChange={(e) => setVoiceInputEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                </label>
              </div>

              {/* Speech Speed Adjustment */}
              <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                      {language === 'kn' ? 'ಧ್ವನಿ ವೇಗ (Speech Playback Speed)' : 'Speech Playback Speed'}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      {language === 'kn'
                        ? 'ಸಹಾಯಕರ ಮಾತು ನಿಧಾನ ಅಥವಾ ವೇಗವಾಗಿರಬೇಕೆ ಎಂದು ಹೊಂದಿಸಿ.'
                        : 'Adjust audio playback rate (0.75x to 1.5x).'}
                    </div>
                  </div>
                  <span className="px-2.5 py-1 bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 font-bold text-xs rounded-lg">
                    {speechSpeed.toFixed(2)}x
                  </span>
                </div>

                <div className="flex items-center gap-2 pt-1">
                  {[0.75, 1.0, 1.25, 1.5].map((spd) => (
                    <button
                      key={spd}
                      type="button"
                      onClick={() => setSpeechSpeed(spd)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-semibold border transition ${
                        Math.abs(speechSpeed - spd) < 0.05
                          ? 'border-emerald-600 bg-emerald-600 text-white'
                          : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                      }`}
                    >
                      {spd === 1.0 ? '1.0x (Normal)' : `${spd}x`}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Save Website Settings Confirmation Button */}
            <div className="flex justify-end pt-3">
              <button
                type="button"
                onClick={handleConfirmSaveSettings}
                className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm hover:shadow transition"
              >
                <Save className="w-4 h-4" />
                <span>
                  {language === 'kn' ? 'ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ಖಚಿತಪಡಿಸಿ (Confirm Settings)' : 'Save Settings'}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION 3: LOGOUT
        ========================================================================= */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 sm:p-8 transition-colors">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 rounded-xl">
                <LogOut className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white font-kannada">
                  {language === 'kn' ? '೩. ಖಾತೆಯಿಂದ ನಿರ್ಗಮಿಸಿ (Logout)' : '3. Logout'}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {language === 'kn'
                    ? 'ನಿಮ್ಮ ಖಾತೆಯ ಪ್ರಸ್ತುತ ಸಕ್ರಿಯ ಅಧಿವೇಶನವನ್ನು ಕೊನೆಗೊಳಿಸಿ. ನಿಮ್ಮ ಉಳಿಸಿದ ಪ್ರೊಫೈಲ್ ಡೇಟಾ ಅಳಿಸಿಹೋಗುವುದಿಲ್ಲ.'
                    : 'Safely end your current authenticated session. Your saved farmer profile and history are preserved.'}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowLogoutModal(true)}
              className="inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-sm font-semibold shadow-sm hover:shadow transition"
            >
              <LogOut className="w-4 h-4" />
              <span>{language === 'kn' ? 'ಖಾತೆಯಿಂದ ನಿರ್ಗಮಿಸಿ' : 'Logout'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* =========================================================================
          LOGOUT CONFIRMATION MODAL
      ========================================================================= */}
      {showLogoutModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-950/80 text-rose-600 mx-auto flex items-center justify-center">
              <LogOut className="w-6 h-6" />
            </div>

            <h3 className="text-lg font-bold text-slate-900 dark:text-white font-kannada">
              {language === 'kn' ? 'ನಿರ್ಗಮಿಸಲು ನೀವು ಖಚಿತವೇ?' : 'Confirm Logout'}
            </h3>

            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              {language === 'kn'
                ? 'ಖಾತೆಯಿಂದ ನಿರ್ಗಮಿಸಿದ ನಂತರ ರಕ್ಷಿತ ಪುಟಗಳನ್ನು ವೀಕ್ಷಿಸಲು ಪುನಃ ಲಾಗಿನ್ ಆಗಬೇಕು. ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಸಂವಾದ ಇತಿಹಾಸ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಸುರಕ್ಷಿತವಾಗಿ ಉಳಿಯುತ್ತದೆ.'
                : 'Are you sure you want to log out? Your saved farmer profile and agricultural conversation history will remain securely stored in the database.'}
            </p>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowLogoutModal(false)}
                className="px-4 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold text-sm rounded-xl transition"
              >
                {language === 'kn' ? 'ರದ್ದುಮಾಡಿ (Cancel)' : 'Cancel'}
              </button>

              <button
                type="button"
                onClick={handleConfirmLogout}
                className="px-4 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-semibold text-sm rounded-xl transition shadow-sm"
              >
                {language === 'kn' ? 'ಹೌದು, ನಿರ್ಗಮಿಸಿ' : 'Yes, Logout'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
