/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"IBM Plex Sans"', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
      colors: {
        institutional: {
          bg: '#F4F5F2',
          surface: '#FFFFFF',
          'surface-muted': '#EDEFEA',
          'surface-subtle': '#F8F9F7',
          border: '#D8DCD6',
          'border-strong': '#BCC3BA',
          text: '#17201C',
          'text-secondary': '#59625D',
          'text-muted': '#808B84',
          sidebar: '#101A17',
          'sidebar-surface': '#182420',
          'sidebar-border': '#22322C',
          'sidebar-active': '#1D2D27',
          brand: '#163C32',
          'brand-hover': '#0E2922',
          'brand-light': '#E8F3EE',
          gold: '#A7833B',
          'gold-light': '#F7F3EB',
          'gold-border': '#D8C59A',
          pass: '#114B3A',
          'pass-bg': '#E8F3EE',
          'pass-border': '#B4DACB',
          fail: '#7A1C1C',
          'fail-bg': '#FBEBEB',
          'fail-border': '#F1B5B5',
          review: '#875200',
          'review-bg': '#FDF5E6',
          'review-border': '#F6D59B',
        }
      },
      borderRadius: {
        none: '0px',
        DEFAULT: '0px',
        sm: '0px',
        md: '0px',
        lg: '0px',
        xl: '0px',
        '2xl': '0px',
        '3xl': '0px',
        full: '0px',
      }
    },
  },
  plugins: [],
}
