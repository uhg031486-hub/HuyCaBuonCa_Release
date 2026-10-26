/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cinematic: {
          dark: '#0B0F17',
          deep: '#070A0F',
          surface: '#121824',
          card: '#161E2E',
          border: 'rgba(255, 255, 255, 0.1)',
        },
        accent: {
          red: '#E50914',
          'red-hover': '#F40612',
          gold: '#F5C518',
          'gold-hover': '#E0B014',
        }
      },
      aspectRatio: {
        'poster': '2 / 3',
        'backdrop': '16 / 9',
      },
      boxShadow: {
        'neon-red': '0 0 25px rgba(229, 9, 20, 0.45)',
        'neon-gold': '0 0 25px rgba(245, 197, 24, 0.45)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
