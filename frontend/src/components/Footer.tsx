import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout, Phone, ExternalLink, ShieldCheck, Heart } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const Footer: React.FC = () => {
  const { language } = useLanguage();

  return (
    <footer className="bg-[#123B2B] text-white border-t border-[#174C36] mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          
          {/* Column 1: Brand Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#2F7650] flex items-center justify-center text-white shadow-inner">
                <Sprout className="w-6 h-6 text-[#D8AA48]" />
              </div>
              <div>
                <span className="font-extrabold text-xl tracking-tight text-white">KRISHI MITRA</span>
                <p className="text-xs text-[#75A96A] font-kannada">ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ</p>
              </div>
            </div>
            <p className="text-sm text-[#9BB0A4] leading-relaxed">
              {language === 'kn'
                ? 'ಕರ್ನಾಟಕದ ಪ್ರತಿಯೊಬ್ಬ ರೈತರಿಗಾಗಿ ರೂಪಿಸಲಾದ ಧ್ವನಿ-ಮೊದಲ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಕೃಷಿ ಸಹಾಯಕ. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಸಾಲಗಳು ಮತ್ತು ನಿಖರ ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ.'
                : 'A voice-first AI agricultural assistant specifically designed for Karnataka farmers to discover government schemes, credit, and crop guidance.'}
            </p>
            <div className="flex items-center gap-2 text-xs text-[#D8AA48] bg-[#174C36]/60 p-2.5 rounded-lg border border-[#2F7650]/40">
              <ShieldCheck className="w-4 h-4 shrink-0" />
              <span>HackFusion 2.0 National Hackathon Innovation</span>
            </div>
          </div>

          {/* Column 2: Agriculture Services */}
          <div>
            <h3 className="font-bold text-sm uppercase tracking-wider text-[#D8AA48] mb-4">
              {language === 'kn' ? 'ಕೃಷಿ ಸೇವೆಗಳು' : 'Services'}
            </h3>
            <ul className="space-y-2.5 text-sm text-[#EAF3E9]/80">
              <li>
                <Link to="/schemes" className="hover:text-white hover:underline transition-colors">
                  {language === 'kn' ? 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಡೇಟಾಬೇಸ್' : 'Government Schemes Database'}
                </Link>
              </li>
              <li>
                <Link to="/eligibility-checker" className="hover:text-white hover:underline transition-colors">
                  {language === 'kn' ? 'ಬುದ್ಧಿವಂತ ಅರ್ಹತೆ ಪರಿಶೀಲನೆ' : 'Intelligent Eligibility Checker'}
                </Link>
              </li>
              <li>
                <Link to="/loans" className="hover:text-white hover:underline transition-colors">
                  {language === 'kn' ? 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ & ಇಎಂಐ ಕ್ಯಾಲ್ಕುಲೇಟರ್' : 'Kisan Credit & EMI Calculator'}
                </Link>
              </li>
              <li>
                <Link to="/crops" className="hover:text-white hover:underline transition-colors">
                  {language === 'kn' ? 'ಕರ್ನಾಟಕ ಬೆಳೆ ಮಾರ್ಗದರ್ಶಿ' : 'Karnataka Crop Guide'}
                </Link>
              </li>
              <li>
                <Link to="/fertilizer" className="hover:text-white hover:underline transition-colors">
                  {language === 'kn' ? 'ರಸಗೊಬ್ಬರ & ಮಣ್ಣು ಆರೋಗ್ಯ' : 'Fertilizer & Soil Health'}
                </Link>
              </li>
              <li>
                <Link to="/weather-market" className="hover:text-white hover:underline transition-colors">
                  {language === 'kn' ? 'ಹವಾಮಾನ & ಮಂಡಿ ಧಾರಣೆ' : 'Live Weather & Mandi Prices'}
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 3: Verified Government Links */}
          <div>
            <h3 className="font-bold text-sm uppercase tracking-wider text-[#D8AA48] mb-4">
              {language === 'kn' ? 'ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಪೋರ್ಟಲ್‌ಗಳು' : 'Official Government Portals'}
            </h3>
            <ul className="space-y-2.5 text-sm text-[#EAF3E9]/80">
              <li>
                <a
                  href="https://sevasindhu.karnataka.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  <span>Seva Sindhu Karnataka</span>
                  <ExternalLink className="w-3.5 h-3.5 text-[#75A96A]" />
                </a>
              </li>
              <li>
                <a
                  href="https://pmkisan.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  <span>PM-KISAN Portal</span>
                  <ExternalLink className="w-3.5 h-3.5 text-[#75A96A]" />
                </a>
              </li>
              <li>
                <a
                  href="https://samrakshane.karnataka.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  <span>Samrakshane (Crop Insurance)</span>
                  <ExternalLink className="w-3.5 h-3.5 text-[#75A96A]" />
                </a>
              </li>
              <li>
                <a
                  href="https://raitamitra.karnataka.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  <span>Raitha Mitra (Dept of Agri)</span>
                  <ExternalLink className="w-3.5 h-3.5 text-[#75A96A]" />
                </a>
              </li>
              <li>
                <a
                  href="https://landrecords.karnataka.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                >
                  <span>Bhoomi RTC Pahani Portal</span>
                  <ExternalLink className="w-3.5 h-3.5 text-[#75A96A]" />
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Farmer Helplines & Support */}
          <div>
            <h3 className="font-bold text-sm uppercase tracking-wider text-[#D8AA48] mb-4">
              {language === 'kn' ? 'ರೈತ ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳು' : 'Farmer Helplines'}
            </h3>
            <div className="space-y-3 text-sm text-[#EAF3E9]/80">
              <div className="bg-[#174C36] p-3 rounded-xl border border-[#2F7650]/50">
                <div className="flex items-center gap-2 text-white font-semibold">
                  <Phone className="w-4 h-4 text-[#D8AA48]" />
                  <span>Kisan Call Center (Toll Free)</span>
                </div>
                <p className="text-lg font-bold text-[#D8AA48] mt-1">1800-180-1551</p>
                <p className="text-xs text-[#9BB0A4]">24x7 Agricultural Guidance in Kannada</p>
              </div>

              <div className="p-2">
                <p className="text-xs text-[#9BB0A4]">
                  {language === 'kn'
                    ? 'ಕರ್ನಾಟಕ ಕೃಷಿ ಇಲಾಖೆ ಸಹಾಯವಾಣಿ:'
                    : 'Karnataka Agriculture Dept:'}
                </p>
                <p className="text-sm font-semibold text-white">080-22212849 / 080-22212818</p>
              </div>

              <div className="pt-2">
                <Link
                  to="/admin"
                  className="inline-flex items-center gap-1 text-xs text-[#75A96A] hover:text-[#D8AA48] transition-colors"
                >
                  <span>{language === 'kn' ? 'ಅಧಿಕೃತ ಅಡ್ಮಿನ್ ಲಾಗಿನ್' : 'Official Admin Access'}</span>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-[#174C36] mt-12 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-[#9BB0A4] gap-4">
          <p>
            © {new Date().getFullYear()} Krishi Mitra. Designed & Developed for Karnataka Farmers. All rights reserved.
          </p>
          <p className="flex items-center gap-1">
            <span>Built with Kannada Voice Intelligence for HackFusion 2.0</span>
          </p>
        </div>
      </div>
    </footer>
  );
};
