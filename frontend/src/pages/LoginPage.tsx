import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sprout, Phone, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();

  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mobile.trim() || !password.trim()) {
      setError('ದಯವಿಟ್ಟು ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಮತ್ತು ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await login(mobile.trim(), password);
      navigate('/voice-assistant');
    } catch (err: any) {
      setError(err.message || 'ಲಾಗಿನ್ ವಿಫಲವಾಗಿದೆ. ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-xl p-8 sm:p-10">
        
        {/* Brand Header */}
        <div className="text-center space-y-2 mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#174C36] to-[#2F7650] flex items-center justify-center text-white mx-auto shadow-md">
            <Sprout className="w-8 h-8 text-[#D8AA48]" />
          </div>
          <h2 className="text-2xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] tracking-tight">
            ಕೃಷಿ ಮಿತ್ರ ಲಾಗಿನ್
          </h2>
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
            Welcome to Krishi Mitra Agriculture Portal
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
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Mobile Number */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1.5 font-kannada">
              ಮೊಬೈಲ್ ಸಂಖ್ಯೆ (Mobile Number)
            </label>
            <div className="relative">
              <input
                type="tel"
                placeholder="10-digit Mobile Number"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                maxLength={10}
                required
                className="w-full pl-10 pr-4 py-3 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
              />
              <Phone className="w-4 h-4 absolute left-3.5 top-3.5 text-[#69766D]" />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-bold text-[#19251E] dark:text-[#EDF3EF] mb-1.5 font-kannada">
              ಪಾಸ್‌ವರ್ಡ್ (Password)
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-10 py-3 text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650]"
              />
              <Lock className="w-4 h-4 absolute left-3.5 top-3.5 text-[#69766D]" />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3.5 text-[#69766D] hover:text-[#19251E]"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Remember me & Forgot Password */}
          <div className="flex items-center justify-between text-xs">
            <label className="flex items-center gap-2 cursor-pointer text-[#69766D] dark:text-[#9BB0A4]">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="rounded border-[#E2E8DF] text-[#174C36] focus:ring-0"
              />
              <span>Remember me</span>
            </label>

            <button
              type="button"
              onClick={() => alert('ದಯವಿಟ್ಟು ನಿಮ್ಮ ನೋಂದಾಯಿತ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ OTP ಮೂಲಕ ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ.')}
              className="text-[#174C36] dark:text-[#75A96A] font-semibold hover:underline"
            >
              Forgot Password?
            </button>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white font-bold text-sm shadow-md transition-colors disabled:opacity-50"
          >
            {loading ? 'ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...' : 'ಲಾಗಿನ್ ಆಗಿ (Login)'}
          </button>
        </form>

        {/* Demo farmer quick login hint */}
        <div className="mt-6 p-3 rounded-xl bg-[#EAF3E9]/60 dark:bg-[#152E22]/40 text-center text-[11px] text-[#69766D] dark:text-[#9BB0A4]">
          <span className="font-semibold text-[#174C36] dark:text-[#75A96A]">ಹ್ಯಾಕಥಾನ್ ಪರೀಕ್ಷಾರ್ಥ ಲಾಗಿನ್: </span>
          <span>ಯಾವುದೇ 10-ಅಂಕಿಯ ಮೊಬೈಲ್ ಮತ್ತು ಪಾಸ್‌ವರ್ಡ್ ಬಳಸಿ ಅಥವಾ ನೋಂದಾಯಿಸಿ.</span>
        </div>

        {/* Register Link */}
        <div className="mt-8 text-center text-xs text-[#69766D] dark:text-[#9BB0A4]">
          <span>ಖಾತೆ ಇಲ್ಲವೇ? </span>
          <Link
            to="/register"
            className="font-bold text-[#174C36] dark:text-[#75A96A] hover:underline"
          >
            ಹೊಸ ರೈತರ ನೋಂದಣಿ (Register here)
          </Link>
        </div>
      </div>
    </div>
  );
};
