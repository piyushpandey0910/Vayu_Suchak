import React from 'react';

export function getAqiMeta(aqi) {
  const val = Math.max(0, Number(aqi) || 0);
  if (val <= 50) {
    return {
      label: 'Good',
      color: '#22C55E',
      bgLight: 'bg-emerald-50',
      border: 'border-emerald-200',
      text: 'text-emerald-700',
    };
  } else if (val <= 100) {
    return {
      label: 'Moderate',
      color: '#EAB308',
      bgLight: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-700',
    };
  } else if (val <= 150) {
    return {
      label: 'Unhealthy for Sensitive Groups',
      color: '#F97316',
      bgLight: 'bg-orange-50',
      border: 'border-orange-200',
      text: 'text-orange-700',
    };
  } else if (val <= 200) {
    return {
      label: 'Unhealthy',
      color: '#EF4444',
      bgLight: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-700',
    };
  } else if (val <= 300) {
    return {
      label: 'Very Unhealthy',
      color: '#A855F7',
      bgLight: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-700',
    };
  } else {
    return {
      label: 'Hazardous',
      color: '#7F1D1D',
      bgLight: 'bg-rose-100',
      border: 'border-rose-300',
      text: 'text-rose-900',
    };
  }
}

export function AqiBadge({ aqi, showValue = true, showLabel = true, size = 'md' }) {
  const meta = getAqiMeta(aqi);

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 font-medium',
    md: 'text-sm px-2.5 py-1 font-semibold',
    lg: 'text-base px-3 py-1.5 font-bold',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${meta.bgLight} ${meta.border} ${meta.text} ${sizeClasses[size]}`}
    >
      <span
        className="w-2 h-2 rounded-full flex-shrink-0"
        style={{ backgroundColor: meta.color }}
      />
      {showValue && <span>{Math.round(aqi)}</span>}
      {showValue && showLabel && <span className="opacity-40">|</span>}
      {showLabel && <span>{meta.label}</span>}
    </span>
  );
}
