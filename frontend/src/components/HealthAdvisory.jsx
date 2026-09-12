import React, { useState, useEffect } from 'react';
import { Shield, Activity, Heart, Wind, Home, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';
import { Card } from './Card';
import { AqiBadge } from './AqiBadge';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

export function HealthAdvisory({ aqi, city }) {
  const { notifyRateLimit } = useApp();
  const [advisory, setAdvisory] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const safeAqi = aqi !== undefined && aqi !== null ? aqi : 110;

  useEffect(() => {
    let isMounted = true;
    async function loadAdvisory() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.getHealthAdvisory(safeAqi);
        if (isMounted) setAdvisory(data);
      } catch (err) {
        if (isMounted) {
          if (err.isRateLimit) notifyRateLimit(err.message);
          setError("Failed to load live advisory.");
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }
    loadAdvisory();
    return () => { isMounted = false; };
  }, [safeAqi]);

  if (isLoading) {
    return (
      <Card title="Health Advisory" subtitle="Medical guidance based on current air quality">
        <div className="flex items-center justify-center py-10 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin text-teal-700 mr-2" />
          <span className="text-sm">Generating personalized health advisory...</span>
        </div>
      </Card>
    );
  }

  if (error || !advisory) {
    return (
      <Card title="Health Advisory" subtitle="Medical guidance based on current air quality">
        <div className="text-center py-6 text-sm text-slate-500">
          <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto mb-2" />
          <p>{error || "Unable to display advisory"}</p>
        </div>
      </Card>
    );
  }

  const adviceItems = [
    {
      title: "Mask Recommendation",
      content: advisory.mask_recommendation,
      icon: Shield,
      badge: safeAqi > 150 ? "Essential" : safeAqi > 100 ? "Advised" : "Optional",
      badgeColor: safeAqi > 150 ? "text-red-700 bg-red-50 border-red-200" : "text-slate-600 bg-slate-100 border-slate-200",
    },
    {
      title: "Outdoor Activity",
      content: advisory.outdoor_activity,
      icon: Wind,
      badge: safeAqi > 150 ? "Restricted" : "Safe with caution",
      badgeColor: safeAqi > 150 ? "text-red-700 bg-red-50 border-red-200" : "text-emerald-700 bg-emerald-50 border-emerald-200",
    },
    {
      title: "Exercise & Fitness",
      content: advisory.exercise_advice,
      icon: Activity,
      badge: safeAqi > 200 ? "Indoor only" : safeAqi > 100 ? "Moderate" : "Safe",
      badgeColor: safeAqi > 100 ? "text-amber-700 bg-amber-50 border-amber-200" : "text-emerald-700 bg-emerald-50 border-emerald-200",
    },
    {
      title: "Sensitive Groups & Children",
      content: advisory.sensitive_groups,
      icon: Heart,
      badge: safeAqi > 100 ? "High Caution" : "Normal",
      badgeColor: safeAqi > 100 ? "text-orange-700 bg-orange-50 border-orange-200" : "text-emerald-700 bg-emerald-50 border-emerald-200",
    },
  ];

  return (
    <Card
      title="Health Advisory"
      subtitle={`Medical and environmental precautions for ${city} (AQI ${Math.round(safeAqi)})`}
      action={<AqiBadge aqi={safeAqi} size="sm" />}
    >
      {/* Headline Banner */}
      <div className="mb-5 p-4 rounded-lg bg-slate-50 border border-slate-200 flex items-start gap-3">
        {safeAqi > 150 ? (
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
        ) : (
          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
        )}
        <div>
          <h4 className="font-semibold text-slate-800 text-sm md:text-base">
            {advisory.headline}
          </h4>
          <p className="text-xs md:text-sm text-slate-600 mt-1 leading-relaxed">
            {advisory.general_advice}
          </p>
        </div>
      </div>

      {/* Advisory Specifics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {adviceItems.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              className="p-3.5 rounded-lg border border-slate-100 bg-white hover:border-slate-200 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-md bg-teal-50 text-teal-700 flex items-center justify-center">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="font-medium text-slate-800 text-xs md:text-sm">{item.title}</span>
                  </div>
                  <span className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded border ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {item.content}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {advisory.air_purifier_needed && (
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-600">
          <Home className="w-4 h-4 text-teal-700 flex-shrink-0" />
          <span>
            <strong>Indoor Protection:</strong> Keep windows sealed and operate a True HEPA air purifier to remove infiltrating fine particles.
          </span>
        </div>
      )}
    </Card>
  );
}
