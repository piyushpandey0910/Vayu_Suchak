import React, { createContext, useContext, useState, useEffect, useRef } from 'react';

const AppContext = createContext();

const STORAGE_KEYS = {
  CITY: 'vayu_suchak_last_city',
  RECENT_SEARCHES: 'vayu_suchak_recent_searches',
};

export function AppProvider({ children }) {
  // Read initial city from localStorage or default to Kanpur
  const [city, setCityState] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.CITY) || 'Kanpur';
    } catch {
      return 'Kanpur';
    }
  });

  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentAqiData, setCurrentAqiData] = useState(null);
  const [rateLimitNotice, setRateLimitNotice] = useState(null);

  // Client-side cache: key format `${type}_${city}_${range/horizon}`
  const cacheRef = useRef({});

  const setCity = (newCity) => {
    if (!newCity || newCity === city) return;
    setCityState(newCity);
    try {
      localStorage.setItem(STORAGE_KEYS.CITY, newCity);
    } catch (e) {
      console.warn("Could not save city to localStorage", e);
    }
  };

  const getCachedData = (type, targetCity, param) => {
    const key = `${type}_${targetCity.toLowerCase()}_${param}`;
    const cached = cacheRef.current[key];
    if (cached && (Date.now() - cached.timestamp < 1000 * 60 * 10)) { // 10 min TTL
      return cached.data;
    }
    return null;
  };

  const setCachedData = (type, targetCity, param, data) => {
    const key = `${type}_${targetCity.toLowerCase()}_${param}`;
    cacheRef.current[key] = {
      timestamp: Date.now(),
      data,
    };
  };

  const notifyRateLimit = (msg) => {
    setRateLimitNotice(msg || "You're sending requests too quickly — please wait a moment.");
    setTimeout(() => {
      setRateLimitNotice(null);
    }, 6000);
  };

  return (
    <AppContext.Provider
      value={{
        city,
        setCity,
        activeTab,
        setActiveTab,
        currentAqiData,
        setCurrentAqiData,
        getCachedData,
        setCachedData,
        rateLimitNotice,
        setRateLimitNotice,
        notifyRateLimit,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
