import React, { useState, useEffect } from 'react';
import {
  CreditCard,
  Calculator,
  ShieldCheck,
  CheckCircle2,
  FileText,
  ExternalLink,
  Percent,
  Banknote,
  Clock,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { Loan } from '../types';
import { useLanguage } from '../context/LanguageContext';

export const LoansPage: React.FC = () => {
  const { language } = useLanguage();
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);

  // EMI Calculator State
  const [amount, setAmount] = useState<number>(100000);
  const [interestRate, setInterestRate] = useState<number>(4.0); // 4% default for KCC
  const [tenureYears, setTenureYears] = useState<number>(3);
  const [emiResult, setEmiResult] = useState<{
    monthly_emi: number;
    total_interest: number;
    total_payment: number;
    principal: number;
  }>({
    monthly_emi: 2952.4,
    total_interest: 6286.39,
    total_payment: 106286.39,
    principal: 100000,
  });

  useEffect(() => {
    async function loadLoans() {
      try {
        const data = await api.getLoans();
        setLoans(data);
      } catch (err) {
        console.error('Failed to load loans:', err);
      } finally {
        setLoading(false);
      }
    }
    loadLoans();
  }, []);

  // Compute EMI via backend API or instant math
  useEffect(() => {
    async function updateEmi() {
      try {
        const res = await api.calculateEmi({
          amount,
          interest_rate: interestRate,
          tenure_months: tenureYears * 12,
        });
        setEmiResult(res);
      } catch (e) {
        // Fallback exact formula
        const p = amount;
        const r = interestRate / 100 / 12;
        const n = tenureYears * 12;
        if (r === 0) {
          const emi = p / n;
          setEmiResult({ monthly_emi: emi, total_interest: 0, total_payment: p, principal: p });
        } else {
          const factor = Math.pow(1 + r, n);
          const emi = (p * r * factor) / (factor - 1);
          const totalPay = emi * n;
          setEmiResult({
            monthly_emi: Math.round(emi * 100) / 100,
            total_interest: Math.round((totalPay - p) * 100) / 100,
            total_payment: Math.round(totalPay * 100) / 100,
            principal: p,
          });
        }
      }
    }
    updateEmi();
  }, [amount, interestRate, tenureYears]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
          <CreditCard className="w-4 h-4 text-[#2F7650]" />
          <span>Institutional Agricultural Credit</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ಕೃಷಿ ಸಾಲಗಳು & ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (Agri Loans & KCC)
        </h1>
        <p className="text-sm text-[#69766D] dark:text-[#9BB0A4] max-w-3xl leading-relaxed">
          {language === 'kn'
            ? 'ಕೇಂದ್ರ ಮತ್ತು ರಾಜ್ಯ ಸರ್ಕಾರದ ಬಡ್ಡಿ ಸಹಾಯಧನದೊಂದಿಗೆ ಲಭ್ಯವಿರುವ ಬೆಳೆ ಸಾಲಗಳು, ಯಂತ್ರೋಪಕರಣ ಸಾಲಗಳು ಹಾಗೂ ಸೌರ ಪಂಪ್‌ಸೆಟ್ ಆರ್ಥಿಕ ನೆರವು.'
            : 'Explore verified subsidized agricultural credit, Kisan Credit Card benefits, interest subvention guidelines, and calculate monthly repayment installments.'}
        </p>
      </div>

      {/* INTERACTIVE EMI CALCULATOR */}
      <div className="bg-gradient-to-br from-white to-[#F7F9F5] dark:from-[#11221A] dark:to-[#0B1711] rounded-3xl border-2 border-[#174C36]/20 dark:border-[#75A96A]/30 p-6 sm:p-10 shadow-lg space-y-8">
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#E2E8DF] dark:border-[#1E382B] pb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-[#174C36] flex items-center justify-center text-white shadow">
              <Calculator className="w-6 h-6 text-[#D8AA48]" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                ಕೃಷಿ ಸಾಲದ EMI ಕ್ಯಾಲ್ಕುಲೇಟರ್ (Agri Loan EMI Calculator)
              </h2>
              <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                Calculate accurate monthly installments, total interest payable, and total loan cost
              </p>
            </div>
          </div>

          <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] border border-[#75A96A]/40">
            ಗಣಿತಶಾಸ್ತ್ರೀಯ ನಿಖರ ಲೆಕ್ಕಾಚಾರ
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Sliders & Inputs (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            
            {/* Amount */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">
                <span className="font-kannada">ಸಾಲದ ಮೊತ್ತ (Loan Amount):</span>
                <span className="text-base text-[#174C36] dark:text-[#75A96A] font-extrabold">
                  ₹ {amount.toLocaleString('en-IN')}
                </span>
              </div>
              <input
                type="range"
                min="10000"
                max="1000000"
                step="5000"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                className="w-full h-2 bg-[#E2E8DF] rounded-lg appearance-none cursor-pointer accent-[#174C36]"
              />
              <div className="flex justify-between text-[10px] text-[#69766D]">
                <span>₹ 10,000</span>
                <span>₹ 3,00,000 (KCC Cap)</span>
                <span>₹ 10,00,000</span>
              </div>
            </div>

            {/* Interest Rate */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">
                <span className="font-kannada">ವಾರ್ಷಿಕ ಬಡ್ಡಿದರ (Interest Rate p.a.):</span>
                <span className="text-base text-[#174C36] dark:text-[#75A96A] font-extrabold">
                  {interestRate}%
                </span>
              </div>
              <input
                type="range"
                min="2.0"
                max="14.0"
                step="0.5"
                value={interestRate}
                onChange={(e) => setInterestRate(Number(e.target.value))}
                className="w-full h-2 bg-[#E2E8DF] rounded-lg appearance-none cursor-pointer accent-[#174C36]"
              />
              <div className="flex justify-between text-[10px] text-[#69766D]">
                <span>2%</span>
                <span className="text-[#D8AA48] font-bold">4% (KCC Prompt Rate)</span>
                <span>7% (Standard)</span>
                <span>14%</span>
              </div>
            </div>

            {/* Tenure */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-[#19251E] dark:text-[#EDF3EF]">
                <span className="font-kannada">ಮರುಪಾವತಿ ಅವಧಿ (Tenure):</span>
                <span className="text-base text-[#174C36] dark:text-[#75A96A] font-extrabold">
                  {tenureYears} ವರ್ಷಗಳು ({tenureYears * 12} Months)
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={tenureYears}
                onChange={(e) => setTenureYears(Number(e.target.value))}
                className="w-full h-2 bg-[#E2E8DF] rounded-lg appearance-none cursor-pointer accent-[#174C36]"
              />
              <div className="flex justify-between text-[10px] text-[#69766D]">
                <span>1 Year</span>
                <span>3 Years</span>
                <span>5 Years</span>
                <span>10 Years</span>
              </div>
            </div>
          </div>

          {/* Results Display Box (5 cols) */}
          <div className="lg:col-span-5 bg-[#174C36] text-white p-6 sm:p-8 rounded-3xl shadow-xl space-y-6">
            
            <div className="text-center pb-4 border-b border-white/15">
              <p className="text-xs font-semibold text-[#EAF3E9]/80 uppercase tracking-wider font-kannada">
                ಮಾಸಿಕ ಕಂತು (Monthly EMI)
              </p>
              <p className="text-3xl sm:text-4xl font-extrabold text-[#D8AA48] mt-2">
                ₹ {emiResult.monthly_emi.toLocaleString('en-IN')}
              </p>
              <p className="text-[11px] text-[#EAF3E9]/70 mt-1">per month for {tenureYears * 12} months</p>
            </div>

            <div className="space-y-3 text-xs sm:text-sm">
              <div className="flex items-center justify-between">
                <span className="text-[#EAF3E9]/80 font-kannada">ಮೂಲ ಸಾಲದ ಮೊತ್ತ (Principal):</span>
                <span className="font-bold text-white">₹ {emiResult.principal.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#EAF3E9]/80 font-kannada">ಒಟ್ಟು ಪಾವತಿಸಬೇಕಾದ ಬಡ್ಡಿ (Interest):</span>
                <span className="font-bold text-[#D8AA48]">₹ {emiResult.total_interest.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-white/15 text-sm sm:text-base font-extrabold">
                <span className="text-white font-kannada">ಒಟ್ಟು ಮರುಪಾವತಿ (Total Repayment):</span>
                <span className="text-white">₹ {emiResult.total_payment.toLocaleString('en-IN')}</span>
              </div>
            </div>

            <p className="text-[10px] text-[#EAF3E9]/60 text-center leading-relaxed">
              *ಸೂಚನೆ: ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ಯೋಜನೆಯಡಿ ಸಕಾಲಕ್ಕೆ ಸಾಲ ಮರುಪಾವತಿ ಮಾಡುವ ರೈತರಿಗೆ ಶೇ. 3% ಹೆಚ್ಚುವರಿ ಬಡ್ಡಿ ರಿಯಾಯಿತಿ ದೊರೆಯುತ್ತದೆ.
            </p>
          </div>
        </div>
      </div>

      {/* VERIFIED LOAN SCHEMES CARDS */}
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
            ಪ್ರಮುಖ ಕೃಷಿ ಸಾಲ ಯೋಜನೆಗಳು (Featured Credit Schemes)
          </h2>
          <p className="text-xs sm:text-sm text-[#69766D] dark:text-[#9BB0A4] mt-0.5">
            Verified institutional credit programs from NABARD, Commercial & Regional Rural Banks (Pragathi Krishna / KVGB)
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {loans.map((loan) => (
            <div
              key={loan.loan_id}
              className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm hover:shadow-lg transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#EAF3E9] dark:bg-[#152E22] text-[#174C36] dark:text-[#92C987] border border-[#75A96A]/40">
                    {loan.loan_id}
                  </span>
                  <span className="text-[11px] font-semibold text-green-700 dark:text-green-400">
                    RBI Approved
                  </span>
                </div>

                <h3 className="font-bold text-lg text-[#19251E] dark:text-[#EDF3EF] font-kannada leading-snug">
                  {loan.name_kn}
                </h3>
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
                  {loan.name}
                </p>

                {/* Purpose */}
                <div className="p-3 rounded-xl bg-[#F7F9F5] dark:bg-[#0B1711] text-xs leading-relaxed space-y-1">
                  <span className="font-bold text-[#174C36] dark:text-[#75A96A] font-kannada">ಉದ್ದೇಶ:</span>
                  <p className="text-[#19251E] dark:text-[#EDF3EF] font-medium font-kannada">
                    {loan.purpose_kn}
                  </p>
                </div>

                {/* Rates & Limit */}
                <div className="space-y-1 text-xs">
                  <div className="flex items-start gap-1.5">
                    <Percent className="w-3.5 h-3.5 text-[#D8AA48] shrink-0 mt-0.5" />
                    <span className="font-semibold text-[#19251E] dark:text-[#EDF3EF]">{loan.interest_rate}</span>
                  </div>
                  <div className="flex items-start gap-1.5">
                    <Banknote className="w-3.5 h-3.5 text-[#2F7650] shrink-0 mt-0.5" />
                    <span className="text-[#69766D] dark:text-[#9BB0A4]">{loan.max_amount}</span>
                  </div>
                </div>

                {/* Eligibility Summary */}
                <p className="text-xs text-[#69766D] dark:text-[#9BB0A4] leading-relaxed pt-2 border-t border-[#E2E8DF] dark:border-[#1E382B]">
                  <strong>ಅರ್ಹತೆ: </strong> {loan.eligibility}
                </p>
              </div>

              {/* Source Link */}
              <div className="pt-3 border-t border-[#E2E8DF] dark:border-[#1E382B] flex items-center justify-between text-xs">
                <span className="text-[11px] text-[#69766D] dark:text-[#9BB0A4] truncate max-w-[180px]">
                  {loan.official_source}
                </span>
                <button
                  onClick={() => alert(`ಈ ಸಾಲಕ್ಕಾಗಿ ನಿಮ್ಮ ಸಮೀಪದ ಬ್ಯಾಂಕ್ ಶಾಖೆ ಅಥವಾ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರವನ್ನು ಭೇಟಿ ಮಾಡಿ. ದಾಖಲೆಗಳು: ${loan.required_documents.join(', ')}`)}
                  className="font-bold text-[#174C36] dark:text-[#75A96A] hover:underline"
                >
                  ದಾಖಲೆಗಳು (Docs)
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
