import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { Calendar, History, AlertCircle, RefreshCw, Loader2 } from 'lucide-react';
import { Card } from './Card';
import { AqiBadge, getAqiMeta } from './AqiBadge';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export function HistoryView() {
  const { city, getCachedData, setCachedData, notifyRateLimit } = useApp();
  const [range, setRange] = useState('7d');
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const ranges = [
    { id: '7d', label: '7 Days' },
    { id: '30d', label: '30 Days' },
    { id: '3m', label: '3 Months' },
    { id: '1y', label: '1 Year' },
  ];

  const fetchHistoryData = async (forceRefresh = false) => {
    // 1. Check client-side cache
    if (!forceRefresh) {
      const cached = getCachedData('history', city, range);
      if (cached) {
        setData(cached);
        setError(null);
        return;
      }
    }

    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getHistory(city, range);
      setData(res);
      setCachedData('history', city, range, res);
    } catch (err) {
      if (err.isRateLimit) {
        notifyRateLimit(err.message);
      }
      setError(err.message || "Failed to load historical air quality data.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistoryData();
  }, [city, range]);

  const formatTimestamp = (ts) => {
    const d = new Date(ts);
    if (range === '7d') {
      return d.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
    }
    return d.toLocaleDateString([], { month: 'short', day: 'numeric', year: range === '1y' ? '2-digit' : undefined });
  };

  // Compute statistics
  const aqiValues = data?.points?.map((p) => p.aqi) || [];
  const avgAqi = aqiValues.length ? Math.round(aqiValues.reduce((a, b) => a + b, 0) / aqiValues.length) : 0;
  const maxAqi = aqiValues.length ? Math.max(...aqiValues) : 0;
  const minAqi = aqiValues.length ? Math.min(...aqiValues) : 0;

  return (
    <div className="space-y-6">
      {/* Header with Range Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <History className="w-5 h-5 text-teal-700" />
            Historical AQI Trends – {city}
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Aggregated historical air quality records from monitoring stations and SQLite database.
          </p>
        </div>

        {/* Range Filter Buttons */}
        <div className="inline-flex bg-slate-200/80 p-1 rounded-lg border border-slate-200 text-xs font-medium self-start sm:self-auto">
          {ranges.map((r) => (
            <button
              key={r.id}
              onClick={() => setRange(r.id)}
              className={`px-3 py-1.5 rounded-md transition-all ${
                range === r.id
                  ? 'bg-white text-teal-800 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <Card className="py-20 flex flex-col items-center justify-center text-center">
          <Loader2 className="w-8 h-8 text-teal-700 animate-spin mb-3" />
          <p className="text-sm font-medium text-slate-700">Loading {range} historical records...</p>
          <p className="text-xs text-slate-400 mt-1">Querying time-series air quality database</p>
        </Card>
      ) : error ? (
        <Card className="py-12 text-center">
          <AlertCircle className="w-10 h-10 text-rose-500 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-800">History Records Unavailable</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">{error}</p>
          <button
            onClick={() => fetchHistoryData(true)}
            className="mt-4 inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-teal-700 text-white text-xs font-medium hover:bg-teal-800 transition-colors shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Query
          </button>
        </Card>
      ) : data ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="!p-4">
              <span className="text-xs text-slate-500 font-medium">Average Period AQI</span>
              <div className="flex items-center justify-between mt-1">
                <span className="text-2xl font-bold text-slate-900">{avgAqi}</span>
                <AqiBadge aqi={avgAqi} size="sm" />
              </div>
            </Card>

            <Card className="!p-4">
              <span className="text-xs text-slate-500 font-medium">Peak Recorded AQI</span>
              <div className="flex items-center justify-between mt-1">
                <span className="text-2xl font-bold text-slate-900">{maxAqi}</span>
                <AqiBadge aqi={maxAqi} size="sm" />
              </div>
            </Card>

            <Card className="!p-4">
              <span className="text-xs text-slate-500 font-medium">Best Recorded AQI</span>
              <div className="flex items-center justify-between mt-1">
                <span className="text-2xl font-bold text-slate-900">{minAqi}</span>
                <AqiBadge aqi={minAqi} size="sm" />
              </div>
            </Card>
          </div>

          {/* Recharts Area Chart */}
          <Card
            title={`AQI Progression (${range})`}
            subtitle="Observed particulate concentrations over the selected time range"
          >
            <div className="h-72 w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={data.points}
                  margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="historyGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0D9488" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#0D9488" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTimestamp}
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    domain={[0, (dataMax) => Math.max(150, Math.ceil((dataMax + 20) / 50) * 50)]}
                  />
                  <ReferenceLine y={50} stroke="#22C55E" strokeDasharray="3 3" />
                  <ReferenceLine y={100} stroke="#EAB308" strokeDasharray="3 3" />
                  <ReferenceLine y={200} stroke="#EF4444" strokeDasharray="3 3" />

                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const pt = payload[0].payload;
                        const meta = getAqiMeta(pt.aqi);
                        return (
                          <div className="bg-white border border-slate-200 rounded-lg shadow-md p-3 text-xs">
                            <p className="font-semibold text-slate-800">{formatTimestamp(pt.timestamp)}</p>
                            <div className="mt-1.5 space-y-1">
                              <div className="flex items-center justify-between gap-4">
                                <span className="text-slate-500">Recorded AQI:</span>
                                <span className="font-bold text-slate-900">{pt.aqi}</span>
                              </div>
                              <div className="flex items-center justify-between gap-4">
                                <span className="text-slate-500">Category:</span>
                                <span className="font-medium" style={{ color: meta.color }}>
                                  {meta.label}
                                </span>
                              </div>
                              <div className="flex items-center justify-between gap-4">
                                <span className="text-slate-500">PM2.5:</span>
                                <span className="text-slate-700">{pt.pm25} µg/m³</span>
                              </div>
                              {pt.pm10 && (
                                <div className="flex items-center justify-between gap-4">
                                  <span className="text-slate-500">PM10:</span>
                                  <span className="text-slate-700">{pt.pm10} µg/m³</span>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="aqi"
                    stroke="#0D9488"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#historyGrad)"
                    activeDot={{ r: 4, fill: "#0D9488" }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </>
      ) : null}
    </div>
  );
}
