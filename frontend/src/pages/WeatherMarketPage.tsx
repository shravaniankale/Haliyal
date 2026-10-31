import React, { useState, useEffect } from 'react';
import {
  CloudSun,
  Droplets,
  Wind,
  Thermometer,
  Activity,
  Calendar,
  MapPin,
  Clock,
  Search,
  Filter,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { WeatherData, MarketPrice } from '../types';
import { useLanguage } from '../context/LanguageContext';

export const WeatherMarketPage: React.FC = () => {
  const { language } = useLanguage();

  const [districts, setDistricts] = useState<any[]>([]);
  const [selectedDistrict, setSelectedDistrict] = useState('Belagavi');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);

  const [marketPrices, setMarketPrices] = useState<MarketPrice[]>([]);
  const [marketLoading, setMarketLoading] = useState(false);
  const [marketSearchCrop, setMarketSearchCrop] = useState('');
  const [marketFilterDistrict, setMarketFilterDistrict] = useState('All');

  useEffect(() => {
    async function init() {
      try {
        const dists = await api.getDistricts();
        setDistricts(dists);
      } catch (e) {}
    }
    init();
  }, []);

  // Fetch weather when district changes
  useEffect(() => {
    async function loadWeather() {
      setWeatherLoading(true);
      try {
        const data = await api.getWeather(selectedDistrict);
        setWeather(data);
      } catch (err) {
        console.error('Weather load error:', err);
      } finally {
        setWeatherLoading(false);
      }
    }
    loadWeather();
  }, [selectedDistrict]);

  // Fetch APMC market prices
  useEffect(() => {
    async function loadMarket() {
      setMarketLoading(true);
      try {
        const data = await api.getMarketPrices(
          marketSearchCrop || undefined,
          marketFilterDistrict === 'All' ? undefined : marketFilterDistrict
        );
        setMarketPrices(data);
      } catch (err) {
        console.error('Market prices error:', err);
      } finally {
        setMarketLoading(false);
      }
    }
    loadMarket();
  }, [marketSearchCrop, marketFilterDistrict]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <CloudSun className="w-4 h-4 text-[#2F7650]" />
          <span>Meteorological & Mandi Intelligence</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ & ಮಾರುಕಟ್ಟೆ ಧಾರಣೆ (Weather & Market Prices)
        </h1>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] max-w-3xl leading-relaxed">
          {language === 'kn'
            ? 'ಕರ್ನಾಟಕದ 31 ಜಿಲ್ಲೆಗಳ ಲೈವ್ ಹವಾಮಾನ ಮಾಹಿತಿ ಮತ್ತು ಪ್ರಮುಖ ಎಪಿಎಂಸಿ ಮಂಡಿಗಳ ದೈನಂದಿನ ಕೃಷಿ ಉತ್ಪನ್ನಗಳ ಅಧಿಕೃತ ಬೆಲೆ ವಿವರಗಳು.'
            : 'Live meteorological updates across Karnataka districts and verified APMC mandi modal commodity price benchmarks.'}
        </p>
      </div>

      {/* SECTION 1: LIVE DISTRICT WEATHER FORECAST */}
      <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 sm:p-8 shadow-sm space-y-6">
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4">
          <div>
            <h2 className="text-xl font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
              <CloudSun className="w-5 h-5 text-[#2F7650]" />
              <span>ಜಿಲ್ಲಾವಾರು ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ (District Weather Forecast)</span>
            </h2>
            <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] mt-0.5">
              Select any of the 31 Karnataka districts for real-time agricultural meteorological forecast
            </p>
          </div>

          {/* District Selector */}
          <div className="w-full sm:w-64">
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="w-full px-3.5 py-2 text-xs sm:text-sm rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] focus:outline-none focus:border-[#2F7650] font-kannada"
            >
              {districts.map((d) => (
                <option key={d.name} value={d.name}>
                  {d.name_kn} ({d.name}) — {d.region}
                </option>
              ))}
            </select>
          </div>
        </div>

        {weatherLoading ? (
          <div className="p-8 text-center">
            <div className="w-8 h-8 rounded-full border-2 border-[#174C36] border-t-transparent animate-spin mx-auto"></div>
            <p className="text-xs text-[#69766D] mt-2 font-kannada">ಹವಾಮಾನ ವಿವರ ಪಡೆಯಲಾಗುತ್ತಿದೆ...</p>
          </div>
        ) : weather ? (
          <div className="space-y-6">
            
            {/* Weather Primary Highlight Card */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-[#174C36] via-[#123B2B] to-[#2F7650] text-white shadow-xl items-center">
              
              <div className="md:col-span-6 space-y-2">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-[#D8AA48]" />
                  <span className="text-lg font-bold font-kannada">{weather.district_kn} ({weather.district})</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-[#D8AA48]">
                    {weather.region}
                  </span>
                </div>
                <div className="flex items-baseline gap-3">
                  <span className="text-4xl sm:text-5xl font-extrabold tracking-tight">
                    {weather.temperature}°C
                  </span>
                  <span className="text-lg font-bold text-[#D8AA48] font-kannada">
                    {weather.condition_kn} ({weather.condition})
                  </span>
                </div>
                <p className="text-xs text-[#EAF3E9]/70 flex items-center gap-1.5 pt-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>ಕೊನೆಯ ಅಪ್ಡೇಟ್ (Updated): {weather.last_updated}</span>
                </p>
              </div>

              <div className="md:col-span-6 grid grid-cols-3 gap-3 text-center">
                <div className="p-3.5 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10">
                  <Droplets className="w-5 h-5 text-cyan-300 mx-auto mb-1" />
                  <span className="text-[11px] text-[#EAF3E9]/80 block font-kannada">ಆರ್ದ್ರತೆ (Humidity)</span>
                  <span className="text-base font-extrabold">{weather.humidity}%</span>
                </div>

                <div className="p-3.5 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10">
                  <CloudSun className="w-5 h-5 text-[#D8AA48] mx-auto mb-1" />
                  <span className="text-[11px] text-[#EAF3E9]/80 block font-kannada">ಮಳೆ (Rainfall)</span>
                  <span className="text-base font-extrabold">{weather.precipitation} mm</span>
                </div>

                <div className="p-3.5 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10">
                  <Wind className="w-5 h-5 text-teal-300 mx-auto mb-1" />
                  <span className="text-[11px] text-[#EAF3E9]/80 block font-kannada">ಗಾಳಿ (Wind)</span>
                  <span className="text-base font-extrabold">{weather.wind_speed} km/h</span>
                </div>
              </div>
            </div>

            {/* SPECIALIZED COASTAL WEATHER & FLOOD-RISK INTELLIGENCE CARD */}
            {weather.coastal_intelligence && weather.coastal_intelligence.is_coastal && (
              <div className="p-6 sm:p-7 rounded-3xl border-2 border-cyan-500/40 bg-gradient-to-br from-cyan-950/20 via-[#11221A] to-emerald-950/20 space-y-6 shadow-md">
                
                {/* Header with Zone Badge */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 rounded-full text-xs font-bold bg-cyan-100 dark:bg-cyan-950/80 text-cyan-800 dark:text-cyan-300 border border-cyan-300">
                        🌊 {language === 'kn' ? weather.coastal_intelligence.zone_kn : weather.coastal_intelligence.zone}
                      </span>
                      <span className="text-xs text-[#69766D] dark:text-[#9BB0A4] font-semibold">
                        {weather.coastal_intelligence.district} • {weather.coastal_intelligence.taluk}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                      ಕರಾವಳಿ ಹವಾಮಾನ & ಪ್ರವಾಹ ಅಪಾಯ ವಿಶ್ಲೇಷಣೆ (Coastal Heavy-Rain & Flood Intelligence)
                    </h3>
                  </div>

                  {/* 5-Level Risk Badge */}
                  <div className="shrink-0 flex items-center gap-2">
                    <span
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold shadow-sm flex items-center gap-1.5 ${
                        weather.coastal_intelligence.heavy_rain_risk_level === 'OFFICIAL FLOOD WARNING'
                          ? 'bg-red-600 text-white animate-pulse'
                          : weather.coastal_intelligence.heavy_rain_risk_level === 'HIGH RISK'
                          ? 'bg-amber-600 text-white'
                          : weather.coastal_intelligence.heavy_rain_risk_level === 'MODERATE RISK'
                          ? 'bg-yellow-500 text-black'
                          : weather.coastal_intelligence.heavy_rain_risk_level === 'LOW RISK'
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-500 text-white'
                      }`}
                    >
                      <AlertCircle className="w-4 h-4" />
                      <span>{weather.coastal_intelligence.heavy_rain_risk_level}</span>
                    </span>
                  </div>
                </div>

                {/* Risk Breakdown Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Heavy-Rain Risk */}
                  <div className="p-4 rounded-2xl bg-white dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
                    <span className="text-xs font-bold text-[#174C36] dark:text-[#75A96A] block font-kannada">
                      🌧️ ಭಾರೀ ಮಳೆ ಅಪಾಯದ ಮಟ್ಟ (Heavy-Rain Risk Level)
                    </span>
                    <p className="text-base font-extrabold text-[#19251E] dark:text-[#EDF3EF]">
                      {weather.coastal_intelligence.heavy_rain_risk_level_kn} ({weather.coastal_intelligence.heavy_rain_risk_level})
                    </p>
                    <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] pt-1">
                      {language === 'kn' ? weather.coastal_intelligence.risk_description_kn : weather.coastal_intelligence.risk_description_en}
                    </p>
                  </div>

                  {/* Riverine Flood Probability */}
                  <div className="p-4 rounded-2xl bg-white dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] space-y-1">
                    <span className="text-xs font-bold text-cyan-700 dark:text-cyan-400 block font-kannada">
                      🌊 ನದಿ ಪ್ರವಾಹ ಸಂಭವನೀಯತೆ (Riverine Flood Probability)
                    </span>
                    <p className="text-base font-extrabold text-[#19251E] dark:text-[#EDF3EF]">
                      {weather.coastal_intelligence.riverine_flood_probability_kn}
                    </p>
                    <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] pt-1 font-kannada">
                      ಪ್ರಮುಖ ನದಿಗಳು: {weather.coastal_intelligence.major_rivers.join(', ')}
                    </p>
                  </div>
                </div>

                {/* Heavy-Rain vs Flood Hydrological Distinction Banner */}
                <div className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/60 text-xs leading-relaxed space-y-1">
                  <span className="font-bold text-blue-900 dark:text-blue-300 block font-kannada">
                    ⚠️ ವೈಜ್ಞಾನಿಕ ಹವಾಮಾನ ಸ್ಪಷ್ಟೀಕರಣ (Hydrological Distinction):
                  </span>
                  <p className="text-blue-800 dark:text-blue-200 font-kannada">
                    {language === 'kn'
                      ? weather.coastal_intelligence.rain_vs_flood_distinction_kn
                      : weather.coastal_intelligence.rain_vs_flood_distinction_en}
                  </p>
                </div>

                {/* Proactive Crop Insurance Advisory Card */}
                {weather.coastal_intelligence.proactive_insurance_advisory && (
                  <div className="p-5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-300 dark:border-emerald-800/60 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-[#174C36] dark:text-[#75A96A] font-kannada">
                        🛡️ ಮುಂಜಾಗ್ರತಾ ಬೆಳೆ ವಿಮೆ ಸಲಹೆ (PMFBY / Samrakshane Advisory)
                      </span>
                      <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#174C36] text-white">
                        Helpline: 1800-180-1551
                      </span>
                    </div>
                    <p className="text-xs text-[#19251E] dark:text-[#EDF3EF] leading-relaxed">
                      {language === 'kn'
                        ? weather.coastal_intelligence.proactive_insurance_advisory.calamity_72h_rule_kn
                        : weather.coastal_intelligence.proactive_insurance_advisory.calamity_72h_rule_en}
                    </p>
                    <p className="text-[11px] text-amber-800 dark:text-amber-300 font-semibold pt-1">
                      {language === 'kn'
                        ? weather.coastal_intelligence.proactive_insurance_advisory.non_retroactive_warning_kn
                        : weather.coastal_intelligence.proactive_insurance_advisory.non_retroactive_warning_en}
                    </p>
                  </div>
                )}

                {/* Crop-Specific Agronomic & Drainage Precautions */}
                <div className="space-y-2 pt-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                    ಬೆಳೆವಾರು ಬಸಿಗಾಲುವೆ ಮತ್ತು ರೋಗ ತಡೆ ಮುನ್ನೆಚ್ಚರಿಕೆಗಳು (Crop Drainage & Disease Safeguards):
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {weather.coastal_intelligence.crop_precautions.map((cp) => (
                      <div
                        key={cp.crop}
                        className="p-3.5 rounded-xl bg-white dark:bg-[#0B1711] border border-[#E2E8DF] dark:border-[#1E382B] text-xs space-y-1"
                      >
                        <span className="font-bold text-[#174C36] dark:text-[#75A96A] block font-kannada">
                          🌱 {cp.crop_kn} ({cp.crop})
                        </span>
                        <p className="text-[#19251E] dark:text-[#EDF3EF] leading-relaxed">
                          {language === 'kn' ? cp.precaution_kn : cp.precaution_en}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Source & Transparency Stamp */}
            <div className="flex items-center justify-between text-[11px] text-[#69766D] dark:text-[#9BB0A4] px-1">
              <span>ಮೂಲ (Source): {weather.source}</span>
              <span className="inline-flex items-center gap-1 font-semibold text-green-700 dark:text-green-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {weather.is_live ? 'Live Sensor Feed' : 'Certified Meteorological Archive'}
              </span>
            </div>
          </div>
        ) : null}
      </div>

      {/* SECTION 2: KARNATAKA APMC MANDI PRICES */}
      <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 sm:p-8 shadow-sm space-y-6">
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-4">
          <div>
            <h2 className="text-xl font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#2F7650]" />
              <span>ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಮಂಡಿ ಮಾರುಕಟ್ಟೆ ಧಾರಣೆ (APMC Mandi Prices)</span>
            </h2>
            <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] mt-0.5">
              Verified minimum, maximum, and modal wholesale prices across Karnataka agricultural markets
            </p>
          </div>

          {/* Commodity and District Quick Filters */}
          <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-48">
              <input
                type="text"
                placeholder="ಬೆಳೆ ಹುಡುಕಿ (Search Crop)..."
                value={marketSearchCrop}
                onChange={(e) => setMarketSearchCrop(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
              />
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-[#69766D]" />
            </div>

            <select
              value={marketFilterDistrict}
              onChange={(e) => setMarketFilterDistrict(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-xl border border-[#E2E8DF] dark:border-[#1E382B] bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF]"
            >
              <option value="All">ಎಲ್ಲಾ ಮಂಡಿಗಳು (All Mandis)</option>
              {districts.map((d) => (
                <option key={d.name} value={d.name}>
                  {d.name} Mandi
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Market Prices Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-[#F7F9F5] dark:bg-[#0B1711] text-[#69766D] dark:text-[#9BB0A4] uppercase text-[11px] font-bold tracking-wider border-b border-[#E2E8DF] dark:border-[#1E382B]">
              <tr>
                <th className="py-3 px-4">ಕೃಷಿ ಉತ್ಪನ್ನ (Commodity)</th>
                <th className="py-3 px-4">ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ (Mandi)</th>
                <th className="py-3 px-4">ಜಿಲ್ಲೆ (District)</th>
                <th className="py-3 px-4">ಕನಿಷ್ಠ ದರ (Min)</th>
                <th className="py-3 px-4">ಗರಿಷ್ಠ ದರ (Max)</th>
                <th className="py-3 px-4 text-[#174C36] dark:text-[#75A96A]">ಮಾದರಿ ದರ (Modal Price)</th>
                <th className="py-3 px-4">ದಿನಾಂಕ (Date)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8DF] dark:divide-[#1E382B] font-medium">
              {marketPrices.map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-[#19251E] dark:text-[#EDF3EF]">
                    <span className="font-kannada block">{item.crop_kn}</span>
                    <span className="text-xs font-normal text-[#69766D] dark:text-[#9BB0A4]">{item.crop}</span>
                  </td>
                  <td className="py-3.5 px-4 text-[#19251E] dark:text-[#EDF3EF]">
                    {item.market}
                  </td>
                  <td className="py-3.5 px-4 text-[#69766D] dark:text-[#9BB0A4]">
                    {item.district}
                  </td>
                  <td className="py-3.5 px-4 text-[#69766D] dark:text-[#9BB0A4]">
                    ₹ {item.min_price}
                  </td>
                  <td className="py-3.5 px-4 text-[#69766D] dark:text-[#9BB0A4]">
                    ₹ {item.max_price}
                  </td>
                  <td className="py-3.5 px-4 font-extrabold text-[#174C36] dark:text-[#92C987] text-base">
                    ₹ {item.modal_price}
                    <span className="text-[10px] font-normal text-[#69766D] block">/ ಕ್ವಿಂಟಾಲ್</span>
                  </td>
                  <td className="py-3.5 px-4 text-[11px] text-[#69766D] dark:text-[#9BB0A4]">
                    {item.date}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Notice on Market Data */}
        <p className="text-[11px] text-[#69766D] dark:text-[#9BB0A4] leading-relaxed pt-2">
          *ಮಾರುಕಟ್ಟೆ ಧಾರಣೆಗಳನ್ನು ಕರ್ನಾಟಕ ಕೃಷಿ ಮಾರಾಟ ಮಂಡಳಿ ಹಾಗೂ ಎಪಿಎಂಸಿ ಮಂಡಿ ದೈನಂದಿನ ವರದಿಗಳಿಂದ ಸಂಗ್ರಹಿಸಲಾಗಿದೆ. ದರಗಳು ಗುಣಮಟ್ಟ ಹಾಗೂ ತೇವಾಂಶದ ಆಧಾರದ ಮೇಲೆ ವ್ಯತ್ಯಾಸವಾಗಬಹುದು.
        </p>
      </div>
    </div>
  );
};
