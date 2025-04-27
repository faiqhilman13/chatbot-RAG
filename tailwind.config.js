/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'tnb-red': '#E31837',
        'tnb-blue': '#0055A4',
        'dark': {
          'bg-primary': '#121212',
          'bg-secondary': '#1E1E1E',
          'text-primary': '#E0E0E0',
          'text-secondary': '#A0A0A0',
          'border': '#333333',
        }
      },
      fontFamily: {
        sans: ['Roboto', 'Open Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}; 