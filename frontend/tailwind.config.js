/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          500: '#1e3a5f',
          600: '#162d4a',
          700: '#0f2035',
          DEFAULT: '#1e3a5f',
        },
        accent: {
          DEFAULT: '#f59e0b',
          dark: '#d97706',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
