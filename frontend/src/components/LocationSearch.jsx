import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, Loader2, X } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';

const POPULAR_CITIES = ['Kanpur', 'Delhi', 'Mumbai', 'Bengaluru', 'Lucknow', 'Kolkata'];

export function LocationSearch() {
  const { city, setCity, notifyRateLimit } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search (300ms)
  useEffect(() => {
    if (!searchTerm.trim()) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const data = await api.searchLocations(searchTerm);
        setResults(data.results || []);
      } catch (err) {
        if (err.isRateLimit) {
          notifyRateLimit(err.message);
        }
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleSelect = (selectedCity) => {
    setCity(selectedCity);
    setSearchTerm('');
    setIsOpen(false);
  };

  return (
    <div className="relative w-full max-w-xl" ref={dropdownRef}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
          <Search className="w-4 h-4" />
        </div>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => {
            if (searchTerm.trim()) setIsOpen(true);
          }}
          placeholder="Search city or monitoring station (e.g. Kanpur, Delhi)..."
          className="w-full pl-10 pr-10 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-transparent transition-all shadow-sm"
        />
        {isLoading ? (
          <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center">
            <Loader2 className="w-4 h-4 text-teal-600 animate-spin" />
          </div>
        ) : searchTerm ? (
          <button
            onClick={() => setSearchTerm('')}
            className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600"
          >
            <X className="w-4 h-4" />
          </button>
        ) : null}
      </div>

      {/* Dropdown Results */}
      {isOpen && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1.5 bg-white rounded-lg border border-slate-200 shadow-lg z-50 overflow-hidden">
          <div className="py-1 max-h-60 overflow-y-auto">
            {results.map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleSelect(item.city)}
                className="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-50 flex items-center justify-between transition-colors border-b border-slate-50 last:border-0"
              >
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-teal-700" />
                  <span className="font-medium text-slate-800">{item.city}</span>
                  {item.state && (
                    <span className="text-xs text-slate-400">, {item.state}</span>
                  )}
                </div>
                <span className="text-[11px] text-slate-400 uppercase tracking-wider">{item.country}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Quick Select City Chips */}
      <div className="flex items-center flex-wrap gap-1.5 mt-2.5">
        <span className="text-xs text-slate-500 mr-1">Popular:</span>
        {POPULAR_CITIES.map((c) => (
          <button
            key={c}
            onClick={() => handleSelect(c)}
            className={`text-xs px-2.5 py-1 rounded-md border transition-colors ${
              city.toLowerCase() === c.toLowerCase()
                ? 'bg-teal-700 text-white border-teal-700 font-medium'
                : 'bg-white text-slate-600 border-slate-200 hover:border-teal-600 hover:text-teal-700'
            }`}
          >
            {c}
          </button>
        ))}
      </div>
    </div>
  );
}
