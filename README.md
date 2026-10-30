# KRISHI MITRA – ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ
### AI-Powered Agriculture Assistant for Karnataka Farmers (HackFusion 2.0)

Krishi Mitra is a voice-first, AI-powered agricultural intelligence platform designed specifically for Karnataka farmers. Built to overcome language barriers, fragmented government portals, and complex eligibility bureaucracies, Krishi Mitra combines **Kannada Conversational Intelligence**, **Deterministic Rule-Based Eligibility Checking**, **Real-Time Karnataka Meteorological Data**, and **APMC Mandi Price Intelligence**.

---

## 🌟 Key Technical Innovations

1. **Two-Way Real-Time Kannada AI Voice Assistant**:
   - Voice-first agricultural dialogue supporting regional Karnataka dialects:
     - **North Karnataka (ಉತ್ತರ ಕರ್ನಾಟಕ)**: e.g. Belagavi, Dharwad, Vijayapura, Kalaburagi dialect tokens (*"ಐತಿ"*, *"ಆಗತೈತಿ"*, *"ನೋಡ್ರೀ"*, *"ಹೌದ್ರೀ"*).
     - **South Karnataka (ದಕ್ಷಿಣ ಕರ್ನಾಟಕ)**: e.g. Mysuru, Mandya, Hassan, Bengaluru dialect (*"ಇದೆ"*, *"ಆಗುತ್ತದೆ"*, *"ತಿಳಿಸಿ"*).
     - **Standard Kannada (ಶಿಷ್ಟ ಕನ್ನಡ)**: Formal official state terminology.
   - Built-in Voice Orb animation with real-time listening rings, voice spectrum wave pulses, and interrupt capability.
   - Genuine Kannada Neural Text-to-Speech (TTS) synthesis and audio streaming.

2. **Deterministic Eligibility Engine (PASS / UNKNOWN / FAIL)**:
   - Eliminates hallucinated AI recommendations by evaluating criteria (land holding size, crop notification, ownership title, farmer category) deterministically against official government scheme rules.
   - Clearly flags **UNKNOWN** when mandatory farmer information is missing, asking follow-up questions instead of guessing.

3. **Government Scheme Repository & Verification Badges**:
   - Features real official welfare programs: **PM-KISAN**, **PMFBY (Crop Insurance)**, **Karnataka Krishi Bhagya**, **PM-KUSUM (Solar Pumps)**.
   - Explicitly flags synthetic benchmark records with amber badges (`Synthetic Demo Record`) to prevent confusion with actual government benefits.

4. **Institutional Credit & Accurate EMI Calculator**:
   - Verified information for Kisan Credit Card (KCC) short-term crop loans with 4% prompt repayment subventions.
   - Mathematical loan EMI calculation with amortization breakdown.

5. **Live Karnataka District Meteorological & Mandi Intelligence**:
   - Connects to Open-Meteo API for real-time temperature, precipitation, humidity, and wind across all 31 Karnataka districts.
   - Daily APMC Mandi modal commodity rates across Belagavi, Raichur, Mysuru, Davanagere, Kalaburagi, and Hubli.

---

## 🏗️ Folder Structure

```
Krishi Mitra/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entrypoint, CORS, static audio mounting
│   │   ├── config.py                  # 31 Karnataka districts, coordinates, regional mapping
│   │   ├── database.py                # SQLAlchemy SQLite/PostgreSQL engine and session
│   │   ├── models.py                  # User, FarmerProfile, Scheme, SavedScheme, Conversation, ChatMessage
│   │   ├── schemas.py                 # Pydantic schemas for requests and responses
│   │   ├── auth.py                    # Security, password hashing, and JWT bearer tokens
│   │   ├── seed_data.py               # Prepopulated verified government schemes, loans, crops, and APMC rates
│   │   ├── routes/
│   │   │   ├── auth_routes.py         # /api/auth/register, /api/auth/login, /api/auth/me
│   │   │   ├── farmer_routes.py       # /api/farmer/profile, /api/farmer/districts
│   │   │   ├── scheme_routes.py       # /api/schemes, /api/schemes/{id}, /api/schemes/eligibility, /api/schemes/stats
│   │   │   ├── loan_routes.py         # /api/loans, /api/loans/calculator
│   │   │   ├── crop_routes.py         # /api/crops, /api/crops/{crop_id}
│   │   │   ├── fertilizer_routes.py   # /api/fertilizer/recommend
│   │   │   ├── weather_routes.py      # /api/weather?district=...
│   │   │   ├── market_routes.py       # /api/market-prices
│   │   │   ├── chat_routes.py         # /api/chat, /api/chat/history, /api/chat/clear
│   │   │   ├── speech_routes.py       # /api/speech/synthesize, /api/speech/transcribe
│   │   │   └── admin_routes.py        # /api/admin/schemes, /api/admin/stats
│   │   └── services/
│   │       ├── district_service.py    # 31 Karnataka districts with taluk mappings
│   │       ├── eligibility_engine.py  # Deterministic PASS / FAIL / UNKNOWN evaluator
│   │       ├── agricultural_agent.py  # Agricultural NLU, entity extraction, context memory
│   │       └── kannada_speech.py      # Kannada Neural TTS (gTTS) & audio stream caching
│   ├── static_audio/                  # Cached MP3 audio generated on the fly
│   ├── requirements.txt               # Backend dependencies
│   ├── krishi_mitra.db                # SQLite database
│   └── test_suite.py                  # Comprehensive automated test suite (13 test cases)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx             # Responsive header with search, dialect selector, theme toggle
│   │   │   ├── Footer.tsx             # Official portals (Seva Sindhu, K-Kisan), helplines (1800-180-1551)
│   │   │   ├── SchemeCard.tsx         # Verified vs Demo card with bookmarking
│   │   │   └── VoiceAssistantWidget.tsx # Floating 2-way Kannada voice assistant orb
│   │   ├── context/
│   │   │   ├── AuthContext.tsx        # Authentication & profile state
│   │   │   ├── LanguageContext.tsx    # Kannada / English dictionary and regional speech dialects
│   │   │   └── ThemeContext.tsx       # Light & Dark mode persistence
│   │   ├── pages/
│   │   │   ├── HomePage.tsx           # Hero section, carousel, live DB stats, 8 service cards, About
│   │   │   ├── LoginPage.tsx          # Mobile number & password login
│   │   │   ├── RegisterPage.tsx       # District selection with automatic North/South Karnataka dialect mapping
│   │   │   ├── SchemesPage.tsx        # Filterable catalog by crop, category, and verification status
│   │   │   ├── SchemeDetailPage.tsx   # Detailed scheme view, transparent criteria, required docs checklist
│   │   │   ├── EligibilityCheckerPage.tsx # "Find Schemes for Me" instant rule evaluation
│   │   │   ├── SavedSchemesPage.tsx   # Farmer's saved schemes
│   │   │   ├── LoansPage.tsx          # KCC loans + Interactive EMI calculator
│   │   │   ├── CropGuidancePage.tsx   # 8 major Karnataka crops (soil, climate, stages, pests)
│   │   │   ├── FertilizerGuidancePage.tsx # Stage-based NPK recommendations, organic alternatives
│   │   │   ├── WeatherMarketPage.tsx  # 31 Karnataka district weather & APMC mandi prices
│   │   │   ├── VoiceAssistantPage.tsx # Dedicated Fullscreen Voice Assistant with glowing orb
│   │   │   ├── FarmerProfilePage.tsx  # Profile management, land size, crops, speech preference
│   │   │   └── AdminDashboardPage.tsx # Scheme management, synthetic demo toggles, system telemetry
│   │   ├── services/
│   │   │   └── api.ts                 # Centralized API client
│   │   ├── types/
│   │   │   └── index.ts               # TypeScript data schemas
│   │   ├── App.tsx                    # Route definitions and layout
│   │   ├── main.tsx                   # React root entrypoint
│   │   └── index.css                  # Tailwind v4, custom theme tokens, and Voice Orb animations
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── README.md
```

---

## 🚀 How to Run the Application Locally

### 1. Start the Backend API Server:
```powershell
cd "c:\Users\Shravani\OneDrive\Documents\Krishi Mitra\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend runs on: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`)*

### 2. Start the Frontend Application:
```powershell
cd "c:\Users\Shravani\OneDrive\Documents\Krishi Mitra\frontend"
npm run dev
```
*Frontend runs on: `http://localhost:5173`*

### 3. Run the Automated Test Suite:
```powershell
cd "c:\Users\Shravani\OneDrive\Documents\Krishi Mitra\backend"
python -X utf8 test_suite.py
```
*(All 13 test suites test authentication, DB seeding, rule engine, speech synthesis, and live weather)*

---

## ⚙️ Environment Variables (Optional)

The application works out-of-the-box with SQLite and local Google Kannada Neural TTS. To configure external services:
```env
DATABASE_URL=sqlite:///./krishi_mitra.db  # Or postgresql://user:pass@localhost:5432/krishimitra
SECRET_KEY=your-custom-jwt-secret
GEMINI_API_KEY=your-google-gemini-api-key # Optional: activates cloud LLM reasoning
```
