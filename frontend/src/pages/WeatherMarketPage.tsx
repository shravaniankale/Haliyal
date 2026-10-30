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
