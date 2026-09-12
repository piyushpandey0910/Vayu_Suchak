import React from 'react';
import { Wind, Activity, TrendingUp, HelpCircle, ShieldCheck, MapPin } from 'lucide-react';
import { useApp } from '../context/AppContext';

export function Navbar() {
  const { activeTab, setActiveTab, city } = useApp();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'prediction', label: 'Prediction', icon: TrendingUp },
    { id: 'advisory', label: 'Health Advisory', icon: ShieldCheck },
    { id: 'history', label: 'History', icon: Wind },
    { id: 'about', label: 'About', icon: HelpCircle },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & App Name */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-teal-700 flex items-center justify-center text-white shadow-sm">
              <Wind className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-lg sm:text-xl text-slate-900 tracking-tight">
                Vayu Suchak
              </span>
              <span className="hidden sm:inline-block text-xs text-slate-500 ml-2 font-normal border-l border-slate-300 pl-2">
                AQI Prediction & Health Advisory
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-teal-50 text-teal-800'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-teal-700' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Active City Indicator */}
          <div className="flex items-center gap-2 text-xs sm:text-sm bg-slate-100 text-slate-700 px-3 py-1.5 rounded-full border border-slate-200">
            <MapPin className="w-3.5 h-3.5 text-teal-700 flex-shrink-0" />
            <span className="font-medium truncate max-w-[120px]">{city}</span>
          </div>
        </div>

        {/* Mobile Subnav */}
        <div className="flex md:hidden overflow-x-auto pb-2.5 pt-1 gap-1 border-t border-slate-100 no-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap ${
                  isActive
                    ? 'bg-teal-700 text-white'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
