import React from 'react';
import { Card } from './Card';
import { Brain, Cpu, Database, ShieldAlert, Sparkles, Wind } from 'lucide-react';
import { AQI_CATEGORIES } from '../utils/constants';

export function AboutView() {
  const aqiTable = [
    { range: '0–50', label: 'Good', color: '#22C55E', desc: 'Air quality is considered satisfactory, and air pollution poses little or no risk.' },
    { range: '51–100', label: 'Moderate', color: '#EAB308', desc: 'Air quality is acceptable; however, a few sensitive individuals may experience minor irritation.' },
    { range: '101–150', label: 'Unhealthy for Sensitive Groups', color: '#F97316', desc: 'Members of sensitive groups (asthmatics, children, elderly) may experience health effects.' },
    { range: '151–200', label: 'Unhealthy', color: '#EF4444', desc: 'Everyone may begin to experience health effects; sensitive groups may experience more serious effects.' },
    { range: '201–300', label: 'Very Unhealthy', color: '#A855F7', desc: 'Health alert: The risk of health effects is significantly increased for everyone in the population.' },
    { range: '301–500', label: 'Hazardous', color: '#7F1D1D', desc: 'Health warning of emergency conditions: Entire population is likely to experience serious adverse symptoms.' },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Overview Card */}
      <Card title="About Vayu Suchak" subtitle="Air Quality Index Forecasting & Health Advisory System">
        <p className="text-sm text-slate-600 leading-relaxed">
          <strong>Vayu Suchak</strong> (वायु सूचक – <em>Air Quality Indicator</em>) is a full-stack, publicly accessible, no-login web application engineered to provide real-time air quality monitoring, predictive particulate forecasting, and personalized medical health advisories across Indian metropolitan and regional areas.
        </p>
        <p className="text-sm text-slate-600 leading-relaxed mt-3">
          By unifying live telemetry from Central Pollution Control Board (CPCB) monitoring stations, OpenAQ, and WAQI with localized machine learning models, Vayu Suchak empowers citizens, commuters, athletes, and patients with asthma to take proactive steps to protect their respiratory health.
        </p>
      </Card>

      {/* How the ML Model Works */}
      <Card title="Machine Learning Architecture & Forecasting Methodology" subtitle="How our predictive models forecast PM2.5 and AQI">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2 text-teal-700">
              <Database className="w-4 h-4" />
              <h4 className="font-semibold text-xs md:text-sm text-slate-800">Telemetry Data</h4>
            </div>
            <p className="text-xs text-slate-600">
              Trained on extensive multi-station continuous air quality monitoring station (CAAQMS) records covering Kanpur and North Indian atmospheric conditions.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2 text-teal-700">
              <Cpu className="w-4 h-4" />
              <h4 className="font-semibold text-xs md:text-sm text-slate-800">Feature Engineering</h4>
            </div>
            <p className="text-xs text-slate-600">
              Extracts 1-hour and 24-hour PM2.5 lag features, 6-hour rolling means, diurnal sinusoidal time factors, and meteorological variables (temperature, relative humidity).
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2 text-teal-700">
              <Brain className="w-4 h-4" />
              <h4 className="font-semibold text-xs md:text-sm text-slate-800">Random Forest</h4>
            </div>
            <p className="text-xs text-slate-600">
              Random Forest Regressor ensemble optimized through chronological out-of-time validation, achieving high R² scores and low RMSE on unseen test periods.
            </p>
          </div>
        </div>

        <div className="p-3.5 bg-teal-50/60 border border-teal-200/80 rounded-lg text-xs text-teal-900 leading-relaxed">
          <strong>Autoregressive Multi-Step Projection:</strong> When requesting a 6-hour, 12-hour, 24-hour, or 7-day forecast, the system recursively feeds previous model predictions back into lag variables while updating diurnal temperature and humidity curves, generating dynamic uncertainty bounds and confidence metrics.
        </div>
      </Card>

      {/* Official AQI Scale Table */}
      <Card title="Air Quality Index (AQI) Classification Standard" subtitle="Standard color-coded severity benchmarks">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-700 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">AQI Range</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Health Impact & Recommendations</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {aqiTable.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50/75 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-slate-800 whitespace-nowrap">
                    <span
                      className="inline-block w-2.5 h-2.5 rounded-full mr-2"
                      style={{ backgroundColor: row.color }}
                    />
                    {row.range}
                  </td>
                  <td className="py-2.5 px-3 font-medium text-slate-800 whitespace-nowrap">
                    {row.label}
                  </td>
                  <td className="py-2.5 px-3 text-slate-600 leading-relaxed">
                    {row.desc}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Architecture & Security Notice */}
      <Card title="Security & Architecture Highlights">
        <ul className="list-disc list-inside text-xs text-slate-600 space-y-1.5 leading-relaxed">
          <li><strong>Zero Client-Side Credentials:</strong> All third-party upstream API keys (WAQI, OpenAQ, Gemini, OpenAI) are strictly retained on the backend server in environment variables.</li>
          <li><strong>Rate Limiting:</strong> IP-based rate limiting safeguards server resources and prevents upstream API depletion.</li>
          <li><strong>Resilient Fallback:</strong> In case external providers or AI models are temporarily unavailable, calibrated station engines provide immediate rule-based advisory and forecast projections.</li>
          <li><strong>Extensible for Accounts:</strong> Database tables include nullable user hooks so account features can be bolted on later without rewriting endpoints.</li>
        </ul>
      </Card>
    </div>
  );
}
