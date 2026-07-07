/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563EB',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: '#3B82F6',
        accent: '#60A5FA',
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
        surface: '#FFFFFF',
        textPrimary: '#0F172A',
        textSecondary: '#64748B',
        border: '#E2E8F0',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 10px -1px rgba(0, 0, 0, 0.03)',
        glass: '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
      },
      backgroundImage: {
        'gradient-mesh': "radial-gradient(at 0% 0%, rgba(219, 234, 254, 0.5) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(239, 246, 255, 0.4) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(219, 234, 254, 0.3) 0px, transparent 50%), radial-gradient(at 0% 100%, rgba(243, 244, 246, 0.5) 0px, transparent 50%)",
      }
    },
  },
  plugins: [],
}
