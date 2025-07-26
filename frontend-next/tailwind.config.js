/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        f1: {
          red: '#FF0033',
          'red-light': '#FF4466',
          teal: '#00FFE6',
          'teal-light': '#66FFF0',
          dark: '#000000',
          darker: '#111111',
          'card-bg': 'rgba(25, 25, 25, 0.98)',
          'glass-bg': 'rgba(255, 255, 255, 0.05)',
        },
        team: {
          mercedes: '#00D2BE',
          redbull: '#1E41FF',
          ferrari: '#DC0000',
          mclaren: '#FF8700',
          alpine: '#0090FF',
          alphatauri: '#4E7C9B',
          aston: '#006F62',
          williams: '#005AFF',
          alfa: '#900000',
          rb: '#6692FF',
          sauber: '#52E252',
          haas: '#FFFFFF',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'monospace'],
      },
      boxShadow: {
        'neon-teal': '0 0 20px rgba(0, 255, 230, 0.5)',
        'neon-red': '0 0 20px rgba(255, 0, 51, 0.5)',
        'glow-lg': '0 25px 50px -12px rgba(0, 0, 0, 0.9)',
        'glow-xl': '0 35px 60px -12px rgba(0, 0, 0, 0.95)',
      },
      animation: {
        'championship-pulse': 'championship-pulse 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        'championship-pulse': {
          '0%, 100%': { 
            transform: 'scale(1) rotate(0deg)', 
            boxShadow: '0 8px 25px rgba(255, 215, 0, 0.4)'
          },
          '50%': { 
            transform: 'scale(1.08) rotate(2deg)', 
            boxShadow: '0 12px 35px rgba(255, 215, 0, 0.6)'
          },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'glow': {
          '0%': { boxShadow: '0 0 5px rgba(0, 255, 230, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 255, 230, 0.8)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}