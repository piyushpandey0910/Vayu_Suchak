import React, { useState, useEffect } from 'react';
import { Thermometer, Droplets, Wind, AlertCircle, RefreshCw, Loader2, ArrowRight, ShieldCheck, Compass } from 'lucide-react';
import { Card } from './Card';
import { AqiBadge, getAqiMeta } from './AqiBadge';
import { LocationSearch } from './LocationSearch';
import { PollutantDetails } from './PollutantDetails';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export function Dashboard() {
  const { city, currentAqiData, setCurrentAqiData, setActiveTab, notifyRateLimit } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadCurrentAqi = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getCurrentAQI(city);
      setCurrentAqiData(data);
    } catch (err) {
      if (err.isRateLimit) {
        notifyRateLimit(err.message);
      }
      setError(err.message || `Unable to fetch current AQI for ${city}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCurrentAqi();
  }, [city]);

  const aqiMeta = currentAqiData ? getAqiMeta(currentAqiData.aqi) : null;

  return (
    <div className="space-y-6">
      {/* Top Location Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-100/70 p-4 rounded-xl border border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Air Quality Dashboard
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time telemetry and atmospheric conditions for <span className="font-semibold text-teal-800">{city}</span>
          </p>
        </div>
        <LocationSearch />
      </div>

      {isLoading ? (
        <Card className="py-20 flex flex-col items-center justify-center text-center">
          <Loader2 className="w-8 h-8 text-teal-700 animate-spin mb-3" />
          <p className="text-sm font-medium text-slate-700">Connecting to air quality station in {city}...</p>
          <p className="text-xs text-slate-400 mt-1">Retrieving particulate sensors and weather telemetry</p>
        </Card>
      ) : error ? (
        <Card className="py-12 text-center">
          <AlertCircle className="w-10 h-10 text-rose-500 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-800">Telemetry Feed Unavailable</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">{error}</p>
          <button
            onClick={loadCurrentAqi}
            className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-teal-700 text-white text-xs font-medium hover:bg-teal-800 transition-colors shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Connection
          </button>
        </Card>
      ) : currentAqiData ? (
        <>
          {/* Main Hero Grid: Current AQI + Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* Current AQI Hero Card (7 cols) */}
            <Card className="lg:col-span-7 flex flex-col justify-between !p-6">
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Current Air Quality Index (AQI)
                    </span>
                    <h2 className="text-2xl font-bold text-slate-900 mt-0.5">{currentAqiData.city}</h2>
                  </div>
                  <span className="text-[11px] px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                    Source: {currentAqiData.source}
                  </span>
                </div>

                <div className="flex items-baseline gap-4 my-6">
                  <span
                    className="text-6xl md:text-7xl font-extrabold tracking-tight"
                    style={{ color: aqiMeta?.color }}
                  >
                    {Math.round(currentAqiData.aqi)}
                  </span>
                  <div>
                    <AqiBadge aqi={currentAqiData.aqi} showValue={false} size="lg" />
                    <p className="text-xs text-slate-500 mt-1">
                      CPCB standard Indian AQI scale
                    </p>
                  </div>
                </div>

                {/* Severity Progress Bar */}
                <div className="space-y-1.5">
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                    <div className="h-full bg-[#22C55E]" style={{ width: '10%' }} title="Good (0-50)" />
                    <div className="h-full bg-[#EAB308]" style={{ width: '10%' }} title="Moderate (51-100)" />
                    <div className="h-full bg-[#F97316]" style={{ width: '10%' }} title="Sensitive (101-150)" />
                    <div className="h-full bg-[#EF4444]" style={{ width: '10%' }} title="Unhealthy (151-200)" />
                    <div className="h-full bg-[#A855F7]" style={{ width: '20%' }} title="Very Unhealthy (201-300)" />
                    <div className="h-full bg-[#7F1D1D]" style={{ width: '40%' }} title="Hazardous (301-500)" />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>0 (Good)</span>
                    <span>100</span>
                    <span>200</span>
                    <span>300</span>
                    <span>500 (Hazardous)</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span>Updated: {new Date(currentAqiData.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                <button
                  onClick={() => setActiveTab('prediction')}
                  className="inline-flex items-center gap-1 font-medium text-teal-700 hover:text-teal-800 transition-colors"
                >
                  View ML Forecast <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </Card>

            {/* Key Atmospheric Metrics (5 cols) */}
            <div className="lg:col-span-5 grid grid-cols-2 gap-3.5">
              {/* Temperature */}
              <Card className="!p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="text-xs font-medium text-slate-600">Temperature</span>
                  <Thermometer className="w-4 h-4 text-amber-500" />
                </div>
                <div className="my-2">
                  <span className="text-2xl font-bold text-slate-900">{currentAqiData.temperature ?? '--'}</span>
                  <span className="text-xs text-slate-500 ml-1">°C</span>
                </div>
                <span className="text-[11px] text-slate-400">Ambient sensor</span>
              </Card>

              {/* Relative Humidity */}
              <Card className="!p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="text-xs font-medium text-slate-600">Humidity</span>
                  <Droplets className="w-4 h-4 text-blue-500" />
                </div>
                <div className="my-2">
                  <span className="text-2xl font-bold text-slate-900">{currentAqiData.humidity ?? '--'}</span>
                  <span className="text-xs text-slate-500 ml-1">%</span>
                </div>
                <span className="text-[11px] text-slate-400">Relative humidity</span>
              </Card>

              {/* Primary PM2.5 */}
              <Card className="!p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="text-xs font-medium text-slate-600">PM2.5 Primary</span>
                  <Wind className="w-4 h-4 text-teal-600" />
                </div>
                <div className="my-2">
                  <span className="text-2xl font-bold text-slate-900">{currentAqiData.pm25}</span>
                  <span className="text-xs text-slate-500 ml-1">µg/m³</span>
                </div>
                <span className="text-[11px] text-slate-400">Key predictor input</span>
              </Card>

              {/* Wind Speed */}
              <Card className="!p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="text-xs font-medium text-slate-600">Wind Velocity</span>
                  <Compass className="w-4 h-4 text-indigo-500" />
                </div>
                <div className="my-2">
                  <span className="text-2xl font-bold text-slate-900">{currentAqiData.wind_speed ?? '2.4'}</span>
                  <span className="text-xs text-slate-500 ml-1">m/s</span>
                </div>
                <span className="text-[11px] text-slate-400">Surface dispersion</span>
              </Card>
            </div>
          </div>

          {/* Quick Health Advisory Banner */}
          <div className="bg-teal-50 border border-teal-200 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-teal-700 text-white flex items-center justify-center flex-shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-800 text-sm">
                  Health & Activity Guidance for {currentAqiData.city}
                </h4>
                <p className="text-xs text-slate-600 mt-0.5">
                  {currentAqiData.aqi > 150
                    ? 'Unhealthy levels detected: Wear an N95 mask outdoors and avoid strenuous exercise.'
                    : currentAqiData.aqi > 100
                    ? 'Sensitive groups should reduce prolonged outdoor exertion.'
                    : 'Air quality is acceptable for outdoor walks and sports.'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setActiveTab('advisory')}
              className="px-3.5 py-1.5 rounded-lg bg-white border border-teal-300 text-teal-800 hover:bg-teal-100/50 text-xs font-semibold whitespace-nowrap transition-colors shadow-sm self-end sm:self-auto"
            >
              Full Advisory & AI Chat
            </button>
          </div>

          {/* Granular Pollutant Breakdown Grid */}
          <PollutantDetails pollutants={currentAqiData.pollutants} />
        </>
      ) : null}
    </div>
  );
}
