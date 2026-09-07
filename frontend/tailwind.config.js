/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        petro: {
          navy: '#10283A',           // Primary dark from PDF
          forest: '#10283A',         // Primary dark
          green: '#123C35',          // Deep petroleum green from PDF
          institutional: '#123C35',
          amber: '#D98A16',          // Amber from PDF
          orange: '#E39A22',         // Orange from PDF
          bg: '#F4F5F7',             // Page background from PDF
          surface: '#FFFFFF',        // White
          'text-primary': '#17212B', // Primary text from PDF
          'text-secondary': '#66717C', // Secondary text from PDF
          border: '#D9DEE3',         // Border from PDF
          sidebar: '#10283A',
          card: '#FFFFFF',
        },
        status: {
          pass: '#198754',           // Success from PDF
          'pass-bg': '#EAF5F0',
          'pass-border': '#A8D9C5',
          review: '#D98A16',         // Warning / Amber from PDF
          'review-bg': '#FEF7EC',
          'review-border': '#F6D8A8',
          fail: '#C83B32',           // Danger from PDF
          'fail-bg': '#FDF2F2',
          'fail-border': '#F7BEBE',
          open: '#10283A',           // Open from PDF
          'open-bg': '#EEF2F6',
          'open-border': '#CBD5E1',
          paused: '#8C9BA5',
          'paused-bg': '#F1F3F5',
          'paused-border': '#D9DEE3',
        }
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        serif: ['"Newsreader"', 'Georgia', 'Cambria', '"Times New Roman"', 'Times', 'serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '4px',
        sm: '3px',
        md: '4px',
        lg: '6px',
        xl: '8px',
        '2xl': '12px',
        full: '9999px',
      },
      boxShadow: {
        'sharp': '0 1px 2px 0 rgba(16, 40, 58, 0.05)',
        'card': '0 1px 3px 0 rgba(16, 40, 58, 0.06), 0 1px 2px -1px rgba(16, 40, 58, 0.04)',
        'panel': '0 1px 3px 0 rgba(16, 40, 58, 0.08)',
        'modal': '0 10px 25px -5px rgba(16, 40, 58, 0.25), 0 8px 10px -6px rgba(16, 40, 58, 0.2)',
        'none': 'none',
      }
    },
  },
  plugins: [],
}
