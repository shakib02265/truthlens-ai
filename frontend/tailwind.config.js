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
        charcoal: {
          50: '#f6f7f9',
          100: '#eceef2',
          800: '#1e232a',
          900: '#13171c',
          950: '#0b0d10'
        },
        brand: {
          50: '#f0fdf4',
          500: '#16a34a',
          600: '#15803d',
          700: '#166534'
        }
      }
    },
  },
  plugins: [],
}
