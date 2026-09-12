/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F0FDFA',
          100: '#CCFBF1',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E', // Primary accent
          800: '#115E59',
          900: '#134E4A',
        },
        aqi: {
          good: '#22C55E',
          moderate: '#EAB308',
          sensitive: '#F97316',
          unhealthy: '#EF4444',
          veryUnhealthy: '#A855F7',
          hazardous: '#7F1D1D',
        }
      }
    },
  },
  plugins: [],
}
