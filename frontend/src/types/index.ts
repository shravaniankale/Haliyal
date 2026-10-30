export interface User {
  id: number;
  name: string;
  username?: string;
  email?: string;
  mobile: string;
  role: 'farmer' | 'admin';
  voice_assistant_enabled?: boolean;
  auto_voice_response?: boolean;
  voice_input_enabled?: boolean;
  speech_speed?: number;
  created_at: string;
}

export interface FarmerProfile {
  id: number;
  user_id: number;
  name: string;
  username?: string;
  email?: string;
  mobile: string;
  district: string;
  taluk: string;
  village?: string;
  preferred_language: 'kn' | 'en';
  regional_speech_preference: 'North Karnataka' | 'South Karnataka' | 'Standard Kannada' | 'English';
  land_acres?: number;
  land_unit?: 'acres' | 'hectares' | 'guntas';
  land_ownership: 'Own' | 'Tenant' | 'Leased' | 'Shared' | 'Other';
  irrigation_type: 'Rainfed' | 'Borewell' | 'Canal' | 'Drip' | 'Sprinkler' | 'Other';
  farmer_category: 'Small & Marginal' | 'Small farmer' | 'Marginal farmer' | 'General' | 'SC/ST' | 'Women' | 'Other farmer category' | 'Not sure';
  crops_grown: string[];
  primary_crop?: string;
  secondary_crops?: string[];
  soil_type?: string;
  crop_stage?: string;
  sowing_date?: string;
  agricultural_season?: string;
  season?: string;
  theme_preference?: 'light' | 'dark';
  voice_gender_preference?: 'female' | 'male';
  voice_assistant_enabled?: boolean;
  auto_voice_response?: boolean;
  voice_input_enabled?: boolean;
  speech_speed?: number;
  account_created_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Scheme {
  id: number;
  scheme_id: string;
  scheme_name: string;
  scheme_name_kn: string;
  scheme_type: string;
  department: string;
  department_kn: string;
  description: string;
  description_kn: string;
  eligibility_conditions: string;
  eligible_farmer_categories: string[];
  eligible_crops: string[];
  land_requirements?: string;
  max_land_acres?: number;
  min_land_acres?: number;
  required_ownership?: string;
  benefit_details: string;
  benefit_details_kn: string;
  required_documents: string[];
  application_steps: string[];
  official_url: string;
  source_url?: string;
  verification_date: string;
  verification_status: 'Verified' | 'Synthetic Demo';
  active_status: boolean;
  image_url?: string;
  is_saved?: boolean;
}

export interface EligibilityResultItem {
  scheme_id: string;
  scheme_name: string;
  scheme_name_kn: string;
  scheme_type: string;
  department: string;
  status: 'PASS' | 'FAIL' | 'UNKNOWN';
  explanation: string;
  explanation_kn: string;
  matched_conditions: string[];
  failing_conditions: string[];
  missing_information: string[];
  required_documents: string[];
  benefit_details: string;
  benefit_details_kn: string;
  official_url: string;
  verification_status: string;
}

export interface EligibilityResponse {
  total_evaluated: number;
  eligible_count: number;
  results: EligibilityResultItem[];
}

export interface Loan {
  loan_id: string;
  name: string;
  name_kn: string;
  purpose: string;
  purpose_kn: string;
  interest_rate: string;
  max_amount: string;
  eligibility: string;
  required_documents: string[];
  official_source: string;
}

export interface Crop {
  crop_id: string;
  name: string;
  name_kn: string;
  scientific_name: string;
  soil: string;
  soil_kn: string;
  climate: string;
  sowing_season: string;
  varieties: string[];
  growth_stages: string[];
  water_requirement: string;
  harvesting: string;
  pests: string;
}

export interface WeatherForecastDay {
  date: string;
  day_name: string;
  condition: string;
  condition_kn: string;
  icon: string;
  temp_max: number;
  temp_min: number;
  precipitation_mm: number;
  rain_probability: number;
  wind_max_kmh: number;
}

export interface WeatherData {
  district: string;
  district_kn: string;
  taluk?: string;
  location_display?: string;
  region: string;
  resolution?: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  wind_speed: number;
  condition: string;
  condition_kn: string;
  icon?: string;
  weather_code: number;
  irrigation_advisory_en?: string;
  irrigation_advisory_kn?: string;
  spraying_advisory_en?: string;
  spraying_advisory_kn?: string;
  alerts?: string[];
  forecast_5_days?: WeatherForecastDay[];
  last_updated: string;
  is_live: boolean;
  source: string;
}

export interface MarketPrice {
  crop: string;
  crop_kn: string;
  market: string;
  district: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  unit?: string;
  date: string;
  is_historical: boolean;
}

export interface ChatMessage {
  id?: number;
  sender: 'farmer' | 'assistant';
  text: string;
  text_kn?: string;
  audio_url?: string;
  transcript?: string;
  topic?: string;
  intent?: string;
  created_at?: string;
}

export interface ConversationItem {
  id: number;
  session_id: string;
  title: string;
  topic: string;
  selected_language: string;
  selected_voice: string;
  message_count: number;
  last_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: number;
  session_id: string;
  title: string;
  topic: string;
  selected_language: string;
  selected_voice: string;
  current_stage: string;
  confirmed_details: Record<string, any>;
  missing_details: string[];
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface AnalysisHistoryItem {
  id: number;
  conversation_id?: number;
  topic: string;
  crop_information?: string;
  season_information?: string;
  weather_used?: string;
  recommendations?: string;
  eligibility_results?: string;
  source_references?: string;
  created_at: string;
}

export interface VoiceOption {
  voice_id: string;
  name: string;
  gender: 'female' | 'male';
  language: 'kn' | 'en';
  preview_text: string;
  description: string;
}

export interface SeasonCalendarPeriod {
  name: string;
  name_kn: string;
  months: string;
  status: string;
  description: string;
}

export interface AgriculturalSeasonData {
  current_date: string;
  current_time: string;
  timezone: string;
  current_season: string;
  current_season_kn: string;
  season_phase: string;
  transition_note?: string;
  crop_calendar: {
    kharif: SeasonCalendarPeriod;
    rabi: SeasonCalendarPeriod;
    summer: SeasonCalendarPeriod;
  };
  district?: string;
  crop?: string;
  crop_stage?: string;
  primary_crops_current_season: string[];
  advisory_bulletin: string;
  advisory_bulletin_kn: string;
  insurance_window: {
    scheme: string;
    scheme_kn: string;
    status: string;
    deadline_note: string;
    deadline_note_kn: string;
  };
  recommended_actions: string[];
  recommended_actions_kn: string[];
}

export interface CropInsuranceStatus {
  scheme_name: string;
  portal_name: string;
  portal_url: string;
  district: string;
  taluk?: string;
  crop: string;
  season: string;
  is_notified: boolean;
  notified_text: string;
  farmer_premium_rate: string;
  farmer_premium_amount_approx: string;
  cut_off_date?: string;
  calamity_intimation_rule: {
    window_hours: number;
    description: string;
    description_kn: string;
    helpline: string;
    steps: string[];
  };
  required_documents: string[];
}
