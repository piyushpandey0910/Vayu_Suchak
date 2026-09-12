import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { Dashboard } from './components/Dashboard';
import { PredictionView } from './components/PredictionView';
import { HealthAdvisory } from './components/HealthAdvisory';
import { AiChatAssistant } from './components/AiChatAssistant';
import { HistoryView } from './components/HistoryView';
import { AboutView } from './components/AboutView';
import { AlertCircle, X } from 'lucide-react';

function AppContent() {
  const { activeTab, city, currentAqiData, rateLimitNotice, setRateLimitNotice } = useApp();

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-50 text-slate-800">
      <div>
        <Navbar />

        {/* Global Rate Limit Toast / Banner */}
        {rateLimitNotice && (
          <div className="bg-amber-500 text-white px-4 py-2.5 shadow-md flex items-center justify-between text-xs sm:text-sm font-medium z-50 sticky top-16 transition-all">
            <div className="max-w-7xl mx-auto flex items-center gap-2 flex-1">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{rateLimitNotice}</span>
            </div>
            <button
              onClick={() => setRateLimitNotice(null)}
              className="text-white/80 hover:text-white p-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Main Content View Container */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'prediction' && <PredictionView />}
          {activeTab === 'advisory' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-7">
                <HealthAdvisory aqi={currentAqiData?.aqi} city={city} />
              </div>
              <div className="lg:col-span-5">
                <AiChatAssistant
                  city={city}
                  currentAqi={currentAqiData?.aqi}
                  pollutants={currentAqiData?.pollutants}
                />
              </div>
            </div>
          )}
          {activeTab === 'history' && <HistoryView />}
          {activeTab === 'about' && <AboutView />}
        </main>
      </div>

      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
