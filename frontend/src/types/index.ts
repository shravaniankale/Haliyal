export interface User {
  id: number;
  name: string;
  mobile: string;
  role: 'farmer' | 'admin';
  created_at: string;
}

export interface FarmerProfile {
  id: number;
  user_id: number;
  name: string;
  mobile: string;
  district: string;
  taluk: string;
  village?: string;
  preferred_language: 'kn' | 'en';
  regional_speech_preference: 'North Karnataka' | 'South Karnataka' | 'Standard Kannada';
  land_acres?: number;
  land_ownership: 'Own' | 'Tenant';
  irrigation_type: 'Rainfed' | 'Borewell' | 'Canal' | 'Drip';
  farmer_category: 'Small & Marginal' | 'General' | 'SC/ST' | 'Women';
  crops_grown: string[];
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

export interface WeatherData {
  district: string;
  district_kn: string;
  region: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  wind_speed: number;
  condition: string;
  condition_kn: string;
  weather_code: number;
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
  intent?: string;
  created_at?: string;
}
