/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'f1-red': '#DC0000',
        'f1-silver': '#C0C0C0',
        'f1-gold': '#FFD700',
        'f1-mercedes': '#00D2BE',
        'f1-redbull': '#1E41FF',
        'f1-ferrari': '#DC0000',
        'f1-mclaren': '#FF8700',
        'f1-alpine': '#0090FF',
        'f1-aston': '#006F62',
        'f1-haas': '#808080',
        'f1-williams': '#87CEEB',
        'f1-sauber': '#00E701'
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}