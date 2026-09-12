import React from 'react';

export function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 mt-12 py-8 text-sm text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-center sm:text-left">
            <p className="font-medium text-slate-700">Vayu Suchak – Air Quality & Health Advisory</p>
            <p className="text-xs text-slate-400 mt-1">
              Data grounded in CPCB monitoring stations & ML forecasting models.
            </p>
          </div>
          <div className="flex items-center gap-6 text-xs">
            <a
              href="https://cpcb.nic.in"
              target="_blank"
              rel="noreferrer"
              className="hover:text-teal-700 transition-colors"
            >
              CPCB India
            </a>
            <a
              href="https://waqi.info"
              target="_blank"
              rel="noreferrer"
              className="hover:text-teal-700 transition-colors"
            >
              WAQI Platform
            </a>
            <a
              href="https://openaq.org"
              target="_blank"
              rel="noreferrer"
              className="hover:text-teal-700 transition-colors"
            >
              OpenAQ
            </a>
          </div>
        </div>
        <div className="text-center mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-400">
          Health recommendations are for general guidance. Consult healthcare providers for severe respiratory distress.
        </div>
      </div>
    </footer>
  );
}
