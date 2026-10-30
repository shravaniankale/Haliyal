import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { SettingsProvider } from './context/SettingsContext';
import { ThemeProvider } from './context/ThemeContext';
import { LanguageProvider } from './context/LanguageContext';
import { AuthProvider } from './context/AuthContext';

import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { VoiceAssistantWidget } from './components/VoiceAssistantWidget';

import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { SchemesPage } from './pages/SchemesPage';
import { SchemeDetailPage } from './pages/SchemeDetailPage';
import { EligibilityCheckerPage } from './pages/EligibilityCheckerPage';
import { SavedSchemesPage } from './pages/SavedSchemesPage';
import { LoansPage } from './pages/LoansPage';
import { CropGuidancePage } from './pages/CropGuidancePage';
import { FertilizerGuidancePage } from './pages/FertilizerGuidancePage';
import { WeatherMarketPage } from './pages/WeatherMarketPage';
import { VoiceAssistantPage } from './pages/VoiceAssistantPage';
import { FarmerProfilePage } from './pages/FarmerProfilePage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';

const AppContent: React.FC = () => {
  const location = useLocation();
  const isFullScreenVoice = location.pathname === '/voice-assistant';

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F9F5] dark:bg-[#0B1711] text-[#19251E] dark:text-[#EDF3EF] transition-colors duration-200">
      <Navbar />

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/schemes" element={<SchemesPage />} />
          <Route path="/schemes/:id" element={<SchemeDetailPage />} />
          <Route path="/eligibility-checker" element={<EligibilityCheckerPage />} />
          <Route path="/saved-schemes" element={<SavedSchemesPage />} />
          <Route path="/loans" element={<LoansPage />} />
          <Route path="/crops" element={<CropGuidancePage />} />
          <Route path="/fertilizer" element={<FertilizerGuidancePage />} />
          <Route path="/weather-market" element={<WeatherMarketPage />} />
          <Route path="/voice-assistant" element={<VoiceAssistantPage />} />
          <Route path="/profile" element={<FarmerProfilePage />} />
          <Route path="/admin" element={<AdminDashboardPage />} />
        </Routes>
      </main>

      {!isFullScreenVoice && <VoiceAssistantWidget />}
      <Footer />
    </div>
  );
};

export function App() {
  return (
    <SettingsProvider>
      <ThemeProvider>
        <LanguageProvider>
          <AuthProvider>
            <BrowserRouter>
              <AppContent />
            </BrowserRouter>
          </AuthProvider>
        </LanguageProvider>
      </ThemeProvider>
    </SettingsProvider>
  );
}

export default App;
