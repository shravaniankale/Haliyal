import {
  Scheme,
  FarmerProfile,
  EligibilityResponse,
  Loan,
  Crop,
  WeatherData,
  MarketPrice,
  ChatMessage,
  VoiceOption,
  AgriculturalSeasonData,
  CropInsuranceStatus,
  ConversationItem,
  ConversationDetail,
  AnalysisHistoryItem
} from '../types';

const BASE_URL = '/api';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('krishi_mitra_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // Auth
  async register(data: any) {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async login(data: any) {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  async getMe() {
    const res = await fetch(`${BASE_URL}/auth/me`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
  },

  // Farmer & Districts
  async getDistricts(): Promise<any[]> {
    const res = await fetch(`${BASE_URL}/farmer/districts`);
    return res.json();
  },

  async getFarmerProfile(): Promise<FarmerProfile> {
    const res = await fetch(`${BASE_URL}/farmer/profile`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load profile');
    return res.json();
  },

  async updateFarmerProfile(data: any): Promise<FarmerProfile> {
    const res = await fetch(`${BASE_URL}/farmer/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update profile');
    return res.json();
  },

  async deleteFarmerProfile(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${BASE_URL}/farmer/profile`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to delete profile');
    return res.json();
  },

  // Schemes
  async getSchemes(params?: { search?: string; crop?: string; verification?: string; category?: string; status?: string }): Promise<Scheme[]> {
    const q = new URLSearchParams();
    if (params?.search) q.append('search', params.search);
    if (params?.crop) q.append('crop', params.crop);
    if (params?.verification) q.append('verification', params.verification);
    if (params?.category) q.append('category', params.category);
    if (params?.status) q.append('status', params.status);

    const res = await fetch(`${BASE_URL}/schemes?${q.toString()}`, {
      headers: { ...getAuthHeader() },
    });
    return res.json();
  },

  async getSchemeDetail(id: string | number): Promise<Scheme> {
    const res = await fetch(`${BASE_URL}/schemes/${id}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Scheme not found');
    return res.json();
  },

  async getSchemeStats() {
    const res = await fetch(`${BASE_URL}/schemes/stats`, {
      headers: { ...getAuthHeader() },
    });
    return res.json();
  },

  async checkEligibility(data: any): Promise<EligibilityResponse> {
    const res = await fetch(`${BASE_URL}/schemes/eligibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async toggleSaveScheme(id: number): Promise<{ saved: boolean; message: string }> {
    const res = await fetch(`${BASE_URL}/schemes/${id}/save`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
    });
    return res.json();
  },

  async getMySavedSchemes(): Promise<Scheme[]> {
    const res = await fetch(`${BASE_URL}/schemes/saved/my`, {
      headers: { ...getAuthHeader() },
    });
    return res.json();
  },

  // Loans
  async getLoans(): Promise<Loan[]> {
    const res = await fetch(`${BASE_URL}/loans`);
    return res.json();
  },

  async calculateEmi(data: { amount: number; interest_rate: number; tenure_months: number }) {
    const res = await fetch(`${BASE_URL}/loans/calculator`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Crops
  async getCrops(): Promise<Crop[]> {
    const res = await fetch(`${BASE_URL}/crops`);
    return res.json();
  },

  async getCropDetail(cropId: string): Promise<Crop> {
    const res = await fetch(`${BASE_URL}/crops/${cropId}`);
    return res.json();
  },

  // Fertilizer
  async getFertilizerGuidance(data: { crop: string; soil_type: string; growth_stage: string }) {
    const res = await fetch(`${BASE_URL}/fertilizer/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Weather Intelligence
  async getWeather(district: string, taluk?: string): Promise<WeatherData> {
    const q = new URLSearchParams();
    q.append('district', district);
    if (taluk) q.append('taluk', taluk);
    const res = await fetch(`${BASE_URL}/weather?${q.toString()}`);
    return res.json();
  },

  // Agricultural Season Intelligence
  async getAgriculturalSeason(params?: { district?: string; crop?: string; crop_stage?: string }): Promise<AgriculturalSeasonData> {
    const q = new URLSearchParams();
    if (params?.district) q.append('district', params.district);
    if (params?.crop) q.append('crop', params.crop);
    if (params?.crop_stage) q.append('crop_stage', params.crop_stage);
    const res = await fetch(`${BASE_URL}/season?${q.toString()}`);
    return res.json();
  },

  // Crop Insurance Intelligence (PMFBY & Samrakshane)
  async getCropInsuranceStatus(params: {
    district: string;
    taluk?: string;
    crop?: string;
    season?: string;
    land_acres?: number;
  }): Promise<CropInsuranceStatus> {
    const q = new URLSearchParams();
    q.append('district', params.district);
    if (params.taluk) q.append('taluk', params.taluk);
    if (params.crop) q.append('crop', params.crop);
    if (params.season) q.append('season', params.season);
    if (params.land_acres !== undefined) q.append('land_acres', String(params.land_acres));
    const res = await fetch(`${BASE_URL}/insurance/status?${q.toString()}`);
    return res.json();
  },

  // Market Prices
  async getMarketPrices(crop?: string, district?: string): Promise<MarketPrice[]> {
    const q = new URLSearchParams();
    if (crop) q.append('crop', crop);
    if (district) q.append('district', district);
    const res = await fetch(`${BASE_URL}/market-prices?${q.toString()}`);
    return res.json();
  },

  // Chat & Speech
  async sendChatMessage(data: {
    message: string;
    session_id?: string;
    language?: string;
    regional_preference?: string;
    voice_gender?: string;
    speech_speed?: number;
    auto_voice_response?: boolean;
    transcript?: string;
  }) {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async getChatHistory(sessionId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${BASE_URL}/chat/history?session_id=${encodeURIComponent(sessionId)}`, {
      headers: { ...getAuthHeader() }
    });
    return res.json();
  },

  async clearChat(sessionId: string) {
    const res = await fetch(`${BASE_URL}/chat/clear?session_id=${encodeURIComponent(sessionId)}`, {
      method: 'POST',
      headers: { ...getAuthHeader() }
    });
    return res.json();
  },

  // Conversation History Endpoints
  async getConversations(): Promise<ConversationItem[]> {
    const res = await fetch(`${BASE_URL}/chat/conversations`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getConversationDetail(convId: number): Promise<ConversationDetail> {
    const res = await fetch(`${BASE_URL}/chat/conversations/${convId}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to load conversation');
    return res.json();
  },

  async startNewConversation(data: {
    title?: string;
    topic?: string;
    language?: string;
    voice_gender?: string;
  }): Promise<ConversationDetail> {
    const res = await fetch(`${BASE_URL}/chat/conversations/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to start conversation');
    return res.json();
  },

  async deleteConversation(convId: number): Promise<{ status: string; id: number }> {
    const res = await fetch(`${BASE_URL}/chat/conversations/${convId}`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() }
    });
    return res.json();
  },

  async deleteAllConversations(): Promise<{ status: string; deleted_count: number }> {
    const res = await fetch(`${BASE_URL}/chat/conversations`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() }
    });
    return res.json();
  },

  async getUserAnalyses(): Promise<AnalysisHistoryItem[]> {
    const res = await fetch(`${BASE_URL}/chat/analyses`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getVoices(): Promise<VoiceOption[]> {
    const res = await fetch(`${BASE_URL}/speech/voices`);
    return res.json();
  },

  async previewVoice(voiceId: string = 'kn_female') {
    const res = await fetch(`${BASE_URL}/speech/preview?voice_id=${encodeURIComponent(voiceId)}`, {
      method: 'POST'
    });
    return res.json();
  },

  async synthesizeSpeech(text: string, voice_gender?: string, language?: string, speech_speed?: number) {
    const res = await fetch(`${BASE_URL}/speech/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice_gender, language, speech_speed }),
    });
    return res.json();
  },

  // Admin
  async getAdminStats() {
    const res = await fetch(`${BASE_URL}/admin/stats`, {
      headers: { ...getAuthHeader() },
    });
    return res.json();
  },

  async createScheme(data: any) {
    const res = await fetch(`${BASE_URL}/admin/schemes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async updateScheme(id: number, data: any) {
    const res = await fetch(`${BASE_URL}/admin/schemes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async toggleSchemeActive(id: number) {
    const res = await fetch(`${BASE_URL}/admin/schemes/${id}/toggle-status`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
    });
    return res.json();
  }
};
