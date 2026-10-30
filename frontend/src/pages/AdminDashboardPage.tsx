import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  Plus,
  Edit,
  Eye,
  CheckCircle,
  XCircle,
  Activity,
  Users,
  Layers,
  Save,
  Trash2,
  Database
} from 'lucide-react';
import { api } from '../services/api';
import { Scheme } from '../types';

export const AdminDashboardPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New Scheme Form State
  const [newSchemeId, setNewSchemeId] = useState('');
  const [newSchemeName, setNewSchemeName] = useState('');
  const [newSchemeNameKn, setNewSchemeNameKn] = useState('');
  const [newDept, setNewDept] = useState('');
  const [newDeptKn, setNewDeptKn] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newDescKn, setNewDescKn] = useState('');
  const [newBenefits, setNewBenefits] = useState('');
  const [newBenefitsKn, setNewBenefitsKn] = useState('');
  const [newOfficialUrl, setNewOfficialUrl] = useState('');
  const [newStatus, setNewStatus] = useState<'Verified' | 'Synthetic Demo'>('Verified');
  const [newMaxLand, setNewMaxLand] = useState<string>('');

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [sData, statData] = await Promise.all([
        api.getSchemes(),
        api.getAdminStats(),
      ]);
      setSchemes(sData);
      setStats(statData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (id: number) => {
    try {
      await api.toggleSchemeActive(id);
      await loadAdminData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateScheme = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createScheme({
        scheme_id: newSchemeId.trim().toUpperCase(),
        scheme_name: newSchemeName.trim(),
        scheme_name_kn: newSchemeNameKn.trim(),
        scheme_type: newStatus === 'Synthetic Demo' ? 'Synthetic Demonstration Record' : 'Karnataka State Scheme',
        department: newDept.trim(),
        department_kn: newDeptKn.trim(),
        description: newDesc.trim(),
        description_kn: newDescKn.trim(),
        eligibility_conditions: JSON.stringify({ land_limit: newMaxLand || 'None' }),
        eligible_farmer_categories: ['Small and Marginal', 'All'],
        eligible_crops: ['All'],
        land_requirements: newMaxLand ? `Up to ${newMaxLand} acres` : 'No land ceiling',
        max_land_acres: newMaxLand ? parseFloat(newMaxLand) : undefined,
        benefit_details: newBenefits.trim(),
        benefit_details_kn: newBenefitsKn.trim(),
        required_documents: ['RTC Pahani', 'Aadhaar Card', 'Bank Passbook'],
        application_steps: ['1. Apply through official state agriculture portal.'],
        official_url: newOfficialUrl.trim() || 'https://raitamitra.karnataka.gov.in',
        source_url: 'https://raitamitra.karnataka.gov.in',
        verification_date: new Date().toISOString().split('T')[0],
        verification_status: newStatus,
        active_status: true,
      });

      setShowAddModal(false);
      await loadAdminData();
      alert('ಹೊಸ ಯೋಜನೆ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ (New Scheme Added)!');
    } catch (err: any) {
      alert(err.message || 'Error creating scheme');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D8AA48]">
            <ShieldCheck className="w-4 h-4 text-[#2F7650]" />
            <span>Authorized Administration Portal</span>
          </div>
          <h1 className="text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF] font-kannada mt-1">
            ಅಡ್ಮಿನ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ (Admin Dashboard)
          </h1>
          <p className="text-xs text-[#69766D] dark:text-[#9BB0A4]">
            Manage verified scheme catalog, synthetic demo sandbox benchmarks, and operational telemetry
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#174C36] hover:bg-[#123B2B] text-white text-xs font-bold shadow-md transition-colors"
        >
          <Plus className="w-4 h-4 text-[#D8AA48]" />
          <span>ಹೊಸ ಯೋಜನೆ ಸೇರಿಸಿ (Add Scheme)</span>
        </button>
      </div>

      {/* Telemetry Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          <div className="bg-white dark:bg-[#11221A] p-5 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm">
            <div className="flex items-center justify-between text-xs text-[#69766D] mb-1">
              <span>ಒಟ್ಟು ಯೋಜನೆಗಳು</span>
              <Database className="w-4 h-4 text-[#2F7650]" />
            </div>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF]">
              {stats.total_schemes}
            </p>
            <span className="text-[10px] text-green-600 font-bold">
              {stats.verified_schemes} Verified • {stats.demo_schemes} Demo
            </span>
          </div>

          <div className="bg-white dark:bg-[#11221A] p-5 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm">
            <div className="flex items-center justify-between text-xs text-[#69766D] mb-1">
              <span>ನೋಂದಾಯಿತ ರೈತರು</span>
              <Users className="w-4 h-4 text-[#D8AA48]" />
            </div>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF]">
              {stats.registered_farmers}
            </p>
            <span className="text-[10px] text-blue-600 font-bold">Active Karnataka Profiles</span>
          </div>

          <div className="bg-white dark:bg-[#11221A] p-5 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm">
            <div className="flex items-center justify-between text-xs text-[#69766D] mb-1">
              <span>ನಡೆದ AI ಧ್ವನಿ ಸಂವಾದಗಳು</span>
              <Activity className="w-4 h-4 text-purple-600" />
            </div>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#19251E] dark:text-[#EDF3EF]">
              {stats.ai_conversations_held}
            </p>
            <span className="text-[10px] text-purple-600 font-bold">Kannada NLU Invocations</span>
          </div>

          <div className="bg-white dark:bg-[#11221A] p-5 rounded-2xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-sm">
            <div className="flex items-center justify-between text-xs text-[#69766D] mb-1">
              <span>ಸಿಸ್ಟಮ್ ಸ್ಥಿತಿ</span>
              <ShieldCheck className="w-4 h-4 text-green-600" />
            </div>
            <p className="text-sm font-extrabold text-green-700 dark:text-green-400 mt-2">
              {stats.system_status}
            </p>
            <span className="text-[10px] text-[#69766D] block mt-1">{stats.last_audit_sync}</span>
          </div>
        </div>
      )}

      {/* Schemes Management Table */}
      <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] p-6 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
          ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ನಿರ್ವಹಣೆ (Scheme Inventory)
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-[#F7F9F5] dark:bg-[#0B1711] text-[#69766D] dark:text-[#9BB0A4] uppercase text-[11px] font-bold tracking-wider border-b border-[#E2E8DF] dark:border-[#1E382B]">
              <tr>
                <th className="py-3 px-4">Scheme ID</th>
                <th className="py-3 px-4">ಹೆಸರು (Name)</th>
                <th className="py-3 px-4">ಇಲಾಖೆ (Department)</th>
                <th className="py-3 px-4">ವರ್ಗೀಕರಣ (Status)</th>
                <th className="py-3 px-4">ಸಕ್ರಿಯ (Active)</th>
                <th className="py-3 px-4 text-right">ಕ್ರಮಗಳು (Actions)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8DF] dark:divide-[#1E382B]">
              {schemes.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-[#174C36] dark:text-[#75A96A]">
                    {s.scheme_id}
                  </td>
                  <td className="py-3 px-4 font-semibold text-[#19251E] dark:text-[#EDF3EF]">
                    <span className="font-kannada block">{s.scheme_name_kn}</span>
                    <span className="text-xs text-[#69766D] font-normal">{s.scheme_name}</span>
                  </td>
                  <td className="py-3 px-4 text-xs text-[#69766D] dark:text-[#9BB0A4]">
                    {s.department}
                  </td>
                  <td className="py-3 px-4">
                    {s.verification_status === 'Verified' ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-950 text-green-800 dark:text-green-300">
                        Verified Official
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">
                        Synthetic Demo
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => handleToggleActive(s.id)}
                      className={`text-xs font-bold px-2.5 py-1 rounded-lg ${
                        s.active_status
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'
                      }`}
                    >
                      {s.active_status ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <a
                      href={s.official_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-[#174C36] dark:text-[#75A96A] hover:underline"
                    >
                      Portal Link
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Scheme Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#11221A] rounded-3xl border border-[#E2E8DF] dark:border-[#1E382B] shadow-2xl p-6 sm:p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto space-y-6">
            
            <div className="flex items-center justify-between border-b pb-4">
              <h3 className="text-lg font-bold text-[#19251E] dark:text-[#EDF3EF] font-kannada">
                ಹೊಸ ಕೃಷಿ ಯೋಜನೆ ಸೇರಿಸಿ (Add New Scheme)
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-500 hover:text-gray-800"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateScheme} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold mb-1">Scheme ID (e.g. KRISHI-SAMRUDDHI)</label>
                  <input
                    type="text"
                    required
                    value={newSchemeId}
                    onChange={(e) => setNewSchemeId(e.target.value)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1">Status (Verification)</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value as any)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                  >
                    <option value="Verified">Verified Official Scheme</option>
                    <option value="Synthetic Demo">Synthetic Demo Record</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold mb-1">Scheme Name (English)</label>
                  <input
                    type="text"
                    required
                    value={newSchemeName}
                    onChange={(e) => setNewSchemeName(e.target.value)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1 font-kannada">ಯೋಜನೆ ಹೆಸರು (ಕನ್ನಡ)</label>
                  <input
                    type="text"
                    required
                    value={newSchemeNameKn}
                    onChange={(e) => setNewSchemeNameKn(e.target.value)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711] font-kannada"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold mb-1">Department</label>
                  <input
                    type="text"
                    required
                    value={newDept}
                    onChange={(e) => setNewDept(e.target.value)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1 font-kannada">ಇಲಾಖೆ (ಕನ್ನಡ)</label>
                  <input
                    type="text"
                    required
                    value={newDeptKn}
                    onChange={(e) => setNewDeptKn(e.target.value)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711] font-kannada"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold mb-1 font-kannada">ವಿವರಣೆ (ಕನ್ನಡ ವಿವರ)</label>
                <textarea
                  rows={2}
                  required
                  value={newDescKn}
                  onChange={(e) => setNewDescKn(e.target.value)}
                  className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711] font-kannada"
                />
              </div>

              <div>
                <label className="block font-bold mb-1">Description (English)</label>
                <textarea
                  rows={2}
                  required
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold mb-1">Key Benefits (English)</label>
                  <input
                    type="text"
                    required
                    value={newBenefits}
                    onChange={(e) => setNewBenefits(e.target.value)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1 font-kannada">ಪ್ರಯೋಜನ / ಸೌಲಭ್ಯ (ಕನ್ನಡ)</label>
                  <input
                    type="text"
                    required
                    value={newBenefitsKn}
                    onChange={(e) => setNewBenefitsKn(e.target.value)}
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711] font-kannada"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold mb-1">Max Land Ceiling (Acres, optional)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={newMaxLand}
                    onChange={(e) => setNewMaxLand(e.target.value)}
                    placeholder="e.g. 5.0"
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1">Official Portal URL</label>
                  <input
                    type="url"
                    required
                    value={newOfficialUrl}
                    onChange={(e) => setNewOfficialUrl(e.target.value)}
                    placeholder="https://..."
                    className="w-full p-2.5 rounded-xl border bg-[#F7F9F5] dark:bg-[#0B1711]"
                  />
                </div>
              </div>

              <div className="pt-4 border-t flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl border text-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-[#174C36] text-white font-bold"
                >
                  Save Scheme
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
