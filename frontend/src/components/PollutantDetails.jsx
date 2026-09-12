import React from 'react';
import { Card } from './Card';

export function PollutantDetails({ pollutants }) {
  if (!pollutants) return null;

  const pollutantList = [
    { key: 'pm25', label: 'PM2.5', desc: 'Fine Particulates (< 2.5 µm)' },
    { key: 'pm10', label: 'PM10', desc: 'Coarse Particulates (< 10 µm)' },
    { key: 'no2', label: 'NO₂', desc: 'Nitrogen Dioxide' },
    { key: 'so2', label: 'SO₂', desc: 'Sulfur Dioxide' },
    { key: 'co', label: 'CO', desc: 'Carbon Monoxide' },
    { key: 'o3', label: 'O₃', desc: 'Ground-level Ozone' },
  ];

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-slate-800 text-base">Pollutant Breakdown</h3>
        <span className="text-xs text-slate-500">Real-time station sensor readings</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {pollutantList.map(({ key, label, desc }) => {
          const item = pollutants[key];
          if (!item) return null;

          return (
            <Card key={key} className="!p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-slate-800 text-sm">{label}</span>
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: item.color }}
                  title={`Status: ${item.status}`}
                />
              </div>
              <div className="my-1">
                <span className="text-xl font-bold text-slate-900">{item.value}</span>
                <span className="text-[11px] text-slate-500 ml-1 font-normal">{item.unit}</span>
              </div>
              <div className="mt-1 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className="text-slate-500 truncate" title={desc}>{item.status}</span>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
